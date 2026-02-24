import os
import sys
import django

sys.path.insert(0, 'c:/Users/orsin/OneDrive/Desktop/UIST-2ITS/uist-2its')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Utilisateur
from django.contrib.auth.hashers import make_password

users_config = [
    {'matricule': 'SA-2026-5HJV', 'password': 'admin123', 'role': 'SUPER_ADMIN'},
    {'matricule': 'DIR-2026-1SXM', 'password': 'directeur123', 'role': 'DIRECTEUR'},
    {'matricule': 'G1-2026-L23C', 'password': 'gestion1123', 'role': 'GESTION_1'},
    {'matricule': 'G2-2026-EPRT', 'password': 'gestion2123', 'role': 'GESTION_2'},
    {'matricule': 'G3-2026-56WD', 'password': 'gestion3123', 'role': 'GESTION_3'},
    {'matricule': 'ENS-2026-TZMK', 'password': 'enseignant123', 'role': 'ENSEIGNANT'},
    {'matricule': 'ETU-2026-1K3B', 'password': 'etudiant123', 'role': 'ETUDIANT'},
    {'matricule': 'PAR-2026-CAH4', 'password': 'parent123', 'role': 'PARENT'},
]

print("Resetting passwords...")
for config in users_config:
    try:
        user = Utilisateur.objects.get(matricule=config['matricule'])
        user.password = make_password(config['password'])
        user.save()
        print(f"OK: {config['matricule']} -> {config['password']}")
    except Utilisateur.DoesNotExist:
        print(f"MISSING: {config['matricule']} not found")

print("\n" + "="*60)
print("COMPTES VALIDES - UIST-2ITS")
print("="*60)
for config in users_config:
    print(f"{config['role']:15} | {config['matricule']:15} | {config['password']}")
print("="*60)
