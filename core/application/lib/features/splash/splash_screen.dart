import 'package:flutter/material.dart';

/// Écran d'attente pendant la lecture du coffre de session.
///
/// Il ne fait rien et c'est volontaire : la redirection est décidée par le
/// routeur dès que le statut d'authentification est connu. Un écran qui devine
/// lui-même où aller finirait par courir en double.
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: SizedBox(
          height: 28,
          width: 28,
          child: CircularProgressIndicator(strokeWidth: 2.5),
        ),
      ),
    );
  }
}