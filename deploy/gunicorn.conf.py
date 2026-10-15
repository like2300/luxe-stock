"""Configuration Gunicorn pour StockPro.

Utilise par le service systemd :
    gunicorn -c deploy/gunicorn.conf.py stockpro.wsgi:application

Les valeurs sont lues dans l'environnement, elles-memes chargees depuis le
fichier .env par systemd (EnvironmentFile).
"""

import multiprocessing
import os


def _int_env(name, default):
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


# Interface d'ecoute. 0.0.0.0:80 necessite CAP_NET_BIND_SERVICE (voir le
# service systemd) ; sinon utiliser un port > 1024 (ex. 0.0.0.0:8000).
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")

# Nombre de workers : reglable, sinon (2 x CPU) + 1.
workers = _int_env("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)

# Redemarre un worker apres un nombre aleatoire de requetes pour limiter les
# fuites memoire eventuelles.
max_requests = 1000
max_requests_jitter = 100

timeout = 120
graceful_timeout = 30
keepalive = 5

# Les journaux vont sur la sortie standard : systemd/journald les collecte.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")

# Derriere un eventuel proxy, on fait confiance a l'entete X-Forwarded-*.
forwarded_allow_ips = "*"
