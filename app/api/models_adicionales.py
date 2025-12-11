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
        ordering = ['-mes', 'estudiante']
    
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
