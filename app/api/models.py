# Modelos de la aplicación API
from django.db import models


class BaseModel(models.Model):
    """
    Modelo base con campos comunes
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# Ejemplo de modelo para la fundación
class Fundacion(BaseModel):
    """
    Modelo de ejemplo para información de la fundación
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    sitio_web = models.URLField(blank=True)

    class Meta:
        verbose_name = "Fundación"
        verbose_name_plural = "Fundaciones"

    def __str__(self):
        return self.nombre