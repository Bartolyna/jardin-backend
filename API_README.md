# API REST - Sistema de Gestión Jardín Infantil

## Descripción
API RESTful desarrollada con Django REST Framework para la gestión integral de un jardín infantil.

## Características
- ✅ Autenticación basada en sesiones
- ✅ CRUD completo para todas las entidades
- ✅ Soft delete en todos los modelos
- ✅ Filtros y búsqueda en endpoints
- ✅ Paginación automática
- ✅ Serializers optimizados con relaciones
- ✅ CORS habilitado para frontend
- ✅ Estadísticas y reportes

## Endpoints Principales

### Autenticación
```
POST   /api/auth/login/       - Iniciar sesión
POST   /api/auth/logout/      - Cerrar sesión
GET    /api/auth/me/          - Obtener usuario actual
```

### Catálogos Base
```
GET    /api/roles/                    - Listar roles
GET    /api/jornadas/                 - Listar jornadas
GET    /api/salones/                  - Listar salones
GET    /api/estados-asistencia/       - Listar estados de asistencia
GET    /api/estados-inventario/       - Listar estados de inventario
GET    /api/categorias/               - Listar categorías
```

### Usuarios
```
GET    /api/usuarios/                 - Listar usuarios
POST   /api/usuarios/                 - Crear usuario
GET    /api/usuarios/{id}/            - Detalle de usuario
PUT    /api/usuarios/{id}/            - Actualizar usuario
DELETE /api/usuarios/{id}/            - Eliminar usuario (soft delete)
POST   /api/usuarios/{id}/cambiar_password/  - Cambiar contraseña
```

**Filtros disponibles:**
- `?rol={id}` - Filtrar por rol
- `?search={texto}` - Buscar por nombre o email

### Jornadas-Salones
```
GET    /api/jornadas-salones/         - Listar jornadas-salones
POST   /api/jornadas-salones/         - Crear asignación
GET    /api/jornadas-salones/{id}/    - Detalle
GET    /api/jornadas-salones/{id}/estudiantes/  - Estudiantes del salon
```

**Filtros disponibles:**
- `?jornada={id}` - Filtrar por jornada
- `?salon={id}` - Filtrar por salón

### Estudiantes
```
GET    /api/estudiantes/              - Listar estudiantes
POST   /api/estudiantes/              - Crear estudiante
GET    /api/estudiantes/{id}/         - Detalle de estudiante
PUT    /api/estudiantes/{id}/         - Actualizar estudiante
DELETE /api/estudiantes/{id}/         - Eliminar estudiante (soft delete)
GET    /api/estudiantes/{id}/asistencias/  - Historial de asistencias
```

**Filtros disponibles:**
- `?jornada_salon={id}` - Filtrar por jornada-salón
- `?search={texto}` - Buscar por nombre, RUT o tutor
- `?fecha_inicio={YYYY-MM-DD}` (en endpoint de asistencias)
- `?fecha_fin={YYYY-MM-DD}` (en endpoint de asistencias)

### Asistencias
```
GET    /api/asistencias/              - Listar asistencias
POST   /api/asistencias/              - Registrar asistencia
GET    /api/asistencias/{id}/         - Detalle
PUT    /api/asistencias/{id}/         - Actualizar
DELETE /api/asistencias/{id}/         - Eliminar (soft delete)
POST   /api/asistencias/registrar_masivo/  - Registro masivo
GET    /api/asistencias/estadisticas/      - Estadísticas
```

**Filtros disponibles:**
- `?fecha={YYYY-MM-DD}` - Filtrar por fecha
- `?estudiante={id}` - Filtrar por estudiante
- `?estado={id}` - Filtrar por estado
- `?jornada_salon={id}` - Filtrar por jornada-salón

### Asistencias de Apoderados
```
GET    /api/asistencias-apoderados/   - Listar asistencias de apoderados
POST   /api/asistencias-apoderados/   - Registrar
GET    /api/asistencias-apoderados/{id}/  - Detalle
```

**Filtros disponibles:**
- `?fecha={YYYY-MM-DD}` - Filtrar por fecha
- `?estudiante={id}` - Filtrar por estudiante
- `?tipo_evento={tipo}` - Filtrar por tipo (ENTRADA/SALIDA)

### Inventario
```
GET    /api/inventario/               - Listar items
POST   /api/inventario/               - Crear item
GET    /api/inventario/{id}/          - Detalle
PUT    /api/inventario/{id}/          - Actualizar
DELETE /api/inventario/{id}/          - Eliminar (soft delete)
POST   /api/inventario/{id}/dar_de_baja/  - Dar de baja item
```

**Filtros disponibles:**
- `?estado={id}` - Filtrar por estado
- `?categoria={id}` - Filtrar por categoría
- `?search={texto}` - Buscar por código, nombre o descripción

### Dashboard
```
GET    /api/dashboard/stats/          - Estadísticas generales
```

**Respuesta:**
```json
{
  "estudiantes": {
    "total": 50
  },
  "personal": {
    "total": 10
  },
  "asistencia_hoy": {
    "fecha": "2024-01-15",
    "por_estado": [
      {"estado__nombre": "Presente", "total": 45},
      {"estado__nombre": "Ausente", "total": 5}
    ]
  },
  "inventario": {
    "por_estado": [
      {"estado__nombre": "Activo", "total": 100},
      {"estado__nombre": "En mantenimiento", "total": 5}
    ]
  }
}
```

## Ejemplos de Uso

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@jardin.com",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Administrador",
  "email": "admin@jardin.com",
  "rol": {
    "id": 1,
    "nombre": "Administrador"
  },
  "ultimo_acceso": "2024-01-15T10:30:00Z"
}
```

### Crear Estudiante
```bash
curl -X POST http://localhost:8000/api/estudiantes/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "jornada_salon": 1,
    "nombre": "Juan Pérez",
    "rut": "12345678-9",
    "fecha_nacimiento": "2020-05-15",
    "tutor_nombre": "María Pérez",
    "tutor_rut": "98765432-1",
    "tutor_telefono": "+56912345678",
    "tutor_email": "maria@example.com"
  }'
```

### Registrar Asistencia
```bash
curl -X POST http://localhost:8000/api/asistencias/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "estudiante": 1,
    "estado": 1,
    "fecha": "2024-01-15",
    "hora_llegada": "08:30:00",
    "registrado_por": 1
  }'
```

### Registro Masivo de Asistencias
```bash
curl -X POST http://localhost:8000/api/asistencias/registrar_masivo/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "asistencias": [
      {
        "estudiante": 1,
        "estado": 1,
        "fecha": "2024-01-15",
        "hora_llegada": "08:30:00",
        "registrado_por": 1
      },
      {
        "estudiante": 2,
        "estado": 1,
        "fecha": "2024-01-15",
        "hora_llegada": "08:45:00",
        "registrado_por": 1
      }
    ]
  }'
```

## Modelos de Datos

### Usuario
```json
{
  "id": 1,
  "rol": 1,
  "rol_nombre": "Administrador",
  "nombre": "Admin User",
  "email": "admin@jardin.com",
  "telefono": "+56912345678",
  "ultimo_acceso": "2024-01-15T10:30:00Z",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Estudiante
```json
{
  "id": 1,
  "jornada_salon": 1,
  "jornada_salon_info": {
    "id": 1,
    "jornada": "Mañana",
    "salon": "Sala 1"
  },
  "nombre": "Juan Pérez",
  "rut": "12345678-9",
  "fecha_nacimiento": "2020-05-15",
  "edad": 3,
  "edad_calculada": 3,
  "tutor_nombre": "María Pérez",
  "tutor_rut": "98765432-1",
  "tutor_telefono": "+56912345678",
  "tutor_email": "maria@example.com",
  "contacto_emergencia_nombre": "Pedro Pérez",
  "contacto_emergencia_telefono": "+56987654321",
  "observaciones_medicas": "Ninguna",
  "alergias": "Ninguna",
  "direccion": "Calle Falsa 123",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Asistencia
```json
{
  "id": 1,
  "estudiante": 1,
  "estudiante_nombre": "Juan Pérez",
  "estado": 1,
  "estado_nombre": "Presente",
  "estado_color": "#22c55e",
  "fecha": "2024-01-15",
  "hora_llegada": "08:30:00",
  "observaciones": "",
  "registrado_por": 1,
  "registrado_por_nombre": "Admin User",
  "is_active": true,
  "created_at": "2024-01-15T08:30:00Z",
  "updated_at": "2024-01-15T08:30:00Z"
}
```

## Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Error en los datos enviados
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permisos
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## Configuración CORS

El backend permite peticiones desde:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

Para agregar más orígenes, editar `CORS_ALLOWED_ORIGINS` en `settings.py`.

## Autenticación

La API usa **SessionAuthentication**. Después del login, la cookie de sesión se envía automáticamente en cada petición.

## Paginación

Por defecto, los listados retornan 20 items por página. Puedes modificar esto con:
- `?page=2` - Ir a la página 2
- `?page_size=50` - Cambiar tamaño de página

## Soft Delete

Todos los modelos usan soft delete. Al eliminar un registro:
- `is_active` se establece en `false`
- El registro no aparece en listados por defecto
- Los datos permanecen en la base de datos

## Variables de Entorno

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_NAME=jardin_db
DB_USER=jardin_user
DB_PASSWORD=jardin*12345
DB_HOST=db
DB_PORT=5432
TIME_ZONE=America/Bogota
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Iniciar el Servidor

```bash
# Desarrollo
cd backend/app
python manage.py runserver

# Con Docker
docker-compose up
```

El servidor estará disponible en `http://localhost:8000`

## Testing

```bash
# Ejecutar tests
python manage.py test

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

## Notas Importantes

1. **Passwords**: Los usuarios usan hash pbkdf2_sha256 con salt
2. **Timestamps**: Todos los modelos tienen `created_at` y `updated_at`
3. **RUT**: Se valida formato chileno en el modelo
4. **Códigos únicos**: El inventario requiere códigos únicos
5. **Relaciones**: Usar `PROTECT` en ForeignKeys para evitar eliminación accidental
