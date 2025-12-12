"""
Module de calcul des metriques de performance

Contient les fonctions de calcul d'erreurs, RMSE, CEP.
"""

import numpy as np


def calculer_erreurs(trajectoire, verite):
    """
    Calcule les erreurs entre trajectoire estimee et verite
    
    Parametres:
    -----------
    trajectoire : dict
        Trajectoire estimee (INS ou EKF)
    verite : dict
        Trajectoire verite
    
    Retour:
    -------
    dict
        Erreurs avec cles: err_N, err_E, err_h, err_2D, err_V_N, err_V_E, err_psi
    """
    erreurs = {}
    
    # Erreurs position
    erreurs['err_N'] = trajectoire['N'] - verite['N']
    erreurs['err_E'] = trajectoire['E'] - verite['E']
    erreurs['err_h'] = trajectoire['h'] - verite['h']
    
    # Erreur 2D
    erreurs['err_2D'] = np.sqrt(erreurs['err_N']**2 + erreurs['err_E']**2)
    
    # Erreurs vitesse
    erreurs['err_V_N'] = trajectoire['V_N'] - verite['V_N']
    erreurs['err_V_E'] = trajectoire['V_E'] - verite['V_E']
    
    # Erreur cap (avec wrapping)
    err_psi = trajectoire['psi'] - verite['psi']
    erreurs['err_psi'] = np.mod(err_psi + np.pi, 2.0 * np.pi) - np.pi
    
    return erreurs


def rmse_glissant(erreurs, fenetre_s, dt):
    """
    Calcule le RMSE glissant sur une fenetre temporelle
    
    Parametres:
    -----------
    erreurs : np.ndarray (N,)
        Serie temporelle d'erreurs
    fenetre_s : float
        Largeur fenetre en secondes
    dt : float
        Pas de temps (s)
    
    Retour:
    -------
    np.ndarray (N,)
        RMSE glissant
    """
    N = len(erreurs)
    n_fenetre = int(fenetre_s / dt)
    rmse_t = np.zeros(N)
    
    for i in range(N):
        i_debut = max(0, i - n_fenetre + 1)
        rmse_t[i] = np.sqrt(np.mean(erreurs[i_debut:i+1]**2))
    
    return rmse_t


def calculer_cep(erreurs_N, erreurs_E, percentile):
    """
    Calcule le Circular Error Probable (CEP)
    
    Parametres:
    -----------
    erreurs_N : np.ndarray
        Erreurs Nord (m)
    erreurs_E : np.ndarray
        Erreurs Est (m)
    percentile : float
        Percentile desire (50 ou 95)
    
    Retour:
    -------
    float
        CEP en metres
    """
    err_2D = np.sqrt(erreurs_N**2 + erreurs_E**2)
    cep = np.percentile(err_2D, percentile)
    
    return cep


def cep_glissant(erreurs_N, erreurs_E, fenetre_s, dt, percentile):
    """
    Calcule le CEP glissant sur une fenetre temporelle
    
    Parametres:
    -----------
    erreurs_N : np.ndarray
        Erreurs Nord (m)
    erreurs_E : np.ndarray
        Erreurs Est (m)
    fenetre_s : float
        Largeur fenetre en secondes
    dt : float
        Pas de temps (s)
    percentile : float
        Percentile desire (50 ou 95)
    
    Retour:
    -------
    np.ndarray
        CEP glissant
    """
    N = len(erreurs_N)
    n_fenetre = int(fenetre_s / dt)
    cep_t = np.zeros(N)
    
    for i in range(N):
        i_debut = max(0, i - n_fenetre + 1)
        err_2D_fenetre = np.sqrt(erreurs_N[i_debut:i+1]**2 + erreurs_E[i_debut:i+1]**2)
        cep_t[i] = np.percentile(err_2D_fenetre, percentile)
    
    return cep_t


def statistiques_finales(erreurs):
    """
    Calcule les statistiques finales sur toute la simulation
    
    Parametres:
    -----------
    erreurs : dict
        Dictionnaire d'erreurs
    
    Retour:
    -------
    dict
        Statistiques avec RMSE, max, CEP50, CEP95 pour chaque composante
    """
    stats = {}
    
    # RMSE position
    stats['RMSE_N'] = np.sqrt(np.mean(erreurs['err_N']**2))
    stats['RMSE_E'] = np.sqrt(np.mean(erreurs['err_E']**2))
    stats['RMSE_h'] = np.sqrt(np.mean(erreurs['err_h']**2))
    stats['RMSE_2D'] = np.sqrt(np.mean(erreurs['err_2D']**2))
    
    # Erreurs max
    stats['max_N'] = np.max(np.abs(erreurs['err_N']))
    stats['max_E'] = np.max(np.abs(erreurs['err_E']))
    stats['max_h'] = np.max(np.abs(erreurs['err_h']))
    stats['max_2D'] = np.max(erreurs['err_2D'])
    
    # CEP
    stats['CEP50'] = calculer_cep(erreurs['err_N'], erreurs['err_E'], 50)
    stats['CEP95'] = calculer_cep(erreurs['err_N'], erreurs['err_E'], 95)
    
    # RMSE vitesse
    stats['RMSE_V_N'] = np.sqrt(np.mean(erreurs['err_V_N']**2))
    stats['RMSE_V_E'] = np.sqrt(np.mean(erreurs['err_V_E']**2))
    
    # RMSE cap
    stats['RMSE_psi'] = np.sqrt(np.mean(erreurs['err_psi']**2))
    stats['RMSE_psi_deg'] = np.rad2deg(stats['RMSE_psi'])
    
    return stats
