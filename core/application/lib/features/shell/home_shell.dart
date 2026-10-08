import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/formatters.dart';
import 'dashboard_screen.dart';

/// Coquille de navigation : rail en large, barre en étroit.
///
/// Les cinq entrées suivent l'ordre du web. Le compteur de notifications vient
/// du fil, et non d'une requête dédiée : c'est le même nombre que l'onglet.
class HomeShell extends ConsumerStatefulWidget {
  const HomeShell({super.key});

  @override
  ConsumerState<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends ConsumerState<HomeShell> {
  int _index = 0;

  static const List<_Destination> _destinations = <_Destination>[
    _Destination('Tableau de bord', Icons.dashboard_outlined, Icons.dashboard),
    _Destination('Produits', Icons.inventory_2_outlined, Icons.inventory_2),
    _Destination('Mouvements', Icons.swap_vert_outlined, Icons.swap_vert),
    _Destination('Notifications', Icons.notifications_outlined, Icons.notifications),
    _Destination('Réglages', Icons.settings_outlined, Icons.settings),
  ];

  @override
  Widget build(BuildContext context) {
    final wide = isWideLayout(context);

    // Les onglets restent montés : sans `IndexedStack`, chaque changement
    // d'onglet relancerait les requêtes et perdrait la position de défilement.
    final pages = <Widget>[
      const DashboardScreen(),
      const _PlaceholderTab(
        icon: Icons.inventory_2_outlined,
        title: 'Produits',
      ),
      const _PlaceholderTab(
        icon: Icons.swap_vert_outlined,
        title: 'Mouvements',
      ),
      const _PlaceholderTab(
        icon: Icons.notifications_outlined,
        title: 'Notifications',
      ),
      const _PlaceholderTab(
        icon: Icons.settings_outlined,
        title: 'Réglages',
      ),
    ];

    final body = IndexedStack(index: _index, children: pages);

    if (!wide) {
      return Scaffold(
        body: body,
        bottomNavigationBar: NavigationBar(
          selectedIndex: _index,
          onDestinationSelected: (int value) => setState(() => _index = value),
          destinations: [
            for (int i = 0; i < _destinations.length; i++)
              NavigationDestination(
                icon: Icon(_destinations[i].icon),
                selectedIcon: Icon(_destinations[i].selectedIcon),
                label: _shortLabel(i),
              ),
          ],
        ),
      );
    }

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _index,
            onDestinationSelected: (int value) => setState(() => _index = value),
            labelType: NavigationRailLabelType.all,
            destinations: [
              for (final destination in _destinations)
                NavigationRailDestination(
                  icon: Icon(destination.icon),
                  selectedIcon: Icon(destination.selectedIcon),
                  label: Text(destination.label),
                ),
            ],
          ),
          const VerticalDivider(),
          Expanded(child: body),
        ],
      ),
    );
  }

  /// En barre basse, les libellés complets ne tiennent pas : on garde le mot
  /// que l'utilisateur cherche, comme le fait le web sur mobile.
  String _shortLabel(int index) => switch (index) {
        0 => 'Accueil',
        3 => 'Alertes',
        _ => _destinations[index].label,
      };
}

class _Destination {
  const _Destination(this.label, this.icon, this.selectedIcon);

  final String label;
  final IconData icon;
  final IconData selectedIcon;
}

/// Onglet en cours de construction, isolé pour que le squelette reste lisible.
class _PlaceholderTab extends StatelessWidget {
  const _PlaceholderTab({required this.icon, required this.title});

  final IconData icon;
  final String title;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: Colors.white38),
          const SizedBox(height: 12),
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 6),
          Text(
            Fr.plural(0, 'ligne'),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white38),
          ),
        ],
      ),
    );
  }
}