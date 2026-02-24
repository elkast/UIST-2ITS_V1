from django.urls import path
from . import views

app_name = "gestion1"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    # Salles
    path("salles/", views.liste_salles, name="salles"),
    path("salles/nouvelle/", views.nouvelle_salle, name="nouvelle_salle"),
    path(
        "salles/<int:salle_id>/modifier/", views.modifier_salle, name="modifier_salle"
    ),
    path(
        "salles/<int:salle_id>/verrouiller/",
        views.verrouiller_salle,
        name="verrouiller_salle",
    ),
    # Filières
    path("filieres/", views.liste_filieres, name="filieres"),
    path("filieres/nouvelle/", views.nouvelle_filiere, name="nouvelle_filiere"),
    path(
        "filieres/<int:filiere_id>/modifier/",
        views.modifier_filiere,
        name="modifier_filiere",
    ),
    # Cours
    path("cours/", views.liste_cours, name="cours"),
    path("cours/nouveau/", views.nouveau_cours, name="nouveau_cours"),
    path("cours/<int:cours_id>/modifier/", views.modifier_cours, name="modifier_cours"),
    # Assignation
    path("assignation/", views.assignation_cours, name="assignation"),
    # Feedback
    path("feedbacks/", views.liste_feedbacks, name="feedbacks"),
    path(
        "feedbacks/<int:feedback_id>/traiter/",
        views.traiter_feedback,
        name="traiter_feedback",
    ),
]
