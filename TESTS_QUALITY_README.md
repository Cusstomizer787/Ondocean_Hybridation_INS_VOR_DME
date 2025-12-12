# Tests Unitaires et Qualité Code

**Projet:** INS + VOR/DME avec EKF Adaptatif  
**Auteur:** Nicolas CUSSEAU - ENSTA ILEMS

---

## Installation Dépendances

### Tests Unitaires

```bash
pip install pytest pytest-cov pytest-mock
```

### Qualité Code

```bash
pip install black isort mypy
```

---

## Structure Tests

```
Codebase/
├── tests/                      # Tests unitaires (à créer)
│   ├── __init__.py
│   ├── test_parametres.py
│   ├── test_modeles_dynamique.py
│   ├── test_stations_sol.py
│   ├── test_ekf.py
│   ├── test_simulateur_ins.py
│   ├── test_generateur_trajectoire.py
│   ├── test_metriques.py
│   └── test_visualisation.py
├── pytest.ini                  # Configuration pytest
└── .coveragerc                 # Configuration couverture
```

---

## Exécution Tests

### Tests Complets avec Couverture

```bash
pytest --cov --cov-report=html
```

### Tests Spécifiques

```bash
# Module spécifique
pytest tests/test_ekf.py

# Fonction spécifique
pytest tests/test_ekf.py::test_prediction

# Verbose
pytest -v

# Arrêt au premier échec
pytest -x
```

### Rapport Couverture

```bash
# Terminal
pytest --cov --cov-report=term-missing

# HTML (ouvre htmlcov/index.html)
pytest --cov --cov-report=html
```

---

## Formatage Code

### Black (Formatter)

```bash
# Formatter tous les fichiers Python
black --line-length 100 *.py

# Vérifier sans modifier
black --check *.py

# Fichier spécifique
black ekf.py
```

### isort (Trier Imports)

```bash
# Trier imports
isort *.py

# Vérifier sans modifier
isort --check *.py
```

### Combiné

```bash
# Formatter et trier en une commande
black --line-length 100 *.py && isort *.py
```

---

## Vérification Types

### mypy (Type Checker)

```bash
# Vérifier tous fichiers
mypy *.py

# Fichier spécifique
mypy ekf.py

# Strict mode
mypy --strict *.py
```

---

## Profiling Performance

### cProfile

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code à profiler
from test_scenarios import test_scenario_3
test_scenario_3()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('time')
stats.print_stats(20)
```

### line_profiler

```bash
pip install line_profiler

# Ajouter @profile avant fonction
kernprof -l -v script.py
```

---

## Objectifs Qualité

### Couverture Tests

- **Objectif:** > 90%
- **Critique:** > 80% pour modules principaux (ekf.py, modeles_dynamique.py)

### Complexité Code

- **Cyclomatic complexity:** < 10 par fonction
- **Lignes par fonction:** < 50

### Documentation

- **Docstrings:** Toutes fonctions publiques
- **Type hints:** Tous paramètres et retours
- **Commentaires:** Code complexe uniquement

---

## Tests par Module

### test_parametres.py

**Tests:**
- Valeurs par défaut correctes
- Types dataclasses valides
- Cohérence paramètres

**Couverture attendue:** 100%

### test_modeles_dynamique.py

**Tests:**
- `dynamique_ins()` - Propagation état 8D
- `jacobienne_F()` - Dimensions [8,8]
- `matrice_Q()` - Adaptation omega_z
- Contrainte douce vitesse

**Couverture attendue:** > 95%

### test_stations_sol.py

**Tests:**
- `distance_to()` - Calcul euclidien
- `azimuth_to()` - Calcul arctan2
- `modele_mesure_vor()` - Normalisation [-π, π]
- `modele_mesure_dme()` - Distance positive
- Jacobiennes H

**Couverture attendue:** 100%

### test_ekf.py

**Tests:**
- Initialisation état et covariance
- `prediction()` - Propagation P positive définie
- `calculer_seuil_gating()` - 3 modes (9.21, 15, 25)
- `update_vor()` - Correction état
- `update_dme()` - Correction état
- Gating acceptation/rejet

**Couverture attendue:** > 90%

### test_simulateur_ins.py

**Tests:**
- Génération biais Gauss-Markov
- Propagation INS avec bruits
- Dérive temporelle observable

**Couverture attendue:** > 85%

### test_generateur_trajectoire.py

**Tests:**
- Scénario 1 - Dimensions correctes
- Scénario 2 - Vitesse constante
- Scénario 3 - Waypoints respectés

**Couverture attendue:** > 80%

### test_metriques.py

**Tests:**
- `calculer_erreur_2D()` - Norme euclidienne
- `calculer_erreur_3D()` - Avec altitude
- `calculer_amelioration()` - Pourcentage

**Couverture attendue:** 100%

### test_visualisation.py

**Tests:**
- Création figures sans erreur
- Dimensions graphiques correctes
- Pas de test affichage (trop lent)

**Couverture attendue:** > 70%

---

## CI/CD GitHub Actions

### Workflow Tests (.github/workflows/tests.yml)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Badges README

### Couverture Tests

```markdown
[![Coverage](https://codecov.io/gh/Cusstomizer787/Ondocean_Hybridation_INS_VOR_DME/branch/main/graph/badge.svg)](https://codecov.io/gh/Cusstomizer787/Ondocean_Hybridation_INS_VOR_DME)
```

### Build Status

```markdown
[![Tests](https://github.com/Cusstomizer787/Ondocean_Hybridation_INS_VOR_DME/workflows/Tests/badge.svg)](https://github.com/Cusstomizer787/Ondocean_Hybridation_INS_VOR_DME/actions)
```

### License

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## Bonnes Pratiques

### Tests

1. **Nommage:** `test_<fonction>_<cas>`
2. **Arrange-Act-Assert:** Structure claire
3. **Isolation:** Pas de dépendances entre tests
4. **Fixtures:** Réutiliser données test
5. **Mocks:** Isoler composants externes

### Code

1. **Type hints:** Tous paramètres et retours
2. **Docstrings:** Google style
3. **Logging:** Pas de prints
4. **Constants:** Pas de magic numbers
5. **DRY:** Don't Repeat Yourself

### Documentation

1. **README:** Instructions claires
2. **Exemples:** Code exécutable
3. **Changelog:** Historique versions
4. **API docs:** Fonctions publiques

---

## Commandes Rapides

### Développement

```bash
# Formatter + trier + tester
black --line-length 100 *.py && isort *.py && pytest --cov

# Vérifier qualité
mypy *.py && pytest --cov --cov-report=term-missing
```

### Pre-commit

```bash
# Installer pre-commit
pip install pre-commit

# Créer .pre-commit-config.yaml
pre-commit install

# Exécuter manuellement
pre-commit run --all-files
```

---

## Ressources

### Documentation

- **pytest:** https://docs.pytest.org/
- **black:** https://black.readthedocs.io/
- **mypy:** https://mypy.readthedocs.io/
- **coverage:** https://coverage.readthedocs.io/

### Tutoriels

- **Real Python - pytest:** https://realpython.com/pytest-python-testing/
- **Type hints:** https://docs.python.org/3/library/typing.html

---

## Prochaines Étapes

### Court Terme

1. Créer dossier `tests/`
2. Écrire tests unitaires (8 fichiers)
3. Atteindre > 90% couverture
4. Ajouter type hints
5. Formatter code (black)

### Moyen Terme

6. CI/CD GitHub Actions
7. Badges README
8. Pre-commit hooks
9. Documentation API (Sphinx)

### Long Terme

10. Tests intégration
11. Tests performance
12. Benchmarking

---

**Guide complet pour tests unitaires et qualité code.**

**Prêt pour implémentation.**
