"""
Modèles Super Admin - Audit et configuration système.
"""

from django.db import models
from datetime import datetime


class AuditLog(models.Model):
    """Journal d'audit des actions utilisateurs"""

    ACTION_CHOICES = [
        ("CONNEXION", "Connexion"),
        ("DECONNEXION", "Déconnexion"),
        ("CREATION_USER", "Création utilisateur"),
        ("MODIFICATION_USER", "Modification utilisateur"),
        ("SUPPRESSION_USER", "Suppression utilisateur"),
        ("VALIDATION_NOTE", "Validation note"),
        ("CREATION_EDT", "Création EDT"),
        ("MODIFICATION_EDT", "Modification EDT"),
        ("IMPORT_NOTES", "Import notes"),
        ("EXPORT", "Export rapport"),
        ("MODIFICATION", "Modification"),
    ]

    id_user = models.IntegerField("ID Utilisateur")
    nom_utilisateur = models.CharField(max_length=100, default="")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    table_affectee = models.CharField(max_length=50, blank=True, default="")
    id_enregistrement = models.IntegerField(null=True, blank=True)
    details = models.TextField(blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        verbose_name = "Log d'Audit"
        verbose_name_plural = "Logs d'Audit"
        ordering = ["-date_action"]

    def __str__(self):
        return f"{self.action} - {self.nom_utilisateur} ({self.date_action})"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================


def creer_log_audit(request, action, table="", id_enreg=None, details=""):
    """Crée un log d'audit à partir de la requête"""
    user = request.user if request.user.is_authenticated else None
    ip = request.META.get("REMOTE_ADDR", "")

    return AuditLog.objects.create(
        id_user=user.pk if user else 0,
        nom_utilisateur=user.nom_complet if user else "Anonyme",
        action=action,
        table_affectee=table,
        id_enregistrement=id_enreg,
        details=details,
        ip_address=ip,
    )


def statistiques_audit():
    """Statistiques globales d'audit"""
    total = AuditLog.objects.count()
    aujourdhui = AuditLog.objects.filter(
        date_action__date=datetime.now().date()
    ).count()
    return {"total": total, "aujourdhui": aujourdhui}
