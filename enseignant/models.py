"""
Modèles Enseignant - Profils, disponibilités, assignations cours.
"""

from django.db import models
from accounts.models import Utilisateur


class Enseignant(models.Model):
    """Table enseignants - Profils enseignants"""

    id_user = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="enseignant_profile",
    )
    specialite = models.CharField(max_length=150, blank=True, default="")
    telephone = models.CharField(max_length=20, blank=True, default="")
    date_recrutement = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "enseignants"
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"

    def __str__(self):
        return f"{self.id_user.nom} {self.id_user.prenom}"


class DisponibiliteEnseignant(models.Model):
    """Table disponibilités - Créneaux de disponibilité des enseignants"""

    JOUR_CHOICES = [
        ("Lundi", "Lundi"),
        ("Mardi", "Mardi"),
        ("Mercredi", "Mercredi"),
        ("Jeudi", "Jeudi"),
        ("Vendredi", "Vendredi"),
        ("Samedi", "Samedi"),
    ]

    enseignant = models.ForeignKey(
        Enseignant, on_delete=models.CASCADE, related_name="disponibilites"
    )
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    est_disponible = models.BooleanField(default=True)

    class Meta:
        db_table = "disponibilites_enseignants"
        verbose_name = "Disponibilité"
        verbose_name_plural = "Disponibilités"
        ordering = ["jour", "heure_debut"]

    def __str__(self):
        statut = "Disponible" if self.est_disponible else "Indisponible"
        return f"{self.jour} {self.heure_debut}-{self.heure_fin} ({statut})"


class EnseignantCours(models.Model):
    """Association enseignant ↔ cours (assignation)"""

    enseignant = models.ForeignKey(
        Enseignant, on_delete=models.CASCADE, related_name="cours_assignes"
    )
    cours = models.ForeignKey(
        "gestion1.Cours", on_delete=models.CASCADE, related_name="enseignants_assignes"
    )
    date_assignation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "enseignant_cours"
        unique_together = ["enseignant", "cours"]
        verbose_name = "Assignation Enseignant-Cours"

    def __str__(self):
        return f"{self.enseignant} → {self.cours}"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]


def obtenir_enseignant_par_user(user_id):
    try:
        return Enseignant.objects.select_related("id_user").get(id_user_id=user_id)
    except Enseignant.DoesNotExist:
        return None


def lister_tous_enseignants():
    return Enseignant.objects.select_related("id_user").all()


def obtenir_disponibilites(enseignant_pk):
    return DisponibiliteEnseignant.objects.filter(
        enseignant_id=enseignant_pk
    ).order_by("jour", "heure_debut")


def lister_cours_enseignant(enseignant_pk):
    """Liste les cours assignés à un enseignant"""
    return EnseignantCours.objects.filter(
        enseignant_id=enseignant_pk
    ).select_related("cours", "cours__filiere")
