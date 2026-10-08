import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'auth_controller.dart';

/// Connexion et inscription, avec le même découpage que la page web.
///
/// Un seul écran pour les deux : l'utilisateur ne sait pas s'il a déjà un
/// compte, et lui demander d'y choisir par avance est une friction inutile.
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _password = TextEditingController();
  bool _registering = false;
  bool _obscure = true;

  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final controller = ref.read(authControllerProvider.notifier);
    final ok = _registering
        ? await controller.signUp(_username.text, _password.text)
        : await controller.signIn(_username.text, _password.text);
    // La redirection est faite par le routeur : pas de `context.go` ici.
    if (!ok && mounted) {
      // Le message est déjà dans `AuthState.error` et affiché plus bas.
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(authControllerProvider);
    final busy = state.status == AuthStatus.unknown;

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(Icons.inventory_2_outlined,
                      size: 56, color: Theme.of(context).colorScheme.primary),
                  const SizedBox(height: 16),
                  Text(
                    'StockPro',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _registering
                        ? 'Créez votre compte et votre boutique'
                        : 'Connectez-vous à votre boutique',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 28),
                  TextFormField(
                    controller: _username,
                    autocorrect: false,
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Nom d\'utilisateur',
                      prefixIcon: Icon(Icons.person_outline),
                    ),
                    validator: (String? value) =>
                        (value == null || value.trim().isEmpty)
                            ? 'Le nom d\'utilisateur est obligatoire.'
                            : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _password,
                    obscureText: _obscure,
                    textInputAction: TextInputAction.done,
                    onFieldSubmitted: (_) => _submit(),
                    decoration: InputDecoration(
                      labelText: 'Mot de passe',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off),
                        tooltip: _obscure ? 'Afficher' : 'Masquer',
                        onPressed: () => setState(() => _obscure = !_obscure),
                      ),
                    ),
                    validator: (String? value) => (value == null || value.isEmpty)
                        ? 'Le mot de passe est obligatoire.'
                        : null,
                  ),
                  if (state.error != null) ...[
                    const SizedBox(height: 16),
                    _ErrorBanner(message: state.error!),
                  ],
                  const SizedBox(height: 22),
                  FilledButton(
                    onPressed: busy ? null : _submit,
                    child: busy
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(_registering ? 'Créer mon compte' : 'Se connecter'),
                  ),
                  const SizedBox(height: 10),
                  TextButton(
                    onPressed: busy
                        ? null
                        : () => setState(() {
                              _registering = !_registering;
                              _formKey.currentState?.reset();
                            }),
                    child: Text(_registering
                        ? 'J\'ai déjà un compte'
                        : 'Créer un compte'),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Vos données restent lisibles hors connexion.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Bandeau d'erreur : le message vient du serveur, on ne le reformule pas.
class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: scheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: scheme.onErrorContainer, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: TextStyle(color: scheme.onErrorContainer),
            ),
          ),
        ],
      ),
    );
  }
}