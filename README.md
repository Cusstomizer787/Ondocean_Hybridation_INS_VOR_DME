# Hybridation INS + VOR/DME pour Navigation Aéronautique

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Production-success)
![Tests](https://img.shields.io/badge/Tests-Passing-success)
![License](https://img.shields.io/badge/License-MIT-green)

**Simulation avancée d'hybridation centrale inertielle (INS) et moyens de radionavigation terrestres (VOR/DME) pour aéronefs, avec filtrage de Kalman étendu (EKF), CMKF et IMM.**

## 👥 Auteurs

**Nicolas CUSSEAU** & **Guillaume COSNARD**  
ENSTA Paris - Décembre 2025  
Projet OndOcean Maritime & Remote ID

---

## 📋 Description

Ce projet implémente une simulation complète d'un système de navigation aéronautique hybride combinant:

- **Centrale Inertielle (INS)** - IMU MEMS 6 axes (gyroscopes + accéléromètres)
- **VOR/DME** - Systèmes de radionavigation terrestre
- **Filtrage Avancé** - EKF, CMKF (Constrained Manifold Kalman Filter), et IMM (Interacting Multiple Model)

### Objectifs

✅ Comparer les performances INS seule (dead reckoning) vs INS hybridée  
✅ Démontrer l'apport du filtrage de Kalman pour corriger la dérive inertielle  
✅ Évaluer différentes architectures de filtrage (EKF, CMKF, IMM)  
✅ Tester sur trajectoires réalistes et données GPS réelles

### Classes d'INS

Le projet simule une **INS MEMS Tactical/Industrial Grade** :

| Classe | Biais Gyro | ARW Gyro | Biais Accel | Application |
|--------|------------|----------|-------------|-------------|
| **Navigation Grade** | < 0.001 °/h | < 0.001 °/√h | < 10 μg | Missiles, sous-marins |
| **Tactical Grade** | 0.01-1 °/h | 0.01-0.1 °/√h | 100 μg - 1 mg | Aviation militaire/commerciale |
| **Industrial/Marine** | 1-10 °/h | 0.1-1 °/√h | 1-10 mg | Navires, UAV |
| **Consumer MEMS** | > 10 °/h | > 1 °/√h | > 10 mg | Smartphones, drones |

**Paramètres de ce projet** (classe Tactical bas / Industrial haut) :
- **ARW gyro**: 0.25 °/√h (0.00436 rad/√s)
- **Biais gyro**: 1.08 °/h (0.00524 rad/s)
- **Biais accéléromètre**: 3 mg (0.0294 m/s²)

## 📚 Documentation

- **[Documentation Complète](DOCUMENTATION_COMPLETE.md)** - Architecture et implémentation détaillée
- **[Résultats de Référence](RESULTATS_REFERENCE.md)** - Métriques et performances validées
- **[Guide de Validation](GUIDE_VALIDATION.md)** - Protocoles de test
- **[Changelog](CHANGELOG.md)** - Historique des versions

## 📁 Structure du Projet

```
📦 Ondocean_Hybridation_INS_VOR_DME_V1/
├── 📄 parametres.py                    # Configuration globale et classes de paramètres
├── 📄 modeles_dynamique.py             # Équations d'état, jacobiennes, matrices Q
├── 📄 stations_sol.py                  # Modèles de mesure VOR/DME et visibilité
├── 📄 generateur_trajectoire.py        # Génération trajectoires vérité (5 scénarios)
├── 📄 simulateur_ins.py                # Simulation IMU + intégration strapdown
├── 📄 ekf.py                           # Extended Kalman Filter avec gating adaptatif
├── 📄 cmkf.py                          # Constrained Manifold Kalman Filter
├── 📄 imm.py                           # Interacting Multiple Model (3 modes)
├── 📄 metriques.py                     # RMSE, CEP, statistiques de performance
├── 📄 visualisation.py                 # Plots et animations interactives
├── 📓 simulation_ins_vor_dme.ipynb     # Notebook principal (EKF)
├── 📓 simulation_ins_vor_dme_cmkf.ipynb # Notebook CMKF
├── 📓 simulation_ins_vor_dme_imm.ipynb  # Notebook IMM
├── 📓 estimateur.ipynb                 # Estimateur sur données réelles
├── 📊 data.csv                         # Données GPS réelles
├── 🧪 test_*.py                        # Suite de tests unitaires
├── 📋 requirements.txt                 # Dépendances Python
├── 📖 README.md                        # Documentation principale
└── 📚 docs/                            # Documentation détaillée
```

## 🔬 Caractéristiques Techniques

### Modèle d'État (8D)

Le vecteur d'état est défini dans le repère NED (North-East-Down) :

```
x = [N, E, h, V_N, V_E, ψ, b_g, b_a]ᵀ
```

- **Position** : `N` (Nord), `E` (Est), `h` (altitude) [m]
- **Vitesse** : `V_N`, `V_E` (composantes Nord/Est) [m/s]
- **Attitude** : `ψ` (cap/yaw) [rad]
- **Biais** : `b_g` (gyroscope) [rad/s], `b_a` (accéléromètre) [m/s²]

### Paramètres INS (MEMS Aéronautique)

**Gyroscope** :
- ARW (Angular Random Walk) : 0.25 °/√h (0.00436 rad/√s)
- Biais initial : 1.08 °/h (0.00524 rad/s)
- Modèle Gauss-Markov : τ = 3600 s
- Bruit de processus : 8.73×10⁻⁵ rad/s²

**Accéléromètre** :
- Bruit blanc : 1.47 mg/√Hz (0.00147 m/s²/√Hz)
- Biais initial : 3 mg (0.0294 m/s²)
- Modèle Gauss-Markov : τ = 3600 s
- Bruit de processus : 4.9×10⁻⁴ m/s³

**Fréquence d'échantillonnage** : 100 Hz (dt = 0.01 s)

### Stations VOR/DME

**Configuration géométrique** :
- Station 1 : (0 m, 0 m, 0 m) - VOR/DME
- Station 2 : (80 km, 0 m, 0 m) - VOR/DME
- Station 3 : (40 km, 60 km, 0 m) - VOR/DME

**Performances** :
- **VOR** : précision 1.5° (σ = 0.02618 rad), biais 0.5° (0.00873 rad)
- **DME** : précision 300 m (σ), biais 50 m
- **Portée** : 200 NM (370.4 km)
- **Angle de site minimum** : 3° (0.05236 rad)
- **Fréquence de mesure** : 1 Hz par station

### Architectures de Filtrage

#### 1. EKF (Extended Kalman Filter)
- Prédiction : dynamique INS avec biais Gauss-Markov
- Correction : mesures VOR/DME asynchrones
- Gating adaptatif : χ² (9.21-30.0 selon manœuvre)
- Covariance : forme Joseph pour stabilité numérique

#### 2. CMKF (Constrained Manifold Kalman Filter)
- Projection sur variété après chaque correction
- Contraintes : normalisation cap, limitation biais
- Gating identique à l'EKF
- Amélioration : stabilité en virage coordonné

#### 3. IMM (Interacting Multiple Model)
- 3 modes : rectiligne, virage, accélération
- Matrice de transition adaptative
- Fusion pondérée des estimations
- Amélioration : transitions de manœuvre

### Scénarios de Test

| # | Nom | Description | Durée | Complexité |
|---|-----|-------------|-------|------------|
| 1 | Approche radiale | Vol direct vers station 1 | 20 min | ⭐ Faible |
| 2 | Arc circulaire | Virage 90° autour station 1 | 20 min | ⭐⭐ Moyenne |
| 3 | Transit multi-stations | Navigation entre 3 stations | 20 min | ⭐⭐⭐ Élevée |
| 4 | Trajectoire GPS réelle | Données vol réel (data.csv) | Variable | ⭐⭐⭐ Élevée |
| 5 | Balises réelles France | DJL, RLP, LXI, EPL, LUL | 20 min | ⭐⭐⭐ Élevée |

## 🚀 Installation

### Prérequis

- **Python** ≥ 3.8
- **Git** (pour cloner le dépôt)
- **Jupyter Notebook** (optionnel, pour notebooks interactifs)

### Installation Rapide

```bash
# Cloner le dépôt
git clone https://github.com/Cusstomizer787/Ondocean_Hybridation_INS_VOR_DME.git
cd Ondocean_Hybridation_INS_VOR_DME_V1

# Installer les dépendances
pip install -r requirements.txt
```

### Installation avec Environnement Virtuel (Recommandé)

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Dépendances Principales

```
numpy>=1.21.0       # Calculs numériques
scipy>=1.7.0        # Fonctions scientifiques
matplotlib>=3.4.0   # Visualisation
```

## 💻 Utilisation

### Méthode 1 : Jupyter Notebook (Recommandé)

```bash
# Lancer Jupyter
jupyter notebook

# Ouvrir un des notebooks :
# - simulation_ins_vor_dme.ipynb (EKF)
# - simulation_ins_vor_dme_cmkf.ipynb (CMKF)
# - simulation_ins_vor_dme_imm.ipynb (IMM)
```

**Paramètres configurables** (cellule de configuration) :
```python
numero_scenario = 3  # Choisir entre 1, 2, 3, 4 ou 5
```

### Méthode 2 : Script Python

```python
from parametres import *
from generateur_trajectoire import *
from simulateur_ins import *
from ekf import *
from metriques import *
from visualisation import *

# Charger parametres
params_sim, params_ins, params_vor_dme, params_ekf = charger_parametres_defaut()
stations = creer_stations_sol()

# Generer scenario
verite = generer_verite_scenario_1(params_sim)

# Simuler INS
mesures_imu = generer_mesures_imu_bruitees(verite, params_ins)
x0 = np.array([verite['N'][0], verite['E'][0], verite['h'][0],
               verite['V_N'][0], verite['V_E'][0], verite['psi'][0],
               params_ins.gyro_biais_init, params_ins.accel_biais_init])
traj_ins = integrer_ins_seule(mesures_imu, x0, params_sim, params_ins)

# Simuler EKF (voir notebook pour boucle complete)
```

## 📊 Résultats de Performance

### Scénario 3 : Transit Multi-Stations (20 min)

| Métrique | INS Seule | INS + EKF | Amélioration |
|----------|-----------|-----------|--------------|
| **RMSE 2D** | 31 116 m | 193 m | **99.4%** ✅ |
| **CEP50** | 27 449 m | 141 m | **99.5%** ✅ |
| **CEP95** | 54 073 m | 367 m | **99.3%** ✅ |
| **Erreur max 2D** | 56 264 m | 564 m | **99.0%** ✅ |
| **RMSE cap** | 23.1° | 105.2° | - |

### INS Seule (Dead Reckoning)
- ❌ Dérive importante : ~82 km/h (~44 NM/h)
- ❌ Erreur finale : 27.5 km après 20 minutes
- ❌ Inutilisable pour navigation opérationnelle

### INS + EKF (Hybridée)
- ✅ Correction efficace par mesures VOR/DME
- ✅ Précision métrique maintenue
- ✅ Mesures VOR : 1605 acceptées, 5 rejetées (gating)
- ✅ Mesures DME : 1610 acceptées, 0 rejetées

### Visualisations Disponibles
1. 🗺️ **Trajectoires 2D** - Comparaison vérité/INS/EKF avec stations
2. 📈 **Erreurs temporelles** - Évolution N, E, 2D
3. 📉 **RMSE glissant** - Fenêtre de 60 secondes
4. 🎯 **Innovations EKF** - VOR/DME avec seuils de gating
5. 📊 **Covariance** - Évolution de l'incertitude
6. 🎬 **Animation** - Trajectoire dynamique (vitesse x50)

## Modifications possibles

### Changer parametres INS
Editer `parametres.py`, classe `ParametresINS`:
```python
self.gyro_biais_init = 0.01  # rad/s
self.accel_biais_init = 0.05  # m/s^2
```

### Ajouter stations
Editer `parametres.py`, fonction `creer_stations_sol()`:
```python
Station(id_station=4, nom="Station 4", position=[100000.0, 50000.0, 0.0],
        a_vor=True, a_dme=True, frequence_mesure=1.0)
```

### Creer nouveau scenario
Editer `generateur_trajectoire.py`, ajouter fonction:
```python
def generer_verite_scenario_4(params_sim):
    # Votre trajectoire
    return verite
```

### Modifier EKF
- Gating: `params_ekf.seuil_gating` (9.21 pour 95%)
- Covariance initiale: `params_ekf.P0`
- Bruits mesure: `params_ekf.R_vor`, `params_ekf.R_dme`

## Limitations actuelles

- Altitude constante (pas de dynamique verticale)
- Transitions cap instantanees (pas de modele de virage)
- Pas de masquage terrain
- Pas de multi-path VOR/DME
- Pas de pannes capteurs

## Evolutions futures

- GNSS, ILS, autres aides radionav
- Dynamique 3D complete avec quaternions
- Modele de virage coordonne
- UKF, CKF, IMM, factor graph
- Monte Carlo pour statistiques robustes
- Interface graphique interactive

## References

- Groves, P. D. (2013). Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems
- Titterton, D. H., & Weston, J. L. (2004). Strapdown Inertial Navigation Technology
- Bar-Shalom, Y., Li, X. R., & Kirubarajan, T. (2001). Estimation with Applications to Tracking and Navigation

## Citation

Si vous utilisez ce code dans vos travaux academiques, veuillez citer:

```
CUSSEAU, N. (2025). Simulation INS + VOR/DME avec Filtre de Kalman Etendu.
ENSTA.
https://github.com/Cusstomizer787/Ondocean_Hybridation_INS_VOR_DME
```

## Licence

Projet academique ENSTA - Usage educatif uniquement

## Contact

Nicolas CUSSEAU - Guillaume COSNARD - ENSTA  
Decembre 2025
