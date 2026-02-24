"""
Vues Authentification - Connexion, déconnexion, page d'accueil.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone


def landing_page(request):
    """Page d'accueil publique"""
    if request.user.is_authenticated:
        return redirect(_redirection_role(request.user.role))
    return render(request, "landing.html")


def login_view(request):
    """Connexion par matricule + mot de passe"""
    if request.user.is_authenticated:
        return redirect(_redirection_role(request.user.role))

    if request.method == "POST":
        matricule = request.POST.get("matricule", "").strip()
        password = request.POST.get("password", "").strip()

        if not matricule or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, "auth/login.html")

        user = authenticate(request, username=matricule, password=password)

        if user is not None:
            if not user.est_actif:
                messages.error(
                    request, "Votre compte est désactivé. Contactez l'administration."
                )
                return render(request, "auth/login.html")

            login(request, user)
            user.derniere_connexion = timezone.now()
            user.save(update_fields=["derniere_connexion"])

            # Log d'audit
            from super_admin.models import creer_log_audit

            creer_log_audit(
                request, "CONNEXION", details=f"Connexion de {user.nom_complet}"
            )

            messages.success(request, f"Bienvenue, {user.nom_complet} !")
            return redirect(_redirection_role(user.role))
        else:
            messages.error(request, "Matricule ou mot de passe invalide.")

    return render(request, "auth/login.html")


def logout_view(request):
    """Déconnexion"""
    if request.user.is_authenticated:
        from super_admin.models import creer_log_audit

        creer_log_audit(
            request, "DECONNEXION", details=f"Déconnexion de {request.user.nom_complet}"
        )
    logout(request)
    messages.info(request, "Déconnexion réussie.")
    return redirect("accounts:login")


def _redirection_role(role):
    """Retourne l'URL du dashboard selon le rôle"""
    redirections = {
        "SUPER_ADMIN": "super_admin:dashboard",
        "DIRECTEUR": "directeur:dashboard",
        "GESTION_1": "gestion1:dashboard",
        "GESTION_2": "gestion2:dashboard",
        "GESTION_3": "gestion3:dashboard",
        "COMMUNICATION": "communication:dashboard",
        "ENSEIGNANT": "enseignant:dashboard",
        "ETUDIANT": "etudiant:dashboard",
        "PARENT": "parent:dashboard",
    }
    return redirections.get(role, "accounts:login")


def feedback_view(request):
    """Soumettre un feedback - Accessible sans connexion"""
    if request.method == "POST":
        note = request.POST.get("note")
        commentaire = request.POST.get("commentaire", "").strip()
        email = request.POST.get("email", "").strip()

        if not note:
            messages.error(request, "Veuillez sélectionner une note.")
            return redirect("accounts:landing")

        from gestion1.models import Feedback

        Feedback.objects.create(note=int(note), commentaire=commentaire, email=email)
        messages.success(
            request, "Merci pour votre retour ! Nous apprécions vos commentaires."
        )
        return redirect("accounts:landing")

    return redirect("accounts:landing")
