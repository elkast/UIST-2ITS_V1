"""
Vues Gestion 1 - Logistique & Infrastructure.
Salles (avec équipements + verrouillage), Filières, Cours.
L'EDT n'est plus géré ici (transféré au Directeur).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.decorators import role_requis
from accounts.exports import exporter_pdf, exporter_excel
from gestion1.models import (
    Filiere,
    Salle,
    Cours,
    Feedback,
    lister_filieres_actives,
    lister_tous_cours_actifs,
    lister_salles,
)


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def dashboard(request):
    """Tableau de bord Gestion 1"""
    return render(
        request,
        "gestion1/dashboard.html",
        {
            "total_salles": Salle.objects.count(),
            "total_filieres": Filiere.objects.filter(est_active=True).count(),
            "total_cours": Cours.objects.filter(statut="Actif").count(),
        },
    )


# ============================================================
# SALLES
# ============================================================


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def liste_salles(request):
    """Liste des salles"""
    salles = lister_salles()
    return render(request, "gestion1/salles.html", {"salles": salles})


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def nouvelle_salle(request):
    """Créer une salle"""
    if request.method == "POST":
        Salle.objects.create(
            nom_salle=request.POST.get("nom_salle", "").strip(),
            capacite=int(request.POST.get("capacite", 30)),
            batiment=request.POST.get("batiment", "").strip(),
            nb_projecteurs=int(request.POST.get("nb_projecteurs", 0)),
            nb_rallonges=int(request.POST.get("nb_rallonges", 0)),
            nb_ordinateurs=int(request.POST.get("nb_ordinateurs", 0)),
            nb_chargeurs=int(request.POST.get("nb_chargeurs", 0)),
            nb_adaptateurs=int(request.POST.get("nb_adaptateurs", 0)),
        )
        messages.success(request, "Salle créée avec succès.")
        return redirect("gestion1:salles")

    return render(request, "gestion1/salle_form.html")


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def modifier_salle(request, salle_id):
    """Modifier une salle (vérifie verrouillage)"""
    salle = get_object_or_404(Salle, pk=salle_id)

    if salle.verrouille and request.user.role != "DIRECTEUR":
        messages.error(
            request,
            "Cette salle est verrouillée. Modification nécessite l'accord du directeur.",
        )
        return redirect("gestion1:salles")

    if request.method == "POST":
        salle.nom_salle = request.POST.get("nom_salle", salle.nom_salle).strip()
        salle.capacite = int(request.POST.get("capacite", salle.capacite))
        salle.batiment = request.POST.get("batiment", salle.batiment).strip()
        salle.nb_projecteurs = int(request.POST.get("nb_projecteurs", 0))
        salle.nb_rallonges = int(request.POST.get("nb_rallonges", 0))
        salle.nb_ordinateurs = int(request.POST.get("nb_ordinateurs", 0))
        salle.nb_chargeurs = int(request.POST.get("nb_chargeurs", 0))
        salle.nb_adaptateurs = int(request.POST.get("nb_adaptateurs", 0))
        salle.save()
        messages.success(request, "Salle modifiée.")
        return redirect("gestion1:salles")

    return render(request, "gestion1/salle_form.html", {"salle": salle})


@login_required
@role_requis("DIRECTEUR")
def verrouiller_salle(request, salle_id):
    """Verrouiller/déverrouiller une salle (directeur seulement)"""
    salle = get_object_or_404(Salle, pk=salle_id)
    salle.verrouille = not salle.verrouille
    salle.save(update_fields=["verrouille"])
    action = "verrouillée" if salle.verrouille else "déverrouillée"
    messages.success(request, f"Salle {action}.")
    return redirect("gestion1:salles")


# ============================================================
# FILIÈRES
# ============================================================


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def liste_filieres(request):
    """Liste des filières"""
    filieres = lister_filieres_actives()
    return render(request, "gestion1/filieres.html", {"filieres": filieres})


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def nouvelle_filiere(request):
    if request.method == "POST":
        Filiere.objects.create(
            code_filiere=request.POST.get("code_filiere", "").strip(),
            nom_filiere=request.POST.get("nom_filiere", "").strip(),
            niveau=request.POST.get("niveau"),
        )
        messages.success(request, "Filière créée.")
        return redirect("gestion1:filieres")

    return render(
        request,
        "gestion1/filiere_form.html",
        {
            "niveaux": Filiere.NIVEAU_CHOICES,
        },
    )


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def modifier_filiere(request, filiere_id):
    filiere = get_object_or_404(Filiere, pk=filiere_id)
    if request.method == "POST":
        filiere.code_filiere = request.POST.get(
            "code_filiere", filiere.code_filiere
        ).strip()
        filiere.nom_filiere = request.POST.get(
            "nom_filiere", filiere.nom_filiere
        ).strip()
        filiere.niveau = request.POST.get("niveau", filiere.niveau)
        filiere.est_active = request.POST.get("est_active") == "on"
        filiere.save()
        messages.success(request, "Filière modifiée.")
        return redirect("gestion1:filieres")

    return render(
        request,
        "gestion1/filiere_form.html",
        {
            "filiere": filiere,
            "niveaux": Filiere.NIVEAU_CHOICES,
        },
    )


# ============================================================
# COURS
# ============================================================


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def liste_cours(request):
    """Liste des cours avec filtre par filière"""
    filiere_id = request.GET.get("filiere_id")
    cours = lister_tous_cours_actifs()
    if filiere_id:
        cours = cours.filter(filiere_id=filiere_id)

    # Export
    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Code", "Libellé", "Crédits", "Vol. Horaire", "Filière", "Statut"]
        donnees = [
            [
                c.code_cours,
                c.libelle,
                c.credit,
                f"{c.volume_horaire}h",
                c.filiere.nom_filiere,
                c.statut,
            ]
            for c in cours
        ]
        if format_export == "excel":
            return exporter_excel("Liste des Cours", colonnes, donnees, "cours")
        return exporter_pdf("Liste des Cours", colonnes, donnees, "cours")

    return render(
        request,
        "gestion1/cours.html",
        {
            "cours": cours,
            "filieres": lister_filieres_actives(),
            "filiere_id": filiere_id,
        },
    )


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def nouveau_cours(request):
    if request.method == "POST":
        Cours.objects.create(
            code_cours=request.POST.get("code_cours", "").strip(),
            libelle=request.POST.get("libelle", "").strip(),
            credit=int(request.POST.get("credit", 3)),
            volume_horaire=int(request.POST.get("volume_horaire", 0)),
            filiere_id=int(request.POST.get("filiere_id")),
        )
        messages.success(request, "Cours créé.")
        return redirect("gestion1:cours")

    return render(
        request,
        "gestion1/cours_form.html",
        {
            "filieres": lister_filieres_actives(),
        },
    )


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def modifier_cours(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id)
    if request.method == "POST":
        cours.code_cours = request.POST.get("code_cours", cours.code_cours).strip()
        cours.libelle = request.POST.get("libelle", cours.libelle).strip()
        cours.credit = int(request.POST.get("credit", cours.credit))
        cours.volume_horaire = int(
            request.POST.get("volume_horaire", cours.volume_horaire)
        )
        cours.filiere_id = int(request.POST.get("filiere_id", cours.filiere_id))
        cours.statut = request.POST.get("statut", cours.statut)
        cours.save()
        messages.success(request, "Cours modifié.")
        return redirect("gestion1:cours")

    return render(
        request,
        "gestion1/cours_form.html",
        {
            "cours": cours,
            "filieres": lister_filieres_actives(),
        },
    )


# ============================================================
# ASSIGNATION ENSEIGNANT-COURS
# ============================================================


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def assignation_cours(request):
    """Ajouter ou retirer un cours/filière à un enseignant"""
    from enseignant.models import Enseignant, EnseignantCours

    if request.method == "POST":
        action = request.POST.get("action")
        enseignant_id = int(request.POST.get("enseignant_id"))
        cours_id = int(request.POST.get("cours_id"))

        if action == "ajouter":
            EnseignantCours.objects.get_or_create(
                enseignant_id=enseignant_id, cours_id=cours_id
            )
            messages.success(request, "Cours assigné à l'enseignant.")
        elif action == "retirer":
            EnseignantCours.objects.filter(
                enseignant_id=enseignant_id, cours_id=cours_id
            ).delete()
            messages.success(request, "Cours retiré de l'enseignant.")

        return redirect("gestion1:assignation")

    enseignants = Enseignant.objects.select_related("id_user").all()
    cours = lister_tous_cours_actifs()
    assignations = EnseignantCours.objects.select_related(
        "enseignant__id_user", "cours__filiere"
    ).all()

    return render(
        request,
        "gestion1/assignation.html",
        {
            "enseignants": enseignants,
            "cours": cours,
            "assignations": assignations,
        },
    )


# ============================================================
# FEEDBACK / ÉVALUATION UI/UX
# ============================================================


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def liste_feedbacks(request):
    """Liste des feedbacks (Gestion 1 et Directeur)"""
    feedbacks = Feedback.objects.all()
    est_traite = request.GET.get("est_traite")
    if est_traite == "oui":
        feedbacks = feedbacks.filter(est_traite=True)
    elif est_traite == "non":
        feedbacks = feedbacks.filter(est_traite=False)

    # Statistiques
    total = Feedback.objects.count()
    moyenne = 0
    if total > 0:
        moyenne = sum(f.note for f in Feedback.objects.all()) / total

    return render(
        request,
        "gestion1/feedbacks.html",
        {
            "feedbacks": feedbacks.order_by("-date_creation"),
            "total": total,
            "moyenne": round(moyenne, 2),
            "est_traite": est_traite,
        },
    )


@login_required
@role_requis("GESTION_1", "DIRECTEUR")
def traiter_feedback(request, feedback_id):
    """Marquer un feedback comme traité"""
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    feedback.est_traite = not feedback.est_traite
    feedback.save(update_fields=["est_traite"])
    messages.success(
        request,
        (
            "Feedback marqué comme traité."
            if feedback.est_traite
            else "Feedback marqué comme non traité."
        ),
    )
    return redirect("gestion1:feedbacks")
