# Configuración para desarrollo con PostgreSQL en Docker
from .settings import *

# Configuración específica para PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='jardin_db_local'),
        'USER': config('DB_USER', default='jardin_user'),
        'PASSWORD': config('DB_PASSWORD', default='jardin*12345'),
        'HOST': config('DB_HOST', default='localhost'),  # Cambiar de 'db' a 'localhost' para desarrollo local
        'PORT': config('DB_PORT', default='5433'),  # Puerto expuesto en docker-compose
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'TEST': {
            'NAME': 'test_jardin_db_local',
        }
    }
}

# Activar DEBUG para desarrollo local
DEBUG = True

# Configuración de logging para desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}