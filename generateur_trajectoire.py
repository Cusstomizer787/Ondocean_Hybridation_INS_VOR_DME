"""
Module de generation de trajectoires verite

Contient 4 scenarios de trajectoire pour la simulation.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import os


def generer_verite_scenario_1(params_sim):
    """
    Scenario 1: Approche radiale avec profil de vitesse realiste
    
    Description:
    - Phase 1 (0-100s): Acceleration 50->100 m/s
    - Phase 2 (100-500s): Croisiere 100 m/s vers station
    - Phase 3 (500-600s): Deceleration 100->50 m/s
    - Phase 4 (600-663s): Virage 180 deg coordonne
    - Phase 5 (663-763s): Acceleration 50->100 m/s
    - Phase 6 (763-1163s): Croisiere 100 m/s retour
    - Phase 7 (1163-1200s): Deceleration 100->50 m/s
    - Altitude constante 3000 m
    
    Parametres:
    -----------
    params_sim : ParametresSimulation
        Parametres de simulation
    
    Retour:
    -------
    dict
        Trajectoire verite avec cles: t, N, E, h, V_N, V_E, psi, 
        a_N_corps, a_E_corps, omega_z
    """
    dt = params_sim.dt_imu
    T = params_sim.duree_simulation
    h_vol = params_sim.altitude_vol
    
    N_samples = int(T / dt) + 1
    t = np.linspace(0, T, N_samples)
    
    # Initialisation tableaux
    N = np.zeros(N_samples)
    E = np.zeros(N_samples)
    h = np.ones(N_samples) * h_vol
    V_N = np.zeros(N_samples)
    V_E = np.zeros(N_samples)
    psi = np.zeros(N_samples)
    a_N_corps = np.zeros(N_samples)
    a_E_corps = np.zeros(N_samples)
    omega_z = np.zeros(N_samples)
    
    # Position et vitesse initiales
    N[0] = 60000.0
    E[0] = 0.0
    V_N[0] = -50.0  # Vitesse initiale vers Sud
    V_E[0] = 0.0
    psi[0] = np.pi  # Cap 180 deg
    
    # Parametres
    a_accel = 0.5  # m/s^2
    a_decel = -0.5  # m/s^2
    R_virage = 1000.0  # m
    
    # Phases temporelles
    t1 = 100.0   # Fin acceleration
    t2 = 500.0   # Fin croisiere
    t3 = 600.0   # Fin deceleration
    t4 = 662.8   # Fin virage (pi*R/V avec V=50)
    t5 = 762.8   # Fin acceleration retour
    t6 = 1162.8  # Fin croisiere retour
    
    for i in range(1, N_samples):
        ti = t[i]
        
        # Phase 1: Acceleration
        if ti <= t1:
            V_mag = 50.0 + a_accel * ti
            psi[i] = np.pi
            a_N_corps[i] = a_accel
            
        # Phase 2: Croisiere approche
        elif ti <= t2:
            V_mag = 100.0
            psi[i] = np.pi
            a_N_corps[i] = 0.0
            
        # Phase 3: Deceleration
        elif ti <= t3:
            V_mag = 100.0 + a_decel * (ti - t2)
            psi[i] = np.pi
            a_N_corps[i] = a_decel
            
        # Phase 4: Virage 180 deg
        elif ti <= t4:
            V_mag = 50.0
            dt_virage = ti - t3
            omega = V_mag / R_virage
            psi[i] = np.pi + omega * dt_virage
            omega_z[i] = omega
            a_E_corps[i] = -V_mag**2 / R_virage  # Centripete vers gauche
            
        # Phase 5: Acceleration retour
        elif ti <= t5:
            V_mag = 50.0 + a_accel * (ti - t4)
            psi[i] = 0.0
            a_N_corps[i] = a_accel
            
        # Phase 6: Croisiere retour
        elif ti <= t6:
            V_mag = 100.0
            psi[i] = 0.0
            a_N_corps[i] = 0.0
            
        # Phase 7: Deceleration finale
        else:
            V_mag = 100.0 - 1.25 * (ti - t6)
            V_mag = max(V_mag, 50.0)
            psi[i] = 0.0
            a_N_corps[i] = -1.25
        
        # Normalisation cap
        psi[i] = np.mod(psi[i] + np.pi, 2.0 * np.pi) - np.pi
        
        # Vitesses NED
        V_N[i] = V_mag * np.cos(psi[i])
        V_E[i] = V_mag * np.sin(psi[i])
        
        # Integration position
        N[i] = N[i-1] + V_N[i] * dt
        E[i] = E[i-1] + V_E[i] * dt
    
    verite = {
        't': t,
        'N': N,
        'E': E,
        'h': h,
        'V_N': V_N,
        'V_E': V_E,
        'psi': psi,
        'a_N_corps': a_N_corps,
        'a_E_corps': a_E_corps,
        'omega_z': omega_z
    }
    
    return verite


def generer_verite_scenario_2(params_sim):
    """
    Scenario 2: Arc circulaire autour de station 1
    
    Description:
    - Trajectoire circulaire rayon 50 km autour de (0, 0)
    - Virage coordonne a DROITE (sens horaire, omega < 0)
    - Vitesse tangentielle 150 m/s
    - Altitude constante 3000 m
    - Acceleration centripete vers interieur (droite)
    
    Parametres:
    -----------
    params_sim : ParametresSimulation
        Parametres de simulation
    
    Retour:
    -------
    dict
        Trajectoire verite
    """
    dt = params_sim.dt_imu
    T = params_sim.duree_simulation
    h_vol = params_sim.altitude_vol
    
    N_samples = int(T / dt) + 1
    t = np.linspace(0, T, N_samples)
    
    # Parametres cercle
    R = 50000.0  # Rayon (m)
    V_mag = 150.0  # Vitesse tangentielle (m/s)
    omega = -V_mag / R  # Vitesse angulaire NEGATIVE (virage droite, sens horaire)
    
    # Position circulaire (virage droite)
    theta = omega * t
    N = R * np.cos(theta)
    E = R * np.sin(theta)
    h = np.ones(N_samples) * h_vol
    
    # Vitesse (tangentielle)
    V_N = -R * omega * np.sin(theta)
    V_E = R * omega * np.cos(theta)
    
    # Cap (tangent au cercle, virage droite)
    psi = theta - np.pi / 2.0
    psi = np.mod(psi + np.pi, 2.0 * np.pi) - np.pi
    
    # Acceleration centripete
    a_c = V_mag**2 / R  # Magnitude acceleration centripete
    
    # Dans le repere corps (avion), acceleration pointe vers interieur du virage (DROITE)
    # Repere corps: x vers avant, y vers droite
    # Virage droite: acceleration centripete vers droite donc a_E_corps POSITIF
    a_N_corps = np.zeros(N_samples)  # Pas d'acceleration longitudinale
    a_E_corps = a_c * np.ones(N_samples)  # Acceleration laterale vers droite (virage coordonne)
    
    # Vitesse angulaire constante
    omega_z = omega * np.ones(N_samples)
    
    verite = {
        't': t,
        'N': N,
        'E': E,
        'h': h,
        'V_N': V_N,
        'V_E': V_E,
        'psi': psi,
        'a_N_corps': a_N_corps,
        'a_E_corps': a_E_corps,
        'omega_z': omega_z
    }
    
    return verite


def generer_verite_scenario_3(params_sim):
    """
    Scenario 3: Transit multi-stations avec virages coordonnes
    
    Description:
    - Trajectoire polygonale passant pres des 3 stations
    - Waypoints: (-20000,-20000) -> (0,0) -> (80000,0) -> (40000,60000) -> (40000,80000)
    - Vitesse croisiere: 120 m/s
    - Virages coordonnes (R=2000m) entre segments
    - Phases acceleration/deceleration sur segments rectilignes
    - Altitude constante 3000 m
    
    Parametres:
    -----------
    params_sim : ParametresSimulation
        Parametres de simulation
    
    Retour:
    -------
    dict
        Trajectoire verite
    """
    dt = params_sim.dt_imu
    T = params_sim.duree_simulation
    h_vol = params_sim.altitude_vol
    
    N_samples = int(T / dt) + 1
    t = np.linspace(0, T, N_samples)
    
    # Initialisation
    N = np.zeros(N_samples)
    E = np.zeros(N_samples)
    h = np.ones(N_samples) * h_vol
    V_N = np.zeros(N_samples)
    V_E = np.zeros(N_samples)
    psi = np.zeros(N_samples)
    a_N_corps = np.zeros(N_samples)
    a_E_corps = np.zeros(N_samples)
    omega_z = np.zeros(N_samples)
    
    # Waypoints [N, E]
    waypoints = np.array([
        [-20000.0, -20000.0],  # Depart
        [0.0, 0.0],            # Station 1
        [80000.0, 0.0],        # Station 2
        [40000.0, 60000.0],    # Station 3
        [40000.0, 80000.0]     # Arrivee
    ])
    
    # Parametres vol
    V_croisiere = 120.0  # m/s
    V_virage = 80.0  # m/s (vitesse reduite en virage)
    R_virage = 2000.0  # m
    a_accel = 0.8  # m/s^2
    a_decel = -0.8  # m/s^2
    
    # Calcul caps entre waypoints
    caps = []
    for i in range(len(waypoints) - 1):
        dN = waypoints[i+1, 0] - waypoints[i, 0]
        dE = waypoints[i+1, 1] - waypoints[i, 1]
        cap = np.arctan2(dE, dN)
        caps.append(cap)
    
    # Construction profil temporel simplifie
    # Pour ce scenario, on utilise vitesse constante avec virages
    idx = 0
    current_pos = waypoints[0].copy()
    current_cap = caps[0]
    current_V = V_virage
    
    N[0] = current_pos[0]
    E[0] = current_pos[1]
    psi[0] = current_cap
    V_N[0] = current_V * np.cos(current_cap)
    V_E[0] = current_V * np.sin(current_cap)
    
    wp_idx = 0  # Waypoint cible
    en_virage = False
    cap_debut_virage = 0.0
    cap_fin_virage = 0.0
    
    for i in range(1, N_samples):
        ti = t[i]
        
        # Distance au waypoint cible
        if wp_idx < len(waypoints) - 1:
            dist_wp = np.sqrt((N[i-1] - waypoints[wp_idx+1, 0])**2 + 
                             (E[i-1] - waypoints[wp_idx+1, 1])**2)
            
            # Si proche du waypoint, passer au suivant
            if dist_wp < 500.0 and not en_virage:
                wp_idx += 1
                if wp_idx < len(waypoints) - 1:
                    # Demarrer virage vers nouveau cap
                    en_virage = True
                    cap_debut_virage = psi[i-1]
                    cap_fin_virage = caps[wp_idx]
        
        # Gestion virage
        if en_virage:
            # Calcul changement cap necessaire
            delta_cap = cap_fin_virage - cap_debut_virage
            delta_cap = np.mod(delta_cap + np.pi, 2.0 * np.pi) - np.pi
            
            # Vitesse angulaire
            omega = V_virage / R_virage
            if delta_cap < 0:
                omega = -omega
            
            # Increment cap
            psi[i] = psi[i-1] + omega * dt
            psi[i] = np.mod(psi[i] + np.pi, 2.0 * np.pi) - np.pi
            
            # Acceleration centripete
            a_E_corps[i] = -np.sign(delta_cap) * V_virage**2 / R_virage
            omega_z[i] = omega
            
            current_V = V_virage
            
            # Verifier fin virage
            delta_actuel = psi[i] - cap_debut_virage
            delta_actuel = np.mod(delta_actuel + np.pi, 2.0 * np.pi) - np.pi
            if np.abs(delta_actuel) >= np.abs(delta_cap) * 0.95:
                en_virage = False
                psi[i] = cap_fin_virage
        else:
            # Vol rectiligne
            if wp_idx < len(waypoints) - 1:
                psi[i] = caps[wp_idx]
            else:
                psi[i] = psi[i-1]
            
            # Acceleration vers vitesse croisiere
            if current_V < V_croisiere - 1.0:
                a_N_corps[i] = a_accel
                current_V = min(current_V + a_accel * dt, V_croisiere)
            elif current_V > V_virage + 1.0 and dist_wp < 3000.0:
                a_N_corps[i] = a_decel
                current_V = max(current_V + a_decel * dt, V_virage)
            else:
                a_N_corps[i] = 0.0
        
        # Vitesses NED
        V_N[i] = current_V * np.cos(psi[i])
        V_E[i] = current_V * np.sin(psi[i])
        
        # Integration position
        N[i] = N[i-1] + V_N[i] * dt
        E[i] = E[i-1] + V_E[i] * dt
    
    verite = {
        't': t,
        'N': N,
        'E': E,
        'h': h,
        'V_N': V_N,
        'V_E': V_E,
        'psi': psi,
        'a_N_corps': a_N_corps,
        'a_E_corps': a_E_corps,
        'omega_z': omega_z
    }
    
    return verite


def calculer_mesures_imu_verite(verite):
    """
    Calcule les mesures IMU ideales a partir de la trajectoire verite
    
    Note: Pour les scenarios avec accelerations nulles, cette fonction
    retourne les valeurs deja presentes dans verite.
    
    Parametres:
    -----------
    verite : dict
        Trajectoire verite
    
    Retour:
    -------
    dict
        Mesures IMU ideales (sans bruit)
    """
    mesures = {
        'a_N_corps': verite['a_N_corps'],
        'a_E_corps': verite['a_E_corps'],
        'omega_z': verite['omega_z']
    }
    
    return mesures


def generer_verite_scenario_4(params_sim, fichier_data='data.csv'):
    """
    Scenario 4: Trajectoire reelle extraite de donnees GPS
    
    Description:
    - Charge donnees reelles depuis data.csv
    - Convertit coordonnees geographiques (lon, lat, alt) en NED
    - Interpole pour correspondre au pas de temps dt_imu
    - Calcule vitesses et accelerations par derivation numerique
    - Altitude variable selon profil reel
    
    Parametres:
    -----------
    params_sim : ParametresSimulation
        Parametres de simulation
    fichier_data : str
        Chemin vers fichier CSV (defaut: 'data.csv')
    
    Retour:
    -------
    dict
        Trajectoire verite avec cles: t, N, E, h, V_N, V_E, psi,
        a_N_corps, a_E_corps, omega_z
    """
    # Verification existence fichier
    if not os.path.exists(fichier_data):
        raise FileNotFoundError(f"Fichier {fichier_data} introuvable")
    
    # Chargement donnees CSV
    print(f"[INFO] Chargement donnees depuis {fichier_data}")
    df = pd.read_csv(fichier_data)
    
    # Validation colonnes requises
    colonnes_requises = ['missn_time', '__lon__deg', '__lat__deg', '__altftmsl', '__mag_comp']
    for col in colonnes_requises:
        if col not in df.columns:
            raise ValueError(f"Colonne {col} manquante dans {fichier_data}")
    
    # Extraction donnees
    t_data = df['missn_time'].values
    lon_data = df['__lon__deg'].values
    lat_data = df['__lat__deg'].values
    alt_ft_data = df['__altftmsl'].values
    psi_mag_data = df['__mag_comp'].values
    
    # Verification duree
    duree_data = t_data[-1] - t_data[0]
    print(f"[INFO] Duree donnees: {duree_data:.1f}s")
    
    if duree_data < params_sim.duree_simulation:
        print(f"[AVERTISSEMENT] Duree donnees ({duree_data:.0f}s) < duree simulation ({params_sim.duree_simulation:.0f}s)")
        print("[INFO] Ajustement de la duree de simulation aux donnees disponibles")
        T = duree_data
    else:
        T = params_sim.duree_simulation
    
    # Constantes conversion
    rayon_terre = 6371000.0
    ft_to_m = 0.3048
    
    # Point de reference (premiere position)
    lat_ref = np.radians(lat_data[0])
    lon_ref = np.radians(lon_data[0])
    
    # Conversion geographique -> NED
    N_data = rayon_terre * (np.radians(lat_data) - lat_ref)
    E_data = rayon_terre * (np.radians(lon_data) - lon_ref) * np.cos(lat_ref)
    h_data = alt_ft_data * ft_to_m
    
    # Conversion cap magnetique en radians
    psi_data = np.radians(psi_mag_data)
    
    # Normalisation angles
    psi_data = np.mod(psi_data + np.pi, 2.0 * np.pi) - np.pi
    
    # Grille temporelle uniforme
    dt = params_sim.dt_imu
    N_samples = int(T / dt) + 1
    t = np.linspace(t_data[0], t_data[0] + T, N_samples)
    
    # Interpolation
    print(f"[INFO] Interpolation sur grille uniforme (dt={dt}s, N={N_samples})")
    interp_N = interp1d(t_data, N_data, kind='cubic', fill_value='extrapolate')
    interp_E = interp1d(t_data, E_data, kind='cubic', fill_value='extrapolate')
    interp_h = interp1d(t_data, h_data, kind='cubic', fill_value='extrapolate')
    
    # Interpolation speciale pour les angles (gestion discontinuites)
    psi_unwrap = np.unwrap(psi_data)
    interp_psi = interp1d(t_data, psi_unwrap, kind='cubic', fill_value='extrapolate')
    
    N = interp_N(t)
    E = interp_E(t)
    h = interp_h(t)
    psi = interp_psi(t)
    psi = np.mod(psi + np.pi, 2.0 * np.pi) - np.pi
    
    # Initialisation tableaux
    V_N = np.zeros(N_samples)
    V_E = np.zeros(N_samples)
    a_N_ned = np.zeros(N_samples)
    a_E_ned = np.zeros(N_samples)
    a_N_corps = np.zeros(N_samples)
    a_E_corps = np.zeros(N_samples)
    omega_z = np.zeros(N_samples)
    
    # Calcul vitesses par derivation numerique
    for i in range(1, N_samples):
        V_N[i] = (N[i] - N[i-1]) / dt
        V_E[i] = (E[i] - E[i-1]) / dt
    
    # Premiere valeur (copie de la deuxieme)
    V_N[0] = V_N[1]
    V_E[0] = V_E[1]
    
    # Lissage vitesses (reduction bruit derivation)
    if N_samples > 11:
        V_N = savgol_filter(V_N, window_length=11, polyorder=3)
        V_E = savgol_filter(V_E, window_length=11, polyorder=3)
    
    # Calcul accelerations NED
    for i in range(1, N_samples):
        a_N_ned[i] = (V_N[i] - V_N[i-1]) / dt
        a_E_ned[i] = (V_E[i] - V_E[i-1]) / dt
    
    a_N_ned[0] = a_N_ned[1]
    a_E_ned[0] = a_E_ned[1]
    
    # Lissage accelerations
    if N_samples > 11:
        a_N_ned = savgol_filter(a_N_ned, window_length=11, polyorder=3)
        a_E_ned = savgol_filter(a_E_ned, window_length=11, polyorder=3)
    
    # Transformation NED -> corps
    for i in range(N_samples):
        a_N_corps[i] = a_N_ned[i] * np.cos(psi[i]) + a_E_ned[i] * np.sin(psi[i])
        a_E_corps[i] = -a_N_ned[i] * np.sin(psi[i]) + a_E_ned[i] * np.cos(psi[i])
    
    # Calcul vitesse angulaire
    for i in range(1, N_samples):
        delta_psi = psi[i] - psi[i-1]
        delta_psi = np.mod(delta_psi + np.pi, 2.0 * np.pi) - np.pi
        omega_z[i] = delta_psi / dt
    
    omega_z[0] = omega_z[1]
    
    # Lissage omega_z
    if N_samples > 11:
        omega_z = savgol_filter(omega_z, window_length=11, polyorder=3)
    
    # Ajustement temps pour commencer a 0
    t = t - t[0]
    
    print(f"[SUCCESS] Scenario 4 genere: {N_samples} echantillons sur {T:.1f}s")
    print(f"[INFO] Vitesse max: {np.max(np.sqrt(V_N**2 + V_E**2)):.1f} m/s")
    print(f"[INFO] Acceleration max: {np.max(np.sqrt(a_N_corps**2 + a_E_corps**2)):.2f} m/s^2")
    print(f"[INFO] Vitesse angulaire max: {np.rad2deg(np.max(np.abs(omega_z))):.2f} deg/s")
    
    verite = {
        't': t,
        'N': N,
        'E': E,
        'h': h,
        'V_N': V_N,
        'V_E': V_E,
        'psi': psi,
        'a_N_corps': a_N_corps,
        'a_E_corps': a_E_corps,
        'omega_z': omega_z
    }
    
    return verite


def generer_verite_scenario_5(params_sim):
    """
    Scenario 5: Transit entre balises de radionavigation reelles
    
    Description:
    - Vol entre 5 balises reelles francaises (DJL, RLP, LXI, EPL, LUL)
    - Coordonnees geographiques converties en NED
    - Trajectoire avec virages coordonnes entre waypoints
    - Altitude variable selon balises
    - Vitesse constante 150 m/s
    
    Parametres:
    -----------
    params_sim : ParametresSimulation
        Parametres de simulation
    
    Retour:
    -------
    dict
        Trajectoire verite avec cles: t, N, E, h, V_N, V_E, psi,
        a_N_corps, a_E_corps, omega_z
    """
    
    # Definition balises reelles
    balises = {
        "DJL": {"nom": "Dole", "type": "VORDME", "lat": 47.16148, "lon": 5.05504, "alt": 200.0},
        "RLP": {"nom": "Reims", "type": "VORDME", "lat": 47.54227, "lon": 5.14570, "alt": 200.0},
        "LXI": {"nom": "Luxeuil", "type": "DME", "lat": 47.46594, "lon": 6.21256, "alt": 200.0},
        "EPL": {"nom": "Epinal", "type": "VOR", "lat": 48.19042, "lon": 6.03339, "alt": 200.0},
        "LUL": {"nom": "Lure", "type": "VOR", "lat": 47.41178, "lon": 6.17441, "alt": 200.0},
    }
    
    # Sequence de transit (ordre geographique logique)
    sequence = ["DJL", "RLP", "EPL", "LUL", "LXI"]
    
    # Conversion GEO -> NED (point de reference: premiere balise DJL)
    lat_ref = np.radians(balises["DJL"]["lat"])
    lon_ref = np.radians(balises["DJL"]["lon"])
    rayon_terre = 6371000.0
    
    waypoints = []
    for code in sequence:
        lat = np.radians(balises[code]["lat"])
        lon = np.radians(balises[code]["lon"])
        alt = balises[code]["alt"]
        
        N = rayon_terre * (lat - lat_ref)
        E = rayon_terre * (lon - lon_ref) * np.cos(lat_ref)
        h = alt
        
        waypoints.append({"code": code, "N": N, "E": E, "h": h})
    
    # Parametres trajectoire
    V = 150.0  # m/s vitesse constante
    rayon_virage = 5000.0  # m rayon virage coordonne
    
    # Generation segments entre waypoints
    segments = []
    
    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i + 1]
        
        # Segment rectiligne
        dN = wp2["N"] - wp1["N"]
        dE = wp2["E"] - wp1["E"]
        distance = np.sqrt(dN**2 + dE**2)
        cap = np.arctan2(dE, dN)
        duree_segment = distance / V
        
        segments.append({
            "type": "ligne",
            "start_N": wp1["N"],
            "start_E": wp1["E"],
            "start_h": wp1["h"],
            "end_N": wp2["N"],
            "end_E": wp2["E"],
            "end_h": wp2["h"],
            "cap": cap,
            "distance": distance,
            "duree": duree_segment
        })
        
        # Si pas dernier segment: ajouter virage
        if i < len(waypoints) - 2:
            wp3 = waypoints[i + 2]
            dN_next = wp3["N"] - wp2["N"]
            dE_next = wp3["E"] - wp2["E"]
            cap_next = np.arctan2(dE_next, dN_next)
            
            delta_cap = cap_next - cap
            # Normalisation angle [-pi, pi]
            delta_cap = np.mod(delta_cap + np.pi, 2.0 * np.pi) - np.pi
            
            # Duree virage
            omega_virage = V / rayon_virage  # rad/s
            duree_virage = abs(delta_cap) / omega_virage
            
            segments.append({
                "type": "virage",
                "centre_N": wp2["N"],
                "centre_E": wp2["E"],
                "centre_h": wp2["h"],
                "cap_initial": cap,
                "cap_final": cap_next,
                "delta_cap": delta_cap,
                "rayon": rayon_virage,
                "duree": duree_virage,
                "omega": omega_virage * np.sign(delta_cap)
            })
    
    # Calcul duree totale
    duree_totale = sum([seg["duree"] for seg in segments])
    if duree_totale > params_sim.duree_simulation:
        print(f"[AVERTISSEMENT] Duree trajectoire ({duree_totale:.0f}s) > duree simulation ({params_sim.duree_simulation:.0f}s)")
        T = params_sim.duree_simulation
    else:
        T = duree_totale
    
    dt = params_sim.dt_imu
    N_samples = int(T / dt) + 1
    t = np.linspace(0, T, N_samples)
    
    # Initialisation tableaux trajectoire
    N_traj = np.zeros(N_samples)
    E_traj = np.zeros(N_samples)
    h_traj = np.zeros(N_samples)
    psi_traj = np.zeros(N_samples)
    V_N = np.zeros(N_samples)
    V_E = np.zeros(N_samples)
    omega_z = np.zeros(N_samples)
    
    # Generation echantillons trajectoire
    t_cumul = 0.0
    seg_idx = 0
    
    for k in range(N_samples):
        t_k = t[k]
        
        # Trouver segment actif
        while seg_idx < len(segments) and t_k >= t_cumul + segments[seg_idx]["duree"]:
            t_cumul += segments[seg_idx]["duree"]
            seg_idx += 1
        
        if seg_idx >= len(segments):
            seg_idx = len(segments) - 1
        
        seg = segments[seg_idx]
        t_seg = t_k - t_cumul  # temps dans segment
        
        if seg["type"] == "ligne":
            # Mouvement rectiligne
            if seg["duree"] > 0:
                alpha = t_seg / seg["duree"]
            else:
                alpha = 1.0
            alpha = np.clip(alpha, 0.0, 1.0)
            
            N_traj[k] = seg["start_N"] + alpha * (seg["end_N"] - seg["start_N"])
            E_traj[k] = seg["start_E"] + alpha * (seg["end_E"] - seg["start_E"])
            h_traj[k] = seg["start_h"] + alpha * (seg["end_h"] - seg["start_h"])
            psi_traj[k] = seg["cap"]
            V_N[k] = V * np.cos(seg["cap"])
            V_E[k] = V * np.sin(seg["cap"])
            omega_z[k] = 0.0
            
        else:  # virage
            # Mouvement circulaire
            angle_parcouru = seg["omega"] * t_seg
            cap_actuel = seg["cap_initial"] + angle_parcouru
            
            # Position sur cercle (centre + rayon * rotation)
            angle_position = cap_actuel - np.pi / 2 * np.sign(seg["omega"])
            N_traj[k] = seg["centre_N"] + seg["rayon"] * np.cos(angle_position)
            E_traj[k] = seg["centre_E"] + seg["rayon"] * np.sin(angle_position)
            h_traj[k] = seg["centre_h"]
            psi_traj[k] = cap_actuel
            V_N[k] = V * np.cos(cap_actuel)
            V_E[k] = V * np.sin(cap_actuel)
            omega_z[k] = seg["omega"]
    
    # Calcul accelerations NED
    a_N_ned = np.zeros(N_samples)
    a_E_ned = np.zeros(N_samples)
    
    for i in range(1, N_samples):
        a_N_ned[i] = (V_N[i] - V_N[i-1]) / dt
        a_E_ned[i] = (V_E[i] - V_E[i-1]) / dt
    a_N_ned[0] = a_N_ned[1]
    a_E_ned[0] = a_E_ned[1]
    
    # Transformation NED -> corps
    a_N_corps = np.zeros(N_samples)
    a_E_corps = np.zeros(N_samples)
    
    for i in range(N_samples):
        a_N_corps[i] = a_N_ned[i] * np.cos(psi_traj[i]) + a_E_ned[i] * np.sin(psi_traj[i])
        a_E_corps[i] = -a_N_ned[i] * np.sin(psi_traj[i]) + a_E_ned[i] * np.cos(psi_traj[i])
    
    # Statistiques
    distance_totale = sum([s["distance"] for s in segments if s["type"] == "ligne"])
    nb_virages = sum([1 for s in segments if s["type"] == "virage"])
    
    print(f"[SUCCESS] Scenario 5 genere: {N_samples} echantillons sur {T:.1f}s")
    print(f"[INFO] Balises: {' -> '.join(sequence)}")
    print(f"[INFO] Distance totale: {distance_totale/1000:.1f} km")
    print(f"[INFO] Vitesse: {V:.1f} m/s ({V*3.6:.0f} km/h)")
    print(f"[INFO] Nombre virages: {nb_virages}")
    print(f"[INFO] Vitesse max: {np.max(np.sqrt(V_N**2 + V_E**2)):.1f} m/s")
    print(f"[INFO] Acceleration max: {np.max(np.sqrt(a_N_corps**2 + a_E_corps**2)):.2f} m/s^2")
    print(f"[INFO] Vitesse angulaire max: {np.rad2deg(np.max(np.abs(omega_z))):.2f} deg/s")
    
    verite = {
        't': t,
        'N': N_traj,
        'E': E_traj,
        'h': h_traj,
        'V_N': V_N,
        'V_E': V_E,
        'psi': psi_traj,
        'a_N_corps': a_N_corps,
        'a_E_corps': a_E_corps,
        'omega_z': omega_z
    }
    
    return verite
