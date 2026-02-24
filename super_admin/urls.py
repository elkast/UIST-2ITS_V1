from django.urls import path
from . import views

app_name = "super_admin"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("utilisateurs/", views.liste_utilisateurs, name="utilisateurs"),
    path("utilisateurs/nouveau/", views.nouvel_utilisateur, name="nouvel_utilisateur"),
    path("utilisateurs/<int:user_id>/modifier/", views.modifier_utilisateur, name="modifier_utilisateur"),
    path("utilisateurs/<int:user_id>/reinitialiser/", views.reinitialiser_mot_de_passe, name="reinitialiser_mdp"),
    path("utilisateurs/<int:user_id>/desactiver/", views.desactiver_utilisateur, name="desactiver_utilisateur"),
    path("audit/", views.audit, name="audit"),
    path("rapports/", views.rapports, name="rapports"),
]
