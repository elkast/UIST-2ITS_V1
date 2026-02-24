"""
Template tags pour la section Communication sur la landing page.
"""

from django import template
from communication.models import Evenement, Publication

register = template.Library()


@register.simple_tag
def get_published_evenements(limit=6):
    """Retourne les événements publiés"""
    return list(
        Evenement.objects.filter(est_publie=True).order_by("-date_creation")[:limit]
    )


@register.simple_tag
def get_publications_accueil(limit=6):
    """Retourne les publications affichées sur la page d'accueil"""
    return list(
        Publication.objects.filter(est_publie=True, est_accueil=True).order_by(
            "-date_creation"
        )[:limit]
    )


@register.simple_tag
def get_all_published_content(limit=9):
    """Retourne tout le contenu publié (événements + publications accueil) trié par date"""
    evenements = list(Evenement.objects.filter(est_publie=True))
    publications = list(Publication.objects.filter(est_publie=True, est_accueil=True))

    # Combiner et trier par date
    all_content = evenements + publications
    all_content.sort(key=lambda x: x.date_creation, reverse=True)

    return all_content[:limit]
