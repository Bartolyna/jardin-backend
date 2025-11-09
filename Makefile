# Makefile simplificado para el proyecto Jardin

# Configuración
COMPOSE_FILE = docker-compose.yml
COMPOSE_FILE_PROD = docker-compose.prod.yml

# Comandos por defecto
.PHONY: help
help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Desarrollo Local
.PHONY: up-dev
up-dev: ## Iniciar ambiente completo LOCAL (Django + PostgreSQL + Nginx)
	@echo "🚀 Iniciando ambiente LOCAL completo..."
	docker-compose -f $(COMPOSE_FILE) up --build -d
	@echo "🌐 URLs disponibles:"
	@echo "   - Sitio principal (Nginx):  http://localhost"
	@echo "   - Django directo:           http://localhost:8000"
	@echo "   - Admin Django:             http://localhost/admin"
	@echo "   - API:                      http://localhost/api/v1/"
	@echo "👤 Credenciales: admin / admin123"

.PHONY: up-dev-simple
up-dev-simple: ## Iniciar solo Django + PostgreSQL LOCAL (sin Nginx)
	@echo "🚀 Iniciando Django + PostgreSQL LOCAL..."
	docker-compose -f $(COMPOSE_FILE) up --build -d db web
	@echo "🌐 Django disponible en: http://localhost:8000"

.PHONY: down
down: ## Detener todos los servicios LOCAL
	docker-compose -f $(COMPOSE_FILE) down

.PHONY: logs
logs: ## Ver logs en tiempo real LOCAL
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: restart
restart: ## Reiniciar servicios LOCAL
	docker-compose -f $(COMPOSE_FILE) restart

.PHONY: status
status: ## Ver estado de los servicios LOCAL
	docker-compose -f $(COMPOSE_FILE) ps

# Producción
.PHONY: up-prod
up-prod: ## Iniciar ambiente de producción
	@echo "🚀 Iniciando ambiente de PRODUCCIÓN..."
	docker-compose -f $(COMPOSE_FILE_PROD) up --build -d
	@echo "🌐 Sitio disponible en: http://localhost"

.PHONY: down-prod
down-prod: ## Detener ambiente de producción
	docker-compose -f $(COMPOSE_FILE_PROD) down

.PHONY: logs-prod
logs-prod: ## Ver logs de producción
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f

.PHONY: status-prod
status-prod: ## Ver estado de servicios de producción
	docker-compose -f $(COMPOSE_FILE_PROD) ps

# Acceso a contenedores LOCAL
.PHONY: exec-web-local
exec-web-local: ## Entrar al contenedor web Django LOCAL
	docker-compose -f $(COMPOSE_FILE) exec web bash

.PHONY: exec-db-local
exec-db-local: ## Entrar al contenedor PostgreSQL LOCAL
	docker-compose -f $(COMPOSE_FILE) exec db bash

.PHONY: exec-nginx-local
exec-nginx-local: ## Entrar al contenedor Nginx LOCAL
	docker-compose -f $(COMPOSE_FILE) exec nginx ash

# Acceso a contenedores PRODUCCIÓN
.PHONY: exec-web-prod
exec-web-prod: ## Entrar al contenedor web Django PRODUCCIÓN
	docker-compose -f $(COMPOSE_FILE_PROD) exec web bash

.PHONY: exec-db-prod
exec-db-prod: ## Entrar al contenedor PostgreSQL PRODUCCIÓN
	docker-compose -f $(COMPOSE_FILE_PROD) exec db bash

.PHONY: exec-nginx-prod
exec-nginx-prod: ## Entrar al contenedor Nginx PRODUCCIÓN
	docker-compose -f $(COMPOSE_FILE_PROD) exec nginx ash

# Django Management LOCAL
.PHONY: django-shell
django-shell: ## Acceder al shell de Django LOCAL
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py shell

.PHONY: django-shell-prod
django-shell-prod: ## Acceder al shell de Django PRODUCCIÓN
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py shell

.PHONY: migrate
migrate: ## Aplicar migraciones LOCAL
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py migrate

.PHONY: superuser
superuser: ## Crear superusuario LOCAL
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py createsuperuser

.PHONY: collectstatic
collectstatic: ## Recopilar archivos estáticos LOCAL
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py collectstatic --noinput

# Base de datos LOCAL
.PHONY: db-shell
db-shell: ## Acceder al shell de PostgreSQL LOCAL
	docker-compose -f $(COMPOSE_FILE) exec db psql -U jardin_user jardin_db_local

.PHONY: db-shell-prod
db-shell-prod: ## Acceder al shell de PostgreSQL PRODUCCIÓN
	docker-compose -f $(COMPOSE_FILE_PROD) exec db psql -U jardin_user jardin_db

# Limpieza
.PHONY: clean
clean: ## Limpiar contenedores e imágenes no utilizadas
	docker system prune -f

.PHONY: clean-all
clean-all: ## PELIGRO: Limpiar todo incluyendo volúmenes
	@echo "⚠️  PELIGRO: Esto eliminará todos los datos."
	@echo "¿Estás seguro? (y/N): " && read ans && [ $${ans:-N} = y ]
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -af

# Testing LOCAL
.PHONY: test
test: ## Ejecutar tests LOCAL
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py test