"""
Décorateurs d'accès basés sur les rôles.
Utilisés dans toutes les vues pour contrôler l'accès.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_requis(*roles_autorises):
    """
    Décorateur vérifiant que l'utilisateur a un rôle autorisé.
    Usage: @role_requis("GESTION_1", "DIRECTEUR")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Veuillez vous connecter.")
                return redirect("accounts:login")
            if request.user.role not in roles_autorises:
                messages.error(request, "Accès non autorisé pour votre rôle.")
                return redirect("accounts:login")
            if not request.user.est_actif:
                messages.error(request, "Votre compte est désactivé.")
                return redirect("accounts:login")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
