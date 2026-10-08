import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:stockpro/core/theme/app_theme.dart';
import 'package:stockpro/core/utils/formatters.dart';
import 'package:stockpro/data/local/app_database.dart';
import 'package:stockpro/data/local/tables.dart';

void main() {
  group('Formatters', () {
    test('les montants gardent deux décimales et la virgule française', () {
      expect(Fr.money('12500', 'MAD'), '12 500,00 MAD');
      expect(Fr.money('3.5', 'EUR'), '3,50 EUR');
      expect(Fr.money(null, 'MAD'), '0,00 MAD');
    });

    test('les quantités sont séparées par des espaces', () {
      expect(Fr.number(1234567), '1 234 567');
    });

    test('le pluriel suit le compte', () {
      expect(Fr.plural(0, 'produit'), '0 produit');
      expect(Fr.plural(1, 'produit'), '1 produit');
      expect(Fr.plural(2, 'produit'), '2 produits');
      expect(Fr.plural(3, 'catégorie', 'catégories'), '3 catégories');
    });
  });

  group('Niveau de stock', () {
    test('le niveau est recalculé, pas lu du serveur', () {
      // C'est le test qui compte : entre deux synchronisations, le stock local
      // a pu changer et l'affichage doit suivre.
      expect(levelOf(0, 5), 'rupture');
      expect(levelOf(5, 5), 'bas');
      expect(levelOf(6, 5), 'ok');
      expect(levelOf(3, 0), 'ok', reason: 'sans seuil, rien n\'est « bas »');
    });

    test('les libellés sont ceux du web', () {
      expect(Labels.level('rupture'), 'Rupture');
      expect(Labels.level('bas'), 'Stock bas');
      expect(Labels.level('ok'), 'Stock sain');
    });
  });

  group('Couleur hexadécimale', () {
    test('les trois écritures du web donnent la même couleur', () {
      expect(colorFromHex('#2563eb'), const Color(0xFF2563EB));
      expect(colorFromHex('2563eb'), const Color(0xFF2563EB));
      expect(colorFromHex('#26f'), const Color(0xFF2266FF));
    });

    test('une valeur illisible retombe sur la couleur par défaut', () {
      expect(colorFromHex('nope'), kDefaultPrimary);
      expect(colorFromHex(null), kDefaultPrimary);
    });
  });

  group('Base locale', () {
    late AppDatabase db;

    setUp(() {
      db = AppDatabase.forTesting(NativeDatabase.memory());
    });

    tearDown(() => db.close());

    test('une catégorie et ses produits se stockent et se relisent', () async {
      await db.into(db.categories).insert(
            CategoriesCompanion.insert(uuid: 'c1', name: 'Boissons'),
          );
      await db.into(db.products).insert(
            ProductsCompanion.insert(
              uuid: 'p1',
              name: 'Cola',
              categoryUuid: const Value('c1'),
              quantity: const Value(8),
            ),
          );

      final row = await (db.select(db.products)..where((Products t) => t.uuid.equals('p1')))
          .getSingle();
      expect(row.name, 'Cola');
      expect(row.quantity, 8);
      expect(row.categoryUuid, 'c1');
    });

    test('l\'outbox garde l\'ordre des opérations', () async {
      // L'ordre du push est ce qui garantit qu'une sortie de stock arrive après
      // la création du produit dont elle dépend.
      for (final entity in ['category', 'product', 'movement']) {
        await db.into(db.outbox).insert(
              OutboxCompanion.insert(
                opId: 'op-$entity',
                entity: entity,
                type: 'create',
                clientTime: DateTime.now(),
              ),
            );
      }
      final rows = await (db.select(db.outbox)..orderBy([(Outbox t) => OrderingTerm.asc(t.seq)]))
          .get();
      expect(rows.map((OutboxRow r) => r.entity).toList(),
          ['category', 'product', 'movement']);
    });

    test('un op_id ne peut pas être réutilisé', () async {
      // L'idempotence du serveur ne protège que si le client n'émet pas deux
      // fois le même op_id : la base doit donc refuser le doublon.
      await db.into(db.outbox).insert(
            OutboxCompanion.insert(
              opId: 'op-1',
              entity: 'product',
              type: 'create',
              clientTime: DateTime.now(),
            ),
          );
      expect(
        () => db.into(db.outbox).insert(
              OutboxCompanion.insert(
                opId: 'op-1',
                entity: 'product',
                type: 'update',
                clientTime: DateTime.now(),
              ),
            ),
        throwsA(anything),
      );
    });

    test('les marques de synchronisation sont lisibles par entité', () async {
      await db.into(db.syncMarks).insert(
            SyncMarksCompanion.insert(entity: 'product', cursor: const Value('abc')),
          );
      await db.into(db.syncMarks).insert(
            SyncMarksCompanion.insert(entity: 'category', cursor: const Value('def')),
          );
      final rows = await db.select(db.syncMarks).get();
      expect(rows.length, 2);
      expect(rows.firstWhere((SyncMarkRow r) => r.entity == 'product').cursor, 'abc');
    });
  });

  group('Base locale — garde des écritures en attente', () {
    test('les produits modifiés hors ligne sont signalés au pull', () async {
      final db = AppDatabase.forTesting(NativeDatabase.memory());
      addTearDown(db.close);

      await db.into(db.outbox).insert(
            OutboxCompanion.insert(
              opId: 'op-1',
              entity: 'product',
              type: 'update',
              uuid: const Value('p1'),
              clientTime: DateTime.now(),
            ),
          );
      // Une suppression ne protège pas la ligne : elle n'a plus rien à perdre.
      await db.into(db.outbox).insert(
            OutboxCompanion.insert(
              opId: 'op-2',
              entity: 'product',
              type: 'delete',
              uuid: const Value('p2'),
              clientTime: DateTime.now(),
            ),
          );

      final pending = await pendingProductUuids(db);
      expect(pending, {'p1'});
    });
  });

  group('Disposition', () {
    testWidgets('le seuil est 720 px comme sur le web', (WidgetTester tester) async {
      Future<void> pumpAt(double width) async {
        tester.view.physicalSize = Size(width, 800);
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.reset);
        await tester.pumpWidget(
          const MaterialApp(home: SizedBox.shrink()),
        );
      }

      await pumpAt(719);
      expect(isWideLayout(tester.element(find.byType(SizedBox))), isFalse);
      await pumpAt(720);
      expect(isWideLayout(tester.element(find.byType(SizedBox))), isTrue);
    });
  });
}