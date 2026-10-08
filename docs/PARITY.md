# PARITY.md — Web Django → API → Flutter

Audit complet de l'application web (`core/`) et table de correspondance avec
l'API REST (`api/`) et l'application Flutter (`core/application/`).

## Conventions

- **Statut** : `OK` = implémenté et vérifié · `PLAN` = prévu, non écrit ·
  `ÉCART` = choix différent du web, justifié plus bas.
- **Règle** : quand le web est ambigu, on reproduit le comportement du web et on
  le note ici plutôt que d'inventer un comportement.
- Tous les libellés, messages et codes couleur viennent littéralement de
  `core/models.py`, `core/forms.py`, `core/views.py` et des gabarits.

## Source de vérité côté serveur (à ne jamais dupliquer)

| Fonction | Emplacement | Usage |
| --- | --- | --- |
| `record_movement()` | `core/models.py:268` | Entrée / sortie : recalcule la quantité de façon atomique, trace le mouvement, gère le franchissement de seuil |
| `record_adjustment()` | `core/models.py:284` | Écart de quantité (formulaire web et synchronisation) |
| `push_notification()` | `core/models.py:306` | Crée la notification, calcule `level` et `sound_code` |
| `notify_threshold_crossing()` | `core/models.py:325` | Alerte au franchissement + escalade rupture |
| `stock_history()` | `core/views.py:131` | Séries mensuelles du graphique (6 mois) |
| `LEVEL_COLORS` | `core/models.py:30` | `rupture #fadbd8/#b03a2e`, `bas #fdecd2/#b8730f`, `ok #e3f4d6/#4c8a1f` |
| `NOTIFICATION_KINDS` | `core/models.py:20` | `ADDED/AJOUT/880`, `IN/ENTREE/660`, `OUT/SORTIE/440`, `LOW/BAS/523`, `RUPT/RUPTURE/294`, `ADJ/AJUST/740` |
| `PERMISSIONS` | `core/models.py:10` | Libellés des 6 permissions (ordre d'affichage conservé) |
| `LEVEL_LABELS` | `core/templatetags/core_tags.py:9` | `Rupture`, `Stock bas`, `Stock sain` |
| `user_initials()` | `core/avatar.py:40` | Prénom + Nom, sinon 2 lettres du pseudo |
| `avatar_gradient()` | `core/avatar.py:77` | 6 dégradés, choisis par somme des codes du nom d'utilisateur |

---

## 1. Authentification

| Écran / fonction web | Endpoint API | Écran Flutter | Statut |
| --- | --- | --- | --- |
| Connexion (`/connexion/`, `auth/login.html`) | `POST /api/v1/auth/login/` | `ConnexionScreen` | OK |
| Message d'erreur « Veuillez entrer un nom d'utilisateur et un mot de passe corrects. » | 401 `detail` | idem | OK |
| Case « Se souvenir de moi » | ignorée côté API (JWT expire ; `REFRESH_TOKEN_LIFETIME` par défaut) | interrupteur « Rester connecté » (conserve le refresh token) | ÉCART (justifié) |
| « Mot de passe oublié ? » | — (flux e-mail Django) | renvoi vers la version web | ÉCART (justifié) |
| Inscription (`/inscription/`) : `username`, `password1`, `password2`, `first_name`, `email` | `POST /api/v1/auth/signup/` | `InscriptionScreen` | OK |
| Validations `UserCreationForm` (mots de passe différents, trop court, trop courant, numérique, similaire au pseudo) | mêmes messages, via `django.contrib.auth.password_validation` | messages affichés sous le champ | OK |
| « Déjà inscrit ? Se connecter » | — | lien local | OK |
| Bouton Google (`_google_btn.html`) | — | non porté | ÉCART (justifié) |
| Création de boutique (`/boutique/creer/`) : nom, téléphone, devise, adresse, logo, 4 couleurs | `POST /api/v1/shops/` | `CreerBoutiqueScreen` | OK |
| Message « Votre boutique est prête. Ajoutez vos premiers produits ! » | `detail` du 201 | toast après création | OK |
| Déconnexion (`/deconnexion/`, modale de confirmation) | `POST /api/v1/auth/logout/` (blacklist refresh) | modale → écran Connexion | OK |

## 2. Tableau de bord (`/`, `dashboard.html`)

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Titre « Bonjour, {prénom nom} » / « Voici ce qui se passe avec votre boutique aujourd'hui. » | `GET /api/v1/dashboard/` → `greeting_name` | `DashboardScreen` | OK |
| Bouton « Derniers 30 jours » (non fonctionnel côté web) | aucun paramètre | bouton visuellement identique, inerte | ÉCART (fidélité) |
| Carte « Revenu Total » = Σ `quantity × cost_price` + devise | `dashboard.value`, `dashboard.currency` | idem | OK |
| Carte « Nombre de Produits » | `dashboard.n_products` | idem | OK |
| Carte « Stock Bas » = `quantity <= alert_threshold` | `dashboard.n_low` | idem | OK |
| Carte « Catégories » | `dashboard.n_categories` | idem | OK |
| Badge « +{{ value_increase }}% » (toujours vide côté web) | `dashboard.value_increase` (0) | rendu identique | ÉCART (fidélité) |
| « Produits à Réapprovisionner » — 8 premiers triés par `quantity` : nom, stock, seuil | `dashboard.low_products[]` | idem | OK |
| Lien « Voir tous » → `/produits/?low=1` | — | navigation locale avec `low=1` | OK |
| « Derniers Mouvements » — 8 derniers : produit, type, quantité, par | `dashboard.recent_movements[]` | idem | OK |
| Graphique « Analyse des Mouvements » : 6 mois, `labels / entries / exits / total` | `dashboard.chart` | `fl_chart` (courbe stock total + barres entrées/sorties) | OK |
| Message « Aucun mouvement sur la période » | `chart` vide | idem | OK |
| Cartes KPI quand `can_view_products` est faux : tableau de bord vide | 200 + compteurs à `null` | idem | OK |

## 3. Produits

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Liste (`/produits/`) colonnes : case, Référence, Produit, Catégorie, Prix d'achat, Prix de vente, Stock, Statut, Actions | `GET /api/v1/products/` | `ProductsScreen` (desktop : `DataTable` triable) | OK |
| Recherche `?q=` sur nom **ou** sku **ou** nom de catégorie | `?q=` | champ de recherche + suggestions | OK |
| Filtre catégorie `?category=` : accepte l'id **ou** le nom (iexact) | `?category_id=` ou `?category=` | champ avec autocomplétion | OK |
| Champ « Toutes catégories » — l'id est retraduit en nom | idem | idem | OK |
| Case « Stock bas » `?low=1` | `?low=true` | interrupteur | OK |
| Bouton « Réinitialiser » (visible si au moins un filtre) | — | idem | OK |
| Pagination `per` ∈ {10, 25, 50, 100}, sinon 10 | `?page=&per=` | idem | OK |
| Pied « Affichage X à Y sur Z résultats », boutons Précédent / pages / Suivant | `count`, `start_index`, `end_index`, `has_next`, `num_pages` | idem | OK |
| Statuts : « Rupture » (≤ 0), « Stock bas » (≤ seuil), « En stock » | `level` + `level_label` | couleurs `LEVEL_COLORS` | OK |
| Prix affichés `floatformat:0` + devise | `cost_price`, `sale_price`, `currency` | `NumberFormat.fr_FR` | OK |
| Action « Mouvement de stock » → `/mouvements/nouveau/?product=ID` | — | formulaire pré-rempli | OK |
| Actions Modifier / Supprimer selon permissions | — | masquées si non autorisées | OK |
| Suppression multiple (`action=delete_selected`) — confirmation « Êtes-vous sûr… » | `DELETE /api/v1/products/bulk_delete/` | cases à cocher + dialogue | OK |
| Messages « N produit(s) supprimé(s). » / « Aucun produit sélectionné. » | `detail` | toast | OK |
| Création (`/produits/ajouter/`) : nom, référence, code-barres, catégorie, prix d'achat, prix de vente, quantité (**« Stock initial »**), seuil, description | `POST /api/v1/products/` | `ProductFormScreen` | OK |
| Aide « Laisser vide pour générer automatiquement. » (sku `PRD-0001`) | `sku` auto serveur si vide | aide affichée, champ laissé vide | OK |
| Aide « Facultatif — scannable ensuite depuis le menu Scanner. » | idem | idem | OK |
| Champ code-barres masqué si `barcode_field_enabled` est faux ; code lu conservé côté serveur | `shop.barcode_field_enabled` + `?barcode=` | champ masqué, code prérempli dans la requête de création | OK |
| Normalisation du code-barres (espaces supprimés) | `barcode` normalisé serveur | idem | OK |
| Unicité sku : « Cette référence existe déjà. » | 400 `errors.sku` | idem | OK |
| Unicité code-barres : « Le code-barres X est déjà attribué à un autre produit de cette boutique. » | 400 `errors.barcode` | idem | OK |
| Quantité négative : « La quantité ne peut pas être négative. » | 400 `errors.quantity` | idem | OK |
| Stock initial > 0 → mouvement « Stock initial » + notification `ADDED` | fait par l'endpoint | idem | OK |
| Message « Produit « X » ajouté. » | `detail` | toast | OK |
| Modification (`/produits/ID/modifier/`) : libellé quantité « Quantité en stock », aide « Toute correction est enregistrée comme ajustement dans l'historique. » | `PUT /api/v1/products/{uuid}/` | idem | OK |
| Changement de quantité → `record_adjustment()` + notification `ADJ` | fait par l'endpoint | idem | OK |
| Message « Produit modifié. » | `detail` | toast | OK |
| Suppression : confirmation « Supprimer ce produit ? », message « Produit supprimé. » | `DELETE /api/v1/products/{uuid}/` (suppression logique) | idem | OK |
| Vide : « Aucun produit trouvé. » | `count == 0` | idem | OK |
| Tri par défaut `-created_at` (plus récents d'abord) | `ordering=-created_at` | idem | OK |

## 4. Catégories (`/categories/`)

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Liste : Nom, Nombre de Produits, Actions | `GET /api/v1/categories/` (avec `product_count`) | `CategoriesScreen` | OK |
| Recherche `?q=` sur le nom | `?q=` | champ + suggestions | OK |
| Modale « Nouvelle Catégorie » (bouton + popup, pas une page) | `POST /api/v1/categories/` | dialogue (desktop) / feuille modale (mobile) | OK |
| Unicité (message « Cette catégorie existe déjà. », test `iexact`) | 409 `errors.name` | idem | OK |
| Message « Catégorie ajoutée. » | `detail` | toast | OK |
| Suppression : confirmation « Supprimer cette catégorie ? », message « Catégorie supprimée. » | `DELETE /api/v1/categories/{uuid}/` | idem | OK |
| Produits sans catégorie après suppression | `category = null` (SET_NULL) | idem | OK |
| Vide : « Aucune catégorie trouvée. » | `count == 0` | idem | OK |
| Tri par nom | `ordering=name` | idem | OK |

## 5. Mouvements (`/mouvements/`)

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Liste : Date (`d/m/Y H:i`), Produit, Type, Quantité, Note, Par | `GET /api/v1/movements/` | `MovementsScreen` | OK |
| Types « Entrée » (vert) / « Sortie » (orange) | `kind` + `kind_label` | idem | OK |
| Recherche `?q=` : produit, **ou** sku, **ou** note, **ou** utilisateur | `?q=` | champ + suggestions | OK |
| Filtre type : Tous / Entrées / Sorties | `?type=IN\|OUT` | sélecteur | OK |
| Filtre produit : liste déroulante `nom (sku)` | `?product_id=` | sélecteur + recherche | OK |
| Pagination **15** par page (différent des produits) | `per` par défaut 15, `?per=` autorisé | idem | OK |
| Pied « Affichage de X à Y sur Z mouvements » | idem | idem | OK |
| Création (`/mouvements/nouveau/`) : produit (autocomplétion), catégorie (**facultative**, filtre la liste de produits), type en deux cartes Entrée (« Augmente le stock ») / Sortie (« Diminue le stock »), quantité, note | `POST /api/v1/movements/` | `MovementFormScreen` | OK |
| Stock insuffisant : « Stock insuffisant (disponible : N). » | 400 `errors.quantity` | idem | OK |
| Quantité < 1 : « La quantité doit être au moins 1. » | 400 `errors.quantity` | idem | OK |
| Effet : `record_movement()` + notification `IN`/`OUT` avec message « Entrée de N — Produit (Q en stock) » | fait par l'endpoint | idem | OK |
| Message « Mouvement enregistré. » | `detail` | toast | OK |
| Ajuda catégorie « Facultatif : filtre la liste des produits. » | paramètre `category_id` (filtrage client) | aide + filtre dynamique de la liste produits | OK |
| Préremplissage par `?product=ID` | `?product_id=` | idem | OK |
| Vide : « Aucun mouvement trouvé. » | `count == 0` | idem | OK |

## 6. Notifications (`/notifications/`)

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Limite d'envoi 200 (`NOTIFICATION_FEED_LIMIT`) + mention « N plus anciennes » | `?limit=` (défaut 200), `truncated` | idem | OK |
| Colonnes : Type, Message, Produit, Quantité, Date, Son, Statut | `GET /api/v1/notifications/` | `NotificationsScreen` | OK |
| Pastille colorée `LEVEL_COLORS[level]` sur le libellé | `background`, `foreground` | idem | OK |
| Filtres : recherche, boutons couleur (Tous / Rupture / Stock bas / Stock sain), case « Non lues », « Réinitialiser » | `?q=&level=&unread=` | idem | OK |
| Pagination **25** par page, pilotée en JS | pagination locale | idem | OK |
| Recherche insensible aux accents (`normalize NFD`) | idem côté client | idem | OK |
| Recherche portant sur libellé, message, produit, code son, quantité | idem | idem | OK |
| Colonne « Son » : bouton de lecture + code (`AJOUT`, `ENTREE`, …) | `sound_code`, `tone` | bips générés aux fréquences de `NOTIFICATION_KINDS` | OK |
| Séquences audio (`sounds.js`) : `AJOUT [880,1175]`, `ENTREE [660,880]`, `SORTIE [440,330]`, `BAS [523,523,392]`, `RUPTURE [294,294,294,220]`, `AJUST [740,622,740]`, pas de 260 ms | idem | sequences identiques | OK |
| Bip des notifications non lues à l'arrivée sur la page (5 max, 700 ms d'écart) | idem | idem | OK |
| Interrupteur Son (par PC, `localStorage stockpro_sound_enabled`) | — | réglages locaux par appareil, défaut activé | ÉCART (justifié) |
| Marquer une comme lue | `POST /api/v1/notifications/{uuid}/read/` | icône coche | OK |
| « Tout lire » — « N notification(s) marquée(s) comme lue(s). » | `POST /api/v1/notifications/read_all/` | idem | OK |
| « Tout effacer » — confirmation, « N notification(s) supprimée(s). » | `DELETE /api/v1/notifications/` | idem | OK |
| Compteur de non lues (menu latéral + pastille barre supérieure) | `notifications.unread_count` | badge menu + badge cloche | OK |
| Toasts des nouvelles notifications (3 par visite, créneau de session) | `/sync/pull/` + champ `created_at` | toasts locaux au pull | ÉCART (justifié) |

## 7. Employés (`/employes/`) — propriétaire uniquement

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Liste : Nom (initiales + nom complet), Rôle « Employé », Permissions, Actions | `GET /api/v1/employees/` | `EmployeesScreen` | OK |
| Recherche `?q=` : username, prénom, nom, email | `?q=` | champ + suggestions | OK |
| Initiales = 2 premières lettres du username en majuscules | idem | idem | OK |
| Pastilles de permissions accordées (libellés de `PERMISSIONS`) | `granted_permissions[]` | idem | OK |
| Création : nom d'utilisateur, prénom, nom, mot de passe (obligatoire) + 6 cases de permissions (`can_view_products` cochée par défaut) | `POST /api/v1/employees/` | `EmployeeFormScreen` | OK |
| Doublon : « Ce nom d'utilisateur est déjà pris. » | 400 `errors.username` | idem | OK |
| Édition : mot de passe facultatif (« Laisser vide pour ne pas changer. ») | `PUT /api/v1/employees/{uuid}/` | idem | OK |
| Messages « Compte « X » créé. » / « Employé mis à jour. » | `detail` | toast | OK |
| Suppression : confirmation, message « Compte employé supprimé. » | `DELETE /api/v1/employees/{uuid}/` | idem | OK |
| Le propriétaire n'apparaît pas dans la liste | `is_owner=false` filtré | idem | OK |
| Vide : « Aucun employé trouvé. » / « Aucun employé ne correspond à « X ». » | `count == 0` | libellé selon recherche | OK |
| Rôle : « Propriétaire » / « Employé » | `role` | en-tête et fiche profil | OK |

## 8. Paramètres / thème (`/parametres/`) — propriétaire uniquement

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Sections : Identité, Couleurs du site, Aperçu en direct, Fonctionnalités | `GET /api/v1/shops/current/` | `SettingsScreen` | OK |
| Nom, Téléphone, Devise, Adresse, Logo | `PUT /api/v1/shops/current/` | idem | OK |
| Couleurs `primary / sidebar / header / background` (sélecteur + hexadécimal affiché) | idem | idem | OK |
| Aperçu en direct réactif | calcul local immédiat | idem | OK |
| Validateur de couleur « Couleur invalide (format #rrggbb). » | 400 `errors.<couleur>` | idem | OK |
| « Réinitialiser » — confirmation, remet les 4 défauts du modèle, message « Thème réinitialisé. » | `POST /api/v1/shops/current/reset_theme/` | idem | OK |
| Interrupteur « Scanner de codes-barres » (page, menu, API) | `scanner_enabled` | idem | OK |
| Interrupteur « Champ « Code-barres » » (formulaires produit) | `barcode_field_enabled` | idem | OK |
| Interrupteur « Son des notifications » + « Tester le son » (réglage local) | — | réglages locaux | ÉCART (fidélité) |
| Favicon suit le logo, sinon initiales (SVG) | `logo_url`, `initials` | idem | OK |
| Message « Paramètres enregistrés. » | `detail` | toast | OK |
| Non-propriétaire → 403 « Accès Interdit » | 403 JSON `detail` | écran 403 / entrée masquée | OK |

## 9. Profil (modale de la barre supérieure)

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Affichage : nom, rôle · boutique, email (désactivé), téléphone, bio, photo | `GET /api/v1/profile/` | `ProfileScreen` | OK |
| « Membre depuis », « Dernière connexion » (format `fr-FR` long) | `date_joined`, `last_login` | `intl fr_FR` | OK |
| Pastilles des permissions | `permissions[]` | idem | OK |
| Envoi photo (multipart, JPEG/PNG/WebP/GIF, 2 Mo max) | `POST /api/v1/profile/` (multipart) | image_picker / file_picker | OK |
| Aide « JPEG, PNG, WebP ou GIF — 2 Mo maximum. Sans photo, vos initiales sont affichées. » | idem | aide affichée | OK |
| Messages « Photo trop lourde (2 Mo maximum). », « Format non supporté (JPEG, PNG, WebP ou GIF). », « Fichier image invalide. » | 400 `errors.photo` | idem | OK |
| « Retirer la photo » → « Photo retirée — vos initiales sont affichées. » | `DELETE /api/v1/profile/photo/` | idem | OK |
| « Profil mis à jour. » | `detail` | toast | OK |
| Avatar : photo sinon initiales, dégradé stable | `avatar{url, initials, gradient, has_photo}` | idem | OK |

## 10. Scanner (`/scanner/`) — si `shop.scanner_enabled`

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Modes : « Sortie (vente) », « Entrée (réception) », « Fiche produit » | — | `ScanScreen`, mode initial `OUT` (ou `?mode=`) | OK |
| Sans `can_manage_stock` → mode forcé `CARD`, modes IN/OUT masqués | idem | idem | OK |
| Mode inconnu (`?mode=XX`) → repli sur `CARD` | idem | idem | OK |
| Titre du champ : « Sortie de stock (vente) » / « Entrée de stock (réception) » / « Fiche produit » | idem | idem | OK |
| Saisie clavier USB/Bluetooth (le code « tapé » + Entrée), champ toujours focalisé | `GET /api/v1/scan/?code=` | champ focalisé en permanence (desktop) | OK |
| Caméra (mobile) via `mobile_scanner` | idem | idem | PLAN |
| Recherche : code-barres d'abord, puis `sku` | `?code=` | base locale d'abord, puis API | OK |
| Code inconnu → « Produit introuvable : CODE » + encadré « Créer ce produit » avec `?barcode=CODE` | 200 `{found: false, code}` | idem | OK |
| Anti-doublon **800 ms** sur le même code | idem | idem | OK |
| Lot : rescanner le même produit **+1** à sa quantité | idem | idem | OK |
| Ligne : nom, référence (« Sans référence » si vide), badge « N en stock », quantité éditable (min 1), bouton Retirer | idem | idem | OK |
| Note (facultative, 200 caractères) — visible seulement en modes IN/OUT | `note` | idem | OK |
| « Vider la liste », « Réinitialiser » (vide la liste **et** la note) | — | idem | OK |
| Bouton « Valider » désactivé tant que la liste est vide | — | idem | OK |
| Validation du lot : **atomique** — si une ligne est refusée, rien n'est enregistré | `POST /api/v1/scan/movements/` | hors-ligne : movements dans l'outbox | OK |
| Erreurs du lot : « Ligne N : format invalide. », « … la quantité doit être un nombre entier. », « … la quantité doit être au moins 1. », « … produit introuvable dans cette boutique. », « Ligne N — X : stock insuffisant (disponible : Q). » | 400 `errors[]` | idem | OK |
| « Type de mouvement invalide : utilisez "IN" ou "OUT". » | 400 | idem | OK |
| « Aucune ligne à enregistrer. » | 400 | idem | OK |
| Retour « N ligne(s) enregistrée(s). » | `count` | idem | OK |
| Mode fiche : nom, référence, badge stock, catégorie (« Sans catégorie » si vide), lien « Modifier ce produit » (si `can_edit_products`) | `scan` response | idem | OK |
| Bips succès (880 puis 1320 Hz) / erreur (200 puis 140 Hz) | idem | idem | OK |
| Aide : 5 lignes, conditionnées aux permissions | — | idem | OK |
| Scanner désactivé → page et API en 403, entrées de menu masquées | 403 | idem | OK |

## 11. Éléments globaux

| Élément web | Endpoint API | Flutter | Statut |
| --- | --- | --- | --- |
| Menu latéral, ordre : Tableau de bord, Ajouter un produit (si `can_add_products`), Produits, Mouvements, Scanner (si `scanner_enabled` et `can_view_products`), Catégories, Employés, Notifications ; puis Paramètres, Déconnexion | `GET /api/v1/profile/` fournit `permissions` | menu desktop identique ; barre basse mobile | OK |
| Note : « Employés » et « Paramètres » sont **affichés** dans le menu web même pour un employé (403 au clic) | idem | masqués si non propriétaire | ÉCART (choix plus sûr, documenté) |
| Couleur du menu = `sidebar_color`, logo ou initiales | `shop.logo_url`, `shop.initials` | idem | OK |
| Barre supérieure : fil d'Ariane, recherche produits (autocomplétion), interrupteur Son, cloche, avatar | `suggest` endpoints | barre supérieure desktop | OK |
| Toasts iOS (max 3, 4500 ms, titres « C'est noté » / « Action impossible » / « Attention » / « Information ») | — | SnackBar / couche de toasts identique | OK |
| Badge « en attente » sur les objets non synchronisés | `sync_state` renvoyé par le pull | badge local | OK |
| Indicateur « En ligne / Hors ligne / Synchronisation… / N opérations en attente » + « Synchroniser maintenant » | `/sync/status/` | `SyncStatusChip` permanent | OK |

## 12. Règles de permission (table unique)

| Règle web (`decorators.py`) | API | Flutter |
| --- | --- | --- |
| `shop_required` : redirection `create_shop` si pas de `Membership` | 409 `{code: "shop_required"}` | écran « Créer une boutique » |
| `perm_required("can_view_products")` → 403 | `IsShopMember` + `HasPermission` | entrées de menu masquées, écrans protégés |
| `perm_required("can_add_products")` | idem | bouton « Ajouter un Produit » masqué |
| `perm_required("can_edit_products")` | idem | crayon masqué |
| `perm_required("can_delete_products")` | idem | poubelle et suppression multiple masqués |
| `perm_required("can_manage_stock")` | idem | « Nouveau Mouvement », onglet Scanner IN/OUT masqués |
| `perm_required("can_manage_categories")` | idem | « Nouvelle Catégorie » masquée |
| `owner_required` (Paramètres, Employés) | `IsShopOwner` | section « Plus » réduite |
| `scanner_required` (`shop.scanner_enabled`) | idem | onglet Scanner retiré |

`Membership.has(perm)` renvoie `True` pour le propriétaire quel que soit le
drapeau : l'API utilise le même `has()`, jamais les drapeaux bruts.

## 13. Écart assumés

| Écart | Raison |
| --- | --- |
| Mot de passe oublié non porté dans l'app | Le flux passe par un e-mail ; l'app renvoie vers la page web. |
| Connexion Google non portée | OAuth web ; hors périmètre mobile/desktop. |
| Employés / Paramètres masqués dans l'« interface » du client | Le web les affiche puis renvoie 403 ; sur mobile l'écran 403 est une impasse. |
| Notifications livrées par lots de 200, pas de toasts de session | Le curseur de synchronisation remplace le créneau de session ; même limite de 200 conservée. |
| Interrupteur Son par appareil, pas par « PC » | Flutter n'a pas de `localStorage` partagé ; le réglage est local et activé par défaut, comme sur le web. |
| Bouton « Derniers 30 jours » et badge « +0% » conservés mais inertes | Le web ne les branche à rien ; les reproduire à l'identique évite de promettre un filtrage inexistant. |
| Référence (`sku`) attribuée par le serveur | La génération `PRD-000N` doit rester unique : le client laisse le champ vide. |

## 14. Formatage

| Règle web | Flutter |
| --- | --- |
| `floatformat:0` + `shop.currency` | `NumberFormat('#,##0', 'fr_FR')` + devise |
| Dates `d/m/Y H:i` (mouvements) | `DateFormat('dd/MM/yyyy HH:mm', 'fr_FR')` |
| Dates profile : `toLocaleDateString('fr-FR', {day:'2-digit', month:'long', year:'numeric'})` | `DateFormat('d MMMM y', 'fr_FR')` |
| Mois du graphique : `Jan, Fév, Mar, Avr, Mai, Juin, Juil, Août, Sep, Oct, Nov, Déc` | `DateFormat.MMM('fr_FR')` + table de correspondance |
| Séparateur de milliers | espace insécable (`fr_FR`) |