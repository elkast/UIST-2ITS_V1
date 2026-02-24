from django.urls import path
from . import views

app_name = "gestion3"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("presences/", views.liste_presences, name="presences"),
    path("presences/<int:creneau_id>/marquer/", views.marquer_presences, name="marquer_presences"),
    path("enseignants/", views.liste_enseignants_filiere, name="enseignants_filiere"),
    path("alertes/", views.alertes, name="alertes"),
]
