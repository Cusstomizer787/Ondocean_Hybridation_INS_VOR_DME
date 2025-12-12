# Simulation INS + VOR/DME

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Fonctionnel-success)
![Tests](https://img.shields.io/badge/Tests-Valides-success)

Simulation d'hybridation centrale inertielle (INS) et moyens de radionavigation terrestres (VOR/DME) pour aeronef.

## Auteur

Nicolas CUSSEAU - ENSTA Bretagne - Projet SAFRAN - Decembre 2025

## Description

Ce projet simule un aeronef equipe d'une centrale inertielle strapdown (IMU 6 axes) et de recepteurs VOR/DME. L'objectif est de comparer les performances de l'INS seule (dead reckoning) avec une solution hybridee INS + VOR/DME via un filtre de Kalman etendu (EKF).

## Documentation

- **[Documentation Complete](DOCUMENTATION_COMPLETE.md)** - Guide complet du projet
- **[Resultats de Reference](RESULTATS_REFERENCE.md)** - Metriques et performances attendues
- **[Guide de Validation](GUIDE_VALIDATION.md)** - Tests et validation
- **[Changelog](CHANGELOG.md)** - Historique des versions

## Structure du projet

```
Codebase/
├── parametres.py              # Configuration globale
├── modeles_dynamique.py       # Equations d'etat, jacobiennes
├── stations_sol.py            # Modeles de mesure VOR/DME
├── generateur_trajectoire.py  # Generation trajectoires verite (3 scenarios)
├── simulateur_ins.py          # Simulation IMU + integration strapdown
├── ekf.py                     # Filtre de Kalman etendu avec gating
├── metriques.py               # RMSE, CEP, statistiques
├── visualisation.py           # Plots et animations
├── simulation_ins_vor_dme.ipynb  # Notebook principal
└── README.md                  # Ce fichier
```

## Caracteristiques techniques

### Modele d'etat (8D)
- Position: N (Nord), E (Est), h (altitude)
- Vitesse: V_N, V_E (composantes Nord/Est)
- Cap: psi (yaw)
- Biais: b_g (gyroscope), b_a (accelerometre)

### Parametres INS (MEMS aeronautique)
- Gyroscope: ARW 0.15 deg/sqrt(h), biais 0.3 deg/s, Gauss-Markov tau=3600s
- Accelerometre: bruit 150 ug/sqrt(Hz), biais 3 mg, Gauss-Markov tau=3600s

### Stations VOR/DME
- 3 stations au sol: (0,0), (80km,0), (40km,60km)
- VOR: precision 1.5 deg, biais 0.5 deg
- DME: precision 300 m, biais 50 m
- Portee: 200 NM, angle site min: 3 deg

### EKF
- Prediction: dynamique INS avec biais Gauss-Markov
- Correction: mesures VOR/DME asynchrones (1 Hz par station)
- Gating: test chi2 a 95% (seuil 9.21)
- Metriques: RMSE glissant (fenetre 60s), CEP50/95

### Scenarios
1. Approche radiale vers station 1
2. Arc circulaire autour station 1
3. Transit multi-stations
4. Trajectoire reelle GPS (data.csv)
5. Transit balises reelles (DJL, RLP, LXI, EPL, LUL)

## Installation

### Prerequis
- Python 3.8+
- numpy
- scipy
- matplotlib

### Installation dependances

```bash
pip install numpy scipy matplotlib
```

Ou avec un environnement virtuel:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install numpy scipy matplotlib
```

## Utilisation

### Execution notebook

1. Ouvrir Jupyter:
```bash
jupyter notebook simulation_ins_vor_dme.ipynb
```

2. Executer les cellules dans l'ordre

3. Choisir le scenario (cellule 3):
```python
numero_scenario = 1  # 1, 2, 3, 4 ou 5
```

### Execution depuis Python

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

## Resultats attendus

### INS seule
- Derive importante sur 20 min (plusieurs km)
- RMSE 2D: 1000-5000 m selon scenario
- CEP95: 2000-8000 m

### INS + EKF
- Correction efficace par VOR/DME
- RMSE 2D: 100-500 m selon scenario
- CEP95: 200-800 m
- Amelioration: 70-90%

### Visualisations
- Trajectoires 2D comparatives
- Erreurs temporelles N/E/2D
- RMSE glissant
- Innovations EKF (gating)
- Evolution covariance
- Animation trajectoires (x10)

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
Projet SAFRAN, ENSTA Bretagne.
https://github.com/[votre-repo]/INS-VOR-DME-Simulation
```

## Licence

Projet academique ENSTA Bretagne - Usage educatif uniquement

## Contact

Nicolas CUSSEAU - ENSTA Bretagne  
Projet SAFRAN - Decembre 2025
