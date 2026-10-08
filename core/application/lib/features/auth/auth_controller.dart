import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../data/remote/api_client.dart';
import '../../data/remote/session_store.dart';

/// Où en est la session, lu au démarrage depuis le coffre.
enum AuthStatus {
  /// Lecture du coffre en cours : on affiche un splash, jamais un écran de login.
  unknown,

  authenticated,

  /// Connecté, mais sans boutique : l'app doit proposer la création.
  needsShop,

  unauthenticated,
}

/// État d'authentification.
class AuthState {
  const AuthState({required this.status, this.username = '', this.error});

  final AuthStatus status;
  final String username;
  final String? error;

  bool get isBusy => status == AuthStatus.unknown;
}

/// Connexion, inscription, déconnexion.
///
/// Passe par l'API plutôt que par la session Django du web : les deux ne se
/// valident pas de la même façon, et mélanger les deuxcookies donnerait des
/// erreurs incompréhensibles.
class AuthController extends Notifier<AuthState> {
  @override
  AuthState build() {
    // La lecture du coffre est asynchrone : on démarre en `unknown` et on
    // laisse l'écran d'accueil décider quoi afficher.
    Future<void>.microtask(_restore);
    return const AuthState(status: AuthStatus.unknown);
  }

  ApiClient get _api => ref.read(apiClientProvider);
  SessionStore get _store => ref.read(sessionStoreProvider);

  Future<void> _restore() async {
    final session = await _store.read();
    if (session == null || session.access.isEmpty) {
      state = const AuthState(status: AuthStatus.unauthenticated);
      return;
    }
    state = AuthState(
      status: session.hasShop ? AuthStatus.authenticated : AuthStatus.needsShop,
      username: session.username,
    );
  }

  Future<bool> signIn(String username, String password) =>
      _authenticate(Endpoints.login, username, password);

  /// L'inscription crée le compte et la boutique en un aller-retour, comme le
  /// web : un compte sans boutique ne pourrait rien faire.
  Future<bool> signUp(String username, String password) =>
      _authenticate(Endpoints.signup, username, password);

  Future<bool> _authenticate(String path, String username, String password) async {
    state = const AuthState(status: AuthStatus.unknown);
    try {
      final body = await _api.post(
        path,
        body: <String, dynamic>{'username': username.trim(), 'password': password},
      );
      await _store.write(_sessionFrom(body, username.trim()));
      state = AuthState(
        status: AuthStatus.authenticated,
        username: username.trim(),
      );
      return true;
    } on ApiException catch (error) {
      state = AuthState(
        status: AuthStatus.unauthenticated,
        username: username,
        error: error.message,
      );
      return false;
    }
  }

  /// La réponse d'authentification est le jeton plus le profil connecté.
  ///
  /// `shop_name` vide signifie « pas de boutique » : le web redirige vers la
  /// création, l'app affiche le même écran. Lire ce champ ici évite une
  /// requête supplémentaire au lancement, et une 409 sur la première requête
  /// métiercorrigera le tir de toute façon.
  Session _sessionFrom(Map<String, dynamic> body, String fallbackUsername) {
    final user = body['user'];
    final profile = user is Map<String, dynamic> ? user : const <String, dynamic>{};
    final shopName = profile['shop_name'];
    return Session(
      access: '${body['access'] ?? ''}',
      refresh: '${body['refresh'] ?? ''}',
      username: '${profile['username'] ?? fallbackUsername}',
      hasShop: shopName is String && shopName.trim().isNotEmpty,
    );
  }

  /// Réponse 409 « pas de boutique » sur un écran métier.
  void markNeedsShop() {
    state = AuthState(status: AuthStatus.needsShop, username: state.username);
  }

  /// La boutique vient d'être créée : le compte passe en « connecté ».
  void markHasShop() {
    state = AuthState(status: AuthStatus.authenticated, username: state.username);
  }

  Future<void> signOut() async {
    // La révocation part au serveur quand le réseau le permet : sans elle, le
    // jeton resterait valable jusqu'à son expiration.
    final token = await _store.refreshToken();
    if (token != null && token.isNotEmpty) {
      try {
        await _api.post(Endpoints.logout, body: <String, dynamic>{'refresh': token});
      } on ApiException {
        // Réseau coupé ou jeton déjà révoqué : la déconnexion locale prime.
      }
    }
    await _store.clear();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}

final authControllerProvider =
    NotifierProvider<AuthController, AuthState>(AuthController.new);

/// Session en cours, lue par les écrans qui ont besoin du nom de compte.
final currentUsernameProvider = Provider<String>(
  (Ref ref) => ref.watch(authControllerProvider).username,
);