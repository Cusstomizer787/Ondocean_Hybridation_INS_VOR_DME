"""
Script de test rapide pour valider les imports

Execute ce script pour verifier que tous les modules sont correctement installes
et que les imports fonctionnent.
"""

import sys

print("Test des imports...")
print("=" * 60)

try:
    import numpy as np
    print("[OK] numpy importe")
except ImportError as e:
    print(f"[ERREUR] numpy: {e}")
    sys.exit(1)

try:
    import scipy
    print("[OK] scipy importe")
except ImportError as e:
    print(f"[ERREUR] scipy: {e}")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    print("[OK] matplotlib importe")
except ImportError as e:
    print(f"[ERREUR] matplotlib: {e}")
    sys.exit(1)

try:
    from parametres import *
    print("[OK] parametres importe")
except ImportError as e:
    print(f"[ERREUR] parametres: {e}")
    sys.exit(1)

try:
    from modeles_dynamique import *
    print("[OK] modeles_dynamique importe")
except ImportError as e:
    print(f"[ERREUR] modeles_dynamique: {e}")
    sys.exit(1)

try:
    from stations_sol import *
    print("[OK] stations_sol importe")
except ImportError as e:
    print(f"[ERREUR] stations_sol: {e}")
    sys.exit(1)

try:
    from generateur_trajectoire import *
    print("[OK] generateur_trajectoire importe")
except ImportError as e:
    print(f"[ERREUR] generateur_trajectoire: {e}")
    sys.exit(1)

try:
    from simulateur_ins import *
    print("[OK] simulateur_ins importe")
except ImportError as e:
    print(f"[ERREUR] simulateur_ins: {e}")
    sys.exit(1)

try:
    from ekf import *
    print("[OK] ekf importe")
except ImportError as e:
    print(f"[ERREUR] ekf: {e}")
    sys.exit(1)

try:
    from metriques import *
    print("[OK] metriques importe")
except ImportError as e:
    print(f"[ERREUR] metriques: {e}")
    sys.exit(1)

try:
    from visualisation import *
    print("[OK] visualisation importe")
except ImportError as e:
    print(f"[ERREUR] visualisation: {e}")
    sys.exit(1)

print("=" * 60)
print("[SUCCESS] Tous les imports sont fonctionnels")
print("\nTest de chargement des parametres...")

try:
    params_sim, params_ins, params_vor_dme, params_ekf = charger_parametres_defaut()
    print(f"[OK] Parametres charges")
    print(f"  - Duree simulation: {params_sim.duree_simulation} s")
    print(f"  - Frequence IMU: {1.0/params_sim.dt_imu} Hz")
    
    stations = creer_stations_sol()
    print(f"[OK] {len(stations)} stations creees")
    
    print("\n[SUCCESS] Configuration validee")
    print("\nVous pouvez maintenant executer le notebook simulation_ins_vor_dme.ipynb")
    
except Exception as e:
    print(f"[ERREUR] Probleme lors du chargement: {e}")
    sys.exit(1)
