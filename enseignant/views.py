"""
Vues Enseignant - EDT, disponibilités, notes.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import time as dt_time

from accounts.decorators import role_requis
from enseignant.models import obtenir_enseignant_par_user


@login_required
@role_requis("ENSEIGNANT")
def dashboard(request):
    """Tableau de bord enseignant"""
    enseignant = obtenir_enseignant_par_user(request.user.pk)
    if not enseignant:
        messages.error(request, "Profil enseignant non trouvé.")
        return redirect("accounts:logout")

    from directeur.models import lister_edt_enseignant
    from enseignant.models import lister_cours_enseignant

    creneaux = lister_edt_enseignant(enseignant.pk)
    cours_assignes = lister_cours_enseignant(enseignant.pk)

    return render(request, "enseignant/dashboard.html", {
        "enseignant": enseignant,
        "creneaux": creneaux[:5],
        "total_cours": cours_assignes.count(),
    })


@login_required
@role_requis("ENSEIGNANT")
def emploi_temps(request):
    """EDT personnel de l'enseignant"""
    enseignant = obtenir_enseignant_par_user(request.user.pk)
    if not enseignant:
        messages.error(request, "Profil non trouvé.")
        return redirect("accounts:logout")

    from directeur.models import lister_edt_enseignant, JOURS_SEMAINE
    creneaux = lister_edt_enseignant(enseignant.pk)

    return render(request, "enseignant/edt.html", {
        "creneaux": creneaux,
        "jours": JOURS_SEMAINE,
    })


@login_required
@role_requis("ENSEIGNANT")
def disponibilites(request):
    """Gérer les disponibilités"""
    from enseignant.models import DisponibiliteEnseignant, JOURS_SEMAINE

    enseignant = obtenir_enseignant_par_user(request.user.pk)
    if not enseignant:
        messages.error(request, "Profil non trouvé.")
        return redirect("accounts:logout")

    if request.method == "POST":
        jour = request.POST.get("jour")
        heure_debut = dt_time.fromisoformat(request.POST.get("heure_debut"))
        heure_fin = dt_time.fromisoformat(request.POST.get("heure_fin"))
        est_dispo = request.POST.get("est_disponible") == "on"

        DisponibiliteEnseignant.objects.create(
            enseignant=enseignant, jour=jour,
            heure_debut=heure_debut, heure_fin=heure_fin,
            est_disponible=est_dispo,
        )
        messages.success(request, "Disponibilité enregistrée.")
        return redirect("enseignant:disponibilites")

    from enseignant.models import obtenir_disponibilites
    dispos = obtenir_disponibilites(enseignant.pk)

    return render(request, "enseignant/disponibilites.html", {
        "disponibilites": dispos,
        "jours": JOURS_SEMAINE,
    })


@login_required
@role_requis("ENSEIGNANT")
def supprimer_disponibilite(request, dispo_id):
    """Supprimer une disponibilité"""
    from enseignant.models import DisponibiliteEnseignant
    dispo = DisponibiliteEnseignant.objects.filter(pk=dispo_id).first()
    if dispo:
        dispo.delete()
        messages.success(request, "Disponibilité supprimée.")
    return redirect("enseignant:disponibilites")


@login_required
@role_requis("ENSEIGNANT")
def voir_notes(request):
    """Voir les notes envoyées par niveau et filière"""
    enseignant = obtenir_enseignant_par_user(request.user.pk)
    if not enseignant:
        return redirect("accounts:logout")

    from enseignant.models import lister_cours_enseignant
    from gestion2.models import Note
    from gestion1.models import lister_filieres_actives

    filiere_id = request.GET.get("filiere_id")
    cours_ens = lister_cours_enseignant(enseignant.pk)
    cours_ids = [c.cours_id for c in cours_ens]

    notes = Note.objects.filter(
        id_cours_id__in=cours_ids
    ).select_related("id_etudiant__id_user", "id_cours", "id_cours__filiere")

    if filiere_id:
        notes = notes.filter(id_cours__filiere_id=filiere_id)

    notes = notes.order_by("-date_saisie")[:50]

    return render(request, "enseignant/notes.html", {
        "notes": notes,
        "filieres": lister_filieres_actives(),
        "filiere_id": filiere_id,
    })
