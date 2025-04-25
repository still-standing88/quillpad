from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os # Keep os import if needed elsewhere, though BASE_DIR uses pathlib now

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Read from environment variable using decouple
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-if-not-set') # Provide a fallback for initial setup

# SECURITY WARNING: don't run with debug turned on in production!
# Read from environment variable using decouple
DEBUG = config('DEBUG', default=False, cast=bool)

# Read from environment variable using decouple
# Add .onrender.com for Render compatibility, keep localhost for dev
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='127.0.0.1,localhost,.onrender.com')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Add WhiteNoise **BEFORE** staticfiles
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites', # Needed for spectacular/admin potentially

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

    # Your Apps (Ensure correct paths if needed)
    "blog.apps.BlogConfig", # Or just "blog" if using default AppConfig
    "users.apps.UsersConfig", # Or just "users"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add WhiteNoise middleware **AFTER** SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Position relative to CommonMiddleware might matter
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quillpad_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Add template dirs here if you have project-level templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Add context processors needed by social_django if used
            ],
        },
    },
]

WSGI_APPLICATION = 'quillpad_backend.wsgi.application'


# Database
# Uses DATABASE_URL from .env file if available, otherwise defaults to SQLite
# Ensures SSL is required only when DEBUG is False (i.e., in production)
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', # Fallback to SQLite for dev
        conn_max_age=600,                 # Recommended for persistent connections
        ssl_require=not DEBUG             # Use SSL for non-DEBUG environments
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True # Recommended for consistent datetime handling


# Static files (CSS, JavaScript, Images) - For Django Admin & collectstatic
STATIC_URL = '/static/'
# Directory where collectstatic will gather all static files for deployment.
# Store outside 'src' directory, e.g., in project root or one level up.
STATIC_ROOT = BASE_DIR.parent / 'staticfiles_collected'
# Tell WhiteNoise how to handle static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Development only: Directories Django looks for additional static files (usually not needed for API + SPA)
# STATICFILES_DIRS = []

# Media files (User uploads)
MEDIA_URL = '/media/'
# Directory where user uploads will be stored. Needs correct permissions.
# Store outside 'src' directory. Render Disks need specific paths.
MEDIA_ROOT = BASE_DIR.parent / 'mediafiles'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication', # Enable if needed for Browsable API/Admin
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # Default to requiring login
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Uncomment and configure pagination if desired globally
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10
}

# CORS Settings
# Read list of allowed origins from environment variable
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='')
CORS_ALLOW_CREDENTIALS = True # Important for sending auth cookies/tokens

# Set default allowed origins for development if DEBUG is True and env var is not set
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:9000", # Default Vite port
        "http://127.0.0.1:9000",
        "http://localhost:5173", # Common alternative
        "http://127.0.0.1:5173",
    ]

# Production Check: Ensure CORS origins are set when DEBUG is False
if not DEBUG and not CORS_ALLOWED_ORIGINS:
     # In a real app, you might log this warning or raise an ImproperlyConfigured error
     print("WARNING: CORS_ALLOWED_ORIGINS is not set in environment variables for production (DEBUG=False)!")


# Djoser Settings (Authentication Library)
DJOSER = {
    "LOGIN_FIELD": "username",
    "SEND_ACTIVATION_EMAIL": config('SEND_ACTIVATION_EMAIL', default=True, cast=bool), # Allow disabling via env
    "ACTIVATION_URL": "activate/{uid}/{token}",
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "username/reset/confirm/{uid}/{token}",
    "SERIALIZERS": {
        "user": "users.serializers.UserSerializer",
        "user_create": "users.serializers.RegisterSerializer",
    },
    "EMAIL": { # Uses standard Djoser emails unless you create custom ones
        "activation": "djoser.email.ActivationEmail",
        "confirmation": "djoser.email.ConfirmationEmail",
        "password_reset": "djoser.email.PasswordResetEmail",
        "password_changed_confirmation": "djoser.email.PasswordChangedConfirmationEmail",
        "username_changed_confirmation": "djoser.email.UsernameChangedConfirmationEmail",
        "username_reset": "djoser.email.UsernameResetEmail",
    },
    "PERMISSIONS": { # Use Djoser defaults unless specific overrides needed
        "user_create": ["rest_framework.permissions.AllowAny"],
        "activation": ["rest_framework.permissions.AllowAny"],
        "password_reset": ["rest_framework.permissions.AllowAny"],
        "password_reset_confirm": ["rest_framework.permissions.AllowAny"],
        "username_reset": ["rest_framework.permissions.AllowAny"],
        "username_reset_confirm": ["rest_framework.permissions.AllowAny"],
        "user_delete": ["djoser.permissions.CurrentUserOrAdmin"],
        "user": ["djoser.permissions.CurrentUserOrAdmin"],
        "user_list": ["rest_framework.permissions.IsAdminUser"],
    },
    # Add SOCIAL_AUTH_ALLOWED_REDIRECT_URIS if using social auth with djoser
}

# Email Backend Configuration (reads from .env)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = config('EMAIL_HOST', default='')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# drf-spectacular Settings (API Schema/Docs)
SPECTACULAR_SETTINGS = {
    'TITLE': 'QuillPad API',
    'DESCRIPTION': 'API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False, # Schema download only through specific endpoint
    # Add other spectacular settings if needed
}

SITE_ID = 1 # Required by django.contrib.sites

# MarkdownX settings (if any customizations are needed)
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.codehilite',
    # Add other extensions here
]
MARKDOWNX_CODEHILITE_CSS = 'codehilite.css' # Example CSS file name

# Add any settings required by social-auth-app-django if you are using it
# Example:
# AUTHENTICATION_BACKENDS = (
#     'social_core.backends.google.GoogleOAuth2', # Example
#     'django.contrib.auth.backends.ModelBackend',
# )
# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_OAUTH_KEY', default='')
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_OAUTH_SECRET', default='')
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/logged-in/' # Example redirect URL
# SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/' # Example error URL