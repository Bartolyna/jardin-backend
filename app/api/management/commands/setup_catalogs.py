from django.core.management.base import BaseCommand
from api.models import Jornada, Salon, JornadaSalon


class Command(BaseCommand):
    help = 'Actualiza jornadas, salones y sus relaciones'

    def handle(self, *args, **kwargs):
        # 1. Actualizar Jornadas
        self.stdout.write(self.style.WARNING('\n=== JORNADAS ==='))
        jornadas_data = [
            (1, 'Mañana', '08:00:00', '13:00:00'),
            (2, 'Tarde', '14:00:00', '19:00:00'),
        ]

        for pk, nombre, hora_inicio, hora_fin in jornadas_data:
            jornada, created = Jornada.objects.update_or_create(
                id=pk,
                defaults={
                    'nombre': nombre,
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'is_active': True
                }
            )
            action = 'Creada' if created else 'Actualizada'
            self.stdout.write(
                self.style.SUCCESS(f'✓ {action}: {jornada.nombre} ({hora_inicio}-{hora_fin})')
            )

        # 2. Actualizar Salones
        self.stdout.write(self.style.WARNING('\n=== SALONES ==='))
        salones_data = [
            (1, 'Medio Menor 1', 20),
            (2, 'Medio Menor 2', 20),
            (3, 'Medio y transición 3', 25),
            (4, 'Medio y transición 4', 25),
            (5, 'Transición 5', 30),
            (6, 'Transición 6', 30),
        ]

        for pk, nombre, capacidad in salones_data:
            salon, created = Salon.objects.update_or_create(
                id=pk,
                defaults={'nombre': nombre, 'capacidad': capacidad, 'is_active': True}
            )
            action = 'Creado' if created else 'Actualizado'
            self.stdout.write(
                self.style.SUCCESS(f'✓ {action}: {salon.nombre} (capacidad: {salon.capacidad})')
            )

        # 3. Crear relaciones JornadaSalon (todas las combinaciones)
        self.stdout.write(self.style.WARNING('\n=== JORNADAS-SALONES ==='))
        contador = 0
        for jornada_id, _, _, _ in jornadas_data:
            for salon_id, _, _ in salones_data:
                jornada = Jornada.objects.get(id=jornada_id)
                salon = Salon.objects.get(id=salon_id)
                
                js, created = JornadaSalon.objects.get_or_create(
                    jornada=jornada,
                    salon=salon,
                    defaults={'is_active': True}
                )
                
                if created:
                    contador += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Creado: {jornada.nombre} - {salon.nombre}')
                    )

        if contador == 0:
            self.stdout.write(self.style.SUCCESS('Todas las relaciones ya existían'))
        
        total_jornadas_salones = JornadaSalon.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total de combinaciones activas: {total_jornadas_salones}')
        )
