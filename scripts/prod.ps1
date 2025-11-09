# Script para iniciar ambiente de PRODUCCIÓN
# Jardin - Docker Compose

Write-Host "Iniciando Jardin - Ambiente PRODUCCIÓN" -ForegroundColor Green
Write-Host "   - Django + PostgreSQL + Nginx" -ForegroundColor Gray

# Verificar que Docker está funcionando
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker no está funcionando"
    }
    Write-Host "Docker esta funcionando" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker no está disponible" -ForegroundColor Red
    Write-Host "Asegúrese de que Docker Desktop esté iniciado" -ForegroundColor Yellow
    exit 1
}

# Crear archivo .env si no existe
if (!(Test-Path ".env")) {
    Write-Host "Creando archivo .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "Construyendo e iniciando contenedores de PRODUCCIÓN..." -ForegroundColor Blue
docker-compose -f docker-compose.prod.yml up --build -d

Write-Host ""
Write-Host "Esperando a que los servicios esten listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "URLs disponibles en PRODUCCIÓN:" -ForegroundColor Cyan
Write-Host "   - Sitio principal (Nginx):  http://localhost" -ForegroundColor White
Write-Host "   - Sitio HTTPS:              https://localhost" -ForegroundColor White
Write-Host "   - Admin Django:             http://localhost/admin" -ForegroundColor White
Write-Host "   - API:                      http://localhost/api/v1/" -ForegroundColor White
Write-Host "   - Health Check:             http://localhost/health/" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales admin: admin / admin123" -ForegroundColor Magenta
Write-Host ""
Write-Host "Comandos utiles para PRODUCCIÓN:" -ForegroundColor Cyan
Write-Host "   - Ver logs:        docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor White
Write-Host "   - Detener:         docker-compose -f docker-compose.prod.yml down" -ForegroundColor White
Write-Host "   - Reiniciar:       docker-compose -f docker-compose.prod.yml restart" -ForegroundColor White
Write-Host ""
Write-Host "Ambiente PRODUCCIÓN listo!" -ForegroundColor Green