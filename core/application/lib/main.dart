import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'data/local/database_provider.dart';

/// Point d'entrée.
///
/// Les objets de longue durée — base locale, routeur — vivent dans des
/// providers : les recréer à chaque `build` ouvrirait un second fichier SQLite
/// et ferait perdre les écritures en cours.
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: StockProApp()));
}

class StockProApp extends ConsumerWidget {
  const StockProApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // `watch` sur la base pour que l'écran de synchronisation puisse écrire :
    // l'apparition de la base dans l'arbre ne doit pas reconstruire le thème.
    ref.watch(databaseProvider);
    final colors = ref.watch(shopThemeProvider).value ?? buildDarkThemeColors();

    return MaterialApp.router(
      title: 'StockPro',
      debugShowCheckedModeBanner: false,
      routerConfig: ref.watch(routerProvider),
      theme: buildDarkTheme(
        primary: colors.$1,
        sidebar: colors.$2,
        header: colors.$3,
        background: colors.$4,
      ),
      // L'interface est en français : les formats de date et de nombre suivent
      // la locale, pas le système de l'appareil.
      locale: const Locale('fr', 'FR'),
      supportedLocales: const [Locale('fr', 'FR'), Locale('en', 'US')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
    );
  }
}