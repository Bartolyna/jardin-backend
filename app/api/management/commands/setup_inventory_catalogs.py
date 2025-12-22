from django.core.management.base import BaseCommand
from api.models import EstadoInventario, Categoria


class Command(BaseCommand):
    help = 'Crea los catálogos iniciales para inventario (estados y categorías)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('\n=== ESTADOS DE INVENTARIO ==='))
        estados_data = [
            (1, 'Disponible'),
            (2, 'En uso'),
            (3, 'En mantenimiento'),
            (4, 'Dado de baja'),
        ]

        for pk, nombre in estados_data:
            estado, created = EstadoInventario.objects.update_or_create(
                id=pk,
                defaults={
                    'nombre': nombre,
                    'is_active': True
                }
            )
            action = 'Creado' if created else 'Actualizado'
            self.stdout.write(
                self.style.SUCCESS(f'✓ {action}: {estado.nombre}')
            )

        self.stdout.write(self.style.WARNING('\n=== CATEGORÍAS ==='))
        categorias_data = [
            (1, 'Alimentos'),
            (2, 'Útiles Escolares'),
            (3, 'Material Didáctico'),
            (4, 'Limpieza'),
            (5, 'Higiene Personal'),
            (6, 'Medicamentos'),
            (7, 'Mobiliario'),
            (8, 'Tecnología'),
            (9, 'Otros'),
        ]

        for pk, nombre in categorias_data:
            categoria, created = Categoria.objects.update_or_create(
                id=pk,
                defaults={'nombre': nombre, 'is_active': True}
            )
            action = 'Creada' if created else 'Actualizada'
            self.stdout.write(
                self.style.SUCCESS(f'✓ {action}: {categoria.nombre}')
            )

        total_estados = EstadoInventario.objects.filter(is_active=True).count()
        total_categorias = Categoria.objects.filter(is_active=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total estados activos: {total_estados}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Total categorías activas: {total_categorias}')
        )
