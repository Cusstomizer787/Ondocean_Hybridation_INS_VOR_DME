"""
Module du filtre de Kalman etendu (EKF)

Contient la classe EKF avec prediction et updates VOR/DME.
"""

import numpy as np
from modeles_dynamique import dynamique_ins, jacobienne_F, matrice_Q
from stations_sol import (modele_mesure_vor, modele_mesure_dme,
                          jacobienne_H_vor, jacobienne_H_dme)


class EKF:
    """
    Filtre de Kalman Etendu pour fusion INS + VOR/DME
    
    Attributs:
    ----------
    x : np.ndarray (8,)
        Etat estime [N, E, h, V_N, V_E, psi, b_g, b_a]
    P : np.ndarray (8, 8)
        Matrice de covariance
    params_ins : ParametresINS
        Parametres INS
    params_vor_dme : ParametresVORDME
        Parametres VOR/DME
    params_ekf : ParametresEKF
        Parametres EKF
    historique : dict
        Historique des etats, covariances, innovations
    """
    
    def __init__(self, x0, P0, params_ins, params_vor_dme, params_ekf):
        """
        Initialisation EKF
        
        Parametres:
        -----------
        x0 : np.ndarray (8,)
            Etat initial
        P0 : np.ndarray (8, 8)
            Covariance initiale
        params_ins : ParametresINS
            Parametres INS
        params_vor_dme : ParametresVORDME
            Parametres VOR/DME
        params_ekf : ParametresEKF
            Parametres EKF
        """
        self.x = x0.copy()
        self.P = P0.copy()
        self.params_ins = params_ins
        self.params_vor_dme = params_vor_dme
        self.params_ekf = params_ekf
        
        # Pour gating adaptatif
        self.V_mag_prev = np.sqrt(x0[3]**2 + x0[4]**2)
        self.a_long_current = 0.0
        
        # Historique
        self.historique = {
            't': [],
            'x': [],
            'P': [],
            'innovations_vor': [],
            'innovations_dme': [],
            'gating_vor': [],
            'gating_dme': [],
            'station_id_vor': [],
            'station_id_dme': []
        }
    
    def prediction(self, u_gyro, u_accel, dt):
        """
        Etape de prediction EKF
        
        Parametres:
        -----------
        u_gyro : float
            Mesure gyroscope (rad/s)
        u_accel : np.ndarray (2,)
            Mesures accelerometre [a_N, a_E] (m/s^2)
        dt : float
            Pas de temps (s)
        """
        # Prediction etat
        self.x = dynamique_ins(self.x, u_gyro, u_accel, dt, self.params_ins)
        
        # Calcul acceleration longitudinale pour gating adaptatif
        V_mag_current = np.sqrt(self.x[3]**2 + self.x[4]**2)
        self.a_long_current = (V_mag_current - self.V_mag_prev) / dt
        self.V_mag_prev = V_mag_current
        
        # Prediction covariance avec Q adaptatif
        F = jacobienne_F(self.x, u_gyro, u_accel, dt, self.params_ins)
        
        # Calculer omega_z corrige pour adaptation de Q
        omega_z_corrige = u_gyro - self.x[6]  # u_gyro - b_g
        Q = matrice_Q(dt, self.params_ins, omega_z_corrige)
        
        self.P = F @ self.P @ F.T + Q
    
    def calculer_seuil_gating(self, omega_z, a_long, S):
        """
        Calcul seuil de gating adaptatif selon type de manoeuvre
        
        Parametres:
        -----------
        omega_z : float
            Vitesse angulaire courante (rad/s)
        a_long : float
            Acceleration longitudinale (m/s^2)
        S : np.ndarray
            Covariance innovation
        
        Retour:
        -------
        float
            Seuil chi2 adaptatif
        """
        # Detection type de mouvement
        if np.abs(omega_z) > 0.01 or np.abs(a_long) > 0.5:
            # Manoeuvre agressive (virage serre ou forte acceleration)
            seuil_base = 25.0
        elif np.abs(omega_z) > 0.002 or np.abs(a_long) > 0.2:
            # Manoeuvre moderee
            seuil_base = 15.0
        else:
            # Mouvement calme
            seuil_base = 9.21  # 95%, 2 DDL
        
        # Adaptation fine basee sur covariance innovation
        # Si S grande (forte incertitude), augmenter seuil
        trace_S = np.trace(S)
        dim_S = S.shape[0]
        facteur_S = 1.0 + 0.05 * (trace_S / dim_S)
        
        seuil_final = seuil_base * facteur_S
        
        # Limites de securite
        seuil_final = np.clip(seuil_final, 9.21, 30.0)
        
        return seuil_final
    
    def update_vor(self, z_vor, station):
        """
        Etape de correction EKF avec mesure VOR
        
        Parametres:
        -----------
        z_vor : float
            Mesure VOR (azimut en rad)
        station : Station
            Station VOR
        
        Retour:
        -------
        bool
            True si mesure acceptee, False si rejetee par gating
        """
        # Prediction mesure
        z_pred = modele_mesure_vor(self.x, station)
        
        # Innovation avec wrapping angulaire
        innov = z_vor - z_pred
        innov = np.mod(innov + np.pi, 2.0 * np.pi) - np.pi
        
        # Jacobienne
        H = jacobienne_H_vor(self.x, station)
        
        # Matrice innovation
        R = self.params_ekf.R_vor
        S = H @ self.P @ H.T + R
        S_scalar = S[0, 0]
        
        # Test gating adaptatif (chi2)
        d2 = innov**2 / S_scalar
        
        # Calcul seuil adaptatif
        omega_z = self.x[5]  # Vitesse angulaire (cap)
        seuil = self.calculer_seuil_gating(omega_z, self.a_long_current, S)
        
        # Sauvegarde innovation
        self.historique['innovations_vor'].append(innov)
        self.historique['gating_vor'].append(d2)
        self.historique['station_id_vor'].append(station.id)
        
        if d2 > seuil:
            # Mesure rejetee
            return False
        
        # Gain Kalman
        K = self.P @ H.T / S_scalar
        K = K.reshape(-1, 1)
        
        # Correction etat
        self.x = self.x + (K * innov).flatten()
        
        # Normalisation angle cap
        self.x[5] = np.mod(self.x[5] + np.pi, 2.0 * np.pi) - np.pi
        
        # Correction covariance (forme Joseph pour stabilite numerique)
        I_KH = np.eye(8) - K @ H
        self.P = I_KH @ self.P @ I_KH.T + K * R * K.T
        
        return True
    
    def update_dme(self, z_dme, station):
        """
        Etape de correction EKF avec mesure DME
        
        Parametres:
        -----------
        z_dme : float
            Mesure DME (distance en m)
        station : Station
            Station DME
        
        Retour:
        -------
        bool
            True si mesure acceptee, False si rejetee par gating
        """
        # Prediction mesure
        z_pred = modele_mesure_dme(self.x, station)
        
        # Innovation
        innov = z_dme - z_pred
        
        # Jacobienne
        H = jacobienne_H_dme(self.x, station)
        
        # Matrice innovation
        R = self.params_ekf.R_dme
        S = H @ self.P @ H.T + R
        S_scalar = S[0, 0]
        
        # Test gating adaptatif (chi2)
        d2 = innov**2 / S_scalar
        
        # Calcul seuil adaptatif
        omega_z = self.x[5]  # Vitesse angulaire (cap)
        seuil = self.calculer_seuil_gating(omega_z, self.a_long_current, S)
        
        # Sauvegarde innovation
        self.historique['innovations_dme'].append(innov)
        self.historique['gating_dme'].append(d2)
        self.historique['station_id_dme'].append(station.id)
        
        if d2 > seuil:
            # Mesure rejetee
            return False
        
        # Gain Kalman
        K = self.P @ H.T / S_scalar
        K = K.reshape(-1, 1)
        
        # Correction etat
        self.x = self.x + (K * innov).flatten()
        
        # Normalisation angle cap
        self.x[5] = np.mod(self.x[5] + np.pi, 2.0 * np.pi) - np.pi
        
        # Correction covariance (forme Joseph)
        I_KH = np.eye(8) - K @ H
        self.P = I_KH @ self.P @ I_KH.T + K * R * K.T
        
        return True
    
    def sauvegarder_etat(self, t):
        """
        Sauvegarde l'etat courant dans l'historique
        
        Parametres:
        -----------
        t : float
            Temps courant (s)
        """
        self.historique['t'].append(t)
        self.historique['x'].append(self.x.copy())
        self.historique['P'].append(self.P.copy())
