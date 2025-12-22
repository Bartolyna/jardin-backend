from django.contrib import admin
from .models import (
    Rol, Jornada, Salon, EstadoAsistencia, EstadoInventario, Categoria,
    Usuario, JornadaSalon, Estudiante, Asistencia, AsistenciaApoderado, Inventario
)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'is_active', 'created_at')
    search_fields = ('nombre',)
    list_filter = ('is_active',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'hora_inicio', 'hora_fin', 'is_active')
    search_fields = ('nombre',)
    list_filter = ('is_active',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'capacidad', 'is_active')
    search_fields = ('nombre',)
    list_filter = ('is_active',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(EstadoAsistencia)
class EstadoAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'color', 'is_active')
    search_fields = ('nombre',)
    list_filter = ('is_active',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(EstadoInventario)
class EstadoInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'is_active')
    search_fields = ('nombre',)
    list_filter = ('is_active',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'is_active')
    search_fields = ('nombre',)
    list_filter = ('is_active',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'rol', 'is_active', 'created_at')
    list_filter = ('rol', 'is_active')
    search_fields = ('nombre', 'email')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'ultimo_acceso')
    exclude = ('password',)  # No mostrar el hash de la contraseña


@admin.register(JornadaSalon)
class JornadaSalonAdmin(admin.ModelAdmin):
    list_display = ('id', 'jornada', 'salon', 'profesor_encargado', 'is_active')
    list_filter = ('jornada', 'salon', 'is_active')
    ordering = ('jornada', 'salon')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_nacimiento', 'jornada_salon', 'tutor_nombre', 'is_active')
    list_filter = ('jornada_salon', 'is_active')
    search_fields = ('nombre', 'tutor_nombre')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('estudiante__nombre',)
    ordering = ('-fecha', 'estudiante__nombre')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AsistenciaApoderado)
class AsistenciaApoderadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'nombre_apoderado', 'fecha', 'numero_reunion')
    list_filter = ('fecha',)
    search_fields = ('estudiante__nombre', 'nombre_apoderado')
    ordering = ('-fecha', 'estudiante__nombre')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'categoria', 'estado', 'responsable', 'is_active')
    list_filter = ('categoria', 'estado', 'is_active', 'fecha_ingreso')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')