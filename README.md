# StockPro — gestion de stock multi-boutiques (Django)

## Installation
    python -m venv env && env\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser   # optionnel (/admin/)
    python manage.py runserver

Ouvrir http://127.0.0.1:8000 → « Créer un compte » → créer la boutique.

## Configuration (.env)
Tout est lu depuis `.env` (ignoré par git, ne jamais le commiter) :
`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `SITE_BASE_URL`, le relais SMTP Brevo
(`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`,
`EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`) et les identifiants Google
(`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).

`ACCOUNT_DEFAULT_HTTP_PROTOCOL` doit correspondre au schéma de `SITE_BASE_URL`
(`http` en local), sinon Google renverrait le callback sur `https://` alors que
le serveur de développement n'écoute qu'en `http`.

## Connexion avec Google (django-allauth)
Le bouton Google est affiché sur les pages « Connexion » et « Créer un compte »
et ouvre directement le sélecteur de comptes Google (`prompt=select_account`).
Un nouvel utilisateur Google est créé automatiquement, puis redirigé vers la
création de sa boutique.

Dans la console Google Cloud (API « OAuth 2.0 Client ID » de type *Web
application*), déclarez l'URI de redirectionAuthorized redirect URI :

    http://127.0.0.1:8000/accounts/google/login/callback/

et ajoutez `http://127.0.0.1:8000` dans *Authorized JavaScript origins*.
L'URI doit correspondre **exactement**, port compris.

Le bouton est masqué automatiquement si `GOOGLE_CLIENT_ID` ou
`GOOGLE_CLIENT_SECRET` est vide.

## Administration (django-unfold)
`/admin/` est stylé par Unfold, avec onglets sur les formulaires, recherche,
filtres, autocomplétion et badges de niveau de stock. Les mouvements de stock
sont en lecture seule : ils font partie de l'historique.

## Notifications (page dédiée)
Menu « Notifications » (cloche de la barre supérieure). Chaque événement produit
une notification avec :

- un **code son** — `AJOUT`, `ENTREE`, `SORTIE`, `BAS`, `RUPTURE`, `AJUST` ;
- un **code couleur** selon la quantité — rouge (rupture, ≤ 0), orange (stock
  bas, ≤ seuil), vert (stock sain) ;
- un **bip** audible, généré par la Web Audio API (aucun fichier son à fournir).

Le bip est joué à l'arrivée sur la page pour les notifications non lues, et
reste déclenchable au clic via la colonne « Bip » ou la légende des codes.
Un interrupteur permet de le couper. Les alertes de seuil ne sont émises qu'au
**franchissement** du seuil, avec escalade vers la rupture quand le stock
atteint zéro.

La quantité en stock est modifiable aussi bien à la création qu'à la
modification d'un produit. Chaque correction est tracée comme mouvement
« Ajustement manuel », donc le stock reste toujours justifié par un mouvement.

## Fonctionnement
- Inscription → création de la boutique → le compte devient propriétaire.
- Le propriétaire crée des employés (menu Employés) et coche leurs permissions :
  voir / ajouter / modifier / supprimer les produits, gérer le stock, gérer les catégories.
- Paramètres (propriétaire uniquement) : nom, devise, logo et 4 couleurs du thème.
- Les données sont isolées par boutique.
- Le stock ne se modifie que par des mouvements (entrée / sortie), historisés :
  toute correction manuelle de la quantité génère elle aussi un mouvement.

## Tests
    python manage.py test
