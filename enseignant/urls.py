from django.urls import path
from . import views

app_name = "enseignant"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("edt/", views.emploi_temps, name="edt"),
    path("disponibilites/", views.disponibilites, name="disponibilites"),
    path("disponibilites/<int:dispo_id>/supprimer/", views.supprimer_disponibilite, name="supprimer_dispo"),
    path("notes/", views.voir_notes, name="notes"),
]
