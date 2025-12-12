"""
Module de gestion des stations VOR/DME au sol

Contient les modeles de mesure, jacobiennes et tests de visibilite.
"""

import numpy as np


def modele_mesure_vor(x, station):
    """
    Modele de mesure VOR (azimut)
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    station : Station
        Station VOR
    
    Retour:
    -------
    float
        Azimut predit (rad) dans [-pi, pi]
    """
    N, E = x[0], x[1]
    N_s, E_s = station.position[0], station.position[1]
    
    theta = np.arctan2(E - E_s, N - N_s)
    
    # Normalisation [-pi, pi]
    theta = np.mod(theta + np.pi, 2.0 * np.pi) - np.pi
    
    return theta


def modele_mesure_dme(x, station):
    """
    Modele de mesure DME (distance oblique)
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    station : Station
        Station DME
    
    Retour:
    -------
    float
        Distance oblique predite (m)
    """
    N, E, h = x[0], x[1], x[2]
    N_s, E_s, h_s = station.position
    
    rho = np.sqrt((N - N_s)**2 + (E - E_s)**2 + (h - h_s)**2)
    
    return rho


def jacobienne_H_vor(x, station):
    """
    Jacobienne du modele de mesure VOR
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    station : Station
        Station VOR
    
    Retour:
    -------
    np.ndarray (1, 8)
        Jacobienne H = dh/dx pour VOR
    """
    N, E = x[0], x[1]
    N_s, E_s = station.position[0], station.position[1]
    
    dN = N - N_s
    dE = E - E_s
    d2 = dN**2 + dE**2
    
    H = np.zeros((1, 8))
    
    # dtheta/dN = -dE / (dN^2 + dE^2)
    H[0, 0] = -dE / d2
    
    # dtheta/dE = dN / (dN^2 + dE^2)
    H[0, 1] = dN / d2
    
    # Autres derivees nulles
    
    return H


def jacobienne_H_dme(x, station):
    """
    Jacobienne du modele de mesure DME
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    station : Station
        Station DME
    
    Retour:
    -------
    np.ndarray (1, 8)
        Jacobienne H = dh/dx pour DME
    """
    N, E, h = x[0], x[1], x[2]
    N_s, E_s, h_s = station.position
    
    dN = N - N_s
    dE = E - E_s
    dh = h - h_s
    
    rho = np.sqrt(dN**2 + dE**2 + dh**2)
    
    H = np.zeros((1, 8))
    
    # drho/dN = dN / rho
    H[0, 0] = dN / rho
    
    # drho/dE = dE / rho
    H[0, 1] = dE / rho
    
    # drho/dh = dh / rho
    H[0, 2] = dh / rho
    
    # Autres derivees nulles
    
    return H


def verifier_visibilite(x, station, params_vor_dme):
    """
    Verifie si la station est visible depuis la position de l'aeronef
    
    Criteres:
    - Distance oblique < portee_max
    - Angle de site > angle_site_min
    
    Parametres:
    -----------
    x : np.ndarray (8,)
        Etat [N, E, h, V_N, V_E, psi, b_g, b_a]
    station : Station
        Station a tester
    params_vor_dme : ParametresVORDME
        Parametres VOR/DME
    
    Retour:
    -------
    bool
        True si visible, False sinon
    """
    # Test distance oblique
    rho = modele_mesure_dme(x, station)
    if rho > params_vor_dme.portee_max:
        return False
    
    # Test angle de site
    N, E, h = x[0], x[1], x[2]
    N_s, E_s, h_s = station.position
    
    dh = h - h_s
    dist_horiz = np.sqrt((N - N_s)**2 + (E - E_s)**2)
    
    # Eviter division par zero
    if dist_horiz < 1e-6:
        angle_site = np.pi / 2.0 if dh > 0 else -np.pi / 2.0
    else:
        angle_site = np.arctan2(dh, dist_horiz)
    
    if angle_site < params_vor_dme.angle_site_min:
        return False
    
    return True
