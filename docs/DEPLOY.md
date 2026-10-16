# Déploiement de StockPro

Deux chemins sont prévus dans `deploy/` :

| Cible | Script | Prérequis |
|---|---|---|
| VPS Ubuntu/Debian (systemd + Gunicorn) | `deploy/setup_server.sh` puis `deploy/deploy.sh` | root / sudo |
| alwaysdata (PaaS mutualisé, sans root) | `deploy/deploy_alwaysdata.sh` | compte alwaysdata en SSH |

> Ne jamais lancer `setup_server.sh` sur un hébergement mutualisé : il n'y a pas
> de root. Inversement, `deploy_alwaysdata.sh` n'installe pas de service systemd.

---

## 1. Configuration (`.env`)

Commun aux deux cas :

```bash
cp .env.example .env
chmod 600 .env
```

À remplir impérativement :

| Variable | Rôle |
|---|---|
| `SECRET_KEY` | clé Django (jamais commiter le `.env`) |
| `DEBUG` | `False` en production |
| `ALLOWED_HOSTS` | domaines/IP séparés par des virgules |
| `CSRF_TRUSTED_ORIGINS` | ex. `https://mon-domaine.tld` |
| `SITE_BASE_URL` + `ACCOUNT_DEFAULT_HTTP_PROTOCOL` | doivent avoir le même schéma (`https` en prod) |
| `EMAIL_*` / `DEFAULT_FROM_EMAIL` | relais SMTP Brevo |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth Google (callback = `SITE_BASE_URL/accounts/google/login/callback/`) |
| `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` | `True` uniquement derrière HTTPS |

Paramètres propres aux scripts (non lus par Django) :

| Variable | Défaut | Rôle |
|---|---|---|
| `APP_USER` | `stock` | utilisateur Linux non-root |
| `APP_DIR` | `/var/www/stock` | dossier d'installation |
| `REPO_URL` | — | dépôt à cloner si le dossier est vide |
| `GUNICORN_BIND` | `0.0.0.0:8000` | interface d'écoute |
| `GUNICORN_WORKERS` | vide = `2×CPU+1` | workers |
| `GUNICORN_LOGLEVEL` | `info` | niveau de log |
| `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` | — | crée le superuser en non-interactif |

---

## 2. VPS Ubuntu 22.04 / 24.04

### 2.1. Préparation (une seule fois, en root)

```bash
sudo bash deploy/setup_server.sh
```

Variables surchargeables : `APP_USER`, `APP_DIR`, `SSH_PORT`, `GUNICORN_PORT`,
`ROOT_PASSWORD`.

Le script installe Python/git/build-essential/ufw, crée l'utilisateur non-root
(avec sudo), durcit SSH (`PermitRootLogin prohibit-password`), ouvre le
pare-feu et prépare `APP_DIR`. Il affiche à la fin le mot de passe root
aléatoire — **à conserver**.

### 2.2. Déploiement (en utilisateur non-root)

```bash
sudo passwd stock            # définir le mot de passe de l'utilisateur
# ... se connecter en « stock », placer le code dans APP_DIR ...
cp .env.example .env         # remplir
bash deploy/deploy.sh
```

Le script exécute, dans l'ordre :

1. `git clone` (si `REPO_URL` défini et pas de `manage.py`) ou `git pull --ff-only` ;
2. création du virtualenv `.venv` + `pip install -r requirements.txt` ;
3. création de `.env` depuis `.env.example` s'il manque (puis arrêt conseillé pour le remplir) ;
4. `manage.py migrate --noinput` ;
5. `manage.py collectstatic --noinput` (WhiteNoise) ;
6. `manage.py createsuperuser --noinput` si `DJANGO_SUPERUSER_*` est défini ;
7. installation du service systemd à partir de `deploy/stockpro.service.template`, puis `daemon-reload` / `enable` / `restart`.

### 2.3. Vérification

```bash
sudo systemctl status stockpro
sudo journalctl -u stockpro -f
curl -I http://127.0.0.1:8000/
```

Variables utiles : `SKIP_GIT_PULL=1` pour ne pas tirer le code,
`SERVICE_NAME` pour renommer l'unité.

### 2.4. Reverse proxy / HTTPS

Gunicorn écoute par défaut sur `0.0.0.0:8000`. Pour servir en HTTP sur le
port 80 sans root, dans `.env` :

```
GUNICORN_BIND=0.0.0.0:80
```

et décommenter dans `deploy/stockpro.service.template` :

```
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```

Derrière nginx/caddy : terminer le TLS au proxy, garder
`SECURE_SSL_REDIRECT=False` (le proxy annonce `X-Forwarded-Proto`), et garder
`SESSION_COOKIE_SECURE=True` / `CSRF_COOKIE_SECURE=True`.

---

## 3. alwaysdata (PaaS, sans root)

Connecté en SSH sur le compte alwaysdata, à la racine du projet :

```bash
bash deploy/deploy_alwaysdata.sh
```

Première exécution : le script crée `.env` puis **s'arrête** — remplir le
fichier avant de relancer.

Ensuite il crée le virtualenv, installe les dépendances, applique les
migrations et collecte les statiques, puis affiche les valeurs à saisir dans
l'interface (**Web > Sites**) :

```
Type                 : Python WSGI
Adresse/domaine      : miraclekidsshop.alwaysdata.net
Application path     : <APP_DIR>/stockpro/wsgi.py
Working directory    : <APP_DIR>
Virtualenv directory : <APP_DIR>/.venv
Version de Python    : 3.x (la plus récente)
```

Activer **SSL** + **Force HTTPS usage** sur le même écran.

> Sur alwaysdata, la commande Python est `python` (jamais `python3`) ; le bloc
> `GUNICORN_*` est ignoré, la plateforme fournit uWSGI.

Après chaque mise à jour du code, relancer simplement :

```bash
bash deploy/deploy_alwaysdata.sh
```

Journaux uWSGI en cas d'erreur 500 : `~/admin/logs/uwsgi/<id_du_site>.log`.

---

## 4. Mise à jour d'une installation existante

```bash
# VPS
bash deploy/deploy.sh

# alwaysdata
bash deploy/deploy_alwaysdata.sh
```

Les deux refont dépendances, migrations, collectstatic et redémarrent le
service (systemd) ou laissent le serveur de la plateforme tel quel.

---

## 5. Dépannage

| Symptôme | Piste |
|---|---|
| `Aucun manage.py ... et REPO_URL non defini` | lancer depuis la racine ou définir `REPO_URL` |
| `git pull` échoue | modifications locales → corriger ou `SKIP_GIT_PULL=1` |
| Erreur 500, cookies qui bouclent | `SECURE_SSL_REDIRECT=True` sans HTTPS réel → `False` |
| Callback Google en `https://` alors que tout est en `http` | `ACCOUNT_DEFAULT_HTTP_PROTOCOL` doit suivre le schéma de `SITE_BASE_URL` |
| Statiques 404 | `python manage.py collectstatic --noinput` puis vérifier `staticfiles/` |
| Service qui redémarre en boucle | `sudo journalctl -u stockpro -e` |
| Port 80 refusé | commenter le bind `:80` ou décommenter `CAP_NET_BIND_SERVICE` |
