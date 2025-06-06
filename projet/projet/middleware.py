import logging

logger = logging.getLogger('scrap_emploi')

class DebugRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log détaillé de chaque requête
        logger.debug(f"[MIDDLEWARE] Requête reçue : {request.method} {request.path}")
        logger.debug(f"[MIDDLEWARE] Paramètres GET : {request.GET}")
        logger.debug(f"[MIDDLEWARE] En-têtes : {dict(request.headers)}")

        response = self.get_response(request)

        # Log de la réponse
        logger.debug(f"[MIDDLEWARE] Statut de réponse : {response.status_code}")
        
        return response 