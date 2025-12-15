# Guide de Validation - Étapes 15-20

Ce guide détaille les étapes de validation des scénarios corrigés.

## Étapes 15-20: Validation par Exécution

### Étape 15: Tester scénario 1

**Objectif:** Vérifier que le scénario 1 génère une séparation visible entre INS seule et INS+EKF.

**Commande:**
```bash
cd C:\Users\ncuss\Desktop\ENSTA\Ondocean_Hybridation_INS_VOR_DME_V1
python test_scenarios.py
```

**Critères de succès:**
- ✓ Accélérations `a_N_corps` max > 0.1 m/s²
- ✓ Accélérations `a_E_corps` max > 2.0 m/s² (virage)
- ✓ Vitesse angulaire `omega_z` max > 0.04 rad/s
- ✓ Dérive INS finale > 500 m
- ✓ Amélioration EKF > 50%

**Valeurs attendues:**
- Accélération longitudinale: 0.5 à 1.25 m/s²
- Accélération centripète (virage): ~2.5 m/s²
- Dérive INS: 1000-3000 m
- Erreur EKF: 100-300 m
- Amélioration: 70-90%

---

### Étape 16: Tester scénario 2

**Objectif:** Vérifier que le scénario 2 fonctionne toujours correctement (inchangé).

**Critères de succès:**
- ✓ Accélération centripète constante: 4.5 m/s² (V²/R = 150²/5000)
- ✓ Vitesse angulaire constante: 0.003 rad/s
- ✓ Dérive INS finale > 1000 m
- ✓ Amélioration EKF > 80%

**Valeurs attendues:**
- Dérive INS: 1500-4000 m
- Erreur EKF: 100-400 m
- Amélioration: 80-95%

---

### Étape 17: Tester scénario 3

**Objectif:** Vérifier que le scénario 3 génère des virages et une dérive.

**Critères de succès:**
- ✓ Accélérations longitudinales: ±0.8 m/s²
- ✓ Accélérations centripètes (virages): ~3.2 m/s² (V²/R = 80²/2000)
- ✓ Vitesse angulaire (virages): ~0.04 rad/s
- ✓ Dérive INS finale > 800 m
- ✓ Amélioration EKF > 50%

**Valeurs attendues:**
- Dérive INS: 1000-3000 m
- Erreur EKF: 150-400 m
- Amélioration: 70-85%

---

### Étape 18: Vérifier accélérations non nulles

**Objectif:** S'assurer que tous les scénarios génèrent des accélérations.

**Méthode:**
Le script `test_scenarios.py` affiche automatiquement les valeurs max de:
- `a_N_corps` (accélération longitudinale)
- `a_E_corps` (accélération latérale)
- `omega_z` (vitesse angulaire)

**Critères:**
- Au moins une des trois valeurs doit être > 0.1 pour chaque scénario
- Scénario 1: a_N et a_E non nuls
- Scénario 2: a_E et omega_z non nuls
- Scénario 3: a_N, a_E et omega_z non nuls

---

### Étape 19: Vérifier erreur finale INS >> EKF

**Objectif:** Confirmer que l'EKF améliore significativement les performances.

**Méthode:**
Le script calcule automatiquement:
```
amélioration = (1 - err_EKF / err_INS) × 100%
```

**Critères de succès:**
- Amélioration > 50% pour tous les scénarios
- Erreur finale INS > 500 m
- Erreur finale EKF < 500 m

**Diagnostic si échec:**
- Si amélioration < 0%: EKF diverge → vérifier matrices P0, Q, R
- Si amélioration < 20%: Peu de corrections → vérifier visibilité stations
- Si amélioration 20-50%: Acceptable mais sous-optimal → ajuster paramètres

---

### Étape 20: Vérifier statistiques amélioration > 50%

**Objectif:** Validation finale avec statistiques complètes.

**Méthode:**
Exécuter le notebook complet pour chaque scénario et vérifier:

```python
amelioration_rmse = (1 - stats_ekf['RMSE_2D'] / stats_ins['RMSE_2D']) * 100
amelioration_cep50 = (1 - stats_ekf['CEP50'] / stats_ins['CEP50']) * 100
amelioration_cep95 = (1 - stats_ekf['CEP95'] / stats_ins['CEP95']) * 100
```

**Critères de succès:**
- RMSE 2D: amélioration > 50%
- CEP50: amélioration > 40%
- CEP95: amélioration > 50%

**Note:** CEP50 peut être plus faible car il mesure la médiane (moins sensible aux grandes erreurs).

---

## Exécution Rapide

### Test automatisé (recommandé)

```bash
cd C:\Users\ncuss\Desktop\ENSTA\Ondocean_Hybridation_INS_VOR_DME_V1
python test_scenarios.py
```

Durée: ~2-5 minutes pour les 3 scénarios.

### Test complet via notebook

1. Ouvrir `simulation_ins_vor_dme.ipynb`
2. Modifier cellule 6: `numero_scenario = 1` (puis 2, puis 3)
3. Exécuter toutes les cellules
4. Vérifier statistiques cellule 18

Durée: ~5-10 minutes par scénario.

---

## Interprétation des Résultats

### Résultat attendu: [SUCCESS]

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

### Résultat problématique: [FAILED]

Si un test échoue, consulter les messages d'erreur:

**[ERREUR] Accelerations quasi-nulles**
→ Le scénario n'a pas été correctement modifié
→ Vérifier que `generateur_trajectoire.py` contient les nouvelles fonctions

**[ERREUR] Derive INS insuffisante (<500m)**
→ Les accélérations sont trop faibles ou les erreurs initiales trop petites
→ Vérifier que les erreurs d'initialisation sont bien ajoutées (cellule 10 notebook)

**[ERREUR] EKF degrade les performances**
→ Problème dans l'EKF (matrices mal paramétrées ou bug)
→ Vérifier matrices P0, Q, R dans `parametres.py`

**[AVERTISSEMENT] Amelioration faible**
→ EKF fonctionne mais sous-optimal
→ Vérifier nombre de mesures acceptées (n_updates)
→ Si n_updates faible: problème visibilité ou gating trop strict

---

## Fichiers de Sortie

Le script `test_scenarios.py` génère:

**`resultats_tests_scenarios.json`**
```json
{
  "1": {
    "nom": "Approche radiale avec accelerations",
    "test_accel": true,
    "test_derive": true,
    "test_amelioration": true,
    "a_N_max": 1.25,
    "a_E_max": 2.5,
    "omega_max": 0.05,
    "err_ins": 2543.2,
    "err_ekf": 631.5,
    "amelioration": 75.2,
    "n_updates": 2847
  },
  ...
}
```

Ce fichier peut être utilisé pour:
- Traçabilité des tests
- Comparaison avant/après modifications
- Génération de rapports automatiques

---

## Dépannage

### Erreur: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'parametres'
```

**Solution:**
```bash
cd C:\Users\ncuss\Desktop\ENSTA\Ondocean_Hybridation_INS_VOR_DME_V1
python test_scenarios.py
```

Assurez-vous d'être dans le bon répertoire.

### Erreur: Numpy/Matplotlib manquant

```
ModuleNotFoundError: No module named 'numpy'
```

**Solution:**
```bash
pip install numpy scipy matplotlib
```

### Script trop lent

Le script teste les 3 scénarios complets. Pour tester un seul scénario:

Modifier `test_scenarios.py` ligne 35:
```python
for num_scenario in [1]:  # Au lieu de [1, 2, 3]
```

---

## Validation Manuelle Alternative

Si vous préférez valider manuellement sans script:

### Pour chaque scénario:

1. **Vérifier accélérations:**
   ```python
   print(f"a_N max: {np.max(np.abs(verite['a_N_corps']))}")
   print(f"a_E max: {np.max(np.abs(verite['a_E_corps']))}")
   print(f"omega max: {np.max(np.abs(verite['omega_z']))}")
   ```

2. **Vérifier dérive INS:**
   ```python
   err_ins = np.sqrt((traj_ins_seule['N'][-1] - verite['N'][-1])**2 + 
                     (traj_ins_seule['E'][-1] - verite['E'][-1])**2)
   print(f"Erreur INS: {err_ins:.0f} m")
   ```

3. **Vérifier amélioration:**
   ```python
   err_ekf = np.sqrt((traj_ekf['N'][-1] - verite['N'][-1])**2 + 
                     (traj_ekf['E'][-1] - verite['E'][-1])**2)
   amelioration = (1 - err_ekf / err_ins) * 100
   print(f"Amélioration: {amelioration:.1f}%")
   ```

---

## Prochaines Étapes

Une fois tous les tests passés:

1. ✓ Exécuter notebook complet pour chaque scénario
2. ✓ Générer et sauvegarder les figures
3. ✓ Documenter les résultats dans un rapport
4. ✓ Archiver les résultats de référence

**Bon test!**
