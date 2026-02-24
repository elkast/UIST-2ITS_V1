"""
Vues Super Admin - Gestion globale, audit, rapports.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Count
from accounts.decorators import role_requis
from accounts.models import Utilisateur, generer_matricule, generer_mot_de_passe
from accounts.exports import exporter_pdf, exporter_excel
from super_admin.models import AuditLog, creer_log_audit


@login_required
@role_requis("SUPER_ADMIN")
def dashboard(request):
    """Tableau de bord Super Admin"""
    stats_roles = Utilisateur.objects.values("role").annotate(total=Count("id")).order_by("role")
    total_users = Utilisateur.objects.count()
    logs_recents = AuditLog.objects.all()[:10]
    connexions_jour = AuditLog.objects.filter(
        action="CONNEXION",
        date_action__date=__import__("datetime").datetime.now().date(),
    ).count()

    return render(request, "super_admin/dashboard.html", {
        "stats_roles": stats_roles,
        "total_users": total_users,
        "logs_recents": logs_recents,
        "connexions_jour": connexions_jour,
    })


@login_required
@role_requis("SUPER_ADMIN")
def liste_utilisateurs(request):
    """Liste de tous les utilisateurs avec filtre par rôle"""
    role_filtre = request.GET.get("role", "")
    query = Utilisateur.objects.all()
    if role_filtre:
        query = query.filter(role=role_filtre)

    # Export
    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Matricule", "Nom", "Prénom", "Rôle", "Email", "Actif"]
        donnees = [
            [u.matricule, u.nom, u.prenom, u.get_role_display(), u.email or "-", "Oui" if u.est_actif else "Non"]
            for u in query
        ]
        creer_log_audit(request, "EXPORT", "utilisateurs", details=f"Export {format_export}")
        if format_export == "pdf":
            return exporter_pdf("Liste des Utilisateurs", colonnes, donnees, "utilisateurs")
        return exporter_excel("Liste des Utilisateurs", colonnes, donnees, "utilisateurs")

    roles = Utilisateur.ROLE_CHOICES
    return render(request, "super_admin/utilisateurs.html", {
        "utilisateurs": query.order_by("role", "nom"),
        "roles": roles,
        "role_filtre": role_filtre,
    })


@login_required
@role_requis("SUPER_ADMIN")
def nouvel_utilisateur(request):
    """Créer un utilisateur (tous rôles)"""
    if request.method == "POST":
        role = request.POST.get("role")
        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        email = request.POST.get("email", "").strip()

        matricule = generer_matricule(role)
        mot_de_passe = generer_mot_de_passe()

        try:
            user = Utilisateur.objects.create(
                username=matricule,
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                email=email or "",
                password=make_password(mot_de_passe),
                role=role,
            )

            # Créer le profil associé si nécessaire
            _creer_profil_role(user, request.POST)

            creer_log_audit(request, "CREATION_USER", "utilisateurs", user.pk,
                            f"Création {role}: {nom} {prenom}")

            messages.success(
                request,
                f"Utilisateur créé ! Matricule: {matricule} | Mot de passe: {mot_de_passe}"
            )
            return redirect("super_admin:utilisateurs")

        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")

    return render(request, "super_admin/utilisateur_form.html", {
        "roles": Utilisateur.ROLE_CHOICES,
    })


@login_required
@role_requis("SUPER_ADMIN")
def modifier_utilisateur(request, user_id):
    """Modifier un utilisateur"""
    user = get_object_or_404(Utilisateur, pk=user_id)

    if request.method == "POST":
        user.nom = request.POST.get("nom", user.nom).strip()
        user.prenom = request.POST.get("prenom", user.prenom).strip()
        user.email = request.POST.get("email", "").strip()
        user.est_actif = request.POST.get("est_actif") == "on"
        user.save()

        creer_log_audit(request, "MODIFICATION_USER", "utilisateurs", user.pk,
                        f"Modification de {user.nom_complet}")
        messages.success(request, "Utilisateur modifié.")
        return redirect("super_admin:utilisateurs")

    return render(request, "super_admin/utilisateur_edit.html", {"utilisateur": user})


@login_required
@role_requis("SUPER_ADMIN")
def reinitialiser_mot_de_passe(request, user_id):
    """Réinitialiser le mot de passe d'un utilisateur"""
    user = get_object_or_404(Utilisateur, pk=user_id)
    nouveau_mdp = generer_mot_de_passe()
    user.password = make_password(nouveau_mdp)
    user.save(update_fields=["password"])

    creer_log_audit(request, "MODIFICATION_USER", "utilisateurs", user.pk,
                    f"Réinitialisation mot de passe de {user.nom_complet}")
    messages.success(request, f"Nouveau mot de passe pour {user.nom_complet}: {nouveau_mdp}")
    return redirect("super_admin:utilisateurs")


@login_required
@role_requis("SUPER_ADMIN")
def desactiver_utilisateur(request, user_id):
    """Désactiver/Réactiver un utilisateur"""
    user = get_object_or_404(Utilisateur, pk=user_id)
    user.est_actif = not user.est_actif
    user.is_active = user.est_actif
    user.save(update_fields=["est_actif", "is_active"])

    action = "réactivé" if user.est_actif else "désactivé"
    creer_log_audit(request, "MODIFICATION_USER", "utilisateurs", user.pk,
                    f"Utilisateur {action}: {user.nom_complet}")
    messages.success(request, f"Utilisateur {action}.")
    return redirect("super_admin:utilisateurs")


@login_required
@role_requis("SUPER_ADMIN")
def audit(request):
    """Consultation des logs d'audit"""
    logs = AuditLog.objects.all()[:100]

    format_export = request.GET.get("export", "")
    if format_export in ("pdf", "excel"):
        colonnes = ["Date", "Utilisateur", "Action", "Table", "Détails"]
        donnees = [
            [l.date_action.strftime("%d/%m/%Y %H:%M"), l.nom_utilisateur, l.get_action_display(), l.table_affectee, l.details[:80]]
            for l in logs
        ]
        if format_export == "pdf":
            return exporter_pdf("Journal d'Audit", colonnes, donnees, "audit")
        return exporter_excel("Journal d'Audit", colonnes, donnees, "audit")

    return render(request, "super_admin/audit.html", {"logs": logs})


@login_required
@role_requis("SUPER_ADMIN")
def rapports(request):
    """Rapports téléchargeables"""
    type_rapport = request.GET.get("type", "")
    format_export = request.GET.get("export", "pdf")

    if type_rapport == "etudiants":
        from etudiant.models import Etudiant
        etudiants = Etudiant.objects.select_related("id_user", "filiere").all()
        colonnes = ["Matricule", "Nom", "Prénom", "Filière", "Niveau"]
        donnees = [[e.id_user.matricule, e.id_user.nom, e.id_user.prenom, e.filiere.nom_filiere, e.filiere.niveau] for e in etudiants]
        titre = "Rapport des Étudiants Inscrits"
        nom = "rapport_etudiants"

    elif type_rapport == "enseignants":
        from enseignant.models import Enseignant
        enseignants = Enseignant.objects.select_related("id_user").all()
        colonnes = ["Matricule", "Nom", "Prénom", "Spécialité", "Téléphone"]
        donnees = [[e.id_user.matricule, e.id_user.nom, e.id_user.prenom, e.specialite, e.telephone] for e in enseignants]
        titre = "Rapport des Enseignants"
        nom = "rapport_enseignants"

    elif type_rapport == "parents":
        from parent.models import Parent
        parents = Parent.objects.select_related("id_user").all()
        colonnes = ["Matricule", "Nom", "Prénom", "Téléphone", "Tél. secondaire"]
        donnees = [[p.id_user.matricule, p.id_user.nom, p.id_user.prenom, p.telephone, p.telephone_secondaire] for p in parents]
        titre = "Rapport des Parents"
        nom = "rapport_parents"

    elif type_rapport == "liaisons":
        from parent.models import LiaisonParentEtudiant
        liaisons = LiaisonParentEtudiant.objects.select_related("parent__id_user", "etudiant__id_user").all()
        colonnes = ["Parent", "Lien", "Étudiant", "Matricule Étudiant"]
        donnees = [[f"{l.parent.id_user.nom} {l.parent.id_user.prenom}", l.lien_parente, f"{l.etudiant.id_user.nom} {l.etudiant.id_user.prenom}", l.etudiant.id_user.matricule] for l in liaisons]
        titre = "Rapport Liaisons Parent-Étudiant"
        nom = "rapport_liaisons"
    else:
        return render(request, "super_admin/rapports.html")

    creer_log_audit(request, "EXPORT", details=f"Export rapport {type_rapport}")
    if format_export == "excel":
        return exporter_excel(titre, colonnes, donnees, nom)
    return exporter_pdf(titre, colonnes, donnees, nom)


def _creer_profil_role(user, post_data):
    """Crée le profil associé au rôle de l'utilisateur"""
    if user.role == "ENSEIGNANT":
        from enseignant.models import Enseignant
        Enseignant.objects.create(
            id_user=user,
            specialite=post_data.get("specialite", ""),
            telephone=post_data.get("telephone", ""),
        )
    elif user.role == "ETUDIANT":
        from etudiant.models import Etudiant
        filiere_id = post_data.get("filiere_id")
        if filiere_id:
            Etudiant.objects.create(id_user=user, filiere_id=filiere_id)
    elif user.role == "PARENT":
        from parent.models import Parent
        Parent.objects.create(
            id_user=user,
            telephone=post_data.get("telephone", ""),
            telephone_secondaire=post_data.get("telephone_secondaire", ""),
        )
