# Script de PowerShell para gestionar el entorno Docker del Jardín Tricahue
# Uso: .\docker-manager.ps1 [comando]

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "reset", "setup", "help")]
    [string]$Command = "help"
)

# Colores para output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param($Message, $Color = "White")
    Write-Host "🐳 $Message" -ForegroundColor $Color
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Blue
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Start-Services {
    Write-Status "Iniciando servicios de Docker..."
    
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker no está ejecutándose. Inicia Docker Desktop primero."
        return
    }
    
    Write-Info "Iniciando base de datos PostgreSQL..."
    docker-compose up -d db
    
    Write-Info "Esperando a que PostgreSQL esté listo..."
    Start-Sleep -Seconds 10
    
    # Verificar estado de la base de datos
    $dbStatus = docker-compose ps db --format "{{.State}}"
    if ($dbStatus -eq "running") {
        Write-Success "PostgreSQL iniciado correctamente"
        
        # Verificar conexión desde Django
        Write-Info "Verificando conexión desde Django..."
        Set-Location app
        ..\..\.venv\Scripts\python.exe manage.py check_database --wait --create-db --settings=jardin.settings_postgres
        Set-Location ..
    } else {
        Write-Error "Error iniciando PostgreSQL"
        Show-Logs
    }
}

function Stop-Services {
    Write-Status "Deteniendo servicios..."
    docker-compose down
    Write-Success "Servicios detenidos"
}

function Restart-Services {
    Write-Status "Reiniciando servicios..."
    Stop-Services
    Start-Sleep -Seconds 3
    Start-Services
}

function Show-Status {
    Write-Status "Estado de los servicios:"
    Write-Host ""
    
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker no está ejecutándose"
        return
    }
    
    docker-compose ps
    Write-Host ""
    
    # Verificar conectividad
    Write-Info "Verificando conectividad..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5433" -TimeoutSec 2 -ErrorAction SilentlyContinue
        Write-Success "Puerto 5433 (PostgreSQL) accesible"
    }
    catch {
        Write-Warning "Puerto 5433 (PostgreSQL) no accesible"
    }
}

function Show-Logs {
    Write-Status "Mostrando logs de la base de datos..."
    docker-compose logs --tail=50 db
}

function Reset-Environment {
    Write-Warning "¡CUIDADO! Esto eliminará todos los datos de la base de datos."
    $confirm = Read-Host "¿Estás seguro? (yes/no)"
    
    if ($confirm -eq "yes") {
        Write-Status "Eliminando contenedores y volúmenes..."
        docker-compose down -v
        docker-compose up -d db
        
        Write-Info "Esperando a que PostgreSQL esté listo..."
        Start-Sleep -Seconds 10
        
        Write-Info "Configurando base de datos desde cero..."
        Set-Location app
        ..\..\.venv\Scripts\python.exe manage.py check_database --create-db --settings=jardin.settings_postgres
        ..\..\.venv\Scripts\python.exe manage.py setup_database --create-admin --settings=jardin.settings_postgres
        Set-Location ..
        
        Write-Success "Entorno reiniciado completamente"
    } else {
        Write-Info "Operación cancelada"
    }
}

function Setup-Environment {
    Write-Status "Configurando entorno completo..."
    
    # Verificar Docker
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker no está ejecutándose. Inicia Docker Desktop primero."
        return
    }
    
    # Iniciar servicios
    Start-Services
    
    # Configurar base de datos
    Write-Info "Configurando base de datos Django..."
    Set-Location app
    
    try {
        ..\..\.venv\Scripts\python.exe manage.py migrate --settings=jardin.settings_postgres
        ..\..\.venv\Scripts\python.exe manage.py setup_database --create-admin --settings=jardin.settings_postgres
        Write-Success "Base de datos configurada correctamente"
        
        Write-Host ""
        Write-Success "🎉 ¡Entorno configurado exitosamente!"
        Write-Info "Puedes iniciar el servidor con: python manage.py runserver --settings=jardin.settings_postgres"
        Write-Info "Panel de admin: http://localhost:8000/admin/"
        Write-Info "Usuario: admin@jardintricahue.cl"
        Write-Info "Contraseña: admin123"
    }
    catch {
        Write-Error "Error configurando la base de datos: $_"
    }
    finally {
        Set-Location ..
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "🐳 DOCKER MANAGER - Jardín Tricahue" -ForegroundColor $Blue
    Write-Host "=================================" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor $Yellow
    Write-Host "  start   - Inicia los servicios Docker" -ForegroundColor $Green
    Write-Host "  stop    - Detiene los servicios Docker" -ForegroundColor $Green
    Write-Host "  restart - Reinicia los servicios Docker" -ForegroundColor $Green
    Write-Host "  status  - Muestra el estado de los servicios" -ForegroundColor $Green
    Write-Host "  logs    - Muestra los logs de PostgreSQL" -ForegroundColor $Green
    Write-Host "  reset   - Reinicia todo el entorno (¡ELIMINA DATOS!)" -ForegroundColor $Red
    Write-Host "  setup   - Configura todo el entorno desde cero" -ForegroundColor $Green
    Write-Host "  help    - Muestra esta ayuda" -ForegroundColor $Green
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor $Yellow
    Write-Host "  .\docker-manager.ps1 start"
    Write-Host "  .\docker-manager.ps1 status"
    Write-Host "  .\docker-manager.ps1 logs"
    Write-Host ""
    Write-Host "Notas:" -ForegroundColor $Blue
    Write-Host "- Asegúrate de que Docker Desktop esté ejecutándose"
    Write-Host "- El entorno virtual debe estar activado para algunos comandos"
    Write-Host "- PostgreSQL estará disponible en localhost:5433"
}

# Ejecutar comando
switch ($Command) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "reset" { Reset-Environment }
    "setup" { Setup-Environment }
    "help" { Show-Help }
    default { Show-Help }
}