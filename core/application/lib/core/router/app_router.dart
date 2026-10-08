import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/auth_controller.dart';
import '../../features/auth/login_screen.dart';
import '../../features/shop/create_shop_screen.dart';
import '../../features/shell/home_shell.dart';
import '../../features/splash/splash_screen.dart';

final routerProvider = Provider<GoRouter>((Ref ref) {
  // `ref.read` et non `watch` : le routeur ne doit pas être reconstruit à
  // chaque changement d'état d'authentification, seulement être consulté au
  // moment de la navigation.
  final notifier = ref.read(authControllerProvider.notifier);
  final refresh = GoRouterRefresh(ref);

  return GoRouter(
    initialLocation: '/',
    refreshListenable: refresh,
    redirect: (BuildContext context, GoRouterState state) {
      final status = ref.read(authControllerProvider).status;
      final location = state.matchedLocation;

      if (status == AuthStatus.unknown) {
        return location == '/' ? null : '/';
      }
      if (status == AuthStatus.unauthenticated) {
        return location == '/connexion' ? null : '/connexion';
      }
      if (status == AuthStatus.needsShop) {
        return location == '/boutique/nouvelle' ? null : '/boutique/nouvelle';
      }
      // Connecté : plus aucune raison de montrer le login ou la création.
      if (location == '/connexion' || location == '/boutique/nouvelle') {
        return '/';
      }
      return null;
    },
    routes: [
      GoRoute(path: '/', builder: (_, _) => const SplashScreen()),
      GoRoute(path: '/connexion', builder: (_, _) => const LoginScreen()),
      GoRoute(path: '/boutique/nouvelle', builder: (_, _) => const CreateShopScreen()),
      GoRoute(
        path: '/app',
        builder: (_, _) => const HomeShell(),
        routes: const [],
      ),
    ],
    errorBuilder: (BuildContext context, GoRouterState state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Écran introuvable'),
            const SizedBox(height: 8),
            Text(state.uri.toString()),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () {
                notifier.markNeedsShop();
              },
              child: const Text('Retour au tableau de bord'),
            ),
          ],
        ),
      ),
    ),
  );
});

/// Relit l'état d'authentification pour rejouer les redirections.
class GoRouterRefresh extends ChangeNotifier {
  GoRouterRefresh(Ref ref) {
    ref.listen<AuthState>(
      authControllerProvider,
      (AuthState? previous, AuthState next) => notifyListeners(),
    );
  }
}

/// Route de connexion, pour les tests et les liens profonds.
void goToLogin(BuildContext context) => context.go('/connexion');

/// Route du tableau de bord.
void goToDashboard(BuildContext context) => context.go('/app');