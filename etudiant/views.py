"""
Vues Étudiant - Dashboard, EDT, notes, profil.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.decorators import role_requis
from etudiant.models import obtenir_etudiant_par_user


@login_required
@role_requis("ETUDIANT")
def dashboard(request):
    etudiant = obtenir_etudiant_par_user(request.user.pk)
    if not etudiant:
        messages.error(request, "Profil étudiant non trouvé.")
        return redirect("accounts:logout")

    from gestion2.models import calculer_moyenne_etudiant, calculer_rang_etudiant

    moyenne = calculer_moyenne_etudiant(etudiant.pk)
    rang = calculer_rang_etudiant(etudiant.pk)

    return render(
        request,
        "etudiant/dashboard.html",
        {
            "etudiant": etudiant,
            "moyenne": moyenne,
            "rang": rang,
        },
    )


@login_required
@role_requis("ETUDIANT")
def emploi_temps(request):
    """EDT de la filière de l'étudiant (temps réel)"""
    etudiant = obtenir_etudiant_par_user(request.user.pk)
    if not etudiant:
        return redirect("accounts:logout")

    from directeur.models import lister_edt_filiere, JOURS_SEMAINE

    creneaux = lister_edt_filiere(etudiant.filiere_id)

    return render(
        request,
        "etudiant/edt.html",
        {
            "creneaux": creneaux,
            "jours": JOURS_SEMAINE,
            "etudiant": etudiant,
        },
    )


@login_required
@role_requis("ETUDIANT")
def mes_notes(request):
    """Notes validées uniquement"""
    etudiant = obtenir_etudiant_par_user(request.user.pk)
    if not etudiant:
        return redirect("accounts:logout")

    from gestion2.models import lister_notes_etudiant, calculer_moyenne_etudiant

    notes = lister_notes_etudiant(etudiant.pk, validees_seulement=True)
    moyenne = calculer_moyenne_etudiant(etudiant.pk)

    return render(
        request,
        "etudiant/notes.html",
        {
            "notes": notes,
            "moyenne": moyenne,
            "etudiant": etudiant,
        },
    )


@login_required
@role_requis("ETUDIANT")
def profil(request):
    etudiant = obtenir_etudiant_par_user(request.user.pk)
    if not etudiant:
        return redirect("accounts:logout")

    if request.method == "POST":
        etudiant.adresse = request.POST.get("adresse", "").strip()
        etudiant.save(update_fields=["adresse"])

        email = request.POST.get("email", "").strip()
        if email:
            etudiant.id_user.email = email
            etudiant.id_user.save(update_fields=["email"])

        messages.success(request, "Profil mis à jour.")
        return redirect("etudiant:profil")

    return render(request, "etudiant/profil.html", {"etudiant": etudiant})


@login_required
@role_requis("ETUDIANT")
def notifications(request):
    """Notifications de l'étudiant"""
    from accounts.models import Notification

    # D'abord mettre à jour les notifications non lues
    Notification.objects.filter(destinataire=request.user, est_lue=False).update(
        est_lue=True
    )
    # Ensuite récupérer les notifications
    notifs = Notification.objects.filter(destinataire=request.user).order_by(
        "-date_creation"
    )[:30]

    return render(request, "etudiant/notifications.html", {"notifications": notifs})
