import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import 'tables.dart';

part 'app_database.g.dart';

/// Base locale : la source des lectures, pas un cache.
///
/// L'écran affiche toujours Drift, y compris connecté. Le serveur alimente la
/// base par `pull`, et les écritures partent par la file `outbox`. Ce choix
/// évite deux implémentations de chaque écran — une avec réseau, une sans.
@DriftDatabase(
  tables: [
    SyncMarks,
    Outbox,
    Shops,
    Categories,
    Products,
    Movements,
    Notifications,
    Memberships,
  ],
)
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_open());

  /// Pour les tests : une base en mémoire, sans fichier.
  AppDatabase.forTesting(super.executor);

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        beforeOpen: (OpeningDetails details) async {
          // `PRAGMA foreign_keys` est ignoré par défaut sur SQLite : sans ça,
          // une catégorie supprimée laisserait des produits orphelins.
          await customStatement('PRAGMA foreign_keys = ON');
          // `wal` : le pull écrit beaucoup pendant que l'utilisateur lit, et
          // un verrou exclusif lui ferait attendre tout l'écran.
          await customStatement('PRAGMA journal_mode = WAL');
          // `NORMAL` suffit : en cas de coupure brutale, on rejoue depuis le
          // pull, et `FULL` coûterait une écriture disque par ligne.
          await customStatement('PRAGMA synchronous = NORMAL');
        },
      );
}

LazyDatabase _open() {
  return LazyDatabase(() async {
    final directory = await getApplicationSupportDirectory();
    // Un sous-dossier dédié : le support applicatif peut contenir d'autres
    // fichiers, et un nom en dur au milieu d'eux est fragile.
    final folder = Directory(p.join(directory.path, 'stockpro'));
    await folder.create(recursive: true);
    final file = File(p.join(folder.path, 'stockpro.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}

/// Les `uuid` de produit touchés par une opération locale en attente.
///
/// Le pull s'en sert pour ne pas écraser une saisie pas encore partie : sans
/// cette garde, un produit modifié hors ligne perdrait ses modifications au
/// pull suivant, et l'utilisateur verrait son travail disparaître.
Future<Set<String>> pendingProductUuids(AppDatabase db) async {
  final rows = await (db.select(db.outbox)
        ..where((Outbox table) =>
            table.entity.equals('product') & table.type.isNotValue('delete')))
      .get();
  return rows.map((OutboxRow row) => row.uuid).whereType<String>().toSet();
}