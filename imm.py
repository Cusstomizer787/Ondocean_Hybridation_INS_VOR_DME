"""
Module du filtre IMM (Interacting Multiple Model)

Contient la classe IMM avec 3 modes: rectiligne, virage, acceleration.
"""

import numpy as np
from ekf import EKF
from modeles_dynamique import matrice_Q


class IMM:
    """
    Interacting Multiple Model pour fusion INS + VOR/DME
    
    Principe:
    - 3 modeles en parallele avec Q differents
    - Probabilites de mode adaptatives
    - Fusion ponderee des estimations
    
    Attributs:
    ----------
    n_modes : int
        Nombre de modes (3)
    filtres : list
        Liste de 3 EKF
    mu : np.ndarray (3,)
        Probabilites modes [rectiligne, virage, acceleration]
    Pi : np.ndarray (3, 3)
        Matrice de transition entre modes
    x : np.ndarray (8,)
        Etat fusionne
    P : np.ndarray (8, 8)
        Covariance fusionnee
    historique : dict
        Historique des etats, probabilites, modes
    """
    
    def __init__(self, x0, P0, params_ins, params_vor_dme, params_ekf):
        """
        Initialisation IMM
        
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
        self.n_modes = 3
        self.params_ins = params_ins
        self.params_vor_dme = params_vor_dme
        self.params_ekf = params_ekf
        
        # Probabilites initiales (favoriser rectiligne)
        self.mu = np.array([0.7, 0.2, 0.1])
        
        # Matrice de transition
        self.Pi = np.array([
            [0.95, 0.04, 0.01],  # Depuis rectiligne
            [0.05, 0.90, 0.05],  # Depuis virage
            [0.05, 0.05, 0.90]   # Depuis acceleration
        ])
        
        # Parametres Q pour chaque mode
        self.Q_vitesse_modes = [0.5, 2.0, 5.0]  # [rectiligne, virage, accel]
        
        # Initialisation filtres
        self.filtres = []
        for j in range(self.n_modes):
            filtre = EKF(x0.copy(), P0.copy(), params_ins, params_vor_dme, params_ekf)
            self.filtres.append(filtre)
        
        # Etat et covariance fusionnes
        self.x = x0.copy()
        self.P = P0.copy()
        
        # Historique
        self.historique = {
            't': [],
            'x': [],
            'P': [],
            'mu': [],
            'mode': []
        }
    
    def interaction(self):
        """
        Etape d'interaction: melange des etats et covariances
        """
        # Calcul probabilites de melange
        c = np.zeros(self.n_modes)
        for j in range(self.n_modes):
            c[j] = np.sum(self.Pi[:, j] * self.mu)
        
        mu_ij = np.zeros((self.n_modes, self.n_modes))
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                if c[j] > 1e-10:
                    mu_ij[i, j] = self.Pi[i, j] * self.mu[i] / c[j]
                else:
                    mu_ij[i, j] = 1.0 / self.n_modes
        
        # Melange etats et covariances
        x0j = []
        P0j = []
        
        for j in range(self.n_modes):
            # Etat melange
            x_mixed = np.zeros(8)
            for i in range(self.n_modes):
                x_mixed += mu_ij[i, j] * self.filtres[i].x
            x0j.append(x_mixed)
            
            # Covariance melangee
            P_mixed = np.zeros((8, 8))
            for i in range(self.n_modes):
                diff = self.filtres[i].x - x_mixed
                P_mixed += mu_ij[i, j] * (self.filtres[i].P + np.outer(diff, diff))
            P0j.append(P_mixed)
        
        # Reinitialiser filtres avec etats melanges
        for j in range(self.n_modes):
            self.filtres[j].x = x0j[j].copy()
            self.filtres[j].P = P0j[j].copy()
    
    def prediction(self, u_gyro, u_accel, dt):
        """
        Etape de prediction pour tous les modes
        
        Parametres:
        -----------
        u_gyro : float
            Mesure gyroscope (rad/s)
        u_accel : np.ndarray (2,)
            Mesures accelerometre [a_N, a_E] (m/s^2)
        dt : float
            Pas de temps (s)
        """
        for j in range(self.n_modes):
            # Sauvegarder Q_vitesse original
            Q_vitesse_original = self.filtres[j].params_ins.Q_vitesse if hasattr(self.filtres[j].params_ins, 'Q_vitesse') else None
            
            # Prediction avec Q specifique au mode
            self.filtres[j].prediction(u_gyro, u_accel, dt)
            
            # Restaurer Q_vitesse si necessaire
            if Q_vitesse_original is not None:
                self.filtres[j].params_ins.Q_vitesse = Q_vitesse_original
    
    def update_vor(self, z_vor, station):
        """
        Etape de correction avec mesure VOR pour tous les modes
        
        Parametres:
        -----------
        z_vor : float
            Mesure VOR (azimut en rad)
        station : Station
            Station VOR
        
        Retour:
        -------
        bool
            True si au moins un filtre accepte la mesure
        """
        Lambda = np.zeros(self.n_modes)
        accepte_global = False
        
        for j in range(self.n_modes):
            accepte = self.filtres[j].update_vor(z_vor, station)
            
            if accepte:
                accepte_global = True
                # Calcul vraisemblance
                if len(self.filtres[j].historique['innovations_vor']) > 0:
                    innov = self.filtres[j].historique['innovations_vor'][-1]
                    # Approximation S depuis historique gating
                    if len(self.filtres[j].historique['gating_vor']) > 0:
                        d2 = self.filtres[j].historique['gating_vor'][-1]
                        S = innov**2 / d2 if d2 > 1e-10 else 1.0
                        Lambda[j] = (1.0 / np.sqrt(2*np.pi*S)) * np.exp(-0.5 * d2)
                    else:
                        Lambda[j] = 1.0
                else:
                    Lambda[j] = 1.0
            else:
                Lambda[j] = 1e-10  # Vraisemblance faible si rejetee
        
        # Mise a jour probabilites modes
        c = np.zeros(self.n_modes)
        for j in range(self.n_modes):
            c[j] = np.sum(self.Pi[:, j] * self.mu)
        
        mu_new = Lambda * c
        sum_mu = np.sum(mu_new)
        if sum_mu > 1e-10:
            self.mu = mu_new / sum_mu
        
        return accepte_global
    
    def update_dme(self, z_dme, station):
        """
        Etape de correction avec mesure DME pour tous les modes
        
        Parametres:
        -----------
        z_dme : float
            Mesure DME (distance en m)
        station : Station
            Station DME
        
        Retour:
        -------
        bool
            True si au moins un filtre accepte la mesure
        """
        Lambda = np.zeros(self.n_modes)
        accepte_global = False
        
        for j in range(self.n_modes):
            accepte = self.filtres[j].update_dme(z_dme, station)
            
            if accepte:
                accepte_global = True
                # Calcul vraisemblance
                if len(self.filtres[j].historique['innovations_dme']) > 0:
                    innov = self.filtres[j].historique['innovations_dme'][-1]
                    # Approximation S depuis historique gating
                    if len(self.filtres[j].historique['gating_dme']) > 0:
                        d2 = self.filtres[j].historique['gating_dme'][-1]
                        S = innov**2 / d2 if d2 > 1e-10 else 1.0
                        Lambda[j] = (1.0 / np.sqrt(2*np.pi*S)) * np.exp(-0.5 * d2)
                    else:
                        Lambda[j] = 1.0
                else:
                    Lambda[j] = 1.0
            else:
                Lambda[j] = 1e-10  # Vraisemblance faible si rejetee
        
        # Mise a jour probabilites modes
        c = np.zeros(self.n_modes)
        for j in range(self.n_modes):
            c[j] = np.sum(self.Pi[:, j] * self.mu)
        
        mu_new = Lambda * c
        sum_mu = np.sum(mu_new)
        if sum_mu > 1e-10:
            self.mu = mu_new / sum_mu
        
        return accepte_global
    
    def fusion(self):
        """
        Fusion des estimations des differents modes
        """
        # Etat fusionne
        self.x = np.zeros(8)
        for j in range(self.n_modes):
            self.x += self.mu[j] * self.filtres[j].x
        
        # Covariance fusionnee
        self.P = np.zeros((8, 8))
        for j in range(self.n_modes):
            diff = self.filtres[j].x - self.x
            self.P += self.mu[j] * (self.filtres[j].P + np.outer(diff, diff))
    
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
        self.historique['mu'].append(self.mu.copy())
        self.historique['mode'].append(np.argmax(self.mu))
