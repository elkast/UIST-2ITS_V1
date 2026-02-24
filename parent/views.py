"""
Vues Parent - Suivi des enfants (EDT, notes, assiduité).
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from accounts.decorators import role_requis
from parent.models import (
    obtenir_parent_par_user,
    obtenir_enfants_parent,
    verifier_lien_parent_etudiant,
)


@login_required
@role_requis("PARENT")
def dashboard(request):
    parent = obtenir_parent_par_user(request.user.pk)
    if not parent:
        messages.error(request, "Profil parent non trouvé.")
        return redirect("accounts:logout")

    enfants = obtenir_enfants_parent(parent.pk)

    return render(
        request,
        "parent/dashboard.html",
        {
            "parent": parent,
            "enfants": enfants,
        },
    )


@login_required
@role_requis("PARENT")
def edt_enfant(request, etudiant_id):
    parent = obtenir_parent_par_user(request.user.pk)
    if not parent or not verifier_lien_parent_etudiant(parent.pk, etudiant_id):
        raise Http404("Accès refusé")

    from etudiant.models import Etudiant

    etudiant = Etudiant.objects.select_related("id_user", "filiere").get(pk=etudiant_id)

    from directeur.models import lister_edt_filiere, JOURS_SEMAINE

    creneaux = lister_edt_filiere(etudiant.filiere_id)

    return render(
        request,
        "parent/edt_enfant.html",
        {
            "etudiant": etudiant,
            "creneaux": creneaux,
            "jours": JOURS_SEMAINE,
        },
    )


@login_required
@role_requis("PARENT")
def notes_enfant(request, etudiant_id):
    parent = obtenir_parent_par_user(request.user.pk)
    if not parent or not verifier_lien_parent_etudiant(parent.pk, etudiant_id):
        raise Http404("Accès refusé")

    from etudiant.models import Etudiant

    etudiant = Etudiant.objects.select_related("id_user", "filiere").get(pk=etudiant_id)

    from gestion2.models import lister_notes_etudiant, calculer_moyenne_etudiant

    notes = lister_notes_etudiant(etudiant_id, validees_seulement=True)
    moyenne = calculer_moyenne_etudiant(etudiant_id)

    return render(
        request,
        "parent/notes_enfant.html",
        {
            "etudiant": etudiant,
            "notes": notes,
            "moyenne": moyenne,
        },
    )


@login_required
@role_requis("PARENT")
def assiduite_enfant(request, etudiant_id):
    parent = obtenir_parent_par_user(request.user.pk)
    if not parent or not verifier_lien_parent_etudiant(parent.pk, etudiant_id):
        raise Http404("Accès refusé")

    from etudiant.models import Etudiant

    etudiant = Etudiant.objects.select_related("id_user", "filiere").get(pk=etudiant_id)

    from gestion3.models import calculer_taux_presence, lister_absences_etudiant

    taux = calculer_taux_presence(etudiant_id)
    absences = lister_absences_etudiant(etudiant_id)

    return render(
        request,
        "parent/assiduite_enfant.html",
        {
            "etudiant": etudiant,
            "taux": taux,
            "absences": absences,
        },
    )


@login_required
@role_requis("PARENT")
def notifications(request):
    from accounts.models import Notification

    # D'abord mettre à jour les notifications non lues
    Notification.objects.filter(destinataire=request.user, est_lue=False).update(
        est_lue=True
    )
    # Ensuite récupérer les notifications (après la mise à jour)
    notifs = Notification.objects.filter(destinataire=request.user).order_by(
        "-date_creation"
    )[:30]
    return render(request, "parent/notifications.html", {"notifications": notifs})
