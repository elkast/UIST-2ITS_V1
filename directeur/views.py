"""
Vues Directeur - EDT CRUD complet, validation notes, rapports, disponibilités.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import time as dt_time

from accounts.decorators import role_requis
from accounts.exports import exporter_pdf, exporter_excel
from accounts.models import Utilisateur, Notification, creer_notification


@login_required
@role_requis("DIRECTEUR")
def dashboard(request):
    """Tableau de bord stratégique du directeur"""
    from gestion2.models import lister_notes_en_attente
    from etudiant.models import Etudiant
    from enseignant.models import Enseignant
    from parent.models import Parent
    from gestion1.models import Filiere
    from directeur.models import lister_tout_edt

    notes_attente = lister_notes_en_attente()
    edt = lister_tout_edt()

    return render(request, "directeur/dashboard.html", {
        "notes_attente_count": notes_attente.count(),
        "total_etudiants": Etudiant.objects.count(),
        "total_enseignants": Enseignant.objects.count(),
        "total_parents": Parent.objects.count(),
        "total_filieres": Filiere.objects.filter(est_active=True).count(),
        "total_creneaux": edt.count(),
        "notifications": Notification.objects.filter(destinataire=request.user, est_lue=False)[:5],
    })


# ============================================================
# VALIDATION DES NOTES
# ============================================================

@login_required
@role_requis("DIRECTEUR")
def validation_notes(request):
    """Liste des notes à valider avec cases à cocher"""
    from gestion2.models import lister_notes_en_attente
    from gestion1.models import lister_filieres_actives

    filiere_id = request.GET.get("filiere_id")
    notes = lister_notes_en_attente()
    if filiere_id:
        notes = notes.filter(id_cours__filiere_id=filiere_id)

    return render(request, "directeur/validation_notes.html", {
        "notes": notes,
        "filieres": lister_filieres_actives(),
        "filiere_id": filiere_id,
    })


@login_required
@role_requis("DIRECTEUR")
def valider_notes_masse(request):
    """Valider plusieurs notes en une fois (cases cochées)"""
    if request.method == "POST":
        from gestion2.models import Note
        from directeur.models import ValidationNote

        note_ids = request.POST.getlist("notes_selectionnees")
        action = request.POST.get("action", "valider")

        compteur = 0
        for note_id in note_ids:
            try:
                note = Note.objects.get(pk=note_id)
                if action == "valider":
                    note.statut_validation = "Valide"
                    note.id_validateur = request.user
                    note.date_validation = timezone.now()
                else:
                    note.statut_validation = "Rejete"
                    note.id_validateur = request.user
                    note.date_validation = timezone.now()
                note.save()

                ValidationNote.objects.create(
                    note=note, validateur=request.user, action=note.statut_validation
                )

                # Notification à l'étudiant
                creer_notification(
                    note.id_etudiant.id_user_id,
                    "VALIDATION_NOTE",
                    f"Note {note.statut_validation.lower()} en {note.id_cours.libelle}",
                    f"Votre note de {note.valeur_note}/20 en {note.id_cours.libelle} a été {note.statut_validation.lower()}.",
                )
                compteur += 1
            except Note.DoesNotExist:
                continue

        from super_admin.models import creer_log_audit
        creer_log_audit(request, "VALIDATION_NOTE", "notes", details=f"{compteur} notes validées")

        messages.success(request, f"{compteur} note(s) traitée(s).")

    return redirect("directeur:validation_notes")


# ============================================================
# EDT - CRUD COMPLET
# ============================================================

@login_required
@role_requis("DIRECTEUR")
def emploi_temps(request):
    """Afficher l'emploi du temps complet"""
    from directeur.models import lister_tout_edt, lister_edt_filiere, JOURS_SEMAINE, HEURES_PLAGE
    from gestion1.models import lister_filieres_actives

    filiere_id = request.GET.get("filiere_id")
    if filiere_id:
        creneaux = lister_edt_filiere(int(filiere_id))
    else:
        creneaux = lister_tout_edt()

    # Export
    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Jour", "Début", "Fin", "Cours", "Enseignant", "Salle", "Type"]
        donnees = [
            [c.jour, c.heure_debut.strftime("%H:%M"), c.heure_fin.strftime("%H:%M"),
             c.cours.libelle, str(c.enseignant), c.salle.nom_salle, c.type_creneau]
            for c in creneaux
        ]
        titre = "Emploi du Temps"
        if format_export == "excel":
            return exporter_excel(titre, colonnes, donnees, "edt")
        return exporter_pdf(titre, colonnes, donnees, "edt")

    return render(request, "directeur/edt.html", {
        "creneaux": creneaux,
        "filieres": lister_filieres_actives(),
        "filiere_id": filiere_id,
        "jours": JOURS_SEMAINE,
        "heures": HEURES_PLAGE,
    })


@login_required
@role_requis("DIRECTEUR")
def nouveau_creneau(request):
    """Créer un créneau EDT"""
    if request.method == "POST":
        from directeur.models import EmploiDuTemps, verifier_conflits_edt

        cours_id = int(request.POST.get("cours_id"))
        enseignant_id = int(request.POST.get("enseignant_id"))
        salle_id = int(request.POST.get("salle_id"))
        jour = request.POST.get("jour")
        heure_debut = dt_time.fromisoformat(request.POST.get("heure_debut"))
        heure_fin = dt_time.fromisoformat(request.POST.get("heure_fin"))
        type_creneau = request.POST.get("type_creneau", "Cours")

        conflits = verifier_conflits_edt(cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin)
        if conflits:
            messages.error(request, f"Conflits détectés: {', '.join(conflits)}")
        else:
            EmploiDuTemps.objects.create(
                cours_id=cours_id, enseignant_id=enseignant_id, salle_id=salle_id,
                jour=jour, heure_debut=heure_debut, heure_fin=heure_fin, type_creneau=type_creneau,
            )
            from super_admin.models import creer_log_audit
            creer_log_audit(request, "CREATION_EDT", "emploi_du_temps")
            messages.success(request, "Créneau créé avec succès.")

        return redirect("directeur:edt")

    from gestion1.models import lister_tous_cours_actifs, lister_salles
    from enseignant.models import lister_tous_enseignants
    from directeur.models import JOURS_SEMAINE

    return render(request, "directeur/creneau_form.html", {
        "cours": lister_tous_cours_actifs(),
        "enseignants": lister_tous_enseignants(),
        "salles": lister_salles(),
        "jours": JOURS_SEMAINE,
        "types": ["Cours", "TD", "TP", "Examen"],
    })


@login_required
@role_requis("DIRECTEUR")
def modifier_creneau(request, creneau_id):
    """Modifier un créneau EDT"""
    from directeur.models import EmploiDuTemps
    creneau = get_object_or_404(EmploiDuTemps, pk=creneau_id)

    if request.method == "POST":
        from directeur.models import verifier_conflits_edt

        creneau.cours_id = int(request.POST.get("cours_id"))
        creneau.enseignant_id = int(request.POST.get("enseignant_id"))
        creneau.salle_id = int(request.POST.get("salle_id"))
        creneau.jour = request.POST.get("jour")
        creneau.heure_debut = dt_time.fromisoformat(request.POST.get("heure_debut"))
        creneau.heure_fin = dt_time.fromisoformat(request.POST.get("heure_fin"))
        creneau.type_creneau = request.POST.get("type_creneau", "Cours")

        conflits = verifier_conflits_edt(
            creneau.cours_id, creneau.enseignant_id, creneau.salle_id,
            creneau.jour, creneau.heure_debut, creneau.heure_fin, exclure_id=creneau.pk,
        )
        if conflits:
            messages.error(request, f"Conflits: {', '.join(conflits)}")
        else:
            creneau.save()
            from super_admin.models import creer_log_audit
            creer_log_audit(request, "MODIFICATION_EDT", "emploi_du_temps", creneau.pk)
            messages.success(request, "Créneau modifié.")
            return redirect("directeur:edt")

    from gestion1.models import lister_tous_cours_actifs, lister_salles
    from enseignant.models import lister_tous_enseignants
    from directeur.models import JOURS_SEMAINE

    return render(request, "directeur/creneau_form.html", {
        "creneau": creneau,
        "cours": lister_tous_cours_actifs(),
        "enseignants": lister_tous_enseignants(),
        "salles": lister_salles(),
        "jours": JOURS_SEMAINE,
        "types": ["Cours", "TD", "TP", "Examen"],
    })


@login_required
@role_requis("DIRECTEUR")
def supprimer_creneau(request, creneau_id):
    """Supprimer un créneau EDT"""
    from directeur.models import EmploiDuTemps
    creneau = get_object_or_404(EmploiDuTemps, pk=creneau_id)
    creneau.est_actif = False
    creneau.save()
    messages.success(request, "Créneau supprimé.")
    return redirect("directeur:edt")


@login_required
@role_requis("DIRECTEUR")
def generer_edt(request):
    """Générer l'EDT automatiquement à partir des disponibilités"""
    if request.method == "POST":
        filiere_id = int(request.POST.get("filiere_id"))
        from directeur.models import generer_edt_auto
        resultats = generer_edt_auto(filiere_id)

        if resultats["crees"]:
            messages.success(request, f"{resultats['crees']} créneau(x) généré(s).")
        if resultats["erreurs"]:
            for err in resultats["erreurs"]:
                messages.warning(request, err)

        return redirect("directeur:edt")

    from gestion1.models import lister_filieres_actives
    return render(request, "directeur/generer_edt.html", {
        "filieres": lister_filieres_actives(),
    })


# ============================================================
# DISPONIBILITÉS ENSEIGNANTS
# ============================================================

@login_required
@role_requis("DIRECTEUR")
def disponibilites_enseignants(request):
    """Saisir/voir les disponibilités de tous les enseignants"""
    from enseignant.models import Enseignant, DisponibiliteEnseignant, JOURS_SEMAINE

    enseignant_id = request.GET.get("enseignant_id")
    enseignants = Enseignant.objects.select_related("id_user").all()
    disponibilites = []

    if enseignant_id:
        disponibilites = DisponibiliteEnseignant.objects.filter(
            enseignant_id=enseignant_id
        ).order_by("jour", "heure_debut")

    if request.method == "POST":
        ens_id = int(request.POST.get("enseignant_id"))
        jour = request.POST.get("jour")
        heure_debut = dt_time.fromisoformat(request.POST.get("heure_debut"))
        heure_fin = dt_time.fromisoformat(request.POST.get("heure_fin"))
        est_dispo = request.POST.get("est_disponible") == "on"

        DisponibiliteEnseignant.objects.create(
            enseignant_id=ens_id, jour=jour,
            heure_debut=heure_debut, heure_fin=heure_fin,
            est_disponible=est_dispo,
        )
        messages.success(request, "Disponibilité enregistrée.")
        return redirect(f"{request.path}?enseignant_id={ens_id}")

    return render(request, "directeur/disponibilites.html", {
        "enseignants": enseignants,
        "disponibilites": disponibilites,
        "enseignant_id": enseignant_id,
        "jours": JOURS_SEMAINE,
    })


# ============================================================
# RAPPORTS
# ============================================================

@login_required
@role_requis("DIRECTEUR")
def rapports(request):
    """Rapports pédagogiques (performance, effectifs, absences, synthèse)"""
    type_rapport = request.GET.get("type", "")
    format_export = request.GET.get("export", "pdf")

    if type_rapport == "performance":
        from gestion1.models import Filiere
        from gestion2.models import calculer_moyenne_etudiant
        from etudiant.models import Etudiant

        filieres = Filiere.objects.filter(est_active=True)
        colonnes = ["Filière", "Niveau", "Nb Étudiants", "Moyenne Générale"]
        donnees = []
        for f in filieres:
            etudiants = Etudiant.objects.filter(filiere=f)
            moyennes = [calculer_moyenne_etudiant(e.pk) for e in etudiants]
            moyennes = [m for m in moyennes if m is not None]
            moy_gen = round(sum(moyennes) / len(moyennes), 2) if moyennes else "-"
            donnees.append([f.nom_filiere, f.niveau, etudiants.count(), moy_gen])

        if format_export == "excel":
            return exporter_excel("Performance par Filière", colonnes, donnees, "performance")
        return exporter_pdf("Performance par Filière", colonnes, donnees, "performance")

    elif type_rapport == "effectifs":
        from accounts.models import Utilisateur
        colonnes = ["Rôle", "Effectif", "Actifs", "Inactifs"]
        donnees = []
        for code, label in Utilisateur.ROLE_CHOICES:
            total = Utilisateur.objects.filter(role=code).count()
            actifs = Utilisateur.objects.filter(role=code, est_actif=True).count()
            donnees.append([label, total, actifs, total - actifs])

        if format_export == "excel":
            return exporter_excel("Rapport des Effectifs", colonnes, donnees, "effectifs")
        return exporter_pdf("Rapport des Effectifs", colonnes, donnees, "effectifs")

    elif type_rapport == "absences":
        from gestion3.models import detecter_absences_critiques
        from django.conf import settings
        alertes = detecter_absences_critiques(settings.SEUIL_ABSENCE_CRITIQUE)
        colonnes = ["Matricule", "Nom", "Prénom", "Filière", "Taux (%)", "Absences", "Total"]
        donnees = [
            [a["matricule"], a["nom"], a["prenom"], a["filiere"], a["taux"], a["absences"], a["total"]]
            for a in alertes
        ]
        if format_export == "excel":
            return exporter_excel("Étudiants Absents", colonnes, donnees, "absences")
        return exporter_pdf("Étudiants Absents", colonnes, donnees, "absences")

    return render(request, "directeur/rapports.html")


# ============================================================
# GESTION UTILISATEURS (hors SUPER_ADMIN)
# ============================================================

@login_required
@role_requis("DIRECTEUR")
def liste_utilisateurs(request):
    """Liste des utilisateurs (hors SUPER_ADMIN)"""
    utilisateurs = Utilisateur.objects.exclude(role="SUPER_ADMIN").order_by("role", "nom")
    return render(request, "directeur/utilisateurs.html", {"utilisateurs": utilisateurs})


@login_required
@role_requis("DIRECTEUR")
def reinitialiser_mdp_directeur(request, user_id):
    """Le directeur peut réinitialiser un mot de passe"""
    user = get_object_or_404(Utilisateur, pk=user_id)
    if user.role == "SUPER_ADMIN":
        messages.error(request, "Impossible de modifier un Super Admin.")
        return redirect("directeur:utilisateurs")

    from accounts.models import generer_mot_de_passe
    from django.contrib.auth.hashers import make_password

    nouveau_mdp = generer_mot_de_passe()
    user.password = make_password(nouveau_mdp)
    user.save(update_fields=["password"])
    messages.success(request, f"Nouveau mot de passe pour {user.nom_complet}: {nouveau_mdp}")
    return redirect("directeur:utilisateurs")
