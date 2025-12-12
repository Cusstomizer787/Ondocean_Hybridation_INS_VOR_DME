# Instructions pour l'Animation

## Modifications Appliquées

Le notebook `simulation_ins_vor_dme.ipynb` a été modifié pour résoudre le problème d'animation vide.

### 1. Nouvelle Cellule de Rechargement (Cellule 26)

Une nouvelle cellule a été ajoutée **avant** la cellule d'animation pour recharger le module `visualisation.py`:

```python
# Recharger module visualisation pour prendre en compte les corrections
import importlib
import visualisation
importlib.reload(visualisation)
from visualisation import animer_trajectoires

print('[OK] Module visualisation recharge')
```

**Objectif:** Forcer Python à recharger le module `visualisation.py` avec les corrections (notamment la ligne `idx_plot = max(1, idx)` qui corrige l'animation vide).

### 2. Cellule d'Animation Modifiée (Cellule 27)

La cellule d'animation a été modifiée pour utiliser **jshtml** au lieu de **ffmpeg**:

```python
# Animation trajectoires (peut prendre du temps)
import matplotlib
matplotlib.rcParams['animation.html'] = 'jshtml'  # Animation JavaScript interactive

anim = animer_trajectoires(verite, traj_ins_seule, traj_ekf, stations, vitesse_lecture=10)

# Affichage avec controles interactifs (play/pause/slider)
anim

# OPTIONNEL: Sauvegarde en fichier video (necessite ffmpeg installe)
# anim.save(f'animation_scenario_{numero_scenario}.mp4', fps=30, writer='ffmpeg')
```

**Avantages de jshtml:**
- Pas besoin d'installer ffmpeg
- Contrôles interactifs (play/pause/slider)
- Compatible avec tous les environnements Jupyter
- Plus fiable que HTML5 video

---

## Instructions d'Utilisation

### Étape 1: Recharger le Notebook

Dans Jupyter, **rechargez la page** (F5 ou Ctrl+R) pour prendre en compte les modifications du fichier `.ipynb`.

### Étape 2: Exécuter les Cellules

1. **Exécuter toutes les cellules précédentes** (jusqu'à la cellule 25)
   - Cela génère `verite`, `traj_ins_seule`, `traj_ekf`, `stations`

2. **Exécuter la cellule 26** (rechargement module)
   - Vous devriez voir: `[OK] Module visualisation recharge`

3. **Exécuter la cellule 27** (animation)
   - L'animation devrait s'afficher avec des contrôles interactifs

### Étape 3: Utiliser l'Animation

L'animation affiche:
- **Ligne noire avec x:** Trajectoire vérité
- **Ligne rouge pointillée:** INS seule (dérive)
- **Ligne bleue avec o:** INS + EKF (corrigée)
- **Triangles verts:** Stations VOR/DME
- **Marqueurs mobiles:** Position courante sur chaque trajectoire
- **Temps:** Affiché en haut à droite

**Contrôles:**
- **Play/Pause:** Bouton lecture
- **Slider:** Déplacer dans le temps
- **Vitesse:** Ajustable via `vitesse_lecture` (défaut: 10)

---

## Dépannage

### L'animation est toujours vide

**Cause:** Le module `visualisation.py` n'a pas été rechargé.

**Solution:**
1. Kernel → Restart & Clear Output
2. Réexécuter toutes les cellules depuis le début

### Erreur "MovieWriter not available"

**Cause:** Tentative d'utiliser ffmpeg qui n'est pas installé.

**Solution:** Vérifier que la cellule 27 utilise bien `jshtml` et non `to_html5_video()`.

### L'animation est lente

**Cause:** `vitesse_lecture` trop faible ou trajectoire trop longue.

**Solution:** Augmenter `vitesse_lecture` dans la cellule 27:
```python
anim = animer_trajectoires(..., vitesse_lecture=50)  # Plus rapide
```

---

## Résumé des Corrections Appliquées

### Fichiers Modifiés

1. **`visualisation.py`** (ligne 371)
   - Ajout: `idx_plot = max(1, idx)`
   - Corrige l'animation vide en assurant au moins 1 point

2. **`ekf.py`** (lignes 56-58, 89-92, 103-143, 180-181, 242-243)
   - Ajout gating adaptatif hybride
   - Calcul accélération longitudinale
   - Adaptation seuil selon manœuvre

3. **`modeles_dynamique.py`** (lignes 47-70, 151-193)
   - Contrainte douce adaptative sur vitesse
   - Matrice Q adaptative selon virage

4. **`simulation_ins_vor_dme.ipynb`**
   - Ajout cellule rechargement module
   - Modification cellule animation (jshtml)

---

## Validation

Pour valider que tout fonctionne:

1. **Scénario 1:** Trajectoire avec virage 180°
   - Animation doit montrer EKF suivant la vérité

2. **Scénario 2:** Arc circulaire
   - Animation doit montrer EKF suivant l'arc

3. **Scénario 3:** Transit multi-stations
   - Animation doit montrer EKF sans divergence
   - Pas de montée verticale après station 2

**Si les 3 scénarios fonctionnent → Système validé!**
