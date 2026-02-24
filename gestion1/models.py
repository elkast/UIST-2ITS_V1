"""
Modèles Gestion 1 - Logistique & Infrastructure.
Filières, Salles, Cours.
"""

from django.db import models


class Filiere(models.Model):
    """Table filières - Programmes académiques"""

    NIVEAU_CHOICES = [
        ("L1", "Licence 1"),
        ("L2", "Licence 2"),
        ("L3", "Licence 3"),
        ("M1", "Master 1"),
        ("M2", "Master 2"),
    ]

    code_filiere = models.CharField(max_length=20, unique=True, db_index=True)
    nom_filiere = models.CharField(max_length=150)
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES)
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "filieres"
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ["niveau", "nom_filiere"]

    def __str__(self):
        return f"{self.code_filiere} - {self.nom_filiere} ({self.niveau})"


class Salle(models.Model):
    """
    Table salles - Salles de cours avec suivi d'équipements.
    Les équipements ne peuvent être modifiés sans accord du directeur (verrouille=True).
    """

    nom_salle = models.CharField(max_length=50, unique=True)
    capacite = models.IntegerField(default=30)
    batiment = models.CharField(max_length=100, blank=True, default="")
    nb_projecteurs = models.IntegerField("Nombre de projecteurs", default=0)
    nb_rallonges = models.IntegerField("Nombre de rallonges", default=0)
    nb_ordinateurs = models.IntegerField("Nombre d'ordinateurs", default=0)
    nb_chargeurs = models.IntegerField("Nombre de chargeurs", default=0)
    nb_adaptateurs = models.IntegerField("Nombre d'adaptateurs", default=0)
    verrouille = models.BooleanField(
        "Verrouillé (modification nécessite accord directeur)", default=False
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "salles"
        verbose_name = "Salle"
        verbose_name_plural = "Salles"
        ordering = ["nom_salle"]

    def __str__(self):
        return f"{self.nom_salle} ({self.capacite} places)"

    @property
    def total_equipements(self):
        return (
            self.nb_projecteurs
            + self.nb_rallonges
            + self.nb_ordinateurs
            + self.nb_chargeurs
            + self.nb_adaptateurs
        )


class Cours(models.Model):
    """Table cours - Unités d'enseignement"""

    STATUT_CHOICES = [
        ("Actif", "Actif"),
        ("Inactif", "Inactif"),
        ("Suspendu", "Suspendu"),
    ]

    code_cours = models.CharField(max_length=20, unique=True, db_index=True)
    libelle = models.CharField(max_length=200)
    credit = models.IntegerField(default=3)
    volume_horaire = models.IntegerField("Volume horaire (heures)", default=0)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name="cours")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="Actif")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cours"
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ["code_cours"]

    def __str__(self):
        return f"{self.code_cours} - {self.libelle}"

    @property
    def est_actif(self):
        return self.statut == "Actif"


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

NIVEAUX_VALIDES = ["L1", "L2", "L3", "M1", "M2"]


def lister_filieres_actives():
    return Filiere.objects.filter(est_active=True).order_by("niveau", "nom_filiere")


def lister_filieres_par_niveau(niveau):
    return Filiere.objects.filter(niveau=niveau, est_active=True)


def lister_cours_par_filiere(filiere_id):
    return Cours.objects.filter(filiere_id=filiere_id, statut="Actif").order_by(
        "libelle"
    )


def lister_tous_cours_actifs():
    return (
        Cours.objects.filter(statut="Actif")
        .select_related("filiere")
        .order_by("code_cours")
    )


def lister_salles():
    return Salle.objects.all().order_by("nom_salle")


# ============================================================
# FEEDBACK / ÉVALUATION UI/UX
# ============================================================


class Feedback(models.Model):
    """Table feedback - Évaluation UI/UX de l'application"""

    NOTE_CHOICES = [
        (1, "1 ★ - Très mécontent"),
        (2, "2 ★ - Mécontent"),
        (3, "3 ★ - Neutre"),
        (4, "4 ★ - Satisfait"),
        (5, "5 ★ - Très satisfait"),
    ]

    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField("Commentaire (optionnel)", blank=True, default="")
    email = models.EmailField("Email (optionnel)", blank=True, default="")
    date_creation = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False)

    class Meta:
        db_table = "feedbacks"
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Feedback {self.note}★ - {self.date_creation.strftime('%d/%m/%Y')}"

    @property
    def note_stars(self):
        return "★" * self.note + "☆" * (5 - self.note)
