import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import 'session_store.dart';

final sessionStoreProvider = Provider<SessionStore>((Ref ref) => SessionStore());

/// Erreur d'API telle que l'API la renvoie, message français compris.
///
/// Le serveur parle déjà la langue de l'utilisateur : on affiche sa phrase
/// plutôt que de la retraduire, sinon deux messages coexistent sur l'écran.
class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode, this.reasonCode, this.errors});

  final String message;
  final int? statusCode;

  /// Code stable prévu par `docs/SYNC.md` § 6, utile pour agir sans lire le texte.
  final String? reasonCode;

  /// Détail champ par champ des erreurs de validation.
  final Map<String, dynamic>? errors;

  /// Le compte n'a pas de boutique : l'app doit proposer l'écran de création.
  bool get needsShop => statusCode == 409;

  /// Session expirée ou révoquée : il faut rendre l'écran de connexion.
  bool get unauthorized => statusCode == 401;

  /// Erreur réseau ou 5xx : le client bascule en mode hors ligne sans alarme.
  bool get isOffline => statusCode == null || statusCode! >= 500;

  @override
  String toString() => 'ApiException($statusCode, $reasonCode): $message';
}

/// Client HTTP unique, avec authentification et rafraîchissement du jeton.
///
/// Un seul `Dio` pour toute l'app : c'est lui qui porte l'intercepteur de
/// rafraîchissement, donc deux clients se marcheraient dessus sur le jeton.
class ApiClient {
  ApiClient(this._store)
      : dio = Dio(
          BaseOptions(
            baseUrl: AppConfig.baseUrl,
            connectTimeout: AppConfig.connectTimeout,
            receiveTimeout: AppConfig.timeout,
            sendTimeout: AppConfig.timeout,
            contentType: Headers.jsonContentType,
            // Le code HTTP reste à traiter : une 400 a du sens pour l'app.
            validateStatus: (int? status) => status != null && status < 400,
          ),
        ) {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (RequestOptions options, RequestInterceptorHandler handler) {
          // `dio` est déjà construit à ce point : la lecture du jeton est
          // asynchrone, on l'attend avant de laisser partir la requête.
          _store.accessToken().then((token) {
            if (token != null && token.isNotEmpty) {
              options.headers['Authorization'] = 'Bearer $token';
            }
            handler.next(options);
          }).catchError((Object _) => handler.next(options));
        },
        onError: (DioException error, ErrorInterceptorHandler handler) async {
          // Un 401 sur un jeton simplement périmé se répare seul : on
          // rafraîchit puis on rejoue une fois, et une seule. Sur les propres
          // routes d'authentification, rejouer ne servirait à rien.
          final alreadyRetried = error.requestOptions.extra['retried'] == true;
          final isAuthRoute = _isAuthRoute(error.requestOptions.path);
          if (error.response?.statusCode != 401 || alreadyRetried || isAuthRoute) {
            handler.next(error);
            return;
          }
          final token = await refreshAccessToken();
          if (token == null) {
            handler.next(error);
            return;
          }
          try {
            final options = error.requestOptions;
            options.extra['retried'] = true;
            options.headers['Authorization'] = 'Bearer $token';
            handler.resolve(await dio.fetch(options));
          } on DioException catch (retryError) {
            handler.next(retryError);
          }
        },
      ),
    );
  }

  final SessionStore _store;

  /// Vrai tant qu'un rafraîchissement est en cours, pour que les requêtes
  /// concurrentes attendent la même réponse au lieu d'en déclencher dix.
  Future<String?>? _pendingRefresh;

  final Dio dio;

  Future<Map<String, dynamic>> get(String path, {Map<String, dynamic>? query}) async =>
      _wrap(() => dio.get<Map<String, dynamic>>(path, queryParameters: query));

  Future<Map<String, dynamic>> post(String path, {Object? body}) async =>
      _wrap(() => dio.post<Map<String, dynamic>>(path, data: body));

  Future<Map<String, dynamic>> put(String path, {Object? body}) async =>
      _wrap(() => dio.put<Map<String, dynamic>>(path, data: body));

  Future<Map<String, dynamic>> patch(String path, {Object? body}) async =>
      _wrap(() => dio.patch<Map<String, dynamic>>(path, data: body));

  Future<Map<String, dynamic>> delete(String path) async =>
      _wrap(() => dio.delete<Map<String, dynamic>>(path));

  /// Envoi multipart : photos de profil et logo de boutique.
  Future<Map<String, dynamic>> upload(
    String path, {
    required String filePath,
    String field = 'file',
    Map<String, dynamic> fields = const {},
  }) async {
    final form = FormData.fromMap({
      ...fields,
      field: await MultipartFile.fromFile(filePath),
    });
    return _wrap(() => dio.post<Map<String, dynamic>>(path, data: form));
  }

  /// Traduit la réponse HTTP en `ApiException`, ou rend le corps JSON tel quel.
  Future<Map<String, dynamic>> _wrap(
    Future<Response<Map<String, dynamic>>> Function() call,
  ) async {
    try {
      final response = await call();
      final data = response.data ?? <String, dynamic>{};
      return data;
    } on DioException catch (error) {
      throw _translate(error);
    }
  }

  /// Les routes d'authentification ne sont jamais rejouées automatiquement.
  bool _isAuthRoute(String path) =>
      path.endsWith(Endpoints.refresh) || path.endsWith(Endpoints.login);

  ApiException _translate(DioException error) {
    final response = error.response;
    if (response == null) {
      return const ApiException(
        'Serveur injoignable. Les données locales restent disponibles.',
      );
    }
    final body = response.data;
    if (body is! Map) {
      return ApiException(
        'Erreur ${response.statusCode}.',
        statusCode: response.statusCode,
      );
    }
    return ApiException(
      _messageOf(body) ?? 'Erreur ${response.statusCode}.',
      statusCode: response.statusCode,
      reasonCode: body['reason_code'] as String?,
      errors: _errorsOf(body),
    );
  }

  /// L'API répond `detail` pour une erreur simple et `errors` pour une
  /// validation : le message affiché doit venir dans tous les cas.
  String? _messageOf(Map<dynamic, dynamic> body) {
    final detail = body['detail'];
    if (detail is String && detail.isNotEmpty) return detail;
    final errors = body['errors'];
    if (errors is Map && errors.isNotEmpty) {
      final first = errors.entries.first;
      final value = first.value;
      if (value is String) return value;
      if (value is List && value.isNotEmpty) return '${first.key} : ${value.first}';
    }
    return null;
  }

  Map<String, dynamic>? _errorsOf(Map<dynamic, dynamic> body) {
    final errors = body['errors'];
    if (errors is Map) return errors.cast<String, dynamic>();
    return null;
  }

  /// Renvoie un nouveau jeton d'accès, en dédupliquant les tentatives.
  ///
  /// Si dix écrans seConnectent en même temps, une seule requête part vers
  /// `auth/refresh/` : les neuf autres attendent son résultat.
  Future<String?> refreshAccessToken() {
    return _pendingRefresh ??= _doRefresh().whenComplete(() => _pendingRefresh = null);
  }

  Future<String?> _doRefresh() async {
    final token = await _store.refreshToken();
    if (token == null || token.isEmpty) return null;
    try {
      // Un `Dio` nu, sans intercepteur : sinon le rafraîchissement
      // s'appellerait lui-même à l'infini sur un 401.
      final plain = Dio(BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: AppConfig.connectTimeout,
        validateStatus: (int? status) => status != null && status < 400,
      ));
      final response = await plain.post<Map<String, dynamic>>(
        Endpoints.refresh,
        data: {'refresh': token},
      );
      final access = response.data?['access'];
      if (access is! String || access.isEmpty) return null;
      await _store.writeAccess(access);
      final refresh = response.data?['refresh'];
      if (refresh is String && refresh.isNotEmpty) {
        await _store.writeRefresh(refresh);
      }
      return access;
    } on DioException {
      // Un jeton de rafraîchissement refusé : la session est morte, on ne
      // tente pas de la prolonger en boucle.
      await _store.clear();
      return null;
    }
  }
}

final apiClientProvider = Provider<ApiClient>(
  (Ref ref) => ApiClient(ref.watch(sessionStoreProvider)),
);