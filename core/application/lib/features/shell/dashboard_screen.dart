import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../core/theme/app_theme.dart';
import '../../core/utils/formatters.dart';
import '../../data/remote/api_client.dart';

/// Indicateurs, produits à réapprovisionner et derniers mouvements.
///
/// Les mêmes quatre chiffres et les mêmes deux listes que le tableau de bord web,
/// dans le même ordre : quelqu'un qui connaît le site retrouve ses repères.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboard = ref.watch(dashboardProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Tableau de bord')),
      body: dashboard.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (Object error, StackTrace stack) => _ErrorView(error: error),
        data: (Map<String, dynamic> data) => _DashboardBody(data: data),
      ),
    );
  }
}

/// `ConsumerWidget` et non `StatelessWidget` : le geste « tirer pour
/// actualiser » invalide le provider, ce qui demande un `ref`.
class _DashboardBody extends ConsumerWidget {
  const _DashboardBody({required this.data});

  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wide = isWideLayout(context);
    final tiles = <Widget>[
      _Tile(
        label: 'Produits',
        value: Fr.number(_int(data['n_products'])),
        icon: Icons.inventory_2_outlined,
      ),
      _Tile(
        label: 'Catégories',
        value: Fr.number(_int(data['n_categories'])),
        icon: Icons.category_outlined,
      ),
      _Tile(
        label: 'Stock bas',
        value: Fr.number(_int(data['n_low'])),
        icon: Icons.warning_amber_outlined,
        tint: const Color(0xFFB8730F),
      ),
      _Tile(
        label: 'Valeur du stock',
        value: Fr.money(data['value'], '${data['currency'] ?? ''}'),
        icon: Icons.payments_outlined,
      ),
    ];

    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(dashboardProvider),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'Bonjour ${data['greeting_name'] ?? ''}',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 4),
          Text(
            Fr.date(DateTime.now()),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white54),
          ),
          const SizedBox(height: 16),
          if (wide)
            Row(
              children: [
                for (int i = 0; i < tiles.length; i++) ...[
                  if (i > 0) const SizedBox(width: 12),
                  Expanded(child: tiles[i]),
                ],
              ],
            )
          else
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.6,
              children: tiles,
            ),
          const SizedBox(height: 20),
          _ChartCard(chart: _chart(data)),
          const SizedBox(height: 20),
          _ListCard(
            title: 'À réapprovisionner',
            icon: Icons.warning_amber_outlined,
            children: _products(data),
          ),
          const SizedBox(height: 20),
          _ListCard(
            title: 'Derniers mouvements',
            icon: Icons.history,
            children: _movements(data),
          ),
        ],
      ),
    );
  }

  static int _int(Object? value) =>
      value is num ? value.toInt() : int.tryParse('${value ?? 0}') ?? 0;

  static Map<String, dynamic> _chart(Map<String, dynamic> data) {
    final chart = data['chart'];
    return chart is Map<String, dynamic> ? chart : const <String, dynamic>{};
  }

  static List<Widget> _products(Map<String, dynamic> data) {
    final rows = data['low_products'];
    if (rows is! List || rows.isEmpty) {
      return const [_EmptyLine(text: 'Aucun produit sous le seuil.')];
    }
    return [
      for (final row in rows.whereType<Map<String, dynamic>>())
        _Line(
          leading: _LevelDot(level: '${row['level'] ?? 'ok'}'),
          title: '${row['name'] ?? ''}',
          trailing: Fr.number(_int(row['quantity'])),
          subtitle: '${row['category_name'] ?? row['sku'] ?? ''}',
        ),
    ];
  }

  static List<Widget> _movements(Map<String, dynamic> data) {
    final rows = data['recent_movements'];
    if (rows is! List || rows.isEmpty) {
      return const [_EmptyLine(text: 'Aucun mouvement enregistré.')];
    }
    return [
      for (final row in rows.whereType<Map<String, dynamic>>())
        _Line(
          leading: Icon(
            row['kind'] == 'IN' ? Icons.arrow_downward : Icons.arrow_upward,
            color: row['kind'] == 'IN' ? const Color(0xFF9BD16B) : const Color(0xFFF08A7E),
          ),
          title: '${row['product_name'] ?? ''}',
          subtitle:
              '${Labels.movement('${row['kind'] ?? ''}')}${row['username'] == null || '${row['username']}'.isEmpty ? '' : ' · ${row['username']}'}',
          trailing: '${row['kind'] == 'IN' ? '+' : '−'}${Fr.number(_int(row['quantity']))}',
        ),
    ];
  }
}

/// Série des six derniers mois, réutilisée telle quelle depuis le web.
class _ChartCard extends StatelessWidget {
  const _ChartCard({required this.chart});

  final Map<String, dynamic> chart;

  @override
  Widget build(BuildContext context) {
    final labels = _strings(chart['labels']);
    final entries = _numbers(chart['entries']);
    final exits = _numbers(chart['exits']);

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Entrées et sorties', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 4),
            Text(
              'Six derniers mois',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white54),
            ),
            const SizedBox(height: 20),
            if (entries.isEmpty && exits.isEmpty)
              const SizedBox(height: 120, child: _EmptyLine(text: 'Pas encore de mouvement.'))
            else
              SizedBox(
                height: 200,
                child: BarChart(
                  BarChartData(
                    alignment: BarChartAlignment.spaceAround,
                    gridData: FlGridData(show: true, drawVerticalLine: false),
                    borderData: FlBorderData(show: false),
                    titlesData: FlTitlesData(
                      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          getTitlesWidget: (double value, TitleMeta meta) {
                            final index = value.toInt();
                            if (index < 0 || index >= labels.length) {
                              return const SizedBox.shrink();
                            }
                            return Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: Text(
                                labels[index],
                                style: const TextStyle(fontSize: 10, color: Colors.white54),
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                    barGroups: [
                      for (int i = 0; i < entries.length; i++)
                        BarChartGroupData(
                          x: i,
                          barsSpace: 4,
                          barRods: [
                            BarChartRodData(toY: entries[i], width: 8, color: const Color(0xFF9BD16B)),
                            BarChartRodData(toY: exits[i], width: 8, color: const Color(0xFFF08A7E)),
                          ],
                        ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  static List<String> _strings(Object? value) =>
      value is List ? value.map((Object? e) => '$e').toList() : const <String>[];

  static List<double> _numbers(Object? value) {
    if (value is! List) return const <double>[];
    return value
        .map((Object? e) => double.tryParse('$e') ?? 0)
        .toList(growable: false);
  }
}

class _Tile extends StatelessWidget {
  const _Tile({required this.label, required this.value, required this.icon, this.tint});

  final String label;
  final String value;
  final IconData icon;
  final Color? tint;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 20, color: tint ?? Theme.of(context).colorScheme.primary),
            const SizedBox(height: 8),
            Text(
              value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white54),
            ),
          ],
        ),
      ),
    );
  }
}

class _ListCard extends StatelessWidget {
  const _ListCard({required this.title, required this.icon, required this.children});

  final String title;
  final IconData icon;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 18, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(title, style: Theme.of(context).textTheme.titleMedium),
              ],
            ),
            const SizedBox(height: 8),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _Line extends StatelessWidget {
  const _Line({
    required this.leading,
    required this.title,
    this.subtitle,
    this.trailing,
  });

  final Widget leading;
  final String title;
  final String? subtitle;
  final String? trailing;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          leading,
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
                if (subtitle != null && subtitle!.isNotEmpty)
                  Text(
                    subtitle!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white54),
                  ),
              ],
            ),
          ),
          if (trailing != null)
            Text(trailing!, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _LevelDot extends StatelessWidget {
  const _LevelDot({required this.level});

  final String level;

  @override
  Widget build(BuildContext context) {
    final colors = Labels.levelColorsDark(level);
    return Container(
      width: 12,
      height: 12,
      decoration: BoxDecoration(color: colors.foreground, shape: BoxShape.circle),
    );
  }
}

class _EmptyLine extends StatelessWidget {
  const _EmptyLine({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white38),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error});

  final Object error;

  @override
  Widget build(BuildContext context) {
    // Une coupure réseau doit lire « injoignable », pas « type d'exception » :
    // `ApiException` porte déjà le message rédigé par le serveur.
    final message = switch (error) {
      ApiException(:final message) => message,
      _ => 'Impossible de charger le tableau de bord.',
    };
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off_outlined, size: 44, color: Colors.white38),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

/// Le tableau de bord est le seul écran à ne pas venir du cache local : ses
/// indicateurs sont recalculés par le serveur à chaque appel, et le pull ne
/// stocke pas ces agrégats. Une coupure affiche donc l'état d'erreur, puis la
/// synchronisation ramène les listes.
final dashboardProvider = FutureProvider<Map<String, dynamic>>(
  (Ref ref) => ref.read(apiClientProvider).get(Endpoints.dashboard),
);