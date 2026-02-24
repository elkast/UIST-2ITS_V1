"""
Modèles Gestion 3 - Suivi & Contrôle (Présences).
"""

from django.db import models
from etudiant.models import Etudiant


class Presence(models.Model):
    """Table présences - Pointage des présences"""

    STATUT_CHOICES = [
        ("Present", "Présent"),
        ("Absent", "Absent"),
        ("Retard", "Retard"),
        ("Excuse", "Excusé"),
    ]

    creneau = models.ForeignKey(
        "directeur.EmploiDuTemps", on_delete=models.CASCADE, related_name="presences"
    )
    etudiant = models.ForeignKey(
        Etudiant, on_delete=models.CASCADE, related_name="presences"
    )
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    date_pointage = models.DateField()
    commentaire = models.TextField(blank=True, default="")

    class Meta:
        db_table = "presences"
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        unique_together = ["creneau", "etudiant", "date_pointage"]

    def __str__(self):
        return f"{self.statut} - {self.etudiant}"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================


def calculer_taux_presence(etudiant_pk):
    """Calcule le taux de présence d'un étudiant"""
    total = Presence.objects.filter(etudiant_id=etudiant_pk).count()
    if total == 0:
        return {"taux": 0, "presents": 0, "absents": 0, "total": 0}

    presents = Presence.objects.filter(etudiant_id=etudiant_pk, statut="Present").count()
    absents = Presence.objects.filter(etudiant_id=etudiant_pk, statut="Absent").count()
    taux = round((presents / total) * 100, 2)

    return {"taux": taux, "presents": presents, "absents": absents, "total": total}


def lister_absences_etudiant(etudiant_pk):
    """Liste détaillée des absences d'un étudiant"""
    return Presence.objects.filter(
        etudiant_id=etudiant_pk, statut="Absent"
    ).select_related("creneau__cours", "creneau__enseignant__id_user").order_by("-date_pointage")


def detecter_absences_critiques(seuil=75):
    """Détecte les étudiants avec taux de présence < seuil"""
    alertes = []
    etudiants = Etudiant.objects.select_related("id_user", "filiere").all()

    for etudiant in etudiants:
        taux = calculer_taux_presence(etudiant.pk)
        if taux["total"] > 0 and taux["taux"] < seuil:
            # Récupérer contacts parents
            from parent.models import LiaisonParentEtudiant
            liaisons = LiaisonParentEtudiant.objects.filter(
                etudiant=etudiant
            ).select_related("parent__id_user")

            contacts_parents = [
                {
                    "nom": l.parent.id_user.nom_complet,
                    "telephone": l.parent.telephone,
                    "lien": l.lien_parente,
                }
                for l in liaisons
            ]

            alertes.append({
                "etudiant": etudiant,
                "matricule": etudiant.id_user.matricule,
                "nom": etudiant.id_user.nom,
                "prenom": etudiant.id_user.prenom,
                "filiere": etudiant.filiere.nom_filiere,
                "niveau": etudiant.filiere.niveau,
                "taux": taux["taux"],
                "absences": taux["absents"],
                "total": taux["total"],
                "contacts_parents": contacts_parents,
            })

    alertes.sort(key=lambda x: x["taux"])
    return alertes


def statistiques_presences_filiere(filiere_id):
    """Statistiques de présence par filière"""
    etudiants = Etudiant.objects.filter(filiere_id=filiere_id).select_related("id_user")
    stats = []
    for etudiant in etudiants:
        taux = calculer_taux_presence(etudiant.pk)
        stats.append({
            "etudiant": etudiant,
            "taux": taux["taux"],
            "presents": taux["presents"],
            "absents": taux["absents"],
            "total": taux["total"],
        })
    return stats
