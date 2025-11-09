# 🚀 Comandos Jardin - Referencia Rápida

## 📋 Comandos principales

### 🛠️ Desarrollo Local
```bash
make up-dev          # Iniciar ambiente completo (Django + PostgreSQL + Nginx)
make up-dev-simple   # Iniciar solo Django + PostgreSQL
make down            # Detener servicios
make logs            # Ver logs en tiempo real
make status          # Ver estado de servicios
```

### 🏭 Producción
```bash
make up-prod         # Iniciar ambiente de producción
make down-prod       # Detener ambiente de producción
make logs-prod       # Ver logs de producción
make status-prod     # Ver estado de servicios de producción
```

### 🐳 Acceso a contenedores
```bash
# Local
make exec-web-local    # Entrar a Django local
make exec-db-local     # Entrar a PostgreSQL local
make exec-nginx-local  # Entrar a Nginx local

# Producción
make exec-web-prod     # Entrar a Django producción
make exec-db-prod      # Entrar a PostgreSQL producción
make exec-nginx-prod   # Entrar a Nginx producción
```

### 🐍 Django Management
```bash
make django-shell      # Shell de Django local
make django-shell-prod # Shell de Django producción
make migrate           # Aplicar migraciones local
make superuser         # Crear superusuario local
make collectstatic     # Recopilar archivos estáticos local
```

### 🗄️ Base de datos
```bash
make db-shell          # Shell PostgreSQL local
make db-shell-prod     # Shell PostgreSQL producción
```

### 🧪 Testing y limpieza
```bash
make test              # Ejecutar tests
make clean             # Limpiar contenedores no utilizados
make clean-all         # ⚠️  PELIGRO: Limpiar todo incluyendo volúmenes
```

## 🌐 URLs disponibles (desarrollo)
- **Sitio principal (Nginx):** http://localhost
- **Django directo:** http://localhost:8000
- **Admin Django:** http://localhost/admin
- **API:** http://localhost/api/v1/

## 🔑 Credenciales por defecto
- **Usuario:** admin
- **Contraseña:** admin123

## 📝 Sin Make (Windows)
Si no tienes `make` instalado, usa Docker Compose directamente:

```powershell
# Desarrollo
docker-compose up --build -d
docker-compose exec web bash

# Producción
docker-compose -f docker-compose.prod.yml up --build -d
docker-compose -f docker-compose.prod.yml exec web bash
```