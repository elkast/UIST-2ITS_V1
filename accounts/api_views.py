"""
Vues API JSON pour consommation mobile.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET


@require_GET
def api_edt_filiere(request, filiere_id):
    """API: EDT d'une filière"""
    from directeur.models import lister_edt_filiere
    creneaux = lister_edt_filiere(filiere_id)
    data = [
        {
            "id": c.pk,
            "jour": c.jour,
            "heure_debut": c.heure_debut.strftime("%H:%M"),
            "heure_fin": c.heure_fin.strftime("%H:%M"),
            "cours": c.cours.libelle,
            "code_cours": c.cours.code_cours,
            "enseignant": str(c.enseignant),
            "salle": c.salle.nom_salle,
            "type": c.type_creneau,
        }
        for c in creneaux
    ]
    return JsonResponse({"edt": data})


@require_GET
def api_notes_etudiant(request, etudiant_id):
    """API: Notes validées d'un étudiant"""
    from gestion2.models import lister_notes_etudiant, calculer_moyenne_etudiant
    notes = lister_notes_etudiant(etudiant_id, validees_seulement=True)
    moyenne = calculer_moyenne_etudiant(etudiant_id)
    data = [
        {
            "cours": n.id_cours.libelle,
            "note": n.valeur_note,
            "type": n.type_evaluation,
            "date": n.date_saisie.strftime("%d/%m/%Y"),
        }
        for n in notes
    ]
    return JsonResponse({"notes": data, "moyenne": moyenne})


@require_GET
def api_presences_etudiant(request, etudiant_id):
    """API: Statistiques de présence"""
    from gestion3.models import calculer_taux_presence
    taux = calculer_taux_presence(etudiant_id)
    return JsonResponse(taux)


@login_required
@require_GET
def api_notifications(request):
    """API: Notifications de l'utilisateur connecté"""
    from accounts.models import Notification
    notifs = Notification.objects.filter(
        destinataire=request.user
    ).order_by("-date_creation")[:20]
    data = [
        {
            "id": n.pk,
            "type": n.type_notif,
            "titre": n.titre,
            "message": n.message,
            "lue": n.est_lue,
            "date": n.date_creation.strftime("%d/%m/%Y %H:%M"),
        }
        for n in notifs
    ]
    return JsonResponse({"notifications": data})


@require_GET
def api_filieres(request):
    """API: Liste des filières actives"""
    from gestion1.models import lister_filieres_actives
    filieres = lister_filieres_actives()
    data = [
        {
            "id": f.pk,
            "code": f.code_filiere,
            "nom": f.nom_filiere,
            "niveau": f.niveau,
        }
        for f in filieres
    ]
    return JsonResponse({"filieres": data})


@require_GET
def api_recherche_parents(request):
    """API: Recherche de parents par nom (autocomplétion)"""
    terme = request.GET.get("q", "").strip()
    if len(terme) < 2:
        return JsonResponse({"parents": []})

    from parent.models import rechercher_parents_par_nom
    parents = rechercher_parents_par_nom(terme)
    data = [
        {
            "id": p.pk,
            "nom": p.id_user.nom,
            "prenom": p.id_user.prenom,
            "matricule": p.id_user.matricule,
            "telephone": p.telephone,
        }
        for p in parents
    ]
    return JsonResponse({"parents": data})
