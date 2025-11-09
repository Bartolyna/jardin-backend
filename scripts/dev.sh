#!/bin/bash

# Script simplificado para desarrollo local con Nginx

echo "🚀 Iniciando Fundación - Ambiente de Desarrollo"
echo "   - Django + PostgreSQL + Nginx"
echo ""

# Verificar que Docker está funcionando
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker no está funcionando. Por favor inicia Docker Desktop."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📄 Creando archivo .env..."
    cp .env.example .env
fi

echo "🔨 Construyendo e iniciando contenedores..."
docker-compose -f docker-compose.dev.yml up --build -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

echo ""
echo "🌐 URLs disponibles:"
echo "   - Sitio principal (Nginx):  http://localhost"
echo "   - Django directo:           http://localhost:8000"  
echo "   - Admin Django:             http://localhost/admin"
echo "   - API:                      http://localhost/api/v1/"
echo "   - Health Check:             http://localhost/health/"
echo ""
echo "👤 Credenciales admin: admin / admin123"
echo ""
echo "📊 Comandos útiles:"
echo "   - Ver logs:        docker-compose -f docker-compose.dev.yml logs -f"
echo "   - Detener:         docker-compose -f docker-compose.dev.yml down"
echo "   - Reiniciar:       docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "✅ ¡Ambiente listo para desarrollo!"