from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse


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