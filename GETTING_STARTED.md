# Guía de Inicio Rápido - Backend API

## Requisitos Previos
- Python 3.11+
- PostgreSQL 14+
- Docker (opcional)

## Instalación Local

### 1. Crear Entorno Virtual
```bash
cd backend/app
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\activate

# Activar entorno (Linux/Mac)
source venv/bin/activate
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` en `backend/app/`:

```env
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Base de datos
DB_NAME=jardin_db
DB_USER=jardin_user
DB_PASSWORD=jardin*12345
DB_HOST=localhost
DB_PORT=5432

# Zona horaria
TIME_ZONE=America/Santiago

# CORS (frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. Configurar Base de Datos

#### Opción A: PostgreSQL Local
```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos y usuario
CREATE DATABASE jardin_db;
CREATE USER jardin_user WITH PASSWORD 'jardin*12345';
GRANT ALL PRIVILEGES ON DATABASE jardin_db TO jardin_user;
\q
```

#### Opción B: Docker
```bash
docker run -d \
  --name jardin-postgres \
  -e POSTGRES_DB=jardin_db \
  -e POSTGRES_USER=jardin_user \
  -e POSTGRES_PASSWORD=jardin*12345 \
  -p 5432:5432 \
  postgres:14
```

### 5. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Cargar Datos Iniciales
```bash
python manage.py loaddata api/fixtures/initial_data.json
```

Este comando carga:
- ✅ Roles (Administrador, Profesor, Asistente)
- ✅ Jornadas (Mañana, Tarde)
- ✅ Salones (Sala 1, Sala 2, Sala 3)
- ✅ Estados de Asistencia (Presente, Ausente, Justificado, Tardanza)
- ✅ Estados de Inventario (Activo, Mantenimiento, Dado de Baja)
- ✅ Categorías de Inventario (Mobiliario, Juguetes, Material Didáctico, etc.)

### 7. Crear Superusuario (Opcional)
```bash
python manage.py createsuperuser
```

### 8. Iniciar Servidor
```bash
python manage.py runserver
```

El servidor estará disponible en: **http://localhost:8000**

## Inicialización con Docker Compose

### 1. Configurar Variables
Editar `backend/.env` si es necesario.

### 2. Construir e Iniciar
```bash
cd backend
docker-compose up --build
```

### 3. Ejecutar Migraciones (primera vez)
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata api/fixtures/initial_data.json
```

## Verificar Instalación

### 1. Verificar Status de API
```bash
curl http://localhost:8000/api/status/
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "message": "Jardin API v1.0 está funcionando correctamente",
  "version": "1.0.0"
}
```

### 2. Verificar Panel Admin
Ir a: **http://localhost:8000/admin/**

## Crear Usuario de Prueba

### Opción A: Admin de Django
1. Ir a http://localhost:8000/admin/
2. Login con superusuario
3. Agregar usuario en "Api > Usuarios"

### Opción B: Shell de Django
```bash
python manage.py shell
```

```python
from api.models import Usuario, Rol

# Obtener rol de Administrador
rol_admin = Rol.objects.get(nombre='Administrador')

# Crear usuario
usuario = Usuario.objects.create(
    rol=rol_admin,
    nombre='Admin Test',
    email='admin@jardin.com',
    telefono='+56912345678'
)
usuario.set_password('admin123')
usuario.save()

print(f'Usuario creado: {usuario.email}')
```

## Endpoints Disponibles

Ver documentación completa en: **[API_README.md](./API_README.md)**

### Resumen de Endpoints:

#### Autenticación
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/me/` - Usuario actual

#### Catálogos
- `GET /api/roles/` - Roles
- `GET /api/jornadas/` - Jornadas
- `GET /api/salones/` - Salones
- `GET /api/estados-asistencia/` - Estados de asistencia
- `GET /api/categorias/` - Categorías de inventario

#### Entidades Principales
- `/api/usuarios/` - Usuarios
- `/api/estudiantes/` - Estudiantes
- `/api/asistencias/` - Asistencias
- `/api/asistencias-apoderados/` - Asistencias de apoderados
- `/api/inventario/` - Inventario

#### Dashboard
- `GET /api/dashboard/stats/` - Estadísticas generales

## Testing

### Ejecutar Tests
```bash
python manage.py test
```

### Con Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage html
# Ver reporte en htmlcov/index.html
```

## Comandos de Gestión

### Ver Usuarios
```bash
python manage.py shell
```
```python
from api.models import Usuario
for u in Usuario.objects.all():
    print(f'{u.id}: {u.nombre} - {u.email}')
```

### Resetear Base de Datos
```bash
python manage.py flush
python manage.py migrate
python manage.py loaddata api/fixtures/initial_data.json
```

### Exportar Datos
```bash
# Exportar todos los datos
python manage.py dumpdata > backup.json

# Exportar solo una app
python manage.py dumpdata api > api_backup.json

# Exportar solo un modelo
python manage.py dumpdata api.Usuario > usuarios.json
```

## Troubleshooting

### Error: "No module named 'rest_framework'"
```bash
pip install djangorestframework
```

### Error: "FATAL: database does not exist"
Crear la base de datos primero:
```bash
createdb jardin_db
```

### Error: "Connection refused" (PostgreSQL)
Verificar que PostgreSQL esté corriendo:
```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql

# Docker
docker start jardin-postgres
```

### Error: CORS
Verificar `CORS_ALLOWED_ORIGINS` en `settings.py` incluye la URL del frontend.

### Error: "Session expired"
Las sesiones se guardan en la base de datos. Verificar que:
1. El middleware de sesiones esté activo
2. Las cookies se estén enviando correctamente
3. El frontend use `credentials: 'include'` en fetch

## Variables de Entorno (Completas)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_LOG_LEVEL=INFO

# Database
DB_NAME=jardin_db
DB_USER=jardin_user
DB_PASSWORD=jardin*12345
DB_HOST=localhost
DB_PORT=5432

# Timezone
TIME_ZONE=America/Santiago

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

## Logs

Los logs se muestran en la consola en modo desarrollo. Para producción, configurar:

```python
# settings.py
LOGGING = {
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/jardin/django.log',
        },
    },
}
```

## Producción

Ver configuración de producción en:
- `Dockerfile.prod`
- `docker-compose.prod.yml`
- `nginx-prod.conf`

## Soporte

Para más información:
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- PostgreSQL Docs: https://www.postgresql.org/docs/
