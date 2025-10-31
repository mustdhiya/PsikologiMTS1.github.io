"""
Django settings for psikologimts1 project - PRODUCTION VERSION
"""
import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-1a$i4%tv3i6$xf0(dby40p(e6aqh(as%vcck1-l2&s1m&3*kze'
)

# SECURITY WARNING: don't run with debug turned on in production!
# Set via environment variable: DEBUG=False di cPanel
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Deteksi apakah ini production atau development
IS_PRODUCTION = not DEBUG and os.environ.get('ENVIRONMENT', 'development') == 'production'

# ALLOWED_HOSTS
if IS_PRODUCTION:
    ALLOWED_HOSTS = ['prestisia.com', 'www.prestisia.com']
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:8000', '127.0.0.1:8000']

# CSRF Trusted Origins
# settings.py
if IS_PRODUCTION:
    # Production CSRF
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = False  # ← PENTING: False agar JS bisa baca
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_USE_SESSIONS = False
    
    CSRF_TRUSTED_ORIGINS = [
        'https://prestisia.com',
        'https://www.prestisia.com',
    ]
else:
    # Development - lebih permissive
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_HTTPONLY = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_USE_SESSIONS = False
    
    # Allow localhost
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://127.0.0.1:8000/',
    ]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4', 
    'import_export',     
    
    # Custom apps
    'accounts',
    'core',        
    'students',
    'teachers',
    'testsystem',
    'certificates',
    'reports',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'psikologimts1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'psikologimts1.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get(
            'DB_ENGINE',
            'django.db.backends.sqlite3' if not IS_PRODUCTION else 'django.db.backends.mysql'
        ),
        'NAME': os.environ.get(
            'DB_NAME',
            os.path.join(BASE_DIR, 'db_local.sqlite3') if not IS_PRODUCTION else 'psikologimts1_db'
        ),
        'USER': os.environ.get('DB_USER', 'root' if not IS_PRODUCTION else ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', '' if not IS_PRODUCTION else ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

AUTHENTICATION_BACKENDS = [
    'accounts.backends.StudentNISNBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public_html', 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public_html', 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Session Settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = IS_PRODUCTION  # ← True hanya di production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'



# ============================================================================
# SECURITY SETTINGS - HANYA AKTIF DI PRODUCTION SETELAH SSL TERVERIFIKASI
# ============================================================================
if IS_PRODUCTION:
    # Redirect HTTP to HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # ⚠️ HSTS HEADERS - HANYA SETELAH VERIFY SSL CERTIFICATE
    # Mulai dengan max_age kecil (1 jam) untuk testing
    # Setelah confirm sempurna, naikkan ke 31536000 (1 tahun)
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '3600'))  # Default 1 jam
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False') == 'True'  # Default False
    
    # Security headers lainnya
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'same-origin'
else:
    # ✅ DEVELOPMENT - Tidak ada SSL redirect atau HSTS
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# Email Configuration
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@prestisia.com')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
} if os.path.exists(os.path.join(BASE_DIR, 'logs')) else {
    'version': 1,
    'disable_existing_loggers': False,
}
