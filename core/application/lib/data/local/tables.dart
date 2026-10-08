import 'package:drift/drift.dart';

/// Repère de synchronisation par entité : le curseur `ts`/`id` du serveur.
@DataClassName('SyncMarkRow')
class SyncMarks extends Table {
  /// Nom d'entité du protocole : `product`, `category`, `movement`, …
  TextColumn get entity => text()();

  /// Curseur opaque renvoyé par le dernier `pull` réussi.
  TextColumn get cursor => text().withDefault(const Constant(''))();

  DateTimeColumn get syncedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {entity};
}

/// Une opération d'écriture en attente d'envoi au serveur.
///
/// L'`seq` est monotone et local : il donne au push un ordre déterministe,
/// indispensable parce qu'une sortie de stock dépend de la création du produit
/// qui la precede.
@DataClassName('OutboxRow')
@TableIndex(name: 'outbox_op_id', unique: true, columns: {#opId})
class Outbox extends Table {
  /// Ordre local : c'est la clé primaire, parce qu'elle seule est monotone.
  IntColumn get seq => integer().autoIncrement()();

  /// Identifiant d'idempotence du protocole. Unique, mais pas primaire : deux
  /// lignes ne peuvent pas partager un `op_id`, et le `seq` doit pouvoir
  /// augmenter tout seul à chaque insertion.
  TextColumn get opId => text()();

  TextColumn get entity => text()();

  TextColumn get type => text()();

  TextColumn get uuid => text().nullable()();

  /// Champs modifiés, au format de `payload` du protocole.
  TextColumn get payload => text().withDefault(const Constant('{}'))();

  DateTimeColumn get clientTime => dateTime()();

  TextColumn get deviceId => text().withDefault(const Constant(''))();

  /// Renseigné après un rejet définitif, pour l'écran de synchronisation.
  TextColumn get lastError => text().nullable()();

  TextColumn get reasonCode => text().nullable()();

  IntColumn get attempts => integer().withDefault(const Constant(0))();

  DateTimeColumn get lastAttemptAt => dateTime().nullable()();
}

@DataClassName('ShopRow')
class Shops extends Table {
  TextColumn get uuid => text()();
  TextColumn get name => text()();
  TextColumn get currency => text().withDefault(const Constant(''))();
  TextColumn get primaryColor => text().withDefault(const Constant('#2563eb'))();
  TextColumn get sidebarColor => text().withDefault(const Constant('#0f172a'))();
  TextColumn get headerColor => text().withDefault(const Constant('#0f172a'))();
  TextColumn get backgroundColor => text().withDefault(const Constant('#020617'))();
  BoolColumn get scannerEnabled => boolean().withDefault(const Constant(true))();
  BoolColumn get barcodeFieldEnabled => boolean().withDefault(const Constant(true))();
  TextColumn get logoUrl => text().nullable()();
  DateTimeColumn get updatedAt => dateTime().nullable()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {uuid};
}

@DataClassName('CategoryRow')
class Categories extends Table {
  TextColumn get uuid => text()();
  TextColumn get name => text()();
  IntColumn get productCount => integer().withDefault(const Constant(0))();
  DateTimeColumn get updatedAt => dateTime().nullable()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {uuid};
}

@DataClassName('ProductRow')
class Products extends Table {
  TextColumn get uuid => text()();
  TextColumn get name => text()();
  TextColumn get sku => text().withDefault(const Constant(''))();
  TextColumn get barcode => text().withDefault(const Constant(''))();

  /// Clé étrangère locale : `Categories.uuid`.
  TextColumn get categoryUuid => text().nullable()();
  TextColumn get categoryName => text().withDefault(const Constant(''))();

  IntColumn get quantity => integer().withDefault(const Constant(0))();
  IntColumn get alertThreshold => integer().withDefault(const Constant(0))();
  TextColumn get salePrice => text().withDefault(const Constant('0'))();
  TextColumn get costPrice => text().withDefault(const Constant('0'))();
  TextColumn get currency => text().withDefault(const Constant(''))();
  TextColumn get description => text().withDefault(const Constant(''))();

  /// `rupture`, `bas` ou `ok`, recalculé localement pour ne pas dépendre du serveur.
  TextColumn get level => text().withDefault(const Constant('ok'))();

  /// Vrai tant que la ligne a une opération locale en attente : le pull ne doit
  /// alors pas l'écraser, sinon la saisie hors ligne disparaît avant d'être envoyée.
  BoolColumn get hasPendingOp => boolean().withDefault(const Constant(false))();

  DateTimeColumn get updatedAt => dateTime().nullable()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {uuid};
}

@DataClassName('MovementRow')
class Movements extends Table {
  TextColumn get uuid => text()();
  TextColumn get productUuid => text()();
  TextColumn get productName => text().withDefault(const Constant(''))();
  TextColumn get productSku => text().withDefault(const Constant(''))();

  /// `IN`, `OUT` ou `ADJ`.
  TextColumn get kind => text()();

  IntColumn get quantity => integer()();
  TextColumn get note => text().withDefault(const Constant(''))();
  TextColumn get username => text().withDefault(const Constant(''))();
  BoolColumn get hasPendingOp => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().nullable()();
  DateTimeColumn get updatedAt => dateTime().nullable()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {uuid};
}

@DataClassName('NotificationRow')
class Notifications extends Table {
  TextColumn get uuid => text()();
  TextColumn get kind => text().withDefault(const Constant(''))();
  TextColumn get kindLabel => text().withDefault(const Constant(''))();
  TextColumn get message => text().withDefault(const Constant(''))();
  TextColumn get productName => text().nullable()();
  IntColumn get quantity => integer().nullable()();
  IntColumn get alertThreshold => integer().nullable()();
  TextColumn get level => text().nullable()();
  IntColumn get tone => integer().nullable()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  BoolColumn get hasPendingOp => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().nullable()();
  DateTimeColumn get updatedAt => dateTime().nullable()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {uuid};
}

@DataClassName('MembershipRow')
class Memberships extends Table {
  TextColumn get uuid => text()();
  TextColumn get username => text()();
  TextColumn get fullName => text().withDefault(const Constant(''))();
  TextColumn get role => text().withDefault(const Constant(''))();
  BoolColumn get isOwner => boolean().withDefault(const Constant(false))();

  /// Drapeaux bruts : `Membership.has()` accorde tout au propriétaire, donc
  /// un écran qui lit ces colonnes doit passer par `hasPermission`.
  BoolColumn get canViewProducts => boolean().withDefault(const Constant(false))();
  BoolColumn get canAddProducts => boolean().withDefault(const Constant(false))();
  BoolColumn get canEditProducts => boolean().withDefault(const Constant(false))();
  BoolColumn get canDeleteProducts => boolean().withDefault(const Constant(false))();
  BoolColumn get canManageStock => boolean().withDefault(const Constant(false))();
  BoolColumn get canManageCategories => boolean().withDefault(const Constant(false))();

  DateTimeColumn get updatedAt => dateTime().nullable()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {uuid};
}

/// Les six permissions de `core.models.PERMISSIONS`, dans l'ordre du web.
const List<String> kPermissionNames = <String>[
  'can_view_products',
  'can_add_products',
  'can_edit_products',
  'can_delete_products',
  'can_manage_stock',
  'can_manage_categories',
];