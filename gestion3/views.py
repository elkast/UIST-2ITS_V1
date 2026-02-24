"""
Vues Gestion 3 - Suivi & Contrôle (Présences, Alertes).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from accounts.decorators import role_requis
from accounts.exports import exporter_pdf, exporter_excel
from gestion1.models import lister_filieres_actives


@login_required
@role_requis("GESTION_3", "DIRECTEUR")
def dashboard(request):
    from gestion3.models import detecter_absences_critiques
    from django.conf import settings

    alertes = detecter_absences_critiques(settings.SEUIL_ABSENCE_CRITIQUE)

    return render(request, "gestion3/dashboard.html", {
        "alertes_presences": alertes[:15],
        "total_alertes": len(alertes),
    })


@login_required
@role_requis("GESTION_3", "DIRECTEUR")
def liste_presences(request):
    """Liste de présence par niveau et filière"""
    from directeur.models import lister_edt_filiere
    from etudiant.models import Etudiant

    filiere_id = request.GET.get("filiere_id")
    creneaux = []
    etudiants = []

    if filiere_id:
        creneaux = lister_edt_filiere(int(filiere_id))
        etudiants = Etudiant.objects.filter(
            filiere_id=filiere_id
        ).select_related("id_user").order_by("id_user__nom")

    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel") and filiere_id:
        from gestion3.models import calculer_taux_presence
        colonnes = ["Matricule", "Nom", "Prénom", "Taux (%)", "Présences", "Absences"]
        donnees = []
        for e in etudiants:
            taux = calculer_taux_presence(e.pk)
            donnees.append([e.id_user.matricule, e.id_user.nom, e.id_user.prenom,
                            taux["taux"], taux["presents"], taux["absents"]])
        if format_export == "excel":
            return exporter_excel("Présences par Filière", colonnes, donnees, "presences")
        return exporter_pdf("Présences par Filière", colonnes, donnees, "presences")

    return render(request, "gestion3/presences.html", {
        "creneaux": creneaux,
        "etudiants": etudiants,
        "filieres": lister_filieres_actives(),
        "filiere_id": filiere_id,
    })


@login_required
@role_requis("GESTION_3", "DIRECTEUR")
def marquer_presences(request, creneau_id):
    """Marquer les présences pour un créneau"""
    from directeur.models import EmploiDuTemps
    from etudiant.models import Etudiant
    from gestion3.models import Presence

    creneau = get_object_or_404(EmploiDuTemps, pk=creneau_id)
    etudiants = Etudiant.objects.filter(
        filiere=creneau.cours.filiere
    ).select_related("id_user").order_by("id_user__nom")

    if request.method == "POST":
        compteur = 0
        for etudiant in etudiants:
            statut = request.POST.get(f"statut_{etudiant.pk}", "")
            if statut:
                Presence.objects.update_or_create(
                    creneau=creneau, etudiant=etudiant, date_pointage=date.today(),
                    defaults={"statut": statut},
                )
                compteur += 1
        messages.success(request, f"{compteur} présence(s) enregistrée(s).")
        return redirect("gestion3:presences")

    presences = {
        p.etudiant_id: p.statut
        for p in Presence.objects.filter(creneau=creneau, date_pointage=date.today())
    }

    return render(request, "gestion3/marquer_presences.html", {
        "creneau": creneau,
        "etudiants": etudiants,
        "presences": presences,
        "statuts": ["Present", "Absent", "Retard", "Excuse"],
    })


@login_required
@role_requis("GESTION_3", "DIRECTEUR")
def liste_enseignants_filiere(request):
    """Liste des enseignants par niveau et filière"""
    from enseignant.models import EnseignantCours

    filiere_id = request.GET.get("filiere_id")
    assignations = EnseignantCours.objects.select_related(
        "enseignant__id_user", "cours__filiere"
    )
    if filiere_id:
        assignations = assignations.filter(cours__filiere_id=filiere_id)

    return render(request, "gestion3/enseignants_filiere.html", {
        "assignations": assignations,
        "filieres": lister_filieres_actives(),
        "filiere_id": filiere_id,
    })


@login_required
@role_requis("GESTION_3", "DIRECTEUR")
def alertes(request):
    """Alertes d'assiduité avec détails étudiant + contacts parents"""
    from gestion3.models import detecter_absences_critiques
    from django.conf import settings

    alertes_presences = detecter_absences_critiques(settings.SEUIL_ABSENCE_CRITIQUE)

    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Matricule", "Nom", "Prénom", "Filière", "Taux (%)", "Absences"]
        donnees = [
            [a["matricule"], a["nom"], a["prenom"], a["filiere"], a["taux"], a["absences"]]
            for a in alertes_presences
        ]
        if format_export == "excel":
            return exporter_excel("Alertes Assiduité", colonnes, donnees, "alertes")
        return exporter_pdf("Alertes Assiduité", colonnes, donnees, "alertes")

    return render(request, "gestion3/alertes.html", {
        "alertes_presences": alertes_presences,
    })
