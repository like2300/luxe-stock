#!/usr/bin/env bash
# =============================================================================
# Deploiement / mise a jour de StockPro.
#
# A executer a la racine du projet, en tant que l'utilisateur NON-ROOT de
# l'application (voir deploy/setup_server.sh) :
#     bash deploy/deploy.sh
#
# Le script :
#   1. (optionnel) clone le depot si le dossier est vide.
#   2. Cree l'environnement virtuel et installe les dependances.
#   3. Cree .env a partir de .env.example s'il n'existe pas.
#   4. Applique les migrations.
#   5. Collecte les fichiers statiques (WhiteNoise).
#   6. Cree le superutilisateur si DJANGO_SUPERUSER_* est defini.
#   7. Installe / met a jour le service systemd (via sudo) et le redemarre.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${APP_DIR}/.venv"
SERVICE_NAME="${SERVICE_NAME:-stockpro}"

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$*"; }

# sudo seulement si on n'est pas deja root.
SUDO=""
if [[ "${EUID}" -ne 0 ]]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        warn "sudo introuvable ; l'installation du service systemd peut echouer."
    fi
fi

# Charge .env (pour APP_USER, REPO_URL, GUNICORN_*).
if [[ -f "${APP_DIR}/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "${APP_DIR}/.env"
    set +a
fi
APP_USER="${APP_USER:-$(id -un)}"

# --- 1. Recuperation du code ------------------------------------------------
if [[ ! -f "${APP_DIR}/manage.py" ]]; then
    if [[ -n "${REPO_URL:-}" ]]; then
        log "Clonage du depot dans ${APP_DIR}"
        git clone "${REPO_URL}" "${APP_DIR}"
    else
        echo "Aucun manage.py dans ${APP_DIR} et REPO_URL non defini." >&2
        exit 1
    fi
elif [[ -d "${APP_DIR}/.git" && "${SKIP_GIT_PULL:-0}" != "1" ]]; then
    log "Mise a jour du code (git pull)"
    git -C "${APP_DIR}" pull --ff-only || warn "git pull ignore (modifications locales ?)"
fi

cd "${APP_DIR}"

# --- 2. Environnement virtuel & dependances ---------------------------------
if [[ ! -d "${VENV_DIR}" ]]; then
    log "Creation de l'environnement virtuel (${VENV_DIR})"
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

log "Installation des dependances Python"
"${VENV_DIR}/bin/pip" install --upgrade pip wheel
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

# --- 3. Fichier .env ---------------------------------------------------------
if [[ ! -f "${APP_DIR}/.env" ]]; then
    log "Creation de .env depuis .env.example"
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    chmod 600 "${APP_DIR}/.env"
    warn "Edite ${APP_DIR}/.env (SECRET_KEY, ALLOWED_HOSTS, emails...) puis relance."
fi

# --- 4. Migrations -----------------------------------------------------------
log "Application des migrations de base de donnees"
"${VENV_DIR}/bin/python" manage.py migrate --noinput

# --- 5. Fichiers statiques ---------------------------------------------------
log "Collecte des fichiers statiques (WhiteNoise)"
"${VENV_DIR}/bin/python" manage.py collectstatic --noinput

# --- 6. Superutilisateur (optionnel, non interactif) -------------------------
if [[ -n "${DJANGO_SUPERUSER_EMAIL:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
    log "Creation du superutilisateur ${DJANGO_SUPERUSER_EMAIL}"
    "${VENV_DIR}/bin/python" manage.py createsuperuser --noinput \
        --email "${DJANGO_SUPERUSER_EMAIL}" 2>/dev/null \
        || warn "Superutilisateur deja existant ou creation ignoree."
fi

# --- 7. Service systemd ------------------------------------------------------
log "Installation du service systemd '${SERVICE_NAME}'"
UNIT_TMP="$(mktemp)"
sed -e "s|__APP_USER__|${APP_USER}|g" \
    -e "s|__APP_DIR__|${APP_DIR}|g" \
    "${APP_DIR}/deploy/stockpro.service.template" > "${UNIT_TMP}"

${SUDO} install -m 644 "${UNIT_TMP}" "/etc/systemd/system/${SERVICE_NAME}.service"
rm -f "${UNIT_TMP}"

${SUDO} systemctl daemon-reload
${SUDO} systemctl enable "${SERVICE_NAME}"
${SUDO} systemctl restart "${SERVICE_NAME}"

# S'assure que l'utilisateur de l'appli possede bien les fichiers generes.
if [[ "${EUID}" -eq 0 && "${APP_USER}" != "root" ]]; then
    chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}" 2>/dev/null || true
fi

BIND="$(grep -E '^GUNICORN_BIND=' "${APP_DIR}/.env" 2>/dev/null | cut -d= -f2 || true)"
cat <<EOF

=============================================================================
 Deploiement termine.
=============================================================================
 Service   : ${SERVICE_NAME}   (sudo systemctl status ${SERVICE_NAME})
 Ecoute    : ${BIND:-0.0.0.0:8000}
 Journal   : sudo journalctl -u ${SERVICE_NAME} -f
 Statiques : ${APP_DIR}/staticfiles
=============================================================================
EOF
