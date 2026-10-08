import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../data/remote/api_client.dart';
import '../auth/auth_controller.dart';

/// Création de la boutique, pour un compte qui n'en a pas encore.
///
/// Les quatre couleurs sont proposées avec les valeurs par défaut du modèle :
/// les envoyer est inutile, donc ce n'est pas demandé.
class CreateShopScreen extends ConsumerStatefulWidget {
  const CreateShopScreen({super.key});

  @override
  ConsumerState<CreateShopScreen> createState() => _CreateShopScreenState();
}

class _CreateShopScreenState extends ConsumerState<CreateShopScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _currency = TextEditingController(text: 'MAD');
  final _address = TextEditingController();
  final _phone = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _name.dispose();
    _currency.dispose();
    _address.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref.read(apiClientProvider).post(
            Endpoints.shopCreate,
            body: <String, dynamic>{
              'name': _name.text.trim(),
              'currency': _currency.text.trim().toUpperCase(),
              if (_address.text.trim().isNotEmpty) 'address': _address.text.trim(),
              if (_phone.text.trim().isNotEmpty) 'phone': _phone.text.trim(),
            },
          );
      // La boutique existe : on repasse en « connecté » et le routeur affiche
      // le tableau de bord.
      if (mounted) {
        ref.read(authControllerProvider.notifier).markHasShop();
      }
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Créer ma boutique'),
        actions: [
          TextButton.icon(
            onPressed: _busy
                ? null
                : () => ref.read(authControllerProvider.notifier).signOut(),
            icon: const Icon(Icons.logout, size: 18),
            label: const Text('Déconnexion'),
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextFormField(
                    controller: _name,
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Nom de la boutique',
                      prefixIcon: Icon(Icons.storefront_outlined),
                    ),
                    validator: (String? value) =>
                        (value == null || value.trim().isEmpty)
                            ? 'Le nom est obligatoire.'
                            : null,
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: TextFormField(
                          controller: _currency,
                          textCapitalization: TextCapitalization.characters,
                          decoration: const InputDecoration(labelText: 'Devise'),
                          validator: (String? value) => (value == null || value.trim().isEmpty)
                              ? 'La devise est obligatoire.'
                              : null,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        flex: 3,
                        child: TextFormField(
                          controller: _phone,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(labelText: 'Téléphone'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _address,
                    textInputAction: TextInputAction.done,
                    decoration: const InputDecoration(
                      labelText: 'Adresse',
                      prefixIcon: Icon(Icons.location_on_outlined),
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 16),
                    Text(
                      _error!,
                      style: TextStyle(color: Theme.of(context).colorScheme.error),
                    ),
                  ],
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _busy ? null : _submit,
                    child: _busy
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Créer la boutique'),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Les couleurs et le logo se règlent ensuite, comme sur le web.',
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