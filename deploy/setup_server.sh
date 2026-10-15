#!/usr/bin/env bash
# =============================================================================
# PREPARATION D'UN VPS (Ubuntu 22.04 / 24.04) UNIQUEMENT.
#
# !! NE PAS utiliser sur alwaysdata (ou tout autre PaaS / hebergement
#    mutualise) : il n'y a pas de root. Sur alwaysdata, utilise :
#        bash deploy/deploy_alwaysdata.sh
#
# A executer UNE FOIS, en root, sur un serveur VPS neuf :
#     sudo bash deploy/setup_server.sh
#
# Ce script :
#   1. Installe les paquets systeme necessaires (Python, build, git, ufw).
#   2. Cree un utilisateur Linux NON-ROOT (avec acces sudo) pour l'appli.
#   3. Genere et applique un mot de passe root aleatoire (affiche a la fin).
#   4. Durcit SSH (connexion root par mot de passe interdite).
#   5. Configure le pare-feu (SSH + port de Gunicorn).
#   6. Prepare le dossier d'installation de l'application.
#
# Variables surchargeables :
#   APP_USER   (defaut: stock)        utilisateur non-root
#   APP_DIR    (defaut: /var/www/stock) dossier de l'application
#   SSH_PORT   (defaut: 22)           port SSH
#   GUNICORN_PORT (defaut: 8000)      port HTTP ouvert dans le pare-feu
#   ROOT_PASSWORD                     mot de passe root impose (sinon aleatoire)
# =============================================================================
set -euo pipefail

APP_USER="${APP_USER:-stock}"
APP_DIR="${APP_DIR:-/var/www/stock}"
SSH_PORT="${SSH_PORT:-22}"
GUNICORN_PORT="${GUNICORN_PORT:-8000}"

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$*"; }

if [[ "${EUID}" -ne 0 ]]; then
    echo "Ce script doit etre execute en root : sudo bash $0" >&2
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "Ce script suppose une distribution basee sur apt (Ubuntu / Debian)." >&2
    exit 1
fi

# --- 1. Paquets systeme ------------------------------------------------------
log "Mise a jour de la liste des paquets"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y

log "Installation des dependances systeme"
apt-get install -y \
    python3 python3-venv python3-pip python3-dev \
    build-essential git curl ca-certificates ufw \
    libjpeg-dev zlib1g-dev libfreetype6-dev libwebp-dev

# --- 2. Utilisateur non-root -------------------------------------------------
if id -u "${APP_USER}" >/dev/null 2>&1; then
    log "L'utilisateur '${APP_USER}' existe deja"
else
    log "Creation de l'utilisateur non-root '${APP_USER}'"
    adduser --disabled-password --gecos "" "${APP_USER}"
    usermod -aG sudo "${APP_USER}"

    # Reprend les cles SSH de root pour permettre la connexion par cle.
    if [[ -s /root/.ssh/authorized_keys ]]; then
        install -d -m 700 -o "${APP_USER}" -g "${APP_USER}" "/home/${APP_USER}/.ssh"
        install -m 600 -o "${APP_USER}" -g "${APP_USER}" \
            /root/.ssh/authorized_keys "/home/${APP_USER}/.ssh/authorized_keys"
    fi
fi

# --- 3. Mot de passe root ----------------------------------------------------
ROOT_PASSWORD="${ROOT_PASSWORD:-$(head -c 24 /dev/urandom | base64 | tr -d '/+=' | cut -c1-20)}"
log "Definition d'un mot de passe root"
echo "root:${ROOT_PASSWORD}" | chpasswd

# --- 4. Durcissement SSH -----------------------------------------------------
SSHD_CONFIG="/etc/ssh/sshd_config"
if [[ -f "${SSHD_CONFIG}" ]]; then
    log "Durcissement de SSH (${SSHD_CONFIG})"
    cp "${SSHD_CONFIG}" "${SSHD_CONFIG}.bak.$(date +%s)"
    sed -i -E 's/^#?PermitRootLogin.*/PermitRootLogin prohibit-password/' "${SSHD_CONFIG}"
    sed -i -E "s/^#?Port .*/Port ${SSH_PORT}/" "${SSHD_CONFIG}"
    systemctl reload ssh 2>/dev/null || systemctl reload sshd 2>/dev/null || true
fi

# --- 5. Pare-feu -------------------------------------------------------------
log "Configuration du pare-feu (ufw)"
ufw allow "${SSH_PORT}/tcp"
ufw allow "${GUNICORN_PORT}/tcp"
ufw --force enable

# --- 6. Dossier de l'application --------------------------------------------
log "Preparation du dossier '${APP_DIR}'"
mkdir -p "${APP_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

cat <<EOF

=============================================================================
 Preparation terminee.
=============================================================================
 Utilisateur non-root : ${APP_USER}
 Mot de passe root    : ${ROOT_PASSWORD}
 Dossier appli        : ${APP_DIR}
 Port Gunicorn        : ${GUNICORN_PORT}

 Etapes suivantes :
   1. Donne un mot de passe a '${APP_USER}' (necessaire pour sudo) :
        sudo passwd ${APP_USER}
   2. Connecte-toi en '${APP_USER}', place le code dans ${APP_DIR}.
   3. Copie et remplis la configuration :
        cp ${APP_DIR}/.env.example ${APP_DIR}/.env
   4. Lance le deploiement :
        bash ${APP_DIR}/deploy/deploy.sh

 CONSERVE le mot de passe root ci-dessus. Pour en imposer un precis :
   ROOT_PASSWORD='MonMotDePasse' sudo -E bash deploy/setup_server.sh
=============================================================================
EOF
