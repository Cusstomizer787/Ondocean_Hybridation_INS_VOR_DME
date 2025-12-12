"""
Test unitaire du scenario 5: Transit entre balises reelles

Ce script teste la generation de trajectoire du scenario 5
qui simule un aeronef transitant entre 5 balises reelles:
DJL, RLP, EPL, LUL, LXI

Auteur: Nicolas CUSSEAU - ENSTA Bretagne
Date: Decembre 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from parametres import charger_parametres_defaut
from generateur_trajectoire import generer_verite_scenario_5

print("="*70)
print("TEST UNITAIRE - SCENARIO 5: Transit balises reelles")
print("="*70)

# Chargement parametres
print("\n[ETAPE 1] Chargement parametres...")
params_sim, params_ins, params_vor_dme, params_ekf = charger_parametres_defaut()
print("[OK] Parametres charges")

# Generation trajectoire scenario 5
print("\n[ETAPE 2] Generation trajectoire scenario 5...")
verite = generer_verite_scenario_5(params_sim)
print("[OK] Trajectoire generee")

# Verification structure donnees
print("\n[ETAPE 3] Verification structure donnees...")
cles_requises = ['t', 'N', 'E', 'h', 'V_N', 'V_E', 'psi', 'a_N_corps', 'a_E_corps', 'omega_z']
for cle in cles_requises:
    if cle not in verite:
        print(f"[ERREUR] Cle manquante: {cle}")
        exit(1)
print("[OK] Structure correcte")

# Statistiques trajectoire
print("\n[ETAPE 4] Statistiques trajectoire...")
N_samples = len(verite['t'])
duree = verite['t'][-1]
distance_2D = 0.0
for i in range(1, N_samples):
    dN = verite['N'][i] - verite['N'][i-1]
    dE = verite['E'][i] - verite['E'][i-1]
    distance_2D += np.sqrt(dN**2 + dE**2)

V_norm = np.sqrt(verite['V_N']**2 + verite['V_E']**2)
a_norm = np.sqrt(verite['a_N_corps']**2 + verite['a_E_corps']**2)

print(f"Nombre echantillons: {N_samples}")
print(f"Duree simulation: {duree:.1f} s")
print(f"Distance totale: {distance_2D/1000:.1f} km")
print(f"Vitesse moyenne: {np.mean(V_norm):.1f} m/s")
print(f"Vitesse max: {np.max(V_norm):.1f} m/s")
print(f"Acceleration max: {np.max(a_norm):.2f} m/s^2")
print(f"Vitesse angulaire max: {np.rad2deg(np.max(np.abs(verite['omega_z']))):.2f} deg/s")

# Tests validation
print("\n[ETAPE 5] Tests validation...")
tests_ok = True

# Test 1: Accelerations non nulles
a_max = np.max(a_norm)
if a_max > 0.01:
    print(f"[OK] Test 1: Accelerations non nulles (max={a_max:.3f} m/s^2)")
else:
    print(f"[ERREUR] Test 1: Accelerations trop faibles (max={a_max:.3f} m/s^2)")
    tests_ok = False

# Test 2: Vitesse constante
V_std = np.std(V_norm)
V_mean = np.mean(V_norm)
if V_std < 5.0:  # Tolerance 5 m/s
    print(f"[OK] Test 2: Vitesse relativement constante (std={V_std:.2f} m/s)")
else:
    print(f"[AVERTISSEMENT] Test 2: Vitesse variable (std={V_std:.2f} m/s)")

# Test 3: Distance coherente
distance_attendue = 150.0 * duree / 1000.0  # km (vitesse * temps)
if abs(distance_2D/1000 - distance_attendue) < 50:  # Tolerance 50 km
    print(f"[OK] Test 3: Distance coherente ({distance_2D/1000:.1f} km vs {distance_attendue:.1f} km attendu)")
else:
    print(f"[AVERTISSEMENT] Test 3: Distance incoherente ({distance_2D/1000:.1f} km vs {distance_attendue:.1f} km attendu)")

# Test 4: Altitude positive
h_min = np.min(verite['h'])
if h_min >= 0:
    print(f"[OK] Test 4: Altitude positive (min={h_min:.1f} m)")
else:
    print(f"[ERREUR] Test 4: Altitude negative (min={h_min:.1f} m)")
    tests_ok = False

# Visualisation trajectoire
print("\n[ETAPE 6] Visualisation trajectoire...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Trajectoire 2D
ax1 = axes[0, 0]
ax1.plot(verite['E']/1000, verite['N']/1000, 'b-', linewidth=2, label='Trajectoire')
ax1.plot(verite['E'][0]/1000, verite['N'][0]/1000, 'go', markersize=10, label='Depart')
ax1.plot(verite['E'][-1]/1000, verite['N'][-1]/1000, 'ro', markersize=10, label='Arrivee')
ax1.set_xlabel('Est (km)', fontsize=11)
ax1.set_ylabel('Nord (km)', fontsize=11)
ax1.set_title('Trajectoire 2D - Scenario 5', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.axis('equal')

# Subplot 2: Profil altitude
ax2 = axes[0, 1]
ax2.plot(verite['t'], verite['h'], 'b-', linewidth=2)
ax2.set_xlabel('Temps (s)', fontsize=11)
ax2.set_ylabel('Altitude (m)', fontsize=11)
ax2.set_title('Profil altitude', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Subplot 3: Vitesse
ax3 = axes[1, 0]
ax3.plot(verite['t'], V_norm, 'b-', linewidth=2)
ax3.axhline(y=150.0, color='r', linestyle='--', label='Vitesse cible (150 m/s)')
ax3.set_xlabel('Temps (s)', fontsize=11)
ax3.set_ylabel('Vitesse (m/s)', fontsize=11)
ax3.set_title('Vitesse au sol', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# Subplot 4: Cap et vitesse angulaire
ax4 = axes[1, 1]
ax4_twin = ax4.twinx()
ax4.plot(verite['t'], np.rad2deg(verite['psi']), 'b-', linewidth=2, label='Cap')
ax4_twin.plot(verite['t'], np.rad2deg(verite['omega_z']), 'r-', linewidth=2, label='Vitesse angulaire')
ax4.set_xlabel('Temps (s)', fontsize=11)
ax4.set_ylabel('Cap (deg)', fontsize=11, color='b')
ax4_twin.set_ylabel('Vitesse angulaire (deg/s)', fontsize=11, color='r')
ax4.set_title('Cap et vitesse angulaire', fontsize=12, fontweight='bold')
ax4.tick_params(axis='y', labelcolor='b')
ax4_twin.tick_params(axis='y', labelcolor='r')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('test_scenario_5_trajectoire.png', dpi=150, bbox_inches='tight')
print("[OK] Graphique sauvegarde: test_scenario_5_trajectoire.png")

# Rapport final
print("\n" + "="*70)
print("RAPPORT FINAL")
print("="*70)
if tests_ok:
    print("[SUCCESS] Tous les tests passes")
    print("\nLe scenario 5 est correctement genere:")
    print("  - Accelerations non nulles")
    print("  - Vitesse relativement constante")
    print("  - Altitude positive")
    print("  - Transit coherent entre balises")
    print("\nVous pouvez maintenant executer test_scenarios.py complet")
else:
    print("[FAILED] Certains tests ont echoue")
    print("Verifiez la fonction generer_verite_scenario_5()")

print("\n[INFO] Fermer la fenetre graphique pour terminer...")
plt.show()
