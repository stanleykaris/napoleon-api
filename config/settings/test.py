from .development import *  # noqa: F401, F403

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password validation during testing
AUTH_PASSWORD_VALIDATORS = []

# Disable debug toolbar during testing
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Disable caching for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use faster JWT settings for tests
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
}

# Test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Media root for tests
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable throttling for tests
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'user': None,
    'anon': None,
}

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True

# Disable SSL redirect for tests
SECURE_SSL_REDIRECT = False

# Disable CSRF for tests
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Disable security middleware for tests
MIDDLEWARE = [
    mw for mw in MIDDLEWARE
    if mw not in [
        'django.middleware.security.SecurityMiddleware',
        'corsheaders.middleware.CorsMiddleware',
    ]
]

# Disable password validation for tests
AUTH_PASSWORD_VALIDATORS = []
