# Script de desarrollo para Windows PowerShell

Write-Host "Iniciando Jardin - Ambiente LOCAL" -ForegroundColor Green
Write-Host "   - Django + PostgreSQL + Nginx" -ForegroundColor Gray
Write-Host ""

# Verificar que Docker está funcionando
try {
    docker --version | Out-Null
    Write-Host "Docker esta funcionando" -ForegroundColor Green
} catch {
    Write-Host "Docker no esta funcionando. Por favor inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Crear archivo .env si no existe
if (!(Test-Path ".env")) {
    Write-Host "Creando archivo .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "Construyendo e iniciando contenedores..." -ForegroundColor Blue
docker-compose up --build -d

Write-Host ""
Write-Host "Esperando a que los servicios esten listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Cyan
Write-Host "   - Sitio principal (Nginx):  http://localhost" -ForegroundColor White
Write-Host "   - Django directo:           http://localhost:8000" -ForegroundColor White
Write-Host "   - Admin Django:             http://localhost/admin" -ForegroundColor White
Write-Host "   - API:                      http://localhost/api/v1/" -ForegroundColor White
Write-Host "   - Health Check:             http://localhost/health/" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales admin: admin / admin123" -ForegroundColor Magenta
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "   - Ver logs:        docker-compose logs -f" -ForegroundColor White
Write-Host "   - Detener:         docker-compose down" -ForegroundColor White
Write-Host "   - Reiniciar:       docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Ambiente LOCAL listo!" -ForegroundColor Green