import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Les jetons JWT et l'identité du compte, gardés dans le coffre du système.
///
/// Rien de sensible ne va dans Drift ni dans les préférences ordinaires : le
/// mot de passe ne transite jamais le stockage local, et les jetons doivent
/// disparaître au premier démontage du coffre.
class Session {
  const Session({
    required this.access,
    required this.refresh,
    required this.username,
    required this.hasShop,
  });

  final String access;
  final String refresh;
  final String username;

  /// Savoir à la volée si le compte possède une boutique évite un aller-retour
  /// réseau au lancement pour savoir quel écran afficher.
  final bool hasShop;

  Map<String, dynamic> toJson() => {
        'access': access,
        'refresh': refresh,
        'username': username,
        'has_shop': hasShop,
      };

  factory Session.fromJson(Map<String, dynamic> json) => Session(
        access: json['access'] as String? ?? '',
        refresh: json['refresh'] as String? ?? '',
        username: json['username'] as String? ?? '',
        hasShop: json['has_shop'] as bool? ?? false,
      );
}

/// Coffre de session : lecture, écriture et effacement des jetons.
class SessionStore {
  SessionStore({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
            );

  static const _accessKey = 'session.access';
  static const _refreshKey = 'session.refresh';
  static const _usernameKey = 'session.username';
  static const _hasShopKey = 'session.has_shop';

  final FlutterSecureStorage _storage;

  Future<Session?> read() async {
    final values = await Future.wait([
      _storage.read(key: _accessKey),
      _storage.read(key: _refreshKey),
      _storage.read(key: _usernameKey),
      _storage.read(key: _hasShopKey),
    ]);
    if (values.any((String? value) => value == null)) {
      // Un seul champ manquant : la session est inexploitable, on la jette.
      return null;
    }
    return Session(
      access: values[0]!,
      refresh: values[1]!,
      username: values[2]!,
      hasShop: values[3] == 'true',
    );
  }

  Future<void> write(Session session) async {
    await _storage.write(key: _accessKey, value: session.access);
    await _storage.write(key: _refreshKey, value: session.refresh);
    await _storage.write(key: _usernameKey, value: session.username);
    await _storage.write(key: _hasShopKey, value: session.hasShop ? 'true' : 'false');
  }

  Future<void> clear() async {
    await Future.wait([
      _storage.delete(key: _accessKey),
      _storage.delete(key: _refreshKey),
      _storage.delete(key: _usernameKey),
      _storage.delete(key: _hasShopKey),
    ]);
  }

  /// Lecture brute, pour le client HTTP qui rafraîchit le jeton à la volée.
  Future<String?> accessToken() => _storage.read(key: _accessKey);

  Future<String?> refreshToken() => _storage.read(key: _refreshKey);

  /// Remplace uniquement le jeton d'accès après un rafraîchissement.
  Future<void> writeAccess(String token) => _storage.write(key: _accessKey, value: token);

  Future<void> writeRefresh(String token) => _storage.write(key: _refreshKey, value: token);

  /// Export lisible pour les tests et le débogage — jamais pour les logs.
  String debugDump() => jsonEncode({'has_session': true});
}