# Configuración local para desarrollo con SQLite
from .settings import *

# Sobrescribir la configuración de base de datos para usar SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Activar DEBUG para desarrollo local
DEBUG = True

# Configuración específica para SQLite
DATABASES['default']['ATOMIC_REQUESTS'] = False