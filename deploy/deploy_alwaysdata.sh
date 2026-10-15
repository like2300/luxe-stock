#!/usr/bin/env bash
# =============================================================================
# Deploiement sur alwaysdata (hebergement mutualise / PaaS) - SANS root.
#
# A executer dans le dossier du projet, connecte en SSH avec ton compte
# alwaysdata (pas besoin de sudo, pas de systemd) :
#     bash deploy/deploy_alwaysdata.sh
#
# Le script :
#   1. Cree l'environnement virtuel et installe les dependances.
#   2. Cree .env a partir de .env.example s'il n'existe pas.
#   3. Applique les migrations et collecte les fichiers statiques (WhiteNoise).
#   4. Cree le superutilisateur si DJANGO_SUPERUSER_* est defini.
#   5. Affiche les valeurs a saisir dans alwaysdata (Web > Sites).
#
# Le site web lui-meme se configure dans l'interface alwaysdata
# (Web > Sites > Ajouter un site), pas dans ce script (voir la sortie finale).
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
VENV_DIR="${VENV_DIR:-${APP_DIR}/.venv}"
# Sur alwaysdata, la commande Python est 'python' (jamais 'python3').
PYTHON_BIN="${PYTHON_BIN:-python}"

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$*"; }

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "Commande '${PYTHON_BIN}' introuvable. Sur alwaysdata, utilise 'python'." >&2
    exit 1
fi

cd "${APP_DIR}"

# --- 1. Environnement virtuel & dependances ---------------------------------
if [[ ! -d "${VENV_DIR}" ]]; then
    log "Creation de l'environnement virtuel (${VENV_DIR})"
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

log "Installation des dependances Python"
"${VENV_DIR}/bin/pip" install --upgrade pip wheel
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

# --- 2. Fichier .env ---------------------------------------------------------
if [[ ! -f "${APP_DIR}/.env" ]]; then
    log "Creation de .env depuis .env.example"
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    chmod 600 "${APP_DIR}/.env"
    warn "Edite ${APP_DIR}/.env (SECRET_KEY, ALLOWED_HOSTS, emails...) puis relance."
    warn "Ne relance pas tout de suite : remplis d'abord le fichier .env."
    exit 0
fi

# --- 3. Migrations & fichiers statiques -------------------------------------
log "Application des migrations de base de donnees"
"${VENV_DIR}/bin/python" manage.py migrate --noinput

log "Collecte des fichiers statiques (WhiteNoise)"
"${VENV_DIR}/bin/python" manage.py collectstatic --noinput

# --- 4. Superutilisateur (optionnel) ----------------------------------------
if [[ -n "${DJANGO_SUPERUSER_EMAIL:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
    log "Creation du superutilisateur ${DJANGO_SUPERUSER_EMAIL}"
    "${VENV_DIR}/bin/python" manage.py createsuperuser --noinput \
        --email "${DJANGO_SUPERUSER_EMAIL}" 2>/dev/null \
        || warn "Superutilisateur deja existant ou creation ignoree."
fi

# --- 5. Configuration du site (a saisir dans alwaysdata) ---------------------
cat <<EOF

=============================================================================
 Dependances, migrations et statiques : OK.
 Il reste a declarer le site dans l'interface alwaysdata.
=============================================================================
 Alwaysdata > Web > Sites > (ton site, ou << Ajouter un site >>) :

   Type                 : Python WSGI
   Adresse/domaine      : miraclekidsshop.alwaysdata.net
   Application path     : ${APP_DIR}/stockpro/wsgi.py
   Working directory    : ${APP_DIR}
   Virtualenv directory : ${VENV_DIR}
   Version de Python    : la plus recente (3.x)
   Variables d'environ. : (optionnel - deja dans .env)

 Ensuite : active << SSL >> + << Force HTTPS usage >> dans le meme ecran.

 Journaux uWSGI (en cas d'erreur 500) :
   ~/admin/logs/uwsgi/<id_du_site>.log

 Astuce : apres chaque mise a jour du code, relance simplement :
   bash deploy/deploy_alwaysdata.sh
=============================================================================
EOF
