from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.contrib.auth import login, logout
from datetime import datetime, date, timedelta

from .models import (
    Rol, Jornada, Salon, EstadoAsistencia, EstadoInventario, Categoria,
    Usuario, JornadaSalon, Estudiante, Asistencia, AsistenciaApoderado, Inventario,
    Cuota, Transaccion, MovimientoInventario
)
from .serializers import (
    RolSerializer, JornadaSerializer, SalonSerializer,
    EstadoAsistenciaSerializer, EstadoInventarioSerializer, CategoriaSerializer,
    UsuarioSerializer, UsuarioListSerializer, JornadaSalonSerializer,
    EstudianteSerializer,
    AsistenciaSerializer, AsistenciaCreateSerializer,
    AsistenciaApoderadoSerializer, InventarioSerializer, InventarioListSerializer,
    LoginSerializer, ChangePasswordSerializer,
    CuotaSerializer, CuotaListSerializer, TransaccionSerializer, TransaccionListSerializer,
    MovimientoInventarioSerializer, MovimientoInventarioListSerializer
)


# ============================================
# ENDPOINT DE STATUS
# ============================================

@api_view(['GET'])
def api_status(request):
    """
    Endpoint para verificar el estado de la API
    """
    return Response({
        'status': 'ok',
        'message': 'Jardin API v1.0 está funcionando correctamente',
        'version': '1.0.0'
    })


# ============================================
# VIEWSETS BASE
# ============================================

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.filter(is_active=True)
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('all') == 'true':
            return Rol.objects.all()
        return queryset


class JornadaViewSet(viewsets.ModelViewSet):
    queryset = Jornada.objects.filter(is_active=True)
    serializer_class = JornadaSerializer
    permission_classes = [permissions.IsAuthenticated]


class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.filter(is_active=True)
    serializer_class = SalonSerializer
    permission_classes = [permissions.IsAuthenticated]


class EstadoAsistenciaViewSet(viewsets.ModelViewSet):
    queryset = EstadoAsistencia.objects.filter(is_active=True)
    serializer_class = EstadoAsistenciaSerializer
    permission_classes = [permissions.IsAuthenticated]


class EstadoInventarioViewSet(viewsets.ModelViewSet):
    queryset = EstadoInventario.objects.filter(is_active=True)
    serializer_class = EstadoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.filter(is_active=True)
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================
# VIEWSETS DE USUARIO
# ============================================

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.filter(is_active=True).select_related('rol')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        rol = self.request.query_params.get('rol')
        search = self.request.query_params.get('search')
        
        if rol:
            queryset = queryset.filter(rol_id=rol)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(email__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        usuario = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not usuario.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Contraseña actual incorrecta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            usuario.set_password(serializer.validated_data['new_password'])
            usuario.save()
            return Response({'message': 'Contraseña actualizada correctamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete del usuario"""
        usuario = self.get_object()
        
        # Prevenir que un usuario se elimine a sí mismo
        if usuario.id == request.user.id:
            return Response(
                {'error': 'No puedes eliminar tu propia cuenta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================
# VIEWSETS DE JORNADA-SALON
# ============================================

class JornadaSalonViewSet(viewsets.ModelViewSet):
    queryset = JornadaSalon.objects.filter(is_active=True).select_related(
        'jornada', 'salon', 'profesor_encargado'
    )
    serializer_class = JornadaSalonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        jornada = self.request.query_params.get('jornada')
        salon = self.request.query_params.get('salon')
        
        if jornada:
            queryset = queryset.filter(jornada_id=jornada)
        if salon:
            queryset = queryset.filter(salon_id=salon)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def estudiantes(self, request, pk=None):
        jornada_salon = self.get_object()
        estudiantes = Estudiante.objects.filter(
            jornada_salon=jornada_salon,
            is_active=True
        )
        serializer = EstudianteSerializer(estudiantes, many=True)
        return Response(serializer.data)


# ============================================
# VIEWSETS DE ESTUDIANTE
# ============================================

class EstudianteViewSet(viewsets.ModelViewSet):
    serializer_class = EstudianteSerializer
    queryset = Estudiante.objects.filter(is_active=True).select_related(
        'jornada_salon', 'jornada_salon__jornada', 'jornada_salon__salon'
    )
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        jornada_salon = self.request.query_params.get('jornada_salon')
        search = self.request.query_params.get('search')
        
        if jornada_salon:
            queryset = queryset.filter(jornada_salon_id=jornada_salon)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(tutor_nombre__icontains=search)
            )
        
        return queryset.order_by('nombre')
    
    @action(detail=True, methods=['get'])
    def asistencias(self, request, pk=None):
        estudiante = self.get_object()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        asistencias = Asistencia.objects.filter(
            estudiante=estudiante,
            is_active=True
        )
        
        if fecha_inicio:
            asistencias = asistencias.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            asistencias = asistencias.filter(fecha__lte=fecha_fin)
        
        asistencias = asistencias.select_related('estado', 'registrado_por').order_by('-fecha')
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)


# ============================================
# VIEWSETS DE ASISTENCIA
# ============================================

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.select_related(
        'estudiante', 'estado'
    )
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AsistenciaCreateSerializer
        return AsistenciaSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        estudiante = self.request.query_params.get('estudiante')
        estado = self.request.query_params.get('estado')
        jornada_salon = self.request.query_params.get('jornada_salon')
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if estudiante:
            queryset = queryset.filter(estudiante_id=estudiante)
        if estado:
            queryset = queryset.filter(estado_id=estado)
        if jornada_salon:
            queryset = queryset.filter(estudiante__jornada_salon_id=jornada_salon)
        
        return queryset.order_by('-fecha', '-id')
    
    @action(detail=False, methods=['post'])
    def registrar_masivo(self, request):
        """Registrar asistencia para múltiples estudiantes"""
        asistencias_data = request.data.get('asistencias', [])
        created = []
        errors = []
        
        for data in asistencias_data:
            serializer = AsistenciaCreateSerializer(data=data)
            if serializer.is_valid():
                asistencia = serializer.save()
                created.append(AsistenciaSerializer(asistencia).data)
            else:
                errors.append({
                    'estudiante': data.get('estudiante'),
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de asistencia"""
        fecha_inicio = request.query_params.get('fecha_inicio', date.today() - timedelta(days=30))
        fecha_fin = request.query_params.get('fecha_fin', date.today())
        
        stats = Asistencia.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            is_active=True
        ).values('estado__nombre').annotate(total=Count('id'))
        
        return Response({
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'por_estado': list(stats)
        })


# ============================================
# VIEWSETS DE ASISTENCIA APODERADO
# ============================================

class AsistenciaApoderadoViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaApoderado.objects.select_related('estudiante')
    serializer_class = AsistenciaApoderadoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        estudiante = self.request.query_params.get('estudiante')
        numero_reunion = self.request.query_params.get('numero_reunion')
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if estudiante:
            queryset = queryset.filter(estudiante_id=estudiante)
        if numero_reunion:
            queryset = queryset.filter(numero_reunion=numero_reunion)
        
        return queryset.order_by('-fecha', '-id')
    
    def create(self, request, *args, **kwargs):
        """Validar que no exista duplicado antes de crear"""
        estudiante_id = request.data.get('estudiante')
        fecha = request.data.get('fecha')
        numero_reunion = request.data.get('numero_reunion')
        
        # Verificar si ya existe un registro para este estudiante en esta fecha/reunión
        filters = {
            'estudiante_id': estudiante_id,
            'fecha': fecha
        }
        
        # Si hay número de reunión, validar por reunión específica
        if numero_reunion:
            filters['numero_reunion'] = numero_reunion
            if AsistenciaApoderado.objects.filter(**filters).exists():
                return Response(
                    {'error': f'El apoderado de este niño ya registró asistencia para la reunión #{numero_reunion}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Si no hay número de reunión, validar que no haya registrado en esta fecha
            if AsistenciaApoderado.objects.filter(**filters).exists():
                return Response(
                    {'error': 'El apoderado de este niño ya registró asistencia hoy'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().create(request, *args, **kwargs)


# ============================================
# VIEWSETS DE INVENTARIO
# ============================================

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.filter(is_active=True).select_related(
        'estado', 'categoria', 'responsable'
    )
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventarioListSerializer
        return InventarioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        categoria = self.request.query_params.get('categoria')
        search = self.request.query_params.get('search')
        
        if estado:
            queryset = queryset.filter(estado_id=estado)
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def dar_de_baja(self, request, pk=None):
        item = self.get_object()
        observacion = request.data.get('observacion', '')
        
        try:
            item.dar_de_baja(observacion)
            return Response({'message': 'Item dado de baja correctamente'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================
# VISTAS DE AUTENTICACIÓN
# ============================================

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            
            # Crear sesión de Django
            login(request, usuario, backend='api.auth_backend.UsuarioBackend')
            
            # Actualizar último acceso
            usuario.ultimo_acceso = timezone.now()
            usuario.save(update_fields=['ultimo_acceso'])
            
            return Response({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'rol': {
                    'id': usuario.rol.id,
                    'nombre': usuario.rol.nombre
                },
                'ultimo_acceso': usuario.ultimo_acceso
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Sesión cerrada correctamente'})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


# ============================================
# VISTAS DE DASHBOARD
# ============================================

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        hoy = date.today()
        
        # Estadísticas generales
        total_estudiantes = Estudiante.objects.filter(is_active=True).count()
        total_personal = Usuario.objects.filter(is_active=True).count()
        
        # Asistencia de hoy
        asistencia_hoy = Asistencia.objects.filter(
            fecha=hoy,
            is_active=True
        ).select_related('estado').values('estado__nombre').annotate(total=Count('id'))
        
        # Inventario por estado
        inventario_stats = Inventario.objects.filter(
            is_active=True
        ).values('estado__nombre').annotate(total=Count('id'))
        
        return Response({
            'estudiantes': {
                'total': total_estudiantes,
            },
            'personal': {
                'total': total_personal,
            },
            'asistencia_hoy': {
                'fecha': hoy,
                'por_estado': list(asistencia_hoy)
            },
            'inventario': {
                'por_estado': list(inventario_stats)
            }
        })


# ============================================
# VIEWSETS PARA CUOTAS Y FINANZAS
# ============================================

class CuotaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cuotas/mensualidades
    
    list: Listar todas las cuotas
    retrieve: Obtener detalle de una cuota
    create: Crear nueva cuota
    update: Actualizar cuota completa
    partial_update: Actualizar cuota parcialmente
    destroy: Desactivar cuota (soft delete)
    """
    queryset = Cuota.objects.all().select_related('estudiante')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CuotaListSerializer
        return CuotaSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por estudiante
        estudiante_id = self.request.query_params.get('estudiante', None)
        if estudiante_id:
            queryset = queryset.filter(estudiante_id=estudiante_id)
        
        # Filtrar por mes
        mes = self.request.query_params.get('mes', None)
        if mes:
            queryset = queryset.filter(mes=mes)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar cuotas vencidas
        vencidas = self.request.query_params.get('vencidas', None)
        if vencidas == 'true':
            hoy = date.today()
            queryset = queryset.filter(
                estado='pending',
                fecha_vencimiento__lt=hoy
            )
        
        return queryset.order_by('-mes', 'estudiante__apellidos')
    
    @action(detail=True, methods=['post'])
    def marcar_pagada(self, request, pk=None):
        """Marcar una cuota como pagada"""
        cuota = self.get_object()
        fecha_pago = request.data.get('fecha_pago', None)
        
        if fecha_pago:
            cuota.marcar_como_pagada(fecha_pago)
        else:
            cuota.marcar_como_pagada()
        
        serializer = self.get_serializer(cuota)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Obtener resumen de cuotas"""
        mes_actual = timezone.now().strftime('%Y-%m')
        
        total_cuotas = self.get_queryset().count()
        cuotas_pagadas = self.get_queryset().filter(estado='paid').count()
        cuotas_pendientes = self.get_queryset().filter(estado='pending').count()
        cuotas_vencidas = self.get_queryset().filter(
            estado='pending',
            fecha_vencimiento__lt=date.today()
        ).count()
        
        # Calcular montos
        monto_total = self.get_queryset().aggregate(total=Sum('monto'))['total'] or 0
        monto_cobrado = self.get_queryset().filter(estado='paid').aggregate(
            total=Sum('monto')
        )['total'] or 0
        monto_pendiente = self.get_queryset().filter(estado='pending').aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        return Response({
            'total_cuotas': total_cuotas,
            'cuotas_pagadas': cuotas_pagadas,
            'cuotas_pendientes': cuotas_pendientes,
            'cuotas_vencidas': cuotas_vencidas,
            'monto_total': float(monto_total),
            'monto_cobrado': float(monto_cobrado),
            'monto_pendiente': float(monto_pendiente)
        })


class TransaccionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar transacciones financieras
    
    list: Listar todas las transacciones
    retrieve: Obtener detalle de una transacción
    create: Crear nueva transacción
    update: Actualizar transacción completa
    partial_update: Actualizar transacción parcialmente
    destroy: Desactivar transacción (soft delete)
    """
    queryset = Transaccion.objects.all().select_related('registrado_por', 'cuota')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TransaccionListSerializer
        return TransaccionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        return queryset.order_by('-fecha', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Obtener resumen financiero"""
        # Filtrar por rango de fechas si se proporciona
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        queryset = self.get_queryset()
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        # Calcular totales
        ingresos = queryset.filter(tipo='income').aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        egresos = queryset.filter(tipo='expense').aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        balance = ingresos - egresos
        
        return Response({
            'ingresos': float(ingresos),
            'egresos': float(egresos),
            'balance': float(balance),
            'total_transacciones': queryset.count()
        })


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar movimientos de inventario
    
    list: Listar todos los movimientos
    retrieve: Obtener detalle de un movimiento
    create: Crear nuevo movimiento (actualiza automáticamente el inventario)
    """
    queryset = MovimientoInventario.objects.all().select_related('item', 'registrado_por')
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # Solo lectura y creación
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MovimientoInventarioListSerializer
        return MovimientoInventarioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por item
        item_id = self.request.query_params.get('item', None)
        if item_id:
            queryset = queryset.filter(item_id=item_id)
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)
