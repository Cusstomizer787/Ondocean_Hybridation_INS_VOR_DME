# Analyse Complète de la Codebase - INS + VOR/DME avec EKF Adaptatif

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Modulaire](#architecture-modulaire)
3. [Innovations Techniques](#innovations-techniques)
4. [Analyse Détaillée par Module](#analyse-détaillée-par-module)
5. [Particularités du Code](#particularités-du-code)
6. [Diagrammes UML](#diagrammes-uml)
7. [Métriques de Code](#métriques-de-code)

---

## Vue d'Ensemble

### Objectif du Projet

Système de navigation hybride combinant:
- **INS (Inertial Navigation System):** Centrale inertielle avec gyroscope et accéléromètres
- **VOR/DME:** Radionavigation terrestre (azimut + distance)
- **EKF Adaptatif:** Filtre de Kalman étendu avec adaptation automatique

### Problématique Résolue

**Défi:** Les EKF classiques divergent lors de manœuvres agressives (virages serrés, accélérations fortes) car:
- Modèle dynamique trop simple
- Gating fixe rejette mesures valides
- Bruit de processus constant inadapté

**Solution:** EKF adaptatif avec:
1. **Contrainte douce sur vitesse** - Maintient ||V|| constant en virage uniforme
2. **Matrice Q adaptative** - Augmente incertitude en virage
3. **Gating hybride** - Ajuste seuil selon manœuvre + covariance

---

## Architecture Modulaire

### Structure des Fichiers

```
Codebase/
├── Configuration
│   └── parametres.py          (1 fichier, 5.2 KB)
│
├── Modèles Physiques
│   ├── modeles_dynamique.py   (6.1 KB)
│   └── stations_sol.py        (3.9 KB)
│
├── Algorithmes
│   ├── ekf.py                 (8.6 KB)
│   ├── simulateur_ins.py      (4.4 KB)
│   └── generateur_trajectoire.py (12.1 KB)
│
├── Métriques & Visualisation
│   ├── metriques.py           (4.6 KB)
│   └── visualisation.py       (13.6 KB)
│
├── Tests
│   ├── test_imports.py        (2.7 KB)
│   └── test_scenarios.py      (9.0 KB)
│
├── Notebook
│   └── simulation_ins_vor_dme.ipynb (753 KB)
│
└── Documentation
    ├── README.md
    ├── GUIDE_VALIDATION.md
    ├── INSTRUCTIONS_ANIMATION.md
    ├── DOCUMENTATION_COMPLETE.md
    ├── CHANGELOG.md
    ├── README_TESTS.md
    └── RESULTATS_REFERENCE.md
```

**Total:** 8 modules Python, 2 tests, 1 notebook, 7 docs

---

## Innovations Techniques

### 1. Contrainte Douce Adaptative sur Vitesse

**Fichier:** `modeles_dynamique.py`, lignes 47-70

**Principe:**
```python
# Détection mouvement circulaire uniforme
est_en_virage = np.abs(omega_z_corrige) > 0.002
variation_vitesse = np.abs(V_mag_current - V_mag_previous)

# Application contrainte SI virage uniforme
if est_en_virage and variation_vitesse < 1.0 and V_mag_current > 1.0:
    alpha = 0.8  # Facteur de lissage
    V_mag_target = alpha * V_mag_previous + (1 - alpha) * V_mag_current
    # Correction proportionnelle des composantes
    V_N_next = V_N_next * (V_mag_target / V_mag_current)
    V_E_next = V_E_next * (V_mag_target / V_mag_current)
```

**Pourquoi c'est innovant:**
- **Contrainte douce (80%)** au lieu de dure (100%) → Permet adaptation
- **Conditionnelle** → S'active uniquement en virage uniforme
- **Détection automatique** → Pas de configuration manuelle

**Cas d'usage:**
- ✓ Scénario 2 (arc circulaire): Contrainte active, maintient V constant
- ✗ Scénario 3 (accélération): Contrainte inactive, permet ΔV

---

### 2. Matrice Q Adaptative

**Fichier:** `modeles_dynamique.py`, lignes 151-193

**Principe:**
```python
def matrice_Q(dt, params_ins, omega_z=0.0):
    # Adaptation selon type de mouvement
    if np.abs(omega_z) > 0.002:
        # En virage: modèle moins précis, EKF fait confiance aux mesures
        Q_vitesse = 2.0  # m²/s³ (×4 par rapport au rectiligne)
    else:
        # Rectiligne: modèle précis
        Q_vitesse = 0.5  # m²/s³
    
    Q[3, 3] = Q_vitesse * dt  # V_N
    Q[4, 4] = Q_vitesse * dt  # V_E
```

**Pourquoi c'est innovant:**
- **Q variable** au lieu de constante
- **Basé sur physique** (ω_z) pas sur temps
- **Équilibre prédiction/correction** automatique

**Effet:**
- Virage: Q élevé → EKF fait plus confiance aux mesures VOR/DME
- Rectiligne: Q faible → EKF fait plus confiance au modèle INS

---

### 3. Gating Adaptatif Hybride

**Fichier:** `ekf.py`, lignes 103-143

**Principe:**
```python
def calculer_seuil_gating(self, omega_z, a_long, S):
    # ÉTAPE 1: Détection type de manœuvre
    if np.abs(omega_z) > 0.01 or np.abs(a_long) > 0.5:
        seuil_base = 25.0  # Manœuvre agressive
    elif np.abs(omega_z) > 0.002 or np.abs(a_long) > 0.2:
        seuil_base = 15.0  # Manœuvre modérée
    else:
        seuil_base = 9.21  # Mouvement calme (95%, 2 DDL)
    
    # ÉTAPE 2: Adaptation fine basée sur covariance
    trace_S = np.trace(S)
    dim_S = S.shape[0]
    facteur_S = 1.0 + 0.05 * (trace_S / dim_S)
    
    seuil_final = seuil_base * facteur_S
    
    # ÉTAPE 3: Limites de sécurité
    seuil_final = np.clip(seuil_final, 9.21, 30.0)
    
    return seuil_final
```

**Pourquoi c'est innovant:**
- **Hybride:** Combine détection physique (ω_z, a_long) + statistique (S)
- **Multi-niveaux:** 3 modes (calme/modéré/agressif)
- **Auto-adaptatif:** Ajustement fin selon incertitude

**Comparaison:**

| Approche | Seuil | Adaptation | Robustesse |
|----------|-------|------------|------------|
| **Classique** | Fixe (9.21) | Aucune | Faible (diverge en manœuvre) |
| **Adaptatif simple** | Variable | Basique | Moyenne |
| **Hybride (notre)** | Variable | Double | **Excellente** |

---

### 4. Calcul Accélération Longitudinale

**Fichier:** `ekf.py`, lignes 89-92

**Principe:**
```python
# Calcul a_long pour gating adaptatif
V_mag_current = np.sqrt(self.x[3]**2 + self.x[4]**2)
self.a_long_current = (V_mag_current - self.V_mag_prev) / dt
self.V_mag_prev = V_mag_current
```

**Pourquoi c'est important:**
- **Détection accélération** en plus de virage
- **Cohérent avec état EKF** (pas mesures brutes)
- **Utilisé pour gating** et détection manœuvre

---

## Analyse Détaillée par Module

### Module 1: `parametres.py`

**Rôle:** Configuration centralisée de tous les paramètres

**Classes:**
1. `ParametresSimulation` - Durée, pas de temps, altitude
2. `ParametresINS` - Biais, bruits, constantes de temps Gauss-Markov
3. `ParametresVORDME` - Écarts-types mesures
4. `ParametresEKF` - Covariance initiale, bruits de mesure, seuil gating

**Particularités:**
- **Dataclasses** pour simplicité et clarté
- **Valeurs réalistes** issues de spécifications aéronautiques
- **Modèle Gauss-Markov** pour biais (τ_c = 3600s)

**Exemple de paramètres:**
```python
# Gyroscope
gyro_biais_initial = 0.01 * np.pi / 180  # 0.01°/s
gyro_sigma_bruit = 0.1 * np.pi / 180     # 0.1°/s
gyro_tau_c = 3600.0                      # 1 heure

# VOR/DME
sigma_vor = 2.0 * np.pi / 180            # 2° (azimut)
sigma_dme = 100.0                        # 100 m (distance)
```

---

### Module 2: `modeles_dynamique.py`

**Rôle:** Modèles dynamiques INS et matrices EKF

**Fonctions principales:**

#### 1. `dynamique_ins(x, u_gyro, u_accel, dt, params_ins)`

**Modèle d'état INS 8D:**
```
x = [N, E, h, V_N, V_E, ψ, b_g, b_a]

Équations:
• Position: N_{k+1} = N_k + V_N·dt
• Vitesse: V_N_{k+1} = V_N_k + a_N·dt
• Cap: ψ_{k+1} = ψ_k + ω_z·dt
• Biais: b_{k+1} = b_k·(1 - β·dt) + w  (Gauss-Markov)
```

**Particularités:**
- **Rotation NED → corps:** Accélérations mesurées dans repère avion
- **Correction biais:** ω_z_corrigé = u_gyro - b_g
- **Contrainte douce:** Maintient ||V|| en virage uniforme

#### 2. `jacobienne_F(x, u_gyro, u_accel, dt, params_ins)`

**Matrice de transition F (8×8):**
```
F = I + ∂f/∂x · dt

Dérivées clés:
• ∂V_N/∂ψ = -V·sin(ψ)·ω_z·dt  (couplage vitesse-cap)
• ∂V_E/∂ψ = V·cos(ψ)·ω_z·dt
• ∂ψ/∂b_g = -dt              (biais gyro affecte cap)
```

**Particularités:**
- **Linéarisation locale** autour de x
- **Couplage non-linéaire** vitesse-cap pris en compte
- **Modèle Gauss-Markov** pour biais

#### 3. `matrice_Q(dt, params_ins, omega_z=0.0)`

**Matrice de bruit de processus Q (8×8):**
```
Q = diag([0, 0, 0, Q_V, Q_V, Q_ψ, Q_bg, Q_ba])

Adaptatif:
• Q_V = 2.0 si |ω_z| > 0.002 (virage)
• Q_V = 0.5 sinon (rectiligne)
```

**Particularités:**
- **Position déterministe** (Q_pos = 0)
- **Vitesse adaptative** selon virage
- **Biais stochastique** (Gauss-Markov)

---

### Module 3: `ekf.py`

**Rôle:** Filtre de Kalman étendu adaptatif

**Classe `EKF`:**

**Attributs:**
```python
self.x: ndarray[8]          # État [N, E, h, V_N, V_E, ψ, b_g, b_a]
self.P: ndarray[8,8]        # Covariance
self.V_mag_prev: float      # Magnitude vitesse précédente
self.a_long_current: float  # Accélération longitudinale
self.historique: dict       # Innovations, gating, etc.
```

**Méthodes:**

#### 1. `prediction(u_gyro, u_accel, dt)`

**Algorithme:**
```
1. Propagation état: x = f(x, u, dt)
2. Calcul a_long: (||V|| - ||V_prev||) / dt
3. Calcul F: jacobienne
4. Calcul Q: adaptatif selon ω_z
5. Propagation P: F·P·F^T + Q
```

**Particularités:**
- **Q adaptatif** passé en paramètre
- **a_long stocké** pour gating

#### 2. `calculer_seuil_gating(omega_z, a_long, S)`

**Algorithme:**
```
1. Détection manœuvre → seuil_base
2. Adaptation covariance → facteur_S
3. seuil_final = seuil_base · facteur_S
4. Clip [9.21, 30.0]
```

**Particularités:**
- **3 niveaux** de manœuvre
- **Adaptation fine** via trace(S)
- **Limites sécurité**

#### 3. `update_vor(z_vor, station)` et `update_dme(z_dme, station)`

**Algorithme:**
```
1. Prédiction mesure: z_pred = h(x, station)
2. Innovation: y = z - z_pred
3. Normalisation angulaire (VOR): y ∈ [-π, π]
4. Covariance innovation: S = H·P·H^T + R
5. Gating adaptatif: d² < seuil(ω_z, a_long, S)
6. SI acceptée:
   - Gain: K = P·H^T·S^(-1)
   - Correction: x = x + K·y
   - Covariance: P = (I - K·H)·P
```

**Particularités:**
- **Normalisation angulaire** pour VOR (évite sauts 2π)
- **Gating adaptatif** au lieu de fixe
- **Historique complet** des innovations

---

### Module 4: `stations_sol.py`

**Rôle:** Modélisation stations VOR/DME

**Classe `Station`:**
```python
class Station:
    id: int          # Identifiant
    N: float         # Position Nord (m)
    E: float         # Position Est (m)
    type: str        # 'VOR', 'DME', ou 'VOR/DME'
    
    def distance_to(self, N, E):
        """Calcul distance euclidienne"""
        return np.sqrt((N - self.N)**2 + (E - self.E)**2)
    
    def azimuth_to(self, N, E):
        """Calcul azimut (rad)"""
        return np.arctan2(E - self.E, N - self.N)
```

**Fonctions de mesure:**

#### 1. `modele_mesure_vor(x, station)`
```python
# Azimut de la station vers l'avion
azimut = np.arctan2(x[1] - station.E, x[0] - station.N)
return azimut
```

#### 2. `modele_mesure_dme(x, station)`
```python
# Distance station-avion
distance = np.sqrt((x[0] - station.N)**2 + (x[1] - station.E)**2)
return distance
```

**Jacobiennes:**
```python
# H_vor = [∂azimut/∂N, ∂azimut/∂E, 0, 0, 0, 0, 0, 0]
# H_dme = [∂distance/∂N, ∂distance/∂E, 0, 0, 0, 0, 0, 0]
```

**Particularités:**
- **Mesures non-linéaires** (arctan2, sqrt)
- **Jacobiennes analytiques** (pas de différences finies)
- **Configuration réaliste** (3 stations en triangle)

---

### Module 5: `generateur_trajectoire.py`

**Rôle:** Génération trajectoires vérité pour 3 scénarios

**Scénarios:**

#### Scénario 1: Approche Radiale
```
Trajectoire:
• Départ: (-20 km, -20 km)
• Approche station 1 (0, 0)
• Virage 180° (R=5000m)
• Retour vers départ
• Durée: 20 min
• Vitesse: 80 m/s
```

**Particularités:**
- Virage coordonné large (R=5000m)
- Accélération/décélération réalistes (0.5 m/s²)
- Test robustesse virage

#### Scénario 2: Arc Circulaire
```
Trajectoire:
• Arc de cercle complet
• Centre: (0, 0)
• Rayon: 50 km
• Vitesse tangentielle: 100 m/s constante
• ω_z = V/R = 0.002 rad/s constant
```

**Particularités:**
- **Mouvement circulaire uniforme** pur
- Test contrainte vitesse
- Accélération centripète constante

#### Scénario 3: Transit Multi-Stations
```
Trajectoire:
• Waypoints: (-20,-20) → (0,0) → (80,0) → (40,60) → (40,80)
• Vitesse croisière: 120 m/s
• Vitesse virage: 80 m/s
• Virages coordonnés (R=2000m)
• Accélération: ±0.8 m/s²
```

**Particularités:**
- **Manœuvres agressives** (R=2000m)
- **Grandes variations vitesse** (80-120 m/s)
- Test gating adaptatif

---

### Module 6: `simulateur_ins.py`

**Rôle:** Simulation centrale inertielle avec erreurs

**Fonction `simuler_ins(verite, params_ins)`:**

**Algorithme:**
```
1. Initialisation biais (Gauss-Markov)
2. Pour chaque instant:
   a. Calcul mesures vraies (ω_z, a_N, a_E)
   b. Ajout biais + bruit blanc
   c. Propagation INS avec mesures bruitées
   d. Évolution biais (Gauss-Markov)
```

**Modèle de bruit:**
```python
# Biais Gauss-Markov
b_{k+1} = b_k · exp(-β·dt) + w_k
où β = 1/τ_c, w_k ~ N(0, σ²·(1-exp(-2β·dt)))

# Bruit blanc
u_gyro_bruité = u_gyro_vrai + b_g + n_g
u_accel_bruité = u_accel_vrai + b_a + n_a
```

**Particularités:**
- **Modèle réaliste** de biais (corrélés dans le temps)
- **Bruits blancs** sur mesures
- **Dérive inertielle** observable

---

### Module 7: `metriques.py`

**Rôle:** Calcul métriques de performance

**Fonctions:**

#### 1. `calculer_erreur_2D(verite, traj, idx)`
```python
# Erreur euclidienne 2D
err_N = traj['N'][idx] - verite['N'][idx]
err_E = traj['E'][idx] - verite['E'][idx]
return np.sqrt(err_N**2 + err_E**2)
```

#### 2. `calculer_amelioration(err_ins, err_ekf)`
```python
# Pourcentage d'amélioration
return 100 * (1 - err_ekf / err_ins)
```

#### 3. `calculer_metriques_complete(verite, traj_ins, traj_ekf)`
```python
# Métriques complètes:
• Erreur finale 2D/3D
• Erreur RMS
• Erreur max
• Amélioration EKF vs INS
• Taux acceptation mesures
```

**Particularités:**
- **Métriques standard** navigation
- **Comparaison INS vs EKF**
- **Validation quantitative**

---

### Module 8: `visualisation.py`

**Rôle:** Visualisation trajectoires et métriques

**Fonctions principales:**

#### 1. `plot_trajectoires_2D(...)`
```python
# Affichage statique trajectoires
• Vérité (noir, x)
• INS seule (rouge pointillé)
• INS+EKF (bleu, o)
• Stations (triangles verts)
```

#### 2. `plot_erreurs(...)`
```python
# Graphiques erreurs temporelles
• Erreur 2D vs temps
• Erreur Nord vs temps
• Erreur Est vs temps
```

#### 3. `plot_innovations(ekf)`
```python
# Innovations VOR/DME
• Innovations acceptées/rejetées
• Test gating
• Statistiques
```

#### 4. `animer_trajectoires(...)`
```python
# Animation matplotlib
• Trajectoires progressives
• Marqueurs mobiles
• Texte temps
```

**Particularités:**
- **Markers sous-échantillonnés** (markevery=10000)
- **Aspect ratio égal** (ax.axis('equal'))
- **Légendes claires**

---

## Particularités du Code

### 1. Normalisation Angulaire

**Problème:** Angles VOR peuvent sauter de -π à +π

**Solution:**
```python
# Dans ekf.py, update_vor()
innov = z_vor - z_pred
innov = np.mod(innov + np.pi, 2.0 * np.pi) - np.pi
```

**Explication:**
```
1. innov + π : décale dans [0, 2π]
2. mod 2π : ramène dans [0, 2π]
3. - π : redécale dans [-π, π]
```

**Importance:** Évite innovations artificiellement grandes

---

### 2. Gestion Scalaire vs Matricielle

**Problème:** VOR/DME sont scalaires, mais EKF matriciel

**Solution:**
```python
# Covariance innovation scalaire
S_scalar = S[0, 0]

# Gain Kalman vectoriel
K = self.P @ H.T / S_scalar
K = K.reshape(-1, 1)

# Correction état
self.x = self.x + (K * innov).flatten()
```

**Particularités:**
- **S extrait** en scalaire pour test gating
- **K reshape** pour multiplication matricielle
- **Résultat flatten** pour cohérence dimension

---

### 3. Modèle Gauss-Markov pour Biais

**Équation continue:**
```
db/dt = -β·b + w(t)
où β = 1/τ_c, w(t) ~ N(0, σ²)
```

**Discrétisation:**
```python
# Dans simulateur_ins.py
phi = np.exp(-beta * dt)
b_next = b * phi + w
où w ~ N(0, sigma² * (1 - phi²))
```

**Avantages:**
- **Réaliste:** Biais corrélés dans le temps
- **Stable:** Pas de divergence
- **Paramétrable:** τ_c = temps de corrélation

---

### 4. Contrainte Douce vs Dure

**Contrainte dure (problématique):**
```python
# Force ||V|| = ||V_prev|| exactement
V_mag_target = V_mag_previous
```

**Contrainte douce (implémentée):**
```python
# Lisse vers ||V_prev|| avec facteur α
alpha = 0.8
V_mag_target = alpha * V_mag_previous + (1 - alpha) * V_mag_current
```

**Avantages:**
- **Flexible:** Permet petites variations
- **Robuste:** Pas de sur-contrainte
- **Adaptatif:** α ajustable

---

### 5. Gating Chi-Carré

**Formule:**
```
d² = y^T · S^(-1) · y

Test: d² < seuil_chi2(α, n)
```

**Interprétation:**
- d² = distance de Mahalanobis au carré
- Mesure "combien de σ" l'innovation est éloignée
- Seuil = quantile distribution χ²(n)

**Valeurs:**
```
α = 95%, n = 2 (VOR ou DME):
• Calme: 9.21 (table χ²)
• Modéré: 15.0 (relaxé)
• Agressif: 25.0 (très relaxé)
```

---

### 6. Rotation Repère Corps → NED

**Problème:** Accéléromètres mesurent dans repère avion

**Solution:**
```python
# Matrice de rotation 2D (cap ψ)
a_N = a_N_corps * np.cos(psi) - a_E_corps * np.sin(psi)
a_E = a_N_corps * np.sin(psi) + a_E_corps * np.cos(psi)
```

**Particularités:**
- **2D seulement** (pas de roulis/tangage)
- **Hypothèse:** Vol coordonné
- **Simplifié mais réaliste** pour navigation

---

## Diagrammes UML

### Diagramme 1: Architecture Modulaire

**Fichier:** `docs/architecture.puml`

**Contenu:**
- Classes de configuration
- Modèles physiques
- Algorithmes
- Visualisation
- Relations entre modules

**Utilisation:**
```bash
# Générer PNG avec PlantUML
java -jar plantuml.jar docs/architecture.puml
```

---

### Diagramme 2: Flux EKF

**Fichier:** `docs/flux_ekf.puml`

**Contenu:**
- Boucle prédiction-correction
- Adaptations (Q, gating, contrainte)
- Tests conditionnels
- Sauvegarde historique

**Points clés:**
- 3 blocs adaptatifs (Q, gating, contrainte)
- Normalisation angulaire VOR
- Gestion rejets mesures

---

### Diagramme 3: Modes de Vol

**Fichier:** `docs/modes_vol.puml`

**Contenu:**
- 3 états (Croisière, Virage Modéré, Manœuvre Agressive)
- Transitions automatiques
- Paramètres EKF par mode
- Scénarios typiques

**Transitions:**
```
Croisière ↔ Virage Modéré : |ω_z| = 0.002
Virage Modéré ↔ Agressif : |ω_z| = 0.01
```

---

## Métriques de Code

### Statistiques Globales

```
Lignes de code Python: ~2500
Lignes de documentation: ~1500
Lignes de tests: ~400
Total: ~4400 lignes

Fichiers Python: 8
Fichiers tests: 2
Fichiers docs: 7
Diagrammes UML: 3
```

### Complexité par Module

| Module | Lignes | Fonctions | Classes | Complexité |
|--------|--------|-----------|---------|------------|
| `ekf.py` | 280 | 5 | 1 | Élevée |
| `generateur_trajectoire.py` | 400 | 3 | 0 | Moyenne |
| `visualisation.py` | 450 | 5 | 0 | Moyenne |
| `modeles_dynamique.py` | 200 | 6 | 0 | Moyenne |
| `simulateur_ins.py` | 150 | 1 | 0 | Faible |
| `metriques.py` | 150 | 4 | 0 | Faible |
| `stations_sol.py` | 130 | 6 | 1 | Faible |
| `parametres.py` | 170 | 0 | 4 | Faible |

### Couverture Tests

```
test_imports.py:
• Import tous modules: ✓
• Vérification classes: ✓
• Vérification fonctions: ✓

test_scenarios.py:
• Scénario 1: ✓
• Scénario 2: ✓
• Scénario 3: ✓
• Métriques: ✓
• Seuils validation: ✓

Couverture estimée: 85%
```

---

## Conclusion

### Points Forts

1. **Architecture modulaire** - Séparation claire des responsabilités
2. **Code documenté** - Docstrings complètes, commentaires explicatifs
3. **Innovations techniques** - 3 adaptations majeures (Q, gating, contrainte)
4. **Tests complets** - 3 scénarios + tests unitaires
5. **Documentation riche** - 7 fichiers + 3 diagrammes UML

### Points d'Amélioration Futurs

1. **Type hints** - Ajouter annotations Python 3.9+
2. **Logging** - Remplacer prints par logging
3. **Configuration externe** - YAML/JSON au lieu de Python
4. **Tests unitaires** - pytest pour chaque fonction
5. **CI/CD** - GitHub Actions pour tests automatiques

### Originalité du Code

**Ce qui rend ce code unique:**

1. **EKF adaptatif complet** - Pas juste Q ou gating, mais les deux + contrainte
2. **Détection automatique** - Pas de configuration manuelle par scénario
3. **Approche hybride** - Combine physique (ω_z) + statistique (S)
4. **Validation rigoureuse** - 3 scénarios couvrant tous les cas
5. **Documentation exhaustive** - Code + diagrammes + guides

**Applicable à:**
- Navigation aérienne
- Robotique mobile
- Véhicules autonomes
- Systèmes de guidage

---

**Auteur:** Nicolas CUSSEAU - Guillaume COSNARD - ENSTA  
**Projet:** Hybridation INS + VOR/DME  
**Date:** Décembre 2025
