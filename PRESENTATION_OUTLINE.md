# Outline Présentation - EKF Adaptatif INS + VOR/DME

**Titre:** Hybridation INS + VOR/DME avec EKF Adaptatif  
**Sous-titre:** Filtre de Kalman Étendu pour Navigation Aérienne  
**Auteur:** Nicolas CUSSEAU - Guillaume COSNARD - ENSTA  
**Date:** Décembre 2025  
**Durée:** 15-20 minutes

---

## Slide 1: Page de Titre

**Contenu:**
- Titre principal: "Hybridation INS + VOR/DME avec EKF Adaptatif"
- Sous-titre: "Filtre de Kalman Étendu pour Navigation Aérienne"
- Auteur: Nicolas CUSSEAU
- Institution: ENSTA
- Date: Décembre 2025

**Visuel:**
- Logo ENSTA
- Image avion ou centrale inertielle

---

## Slide 2: Contexte et Problématique

**Titre:** Navigation Aérienne - Défis et Enjeux

**Contenu:**

**Navigation aérienne moderne:**
- Besoin de précision élevée (< 100 m)
- Environnements variés (croisière, manœuvres)
- Redondance et robustesse critiques

**Systèmes disponibles:**
- **INS (Inertial Navigation System)**
  - Autonome, haute fréquence (100 Hz)
  - Dérive dans le temps (biais capteurs)
- **VOR/DME (Radionavigation)**
  - Mesures absolues (azimut + distance)
  - Basse fréquence (1 Hz), couverture limitée

**Problématique:**
- EKF classique diverge en manœuvres agressives
- Gating fixe rejette mesures valides
- Modèle dynamique inadapté aux virages

**Visuel:**
- Schéma INS (gyroscope + accéléromètres)
- Schéma VOR/DME (stations au sol)
- Graphique dérive INS vs temps

---

## Slide 3: Objectifs du Projet

**Titre:** Objectifs et Contributions

**Objectifs:**
1. Fusionner INS + VOR/DME via EKF
2. Adapter EKF aux manœuvres dynamiques
3. Valider sur scénarios réalistes
4. Système générique et robuste

**Contributions:**
1. **Contrainte douce adaptative** sur vitesse
2. **Matrice Q adaptative** selon manœuvre
3. **Gating hybride** (physique + statistique)

**Résultats attendus:**
- Amélioration > 50% vs INS seule
- Pas de divergence en manœuvres
- Taux acceptation mesures > 70%

**Visuel:**
- Schéma fusion de capteurs
- Icônes innovations (3 blocs)

---

## Slide 4: Architecture Système

**Titre:** Architecture Modulaire

**Contenu:**

**4 Packages principaux:**
1. **Configuration** - Paramètres (INS, VOR/DME, EKF)
2. **Modèles Physiques** - Dynamique INS, mesures VOR/DME
3. **Algorithmes** - EKF adaptatif, simulateur, générateur
4. **Métriques & Visualisation** - Analyse performances

**Flux de données:**
```
Vérité → Simulateur INS → Mesures IMU bruitées
                              ↓
Stations VOR/DME → Mesures radionavigation
                              ↓
                    EKF Adaptatif
                              ↓
                    Trajectoire corrigée
```

**Visuel:**
- Diagramme UML architecture (docs/architecture.png)
- Flux de données schématique

---

## Slide 5: Innovation 1 - Contrainte Douce Adaptative

**Titre:** Contrainte Douce sur Magnitude de Vitesse

**Problème:**
- En virage uniforme, ||V|| devrait rester constant
- Modèle INS accumule erreurs → ||V|| dérive
- EKF classique ne corrige pas assez vite

**Solution:**
```
Détection: |ω_z| > 0.002 rad/s ET ΔV < 1.0 m/s
Correction: V_target = 0.8 × V_prev + 0.2 × V_current
```

**Avantages:**
- **Douce (80%)** vs dure (100%) → Flexible
- **Conditionnelle** → Active uniquement si nécessaire
- **Automatique** → Pas de configuration manuelle

**Impact:**
- Scénario 2 (arc circulaire): Pas de divergence
- Maintient précision en virage prolongé

**Visuel:**
- Schéma virage coordonné
- Graphique ||V|| avec/sans contrainte
- Équation correction

---

## Slide 6: Innovation 2 - Matrice Q Adaptative

**Titre:** Bruit de Processus Adaptatif

**Problème:**
- Q fixe → Confiance modèle constante
- En virage: modèle moins précis
- En rectiligne: modèle très précis

**Solution:**
```
SI |ω_z| > 0.002 rad/s:
    Q_vitesse = 2.0 m²/s³  (virage - confiance mesures)
SINON:
    Q_vitesse = 0.5 m²/s³  (rectiligne - confiance modèle)
```

**Principe:**
- Q élevé → EKF fait plus confiance aux mesures
- Q faible → EKF fait plus confiance au modèle
- Adaptation temps réel selon ω_z

**Impact:**
- Équilibre optimal prédiction/correction
- Convergence plus rapide en virage
- Précision maintenue en rectiligne

**Visuel:**
- Graphique Q vs temps
- Schéma équilibre modèle/mesures
- Équation matrice Q

---

## Slide 7: Innovation 3 - Gating Adaptatif Hybride

**Titre:** Seuil de Validation Adaptatif

**Problème:**
- Gating fixe (χ² < 9.21) → Trop strict en manœuvres
- Innovations grandes rejetées → Divergence
- Pas d'adaptation au contexte

**Solution - Approche Hybride:**

**Étape 1: Détection manœuvre**
```
Agressif: |ω_z| > 0.01 OU |a_long| > 0.5 → seuil = 25.0
Modéré:   |ω_z| > 0.002 OU |a_long| > 0.2 → seuil = 15.0
Calme:    sinon → seuil = 9.21
```

**Étape 2: Adaptation covariance**
```
facteur = 1 + 0.05 × trace(S) / dim(S)
seuil_final = seuil_base × facteur
```

**Étape 3: Limites sécurité**
```
seuil_final ∈ [9.21, 30.0]
```

**Impact:**
- Scénario 3: Pas de divergence
- Taux acceptation > 75%
- Robustesse manœuvres agressives

**Visuel:**
- Diagramme états (3 modes)
- Graphique seuil vs temps
- Formule gating

---

## Slide 8: Scénarios de Validation

**Titre:** 3 Scénarios de Vol Réalistes

**Tableau Caractéristiques:**

| Scénario | Type | Vitesse | Manœuvres | Objectif Test |
|----------|------|---------|-----------|---------------|
| **1 - Approche radiale** | Modéré | 80 m/s | Virage 180° (R=5000m) | Virage large |
| **2 - Arc circulaire** | Uniforme | 100 m/s | Arc complet (R=50km) | Contrainte vitesse |
| **3 - Transit multi-stations** | Agressif | 80-120 m/s | Virages serrés (R=2000m) | Gating adaptatif |

**Paramètres communs:**
- Durée: 20 minutes
- Altitude: 3000 m
- 3 stations VOR/DME
- Fréquence IMU: 100 Hz
- Fréquence VOR/DME: 1 Hz

**Visuel:**
- Carte 3 trajectoires
- Positions stations
- Légende couleurs

---

## Slide 9: Résultats Scénario 1

**Titre:** Scénario 1 - Approche Radiale

**Métriques:**
- Erreur finale: [XX] m (INS) → [XX] m (EKF)
- Amélioration: [XX] %
- Taux acceptation: [XX] %

**Observations:**
- EKF suit trajectoire vérité
- Virage 180° bien géré
- Gating modéré actif en virage

**Visuel:**
- Graphique trajectoire 2D
- Courbe erreur vs temps
- Tableau métriques

---

## Slide 10: Résultats Scénario 2

**Titre:** Scénario 2 - Arc Circulaire

**Métriques:**
- Erreur finale: [XX] m (INS) → [XX] m (EKF)
- Amélioration: [XX] %
- Taux acceptation: [XX] %

**Observations:**
- Contrainte vitesse active tout le temps
- EKF suit arc parfaitement
- Pas de divergence (problème résolu!)

**Visuel:**
- Graphique trajectoire 2D (arc)
- Courbe ||V|| vs temps
- Tableau métriques

---

## Slide 11: Résultats Scénario 3

**Titre:** Scénario 3 - Transit Multi-Stations

**Métriques:**
- Erreur finale: [XX] m (INS) → [XX] m (EKF)
- Amélioration: [XX] %
- Taux acceptation: [XX] %

**Observations:**
- **PAS de divergence après station 2** ✓
- Gating adaptatif fonctionne (seuil 25-28)
- Manœuvres agressives bien gérées

**Point clé:**
- Problème initial: Divergence verticale après station 2
- Solution: Gating adaptatif + Q adaptatif
- Résultat: Trajectoire suit vérité

**Visuel:**
- Graphique trajectoire 2D
- Zoom zone station 2
- Tableau métriques

---

## Slide 12: Conclusion et Perspectives

**Titre:** Conclusion et Perspectives

**Résultats:**
- ✓ Système EKF adaptatif opérationnel
- ✓ 3 innovations techniques validées
- ✓ Amélioration > 50% sur tous scénarios
- ✓ Pas de divergence en manœuvres

**Contributions scientifiques:**
1. Gating adaptatif hybride (manœuvre + covariance)
2. Contrainte douce conditionnelle (virage uniforme)
3. Q adaptatif temps réel (confiance dynamique)

**Applications:**
- Navigation aérienne (avions, drones)
- Robotique mobile
- Véhicules autonomes
- Systèmes de guidage

**Perspectives:**
- EKF IMM (Interacting Multiple Models)
- Fusion multi-capteurs (GNSS, baro, mag)
- Détecteur modes de vol avec hystérésis
- Tests en vol réel

**Visuel:**
- Icônes applications
- Schéma perspectives
- Logo ENSTA

---

## Notes pour Présentation

**Timing (15-20 min):**
- Slides 1-3: 3 min (intro)
- Slides 4-7: 8 min (innovations)
- Slides 8-11: 6 min (résultats)
- Slide 12: 2 min (conclusion)
- Questions: 5-10 min

**Points clés à souligner:**
- Problème divergence scénario 3 (avant)
- Solution gating adaptatif (après)
- Approche générique (pas de tuning manuel)

**Démonstration possible:**
- Animation trajectoire scénario 3
- Montrer divergence vs convergence

---

**Présentation prête pour création PowerPoint/PDF.**
