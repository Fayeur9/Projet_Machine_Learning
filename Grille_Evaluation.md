# Grille d'Évaluation — Projet Final ML

Cette grille détaille les critères d'évaluation du projet final, de la Phase 0 à la soutenance.

**Total : 100 points** — c'est la note du **Bloc 8 (Évaluation)**.

---

## Vue d'ensemble de la notation

| Phase | Points | Poids |
|-------|--------|-------|
| Phase 0 : Cadrage (business **et** prédictif) | /6 | 6% |
| Phase 1 : Extraction | /4 | 4% |
| Phase 2 : Diagnostic qualité | /8 | 8% |
| Phase 3 : Nettoyage | /12 | 12% |
| Phase 4 : Transformation & feature engineering | /8 | 8% |
| Phase 5 : EDA analytique | /12 | 12% |
| Phase 6 : Visualisation | /8 | 8% |
| **Phase 7 : Modélisation ML** | **/25** | **25%** |
| Phase 8 : Documentation & reproductibilité | /5 | 5% |
| Phase 9 : Soutenance | /7 | 7% |
| Utilisation de l'IA | /5 | 5% |
| **TOTAL** | **/100** | **100%** |

> **Le cœur de la note est la Phase 7.** Ce cours est un cours de Machine Learning : le pipeline data est le moyen, le modèle est la fin.

---

## Règles éliminatoires

Trois manquements plafonnent la note, quelle que soit la qualité du reste :

| Manquement | Plafond |
|---|---|
| **Fuite de données** non détectée (preprocessing avant le split, ou feature contenant la réponse) | Phase 7 plafonnée à 8/25 |
| **Notebook non exécutable** de bout en bout | Note finale plafonnée à 50/100 |
| **Aucune baseline** calculée | Phase 7 plafonnée à 15/25 |

---

## Phase 0 : Cadrage (6 points)

| Critère | 0-1 pt | 2 pts | 3 pts |
|---------|--------|-------|-------|
| **Sujet et questions business** (3 pts) | Sujet vague, < 3 questions | Sujet clair, 3-4 questions | Sujet motivé, 5 questions SMART |
| **Cadrage prédictif** (3 pts) | Cible absente ou floue | Cible et type de problème identifiés | + métrique justifiée par le métier, répartition de la cible analysée |

### Checklist

- [ ] Sujet et contexte définis, dataset validé par le formateur
- [ ] 3 à 5 questions business formulées
- [ ] Question prédictive formulée
- [ ] Colonne cible nommée et présente dans les données
- [ ] Classification / régression tranché
- [ ] Répartition de la cible examinée

### Note Phase 0 : _____ / 6

---

## Phase 1 : Extraction (4 points)

| Critère | 0-1 pt | 2-3 pts | 4 pts |
|---------|--------|---------|-------|
| **Chargement des données** (4 pts) | Erreurs non résolues | Chargement fonctionnel, 1 source | Plusieurs sources/formats, types et encodage maîtrisés |

### Checklist

- [ ] Données chargées sans erreur
- [ ] Types de données vérifiés
- [ ] Origine et licence des données mentionnées
- [ ] Tableau récapitulatif des données complété

### Note Phase 1 : _____ / 4

---

## Phase 2 : Diagnostic qualité (8 points)

| Critère | 0-2 pts | 3-5 pts | 6-8 pts |
|---------|---------|---------|---------|
| **Exhaustivité du diagnostic** (8 pts) | 1-2 dimensions analysées | 3-4 dimensions | 5 dimensions + rapport complet et priorisé |

### Les 5 dimensions

| Dimension | Analysée ? | Problèmes identifiés ? |
|-----------|------------|------------------------|
| Complétude | ☐ | ☐ |
| Unicité | ☐ | ☐ |
| Cohérence | ☐ | ☐ |
| Exactitude | ☐ | ☐ |
| Fraîcheur | ☐ | ☐ |

### Checklist

- [ ] Valeurs manquantes quantifiées
- [ ] Doublons détectés et comptés
- [ ] Incohérences de format identifiées
- [ ] Outliers repérés
- [ ] Problèmes priorisés

### Note Phase 2 : _____ / 8

---

## Phase 3 : Nettoyage (12 points)

| Critère | 0-3 pts | 4-7 pts | 8-12 pts |
|---------|---------|---------|----------|
| **Traitement des problèmes** (7 pts) | Problèmes non traités | Principaux problèmes traités | Tous traités, stratégies justifiées |
| **Traçabilité** (3 pts) | Pas de log | Log partiel | Log complet avec justifications |
| **Validation** (2 pts) | Pas de vérification | Vérification basique | Comparatif avant/après détaillé |

### Checklist

- [ ] Doublons supprimés
- [ ] Valeurs aberrantes traitées (et le choix justifié)
- [ ] Formats standardisés
- [ ] Valeurs manquantes gérées avec une stratégie explicite
- [ ] Types de données corrigés
- [ ] Données originales préservées

> ⚠️ **Attention** : l'imputation destinée au modèle doit se faire **dans la pipeline** (Phase 7), pas ici. Ce qui est nettoyé en Phase 3, ce sont les erreurs de saisie et les incohérences — pas les statistiques apprises sur les données.

### Note Phase 3 : _____ / 12

---

## Phase 4 : Transformation & feature engineering (8 points)

| Critère | 0-2 pts | 3-5 pts | 6-8 pts |
|---------|---------|---------|---------|
| **Features créées** (5 pts) | 0-2 features | 3-6 features | 7+ features variées et **pertinentes pour la prédiction** |
| **Documentation du dataset** (3 pts) | Absente | Liste des colonnes | Description complète, jointures expliquées |

### Types de features

| Type | Créée ? | Exemples |
|-----------------|---------|----------|
| Temporelles | ☐ | mois, jour_semaine, ancienneté |
| Agrégées | ☐ | moyenne_par_groupe, total_par_catégorie |
| Calculées | ☐ | ratio, marge, densité |
| Catégorielles | ☐ | segment, tranche |
| Indicateurs | ☐ | is_nouveau, a_retour |

> Une feature n'est bonne que si elle **aide le modèle**. En Phase 7, vérifiez lesquelles ressortent réellement importantes.

### Note Phase 4 : _____ / 8

---

## Phase 5 : EDA analytique (12 points)

| Critère | 0-3 pts | 4-8 pts | 9-12 pts |
|---------|---------|---------|----------|
| **Couverture des questions** (5 pts) | < 3 questions traitées | Toutes traitées | + découvertes inattendues |
| **Quantification** (4 pts) | Insights sans chiffres | Chiffres présents | Chiffres contextualisés |
| **Lien avec la cible** (3 pts) | Aucune analyse de la cible | Corrélations features/cible explorées | + hypothèses formulées sur ce que le modèle devrait apprendre |

### Note Phase 5 : _____ / 12

---

## Phase 6 : Visualisation (8 points)

| Critère | 0-2 pts | 3-5 pts | 6-8 pts |
|---------|---------|---------|---------|
| **Quantité et variété** (3 pts) | < 3 visualisations | 5-6 visualisations | 7+ visualisations variées |
| **Qualité du design** (3 pts) | Mauvaises pratiques | Propre et lisible | Professionnel et impactant |
| **Storytelling** (2 pts) | Pas de fil conducteur | Récit présent | Récit structuré et convaincant |

### Checklist

- [ ] Titres clairs, axes labellisés avec unités
- [ ] Légendes présentes si nécessaire
- [ ] Pas de 3D ni d'axe tronqué
- [ ] Cohérence visuelle

### Note Phase 6 : _____ / 8

---

## Phase 7 : Modélisation ML (25 points)

**C'est le cœur de l'évaluation.**

### 7.1 — Rigueur méthodologique (8 pts)

| Critère | 0-2 pts | 3-5 pts | 6-8 pts |
|---------|---------|---------|---------|
| Split, pipeline, absence de fuite | Fuite présente ou pas de split | Split + pipeline corrects | + test ouvert une seule fois, `random_state` fixé partout |

- [ ] `train_test_split` réalisé **avant** tout preprocessing
- [ ] `stratify=y` en classification
- [ ] Tout le preprocessing est dans un `ColumnTransformer` / `Pipeline`
- [ ] Aucune colonne fuitante dans `X` (identifiants supprimés)
- [ ] Le jeu de test n'a servi qu'une fois
- [ ] `random_state` fixé (résultats reproductibles)

### 7.2 — Baseline et comparaison de modèles (7 pts)

| Critère | 0-2 pts | 3-4 pts | 5-7 pts |
|---------|---------|---------|---------|
| Démarche comparative | 1 seul modèle, pas de baseline | Baseline + 2 modèles | Baseline + 3 modèles via `GridSearchCV`, tableau `cv_results_` à l'appui |

- [ ] Baseline (`DummyClassifier` / `DummyRegressor`) calculée
- [ ] Au moins 3 modèles comparés, dont un modèle simple (linéaire / logistique)
- [ ] Hyperparamètres explorés par `GridSearchCV` avec `cv=5`
- [ ] Tableau de comparaison présenté et commenté
- [ ] Le choix du modèle final est **justifié**, pas subi

### 7.3 — Évaluation (6 pts)

| Critère | 0-1 pt | 2-4 pts | 5-6 pts |
|---------|--------|---------|---------|
| Métriques et diagnostic | Un seul chiffre d'accuracy | Métriques adaptées reportées | + surapprentissage diagnostiqué et argumenté |

- [ ] Métrique principale cohérente avec le problème (et justifiée)
- [ ] Classification : `classification_report` + matrice de confusion interprétée
- [ ] Régression : MAE / RMSE **dans l'unité de la cible** + R² + résidus
- [ ] Écart train / validation analysé et **traduit en nombre de lignes**
- [ ] Score de test reporté honnêtement, gain sur la baseline chiffré

### 7.4 — Interprétation et limites (4 pts)

| Critère | 0-1 pt | 2-3 pts | 4 pts |
|---------|--------|---------|-------|
| Compréhension du modèle | Aucune interprétation | Features importantes listées | + reliées à l'EDA, limites et biais discutés |

- [ ] Top features (`feature_importances_` ou `coef_`) présenté
- [ ] Cohérence avec les corrélations de la Phase 5 discutée
- [ ] Cas d'échec du modèle identifiés
- [ ] Risque de biais évoqué (lien Bloc 7)

### Note Phase 7 : _____ / 25

---

## Phase 8 : Documentation & reproductibilité (5 points)

| Critère | 0-1 pt | 2-3 pts | 4-5 pts |
|---------|--------|---------|---------|
| Documentation et livraison | Notebook non documenté | Data Dictionary + notebook commenté | + notebook exécutable de bout en bout, modèle sauvegardé en .joblib |

### Checklist

- [ ] Dataset final exporté
- [ ] Data Dictionary complet
- [ ] Notebook structuré, commenté, exécutable en une passe
- [ ] Pipeline complète sauvegardée (`joblib`)
- [ ] Démonstration de prédiction sur de nouvelles données brutes

### Note Phase 8 : _____ / 5

---

## Phase 9 : Soutenance (7 points)

| Critère | 0-1 pt | 2-4 pts | 5-7 pts |
|---------|--------|---------|---------|
| **Clarté du récit** (3 pts) | Lecture des slides | Structure claire | Récit fluide, chiffres mémorables |
| **Défense du modèle** (4 pts) | Ne sait pas expliquer son modèle | Explique la démarche | Défend ses choix, assume ses limites, répond aux objections |

### Checklist

- [ ] Pitch tenu dans le temps (7 min)
- [ ] Le modèle est expliqué : cible, métrique, comparaison, score, limites
- [ ] Les limites sont mentionnées **proactivement**
- [ ] Les questions du jury reçoivent des réponses argumentées

### Note Phase 9 : _____ / 7

---

## Utilisation de l'IA (5 points)

| Critère | 0-1 pt | 2-3 pts | 4-5 pts |
|---------|--------|---------|---------|
| **Intégration de l'IA** (5 pts) | Non utilisée, ou code copié sans compréhension | Utilisée ponctuellement | Utilisée stratégiquement, prompts documentés, résultats vérifiés |

> ⚠️ Un code généré par IA que l'étudiant ne sait pas expliquer en soutenance est pénalisé, pas valorisé.

### Preuves d'utilisation

| Phase | Prompt documenté ? | Utilité démontrée ? |
|-------|--------------------|---------------------|
| Cadrage | ☐ | ☐ |
| Diagnostic | ☐ | ☐ |
| Nettoyage | ☐ | ☐ |
| Feature engineering | ☐ | ☐ |
| Modélisation | ☐ | ☐ |
| Interprétation | ☐ | ☐ |

### Note Utilisation IA : _____ / 5

---

## Récapitulatif des notes

| Phase | Note | Max |
|-------|------|-----|
| Phase 0 : Cadrage | _____ | /6 |
| Phase 1 : Extraction | _____ | /4 |
| Phase 2 : Diagnostic | _____ | /8 |
| Phase 3 : Nettoyage | _____ | /12 |
| Phase 4 : Transformation | _____ | /8 |
| Phase 5 : EDA analytique | _____ | /12 |
| Phase 6 : Visualisation | _____ | /8 |
| **Phase 7 : Modélisation ML** | **_____** | **/25** |
| Phase 8 : Documentation | _____ | /5 |
| Phase 9 : Soutenance | _____ | /7 |
| Utilisation IA | _____ | /5 |
| **TOTAL** | **_____** | **/100** |

Plafond éliminatoire appliqué : ☐ Non ☐ Oui — lequel : _______________

---

## Barème de conversion

| Note /100 | Note /20 | Appréciation |
|-----------|----------|--------------|
| 90-100 | 18-20 | Excellent — qualité professionnelle |
| 80-89 | 16-17 | Très bien — maîtrise solide |
| 70-79 | 14-15 | Bien — quelques points à améliorer |
| 60-69 | 12-13 | Satisfaisant — bases acquises |
| 50-59 | 10-11 | Passable — compétences partielles |
| < 50 | < 10 | Insuffisant — travail à reprendre |

---

## Commentaires généraux

### Points forts du projet

```
_________________________________________________________________
_________________________________________________________________
```

### Axes d'amélioration

```
_________________________________________________________________
_________________________________________________________________
```

### Observations sur la soutenance

```
_________________________________________________________________
_________________________________________________________________
```

---

## Signature

**Évaluateur** : _______________________

**Date** : _______________________

---

*Cette grille fait partie du workflow « Projet Final ML ».*
