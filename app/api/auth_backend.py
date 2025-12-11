from django.contrib.auth.backends import BaseBackend
from rest_framework.authentication import SessionAuthentication
from .models import Usuario


class UsuarioBackend(BaseBackend):
    """
    Backend de autenticación personalizado para el modelo Usuario
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscar usuario por email
            usuario = Usuario.objects.get(email=username, is_active=True)
            
            # Verificar contraseña
            if usuario.check_password(password):
                return usuario
        except Usuario.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id, is_active=True)
        except Usuario.DoesNotExist:
            return None


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication sin verificación CSRF para APIs
    """
    def enforce_csrf(self, request):
        return  # No hacer nada, deshabilitar CSRF
