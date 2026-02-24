"""
Vues Gestion 2 - Scolarité & Évaluations.
Étudiants, Parents, Notes, Liaisons, Import Excel, Export.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from accounts.decorators import role_requis
from accounts.models import Utilisateur, generer_matricule, generer_mot_de_passe, creer_notification
from accounts.exports import exporter_pdf, exporter_excel, importer_excel_notes
from gestion1.models import lister_filieres_actives, lister_tous_cours_actifs


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def dashboard(request):
    from etudiant.models import Etudiant
    from parent.models import Parent
    from gestion2.models import Note

    return render(request, "gestion2/dashboard.html", {
        "total_etudiants": Etudiant.objects.count(),
        "total_parents": Parent.objects.count(),
        "notes_en_attente": Note.objects.filter(statut_validation="En attente").count(),
        "filieres": lister_filieres_actives(),
    })


# ============================================================
# ÉTUDIANTS
# ============================================================

@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def liste_etudiants(request):
    from etudiant.models import Etudiant

    filiere_id = request.GET.get("filiere_id")
    niveau = request.GET.get("niveau")
    query = Etudiant.objects.select_related("id_user", "filiere")

    if filiere_id:
        query = query.filter(filiere_id=filiere_id)
    if niveau:
        query = query.filter(filiere__niveau=niveau)

    etudiants = query.order_by("id_user__nom")

    # Export
    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Matricule", "Nom", "Prénom", "Filière", "Niveau"]
        donnees = [[e.id_user.matricule, e.id_user.nom, e.id_user.prenom, e.filiere.nom_filiere, e.filiere.niveau] for e in etudiants]
        if format_export == "excel":
            return exporter_excel("Liste des Étudiants", colonnes, donnees, "etudiants")
        return exporter_pdf("Liste des Étudiants", colonnes, donnees, "etudiants")

    return render(request, "gestion2/etudiants.html", {
        "etudiants": etudiants,
        "filieres": lister_filieres_actives(),
        "filiere_id": filiere_id,
    })


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def nouvel_etudiant(request):
    """Créer un étudiant (email non obligatoire, mot de passe visible)"""
    if request.method == "POST":
        from etudiant.models import Etudiant
        from django.db import IntegrityError

        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        email = request.POST.get("email", "").strip()  # Non obligatoire
        filiere_id = int(request.POST.get("filiere_id"))

        matricule = generer_matricule("ETUDIANT")
        mot_de_passe = generer_mot_de_passe()

        try:
            user = Utilisateur.objects.create(
                username=matricule, matricule=matricule,
                nom=nom, prenom=prenom, email=email,
                password=make_password(mot_de_passe), role="ETUDIANT",
            )
            Etudiant.objects.create(id_user=user, filiere_id=filiere_id)

            messages.success(
                request,
                f"Étudiant créé ! Matricule: {matricule} | Mot de passe: {mot_de_passe}"
            )
            return redirect("gestion2:etudiants")

        except IntegrityError:
            messages.error(request, "Erreur de création (données dupliquées).")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")

    return render(request, "gestion2/etudiant_form.html", {
        "filieres": lister_filieres_actives(),
    })


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def modifier_etudiant(request, etudiant_id):
    """Modifier un étudiant (filière, niveau, infos)"""
    from etudiant.models import Etudiant
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)

    if request.method == "POST":
        etudiant.id_user.nom = request.POST.get("nom", etudiant.id_user.nom).strip()
        etudiant.id_user.prenom = request.POST.get("prenom", etudiant.id_user.prenom).strip()
        etudiant.id_user.email = request.POST.get("email", "").strip()
        etudiant.id_user.save()

        nouvelle_filiere = request.POST.get("filiere_id")
        if nouvelle_filiere:
            etudiant.filiere_id = int(nouvelle_filiere)
        etudiant.adresse = request.POST.get("adresse", "").strip()
        etudiant.save()

        messages.success(request, "Étudiant modifié.")
        return redirect("gestion2:etudiants")

    return render(request, "gestion2/etudiant_form.html", {
        "etudiant": etudiant,
        "filieres": lister_filieres_actives(),
    })


# ============================================================
# PARENTS
# ============================================================

@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def liste_parents(request):
    from parent.models import Parent
    parents = Parent.objects.select_related("id_user").order_by("id_user__nom")

    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Matricule", "Nom", "Prénom", "Téléphone", "Tél. secondaire"]
        donnees = [[p.id_user.matricule, p.id_user.nom, p.id_user.prenom, p.telephone, p.telephone_secondaire] for p in parents]
        if format_export == "excel":
            return exporter_excel("Liste des Parents", colonnes, donnees, "parents")
        return exporter_pdf("Liste des Parents", colonnes, donnees, "parents")

    return render(request, "gestion2/parents.html", {"parents": parents})


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def nouveau_parent(request):
    """Créer un parent (email non obligatoire, 2 numéros de téléphone)"""
    if request.method == "POST":
        from parent.models import Parent

        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        email = request.POST.get("email", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        telephone_secondaire = request.POST.get("telephone_secondaire", "").strip()

        matricule = generer_matricule("PARENT")
        mot_de_passe = generer_mot_de_passe()

        try:
            user = Utilisateur.objects.create(
                username=matricule, matricule=matricule,
                nom=nom, prenom=prenom, email=email,
                password=make_password(mot_de_passe), role="PARENT",
            )
            Parent.objects.create(
                id_user=user, telephone=telephone,
                telephone_secondaire=telephone_secondaire,
            )
            messages.success(
                request,
                f"Parent créé ! Matricule: {matricule} | Mot de passe: {mot_de_passe}"
            )
            return redirect("gestion2:parents")

        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")

    return render(request, "gestion2/parent_form.html")


# ============================================================
# NOTES
# ============================================================

@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def saisie_notes(request):
    if request.method == "POST":
        from gestion2.models import Note

        etudiant_id = int(request.POST.get("etudiant_id"))
        cours_id = int(request.POST.get("cours_id"))
        valeur_note = float(request.POST.get("valeur_note"))
        type_eval = request.POST.get("type_evaluation", "Examen")

        if not (0 <= valeur_note <= 20):
            messages.error(request, "La note doit être entre 0 et 20.")
        else:
            Note.objects.create(
                id_etudiant_id=etudiant_id, id_cours_id=cours_id,
                valeur_note=valeur_note, type_evaluation=type_eval,
            )
            messages.success(request, "Note enregistrée (en attente de validation).")
        return redirect("gestion2:saisie_notes")

    from gestion2.models import Note
    from etudiant.models import Etudiant

    notes_recentes = Note.objects.select_related("id_etudiant__id_user", "id_cours").order_by("-date_saisie")[:30]
    etudiants = Etudiant.objects.select_related("id_user").order_by("id_user__nom")

    return render(request, "gestion2/saisie_notes.html", {
        "notes": notes_recentes,
        "etudiants": etudiants,
        "cours": lister_tous_cours_actifs(),
        "types_eval": ["Examen", "Controle", "TP", "TD", "Projet", "Devoir"],
    })


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def import_notes(request):
    """Import de notes depuis un fichier Excel"""
    if request.method == "POST" and request.FILES.get("fichier_excel"):
        resultats = importer_excel_notes(request.FILES["fichier_excel"])

        if resultats["importees"]:
            messages.success(request, f"{resultats['importees']} note(s) importée(s).")

            # Notification au directeur
            directeur = Utilisateur.objects.filter(role="DIRECTEUR").first()
            if directeur:
                creer_notification(
                    directeur.pk, "VALIDATION_NOTE",
                    f"{resultats['importees']} notes importées",
                    "De nouvelles notes ont été importées et attendent votre validation.",
                )

            from super_admin.models import creer_log_audit
            creer_log_audit(request, "IMPORT_NOTES", "notes",
                            details=f"{resultats['importees']} notes importées")

        for erreur in resultats["erreurs"]:
            messages.warning(request, erreur)

        return redirect("gestion2:import_notes")

    return render(request, "gestion2/import_notes.html", {
        "filieres": lister_filieres_actives(),
    })


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def valider_et_notifier(request):
    """Valider les notes saisies et notifier le directeur"""
    if request.method == "POST":
        from gestion2.models import Note

        filiere_id = request.POST.get("filiere_id")
        cours_id = request.POST.get("cours_id")

        notes = Note.objects.filter(statut_validation="En attente")
        if filiere_id:
            notes = notes.filter(id_cours__filiere_id=filiere_id)
        if cours_id:
            notes = notes.filter(id_cours_id=cours_id)

        count = notes.count()

        # Notifier le directeur
        directeur = Utilisateur.objects.filter(role="DIRECTEUR").first()
        if directeur and count > 0:
            from gestion1.models import Cours
            cours_info = ""
            if cours_id:
                c = Cours.objects.filter(pk=cours_id).first()
                cours_info = f" en {c.libelle}" if c else ""

            creer_notification(
                directeur.pk, "VALIDATION_NOTE",
                f"{count} notes en attente de validation{cours_info}",
                f"Gestion 2 a soumis {count} notes pour validation. Veuillez les examiner.",
            )
            messages.success(request, f"Notification envoyée au directeur pour {count} note(s).")
        else:
            messages.info(request, "Aucune note à soumettre.")

    return redirect("gestion2:saisie_notes")


# ============================================================
# LIAISONS PARENT-ÉTUDIANT
# ============================================================

@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def liaisons(request):
    from parent.models import LiaisonParentEtudiant
    liaisons = LiaisonParentEtudiant.objects.select_related(
        "parent__id_user", "etudiant__id_user"
    ).all()
    return render(request, "gestion2/liaisons.html", {"liaisons": liaisons})


@login_required
@role_requis("GESTION_2", "DIRECTEUR")
def liaison_parent(request):
    """Créer une liaison parent-étudiant (avec recherche par nom)"""
    if request.method == "POST":
        from parent.models import LiaisonParentEtudiant

        parent_id = int(request.POST.get("parent_id"))
        etudiant_id = int(request.POST.get("etudiant_id"))
        lien = request.POST.get("lien_parente")

        try:
            LiaisonParentEtudiant.objects.create(
                parent_id=parent_id, etudiant_id=etudiant_id, lien_parente=lien,
            )
            messages.success(request, "Liaison créée.")
        except Exception:
            messages.error(request, "Cette liaison existe déjà.")

        return redirect("gestion2:liaisons")

    from parent.models import Parent
    from etudiant.models import Etudiant

    return render(request, "gestion2/liaison_parent.html", {
        "parents": Parent.objects.select_related("id_user").order_by("id_user__nom"),
        "etudiants": Etudiant.objects.select_related("id_user").order_by("id_user__nom"),
        "liens": ["Père", "Mère", "Tuteur", "Tutrice", "Autre"],
    })
