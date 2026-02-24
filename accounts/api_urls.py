"""
URLs API REST pour consommation mobile.
"""
from django.urls import path
from . import api_views

app_name = "api"

urlpatterns = [
    path("edt/<int:filiere_id>/", api_views.api_edt_filiere, name="edt_filiere"),
    path("notes/<int:etudiant_id>/", api_views.api_notes_etudiant, name="notes_etudiant"),
    path("presences/<int:etudiant_id>/", api_views.api_presences_etudiant, name="presences_etudiant"),
    path("notifications/", api_views.api_notifications, name="notifications"),
    path("filieres/", api_views.api_filieres, name="filieres"),
    path("parents/recherche/", api_views.api_recherche_parents, name="recherche_parents"),
]
