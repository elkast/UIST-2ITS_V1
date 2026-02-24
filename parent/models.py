"""
Modèles Parent - Profil parent et liaison avec étudiants.
"""

from django.db import models
from accounts.models import Utilisateur
from etudiant.models import Etudiant


class Parent(models.Model):
    """Table parents - Profils parents"""

    id_user = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="parent_profile",
    )
    telephone = models.CharField(max_length=20, blank=True, default="")
    telephone_secondaire = models.CharField(
        "Deuxième numéro", max_length=20, blank=True, default=""
    )
    profession = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "parents"
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    def __str__(self):
        return f"{self.id_user.nom} {self.id_user.prenom}"


class LiaisonParentEtudiant(models.Model):
    """Table liaison parent-étudiant (relation N:N)"""

    LIEN_CHOICES = [
        ("Père", "Père"),
        ("Mère", "Mère"),
        ("Tuteur", "Tuteur"),
        ("Tutrice", "Tutrice"),
        ("Autre", "Autre"),
    ]

    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name="liaisons"
    )
    etudiant = models.ForeignKey(
        Etudiant, on_delete=models.CASCADE, related_name="liaisons_parent"
    )
    lien_parente = models.CharField(max_length=20, choices=LIEN_CHOICES)
    date_liaison = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "liaison_parent_etudiant"
        unique_together = ["parent", "etudiant"]
        verbose_name = "Liaison Parent-Étudiant"

    def __str__(self):
        return f"{self.parent} → {self.etudiant} ({self.lien_parente})"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================


def obtenir_parent_par_user(user_id):
    try:
        return Parent.objects.select_related("id_user").get(id_user_id=user_id)
    except Parent.DoesNotExist:
        return None


def obtenir_enfants_parent(parent_pk):
    """Liste les étudiants liés à un parent"""
    liaisons = LiaisonParentEtudiant.objects.filter(
        parent_id=parent_pk
    ).select_related("etudiant__id_user", "etudiant__filiere")

    return [
        {
            "etudiant": l.etudiant,
            "user": l.etudiant.id_user,
            "filiere": l.etudiant.filiere,
            "lien": l.lien_parente,
        }
        for l in liaisons
    ]


def verifier_lien_parent_etudiant(parent_pk, etudiant_pk):
    return LiaisonParentEtudiant.objects.filter(
        parent_id=parent_pk, etudiant_id=etudiant_pk
    ).exists()


def rechercher_parents_par_nom(terme):
    """Recherche un parent par nom ou prénom (pour autocomplétion)"""
    from django.db.models import Q
    return Parent.objects.filter(
        Q(id_user__nom__icontains=terme) | Q(id_user__prenom__icontains=terme)
    ).select_related("id_user")[:20]
