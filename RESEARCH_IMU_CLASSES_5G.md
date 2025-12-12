# Research: Configuration Classes IMU et Extension 5G Portuaire

**Date:** 7 décembre 2025  
**Auteur:** Nicolas CUSSEAU - ENSTA ILEMS  
**Contexte:** Extension système INS + VOR/DME vers multi-classes IMU et 5G portuaire

---

## OBJECTIFS DE RECHERCHE

### Objectif 1: Configuration Paramétrique Classes IMU

Permettre la sélection dynamique de classes IMU (consumer → strategic) pour:
- Évaluer l'impact de la qualité IMU sur la dérive
- Quantifier l'apport des aides radionavigation selon la classe
- Préparer l'extension vers 5G portuaire

### Objectif 2: Extension Radionavigation 5G

Adapter l'architecture pour intégrer:
- Mesures 5G (AoA, RTT/ToA, TDoA)
- Architecture Méduse/Anémone
- Environnement portuaire dense

---

## PARTIE 1: ANALYSE ARCHITECTURE ACTUELLE

### 1.1 Structure Paramètres INS

**Fichier:** `parametres.py`

**Classe actuelle:** `ParametresINS` (lignes 20-34)

```python
class ParametresINS:
    def __init__(self):
        # Gyroscope
        self.gyro_arw = 0.00436          # rad/sqrt(s)
        self.gyro_biais_init = 0.00524   # rad/s
        self.gyro_tau_c = 3600.0         # s
        self.gyro_sigma_bruit = 8.73e-5  # rad/s^2
        
        # Accelerometre
        self.accel_bruit = 0.00147       # m/s^2/sqrt(Hz)
        self.accel_biais_init = 0.0294   # m/s^2
        self.accel_tau_c = 3600.0        # s
        self.accel_sigma_bruit = 4.9e-4  # m/s^3
```

**Observation:** Valeurs codées en dur, pas de sélection de classe.

### 1.2 Unités Actuelles vs Unités Standard Industrie

| Paramètre | Unité Actuelle | Unité Industrie | Conversion Nécessaire |
|-----------|----------------|-----------------|----------------------|
| Biais gyro | rad/s | °/h | °/h × π/(180×3600) |
| ARW gyro | rad/√s | °/√h | °/√h × π/(180×60) |
| Biais accel | m/s² | mg | mg × 9.81/1000 |
| Bruit accel | m/s²/√Hz | µg/√Hz | µg/√Hz × 9.81/1e6 |

### 1.3 Classes IMU Standard Industrie

**5 Classes identifiées:**

| Classe | Biais Gyro | ARW Gyro | Biais Accel | Bruit Accel | Application |
|--------|------------|----------|-------------|-------------|-------------|
| Consumer | 20 °/h | 0.5 °/√h | 3 mg | 700 µg/√Hz | Smartphones, drones loisir |
| Industrial | 5 °/h | 0.2 °/√h | 1 mg | 200 µg/√Hz | Robotique, AGV |
| Tactical | 1 °/h | 0.07 °/√h | 0.1 mg | 80 µg/√Hz | Drones militaires, USV |
| Navigation | 0.05 °/h | 0.01 °/√h | 0.02 mg | 30 µg/√Hz | Aviation commerciale |
| Strategic | 0.001 °/h | 0.001 °/√h | 0.005 mg | 10 µg/√Hz | Missiles, sous-marins |

**Classe actuelle du code:** Entre Industrial et Tactical

### 1.4 Impact Dérive Positionnelle

**Dérive estimée après 10 minutes (sans aide externe):**

| Classe | Dérive Position | Dérive Cap | Utilisable Seule? |
|--------|-----------------|------------|-------------------|
| Consumer | 5-10 km | 3-5° | NON |
| Industrial | 1-3 km | 1-2° | NON |
| Tactical | 200-500 m | 0.2-0.5° | Limité (< 5 min) |
| Navigation | 20-50 m | 0.02-0.05° | Oui (< 30 min) |
| Strategic | < 5 m | < 0.01° | Oui (plusieurs heures) |

**Conclusion:** Hybridation INS + radionavigation **obligatoire** pour classes Consumer à Tactical.

---

## PARTIE 2: PROPOSITION ARCHITECTURE MULTI-CLASSES

### 2.1 Nouvelle Structure Paramètres

**Fichier à créer:** `imu_classes.py`

```python
"""
Configuration des classes IMU standard industrie
"""

import numpy as np

# Constantes de conversion
DEG_PER_HOUR_TO_RAD_PER_SEC = np.pi / (180.0 * 3600.0)
DEG_PER_SQRT_HOUR_TO_RAD_PER_SQRT_SEC = np.pi / (180.0 * 60.0)
MG_TO_M_PER_S2 = 9.81 / 1000.0
UG_PER_SQRT_HZ_TO_M_PER_S2_PER_SQRT_HZ = 9.81 / 1e6

# Définition des classes IMU (unités industrie)
IMU_CLASSES = {
    "consumer": {
        "gyro_bias_dph": 20.0,        # °/h
        "gyro_arw_dph_sqrt": 0.5,     # °/√h
        "accel_bias_mg": 3.0,         # mg
        "accel_noise_ug_sqrtHz": 700, # µg/√Hz
        "description": "Smartphones, drones loisir",
        "cost": "< 10 EUR"
    },
    "industrial": {
        "gyro_bias_dph": 5.0,
        "gyro_arw_dph_sqrt": 0.2,
        "accel_bias_mg": 1.0,
        "accel_noise_ug_sqrtHz": 200,
        "description": "Robotique industrielle, AGV",
        "cost": "50-200 EUR"
    },
    "tactical": {
        "gyro_bias_dph": 1.0,
        "gyro_arw_dph_sqrt": 0.07,
        "accel_bias_mg": 0.1,
        "accel_noise_ug_sqrtHz": 80,
        "description": "Drones militaires, USV, véhicules autonomes",
        "cost": "500-2000 EUR"
    },
    "navigation": {
        "gyro_bias_dph": 0.05,
        "gyro_arw_dph_sqrt": 0.01,
        "accel_bias_mg": 0.02,
        "accel_noise_ug_sqrtHz": 30,
        "description": "Aviation commerciale, navigation marine",
        "cost": "5000-20000 EUR"
    },
    "strategic": {
        "gyro_bias_dph": 0.001,
        "gyro_arw_dph_sqrt": 0.001,
        "accel_bias_mg": 0.005,
        "accel_noise_ug_sqrtHz": 10,
        "description": "Missiles, sous-marins, systèmes stratégiques",
        "cost": "> 100000 EUR"
    }
}


def convert_imu_class_to_si(imu_class_name):
    """
    Convertit les paramètres IMU d'une classe vers unités SI
    
    Paramètres:
    -----------
    imu_class_name : str
        Nom de la classe IMU (consumer, industrial, tactical, navigation, strategic)
    
    Retour:
    -------
    dict
        Paramètres convertis en unités SI
    """
    if imu_class_name not in IMU_CLASSES:
        raise ValueError(f"Classe IMU inconnue: {imu_class_name}")
    
    cfg = IMU_CLASSES[imu_class_name]
    
    # Conversion vers SI
    params_si = {
        "gyro_bias": cfg["gyro_bias_dph"] * DEG_PER_HOUR_TO_RAD_PER_SEC,  # rad/s
        "gyro_arw": cfg["gyro_arw_dph_sqrt"] * DEG_PER_SQRT_HOUR_TO_RAD_PER_SQRT_SEC,  # rad/√s
        "accel_bias": cfg["accel_bias_mg"] * MG_TO_M_PER_S2,  # m/s²
        "accel_noise": cfg["accel_noise_ug_sqrtHz"] * UG_PER_SQRT_HZ_TO_M_PER_S2_PER_SQRT_HZ,  # m/s²/√Hz
        "class_name": imu_class_name,
        "description": cfg["description"],
        "cost": cfg["cost"]
    }
    
    return params_si


def create_params_ins_from_class(imu_class_name, tau_c=3600.0):
    """
    Crée un objet ParametresINS à partir d'une classe IMU
    
    Paramètres:
    -----------
    imu_class_name : str
        Nom de la classe IMU
    tau_c : float
        Temps de corrélation Gauss-Markov (s)
    
    Retour:
    -------
    ParametresINS
        Objet paramètres configuré
    """
    from parametres import ParametresINS
    
    params_si = convert_imu_class_to_si(imu_class_name)
    
    params_ins = ParametresINS()
    
    # Gyroscope
    params_ins.gyro_arw = params_si["gyro_arw"]
    params_ins.gyro_biais_init = params_si["gyro_bias"]
    params_ins.gyro_tau_c = tau_c
    params_ins.gyro_sigma_bruit = params_si["gyro_bias"] / np.sqrt(tau_c)  # Gauss-Markov
    
    # Accéléromètre
    params_ins.accel_bruit = params_si["accel_noise"]
    params_ins.accel_biais_init = params_si["accel_bias"]
    params_ins.accel_tau_c = tau_c
    params_ins.accel_sigma_bruit = params_si["accel_bias"] / np.sqrt(tau_c)  # Gauss-Markov
    
    return params_ins


def print_imu_class_comparison():
    """
    Affiche un tableau comparatif des classes IMU
    """
    print("=" * 100)
    print("COMPARAISON CLASSES IMU")
    print("=" * 100)
    print(f"{'Classe':<12} {'Biais Gyro':<15} {'ARW Gyro':<15} {'Biais Accel':<15} {'Bruit Accel':<15}")
    print(f"{'':12} {'(°/h)':<15} {'(°/√h)':<15} {'(mg)':<15} {'(µg/√Hz)':<15}")
    print("-" * 100)
    
    for class_name, cfg in IMU_CLASSES.items():
        print(f"{class_name:<12} {cfg['gyro_bias_dph']:<15.3f} {cfg['gyro_arw_dph_sqrt']:<15.3f} "
              f"{cfg['accel_bias_mg']:<15.3f} {cfg['accel_noise_ug_sqrtHz']:<15.0f}")
    
    print("=" * 100)
    print("\nCONVERSION VERS UNITÉS SI")
    print("=" * 100)
    print(f"{'Classe':<12} {'Biais Gyro':<20} {'ARW Gyro':<20} {'Biais Accel':<20} {'Bruit Accel':<20}")
    print(f"{'':12} {'(rad/s)':<20} {'(rad/√s)':<20} {'(m/s²)':<20} {'(m/s²/√Hz)':<20}")
    print("-" * 100)
    
    for class_name in IMU_CLASSES.keys():
        params_si = convert_imu_class_to_si(class_name)
        print(f"{class_name:<12} {params_si['gyro_bias']:<20.6e} {params_si['gyro_arw']:<20.6e} "
              f"{params_si['accel_bias']:<20.6e} {params_si['accel_noise']:<20.6e}")
    
    print("=" * 100)
```

### 2.2 Modification `parametres.py`

**Ajouter méthode de configuration:**

```python
class ParametresINS:
    """Parametres de la centrale inertielle"""
    
    def __init__(self, imu_class=None):
        """
        Initialise les paramètres INS
        
        Paramètres:
        -----------
        imu_class : str, optional
            Classe IMU (consumer, industrial, tactical, navigation, strategic)
            Si None, utilise valeurs par défaut (tactical)
        """
        if imu_class is not None:
            self._init_from_class(imu_class)
        else:
            self._init_default()
    
    def _init_default(self):
        """Valeurs par défaut (tactical)"""
        # Gyroscope
        self.gyro_arw = 0.00436
        self.gyro_biais_init = 0.00524
        self.gyro_tau_c = 3600.0
        self.gyro_sigma_bruit = 8.73e-5
        
        # Accelerometre
        self.accel_bruit = 0.00147
        self.accel_biais_init = 0.0294
        self.accel_tau_c = 3600.0
        self.accel_sigma_bruit = 4.9e-4
    
    def _init_from_class(self, imu_class):
        """Initialise depuis classe IMU"""
        from imu_classes import create_params_ins_from_class
        params = create_params_ins_from_class(imu_class)
        self.__dict__.update(params.__dict__)
```

### 2.3 Utilisation dans Notebook

```python
# Configuration classe IMU
from imu_classes import IMU_CLASSES, print_imu_class_comparison

# Afficher comparaison
print_imu_class_comparison()

# Sélectionner classe
imu_class = "industrial"  # ou "tactical", "consumer", etc.

# Créer paramètres
params_ins = ParametresINS(imu_class=imu_class)

# Lancer simulation
# ... (reste du code inchangé)
```

---

## PARTIE 3: EXTENSION RADIONAVIGATION 5G

### 3.1 Analogie VOR/DME ↔ 5G

| Système Aéro | Mesure | Équivalent 5G | Observable |
|--------------|--------|---------------|------------|
| VOR | Azimut (angle) | AoA (Angle of Arrival) | Angle d'arrivée signal |
| DME | Distance | RTT/ToA (Round-Trip Time) | Temps aller-retour |
| - | - | TDoA (Time Difference of Arrival) | Multilatération |
| - | - | RSSI/RSRP | Puissance reçue |

### 3.2 Architecture 5G Portuaire

**Composants:**

1. **gNB (gNodeB):** Stations de base 5G (équivalent stations VOR/DME)
2. **UE (User Equipment):** Plateforme mobile (drone, USV)
3. **Méduse:** Altitude informationnelle (fusion multi-capteurs)
4. **Anémone:** Transport optimal distribué (minimise latence/incertitude)

**Densité:** 5-20 gNB par km² en environnement portuaire

### 3.3 Observabilité État INS

**État INS 8D:** [N, E, h, V_N, V_E, ψ, b_g, b_a]

**Observables 5G:**

| Observable | Dimension | Contraint |
|------------|-----------|-----------|
| AoA (azimut) | 1D par gNB | ψ (cap), N, E |
| RTT/ToA (distance) | 1D par gNB | N, E, h |
| TDoA (différence temps) | 1D par paire gNB | N, E, h |
| Doppler | 1D par gNB | V_N, V_E |

**Avec 3+ gNB visibles:** État complètement observable (sauf biais inertiels sur court terme)

### 3.4 Nouvelle Classe Station 5G

**Fichier à créer:** `stations_5g.py`

```python
"""
Module de gestion des stations 5G (gNB) pour radionavigation portuaire
"""

import numpy as np


class Station5G:
    """Classe représentant une station de base 5G (gNodeB)"""
    
    def __init__(self, id_station, nom, position, frequence_mesure, 
                 capabilities=None):
        """
        Paramètres:
        -----------
        id_station : int
            Identifiant unique
        nom : str
            Nom de la station
        position : np.ndarray (3,)
            Position [N, E, h] en mètres
        frequence_mesure : float
            Fréquence de mesure (Hz)
        capabilities : dict
            Capacités de mesure {'aoa': bool, 'rtt': bool, 'tdoa': bool}
        """
        self.id = id_station
        self.nom = nom
        self.position = np.array(position, dtype=float)
        self.frequence_mesure = frequence_mesure
        
        # Capacités par défaut
        if capabilities is None:
            self.capabilities = {
                'aoa': True,   # Angle of Arrival
                'rtt': True,   # Round-Trip Time
                'tdoa': True,  # Time Difference of Arrival
                'rssi': True   # Received Signal Strength
            }
        else:
            self.capabilities = capabilities
        
        self.prochain_temps_mesure = 1.0 / frequence_mesure
    
    @property
    def N(self):
        return self.position[0]
    
    @property
    def E(self):
        return self.position[1]
    
    @property
    def h(self):
        return self.position[2]


class Parametres5G:
    """Paramètres des mesures 5G"""
    
    def __init__(self):
        # AoA (Angle of Arrival)
        self.aoa_sigma = 0.0349  # rad (2°)
        self.aoa_biais = 0.0087  # rad (0.5°)
        
        # RTT/ToA (Round-Trip Time / Time of Arrival)
        self.rtt_sigma = 10.0  # m (équivalent distance)
        self.rtt_biais = 2.0   # m
        
        # TDoA (Time Difference of Arrival)
        self.tdoa_sigma = 5.0  # m (équivalent distance)
        
        # RSSI/RSRP (Received Signal Strength)
        self.rssi_sigma = 3.0  # dBm
        
        # Contraintes visibilité
        self.portee_max = 2000.0  # m (portée 5G en environnement urbain)
        self.angle_site_min = 0.0  # rad (pas de contrainte site en portuaire)
        self.nlos_degradation = 3.0  # Facteur dégradation NLOS


def creer_reseau_5g_portuaire(densite="dense"):
    """
    Crée un réseau de gNB 5G pour environnement portuaire
    
    Paramètres:
    -----------
    densite : str
        'sparse' (5 gNB), 'medium' (10 gNB), 'dense' (20 gNB)
    
    Retour:
    -------
    list[Station5G]
        Liste des stations 5G
    """
    if densite == "sparse":
        # Configuration minimale (5 gNB)
        positions = [
            [0, 0, 15],          # Quai principal
            [500, 0, 15],        # Terminal conteneurs
            [0, 500, 15],        # Zone logistique
            [500, 500, 15],      # Centre port
            [250, 250, 30]       # Tour de contrôle
        ]
    elif densite == "medium":
        # Configuration moyenne (10 gNB)
        positions = [
            [0, 0, 15], [500, 0, 15], [1000, 0, 15],
            [0, 500, 15], [500, 500, 15], [1000, 500, 15],
            [0, 1000, 15], [500, 1000, 15],
            [250, 250, 30], [750, 750, 30]
        ]
    else:  # dense
        # Configuration dense (20 gNB) - Grille 5x4
        positions = []
        for i in range(5):
            for j in range(4):
                h = 15 if (i + j) % 2 == 0 else 20
                positions.append([i * 250, j * 250, h])
    
    stations = []
    for idx, pos in enumerate(positions):
        stations.append(Station5G(
            id_station=idx + 1,
            nom=f"gNB_{idx+1}",
            position=pos,
            frequence_mesure=10.0  # 10 Hz (5G plus rapide que VOR/DME)
        ))
    
    return stations
```

### 3.5 Modèles de Mesure 5G

**Fichier à créer:** `modeles_5g.py`

```python
"""
Modèles de mesure pour radionavigation 5G
"""

import numpy as np


def modele_mesure_aoa(x, station_5g):
    """
    Modèle de mesure AoA (Angle of Arrival)
    Analogue au VOR
    
    Paramètres:
    -----------
    x : np.ndarray (8,)
        État INS [N, E, h, V_N, V_E, psi, b_g, b_a]
    station_5g : Station5G
        Station 5G
    
    Retour:
    -------
    float
        Azimut prédit (rad)
    """
    delta_N = x[0] - station_5g.N
    delta_E = x[1] - station_5g.E
    azimut = np.arctan2(delta_E, delta_N)
    azimut = np.mod(azimut + np.pi, 2*np.pi) - np.pi
    return azimut


def modele_mesure_rtt(x, station_5g):
    """
    Modèle de mesure RTT (Round-Trip Time)
    Analogue au DME
    
    Paramètres:
    -----------
    x : np.ndarray (8,)
        État INS
    station_5g : Station5G
        Station 5G
    
    Retour:
    -------
    float
        Distance prédite (m)
    """
    delta_N = x[0] - station_5g.N
    delta_E = x[1] - station_5g.E
    delta_h = x[2] - station_5g.h
    distance = np.sqrt(delta_N**2 + delta_E**2 + delta_h**2)
    return distance


def modele_mesure_tdoa(x, station_5g_1, station_5g_2):
    """
    Modèle de mesure TDoA (Time Difference of Arrival)
    Différence de distance entre 2 stations
    
    Paramètres:
    -----------
    x : np.ndarray (8,)
        État INS
    station_5g_1, station_5g_2 : Station5G
        Paire de stations 5G
    
    Retour:
    -------
    float
        Différence de distance (m)
    """
    d1 = modele_mesure_rtt(x, station_5g_1)
    d2 = modele_mesure_rtt(x, station_5g_2)
    return d1 - d2


def jacobienne_H_aoa(x, station_5g):
    """
    Jacobienne du modèle AoA
    """
    delta_N = x[0] - station_5g.N
    delta_E = x[1] - station_5g.E
    d2 = delta_N**2 + delta_E**2
    
    H = np.zeros((1, 8))
    H[0, 0] = -delta_E / d2  # dh/dN
    H[0, 1] = delta_N / d2   # dh/dE
    return H


def jacobienne_H_rtt(x, station_5g):
    """
    Jacobienne du modèle RTT
    """
    delta_N = x[0] - station_5g.N
    delta_E = x[1] - station_5g.E
    delta_h = x[2] - station_5g.h
    d = np.sqrt(delta_N**2 + delta_E**2 + delta_h**2)
    
    if d < 1e-6:
        d = 1e-6
    
    H = np.zeros((1, 8))
    H[0, 0] = delta_N / d  # dh/dN
    H[0, 1] = delta_E / d  # dh/dE
    H[0, 2] = delta_h / d  # dh/dh
    return H


def jacobienne_H_tdoa(x, station_5g_1, station_5g_2):
    """
    Jacobienne du modèle TDoA
    """
    H1 = jacobienne_H_rtt(x, station_5g_1)
    H2 = jacobienne_H_rtt(x, station_5g_2)
    return H1 - H2
```

---

## PARTIE 4: ARCHITECTURE MÉDUSE/ANÉMONE

### 4.1 Méduse: Altitude Informationnelle

**Concept:** Fusion multi-capteurs pour réduire distance informationnelle

**Capteurs à fusionner:**
- INS (haute fréquence, dérive)
- 5G (AoA, RTT, TDoA)
- GNSS RTK (précis mais vulnérable)
- LoRaWAN (longue portée, faible débit)
- Balises locales (UWB, WiFi)

**Architecture:**

```
┌─────────────────────────────────────────────┐
│           MÉDUSE (Fusion Layer)             │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │   INS   │  │   5G    │  │  GNSS   │   │
│  │ 100 Hz  │  │  10 Hz  │  │  1 Hz   │   │
│  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │         │
│       └────────────┼────────────┘         │
│                    │                      │
│            ┌───────▼───────┐              │
│            │  EKF Adaptatif │              │
│            │  Multi-Capteurs│              │
│            └───────┬───────┘              │
│                    │                      │
│            État Fusionné                  │
│            [N,E,h,V,ψ,biais]             │
└────────────────────┼───────────────────────┘
                     │
                     ▼
            ANÉMONE (Distribution)
```

### 4.2 Anémone: Transport Optimal Distribué

**Concept:** Minimiser latence, incertitude, fragmentation

**Problème de transport optimal:**

```
min  ∫∫ c(x,y) dπ(x,y)
π

où:
- x: source de données (capteur, station)
- y: usage (plateforme, opérateur)
- c(x,y): coût transport (latence, incertitude)
- π: plan de transport
```

**Contraintes:**
- Latence < 100 ms (temps réel)
- Incertitude < seuil sécurité
- Bande passante limitée

**Implémentation:**
- Algorithme Sinkhorn (régularisation entropique)
- Distribution edge computing
- Priorisation flux critiques

### 4.3 Intégration Système Global

```
┌──────────────────────────────────────────────────────────┐
│                  ENVIRONNEMENT PORTUAIRE                  │
│                                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  gNB 1  │  │  gNB 2  │  │  gNB 3  │  │  gNB N  │   │
│  │  (5G)   │  │  (5G)   │  │  (5G)   │  │  (5G)   │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│       └────────────┼────────────┼────────────┘         │
│                    │            │                      │
│            ┌───────▼────────────▼───────┐              │
│            │   ANÉMONE (Edge Layer)     │              │
│            │   - Routage optimal        │              │
│            │   - Minimise latence       │              │
│            └───────┬────────────────────┘              │
│                    │                                   │
│            ┌───────▼───────┐                           │
│            │     MÉDUSE     │                           │
│            │  (Fusion INS   │                           │
│            │   + 5G + GNSS) │                           │
│            └───────┬───────┘                           │
│                    │                                   │
│            ┌───────▼───────┐                           │
│            │  PLATEFORME   │                           │
│            │  (Drone/USV)  │                           │
│            │  - INS onboard│                           │
│            │  - Récepteur  │                           │
│            └───────────────┘                           │
└──────────────────────────────────────────────────────────┘
```

---

## PARTIE 5: PLAN D'IMPLÉMENTATION

### 5.1 Phase 1: Multi-Classes IMU (Court Terme - 1 semaine)

**Objectif:** Permettre sélection classe IMU et quantifier impact

**Tâches:**
1. Créer `imu_classes.py` avec conversions
2. Modifier `ParametresINS` pour accepter classe
3. Ajouter sélection dans notebook
4. Exécuter 3 scénarios × 5 classes = 15 simulations
5. Documenter résultats comparatifs

**Livrables:**
- Module `imu_classes.py`
- Notebook mis à jour
- Document `RESULTATS_MULTI_CLASSES.md`
- Graphiques comparatifs dérive vs classe

### 5.2 Phase 2: Extension 5G (Moyen Terme - 2-3 semaines)

**Objectif:** Intégrer mesures 5G (AoA, RTT, TDoA)

**Tâches:**
1. Créer `stations_5g.py` (classe Station5G)
2. Créer `modeles_5g.py` (modèles mesure + jacobiennes)
3. Étendre `ekf.py` pour mesures 5G
4. Créer générateur réseau 5G portuaire
5. Simuler scénarios portuaires (USV, drone)
6. Comparer INS+VOR/DME vs INS+5G

**Livrables:**
- Modules 5G complets
- EKF multi-capteurs
- Scénarios portuaires
- Document `RESULTATS_5G.md`

### 5.3 Phase 3: Méduse/Anémone (Long Terme - 1-2 mois)

**Objectif:** Architecture fusion distribuée

**Tâches:**
1. Implémenter couche Méduse (fusion multi-capteurs)
2. Implémenter couche Anémone (transport optimal)
3. Simuler environnement portuaire dense
4. Évaluer robustesse dégradation GNSS
5. Benchmarking performance

**Livrables:**
- Architecture complète
- Simulations réalistes
- Publication scientifique

---

## PARTIE 6: MÉTRIQUES ET VALIDATION

### 6.1 Métriques Multi-Classes IMU

**Pour chaque classe IMU:**
- Dérive position après 1, 5, 10, 20 min (sans aide)
- Amélioration avec VOR/DME (%)
- Taux acceptation mesures
- Erreur RMS 2D finale
- CEP50, CEP95

**Tableau attendu:**

| Classe | Dérive 10min | RMSE avec VOR/DME | Amélioration | Coût |
|--------|--------------|-------------------|--------------|------|
| Consumer | 5-10 km | 200-300 m | 99.5% | < 10 EUR |
| Industrial | 1-3 km | 180-250 m | 99.3% | 50-200 EUR |
| Tactical | 200-500 m | 150-200 m | 98.5% | 500-2000 EUR |
| Navigation | 20-50 m | 50-100 m | 90% | 5-20k EUR |
| Strategic | < 5 m | 10-20 m | 50% | > 100k EUR |

**Conclusion attendue:** Classes Consumer à Tactical bénéficient massivement de l'hybridation (> 98%), justifiant l'approche.

### 6.2 Métriques 5G vs VOR/DME

**Comparaison:**

| Métrique | VOR/DME | 5G (dense) | 5G (sparse) |
|----------|---------|------------|-------------|
| Fréquence mesure | 1 Hz | 10 Hz | 10 Hz |
| Précision azimut | 1.5° | 2° | 2° |
| Précision distance | 300 m | 10 m | 10 m |
| Portée | 200 NM | 2 km | 2 km |
| Densité stations | 3 | 20 | 5 |
| Observabilité cap | Partielle | Complète | Complète |
| Robustesse NLOS | Bonne | Moyenne | Moyenne |

**Hypothèse:** 5G dense (20 gNB) surpasse VOR/DME en précision et observabilité, mais sensible NLOS.

---

## PARTIE 7: APPLICATIONS ET IMPACT

### 7.1 Cas d'Usage Portuaire

**1. Drones de Surveillance:**
- Classe IMU: Industrial ou Tactical
- Radionavigation: 5G dense + GNSS RTK
- Précision requise: < 1 m
- Autonomie: 20-30 min

**2. USV (Unmanned Surface Vehicles):**
- Classe IMU: Tactical
- Radionavigation: 5G + LoRaWAN + GNSS
- Précision requise: < 5 m
- Autonomie: Plusieurs heures

**3. AGV Portuaires:**
- Classe IMU: Industrial
- Radionavigation: 5G + UWB + Balises
- Précision requise: < 0.5 m
- Environnement: Quais, terminaux

### 7.2 Sûreté Portuaire

**Bénéfices Méduse/Anémone:**
- Détection intrusion (drones, bateaux)
- Coordination équipes sécurité
- Surveillance zones sensibles
- Réponse rapide incidents

**Contraintes:**
- Latence < 100 ms (temps réel)
- Disponibilité > 99.9%
- Robustesse dégradation GNSS
- Cybersécurité (authentification 5G)

### 7.3 Impact Scientifique

**Contributions:**
1. Architecture fusion multi-capteurs distribuée (Méduse)
2. Transport optimal temps réel (Anémone)
3. Radionavigation 5G pour navigation maritime
4. Quantification apport hybridation selon classe IMU

**Publications potentielles:**
- IEEE/ION GNSS+ (navigation)
- IEEE ICRA (robotique)
- IFAC (contrôle automatique)
- Revue maritime (applications)

---

## CONCLUSION RECHERCHE

### Synthèse

**Configuration Multi-Classes IMU:**
- Architecture modulaire permettant sélection dynamique
- Conversions unités industrie → SI automatisées
- Quantification impact qualité IMU sur dérive
- Justification hybridation pour classes Consumer-Tactical

**Extension 5G Portuaire:**
- Analogie VOR/DME ↔ 5G (AoA, RTT, TDoA)
- Observabilité complète état INS avec réseau dense
- Architecture Méduse/Anémone pour fusion distribuée
- Cas d'usage portuaire (drones, USV, AGV)

### Prochaines Étapes

**Immédiat (1 semaine):**
1. Implémenter `imu_classes.py`
2. Modifier `parametres.py`
3. Exécuter simulations multi-classes
4. Documenter résultats

**Court terme (1 mois):**
5. Implémenter modules 5G
6. Étendre EKF pour mesures 5G
7. Simuler scénarios portuaires

**Moyen terme (2-3 mois):**
8. Architecture Méduse/Anémone
9. Validation environnement réel
10. Publication scientifique

---

**Recherche complète - Prêt pour implémentation Phase 1.**

**Document de référence pour extension système INS + VOR/DME vers multi-classes IMU et 5G portuaire.**
