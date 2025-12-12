# Tests de Validation - Scénarios Corrigés

## Exécution Rapide

### Windows

Double-cliquer sur `run_tests.bat` ou exécuter:

```bash
run_tests.bat
```

### Linux/Mac

```bash
python test_scenarios.py
```

## Fichiers de Test

- `test_scenarios.py` - Script de validation automatisé (étapes 15-20)
- `run_tests.bat` - Lanceur Windows avec vérification dépendances
- `GUIDE_VALIDATION.md` - Guide détaillé de validation

## Que Testent Ces Scripts?

### Étape 15: Scénario 1 - Approche radiale
- Accélérations longitudinales présentes (0.5-1.25 m/s²)
- Virage coordonné avec accélération centripète (2.5 m/s²)
- Dérive INS observable (>500m)
- Amélioration EKF significative (>50%)

### Étape 16: Scénario 2 - Arc circulaire
- Accélération centripète constante (4.5 m/s²)
- Dérive INS importante (>1000m)
- Amélioration EKF excellente (>80%)

### Étape 17: Scénario 3 - Transit multi-stations
- Virages coordonnés entre waypoints
- Phases accélération/décélération
- Dérive INS observable (>800m)
- Amélioration EKF significative (>50%)

### Étape 18: Vérification accélérations
- Toutes les composantes (a_N, a_E, omega_z) vérifiées
- Au moins une non nulle pour chaque scénario

### Étape 19: Comparaison INS vs EKF
- Erreur finale INS >> Erreur finale EKF
- Ratio vérifié pour chaque scénario

### Étape 20: Statistiques globales
- RMSE 2D amélioration >50%
- CEP amélioration >40%
- Validation complète

## Résultats Attendus

```
============================================================
RAPPORT FINAL - VALIDATION SCENARIOS
============================================================

Scenario 1: Approche radiale avec accelerations
  Accelerations: [OK]
  Derive INS: [OK] (2500m)
  Amelioration EKF: [OK] (75.2%)
  Updates EKF: 2800

Scenario 2: Arc circulaire
  Accelerations: [OK]
  Derive INS: [OK] (3200m)
  Amelioration EKF: [OK] (88.5%)
  Updates EKF: 3100

Scenario 3: Transit multi-stations avec virages
  Accelerations: [OK]
  Derive INS: [OK] (1800m)
  Amelioration EKF: [OK] (72.8%)
  Updates EKF: 2600

============================================================
[SUCCESS] TOUS LES TESTS PASSES
============================================================
```

## Fichiers de Sortie

- `resultats_tests_scenarios.json` - Résultats détaillés au format JSON

## En Cas de Problème

Consulter `GUIDE_VALIDATION.md` section "Dépannage"

### Problèmes Courants

**Dépendances manquantes:**
```bash
pip install numpy scipy matplotlib
```

**Mauvais répertoire:**
```bash
cd C:\Users\ncuss\Desktop\ENSTA\Projet_SAFRAN\Codebase
```

**Tests échouent:**
- Vérifier que les modifications ont bien été appliquées
- Consulter les messages d'erreur détaillés
- Vérifier `generateur_trajectoire.py` et notebook cellule 10

## Prochaines Étapes

Une fois les tests passés:

1. Exécuter le notebook complet pour chaque scénario
2. Générer et analyser les visualisations
3. Documenter les résultats
4. Comparer avec les résultats avant correction
