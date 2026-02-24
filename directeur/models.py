"""
Modèles Directeur - Emploi du temps et validation des notes.
Le directeur gère le CRUD complet de l'EDT et valide les notes.
"""

from django.db import models
from django.utils import timezone


class EmploiDuTemps(models.Model):
    """Table emploi du temps - Planning des cours"""

    JOUR_CHOICES = [
        ("Lundi", "Lundi"),
        ("Mardi", "Mardi"),
        ("Mercredi", "Mercredi"),
        ("Jeudi", "Jeudi"),
        ("Vendredi", "Vendredi"),
        ("Samedi", "Samedi"),
    ]

    TYPE_CRENEAU_CHOICES = [
        ("Cours", "Cours"),
        ("TD", "TD"),
        ("TP", "TP"),
        ("Examen", "Examen"),
    ]

    cours = models.ForeignKey(
        "gestion1.Cours", on_delete=models.CASCADE, related_name="creneaux_edt"
    )
    enseignant = models.ForeignKey(
        "enseignant.Enseignant", on_delete=models.CASCADE, related_name="creneaux_edt"
    )
    salle = models.ForeignKey(
        "gestion1.Salle", on_delete=models.CASCADE, related_name="creneaux_edt"
    )
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    type_creneau = models.CharField(
        max_length=20, choices=TYPE_CRENEAU_CHOICES, default="Cours"
    )
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "emploi_du_temps"
        verbose_name = "Créneau EDT"
        verbose_name_plural = "Emplois du Temps"
        ordering = ["jour", "heure_debut"]

    def __str__(self):
        return f"{self.jour} {self.heure_debut}-{self.heure_fin} | {self.cours}"


class ValidationNote(models.Model):
    """Journal des validations de notes par le directeur"""

    note = models.ForeignKey(
        "gestion2.Note", on_delete=models.CASCADE, related_name="validations"
    )
    validateur = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.CASCADE, related_name="validations_effectuees"
    )
    action = models.CharField(max_length=20, default="Valide")  # Valide ou Rejete
    date_validation = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, default="")

    class Meta:
        db_table = "validation_notes"
        verbose_name = "Validation de Note"
        ordering = ["-date_validation"]

    def __str__(self):
        return f"Validation #{self.pk} par {self.validateur}"


# ============================================================
# FONCTIONS UTILITAIRES - EDT
# ============================================================

JOURS_ORDRE = {
    "Lundi": 0, "Mardi": 1, "Mercredi": 2,
    "Jeudi": 3, "Vendredi": 4, "Samedi": 5,
}

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

HEURES_PLAGE = [
    "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
]


def lister_edt_filiere(filiere_id):
    """Liste l'EDT d'une filière"""
    return EmploiDuTemps.objects.filter(
        cours__filiere_id=filiere_id,
        est_actif=True,
    ).select_related("cours", "enseignant__id_user", "salle").order_by("jour", "heure_debut")


def lister_edt_enseignant(enseignant_pk):
    """Liste l'EDT d'un enseignant"""
    return EmploiDuTemps.objects.filter(
        enseignant_id=enseignant_pk,
        est_actif=True,
    ).select_related("cours", "cours__filiere", "salle").order_by("jour", "heure_debut")


def lister_tout_edt():
    """Liste tout l'EDT actif"""
    return EmploiDuTemps.objects.filter(
        est_actif=True
    ).select_related(
        "cours", "cours__filiere", "enseignant__id_user", "salle"
    ).order_by("jour", "heure_debut")


def heures_se_chevauchent(debut1, fin1, debut2, fin2):
    return not (fin1 <= debut2 or fin2 <= debut1)


def verifier_conflits_edt(cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin, exclure_id=None):
    """Vérifie les conflits d'EDT (RG01)"""
    conflits = []
    query = EmploiDuTemps.objects.filter(jour=jour, est_actif=True)

    if exclure_id:
        query = query.exclude(pk=exclure_id)

    for creneau in query.select_related("cours"):
        if heures_se_chevauchent(heure_debut, heure_fin, creneau.heure_debut, creneau.heure_fin):
            if creneau.enseignant_id == enseignant_id:
                conflits.append("Enseignant déjà occupé à ce créneau")
            if creneau.salle_id == salle_id:
                conflits.append("Salle déjà occupée à ce créneau")
            if creneau.cours.filiere_id == cours_id:
                conflits.append("Filière déjà en cours à ce créneau")

    return conflits


def generer_edt_auto(filiere_id):
    """
    Génère automatiquement un EDT basé sur les disponibilités enseignants.
    Retourne la liste des créneaux créés et les erreurs.
    """
    from gestion1.models import Cours, Salle
    from enseignant.models import EnseignantCours, DisponibiliteEnseignant

    cours_filiere = Cours.objects.filter(filiere_id=filiere_id, statut="Actif")
    salles = list(Salle.objects.all().order_by("-capacite"))
    resultats = {"crees": 0, "erreurs": []}

    for cours in cours_filiere:
        # Trouver les enseignants assignés
        assignations = EnseignantCours.objects.filter(cours=cours)

        if not assignations.exists():
            resultats["erreurs"].append(f"Aucun enseignant assigné pour {cours.libelle}")
            continue

        enseignant = assignations.first().enseignant

        # Trouver une disponibilité
        disponibilites = DisponibiliteEnseignant.objects.filter(
            enseignant=enseignant, est_disponible=True
        ).order_by("jour", "heure_debut")

        place = False
        for dispo in disponibilites:
            for salle in salles:
                conflits = verifier_conflits_edt(
                    cours.pk, enseignant.pk, salle.pk,
                    dispo.jour, dispo.heure_debut, dispo.heure_fin,
                )
                if not conflits:
                    EmploiDuTemps.objects.create(
                        cours=cours,
                        enseignant=enseignant,
                        salle=salle,
                        jour=dispo.jour,
                        heure_debut=dispo.heure_debut,
                        heure_fin=dispo.heure_fin,
                    )
                    resultats["crees"] += 1
                    place = True
                    break
            if place:
                break

        if not place:
            resultats["erreurs"].append(
                f"Impossible de placer {cours.libelle} (pas de créneau libre)"
            )

    return resultats
