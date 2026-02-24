"""
Modèles Communication - Événements, Publications, Vidéos.
"""

from django.db import models
from django.conf import settings


class Evenement(models.Model):
    """Table événements - Publications d'événements sur le site"""

    TYPE_CHOICES = [
        ("EVENEMENT", "Événement"),
        ("VIDEO", "Vidéo"),
        ("ANNONCE", "Annonce"),
        ("ACTUALITE", "Actualité"),
        ("ALERTE", "Alerte"),
    ]

    titre = models.CharField("Titre", max_length=200)
    description = models.TextField("Description")
    type_evenement = models.CharField(
        "Type", max_length=20, choices=TYPE_CHOICES, default="EVENEMENT"
    )

    # Pour les vidéos
    url_video = models.URLField("URL Vidéo (YouTube, Vimeo...)", blank=True, default="")

    # Pour les événements avec date
    date_evenement = models.DateTimeField("Date de l'événement", blank=True, null=True)
    lieu = models.CharField("Lieu", max_length=200, blank=True, default="")

    # Image de couverture
    image = models.ImageField(
        "Image de couverture", upload_to="evenements/", blank=True, null=True
    )

    # Statut de publication
    est_publie = models.BooleanField("Publié", default=False)
    est_urgent = models.BooleanField("Urgent", default=False)

    # Relations
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="evenements_crees",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evenements"
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.titre} ({self.get_type_evenement_display()})"

    @property
    def est_video(self):
        return self.type_evenement == "VIDEO" and self.url_video


class Publication(models.Model):
    """Table publications - Actualités et articles"""

    titre = models.CharField("Titre", max_length=200)
    contenu = models.TextField("Contenu")
    image = models.ImageField("Image", upload_to="publications/", blank=True, null=True)

    est_publie = models.BooleanField("Publié", default=False)
    est_accueil = models.BooleanField("Afficher sur la page d'accueil", default=False)

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="publications_creees",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "publications"
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        ordering = ["-date_creation"]

    def __str__(self):
        return self.titre
