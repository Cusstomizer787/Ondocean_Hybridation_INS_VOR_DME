# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.1.0] - 2025-12-06

### Ajouté

- Scénarios avec accélérations réalistes pour générer dérive INS observable
- Erreurs d'initialisation aléatoires (position, vitesse, cap, biais)
- Script de tests automatisés (`test_scenarios.py`)
- Guide de validation complet (`GUIDE_VALIDATION.md`)
- Lanceur Windows (`run_tests.bat`)
- Documentation complète du projet (`DOCUMENTATION_COMPLETE.md`)
- Résultats de référence (`RESULTATS_REFERENCE.md`)
- Changelog (ce fichier)

### Modifié

- **Scénario 1:** Profil de vitesse réaliste avec 7 phases (accélération, croisière, virage 180°)
  - Accélérations longitudinales: 0.5 à 1.25 m/s²
  - Virage coordonné: R=1000m, a_c=2.5 m/s²
  - Génère dérive INS de 1500-3000 m

- **Scénario 3:** Transit avec virages coordonnés entre waypoints
  - Virages: R=2000m, a_c=3.2 m/s²
  - Phases accélération/décélération: ±0.8 m/s²
  - Génère dérive INS de 1200-2500 m

- **Notebook cellule 10:** Ajout erreurs d'initialisation avec seed reproductible
  - Erreurs position: ±50m std
  - Erreurs vitesse: ±2 m/s std
  - Erreur cap: ±2° std
  - Erreurs biais: 50% estimation initiale

- **Notebook cellule 26:** Ajout méthodes alternatives d'affichage animation
  - Méthode HTML5 pour Jupyter
  - Option sauvegarde vidéo

### Corrigé

- **Animation vide:** Correction fonction `animate()` dans `visualisation.py`
  - Problème: `idx=0` générait slice vide `[:0]`
  - Solution: `idx_plot = max(1, idx)` pour assurer au moins 1 point

- **Dérive INS insuffisante:** Scénarios 1 et 3 généraient MRU sans accélérations
  - Résultat: Pas de dérive observable
  - Solution: Ajout profils réalistes avec accélérations

### Sécurité

- Aucun problème de sécurité identifié (projet académique local)

---

## [1.0.0] - 2025-12-05

### Ajouté - Version Initiale

**Modules Python:**
- `parametres.py`: Configuration complète (INS, VOR/DME, EKF, stations)
- `modeles_dynamique.py`: Équations d'état INS avec biais Gauss-Markov
- `stations_sol.py`: Modèles de mesure VOR/DME avec jacobiennes
- `generateur_trajectoire.py`: 3 scénarios de trajectoire
- `simulateur_ins.py`: Génération mesures IMU bruitées + intégration
- `ekf.py`: Filtre de Kalman étendu avec gating chi2
- `metriques.py`: RMSE, CEP, statistiques
- `visualisation.py`: 5 fonctions plot + animation

**Notebook:**
- `simulation_ins_vor_dme.ipynb`: Notebook principal avec 11 cellules
  - Imports et configuration
  - Choix scénario
  - Simulation INS seule
  - Simulation INS + EKF
  - Calcul métriques
  - Visualisations
  - Animation

**Scénarios:**
- Scénario 1: Approche radiale (MRU initial)
- Scénario 2: Arc circulaire (accélération centripète)
- Scénario 3: Transit multi-stations (MRU initial)

**Fonctionnalités:**
- État 8D: [N, E, h, V_N, V_E, ψ, b_g, b_a]
- Dynamique INS avec biais évolutifs (Gauss-Markov)
- Mesures VOR (azimut) et DME (distance oblique)
- EKF avec gating (seuil 95%)
- Métriques: RMSE glissant (60s), CEP50/95
- 5 visualisations + animation

**Documentation:**
- `README.md`: Documentation principale
- `test_imports.py`: Script de validation imports

**Paramètres:**
- INS MEMS aéronautique (gyro ARW 0.15°/√h, accel 150µg/√Hz)
- VOR: σ=1.5°, DME: σ=300m
- 3 stations VOR/DME: (0,0), (80km,0), (40km,60km)
- Portée: 200 NM, angle site min: 3°

---

## [Non publié] - Évolutions Futures

### À Venir (v1.2.0)

- [ ] Export résultats en CSV/JSON
- [ ] Sauvegarde automatique figures
- [ ] Script comparaison multi-runs
- [ ] Notebook interactif avec widgets

### Planifié (v2.0.0)

- [ ] GNSS comme source de correction supplémentaire
- [ ] UKF (Unscented Kalman Filter)
- [ ] Scénarios avec pannes capteurs
- [ ] Interface graphique (Dash/Streamlit)

### Vision Long Terme (v3.0.0)

- [ ] Dynamique 3D complète avec quaternions
- [ ] IMM (Interacting Multiple Model)
- [ ] Factor graph pour fusion multi-capteurs
- [ ] Simulation Monte Carlo
- [ ] Intégration temps réel

---

## Notes de Version

### Compatibilité

- **Python:** 3.8+
- **Dépendances:** numpy, scipy, matplotlib
- **OS:** Windows, Linux, macOS

### Migration v1.0 → v1.1

**Changements cassants:** Aucun

**Changements recommandés:**
1. Réexécuter scénarios 1 et 3 (trajectoires modifiées)
2. Utiliser erreurs d'initialisation (cellule 10 notebook)
3. Tester avec `test_scenarios.py`

**Rétrocompatibilité:** Complète

---

## Contributeurs

- Nicolas CUSSEAU - ENSTA Bretagne - Développement initial et v1.1

---

## Licence

Projet académique ENSTA Bretagne - Usage éducatif uniquement

---

## Liens

- [Documentation Complète](DOCUMENTATION_COMPLETE.md)
- [Résultats de Référence](RESULTATS_REFERENCE.md)
- [Guide de Validation](GUIDE_VALIDATION.md)
- [README Principal](README.md)
