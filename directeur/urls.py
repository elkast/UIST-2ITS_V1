from django.urls import path
from . import views

app_name = "directeur"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    # Validation notes
    path("notes/validation/", views.validation_notes, name="validation_notes"),
    path("notes/valider/", views.valider_notes_masse, name="valider_notes_masse"),
    # EDT - CRUD complet
    path("edt/", views.emploi_temps, name="edt"),
    path("edt/nouveau/", views.nouveau_creneau, name="nouveau_creneau"),
    path("edt/<int:creneau_id>/modifier/", views.modifier_creneau, name="modifier_creneau"),
    path("edt/<int:creneau_id>/supprimer/", views.supprimer_creneau, name="supprimer_creneau"),
    path("edt/generer/", views.generer_edt, name="generer_edt"),
    # Disponibilités
    path("disponibilites/", views.disponibilites_enseignants, name="disponibilites"),
    # Rapports
    path("rapports/", views.rapports, name="rapports"),
    # Utilisateurs
    path("utilisateurs/", views.liste_utilisateurs, name="utilisateurs"),
    path("utilisateurs/<int:user_id>/reinitialiser/", views.reinitialiser_mdp_directeur, name="reinitialiser_mdp"),
]
