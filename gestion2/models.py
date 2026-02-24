"""
Modèles Gestion 2 - Scolarité & Évaluations.
Notes, Bulletins.
"""

from django.db import models
from etudiant.models import Etudiant
from gestion1.models import Cours
from accounts.models import Utilisateur


class Note(models.Model):
    """Table notes - Évaluations des étudiants"""

    STATUT_CHOICES = [
        ("En attente", "En attente"),
        ("Valide", "Validé"),
        ("Rejete", "Rejeté"),
    ]

    TYPE_EVALUATION_CHOICES = [
        ("Examen", "Examen"),
        ("Controle", "Contrôle"),
        ("TP", "TP"),
        ("TD", "TD"),
        ("Projet", "Projet"),
        ("Devoir", "Devoir"),
    ]

    id_etudiant = models.ForeignKey(
        Etudiant, on_delete=models.CASCADE, related_name="notes"
    )
    id_cours = models.ForeignKey(
        Cours, on_delete=models.CASCADE, related_name="notes"
    )
    valeur_note = models.FloatField()
    type_evaluation = models.CharField(
        max_length=20, choices=TYPE_EVALUATION_CHOICES, default="Examen"
    )
    statut_validation = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="En attente", db_index=True
    )
    id_validateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="notes_validees",
    )
    date_saisie = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True, default="")

    class Meta:
        db_table = "notes"
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-date_saisie"]

    def __str__(self):
        return f"{self.valeur_note}/20 - {self.id_etudiant}"


class Bulletin(models.Model):
    """Table bulletins"""

    SEMESTRE_CHOICES = [
        ("S1", "Semestre 1"),
        ("S2", "Semestre 2"),
    ]

    id_etudiant = models.ForeignKey(
        Etudiant, on_delete=models.CASCADE, related_name="bulletins"
    )
    annee_academique = models.CharField(max_length=20)
    semestre = models.CharField(max_length=10, choices=SEMESTRE_CHOICES)
    moyenne_generale = models.FloatField(null=True, blank=True)
    rang = models.IntegerField(null=True, blank=True)
    total_credits = models.IntegerField(null=True, blank=True)
    chemin_pdf = models.CharField(max_length=255, blank=True, default="")
    date_generation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bulletins"
        verbose_name = "Bulletin"
        ordering = ["-annee_academique", "-semestre"]

    def __str__(self):
        return f"Bulletin {self.annee_academique} {self.semestre}"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

TYPES_EVALUATION = ["Examen", "Controle", "TP", "TD", "Projet", "Devoir"]


def lister_notes_en_attente():
    return Note.objects.filter(
        statut_validation="En attente"
    ).select_related(
        "id_etudiant__id_user", "id_cours", "id_cours__filiere"
    ).order_by("-date_saisie")


def lister_notes_etudiant(etudiant_pk, validees_seulement=False):
    query = Note.objects.filter(id_etudiant_id=etudiant_pk).select_related("id_cours")
    if validees_seulement:
        query = query.filter(statut_validation="Valide")
    return query.order_by("-date_saisie")


def calculer_moyenne_etudiant(etudiant_pk):
    """Calcule la moyenne pondérée (notes validées uniquement)"""
    from django.db.models import Sum, F

    result = Note.objects.filter(
        id_etudiant_id=etudiant_pk,
        statut_validation="Valide",
    ).aggregate(
        total_pondere=Sum(F("valeur_note") * F("id_cours__credit")),
        total_credits=Sum("id_cours__credit"),
    )

    if result["total_credits"] and result["total_credits"] > 0:
        return round(result["total_pondere"] / result["total_credits"], 2)
    return None


def calculer_rang_etudiant(etudiant_pk):
    """Calcule le rang d'un étudiant dans sa filière"""
    try:
        etudiant = Etudiant.objects.get(pk=etudiant_pk)
    except Etudiant.DoesNotExist:
        return None

    camarades = Etudiant.objects.filter(filiere=etudiant.filiere)
    moyennes = []

    for c in camarades:
        moy = calculer_moyenne_etudiant(c.pk)
        if moy is not None:
            moyennes.append((c.pk, moy))

    moyennes.sort(key=lambda x: x[1], reverse=True)

    for idx, (pk, moy) in enumerate(moyennes, 1):
        if pk == etudiant_pk:
            return idx
    return None
