"""
Module des modeles dynamiques pour la simulation INS

Contient les equations d'etat, les jacobiennes et les matrices de bruit.
"""

import numpy as np


def dynamique_ins(x, u_gyro, u_accel, dt, params_ins):
    """
    Modele de dynamique INS pour un pas de temps
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    u_gyro : float
        Mesure gyroscope bruitee (rad/s)
    u_accel : np.ndarray (2,)
        Mesures accelerometre [a_N_corps, a_E_corps] bruitees (m/s^2)
    dt : float
        Pas de temps (s)
    params_ins : ParametresINS
        Parametres INS
    
    Retour:
    -------
    np.ndarray (8,)
        Etat au pas suivant
    """
    # Extraction etat
    N, E, h, V_N, V_E, psi, b_g, b_a = x
    
    # Correction mesures par biais
    omega_z_corrige = u_gyro - b_g
    a_N_corrige = u_accel[0] - b_a
    a_E_corrige = u_accel[1] - b_a
    
    # Rotation repere corps vers repere NED
    cos_psi = np.cos(psi)
    sin_psi = np.sin(psi)
    a_N_ned = a_N_corrige * cos_psi - a_E_corrige * sin_psi
    a_E_ned = a_N_corrige * sin_psi + a_E_corrige * cos_psi
    
    # Integration Euler
    N_next = N + V_N * dt
    E_next = E + V_E * dt
    h_next = h  # Altitude constante
    V_N_next = V_N + a_N_ned * dt
    V_E_next = V_E + a_E_ned * dt
    psi_next = psi + omega_z_corrige * dt
    
    # Contrainte douce adaptative pour mouvements circulaires uniformes
    V_mag_current = np.sqrt(V_N_next**2 + V_E_next**2)
    V_mag_previous = np.sqrt(V_N**2 + V_E**2)
    
    # Detection mouvement circulaire uniforme
    est_en_virage = np.abs(omega_z_corrige) > 0.002  # rad/s
    variation_vitesse = np.abs(V_mag_current - V_mag_previous)
    seuil_variation = 1.0  # m/s (tolerance pour acceleration reelle)
    
    # Appliquer contrainte douce seulement si virage + vitesse quasi-constante
    if est_en_virage and variation_vitesse < seuil_variation and V_mag_current > 1.0:
        # Correction partielle (80% vers vitesse precedente)
        # Permet petites variations mais limite derives numeriques
        alpha = 0.8
        V_mag_target = alpha * V_mag_previous + (1 - alpha) * V_mag_current
        V_N_next = V_N_next * (V_mag_target / V_mag_current)
        V_E_next = V_E_next * (V_mag_target / V_mag_current)
    
    # Normalisation angle [-pi, pi]
    psi_next = np.mod(psi_next + np.pi, 2.0 * np.pi) - np.pi
    
    # Biais Gauss-Markov: db/dt = -beta*b + w
    # Discretisation: b_next = b*(1 - beta*dt) + w*sqrt(dt)
    beta_g = 1.0 / params_ins.gyro_tau_c
    beta_a = 1.0 / params_ins.accel_tau_c
    
    w_bg = np.random.randn() * params_ins.gyro_sigma_bruit * np.sqrt(dt)
    w_ba = np.random.randn() * params_ins.accel_sigma_bruit * np.sqrt(dt)
    
    b_g_next = b_g * (1.0 - beta_g * dt) + w_bg
    b_a_next = b_a * (1.0 - beta_a * dt) + w_ba
    
    return np.array([N_next, E_next, h_next, V_N_next, V_E_next, 
                     psi_next, b_g_next, b_a_next])


def jacobienne_F(x, u_gyro, u_accel, dt, params_ins):
    """
    Calcul de la jacobienne de la dynamique par rapport a l'etat
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    u_gyro : float
        Mesure gyroscope (rad/s)
    u_accel : np.ndarray (2,)
        Mesures accelerometre [a_N_corps, a_E_corps] (m/s^2)
    dt : float
        Pas de temps (s)
    params_ins : ParametresINS
        Parametres INS
    
    Retour:
    -------
    np.ndarray (8, 8)
        Matrice jacobienne F = df/dx
    """
    # Extraction etat
    N, E, h, V_N, V_E, psi, b_g, b_a = x
    
    # Mesures corrigees
    a_N_corrige = u_accel[0] - b_a
    a_E_corrige = u_accel[1] - b_a
    
    cos_psi = np.cos(psi)
    sin_psi = np.sin(psi)
    
    # Initialisation matrice identite
    F = np.eye(8)
    
    # Derivees position par rapport vitesse
    F[0, 3] = dt  # dN/dV_N
    F[1, 4] = dt  # dE/dV_E
    
    # Derivees vitesse par rapport cap
    # dV_N/dpsi = d/dpsi[(a_N*cos(psi) - a_E*sin(psi))*dt]
    F[3, 5] = (-a_N_corrige * sin_psi - a_E_corrige * cos_psi) * dt
    # dV_E/dpsi = d/dpsi[(a_N*sin(psi) + a_E*cos(psi))*dt]
    F[4, 5] = (a_N_corrige * cos_psi - a_E_corrige * sin_psi) * dt
    
    # Derivees vitesse par rapport biais accelerometre
    F[3, 7] = -cos_psi * dt  # dV_N/db_a
    F[4, 7] = -sin_psi * dt  # dV_E/db_a
    
    # Derivees cap par rapport biais gyroscope
    F[5, 6] = -dt  # dpsi/db_g
    
    # Derivees biais (Gauss-Markov)
    beta_g = 1.0 / params_ins.gyro_tau_c
    beta_a = 1.0 / params_ins.accel_tau_c
    F[6, 6] = 1.0 - beta_g * dt  # db_g/db_g
    F[7, 7] = 1.0 - beta_a * dt  # db_a/db_a
    
    return F


def matrice_Q(dt, params_ins, omega_z=0.0):
    """
    Calcul de la matrice de bruit de processus adaptative
    
    Parametres:
    -----------
    dt : float
        Pas de temps (s)
    params_ins : ParametresINS
        Parametres INS
    omega_z : float
        Vitesse angulaire courante (rad/s) pour adaptation
    
    Retour:
    -------
    np.ndarray (8, 8)
        Matrice de covariance du bruit de processus Q
    """
    Q = np.zeros((8, 8))
    
    # Bruit de processus adaptatif selon type de mouvement
    if np.abs(omega_z) > 0.002:
        # En virage: augmenter incertitude vitesse
        # (modele moins precis en virage, EKF fait plus confiance aux mesures)
        Q_vitesse = 2.0  # m^2/s^3
    else:
        # Rectiligne: incertitude normale
        Q_vitesse = 0.5  # m^2/s^3
    
    Q[3, 3] = Q_vitesse * dt  # V_N
    Q[4, 4] = Q_vitesse * dt  # V_E
    
    # Bruit de processus sur cap (erreur integration gyro)
    Q_cap = 0.0001  # rad^2/s
    Q[5, 5] = Q_cap * dt
    
    # Biais gyroscope
    Q[6, 6] = (params_ins.gyro_sigma_bruit)**2 * dt
    
    # Biais accelerometre
    Q[7, 7] = (params_ins.accel_sigma_bruit)**2 * dt
    
    return Q
