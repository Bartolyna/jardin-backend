from rest_framework import serializers
from .models import (
    Rol, Jornada, Salon, EstadoAsistencia, EstadoInventario, Categoria,
    Usuario, JornadaSalon, Estudiante, Asistencia, AsistenciaApoderado, Inventario,
    Cuota, Transaccion, MovimientoInventario
)


# ============================================
# SERIALIZERS BASE
# ============================================

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class JornadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jornada
        fields = ['id', 'nombre', 'hora_inicio', 'hora_fin', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['id', 'nombre', 'capacidad', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class EstadoAsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoAsistencia
        fields = ['id', 'nombre', 'color', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class EstadoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoInventario
        fields = ['id', 'nombre', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ============================================
# SERIALIZERS DE USUARIO
# ============================================

class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'rol', 'rol_nombre', 'nombre', 'email', 'password',
            'telefono', 'ultimo_acceso', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'ultimo_acceso']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario.objects.create(**validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email', 'rol_nombre', 'is_active']


# ============================================
# SERIALIZERS DE JORNADA-SALON
# ============================================

class JornadaSalonSerializer(serializers.ModelSerializer):
    jornada_nombre = serializers.CharField(source='jornada.nombre', read_only=True)
    salon_nombre = serializers.CharField(source='salon.nombre', read_only=True)
    profesor_nombre = serializers.CharField(source='profesor_encargado.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = JornadaSalon
        fields = [
            'id', 'jornada', 'jornada_nombre', 'salon', 'salon_nombre',
            'profesor_encargado', 'profesor_nombre', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# ============================================
# SERIALIZERS DE ESTUDIANTE
# ============================================

class EstudianteSerializer(serializers.ModelSerializer):
    # Mapear campos del modelo a lo que espera el frontend
    apellidos = serializers.SerializerMethodField()
    apoderado_nombre = serializers.CharField(source='tutor_nombre')
    apoderado_telefono = serializers.CharField(source='tutor_telefono')
    salon = serializers.IntegerField(source='jornada_salon.salon.id', read_only=True)
    salon_nombre = serializers.CharField(source='jornada_salon.salon.nombre', read_only=True)
    jornada = serializers.IntegerField(source='jornada_salon.jornada.id', read_only=True)
    jornada_nombre = serializers.CharField(source='jornada_salon.jornada.nombre', read_only=True)
    edad = serializers.ReadOnlyField(source='edad_calculada')
    
    class Meta:
        model = Estudiante
        fields = [
            'id', 'nombre', 'apellidos', 'fecha_nacimiento', 'edad',
            'apoderado_nombre', 'apoderado_telefono',
            'salon', 'salon_nombre', 'jornada', 'jornada_nombre', 
            'jornada_salon', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'edad', 'salon', 'salon_nombre', 'jornada', 'jornada_nombre', 'apellidos']
    
    def get_apellidos(self, obj):
        return ""
    
    def create(self, validated_data):
        # Mapear apoderado_* de vuelta a tutor_*
        if 'tutor_nombre' in validated_data:
            pass  # Ya viene con el nombre correcto del source
        if 'tutor_telefono' in validated_data:
            pass  # Ya viene con el nombre correcto del source
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


# ============================================
# SERIALIZERS DE ASISTENCIA
# ============================================

class AsistenciaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='estudiante.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    estado_color = serializers.CharField(source='estado.color', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = [
            'id', 'estudiante', 'estudiante_nombre', 'estado', 'estado_nombre', 'estado_color',
            'fecha', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AsistenciaCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación masiva de asistencias"""
    
    class Meta:
        model = Asistencia
        fields = ['estudiante', 'estado', 'fecha']


# ============================================
# SERIALIZERS DE ASISTENCIA APODERADO
# ============================================

class AsistenciaApoderadoSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='estudiante.nombre', read_only=True)
    
    class Meta:
        model = AsistenciaApoderado
        fields = [
            'id', 'estudiante', 'estudiante_nombre', 'nombre_apoderado', 'fecha',
            'numero_reunion', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# ============================================
# SERIALIZERS DE INVENTARIO
# ============================================

class InventarioSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    responsable_nombre = serializers.CharField(source='responsable.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = Inventario
        fields = [
            'id', 'estado', 'estado_nombre', 'categoria', 'categoria_nombre', 'codigo',
            'nombre', 'descripcion', 'fecha_ingreso', 'fecha_baja', 'valor_compra',
            'ubicacion', 'responsable', 'responsable_nombre', 'observacion',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InventarioListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Inventario
        fields = ['id', 'codigo', 'nombre', 'estado_nombre', 'categoria_nombre', 'is_active']


# ============================================
# SERIALIZERS DE AUTENTICACIÓN
# ============================================

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email y contraseña son requeridos")
        
        try:
            usuario = Usuario.objects.get(email=email, is_active=True)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Credenciales inválidas")
        
        if not usuario.check_password(password):
            raise serializers.ValidationError("Credenciales inválidas")
        
        data['usuario'] = usuario
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    
    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres")
        return value


# ============================================
# SERIALIZERS PARA CUOTAS Y FINANZAS
# ============================================

class CuotaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='estudiante.nombre', read_only=True)
    
    class Meta:
        model = Cuota
        fields = [
            'id', 'estudiante', 'estudiante_nombre',
            'monto', 'mes', 'fecha_vencimiento', 'fecha_pago', 'estado', 'notas',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_mes(self, value):
        import re
        if not re.match(r'^\d{4}-\d{2}$', value):
            raise serializers.ValidationError("El mes debe tener formato YYYY-MM")
        return value


class CuotaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar cuotas"""
    estudiante_nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Cuota
        fields = ['id', 'estudiante_nombre_completo', 'monto', 'mes', 'fecha_vencimiento', 'estado']
    
    def get_estudiante_nombre_completo(self, obj):
        return obj.estudiante.nombre


class TransaccionSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.CharField(source='registrado_por.nombre', read_only=True)
    cuota_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaccion
        fields = [
            'id', 'tipo', 'monto', 'fecha', 'descripcion', 'referencia',
            'cuota', 'cuota_info', 'registrado_por', 'registrado_por_nombre',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_cuota_info(self, obj):
        if obj.cuota:
            return {
                'id': obj.cuota.id,
                'mes': obj.cuota.mes,
                'estudiante': obj.cuota.estudiante.nombre
            }
        return None


class TransaccionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar transacciones"""
    tipo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaccion
        fields = ['id', 'tipo', 'tipo_display', 'monto', 'fecha', 'descripcion']
    
    def get_tipo_display(self, obj):
        return 'Ingreso' if obj.tipo == 'income' else 'Egreso'


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    item_nombre = serializers.CharField(source='item.nombre', read_only=True)
    registrado_por_nombre = serializers.CharField(source='registrado_por.nombre', read_only=True)
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'item', 'item_nombre', 'tipo', 'cantidad',
            'cantidad_anterior', 'cantidad_nueva', 'notas',
            'registrado_por', 'registrado_por_nombre',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'cantidad_anterior', 'cantidad_nueva']
    
    def validate(self, data):
        """Validar y calcular cantidades antes y después del movimiento"""
        item = data.get('item')
        tipo = data.get('tipo')
        cantidad = data.get('cantidad')
        
        if item:
            data['cantidad_anterior'] = item.cantidad
            
            if tipo == 'ingreso':
                data['cantidad_nueva'] = item.cantidad + cantidad
            else:  # egreso
                if item.cantidad < cantidad:
                    raise serializers.ValidationError({
                        'cantidad': f'No hay suficiente stock. Disponible: {item.cantidad}'
                    })
                data['cantidad_nueva'] = item.cantidad - cantidad
        
        return data
    
    def create(self, validated_data):
        """Crear movimiento y actualizar inventario"""
        movimiento = super().create(validated_data)
        
        # Actualizar cantidad en inventario
        item = movimiento.item
        item.cantidad = movimiento.cantidad_nueva
        item.save()
        
        return movimiento


class MovimientoInventarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar movimientos"""
    item_nombre = serializers.CharField(source='item.nombre', read_only=True)
    tipo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MovimientoInventario
        fields = ['id', 'item_nombre', 'tipo', 'tipo_display', 'cantidad', 'created_at']
    
    def get_tipo_display(self, obj):
        return 'Ingreso' if obj.tipo == 'ingreso' else 'Egreso'

