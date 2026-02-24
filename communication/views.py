"""
Vues Communication - Dashboard, Gestion des événements et publications.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Evenement, Publication


@login_required
def dashboard(request):
    """Dashboard Communication - Aperçu des publications et événements"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    # Statistiques
    nb_evenements = Evenement.objects.count()
    nb_evenements_publies = Evenement.objects.filter(est_publie=True).count()
    nb_publications = Publication.objects.count()
    nb_publications_publiees = Publication.objects.filter(est_publie=True).count()

    # Derniers événements et publications
    derniers_evenements = Evenement.objects.order_by("-date_creation")[:5]
    dernieres_publications = Publication.objects.order_by("-date_creation")[:5]

    context = {
        "nb_evenements": nb_evenements,
        "nb_evenements_publies": nb_evenements_publies,
        "nb_publications": nb_publications,
        "nb_publications_publiees": nb_publications_publiees,
        "derniers_evenements": derniers_evenements,
        "dernieres_publications": dernieres_publications,
    }
    return render(request, "communication/dashboard.html", context)


@login_required
def liste_evenements(request):
    """Liste des événements"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    evenements = Evenement.objects.order_by("-date_creation")
    return render(request, "communication/evenements.html", {"evenements": evenements})


@login_required
def creer_evenement(request):
    """Créer un nouvel événement"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    if request.method == "POST":
        titre = request.POST.get("titre", "").strip()
        description = request.POST.get("description", "").strip()
        type_evenement = request.POST.get("type_evenement", "EVENEMENT")
        url_video = request.POST.get("url_video", "").strip()
        date_evenement = request.POST.get("date_evenement", "").strip()
        lieu = request.POST.get("lieu", "").strip()
        est_publie = request.POST.get("est_publie") == "on"
        est_urgent = request.POST.get("est_urgent") == "on"

        if not titre or not description:
            messages.error(request, "Titre et description sont requis.")
            return redirect("communication:creer_evenement")

        evenement = Evenement.objects.create(
            titre=titre,
            description=description,
            type_evenement=type_evenement,
            url_video=url_video,
            lieu=lieu,
            est_publie=est_publie,
            est_urgent=est_urgent,
            auteur=request.user,
        )

        if date_evenement:
            from datetime import datetime

            try:
                evenement.date_evenement = datetime.strptime(
                    date_evenement, "%Y-%m-%dT%H:%M"
                )
                evenement.save()
            except ValueError:
                pass

        messages.success(request, "Événement créé avec succès!")
        return redirect("communication:liste_evenements")

    return render(request, "communication/evenement_form.html")


@login_required
def modifier_evenement(request, pk):
    """Modifier un événement"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    evenement = get_object_or_404(Evenement, pk=pk)

    if request.method == "POST":
        evenement.titre = request.POST.get("titre", "").strip()
        evenement.description = request.POST.get("description", "").strip()
        evenement.type_evenement = request.POST.get("type_evenement", "EVENEMENT")
        evenement.url_video = request.POST.get("url_video", "").strip()
        evenement.lieu = request.POST.get("lieu", "").strip()
        evenement.est_publie = request.POST.get("est_publie") == "on"
        evenement.est_urgent = request.POST.get("est_urgent") == "on"

        date_evenement = request.POST.get("date_evenement", "").strip()
        if date_evenement:
            from datetime import datetime

            try:
                evenement.date_evenement = datetime.strptime(
                    date_evenement, "%Y-%m-%dT%H:%M"
                )
            except ValueError:
                evenement.date_evenement = None
        else:
            evenement.date_evenement = None

        evenement.save()
        messages.success(request, "Événement modifié avec succès!")
        return redirect("communication:liste_evenements")

    return render(
        request, "communication/evenement_form.html", {"evenement": evenement}
    )


@login_required
def supprimer_evenement(request, pk):
    """Supprimer un événement"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    evenement = get_object_or_404(Evenement, pk=pk)
    evenement.delete()
    messages.success(request, "Événement supprimé avec succès!")
    return redirect("communication:liste_evenements")


@login_required
def liste_publications(request):
    """Liste des publications"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    publications = Publication.objects.order_by("-date_creation")
    return render(
        request, "communication/publications.html", {"publications": publications}
    )


@login_required
def creer_publication(request):
    """Créer une nouvelle publication"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    if request.method == "POST":
        titre = request.POST.get("titre", "").strip()
        contenu = request.POST.get("contenu", "").strip()
        est_publie = request.POST.get("est_publie") == "on"
        est_accueil = request.POST.get("est_accueil") == "on"

        if not titre or not contenu:
            messages.error(request, "Titre et contenu sont requis.")
            return redirect("communication:creer_publication")

        publication = Publication.objects.create(
            titre=titre,
            contenu=contenu,
            est_publie=est_publie,
            est_accueil=est_accueil,
            auteur=request.user,
        )

        messages.success(request, "Publication créée avec succès!")
        return redirect("communication:liste_publications")

    return render(request, "communication/publication_form.html")


@login_required
def modifier_publication(request, pk):
    """Modifier une publication"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    publication = get_object_or_404(Publication, pk=pk)

    if request.method == "POST":
        publication.titre = request.POST.get("titre", "").strip()
        publication.contenu = request.POST.get("contenu", "").strip()
        publication.est_publie = request.POST.get("est_publie") == "on"
        publication.est_accueil = request.POST.get("est_accueil") == "on"
        publication.save()

        messages.success(request, "Publication modifiée avec succès!")
        return redirect("communication:liste_publications")

    return render(
        request, "communication/publication_form.html", {"publication": publication}
    )


@login_required
def supprimer_publication(request, pk):
    """Supprimer une publication"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    publication = get_object_or_404(Publication, pk=pk)
    publication.delete()
    messages.success(request, "Publication supprimée avec succès!")
    return redirect("communication:liste_publications")


@login_required
def toggle_publication_evenement(request, pk):
    """Publier/Dépublier un événement"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    evenement = get_object_or_404(Evenement, pk=pk)
    evenement.est_publie = not evenement.est_publie
    evenement.save()

    status = "publié" if evenement.est_publie else "dépublié"
    messages.success(request, f"Événement {status} avec succès!")
    return redirect("communication:liste_evenements")


@login_required
def toggle_publication(request, pk):
    """Publier/Dépublier une publication"""
    if request.user.role != "COMMUNICATION":
        messages.error(request, "Accès réservé au service Communication.")
        return redirect("accounts:login")

    publication = get_object_or_404(Publication, pk=pk)
    publication.est_publie = not publication.est_publie
    publication.save()

    status = "publiée" if publication.est_publie else "dépubliée"
    messages.success(request, f"Publication {status} avec succès!")
    return redirect("communication:liste_publications")
