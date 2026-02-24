"""
Modèle Étudiant - Profil étudiant lié à un utilisateur.
"""

from django.db import models
from accounts.models import Utilisateur


class Etudiant(models.Model):
    """Table étudiants - Profils étudiants"""

    id_user = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="etudiant_profile",
    )
    filiere = models.ForeignKey(
        "gestion1.Filiere", on_delete=models.CASCADE, related_name="etudiants"
    )
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.TextField(blank=True, default="")
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "etudiants"
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

    def __str__(self):
        return f"{self.id_user.nom} {self.id_user.prenom} ({self.id_user.matricule})"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================


def obtenir_etudiant_par_user(user_id):
    try:
        return Etudiant.objects.select_related("id_user", "filiere").get(
            id_user_id=user_id
        )
    except Etudiant.DoesNotExist:
        return None


def obtenir_etudiant_par_matricule(matricule):
    try:
        return Etudiant.objects.select_related("id_user", "filiere").get(
            id_user__matricule=matricule
        )
    except Etudiant.DoesNotExist:
        return None


def lister_etudiants_par_filiere(filiere_id):
    return Etudiant.objects.filter(filiere_id=filiere_id).select_related(
        "id_user", "filiere"
    ).order_by("id_user__nom")


def compter_etudiants_filiere(filiere_id):
    return Etudiant.objects.filter(filiere_id=filiere_id).count()
