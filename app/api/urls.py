from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuración del router para ViewSets
router = DefaultRouter()

# Registrar ViewSets base
router.register(r'roles', views.RolViewSet, basename='rol')
router.register(r'jornadas', views.JornadaViewSet, basename='jornada')
router.register(r'salones', views.SalonViewSet, basename='salon')
router.register(r'estados-asistencia', views.EstadoAsistenciaViewSet, basename='estado-asistencia')
router.register(r'categorias', views.CategoriaViewSet, basename='categoria')

# Registrar ViewSets de entidades principales
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'jornadas-salones', views.JornadaSalonViewSet, basename='jornada-salon')
router.register(r'estudiantes', views.EstudianteViewSet, basename='estudiante')
router.register(r'asistencias', views.AsistenciaViewSet, basename='asistencia')
router.register(r'asistencias-apoderados', views.AsistenciaApoderadoViewSet, basename='asistencia-apoderado')
router.register(r'inventario', views.InventarioViewSet, basename='inventario')
router.register(r'movimientos-inventario', views.MovimientoInventarioViewSet, basename='movimiento-inventario')

# Registrar ViewSets de cuotas y finanzas
router.register(r'cuotas', views.CuotaViewSet, basename='cuota')
router.register(r'transacciones', views.TransaccionViewSet, basename='transaccion')

urlpatterns = [
    # Endpoints de autenticación
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    
    # Dashboard
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Status
    path('status/', views.api_status, name='api-status'),
    
    # Router URLs (CRUD endpoints)
    path('', include(router.urls)),
]