/// Configuration figée au démarrage, lue depuis `--dart-define`.
///
/// Aucune URL n'est écrite en dur dans le code : un build de développement et
/// un build de production n'ont pas la même adresse, et les comparer à la main
/// à chaque exécution est la source d'erreur la plus fréquente.
///
/// ```sh
/// flutter run --dart-define=API_BASE_URL=http://192.168.1.20:8000/api/v1/
/// ```
class AppConfig {
  const AppConfig._();

  /// Racine de l'API, terminaison slash comprise.
  ///
  /// `10.0.2.2` est l'alias de la machine hôte depuis l'émulateur Android ;
  /// sur appareil réel il faut l'adresse IP locale du serveur Django.
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1/',
  );

  /// Durée d'attente d'une requête, en millisecondes.
  ///
  /// Courte : la synchronisation mobile doit échouer vite pour repasser en mode
  /// hors ligne plutôt que de laisser l'interface figée.
  static const Duration timeout = Duration(seconds: 20);

  /// Nombre de lignes par lot de synchronisation.
  static const int pageSize = 200;

  /// Nombre maximal d'opérations par `push`, aligné sur `PUSH_LIMIT` côté API.
  static const int pushBatchSize = 200;

  /// Durée minimale avant un nouvel essai après un échec réseau.
  static const Duration retryDelay = Duration(seconds: 5);

  /// Au-delà de cette durée de silence, on considère que la connexion est morte.
  static const Duration connectTimeout = Duration(seconds: 8);
}

/// Les routes de l'API, regroupées ici pour éviter les chaînes en doublon.
class Endpoints {
  const Endpoints._();

  static const String login = 'auth/login/';
  static const String signup = 'auth/signup/';
  static const String refresh = 'auth/refresh/';
  static const String logout = 'auth/logout/';

  static const String shopCreate = 'shops/';
  static const String shopCurrent = 'shops/current/';
  static const String shopResetTheme = 'shops/current/reset_theme/';

  static const String dashboard = 'dashboard/';

  static const String products = 'products/';
  static const String productBulkDelete = 'products/bulk_delete/';
  static const String categories = 'categories/';
  static const String movements = 'movements/';

  static const String notifications = 'notifications/';
  static const String notificationsReadAll = 'notifications/read_all/';
  static const String notificationsClear = 'notifications/clear/';
  static String notificationRead(String uuid) => 'notifications/$uuid/read/';

  static const String employees = 'employees/';
  static const String profile = 'profile/';
  static const String profilePhoto = 'profile/photo/';

  static const String scanConfig = 'scan/config/';
  static const String scanLookup = 'scan/';
  static const String scanMovements = 'scan/movements/';

  static const String suggestProducts = 'suggest/products/';
  static const String suggestCategories = 'suggest/categories/';
  static const String suggestMovements = 'suggest/movements/';
  static const String suggestEmployees = 'suggest/employees/';
  static const String suggestNotifications = 'suggest/notifications/';

  static const String syncStatus = 'sync/status/';
  static const String syncPull = 'sync/pull/';
  static const String syncPush = 'sync/push/';
  static const String syncPushPhoto = 'sync/push/photo/';
  static const String syncOperations = 'sync/operations/';

  static String product(String uuid) => 'products/$uuid/';
  static String category(String uuid) => 'categories/$uuid/';
  static String movement(int id) => 'movements/$id/';
  static String employee(String uuid) => 'employees/$uuid/';
}