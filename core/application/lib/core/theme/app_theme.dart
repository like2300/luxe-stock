import 'package:flutter/material.dart';

import '../config/app_config.dart';

/// Libellés et couleurs du web (`core.templatetags.core_tags`), recopiés pour que
/// l'app affiche exactement les mêmes mots que le site.
class Labels {
  const Labels._();

  static const Map<String, String> levels = {
    'rupture': 'Rupture',
    'bas': 'Stock bas',
    'ok': 'Stock sain',
  };

  static const Map<String, String> movements = {
    'IN': 'Entrée',
    'OUT': 'Sortie',
    'ADDED': 'Produit ajouté',
    'LOW': 'Stock bas',
    'RUPT': 'Rupture de stock',
    'ADJ': 'Quantité ajustée',
  };

  static String level(String code) => levels[code] ?? code;

  static String movement(String code) => movements[code] ?? code;

  /// Fond et texte d'une pastille de niveau, identiques à `LEVEL_COLORS`.
  static ({Color background, Color foreground}) levelColors(String code) {
    switch (code) {
      case 'rupture':
        return (background: const Color(0xFFFADBD8), foreground: const Color(0xFFB03A2E));
      case 'bas':
        return (background: const Color(0xFFFDECD2), foreground: const Color(0xFFB8730F));
      default:
        return (background: const Color(0xFFE3F4D6), foreground: const Color(0xFF4C8A1F));
    }
  }

  /// Couleurs lisibles sur fond sombre, dérivées des mêmes codes.
  static ({Color background, Color foreground}) levelColorsDark(String code) {
    switch (code) {
      case 'rupture':
        return (background: const Color(0x33B03A2E), foreground: const Color(0xFFF08A7E));
      case 'bas':
        return (background: const Color(0x33B8730F), foreground: const Color(0xFFE5B769));
      default:
        return (background: const Color(0x334C8A1F), foreground: const Color(0xFF9BD16B));
    }
  }

  /// Les six permissions de `core.models.PERMISSIONS`, dans l'ordre du web.
  static const Map<String, String> permissions = {
    'can_view_products': 'Voir les produits',
    'can_add_products': 'Ajouter des produits',
    'can_edit_products': 'Modifier des produits',
    'can_delete_products': 'Supprimer des produits',
    'can_manage_stock': 'Gérer le stock',
    'can_manage_categories': 'Gérer les catégories',
  };
}

/// Conversion d'un code couleur `#rrggbb` — le format que le web valide.
Color colorFromHex(String? hex, {Color fallback = const Color(0xFF2563EB)}) {
  if (hex == null) return fallback;
  var value = hex.trim();
  if (value.startsWith('#')) value = value.substring(1);
  if (value.length == 3) {
    value = value.split('').map((String c) => '$c$c').join();
  }
  if (value.length != 6) return fallback;
  final parsed = int.tryParse(value, radix: 16);
  return parsed == null ? fallback : Color(0xFF000000 | parsed);
}

/// Les quatre couleurs par défaut, identiques aux valeurs du modèle Django.
const Color kDefaultPrimary = Color(0xFF2563EB);
const Color kDefaultSidebar = Color(0xFF0F172A);
const Color kDefaultHeader = Color(0xFF0F172A);
const Color kDefaultBackground = Color(0xFF020617);

/// Le tuple des couleurs par défaut, tant qu'aucun pull n'a rien rapporté.
(Color, Color, Color, Color) buildDarkThemeColors() => (
      kDefaultPrimary,
      kDefaultSidebar,
      kDefaultHeader,
      kDefaultBackground,
    );

/// Thème sombre unique, teinté par les couleurs de la boutique.
///
/// La boutique peut changer ses quatre couleurs depuis le web : elles sont
/// appliquées à chaud au pull, sans redémarrage.
ThemeData buildDarkTheme({
  Color primary = kDefaultPrimary,
  Color sidebar = kDefaultSidebar,
  Color header = kDefaultHeader,
  Color background = kDefaultBackground,
}) {
  final scheme = ColorScheme.fromSeed(
    seedColor: primary,
    brightness: Brightness.dark,
  ).copyWith(
    primary: primary,
    surface: sidebar,
    surfaceContainerHighest: Color.alphaBlend(primary.withValues(alpha: 0.08), sidebar),
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: background,
    appBarTheme: AppBarTheme(
      backgroundColor: header,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: Colors.white,
      ),
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(48),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: sidebar,
      indicatorColor: primary.withValues(alpha: 0.18),
      selectedIconTheme: IconThemeData(color: primary),
      unselectedIconTheme: const IconThemeData(color: Colors.white70),
      selectedLabelTextStyle: const TextStyle(color: Colors.white, fontSize: 12),
      unselectedLabelTextStyle: const TextStyle(color: Colors.white60, fontSize: 12),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: sidebar,
      indicatorColor: primary.withValues(alpha: 0.18),
    ),
    dividerTheme: const DividerThemeData(color: Color(0x1FFFFFFF), space: 1),
  );
}

/// Sous quel seuil on bascule en disposition large.
///
/// 720 px est la limite retenue à l'identique pour le téléphone, la tablette et
/// le bureau : en dessous, une barre de navigation basse ; au-dessus, un rail.
const int kWideLayoutBreakpoint = 720;

/// Vrai sur tablette et bureau.
bool isWideLayout(BuildContext context) =>
    MediaQuery.sizeOf(context).width >= kWideLayoutBreakpoint;

/// Timeout de repli des commandes en attente d'un accord réseau.
const Duration kPendingTimeout = AppConfig.timeout;