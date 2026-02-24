import os
import sys
import django

sys.path.insert(0, "c:/Users/orsin/OneDrive/Desktop/UIST-2ITS/uist-2its")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import Utilisateur
from django.contrib.auth.hashers import make_password

# Créer le compte Communication
comm_config = {
    "matricule": "COM-2026-001",
    "password": "communication123",
    "nom": "Service",
    "prenom": "Communication",
    "role": "COMMUNICATION",
}

print("Creating Communication user...")
try:
    user, created = Utilisateur.objects.get_or_create(
        matricule=comm_config["matricule"],
        defaults={
            "nom": comm_config["nom"],
            "prenom": comm_config["prenom"],
            "role": comm_config["role"],
            "password": make_password(comm_config["password"]),
            "est_actif": True,
        },
    )
    if created:
        print(f"Created: {comm_config['matricule']} -> {comm_config['password']}")
    else:
        user.password = make_password(comm_config["password"])
        user.est_actif = True
        user.save()
        print(f"Updated: {comm_config['matricule']} -> {comm_config['password']}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== COMPTE COMMUNICATION ===")
print(f"Matricule: {comm_config['matricule']}")
print(f"Mot de passe: {comm_config['password']}")
print("===========================")
