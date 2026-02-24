"""
Middleware pour forcer HTTP en développement local
"""

from django.http import HttpResponseRedirect


class ForceHTTPMiddleware:
    """
    Middleware qui redirige automatiquement vers HTTP si l'utilisateur accède via HTTPS
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # En développement local, rediriger HTTPS vers HTTP
        if request.is_secure():
            # Construire l'URL HTTP
            host = request.get_host().split(":")[0]  # Enlever le port si présent
            port = ":8000"  # Port par défaut de Django
            path = request.get_full_path()
            http_url = f"http://{host}{port}{path}"
            return HttpResponseRedirect(http_url)

        return self.get_response(request)
