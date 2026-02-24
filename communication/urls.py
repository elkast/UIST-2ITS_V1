"""
URLs Communication - Routes pour la gestion des événements et publications.
"""

from django.urls import path
from . import views

app_name = "communication"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # Événements
    path("evenements/", views.liste_evenements, name="liste_evenements"),
    path("evenements/creer/", views.creer_evenement, name="creer_evenement"),
    path(
        "evenements/<int:pk>/modifier/",
        views.modifier_evenement,
        name="modifier_evenement",
    ),
    path(
        "evenements/<int:pk>/supprimer/",
        views.supprimer_evenement,
        name="supprimer_evenement",
    ),
    path(
        "evenements/<int:pk>/toggle/",
        views.toggle_publication_evenement,
        name="toggle_evenement",
    ),
    # Publications
    path("publications/", views.liste_publications, name="liste_publications"),
    path("publications/creer/", views.creer_publication, name="creer_publication"),
    path(
        "publications/<int:pk>/modifier/",
        views.modifier_publication,
        name="modifier_publication",
    ),
    path(
        "publications/<int:pk>/supprimer/",
        views.supprimer_publication,
        name="supprimer_publication",
    ),
    path(
        "publications/<int:pk>/toggle/",
        views.toggle_publication,
        name="toggle_publication",
    ),
]
