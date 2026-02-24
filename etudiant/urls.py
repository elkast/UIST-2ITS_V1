from django.urls import path
from . import views

app_name = "etudiant"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("edt/", views.emploi_temps, name="edt"),
    path("notes/", views.mes_notes, name="notes"),
    path("profil/", views.profil, name="profil"),
    path("notifications/", views.notifications, name="notifications"),
]
