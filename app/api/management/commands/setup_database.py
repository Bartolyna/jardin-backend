"""
Comando de gestión para inicializar la base de datos del Jardín Infantil Tricahue.

Este comando:
1. Aplica todas las migraciones pendientes
2. Carga los datos iniciales (fixtures)
3. Crea las relaciones jornada-salon necesarias
4. Valida la integridad de los datos
5. Proporciona un reporte de la configuración final
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction
from django.utils import timezone
from api.models import (
    Rol, Jornada, Salon, EstadoAsistencia, EstadoInventario, Categoria,
    JornadaSalon, Usuario
)


class Command(BaseCommand):
    help = 'Inicializa la base de datos con migraciones, datos iniciales y configuración base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los datos existentes antes de inicializar (¡CUIDADO!)',
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Crea un usuario administrador de ejemplo',
        )
        parser.add_argument(
            '--skip-fixtures',
            action='store_true',
            help='Omite la carga de datos iniciales',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando configuración de base de datos...'))
        
        try:
            # Paso 1: Aplicar migraciones
            self._apply_migrations()
            
            # Paso 2: Resetear datos si se solicita
            if options['reset']:
                self._reset_data()
            
            # Paso 3: Cargar datos iniciales
            if not options['skip_fixtures']:
                self._load_initial_data()
            
            # Paso 4: Crear relaciones jornada-salon
            self._create_jornada_salon_relations()
            
            # Paso 5: Crear usuario admin si se solicita
            if options['create_admin']:
                self._create_admin_user()
            
            # Paso 6: Validar configuración
            self._validate_setup()
            
            # Paso 7: Mostrar resumen
            self._show_summary()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la configuración: {e}')
            )
            raise CommandError(f'La configuración falló: {e}')

    def _apply_migrations(self):
        """Aplica todas las migraciones pendientes."""
        self.stdout.write('📦 Aplicando migraciones...')
        try:
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  ✅ Migraciones aplicadas correctamente'))
        except Exception as e:
            raise CommandError(f'Error aplicando migraciones: {e}')

    def _reset_data(self):
        """Elimina todos los datos existentes."""
        self.stdout.write(self.style.WARNING('⚠️  Eliminando datos existentes...'))
        
        # Eliminar en orden inverso por dependencias
        models_to_clear = [
            Usuario, JornadaSalon, Categoria, EstadoInventario, 
            EstadoAsistencia, Salon, Jornada, Rol
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'  🗑️  Eliminados {count} registros de {model._meta.verbose_name_plural}')

    def _load_initial_data(self):
        """Carga los datos iniciales desde fixtures."""
        self.stdout.write('📋 Cargando datos iniciales...')
        try:
            call_command('loaddata', 'initial_data.json', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  ✅ Datos iniciales cargados correctamente'))
        except Exception as e:
            raise CommandError(f'Error cargando datos iniciales: {e}')

    def _create_jornada_salon_relations(self):
        """Crea las relaciones entre jornadas y salones."""
        self.stdout.write('🔗 Creando relaciones jornada-salón...')
        
        try:
            # Obtener todas las jornadas y salones activos
            jornadas = Jornada.objects.filter(is_active=True)
            salones = Salon.objects.filter(is_active=True)
            
            created_count = 0
            existing_count = 0
            
            for jornada in jornadas:
                for salon in salones:
                    jornada_salon, created = JornadaSalon.objects.get_or_create(
                        jornada=jornada,
                        salon=salon,
                        defaults={'is_active': True}
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            f'  ✨ Creada: {jornada.get_nombre_display()} - {salon.get_nombre_display()}'
                        )
                    else:
                        existing_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✅ Relaciones procesadas: {created_count} creadas, {existing_count} existentes'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Error creando relaciones jornada-salón: {e}')

    def _create_admin_user(self):
        """Crea un usuario administrador de ejemplo."""
        self.stdout.write('👤 Creando usuario administrador...')
        
        try:
            admin_rol = Rol.objects.get(nombre=Rol.ADMINISTRADOR)
            
            admin_user, created = Usuario.objects.get_or_create(
                email='admin@jardintricahue.cl',
                defaults={
                    'nombre': 'Administrador del Sistema',
                    'rol': admin_rol,
                    'contraseña': 'admin123',  # Se encriptará automáticamente
                    'telefono': '+56912345678',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Usuario administrador creado')
                )
                self.stdout.write('     📧 Email: admin@jardintricahue.cl')
                self.stdout.write('     🔐 Contraseña: admin123')
                self.stdout.write(
                    self.style.WARNING('     ⚠️  Recuerda cambiar la contraseña en producción!')
                )
            else:
                self.stdout.write('  ℹ️  El usuario administrador ya existe')
                
        except Rol.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('  ❌ No se encontró el rol de administrador')
            )
        except Exception as e:
            raise CommandError(f'Error creando usuario administrador: {e}')

    def _validate_setup(self):
        """Valida que la configuración se haya completado correctamente."""
        self.stdout.write('🔍 Validando configuración...')
        
        validations = [
            (Rol, 3, 'roles'),
            (Jornada, 2, 'jornadas'),
            (Salon, 4, 'salones'),
            (EstadoAsistencia, 4, 'estados de asistencia'),
            (EstadoInventario, 5, 'estados de inventario'),
            (Categoria, 6, 'categorías'),
        ]
        
        for model, expected_count, name in validations:
            actual_count = model.objects.filter(is_active=True).count()
            if actual_count >= expected_count:
                self.stdout.write(f'  ✅ {name.capitalize()}: {actual_count} registros')
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠️  {name.capitalize()}: {actual_count}/{expected_count} registros'
                    )
                )
        
        # Validar relaciones jornada-salon
        js_count = JornadaSalon.objects.filter(is_active=True).count()
        expected_js = Jornada.objects.filter(is_active=True).count() * Salon.objects.filter(is_active=True).count()
        
        if js_count >= expected_js:
            self.stdout.write(f'  ✅ Relaciones jornada-salón: {js_count} registros')
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠️  Relaciones jornada-salón: {js_count}/{expected_js} registros'
                )
            )

    def _show_summary(self):
        """Muestra un resumen de la configuración completada."""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 ¡Configuración completada exitosamente!'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE LA CONFIGURACIÓN:'))
        self.stdout.write('')
        
        # Mostrar estadísticas por modelo
        models_info = [
            ('👥 Roles', Rol),
            ('⏰ Jornadas', Jornada),
            ('🏫 Salones', Salon),
            ('📋 Estados de Asistencia', EstadoAsistencia),
            ('📦 Estados de Inventario', EstadoInventario),
            ('🏷️  Categorías', Categoria),
            ('🔗 Relaciones Jornada-Salón', JornadaSalon),
            ('👤 Usuarios', Usuario),
        ]
        
        for label, model in models_info:
            active_count = model.objects.filter(is_active=True).count()
            total_count = model.objects.count()
            if active_count == total_count:
                self.stdout.write(f'   {label}: {active_count} registros')
            else:
                self.stdout.write(f'   {label}: {active_count}/{total_count} registros activos')
        
        self.stdout.write('')
        self.stdout.write('🚀 PRÓXIMOS PASOS:')
        self.stdout.write('   1. Ejecuta: python manage.py runserver')
        self.stdout.write('   2. Visita: http://localhost:8000/admin/')
        self.stdout.write('   3. Comienza a registrar estudiantes y asistencia')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✨ ¡El sistema está listo para usar!'))