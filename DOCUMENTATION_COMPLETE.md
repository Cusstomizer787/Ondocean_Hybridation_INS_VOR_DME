# Documentation Complète - Simulation INS + VOR/DME

## 1. Introduction

### Contexte du Projet

Ce projet implémente une simulation complète d'hybridation entre une **centrale inertielle strapdown (INS)** et des **moyens de radionavigation terrestres (VOR/DME)** pour un aéronef.

L'objectif est de démontrer l'apport de la fusion de données via un **filtre de Kalman étendu (EKF)** pour corriger la dérive inertielle inhérente aux centrales inertielles MEMS.

### Objectifs de la Simulation

1. **Comparer** les performances d'une INS seule (dead reckoning) avec une solution hybridée INS + VOR/DME
2. **Évaluer** l'amélioration apportée par l'EKF sur différents scénarios de trajectoire
3. **Analyser** l'impact de la géométrie des stations au sol sur la précision
4. **Fournir** un outil pédagogique pour comprendre la fusion de capteurs

### Résumé des Fonctionnalités

- Simulation de 3 scénarios de vol réalistes
- Modèle INS 8D avec biais gyroscope/accéléromètre évolutifs (Gauss-Markov)
- Modèles de mesure VOR (azimut) et DME (distance oblique)
- EKF avec gating chi2 pour rejeter les mesures aberrantes
- Métriques de performance: RMSE, CEP50/95, erreurs temporelles
- Visualisations: trajectoires 2D, erreurs, RMSE glissant, innovations, covariance
- Animation des trajectoires

### Auteur

**Nicolas CUSSEAU**  
ENSTA Bretagne - Projet SAFRAN  
Décembre 2025

---

## 2. Architecture du Code

### Structure des Fichiers

```
Codebase/
├── parametres.py              # Configuration globale
├── modeles_dynamique.py       # Équations d'état INS
├── stations_sol.py            # Modèles de mesure VOR/DME
├── generateur_trajectoire.py  # Génération scénarios
├── simulateur_ins.py          # Simulation IMU + intégration
├── ekf.py                     # Filtre de Kalman étendu
├── metriques.py               # Calcul performances
├── visualisation.py           # Plots et animations
├── simulation_ins_vor_dme.ipynb  # Notebook principal
├── test_scenarios.py          # Tests automatisés
├── README.md                  # Documentation principale
└── GUIDE_VALIDATION.md        # Guide de validation
```

### Description des Modules

#### `parametres.py`

**Rôle:** Centralise toute la configuration de la simulation.

**Classes:**
- `ParametresSimulation`: Paramètres temporels (dt, durée)
- `ParametresINS`: Caractéristiques gyroscope/accéléromètre
- `ParametresVORDME`: Précision et portée VOR/DME
- `ParametresEKF`: Matrices de covariance, seuil gating
- `Station`: Définition d'une station au sol

**Fonctions:**
- `charger_parametres_defaut()`: Charge configuration standard
- `creer_stations_sol()`: Crée les 3 stations VOR/DME

#### `modeles_dynamique.py`

**Rôle:** Implémente les équations de dynamique INS.

**Fonctions:**
- `dynamique_ins()`: Modèle de transition d'état (Euler)
- `jacobienne_F()`: Jacobienne de la dynamique (pour EKF)
- `matrice_Q()`: Matrice de bruit de processus

**Équations clés:**
- Intégration position: N_next = N + V_N * dt
- Intégration vitesse: V_N_next = V_N + a_N_ned * dt
- Rotation corps→NED: a_N_ned = a_N * cos(ψ) - a_E * sin(ψ)
- Biais Gauss-Markov: b_next = b * (1 - β*dt) + w

#### `stations_sol.py`

**Rôle:** Modèles de mesure VOR/DME et tests de visibilité.

**Fonctions:**
- `modele_mesure_vor()`: Calcul azimut prédit
- `modele_mesure_dme()`: Calcul distance oblique prédite
- `jacobienne_H_vor()`: Jacobienne mesure VOR
- `jacobienne_H_dme()`: Jacobienne mesure DME
- `verifier_visibilite()`: Tests portée et angle de site

**Équations:**
- VOR: θ = atan2(E - E_s, N - N_s)
- DME: ρ = √[(N-N_s)² + (E-E_s)² + (h-h_s)²]

#### `generateur_trajectoire.py`

**Rôle:** Génère les trajectoires vérité pour les 3 scénarios.

**Fonctions:**
- `generer_verite_scenario_1()`: Approche radiale avec accélérations
- `generer_verite_scenario_2()`: Arc circulaire
- `generer_verite_scenario_3()`: Transit multi-stations avec virages

**Sorties:** Dictionnaire avec t, N, E, h, V_N, V_E, ψ, a_N_corps, a_E_corps, omega_z

#### `simulateur_ins.py`

**Rôle:** Simule les mesures IMU et intègre l'INS.

**Fonctions:**
- `generer_mesures_imu_bruitees()`: Ajoute bruit + biais aux mesures
- `integrer_ins_seule()`: Dead reckoning sans correction

#### `ekf.py`

**Rôle:** Implémente le filtre de Kalman étendu.

**Classe `EKF`:**
- `__init__()`: Initialisation état et covariance
- `prediction()`: Prédiction avec modèle INS
- `update_vor()`: Correction avec mesure VOR (+ gating)
- `update_dme()`: Correction avec mesure DME (+ gating)
- `sauvegarder_etat()`: Stockage historique

**Algorithme:**
1. Prédiction: x̂ = f(x, u), P = F P F^T + Q
2. Innovation: y = z - h(x̂)
3. Gating: d² = y^T S^(-1) y < seuil
4. Correction: x = x̂ + K y, P = (I - K H) P

#### `metriques.py`

**Rôle:** Calcul des métriques de performance.

**Fonctions:**
- `calculer_erreurs()`: Erreurs N, E, h, 2D, cap
- `rmse_glissant()`: RMSE sur fenêtre mobile
- `calculer_cep()`: Circular Error Probable
- `cep_glissant()`: CEP sur fenêtre mobile
- `statistiques_finales()`: RMSE, max, CEP50/95

#### `visualisation.py`

**Rôle:** Génération de figures et animations.

**Fonctions:**
- `plot_trajectoires_2D()`: Vue de dessus avec stations
- `plot_erreurs_temporelles()`: Erreurs N, E, 2D vs temps
- `plot_rmse_glissant()`: RMSE évolutif
- `plot_innovations_ekf()`: Innovations VOR/DME
- `plot_covariance_ekf()`: Évolution incertitude
- `animer_trajectoires()`: Animation matplotlib

### Flux de Données

```
[Paramètres] → [Générateur Trajectoire] → [Vérité]
                                              ↓
[Vérité] → [Simulateur INS] → [Mesures IMU bruitées]
                                              ↓
[Mesures IMU] → [Intégration INS] → [Trajectoire INS seule]
                                              ↓
[Mesures IMU] + [Mesures VOR/DME] → [EKF] → [Trajectoire INS+EKF]
                                              ↓
[Vérité] + [INS] + [EKF] → [Métriques] → [Statistiques]
                                              ↓
                                      [Visualisation]
```

---

## 3. Modèles Mathématiques

### État du Système

Vecteur d'état 8D:

```
x = [N, E, h, V_N, V_E, ψ, b_g, b_a]^T
```

Où:
- N, E: Position Nord/Est (m)
- h: Altitude (m)
- V_N, V_E: Vitesse Nord/Est (m/s)
- ψ: Cap (rad)
- b_g: Biais gyroscope (rad/s)
- b_a: Biais accéléromètre (m/s²)

### Équations de Dynamique INS

**Modèle continu:**

```
dN/dt = V_N
dE/dt = V_E
dh/dt = 0  (altitude constante)
dV_N/dt = a_N_ned
dV_E/dt = a_E_ned
dψ/dt = ω_z - b_g
db_g/dt = -β_g * b_g + w_bg
db_a/dt = -β_a * b_a + w_ba
```

**Rotation repère corps → NED:**

```
a_N_ned = (a_N_corps - b_a) * cos(ψ) - (a_E_corps - b_a) * sin(ψ)
a_E_ned = (a_N_corps - b_a) * sin(ψ) + (a_E_corps - b_a) * cos(ψ)
```

**Discrétisation Euler (dt = 0.01s):**

```
x_{k+1} = x_k + f(x_k, u_k) * dt
```

### Modèles de Mesure VOR/DME

**VOR (azimut):**

```
z_VOR = atan2(E - E_s, N - N_s) + v_θ
```

Avec v_θ ~ N(0, σ²_VOR)

**DME (distance oblique):**

```
z_DME = √[(N-N_s)² + (E-E_s)² + (h-h_s)²] + v_ρ
```

Avec v_ρ ~ N(0, σ²_DME)

### Équations EKF

**Prédiction:**

```
x̂_{k|k-1} = f(x_{k-1|k-1}, u_k)
P_{k|k-1} = F_k P_{k-1|k-1} F_k^T + Q_k
```

**Correction:**

```
y_k = z_k - h(x̂_{k|k-1})  (innovation)
S_k = H_k P_{k|k-1} H_k^T + R_k  (covariance innovation)
K_k = P_{k|k-1} H_k^T S_k^(-1)  (gain Kalman)
x̂_{k|k} = x̂_{k|k-1} + K_k y_k
P_{k|k} = (I - K_k H_k) P_{k|k-1}
```

**Gating:**

```
d² = y_k^T S_k^(-1) y_k
Si d² > χ²_{0.95}(2) = 9.21 → rejeter mesure
```

### Matrices de Covariance

**P0 (covariance initiale):**

```
P0 = diag([100², 100², 50², 5², 5², 0.1², 0.01², 0.05²])
```

**Q (bruit de processus):**

```
Q = diag([0, 0, 0, 0, 0, 0, σ²_bg*dt, σ²_ba*dt])
```

**R (bruit de mesure):**

```
R_VOR = (0.02618)² rad²  (1.5°)
R_DME = (300)² m²
```

---

## 4. Scénarios de Simulation

### Scénario 1: Approche Radiale avec Profil Réaliste

**Description:**
Approche vers station 1 avec profil de vitesse réaliste incluant accélérations, décélérations et virage 180°.

**Phases:**
1. 0-100s: Accélération 50→100 m/s (a = 0.5 m/s²)
2. 100-500s: Croisière 100 m/s
3. 500-600s: Décélération 100→50 m/s (a = -0.5 m/s²)
4. 600-663s: Virage 180° coordonné (R = 1000m, a_c = 2.5 m/s²)
5. 663-763s: Accélération 50→100 m/s
6. 763-1163s: Croisière retour 100 m/s
7. 1163-1200s: Décélération finale

**Accélérations attendues:**
- Longitudinale: 0.5 à 1.25 m/s²
- Centripète (virage): 2.5 m/s²
- Vitesse angulaire: 0.05 rad/s

**Résultats typiques:**
- Dérive INS: 1500-3000 m
- Erreur EKF: 200-600 m
- Amélioration: 70-85%

### Scénario 2: Arc Circulaire

**Description:**
Trajectoire circulaire rayon 50 km autour de station 1.

**Paramètres:**
- Rayon: R = 50000 m
- Vitesse: V = 150 m/s
- Vitesse angulaire: ω = V/R = 0.003 rad/s
- Accélération centripète: a_c = V²/R = 4.5 m/s²

**Résultats typiques:**
- Dérive INS: 2000-4000 m
- Erreur EKF: 150-400 m
- Amélioration: 80-95%

### Scénario 3: Transit Multi-Stations

**Description:**
Trajectoire polygonale passant près des 3 stations avec virages coordonnés.

**Waypoints:**
1. Départ: (-20000, -20000)
2. Station 1: (0, 0)
3. Station 2: (80000, 0)
4. Station 3: (40000, 60000)
5. Arrivée: (40000, 80000)

**Paramètres:**
- Vitesse croisière: 120 m/s
- Vitesse virage: 80 m/s
- Rayon virages: 2000 m
- Accélération: ±0.8 m/s²

**Résultats typiques:**
- Dérive INS: 1200-2500 m
- Erreur EKF: 200-500 m
- Amélioration: 70-85%

---

## 5. Paramètres de Configuration

### Paramètres INS (MEMS Aéronautique)

**Gyroscope:**
- Bruit ARW: 0.15 °/√h = 0.00436 rad/√s
- Biais initial: 0.3 °/s = 0.00524 rad/s
- Temps corrélation: τ_g = 3600 s
- Écart-type bruit processus: σ_bg = 8.73e-5 rad/s²

**Accéléromètre:**
- Bruit: 150 µg/√Hz = 0.00147 m/s²/√Hz
- Biais initial: 3 mg = 0.0294 m/s²
- Temps corrélation: τ_a = 3600 s
- Écart-type bruit processus: σ_ba = 4.9e-4 m/s³

### Paramètres VOR/DME

**VOR:**
- Écart-type azimut: 1.5° = 0.02618 rad
- Biais systématique: 0.5° = 0.00873 rad

**DME:**
- Écart-type distance: 300 m
- Biais systématique: 50 m

**Contraintes:**
- Portée maximale: 200 NM = 370400 m
- Angle site minimum: 3° = 0.05236 rad

### Paramètres EKF

**Covariance initiale P0:**
- Position: 100 m std
- Vitesse: 5 m/s std
- Cap: 0.1 rad std
- Biais gyro: 0.01 rad/s std
- Biais accel: 0.05 m/s² std

**Gating:**
- Seuil chi2: 9.21 (95%, 2 DDL)

**Métriques:**
- Fenêtre RMSE glissant: 60 s

### Comment Modifier les Paramètres

**Éditer `parametres.py`:**

```python
# Exemple: changer précision gyroscope
class ParametresINS:
    def __init__(self):
        self.gyro_arw = 0.002  # Meilleur gyro
        self.gyro_biais_init = 0.001  # Biais plus faible
```

**Éditer stations:**

```python
def creer_stations_sol():
    stations = [
        Station(1, "Station 1", [0, 0, 0], True, True, 1.0),
        Station(2, "Station 2", [100000, 0, 0], True, True, 1.0),  # Plus loin
        # Ajouter station 4:
        Station(4, "Station 4", [50000, 50000, 0], True, True, 1.0)
    ]
    return stations
```

---

## 6. Guide d'Utilisation

### Installation

**Prérequis:**
- Python 3.8+
- numpy, scipy, matplotlib

**Installation dépendances:**

```bash
pip install numpy scipy matplotlib
```

### Exécution Notebook

**1. Ouvrir le notebook:**

```bash
cd C:\Users\ncuss\Desktop\ENSTA\Projet_SAFRAN\Codebase
jupyter notebook simulation_ins_vor_dme.ipynb
```

**2. Exécuter les cellules dans l'ordre:**
- Cellule 2: Imports
- Cellule 4: Chargement paramètres
- Cellule 6: Choix scénario (modifier `numero_scenario`)
- Cellule 8: Génération mesures IMU
- Cellule 10: Simulation INS seule
- Cellule 12: Simulation INS + EKF
- Cellules 14-18: Calcul métriques
- Cellules 20-26: Visualisations

**3. Changer de scénario:**

Modifier cellule 6:
```python
numero_scenario = 2  # 1, 2 ou 3
```

### Interprétation des Résultats

**Cellule 18 - Statistiques:**

```
RMSE 2D:  75.2%  → EKF réduit erreur de 75%
CEP50:    82.2%  → Médiane erreur réduite de 82%
CEP95:    -3.3%  → 95e percentile légèrement dégradé (normal si peu de mesures)
```

**Valeurs attendues:**
- Amélioration RMSE > 50%: Bon
- Amélioration CEP50 > 40%: Bon
- Si amélioration < 0%: Problème (vérifier gating, visibilité)

**Figures:**
- Figure 1: Trajectoires 2D → Vérifier séparation INS/EKF
- Figure 2: Erreurs temporelles → Convergence EKF visible
- Figure 3: RMSE glissant → Amélioration progressive
- Figure 4: Innovations → Mesures acceptées/rejetées
- Figure 5: Covariance → Réduction incertitude

### Génération Figures

**Sauvegarder figures:**

```python
fig1.savefig(f'trajectoires_scenario_{numero_scenario}.png', dpi=300, bbox_inches='tight')
fig2.savefig(f'erreurs_scenario_{numero_scenario}.png', dpi=300, bbox_inches='tight')
```

---

## 7. Résultats de Référence

Voir fichier séparé: `RESULTATS_REFERENCE.md`

**Résumé:**

| Scénario | Dérive INS (m) | Erreur EKF (m) | Amélioration |
|----------|----------------|----------------|--------------|
| 1        | 2500           | 600            | 76%          |
| 2        | 3200           | 350            | 89%          |
| 3        | 1800           | 500            | 72%          |

---

## 8. Validation et Tests

### Script de Test Automatisé

**Exécution:**

```bash
python test_scenarios.py
```

**Critères validés:**
- Accélérations non nulles
- Dérive INS > 500 m
- Amélioration EKF > 50%

**Résultat attendu:**

```
[SUCCESS] TOUS LES TESTS PASSES
```

Voir `GUIDE_VALIDATION.md` pour détails.

---

## 9. Troubleshooting

### Problèmes Courants

**1. Animation vide**

**Symptôme:** Seules les stations sont affichées.

**Solution:**
```python
# Utiliser affichage HTML5
from IPython.display import HTML
HTML(anim.to_html5_video())
```

**2. EKF ne corrige pas**

**Symptôme:** Amélioration < 10%

**Diagnostic:**
- Vérifier nombre mesures acceptées (cellule 12)
- Si faible: problème visibilité ou gating trop strict

**Solution:**
```python
# Assouplir gating
params_ekf.seuil_gating = 15.0  # Au lieu de 9.21
```

**3. Dérive INS insuffisante**

**Symptôme:** Erreur INS < 500 m

**Cause:** Scénario sans accélérations

**Solution:** Vérifier que scénarios 1 et 3 sont bien modifiés (voir CHANGELOG)

**4. Erreur ModuleNotFoundError**

**Solution:**
```bash
pip install numpy scipy matplotlib
```

**5. Notebook lent**

**Cause:** 120000 échantillons (20 min à 100 Hz)

**Solution:**
```python
# Réduire durée
params_sim.duree_simulation = 600.0  # 10 min au lieu de 20
```

---

## 10. Évolutions Futures

### Court Terme

- Ajouter GNSS comme source de correction supplémentaire
- Implémenter UKF (Unscented Kalman Filter)
- Ajouter scénarios avec pannes capteurs
- Export résultats en CSV/JSON

### Moyen Terme

- Dynamique 3D complète avec quaternions
- Modèle de virage coordonné réaliste
- Simulation multi-path VOR/DME
- Interface graphique interactive (Dash/Streamlit)

### Long Terme

- IMM (Interacting Multiple Model) pour modes de vol
- Factor graph pour fusion multi-capteurs
- Simulation Monte Carlo pour statistiques robustes
- Intégration temps réel avec données réelles

---

## Références

1. Groves, P. D. (2013). *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*. Artech House.

2. Titterton, D. H., & Weston, J. L. (2004). *Strapdown Inertial Navigation Technology*. IET.

3. Bar-Shalom, Y., Li, X. R., & Kirubarajan, T. (2001). *Estimation with Applications to Tracking and Navigation*. Wiley.

4. Farrell, J. A. (2008). *Aided Navigation: GPS with High Rate Sensors*. McGraw-Hill.

---

## Licence

Projet académique ENSTA Bretagne - Usage éducatif uniquement

## Contact

Nicolas CUSSEAU - ENSTA Bretagne  
Projet SAFRAN - Décembre 2025
