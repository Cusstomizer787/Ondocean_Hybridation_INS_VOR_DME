"""
Test rapide du CMKF apres correction
"""

import numpy as np
from parametres import *
from modeles_dynamique import *
from stations_sol import *
from generateur_trajectoire import *
from simulateur_ins import *

# Recharger le module CMKF
import importlib
import cmkf
importlib.reload(cmkf)
from cmkf import CMKF

print("[INFO] Test CMKF apres correction")
print("="*60)

# Chargement parametres
params_sim, params_ins, params_vor_dme, params_ekf = charger_parametres_defaut()
stations = creer_stations_sol()

# Generation scenario 3
verite = generer_verite_scenario_3(params_sim)
print(f"[OK] Scenario 3 genere")

# Generation mesures IMU
mesures_imu = generer_mesures_imu_bruitees(verite, params_ins)
print(f"[OK] Mesures IMU generees")

# Etat initial
np.random.seed(42)
err_N = np.random.randn() * 50.0
err_E = np.random.randn() * 50.0
err_V_N = np.random.randn() * 2.0
err_V_E = np.random.randn() * 2.0
err_psi = np.random.randn() * 0.0349
err_b_g = params_ins.gyro_biais_init * 0.5
err_b_a = params_ins.accel_biais_init * 0.5

x0 = np.array([
    verite['N'][0] + err_N,
    verite['E'][0] + err_E,
    verite['h'][0],
    verite['V_N'][0] + err_V_N,
    verite['V_E'][0] + err_V_E,
    verite['psi'][0] + err_psi,
    params_ins.gyro_biais_init + err_b_g,
    params_ins.accel_biais_init + err_b_a
])

# Initialisation CMKF
cmkf_test = CMKF(x0, params_ekf.P0, params_ins, params_vor_dme, params_ekf)

# Reinitialisation timers stations
for station in stations:
    station.prochain_temps_mesure = 1.0 / station.frequence_mesure

# Test sur premiers 10000 echantillons (100s)
N_samples_test = min(10000, len(verite['t']))

n_mesures_vor_acceptees = 0
n_mesures_vor_rejetees = 0
n_mesures_dme_acceptees = 0
n_mesures_dme_rejetees = 0

print(f"[INFO] Test sur {N_samples_test} echantillons...")

for k in range(1, N_samples_test):
    t = verite['t'][k]
    
    # Prediction CMKF
    u_accel = np.array([mesures_imu['u_accel_N'][k-1], mesures_imu['u_accel_E'][k-1]])
    cmkf_test.prediction(mesures_imu['u_gyro'][k-1], u_accel, params_sim.dt_imu)
    
    # Updates VOR/DME asynchrones
    for station in stations:
        if t >= station.prochain_temps_mesure:
            if verifier_visibilite(cmkf_test.x, station, params_vor_dme):
                x_verite = np.array([verite['N'][k], verite['E'][k], verite['h'][k], 
                                    0, 0, 0, 0, 0])
                
                if station.a_vor:
                    z_vor_vrai = modele_mesure_vor(x_verite, station)
                    z_vor = z_vor_vrai + np.random.randn() * params_vor_dme.vor_sigma + params_vor_dme.vor_biais
                    accepte = cmkf_test.update_vor(z_vor, station)
                    if accepte:
                        n_mesures_vor_acceptees += 1
                    else:
                        n_mesures_vor_rejetees += 1
                
                if station.a_dme:
                    z_dme_vrai = modele_mesure_dme(x_verite, station)
                    z_dme = z_dme_vrai + np.random.randn() * params_vor_dme.dme_sigma + params_vor_dme.dme_biais
                    accepte = cmkf_test.update_dme(z_dme, station)
                    if accepte:
                        n_mesures_dme_acceptees += 1
                    else:
                        n_mesures_dme_rejetees += 1
            
            station.prochain_temps_mesure += 1.0 / station.frequence_mesure
    
    cmkf_test.sauvegarder_etat(t)

# Resultats
print("="*60)
print("[RESULTATS]")
print(f"Mesures VOR: {n_mesures_vor_acceptees} acceptees, {n_mesures_vor_rejetees} rejetees")
print(f"Taux acceptation VOR: {100*n_mesures_vor_acceptees/(n_mesures_vor_acceptees+n_mesures_vor_rejetees):.1f}%")
print(f"Mesures DME: {n_mesures_dme_acceptees} acceptees, {n_mesures_dme_rejetees} rejetees")
print(f"Taux acceptation DME: {100*n_mesures_dme_acceptees/(n_mesures_dme_acceptees+n_mesures_dme_rejetees):.1f}%")

# Position finale
err_N_final = cmkf_test.x[0] - verite['N'][N_samples_test-1]
err_E_final = cmkf_test.x[1] - verite['E'][N_samples_test-1]
err_2D_final = np.sqrt(err_N_final**2 + err_E_final**2)

print(f"\nPosition CMKF: N={cmkf_test.x[0]:.0f} m, E={cmkf_test.x[1]:.0f} m")
print(f"Position verite: N={verite['N'][N_samples_test-1]:.0f} m, E={verite['E'][N_samples_test-1]:.0f} m")
print(f"Erreur 2D: {err_2D_final:.0f} m")
print("="*60)

# Comparaison attendue
print("\n[COMPARAISON]")
print("EKF (reference): VOR 99.8% acceptees, DME 100% acceptees")
print("CMKF avant fix: VOR 68% acceptees, DME 20% acceptees")
print(f"CMKF apres fix: VOR {100*n_mesures_vor_acceptees/(n_mesures_vor_acceptees+n_mesures_vor_rejetees):.1f}% acceptees, DME {100*n_mesures_dme_acceptees/(n_mesures_dme_acceptees+n_mesures_dme_rejetees):.1f}% acceptees")

if n_mesures_vor_acceptees/(n_mesures_vor_acceptees+n_mesures_vor_rejetees) > 0.95:
    print("\n[SUCCESS] Fix reussi! Taux d'acceptation normalise")
else:
    print("\n[FAILED] Probleme persiste, investigation supplementaire necessaire")
