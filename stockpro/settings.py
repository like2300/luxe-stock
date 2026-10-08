from pathlib import Path
from datetime import timedelta

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-5l7(@gkzyx(r6uz(wo=dm9h%t-7(!drn^v+qdk-9+!*or&=!+1'
DEBUG = True
ALLOWED_HOSTS = [
    host.strip()
    for host in config('ALLOWED_HOSTS', default='').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'rest_framework_simplejwt.token_blacklist',
    'core',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stockpro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.avatar',
                'core.context_processors.shop',
                'core.context_processors.social_login',
            ],
        },
    },
]

WSGI_APPLICATION = 'stockpro.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Brazzaville'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_SIGNUP_REDIRECT_URL = '/'
ACCOUNT_LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/login/'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_LOGIN_ON_GET = True

EMAIL_HOST = config('EMAIL_HOST', default='smtp-relay.brevo.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='elengaomerfils@gmail.com')

SITE_BASE_URL = config('SITE_BASE_URL', default='http://127.0.0.1:8000')
ACCOUNT_DEFAULT_HTTP_PROTOCOL = config('ACCOUNT_DEFAULT_HTTP_PROTOCOL', default='http')

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online', 'prompt': 'select_account'},
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': '',
        },
    }
}

UNFOLD = {
    'SITE_TITLE': 'Stock - Administration',
    'SITE_HEADER': 'Gestion du Stock',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'push': '60/min',
        'pull': '120/min',
        'login': '20/min',
    },
    'EXCEPTION_HANDLER': 'api.exceptions.api_exception_handler',
}

SIMPLE_JWT = {
    # Des durees, pas des secondes : simplejwt additionne la duree a l'instant
    # d'emission. Un entier ici leve une TypeError a la creation du jeton.
    'ACCESS_TOKEN_LIFETIME': timedelta(
        seconds=config('JWT_ACCESS_TOKEN_LIFETIME', default=60 * 60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=30, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Stock API',
    'DESCRIPTION': (
        "API REST de l'application Stock. Les règles métier (mouvements de "
        "stock, notifications, seuils d'alerte) sont partagées avec "
        "l'application web Django."
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'TAGS': [
        {'name': 'Auth', 'description': 'Connexion, inscription, jetons JWT.'},
        {'name': 'Boutique', 'description': 'Boutique, thème, logo, paramètres.'},
        {'name': 'Produits', 'description': 'Produits, catégories, mouvements, scan.'},
        {'name': 'Notifications', 'description': 'Fil et état de lecture des notifications.'},
        {'name': 'Employés', 'description': 'Comptes et permissions (propriétaire).'},
        {'name': 'Profil', 'description': 'Profil, photo, avatar.'},
        {'name': 'Synchronisation', 'description': 'Pull/push hors ligne par curseur.'},
    ],
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config('CORS_ALLOWED_ORIGINS', default='').split(',')
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
