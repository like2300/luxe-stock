import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme/app_theme.dart';
import 'app_database.dart';
import 'tables.dart';

/// La base locale, une seule fois par processus.
///
/// `ref.onDispose` la ferme quand le `ProviderScope` est détruit : sans cela le
/// fichier SQLite resterait ouvert et les dernières écrituresipartiraient
/// quand même, mais la connexionFuiterait à chaque rebuild du provider.
final databaseProvider = Provider<AppDatabase>((Ref ref) {
  final database = AppDatabase();
  ref.onDispose(database.close);
  return database;
});

/// Les quatre couleurs de la boutique, lues depuis la base locale.
///
/// Elles viennent du pull et non du réseau : changer de boutique ou appliquer un
/// thème ne doit pas dépendre d'une connexion. Tant qu'aucun pull n'a eu lieu,
/// le thème par défaut du modèle s'applique.
final shopThemeProvider = StreamProvider<(Color, Color, Color, Color)>((Ref ref) {
  final database = ref.watch(databaseProvider);
  final query = database.select(database.shops)
    ..where((Shops table) => table.deletedAt.isNull())
    ..limit(1);

  return query.watchSingleOrNull().map((ShopRow? row) {
    if (row == null) {
      return buildDarkThemeColors();
    }
    return (
      colorFromHex(row.primaryColor),
      colorFromHex(row.sidebarColor, fallback: const Color(0xFF0F172A)),
      colorFromHex(row.headerColor, fallback: const Color(0xFF0F172A)),
      colorFromHex(row.backgroundColor, fallback: const Color(0xFF020617)),
    );
  });
});