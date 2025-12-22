from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone


# ============================================
# MODELOS BASE ABSTRACTOS
# ============================================

class TimeStampedModel(models.Model):
    """Modelo abstracto que añade timestamps automáticos"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Modelo abstracto que añade soft delete"""
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado sin borrarlo de la BD"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaura un registro eliminado"""
        self.is_active = True
        self.deleted_at = None
        self.save()


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """Modelo base que combina timestamps y soft delete"""
    class Meta:
        abstract = True


# ============================================
# 1. TABLAS BASE (sin dependencias)
# ============================================

class Rol(BaseModel):
    """Modelo para los roles de usuario"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        db_table = 'rol'
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Jornada(BaseModel):
    """Modelo para las jornadas de trabajo"""
    nombre = models.CharField(max_length=50)
    hora_inicio = models.TimeField(null=True, blank=True, verbose_name="Hora de inicio")
    hora_fin = models.TimeField(null=True, blank=True, verbose_name="Hora de fin")
    
    class Meta:
        db_table = 'jornada'
        verbose_name = "Jornada"
        verbose_name_plural = "Jornadas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Salon(BaseModel):
    """Modelo para los salones"""
    nombre = models.CharField(max_length=50)
    capacidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        verbose_name="Capacidad máxima"
    )
    
    class Meta:
        db_table = 'salon'
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class EstadoAsistencia(BaseModel):
    """Modelo para los estados de asistencia"""
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#000000', verbose_name="Color (hex)")
    
    class Meta:
        db_table = 'estado_asistencia'
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class EstadoInventario(BaseModel):
    """Modelo para los estados del inventario"""
    nombre = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'estado_inventario'
        verbose_name = "Estado de Inventario"
        verbose_name_plural = "Estados de Inventario"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Categoria(BaseModel):
    """Modelo para las categorías de inventario"""
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        db_table = 'categoria'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ============================================
# 2. TABLA USUARIOS (CON HASH DE CONTRASEÑAS)
# ============================================

class Usuario(BaseModel):
    """Modelo para los usuarios del sistema con hash de contraseñas"""
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,  # PROTECT en lugar de CASCADE
        related_name='usuarios',
        verbose_name="Rol"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre completo")
    email = models.EmailField(max_length=254, unique=True, verbose_name="Correo electrónico")
    password = models.CharField(max_length=255, verbose_name="Contraseña")  # Renombrado de 'contraseña'
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El teléfono debe tener entre 9 y 15 dígitos"
        )],
        verbose_name="Teléfono"
    )
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name="Último acceso")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Último login")
    
    # Propiedades requeridas para compatibilidad con Django auth
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    # Backend de autenticación necesita estos métodos
    def get_username(self):
        return self.email
    
    class Meta:
        db_table = 'usuario'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        indexes = [
            models.Index(fields=['email'], name='idx_usuario_email'),
            models.Index(fields=['rol'], name='idx_usuario_rol'),
            models.Index(fields=['is_active'], name='idx_usuario_activo'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"
    
    def set_password(self, raw_password):
        """Establece la contraseña hasheada"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verifica si la contraseña es correcta"""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        """Override save para hashear la contraseña si es necesaria"""
        # Si la contraseña no está hasheada (no empieza con algoritmo de hash)
        if self.password and not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)


# ============================================
# 3. TABLA RELACIONAL: jornadas_salones
# ============================================

class JornadaSalon(BaseModel):
    """Modelo para la relación entre jornadas y salones"""
    jornada = models.ForeignKey(
        Jornada,
        on_delete=models.PROTECT,  # PROTECT en lugar de CASCADE
        related_name='jornadas_salones',
        verbose_name="Jornada"
    )
    salon = models.ForeignKey(
        Salon,
        on_delete=models.PROTECT,  # PROTECT en lugar de CASCADE
        related_name='jornadas_salones',
        verbose_name="Salón"
    )
    profesor_encargado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,  # SET_NULL en lugar de CASCADE
        null=True,
        blank=True,
        related_name='jornadas_salones_encargadas',
        verbose_name="Profesor encargado"
    )
    
    class Meta:
        db_table = 'jornada_salon'
        verbose_name = "Jornada-Salón"
        verbose_name_plural = "Jornadas-Salones"
        unique_together = [['jornada', 'salon']]
        indexes = [
            models.Index(fields=['jornada', 'salon'], name='idx_jornada_salon'),
        ]
    
    def __str__(self):
        return f"{self.jornada.nombre} - {self.salon.nombre}"


# ============================================
# 4. TABLA ESTUDIANTES
# ============================================

class Estudiante(BaseModel):
    """Modelo para los estudiantes - Campos esenciales únicamente"""
    jornada_salon = models.ForeignKey(
        JornadaSalon,
        on_delete=models.PROTECT,
        related_name='estudiantes',
        verbose_name="Jornada-Salón"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre completo")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    
    # Información del tutor/apoderado
    tutor_nombre = models.CharField(max_length=100, verbose_name="Nombre del tutor")
    tutor_telefono = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El teléfono debe tener entre 9 y 15 dígitos"
        )],
        verbose_name="Teléfono del tutor"
    )
    
    class Meta:
        db_table = 'estudiante'
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        indexes = [
            models.Index(fields=['jornada_salon'], name='idx_estudiante_jornada_salon'),
            models.Index(fields=['is_active'], name='idx_estudiante_activo'),
        ]
    
    def __str__(self):
        return self.nombre
    
    @property
    def edad_calculada(self):
        """Calcula la edad actual del estudiante"""
        if self.fecha_nacimiento:
            today = timezone.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None


# ============================================
# 5. TABLA ASISTENCIAS
# ============================================

class Asistencia(TimeStampedModel):
    """Modelo para el registro de asistencia"""
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.PROTECT,
        related_name='asistencias',
        verbose_name="Estudiante"
    )
    estado = models.ForeignKey(
        EstadoAsistencia,
        on_delete=models.PROTECT,
        related_name='asistencias',
        verbose_name="Estado"
    )
    fecha = models.DateField(verbose_name="Fecha")
    
    class Meta:
        db_table = 'asistencia'
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = [['estudiante', 'fecha']]
        indexes = [
            models.Index(fields=['fecha'], name='idx_asistencia_fecha'),
            models.Index(fields=['estudiante'], name='idx_asistencia_estudiante'),
            models.Index(fields=['estado'], name='idx_asistencia_estado'),
            models.Index(fields=['-fecha'], name='idx_asistencia_fecha_desc'),
        ]
        ordering = ['-fecha', 'estudiante__nombre']
    
    def __str__(self):
        return f"{self.estudiante.nombre} - {self.fecha} ({self.estado.nombre})"


# ============================================
# 6. TABLA ASISTENCIA APODERADO
# ============================================

class AsistenciaApoderado(TimeStampedModel):
    """Modelo para el registro de asistencia de apoderados"""
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.PROTECT,
        related_name='asistencias_apoderados',
        verbose_name="Estudiante"
    )
    nombre_apoderado = models.CharField(max_length=100, verbose_name="Nombre del apoderado")
    fecha = models.DateField(verbose_name="Fecha")
    numero_reunion = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de reunión")
    
    class Meta:
        db_table = 'asistencia_apoderado'
        verbose_name = "Asistencia de Apoderado"
        verbose_name_plural = "Asistencias de Apoderados"
        indexes = [
            models.Index(fields=['fecha'], name='idx_asist_apod_fecha'),
            models.Index(fields=['estudiante'], name='idx_asist_apod_estudiante'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'fecha'],
                name='unique_estudiante_fecha_asistencia_apoderado'
            )
        ]
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.nombre_apoderado} - {self.estudiante.nombre} ({self.fecha})"


# ============================================
# 7. TABLA INVENTARIO
# ============================================

class Inventario(BaseModel):
    """Modelo para el inventario"""
    estado = models.ForeignKey(
        EstadoInventario,
        on_delete=models.PROTECT,  # PROTECT en lugar de CASCADE
        related_name='inventarios',
        verbose_name="Estado"
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # PROTECT en lugar de CASCADE
        related_name='inventarios',
        verbose_name="Categoría"
    )
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # Fechas
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso")
    fecha_baja = models.DateField(null=True, blank=True, verbose_name="Fecha de baja")
    
    # Información adicional
    valor_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Valor de compra"
    )
    ubicacion = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ubicación")
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,  # SET_NULL en lugar de CASCADE
        null=True,
        blank=True,
        related_name='inventarios_responsable',
        verbose_name="Responsable"
    )
    observacion = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    
    class Meta:
        db_table = 'inventario'
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        indexes = [
            models.Index(fields=['codigo'], name='idx_inventario_codigo'),
            models.Index(fields=['categoria'], name='idx_inventario_categoria'),
            models.Index(fields=['estado'], name='idx_inventario_estado'),
            models.Index(fields=['is_active'], name='idx_inventario_activo'),
        ]
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def dar_de_baja(self, motivo=None):
        """Da de baja un item del inventario"""
        self.fecha_baja = timezone.now().date()
        if motivo:
            self.observacion = f"{self.observacion or ''}\nBaja: {motivo}".strip()
        self.soft_delete()


# ============================================
# MODELOS ADICIONALES PARA CUOTAS Y FINANZAS
# ============================================

# MODELO: CUOTA/MENSUALIDAD
class Cuota(BaseModel):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.PROTECT,
        related_name='cuotas',
        verbose_name="Estudiante"
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto"
    )
    mes = models.CharField(max_length=7, verbose_name="Mes")  # Formato: 2024-01
    fecha_vencimiento = models.DateField(verbose_name="Fecha de vencimiento")
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de pago")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('paid', 'Pagada'),
            ('overdue', 'Vencida'),
        ],
        default='pending',
        verbose_name="Estado"
    )
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    
    class Meta:
        db_table = 'cuota'
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        unique_together = [['estudiante', 'mes']]
        indexes = [
            models.Index(fields=['estudiante'], name='idx_cuota_estudiante'),
            models.Index(fields=['mes'], name='idx_cuota_mes'),
            models.Index(fields=['estado'], name='idx_cuota_estado'),
            models.Index(fields=['fecha_vencimiento'], name='idx_cuota_vencimiento'),
        ]
        ordering = ['-mes', 'estudiante__nombre']
    
    def __str__(self):
        return f"Cuota {self.mes} - {self.estudiante.nombre}"
    
    def marcar_como_pagada(self, fecha_pago=None):
        """Marca la cuota como pagada"""
        from django.utils import timezone
        self.estado = 'paid'
        self.fecha_pago = fecha_pago or timezone.now().date()
        self.save()


# MODELO: TRANSACCIÓN FINANCIERA
class Transaccion(BaseModel):
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('income', 'Ingreso'),
            ('expense', 'Egreso'),
        ],
        verbose_name="Tipo"
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto"
    )
    fecha = models.DateField(verbose_name="Fecha")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia")
    cuota = models.ForeignKey(
        'Cuota',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones',
        verbose_name="Cuota relacionada"
    )
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='transacciones_registradas',
        verbose_name="Registrado por"
    )
    
    class Meta:
        db_table = 'transaccion'
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        indexes = [
            models.Index(fields=['tipo'], name='idx_transaccion_tipo'),
            models.Index(fields=['fecha'], name='idx_transaccion_fecha'),
            models.Index(fields=['-fecha'], name='idx_transaccion_fecha_desc'),
            models.Index(fields=['cuota'], name='idx_transaccion_cuota'),
        ]
        ordering = ['-fecha', '-created_at']
    
    def __str__(self):
        tipo_display = 'Ingreso' if self.tipo == 'income' else 'Egreso'
        return f"{tipo_display} - ${self.monto} ({self.fecha})"


# MODELO: MOVIMIENTO DE INVENTARIO
class MovimientoInventario(BaseModel):
    item = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name="Item"
    )
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('ingreso', 'Ingreso'),
            ('egreso', 'Egreso'),
        ],
        verbose_name="Tipo"
    )
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    cantidad_anterior = models.IntegerField(verbose_name="Cantidad anterior")
    cantidad_nueva = models.IntegerField(verbose_name="Cantidad nueva")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='movimientos_inventario',
        verbose_name="Registrado por"
    )
    
    class Meta:
        db_table = 'movimiento_inventario'
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        indexes = [
            models.Index(fields=['item'], name='idx_mov_inv_item'),
            models.Index(fields=['tipo'], name='idx_mov_inv_tipo'),
            models.Index(fields=['-created_at'], name='idx_mov_inv_fecha'),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tipo} - {self.item.nombre} ({self.cantidad})"
