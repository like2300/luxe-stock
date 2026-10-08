import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';

import '../../data/local/app_database.dart';

/// Formatage en français : la langue de l'utilisateur, pas celle du serveur.
class Fr {
  const Fr._();

  static final NumberFormat _integer = NumberFormat.decimalPattern('fr_FR');
  static final DateFormat _date = DateFormat('dd/MM/yyyy', 'fr_FR');
  static final DateFormat _dateTime = DateFormat('dd/MM/yyyy HH:mm', 'fr_FR');
  static final DateFormat _month = DateFormat('MMMM yyyy', 'fr_FR');

  /// `12 500` — séparateur espace normal.
  ///
  /// Le CLDR utilise l'espace fine insécable pour le français, et sa forme
  /// change selon les versions d'ICU : on la ramène à une espace ordinaire pour
  /// que l'affichage et les comparaisons de texte soient stables d'une machine
  /// à l'autre.
  static String number(num value) => _plain(_integer.format(value));

  /// `12 500,00` — la virgule décimale et deux chiffres après.
  static String money(Object? amount, [String currency = '']) {
    final value = double.tryParse('${amount ?? 0}'.replaceAll(',', '.')) ?? 0;
    final formatted = _plain(NumberFormat('#,##0.00', 'fr_FR').format(value));
    return currency.isEmpty ? formatted : '$formatted $currency';
  }

  /// Espaces fines et insécables du CLDR, ramenées à une espace normale.
  ///
  /// Une classe de caractères, pas une séquence : l'espace fine et l'espace
  /// insécable n'apparaissent jamais côte à côte, et chercher les deux d'un
  /// bloc ne remplacerait rien.
  static final RegExp _cldrSpaces = RegExp('[\u202f\u00a0]');

  static String _plain(String value) => value.replaceAll(_cldrSpaces, ' ');

  static String date(DateTime? value) => value == null ? '' : _date.format(value.toLocal());

  static String dateTime(DateTime? value) =>
      value == null ? '' : _dateTime.format(value.toLocal());

  static String month(DateTime value) => _month.format(value);

  /// « il y a 3 min », comme le web — l'utilisateur juge une fraîcheur, pas une date.
  static String relative(DateTime? value) {
    if (value == null) return '';
    final delta = DateTime.now().difference(value.toLocal());
    if (delta.isNegative) return "à l'instant";
    if (delta.inSeconds < 60) return "à l'instant";
    if (delta.inMinutes < 60) return 'il y a ${delta.inMinutes} min';
    if (delta.inHours < 24) return 'il y a ${delta.inHours} h';
    if (delta.inDays < 7) return 'il y a ${delta.inDays} j';
    return _date.format(value.toLocal());
  }

  /// Signature d'une entrée de menu : `Ctrl + S`, `⌘ + S` selon la plateforme.
  static String shortcut(String key) =>
      switch (defaultTargetPlatform) {
        TargetPlatform.macOS || TargetPlatform.iOS => '⌘ + $key',
        _ => 'Ctrl + $key',
      };

  /// Nombre avec son pluriel : `1 produit` / `3 produits`.
  static String plural(int count, String singular, [String? plural]) =>
      count <= 1 ? '$count $singular' : '$count ${plural ?? '${singular}s'}';
}

/// Le niveau d'un produit, recalculé localement plutôt que lu du serveur.
///
/// Le pull apporte le niveau du serveur, mais entre deux synchronisations le
/// stock local a pu changer : c'est ce calcul qui évite d'afficher « Stock sain »
/// sur un produit dont la dernière sortie l'a vidé.
String levelOf(int quantity, int alertThreshold) {
  if (quantity <= 0) return 'rupture';
  if (alertThreshold > 0 && quantity <= alertThreshold) return 'bas';
  return 'ok';
}

/// Un produit affiché, avec les jointures déjà résolues.
class ProductView {
  const ProductView({
    required this.row,
    required this.categoryName,
    required this.pendingCount,
  });

  final ProductRow row;
  final String categoryName;

  /// Nombre d'opérations locales en attente sur ce produit.
  final int pendingCount;

  String get uuid => row.uuid;
  String get name => row.name;
  int get quantity => row.quantity;
  int get alertThreshold => row.alertThreshold;
  String get level => levelOf(row.quantity, row.alertThreshold);
  bool get isDeleted => row.deletedAt != null;
  bool get hasPending => row.hasPendingOp;
}

/// Une notification affichée.
class NotificationView {
  const NotificationView(this.row);

  final NotificationRow row;

  bool get isUnread => !row.isRead;
  bool get isDeleted => row.deletedAt != null;
}