from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'taggit',
    'markdownx',
    'djoser',
    'drf_spectacular',
    'social_django',
    'django_filters',

    'blog.apps.BlogConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Place CORS middleware high, especially before CommonMiddleware if needed
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'quillpad_backend.wsgi.application'


# Database
# Uses DATABASE_URL from .env file if available, otherwise defaults to SQLite
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) for Django Admin
STATIC_URL = '/static/'
# Production only: Directory where collectstatic will gather files
STATIC_ROOT = BASE_DIR.parent / 'staticfiles_collected'
# Development only: Directories to find static files not tied to an app (usually empty)
# STATICFILES_DIRS = [BASE_DIR / 'static'] # Not typically needed if frontend handles its own static files

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'mediafiles' # Store outside 'src'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # Consider SessionAuthentication if you use the admin or browsable API extensively
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # Default to requiring authentication
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Add pagination settings if desired globally, or keep per-view
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='')
CORS_ALLOW_CREDENTIALS = True

# Use different CORS settings for Debug vs Production if needed
if DEBUG:
    # Allow common dev origins if CORS_ALLOWED_ORIGINS is empty in .env for debug
    if not CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS = [
            "http://localhost:9000", # Vite default dev port
            "http://127.0.0.1:9000",
            "http://localhost:5173", # Common alternative Vite port
            "http://127.0.0.1:5173",
        ]
else:
    # Production: Ensure CORS_ALLOWED_ORIGINS is explicitly set in .env
    if not CORS_ALLOWED_ORIGINS:
        print("WARNING: CORS_ALLOWED_ORIGINS is not set for production (DEBUG=False)!")
    # Production security enhancements (optional, often handled by proxy)
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_SECONDS = 31536000 # 1 year
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# Djoser Configuration (Authentication Endpoints)
DJOSER = {
    "LOGIN_FIELD": "username",
    "SEND_ACTIVATION_EMAIL": True, # Set to False if you don't want email activation
    "ACTIVATION_URL": "activate/{uid}/{token}", # Frontend route for activation
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}", # Frontend route
    "USERNAME_RESET_CONFIRM_URL": "username/reset/confirm/{uid}/{token}", # Frontend route
    "SERIALIZERS": {
        "user": "users.serializers.UserSerializer",
        "user_create": "users.serializers.RegisterSerializer",
        # Add other serializers if needed (current_user, etc.)
    },
    "EMAIL": {
        # You can customize email templates if needed
        "activation": "djoser.email.ActivationEmail",
        "confirmation": "djoser.email.ConfirmationEmail",
        "password_reset": "djoser.email.PasswordResetEmail",
        "password_changed_confirmation": "djoser.email.PasswordChangedConfirmationEmail",
        "username_changed_confirmation": "djoser.email.UsernameChangedConfirmationEmail",
        "username_reset": "djoser.email.UsernameResetEmail",
    },
    "PERMISSIONS": {
        # Keep defaults or customize as needed
        "activation": ["rest_framework.permissions.AllowAny"],
        "password_reset": ["rest_framework.permissions.AllowAny"],
        "password_reset_confirm": ["rest_framework.permissions.AllowAny"],
        "set_password": ["djoser.permissions.CurrentUserOrAdmin"],
        "username_reset": ["rest_framework.permissions.AllowAny"],
        "username_reset_confirm": ["rest_framework.permissions.AllowAny"],
        "set_username": ["djoser.permissions.CurrentUserOrAdmin"],
        "user_create": ["rest_framework.permissions.AllowAny"],
        "user_delete": ["djoser.permissions.CurrentUserOrAdmin"],
        "user": ["djoser.permissions.CurrentUserOrAdmin"],
        "user_list": ["rest_framework.permissions.IsAdminUser"],
        "token_create": ["rest_framework.permissions.AllowAny"],
        "token_destroy": ["rest_framework.permissions.IsAuthenticated"],
    },
    # Optional: Social Auth Settings (if using social_django with Djoser)
    # "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": config('SOCIAL_AUTH_ALLOWED_REDIRECT_URIS', cast=Csv(), default=''),
}

# Email Backend Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')


# API Documentation Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'QuillPad API',
    'DESCRIPTION': 'API documentation for QuillPad blogging platform',
    'VERSION': '1.0.0',
    # Other settings...
}

SITE_ID = 1 # Required by django.contrib.sites