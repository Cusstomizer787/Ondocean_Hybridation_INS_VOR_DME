"""
Script de test automatise pour valider les scenarios corriges

Execute ce script pour verifier que les modifications generent bien
une derive INS observable et une amelioration EKF significative.

Etapes 15-20 du plan de correction.
"""

import numpy as np
import matplotlib.pyplot as plt
from parametres import *
from modeles_dynamique import *
from stations_sol import *
from generateur_trajectoire import *
from simulateur_ins import *
from ekf import *
from metriques import *

print("="*70)
print("TEST DES SCENARIOS CORRIGES")
print("="*70)

# Chargement parametres
params_sim, params_ins, params_vor_dme, params_ekf = charger_parametres_defaut()
stations = creer_stations_sol()

# Seed pour reproductibilite
np.random.seed(42)

# Tests pour chaque scenario
resultats = {}

for num_scenario in [1, 2, 3, 4]:
    print(f"\n{'='*70}")
    print(f"SCENARIO {num_scenario}")
    print(f"{'='*70}")
    
    # Generation trajectoire
    if num_scenario == 1:
        verite = generer_verite_scenario_1(params_sim)
        nom = "Approche radiale avec accelerations"
    elif num_scenario == 2:
        verite = generer_verite_scenario_2(params_sim)
        nom = "Arc circulaire"
    elif num_scenario == 3:
        verite = generer_verite_scenario_3(params_sim)
        nom = "Transit multi-stations avec virages"
    elif num_scenario == 4:
        verite = generer_verite_scenario_4(params_sim)
        nom = "Trajectoire reelle GPS"
    else:
        verite = generer_verite_scenario_5(params_sim)
        nom = "Transit balises reelles"
    
    print(f"\n[ETAPE 15-{num_scenario}] Test scenario {num_scenario}: {nom}")
    
    # Verification 1: Accelerations non nulles
    print("\n[VERIFICATION 1] Accelerations non nulles:")
    a_N_max = np.max(np.abs(verite['a_N_corps']))
    a_E_max = np.max(np.abs(verite['a_E_corps']))
    omega_max = np.max(np.abs(verite['omega_z']))
    
    print(f"  a_N_corps max: {a_N_max:.3f} m/s^2")
    print(f"  a_E_corps max: {a_E_max:.3f} m/s^2")
    print(f"  omega_z max: {np.rad2deg(omega_max):.3f} deg/s")
    
    if a_N_max > 0.1 or a_E_max > 0.1 or omega_max > 0.001:
        print("  [OK] Accelerations presentes")
        test_accel = True
    else:
        print("  [ERREUR] Accelerations quasi-nulles")
        test_accel = False
    
    # Generation mesures IMU
    mesures_imu = generer_mesures_imu_bruitees(verite, params_ins)
    
    # Etat initial avec erreurs
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
    
    # Simulation INS seule
    print("\n[VERIFICATION 2] Simulation INS seule:")
    traj_ins = integrer_ins_seule(mesures_imu, x0, params_sim, params_ins)
    
    # Calcul derive
    err_finale_ins = np.sqrt((traj_ins['N'][-1] - verite['N'][-1])**2 + 
                             (traj_ins['E'][-1] - verite['E'][-1])**2)
    
    print(f"  Erreur finale 2D: {err_finale_ins:.0f} m")
    
    if err_finale_ins > 500.0:
        print("  [OK] Derive INS significative (>500m)")
        test_derive = True
    else:
        print("  [ERREUR] Derive INS insuffisante (<500m)")
        test_derive = False
    
    # Simulation EKF (version simplifiee pour test rapide)
    print("\n[VERIFICATION 3] Simulation INS + EKF:")
    ekf = EKF(x0, params_ekf.P0, params_ins, params_vor_dme, params_ekf)
    
    # Reinitialisation timers
    for station in stations:
        station.prochain_temps_mesure = 1.0 / station.frequence_mesure
    
    N_samples = len(verite['t'])
    traj_ekf = {
        'N': np.zeros(N_samples),
        'E': np.zeros(N_samples)
    }
    
    for i, key in enumerate(['N', 'E']):
        traj_ekf[key][0] = ekf.x[i]
    
    n_updates = 0
    
    # Boucle EKF
    for k in range(1, N_samples):
        t = verite['t'][k]
        
        u_accel = np.array([mesures_imu['u_accel_N'][k-1], 
                           mesures_imu['u_accel_E'][k-1]])
        ekf.prediction(mesures_imu['u_gyro'][k-1], u_accel, params_sim.dt_imu)
        
        for station in stations:
            if t >= station.prochain_temps_mesure:
                if verifier_visibilite(ekf.x, station, params_vor_dme):
                    x_verite = np.array([verite['N'][k], verite['E'][k], 
                                        verite['h'][k], 0, 0, 0, 0, 0])
                    
                    if station.a_vor:
                        z_vor_vrai = modele_mesure_vor(x_verite, station)
                        z_vor = z_vor_vrai + np.random.randn() * params_vor_dme.vor_sigma
                        if ekf.update_vor(z_vor, station):
                            n_updates += 1
                    
                    if station.a_dme:
                        z_dme_vrai = modele_mesure_dme(x_verite, station)
                        z_dme = z_dme_vrai + np.random.randn() * params_vor_dme.dme_sigma
                        if ekf.update_dme(z_dme, station):
                            n_updates += 1
                
                station.prochain_temps_mesure += 1.0 / station.frequence_mesure
        
        traj_ekf['N'][k] = ekf.x[0]
        traj_ekf['E'][k] = ekf.x[1]
    
    err_finale_ekf = np.sqrt((traj_ekf['N'][-1] - verite['N'][-1])**2 + 
                             (traj_ekf['E'][-1] - verite['E'][-1])**2)
    
    print(f"  Erreur finale 2D: {err_finale_ekf:.0f} m")
    print(f"  Nombre updates acceptes: {n_updates}")
    
    # Verification amelioration
    print("\n[VERIFICATION 4] Amelioration EKF vs INS:")
    amelioration = (1 - err_finale_ekf / err_finale_ins) * 100
    print(f"  Amelioration: {amelioration:.1f}%")
    
    if amelioration > 50.0:
        print("  [OK] Amelioration significative (>50%)")
        test_amelioration = True
    elif amelioration > 0:
        print("  [AVERTISSEMENT] Amelioration faible ({amelioration:.1f}%)")
        test_amelioration = False
    else:
        print("  [ERREUR] EKF degrade les performances")
        test_amelioration = False
    
    # Stockage resultats
    resultats[num_scenario] = {
        'nom': nom,
        'test_accel': test_accel,
        'test_derive': test_derive,
        'test_amelioration': test_amelioration,
        'a_N_max': a_N_max,
        'a_E_max': a_E_max,
        'omega_max': omega_max,
        'err_ins': err_finale_ins,
        'err_ekf': err_finale_ekf,
        'amelioration': amelioration,
        'n_updates': n_updates
    }

# Rapport final
print(f"\n{'='*70}")
print("RAPPORT FINAL - VALIDATION SCENARIOS")
print(f"{'='*70}\n")

tous_ok = True

for num_scenario in [1, 2, 3, 4, 5]:
    res = resultats[num_scenario]
    print(f"Scenario {num_scenario}: {res['nom']}")
    print(f"  Accelerations: {'[OK]' if res['test_accel'] else '[FAILED]'}")
    print(f"  Derive INS: {'[OK]' if res['test_derive'] else '[FAILED]'} ({res['err_ins']:.0f}m)")
    print(f"  Amelioration EKF: {'[OK]' if res['test_amelioration'] else '[FAILED]'} ({res['amelioration']:.1f}%)")
    print(f"  Updates EKF: {res['n_updates']}")
    
    if not (res['test_accel'] and res['test_derive'] and res['test_amelioration']):
        tous_ok = False
    print()

print(f"{'='*70}")
if tous_ok:
    print("[SUCCESS] TOUS LES TESTS PASSES")
    print("\nLes scenarios corriges generent bien:")
    print("  - Des accelerations non nulles")
    print("  - Une derive INS observable")
    print("  - Une amelioration EKF significative (>50%)")
    print("\nVous pouvez maintenant executer le notebook complet.")
else:
    print("[FAILED] CERTAINS TESTS ONT ECHOUE")
    print("\nVerifier les scenarios qui ont echoue ci-dessus.")
    print("Consulter les messages d'erreur pour diagnostiquer le probleme.")

print(f"{'='*70}\n")

# Sauvegarde resultats
import json
with open('resultats_tests_scenarios.json', 'w') as f:
    # Conversion types numpy pour JSON
    resultats_json = {}
    for k, v in resultats.items():
        resultats_json[k] = {
            'nom': v['nom'],
            'test_accel': bool(v['test_accel']),
            'test_derive': bool(v['test_derive']),
            'test_amelioration': bool(v['test_amelioration']),
            'a_N_max': float(v['a_N_max']),
            'a_E_max': float(v['a_E_max']),
            'omega_max': float(v['omega_max']),
            'err_ins': float(v['err_ins']),
            'err_ekf': float(v['err_ekf']),
            'amelioration': float(v['amelioration']),
            'n_updates': int(v['n_updates'])
        }
    json.dump(resultats_json, f, indent=2)

print("Resultats sauvegardes dans: resultats_tests_scenarios.json")
