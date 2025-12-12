"""
Module de parametres pour la simulation INS + VOR/DME

Contient toutes les classes de configuration et fonctions de chargement
des parametres par defaut.
"""

import numpy as np


class ParametresSimulation:
    """Parametres temporels de la simulation"""
    def __init__(self):
        self.dt_imu = 0.01  # Periode echantillonnage IMU (s)
        self.dt_vor_dme = 1.0  # Periode echantillonnage VOR/DME (s)
        self.duree_simulation = 1200.0  # Duree totale (s)
        self.altitude_vol = 3000.0  # Altitude de vol (m)


class ParametresINS:
    """Parametres de la centrale inertielle (MEMS aeronautique)"""
    def __init__(self):
        # Gyroscope
        self.gyro_arw = 0.00436  # Bruit ARW (rad/sqrt(s))
        self.gyro_biais_init = 0.00524  # Biais initial (rad/s)
        self.gyro_tau_c = 3600.0  # Temps correlation Gauss-Markov (s)
        self.gyro_sigma_bruit = 8.73e-5  # Ecart-type bruit processus (rad/s^2)
        
        # Accelerometre
        self.accel_bruit = 0.00147  # Bruit (m/s^2/sqrt(Hz))
        self.accel_biais_init = 0.0294  # Biais initial (m/s^2)
        self.accel_tau_c = 3600.0  # Temps correlation Gauss-Markov (s)
        self.accel_sigma_bruit = 4.9e-4  # Ecart-type bruit processus (m/s^3)


class ParametresVORDME:
    """Parametres des stations VOR/DME"""
    def __init__(self):
        # VOR
        self.vor_sigma = 0.02618  # Ecart-type azimut (rad) = 1.5 deg
        self.vor_biais = 0.00873  # Biais systematique (rad) = 0.5 deg
        
        # DME
        self.dme_sigma = 300.0  # Ecart-type distance (m)
        self.dme_biais = 50.0  # Biais systematique (m)
        
        # Contraintes visibilite
        self.portee_max = 370400.0  # Portee maximale (m) = 200 NM
        self.angle_site_min = 0.05236  # Angle site minimum (rad) = 3 deg


class ParametresEKF:
    """Parametres du filtre de Kalman etendu"""
    def __init__(self):
        # Covariance initiale (8x8)
        # Ordre: [N, E, h, V_N, V_E, psi, b_g, b_a]
        self.P0 = np.diag([
            100.0**2,  # N (m^2)
            100.0**2,  # E (m^2)
            50.0**2,   # h (m^2)
            5.0**2,    # V_N (m^2/s^2)
            5.0**2,    # V_E (m^2/s^2)
            0.1**2,    # psi (rad^2)
            0.01**2,   # b_g (rad^2/s^2)
            0.05**2    # b_a (m^2/s^4)
        ])
        
        # Matrice Q sera calculee dynamiquement dans modeles_dynamique.py
        self.Q = None
        
        # Variances de mesure
        self.R_vor = 0.02618**2  # Variance VOR (rad^2)
        self.R_dme = 300.0**2    # Variance DME (m^2)
        
        # Gating (assoupli pour mouvements circulaires)
        self.seuil_gating = 15.0  # Seuil chi2 assoupli (etait 9.21 pour 95%)
        
        # Metriques
        self.fenetre_rmse = 60.0  # Fenetre RMSE glissant (s)


class Station:
    """Classe representant une station VOR/DME au sol"""
    def __init__(self, id_station, nom, position, a_vor, a_dme, frequence_mesure):
        """
        Parametres:
        -----------
        id_station : int
            Identifiant unique de la station
        nom : str
            Nom de la station
        position : np.ndarray (3,)
            Position [N, E, h] en metres
        a_vor : bool
            Station equipee VOR
        a_dme : bool
            Station equipee DME
        frequence_mesure : float
            Frequence de mesure (Hz)
        """
        self.id = id_station
        self.nom = nom
        self.position = np.array(position, dtype=float)
        self.a_vor = a_vor
        self.a_dme = a_dme
        self.frequence_mesure = frequence_mesure
        self.prochain_temps_mesure = 1.0 / frequence_mesure  # Premiere mesure


def charger_parametres_defaut():
    """
    Charge tous les parametres par defaut
    
    Retour:
    -------
    tuple
        (params_sim, params_ins, params_vor_dme, params_ekf)
    """
    params_sim = ParametresSimulation()
    params_ins = ParametresINS()
    params_vor_dme = ParametresVORDME()
    params_ekf = ParametresEKF()
    
    return params_sim, params_ins, params_vor_dme, params_ekf


def creer_stations_sol():
    """
    Cree la liste des stations VOR/DME au sol
    
    Configuration:
    - Station 1: (0, 0, 0) - VOR/DME
    - Station 2: (80000, 0, 0) - VOR/DME
    - Station 3: (40000, 60000, 0) - VOR/DME
    
    Retour:
    -------
    list[Station]
        Liste des 3 stations
    """
    stations = [
        Station(
            id_station=1,
            nom="Station 1",
            position=[0.0, 0.0, 0.0],
            a_vor=True,
            a_dme=True,
            frequence_mesure=1.0
        ),
        Station(
            id_station=2,
            nom="Station 2",
            position=[80000.0, 0.0, 0.0],
            a_vor=True,
            a_dme=True,
            frequence_mesure=1.0
        ),
        Station(
            id_station=3,
            nom="Station 3",
            position=[40000.0, 60000.0, 0.0],
            a_vor=True,
            a_dme=True,
            frequence_mesure=1.0
        )
    ]
    
    return stations


def creer_stations_reelles():
    """
    Cree la liste des stations VOR/DME reelles en France
    
    Configuration basee sur les balises reelles utilisees dans estimateur.ipynb:
    - DJL (11145 kHz): VORDME a Dole-Tavaux
    - RLP (11735 kHz): VORDME a Reims-Prunay
    - LXI (10820 kHz): DME a Luxeuil
    - EPL (11300 kHz): VOR a Epinal
    - LUL (11710 kHz): VOR a Luxeuil
    
    Les coordonnees GPS sont converties en NED avec le meme point de reference
    que la trajectoire du scenario 4 (data.csv): lat_ref=47.44106, lon_ref=5.07231
    
    Retour:
    -------
    list[Station]
        Liste des 5 stations reelles
    """
    # Point de reference (premiere position data.csv)
    lat_ref = np.radians(47.44106)
    lon_ref = np.radians(5.07231)
    rayon_terre = 6371000.0
    
    # Donnees balises: [nom, lat, lon, alt_m, a_vor, a_dme, frequence_kHz]
    balises_gps = [
        ["DJL", 47.16148, 5.05504, 200.0, True, True, 11145],
        ["RLP", 47.54227, 5.14570, 200.0, True, True, 11735],
        ["LXI", 47.46594, 6.21256, 200.0, False, True, 10820],
        ["EPL", 48.19042, 6.03339, 200.0, True, False, 11300],
        ["LUL", 47.41178, 6.17441, 200.0, True, False, 11710]
    ]
    
    stations = []
    
    for i, balise in enumerate(balises_gps):
        nom = balise[0]
        lat = np.radians(balise[1])
        lon = np.radians(balise[2])
        alt = balise[3]
        a_vor = balise[4]
        a_dme = balise[5]
        
        # Conversion GPS -> NED
        N = rayon_terre * (lat - lat_ref)
        E = rayon_terre * (lon - lon_ref) * np.cos(lat_ref)
        h = alt
        
        station = Station(
            id_station=i+1,
            nom=nom,
            position=[N, E, h],
            a_vor=a_vor,
            a_dme=a_dme,
            frequence_mesure=1.0
        )
        
        stations.append(station)
    
    return stations
