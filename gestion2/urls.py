from django.urls import path
from . import views

app_name = "gestion2"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    # Étudiants
    path("etudiants/", views.liste_etudiants, name="etudiants"),
    path("etudiants/nouveau/", views.nouvel_etudiant, name="nouvel_etudiant"),
    path("etudiants/<int:etudiant_id>/modifier/", views.modifier_etudiant, name="modifier_etudiant"),
    # Parents
    path("parents/", views.liste_parents, name="parents"),
    path("parents/nouveau/", views.nouveau_parent, name="nouveau_parent"),
    # Notes
    path("notes/saisie/", views.saisie_notes, name="saisie_notes"),
    path("notes/import/", views.import_notes, name="import_notes"),
    path("notes/valider-notifier/", views.valider_et_notifier, name="valider_notifier"),
    # Liaisons
    path("liaisons/", views.liaisons, name="liaisons"),
    path("liaison-parent/", views.liaison_parent, name="liaison_parent"),
]
