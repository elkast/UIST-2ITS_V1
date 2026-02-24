# UIST-2ITS — Système de Gestion Académique

Université Internationale des Sciences et Technologies — Plateforme complète de gestion académique.

## Architecture

```
uist-2its/
├── accounts/          # Auth, matricules, notifications, API mobile
├── super_admin/       # Gestion globale, audit, rapports
├── directeur/         # EDT CRUD, validation notes, rapports
├── gestion1/          # Logistique: salles, filières, cours, assignations
├── gestion2/          # Scolarité: étudiants, parents, notes, import Excel
├── gestion3/          # Suivi: présences, alertes, listes enseignants
├── enseignant/        # EDT perso, disponibilités, notes
├── etudiant/          # Dashboard, EDT, notes validées, profil
├── parent/            # Suivi enfants: EDT, notes, assiduité
├── core/              # Settings Django, URLs principales
├── templates/         # Templates Django (thème vert Bootstrap 5)
├── static/            # CSS, images, JS
└── requirements.txt
```

##  Rôles

| Rôle | Accès |
|------|-------|
| **Super Admin** | CRUD utilisateurs, audit, rapports globaux (PDF/Excel) |
| **Directeur** | EDT (CRUD + génération auto), validation notes, rapports pédagogiques |
| **Gestion 1** | Salles (équipements + verrouillage), filières, cours, assignation enseignant |
| **Gestion 2** | Étudiants, parents, notes (saisie + import Excel), liaisons parent-étudiant |
| **Gestion 3** | Présences, alertes assiduité, liste enseignants par filière |
| **Enseignant** | EDT perso, disponibilités, consultation des notes |
| **Étudiant** | Dashboard (moyenne + rang), EDT temps réel, notes validées, profil |
| **Parent** | Suivi enfants: EDT, notes, assiduité, notifications |

##  Installation locale

```bash
# 1. Cloner et entrer dans le projet
cd uist-2its

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env avec vos paramètres (DATABASE_URL, SECRET_KEY)

# 5. Migrations
python manage.py makemigrations accounts super_admin directeur gestion1 gestion2 gestion3 enseignant etudiant parent
python manage.py migrate

# 6. Créer un super utilisateur
python manage.py createsuperuser

# 7. Collecte des fichiers statiques
python manage.py collectstatic --noinput

# 8. Lancer le serveur
python manage.py runserver
```

## 🌐 Déploiement sur Render

1. **Base de données**: Créer une base PostgreSQL sur [Neon](https://neon.tech)
2. **Variables d'environnement** sur Render :
   - `DATABASE_URL` : URL PostgreSQL de Neon
   - `SECRET_KEY` : Clé secrète Django (générer avec `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DEBUG` : `False`
   - `ALLOWED_HOSTS` : `votre-app.onrender.com`
3. **Build Command** : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. **Start Command** : `gunicorn core.wsgi:application`

##  Exports

- **PDF** : Rapports avec en-tête vert UIST (ReportLab)
- **Excel** : Tableaux formatés avec en-tête vert (openpyxl)
- Disponibles sur toutes les listes : étudiants, enseignants, parents, notes, EDT, présences, audit

##  API Mobile (JSON)

| Endpoint | Description |
|----------|-------------|
| `GET /api/edt/<filiere_id>/` | EDT d'une filière |
| `GET /api/notes/<etudiant_id>/` | Notes validées d'un étudiant |
| `GET /api/presences/<etudiant_id>/` | Taux de présence |
| `GET /api/notifications/` | Notifications utilisateur |
| `GET /api/filieres/` | Liste des filières actives |
| `GET /api/parents/recherche/?q=nom` | Recherche de parents |

## Stack Technique

- **Backend** : Django 5.2
- **BDD** : PostgreSQL (Neon) / SQLite (dev)
- **CSS** : Bootstrap 5 + Thème vert personnalisé
- **PDF** : ReportLab
- **Excel** : openpyxl
- **Déploiement** : Render + WhiteNoise
