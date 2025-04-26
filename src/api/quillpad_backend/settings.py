from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os

# --- Core Setup ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='django-insecure-pleasereplaceme!' + os.urandom(12).hex()) # Default for DEV ONLY
DEBUG = config('DEBUG', default=True, cast=bool) # Default to DEBUG=True for local dev

# --- Dynamic Host/Origin Configuration ---
ALLOWED_HOSTS_DEFAULTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS_DEFAULTS = [
    "http://localhost:9000", # Default Vite port
    "http://127.0.0.1:9000",
    "http://localhost:5173", # Common alternative
    "http://127.0.0.1:5173",
]
# Detect Render
if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    RENDER_EXTERNAL_HOSTNAME = os.environ['RENDER_EXTERNAL_HOSTNAME']
    ALLOWED_HOSTS_DEFAULTS.append(f'.{RENDER_EXTERNAL_HOSTNAME}') # Allow render service domain
    ALLOWED_HOSTS_DEFAULTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
# Detect Replit
elif 'REPL_SLUG' in os.environ and 'REPL_OWNER' in os.environ:
    REPLIT_HOST = f"{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}.replit.dev"
    ALLOWED_HOSTS_DEFAULTS.append(f'.{REPLIT_HOST}')
    ALLOWED_HOSTS_DEFAULTS.append(REPLIT_HOST)
    preview_url = f"https://{os.environ['REPL_SLUG']}--{os.environ['REPL_OWNER']}.repl.co"
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(preview_url)
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://{REPLIT_HOST}')
    CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://*.{REPLIT_HOST}')
# Detect GitHub Codespaces (Example)
elif 'CODESPACE_NAME' in os.environ and 'GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN' in os.environ:
     CODESPACE_HOST_9000 = f"{os.environ['CODESPACE_NAME']}-9000.{os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']}" # Port 9000 for Vite
     CODESPACE_HOST_8000 = f"{os.environ['CODESPACE_NAME']}-8000.{os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']}" # Port 8000 for Django
     ALLOWED_HOSTS_DEFAULTS.append(CODESPACE_HOST_9000)
     ALLOWED_HOSTS_DEFAULTS.append(CODESPACE_HOST_8000)
     CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://{CODESPACE_HOST_9000}')
     CSRF_TRUSTED_ORIGINS_DEFAULTS.append(f'https://{CODESPACE_HOST_8000}')


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default=','.join(ALLOWED_HOSTS_DEFAULTS))
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default=','.join(CSRF_TRUSTED_ORIGINS_DEFAULTS))


# --- Application definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Use WhiteNoise only in Production (when DEBUG is False)
    # 'whitenoise.runserver_nostatic', # No longer needed here
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # 3rd Party Apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "taggit",
    "markdownx",
    "djoser",
    'drf_spectacular',
    # 'social_django', # Uncomment if you use this
    'django_filters',

    # Your Apps
    "blog.apps.BlogConfig",
    "users.apps.UsersConfig",
]

# Conditionally add WhiteNoise for production
if not DEBUG:
    INSTALLED_APPS.insert(INSTALLED_APPS.index('django.contrib.staticfiles'), 'whitenoise.runserver_nostatic')


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Conditionally add WhiteNoise middleware AFTER SecurityMiddleware in production
    # 'whitenoise.middleware.WhiteNoiseMiddleware', # Added below conditionally
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Conditionally add WhiteNoise middleware
if not DEBUG:
    # Insert WhiteNoiseMiddleware after SecurityMiddleware.
    # Find the index of SecurityMiddleware and insert after it.
    try:
        security_middleware_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        MIDDLEWARE.insert(security_middleware_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    except ValueError:
        # If SecurityMiddleware is not found (unlikely), add it at the beginning
        MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')


ROOT_URLCONF = 'quillpad_backend.urls'
TEMPLATES = [ { 'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': { 'context_processors': [ 'django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages', ], }, }, ]
WSGI_APPLICATION = 'quillpad_backend.wsgi.application' # Used by Gunicorn

# --- Database Configuration ---
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', # Default to SQLite
        conn_max_age=600,
        # Set ssl_require based on DEBUG for platforms like Render
        # For SQLite or local non-SSL DBs, this will be ignored/False.
        ssl_require=config('DB_SSL_REQUIRE', default=not DEBUG, cast=bool)
    )
}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [ {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',}, ]

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'; TIME_ZONE = 'UTC'; USE_I18N = True; USE_TZ = True

# --- Static files ---
STATIC_URL = '/static/'
if DEBUG:
    # Development: Where Django looks for extra static files (e.g., project-wide assets)
    STATICFILES_DIRS = [ BASE_DIR.parent / 'static_dev_assets' ] # Example path
else:
    # Production: Where 'collectstatic' will copy files to
    STATIC_ROOT = BASE_DIR.parent / 'staticfiles_collected'
    # Production: Storage backend using WhiteNoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Media files ---
MEDIA_URL = '/media/'
# Use different roots for local dev vs potentially persistent storage in prod
MEDIA_ROOT = config('MEDIA_ROOT', default=str(BASE_DIR.parent / 'mediafiles_local_dev'))


# --- Other Settings ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
SITE_ID = 1

# --- REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication',],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly',], # Allow reading public APIs
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter',],
}

# --- CORS ---
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default=','.join(CSRF_TRUSTED_ORIGINS_DEFAULTS))
CORS_ALLOW_CREDENTIALS = True
if not DEBUG and not CORS_ALLOWED_ORIGINS: print("WARNING: CORS_ALLOWED_ORIGINS not set for production!")

# --- Djoser ---
DJOSER = { "LOGIN_FIELD": "username", "SEND_ACTIVATION_EMAIL": config('SEND_ACTIVATION_EMAIL', default=False, cast=bool), "ACTIVATION_URL": "#/activate/{uid}/{token}", "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}", "USERNAME_RESET_CONFIRM_URL": "#/username/reset/confirm/{uid}/{token}", "SERIALIZERS": { "user": "users.serializers.UserSerializer", "user_create": "users.serializers.RegisterSerializer", }, "EMAIL": { "activation": "djoser.email.ActivationEmail", "password_reset": "djoser.email.PasswordResetEmail", }, "PERMISSIONS": { "user_create": ["rest_framework.permissions.AllowAny"], }, }

# --- Email ---
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend': EMAIL_HOST = config('EMAIL_HOST', default=''); EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int); EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool); EMAIL_HOST_USER = config('EMAIL_HOST_USER', default=''); EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='');
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# --- drf-spectacular ---
SPECTACULAR_SETTINGS = { 'TITLE': 'QuillPad API', 'VERSION': '1.0.0', 'SERVE_INCLUDE_SCHEMA': DEBUG, } # Show schema only in DEBUG

# --- MarkdownX ---
MARKDOWNX_MARKDOWN_EXTENSIONS = ['markdown.extensions.extra','markdown.extensions.codehilite',]

# --- Production Security Settings (Activated when DEBUG=False) ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    # Consider adjusting HSTS settings based on deployment strategy
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int) # Default to 0 (off) unless explicitly set
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
    # SECURE_BROWSER_XSS_FILTER = True # Deprecated / superseded
    SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)