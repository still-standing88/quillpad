from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='django-insecure-local-dev-key-123!xyz') # Default non-empty key for dev
DEBUG = config('DEBUG', default=True, cast=bool) # Default True for local/Replit dev

ALLOWED_HOSTS_DEFAULTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS_DEFAULTS = ["http://localhost:9000", "http://127.0.0.1:9000"]
REPLIT_HOST = None
CODESPACE_HOST = None

# Detect Replit
if 'REPL_SLUG' in os.environ and 'REPL_OWNER' in os.environ:
    REPLIT_HOST = f"{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}.replit.dev"
    ALLOWED_HOSTS_DEFAULTS.append(f'.{REPLIT_HOST}')
    ALLOWED_HOSTS_DEFAULTS.append(REPLIT_HOST)
    # Derive potential preview URL
    preview_url = f"https://{os.environ['REPL_SLUG']}--{os.environ['REPL_OWNER']}.repl.co"
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(preview_url)
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://*.{REPLIT_HOST}') # Also trust the service domain if needed

# Detect GitHub Codespaces
elif 'CODESPACE_NAME' in os.environ and 'GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN' in os.environ:
    CODESPACE_HOST = f"{os.environ['CODESPACE_NAME']}-9000.{os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']}" # Port 9000 for Vite
    ALLOWED_HOSTS_DEFAULTS.append(CODESPACE_HOST)
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://{CODESPACE_HOST}')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default=','.join(ALLOWED_HOSTS_DEFAULTS))
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default=','.join(CSRF_TRUSTED_ORIGINS_DEFAULTS))

INSTALLED_APPS = [ 'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.sites', 'rest_framework', 'rest_framework.authtoken', 'corsheaders', 'taggit', 'markdownx', 'djoser', 'drf_spectacular', 'django_filters', 'blog.apps.BlogConfig', 'users.apps.UsersConfig', ]
MIDDLEWARE = [ 'django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'corsheaders.middleware.CorsMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware', ]
ROOT_URLCONF = 'quillpad_backend.urls'
TEMPLATES = [ { 'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': { 'context_processors': [ 'django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages', ], }, }, ]
WSGI_APPLICATION = 'quillpad_backend.wsgi.application'
DATABASES = { 'default': dj_database_url.config( default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', conn_max_age=600 ) } # No ssl_require for dev server
AUTH_PASSWORD_VALIDATORS = [ {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',}, ]
LANGUAGE_CODE = 'en-us'; TIME_ZONE = 'UTC'; USE_I18N = True; USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR.parent / 'static_dev_assets' ]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'mediafiles_local_dev'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
REST_FRAMEWORK = { 'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication',], 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly',], 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema', 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter',], }
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default=','.join(CSRF_TRUSTED_ORIGINS_DEFAULTS))
CORS_ALLOW_CREDENTIALS = True
if not DEBUG and not CORS_ALLOWED_ORIGINS: print("WARNING: CORS_ALLOWED_ORIGINS not set for production!")
DJOSER = { "LOGIN_FIELD": "username", "SEND_ACTIVATION_EMAIL": config('SEND_ACTIVATION_EMAIL', default=False, cast=bool), "ACTIVATION_URL": "#/activate/{uid}/{token}", "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}", "USERNAME_RESET_CONFIRM_URL": "#/username/reset/confirm/{uid}/{token}", "SERIALIZERS": { "user": "users.serializers.UserSerializer", "user_create": "users.serializers.RegisterSerializer", }, "EMAIL": { "activation": "djoser.email.ActivationEmail", "password_reset": "djoser.email.PasswordResetEmail", }, "PERMISSIONS": { "user_create": ["rest_framework.permissions.AllowAny"], }, }
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend': EMAIL_HOST = config('EMAIL_HOST', default=''); EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int); EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool); EMAIL_HOST_USER = config('EMAIL_HOST_USER', default=''); EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='');
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
SPECTACULAR_SETTINGS = { 'TITLE': 'QuillPad API', 'VERSION': '1.0.0', 'SERVE_INCLUDE_SCHEMA': DEBUG, } # Show schema in debug
SITE_ID = 1
MARKDOWNX_MARKDOWN_EXTENSIONS = ['markdown.extensions.extra','markdown.extensions.codehilite',]

# --- Logging (Optional: Add basic logging for easier debugging) ---
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'INFO', # Change to DEBUG for more verbosity
#     },
# }