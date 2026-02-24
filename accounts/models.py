"""
Modèle Utilisateur personnalisé et Notifications.
Source unique d'authentification pour tout le système.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
import string
from datetime import datetime


class Utilisateur(AbstractUser):
    """Table utilisateurs - Authentification et rôles"""

    ROLE_CHOICES = [
        ("SUPER_ADMIN", "Super Administrateur"),
        ("DIRECTEUR", "Directeur"),
        ("GESTION_1", "Gestion 1 - Logistique"),
        ("GESTION_2", "Gestion 2 - Scolarité"),
        ("GESTION_3", "Gestion 3 - Suivi"),
        ("COMMUNICATION", "Communication - Publications"),
        ("ENSEIGNANT", "Enseignant"),
        ("ETUDIANT", "Étudiant"),
        ("PARENT", "Parent"),
    ]

    matricule = models.CharField(max_length=30, unique=True, db_index=True)
    nom = models.CharField("Nom de famille", max_length=100, default="")
    prenom = models.CharField("Prénom", max_length=100, default="")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "matricule"
    REQUIRED_FIELDS = ["nom", "prenom", "role"]

    class Meta:
        db_table = "utilisateurs"
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def est_admin(self):
        return self.role in ("SUPER_ADMIN", "DIRECTEUR")

    @property
    def est_gestionnaire(self):
        return self.role in ("GESTION_1", "GESTION_2", "GESTION_3")


class Notification(models.Model):
    """Notifications internes du système"""

    TYPE_CHOICES = [
        ("VALIDATION_NOTE", "Validation de note"),
        ("MODIFICATION_EDT", "Modification EDT"),
        ("ALERTE_ABSENCE", "Alerte absence"),
        ("SYSTEME", "Système"),
    ]

    destinataire = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name="notifications"
    )
    type_notif = models.CharField(max_length=30, choices=TYPE_CHOICES, default="SYSTEME")
    titre = models.CharField(max_length=200)
    message = models.TextField()
    est_lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"[{self.type_notif}] {self.titre}"


# ============================================================
# CONSTANTES
# ============================================================

ROLES_VALIDES = [r[0] for r in Utilisateur.ROLE_CHOICES]

HIERARCHIE_ROLES = {
    "SUPER_ADMIN": 5,
    "DIRECTEUR": 4,
    "GESTION_1": 3,
    "GESTION_2": 3,
    "GESTION_3": 3,
    "COMMUNICATION": 3,
    "ENSEIGNANT": 2,
    "ETUDIANT": 1,
    "PARENT": 1,
}


def obtenir_niveau_role(role):
    """Retourne le niveau hiérarchique d'un rôle"""
    return HIERARCHIE_ROLES.get(role, 0)


def peut_gerer_role(role_acteur, role_cible):
    """Vérifie si un acteur peut gérer un rôle cible"""
    return obtenir_niveau_role(role_acteur) > obtenir_niveau_role(role_cible)


def generer_matricule(role):
    """
    Génère un matricule sécurisé et non devinable.
    Format: PREFIX-ANNEE-XXXX (X = alphanumérique aléatoire)
    """
    prefixes = {
        "SUPER_ADMIN": "SA",
        "DIRECTEUR": "DIR",
        "GESTION_1": "G1",
        "GESTION_2": "G2",
        "GESTION_3": "G3",
        "COMMUNICATION": "COM",
        "ENSEIGNANT": "ENS",
        "ETUDIANT": "ETU",
        "PARENT": "PAR",
    }
    prefix = prefixes.get(role, "USR")
    annee = datetime.now().year
    # 4 caractères alphanumériques aléatoires (non devinable)
    charset = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(charset) for _ in range(4))
    matricule = f"{prefix}-{annee}-{suffix}"

    # Vérifier l'unicité
    while Utilisateur.objects.filter(matricule=matricule).exists():
        suffix = "".join(secrets.choice(charset) for _ in range(4))
        matricule = f"{prefix}-{annee}-{suffix}"

    return matricule


def generer_mot_de_passe(longueur=8):
    """Génère un mot de passe aléatoire lisible"""
    charset = string.ascii_letters + string.digits
    return "".join(secrets.choice(charset) for _ in range(longueur))


def creer_notification(destinataire_id, type_notif, titre, message):
    """Crée une notification pour un utilisateur"""
    return Notification.objects.create(
        destinataire_id=destinataire_id,
        type_notif=type_notif,
        titre=titre,
        message=message,
    )
