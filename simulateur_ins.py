"""
Module de simulation INS

Contient les fonctions de generation de mesures IMU bruitees et
d'integration strapdown.
"""

import numpy as np
from modeles_dynamique import dynamique_ins


def generer_mesures_imu_bruitees(verite, params_ins):
    """
    Genere les mesures IMU bruitees a partir de la trajectoire verite
    
    Ajoute:
    - Bruit blanc sur gyroscope et accelerometres
    - Biais evoluant selon modele Gauss-Markov
    
    Parametres:
    -----------
    verite : dict
        Trajectoire verite
    params_ins : ParametresINS
        Parametres INS
    
    Retour:
    -------
    dict
        Mesures IMU bruitees avec cles:
        - u_gyro: mesures gyroscope (rad/s)
        - u_accel_N: mesures accelerometre Nord (m/s^2)
        - u_accel_E: mesures accelerometre Est (m/s^2)
        - b_g_reel: biais gyroscope reel (rad/s)
        - b_a_reel: biais accelerometre reel (m/s^2)
    """
    N_samples = len(verite['t'])
    dt = verite['t'][1] - verite['t'][0]
    
    # Initialisation tableaux
    u_gyro = np.zeros(N_samples)
    u_accel_N = np.zeros(N_samples)
    u_accel_E = np.zeros(N_samples)
    b_g_reel = np.zeros(N_samples)
    b_a_reel = np.zeros(N_samples)
    
    # Biais initiaux
    b_g_reel[0] = params_ins.gyro_biais_init
    b_a_reel[0] = params_ins.accel_biais_init
    
    # Parametres Gauss-Markov
    beta_g = 1.0 / params_ins.gyro_tau_c
    beta_a = 1.0 / params_ins.accel_tau_c
    
    # Generation mesures
    for i in range(N_samples):
        # Evolution biais Gauss-Markov
        if i > 0:
            w_bg = np.random.randn() * params_ins.gyro_sigma_bruit * np.sqrt(dt)
            w_ba = np.random.randn() * params_ins.accel_sigma_bruit * np.sqrt(dt)
            
            b_g_reel[i] = b_g_reel[i-1] * (1.0 - beta_g * dt) + w_bg
            b_a_reel[i] = b_a_reel[i-1] * (1.0 - beta_a * dt) + w_ba
        
        # Bruit blanc
        bruit_gyro = np.random.randn() * params_ins.gyro_arw / np.sqrt(dt)
        bruit_accel_N = np.random.randn() * params_ins.accel_bruit * np.sqrt(1.0 / dt)
        bruit_accel_E = np.random.randn() * params_ins.accel_bruit * np.sqrt(1.0 / dt)
        
        # Mesures = verite + biais + bruit
        u_gyro[i] = verite['omega_z'][i] + b_g_reel[i] + bruit_gyro
        u_accel_N[i] = verite['a_N_corps'][i] + b_a_reel[i] + bruit_accel_N
        u_accel_E[i] = verite['a_E_corps'][i] + b_a_reel[i] + bruit_accel_E
    
    mesures = {
        'u_gyro': u_gyro,
        'u_accel_N': u_accel_N,
        'u_accel_E': u_accel_E,
        'b_g_reel': b_g_reel,
        'b_a_reel': b_a_reel
    }
    
    return mesures


def integrer_ins_seule(mesures_imu, x0, params_sim, params_ins):
    """
    Integration strapdown INS sans correction externe (dead reckoning)
    
    Parametres:
    -----------
    mesures_imu : dict
        Mesures IMU bruitees
    x0 : np.ndarray (8,)
        Etat initial [N, E, h, V_N, V_E, psi, b_g, b_a]
    params_sim : ParametresSimulation
        Parametres simulation
    params_ins : ParametresINS
        Parametres INS
    
    Retour:
    -------
    dict
        Trajectoire INS avec cles: t, N, E, h, V_N, V_E, psi, b_g, b_a
    """
    N_samples = len(mesures_imu['u_gyro'])
    dt = params_sim.dt_imu
    
    # Initialisation tableaux
    t = np.arange(N_samples) * dt
    N = np.zeros(N_samples)
    E = np.zeros(N_samples)
    h = np.zeros(N_samples)
    V_N = np.zeros(N_samples)
    V_E = np.zeros(N_samples)
    psi = np.zeros(N_samples)
    b_g = np.zeros(N_samples)
    b_a = np.zeros(N_samples)
    
    # Etat initial
    x = x0.copy()
    N[0], E[0], h[0], V_N[0], V_E[0], psi[0], b_g[0], b_a[0] = x
    
    # Integration
    for k in range(1, N_samples):
        u_accel = np.array([mesures_imu['u_accel_N'][k-1], 
                           mesures_imu['u_accel_E'][k-1]])
        
        x = dynamique_ins(x, mesures_imu['u_gyro'][k-1], u_accel, dt, params_ins)
        
        N[k], E[k], h[k], V_N[k], V_E[k], psi[k], b_g[k], b_a[k] = x
    
    trajectoire = {
        't': t,
        'N': N,
        'E': E,
        'h': h,
        'V_N': V_N,
        'V_E': V_E,
        'psi': psi,
        'b_g': b_g,
        'b_a': b_a
    }
    
    return trajectoire
