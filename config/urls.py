"""
Configuration URL principale - UIST-2ITS
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentification + page d'accueil
    path("", include("accounts.urls")),
    # Modules par rôle
    path("super-admin/", include("super_admin.urls")),
    path("directeur/", include("directeur.urls")),
    path("gestion1/", include("gestion1.urls")),
    path("gestion2/", include("gestion2.urls")),
    path("gestion3/", include("gestion3.urls")),
    path("communication/", include("communication.urls")),
    path("etudiant/", include("etudiant.urls")),
    path("enseignant/", include("enseignant.urls")),
    path("parent/", include("parent.urls")),
    # API (JSON)
    path("api/", include("accounts.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
