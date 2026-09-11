# Étape 1 - Extraction Multi-Sources

## Objectif

Documenter et valider l'extraction des données avant l'EDA : sources, formats, problèmes
détectés, décisions prises.

Notebook associé : [`Projet/notebooks/etape_1_extraction.ipynb`](../notebooks/etape_1_extraction.ipynb)

**L'extraction est rejouée dans le notebook**, avec une garde de cache : le fichier brut
n'est retraité que si l'un des jeux produits est absent. L'entonnoir de filtrage est donc
reproductible, pas seulement documenté.

---

## 1. Source identifiée

| Élément | Valeur |
|---|---|
| Fichier | `Projet/csv/dataset.csv` |
| Contenu | INSERSUP, insertion professionnelle des diplômés du supérieur |
| Millésime de diffusion | `2026_S1` |
| Format | CSV |
| Taille | 773 Mo |
| Encodage | UTF-8 **avec BOM** → `encoding='utf-8-sig'` obligatoire |
| Séparateur | point-virgule (`;`) |
| Séparateur décimal | point (`.`) |
| En-tête | Oui, sur la première ligne |
| Codes de valeur manquante | `nd` (non disponible), `ns` (non significatif), chaîne vide |
| Producteur | Ministère de l'Enseignement supérieur et de la Recherche (SIES) |
| Licence | Licence Ouverte / Open Licence (Etalab) : réutilisation libre avec mention de la source |
| Portail | data.enseignementsup-recherche.gouv.fr |

Une seule source à ce jour. L'ajout d'une seconde source dans un second format reste à
faire, voir étape 0 section 4.

---

## 2. Paramètres de chargement retenus

```python
PARAMS_LECTURE = {
    "sep": ";",
    "encoding": "utf-8-sig",
    "dtype": str,                # conversion numérique explicite ensuite
    "na_values": ["nd", "ns"],
}
TAILLE_BLOC = 200_000            # lecture par blocs : 773 Mo ne tiennent pas en mémoire
```

Trois points justifient ces paramètres :

- **`utf-8-sig`** : sans lui, la première colonne s'appelle `﻿Diffusion des données`
  et tout accès par nom échoue.
- **`na_values`** : INSERSUP code la non-diffusion par `nd` et `ns`. Sans déclaration,
  ces valeurs deviennent des chaînes et polluent silencieusement les colonnes numériques.
- **Lecture par blocs** : le poste dispose de moins de mémoire que ce que réclamerait le
  fichier chargé d'un seul tenant.

---

## 3. Problèmes détectés au chargement

### 3.1 La colonne cible du cadrage est vide (bloquant, résolu)

`6-Taux d'emploi - 6 mois après le diplôme` ne contient **aucune valeur** sur les
1 036 781 lignes. Même constat pour ses variantes à 12 et 18 mois.

Neuf colonnes sont entièrement vides dans ce millésime :

- `6-Taux d'emploi`, `12-Taux d'emploi`, `18-Taux d'emploi`
- `6-Taux de sortants en emploi à l'étranger` et ses variantes 12 et 18 mois
- les trois colonnes de salaire à 6 mois (1er quartile, médiane, 3e quartile)

**Résolution** : la cible devient `6-Taux d'emploi salarié en France - 6 mois après le
diplôme`, remplie sur 438 696 lignes (42,3 %).

### 3.2 Le fichier contient ses propres agrégats (structurel, résolu)

INSERSUP est un cube **avec ses marges**. Quatre familles de totaux cohabitent avec le
détail dans les mêmes lignes :

| Famille | Colonnes | Valeur de total |
|---|---|---|
| Démographique | `Genre`, `Nationalité`, `Régime d'inscription`, `Obtention du diplôme` | `ensemble` |
| Temporelle | `Promotion` | cumuls de deux années (`2019,2020`) |
| Géographique | `Région`, `Établissement` | `National` |
| Disciplinaire | `Domaine disciplinaire`, `Discipline`, `Secteur disciplinaire` | `Tous domaines...`, `Toutes disciplines`, `Tous secteurs...` |

Entraîner un modèle sur le fichier brut ferait apprendre sur des lignes qui recomptent
leurs propres sous-lignes, avec fuite de la cible du total vers ses composantes.

**Résolution** : production de deux jeux distincts, voir section 5.

### 3.3 Colonnes réclamées mais inexistantes (résolu)

La version précédente de cette étape demandait des taux d'emploi à 24 et 30 mois. Ces
colonnes n'existent que pour l'emploi *salarié en France*, pas pour le taux d'emploi
global. Le notebook vérifie désormais par `assert` que chaque colonne demandée existe,
au lieu de filtrer les absentes en silence.

### 3.4 Pas de clé primaire native (résolu)

La colonne `id` du fichier source est entièrement vide. La clé métier reconstruite sur les
**libellés** (établissement × type de diplôme × domaine × discipline × secteur × libellé ×
promotion) laisse **144 lignes en trop**, soit 261 lignes impliquées dans un conflit. En
remplaçant le seul nom d'établissement par son code UAI, il en reste encore **107**.

Ces conflits ne sont pas des duplications : ce sont des formations différentes qui portent
le même nom. Les libellés ne sont pas des identifiants, ni côté diplôme ni côté
établissement :

- 1 290 libellés de diplôme pour **1 408 codes SISE** : 91 libellés sont portés par
  plusieurs codes, jusqu'à 6 pour `SCIENCES HUMAINES ET SOCIALES : PSYCHOLOGIE` ;
- 329 noms d'établissement pour **365 codes UAI** : 29 noms sont des homonymes.

**Résolution** : `Code du diplôme SISE` a été ajouté au schéma d'extraction. La clé
`Code UAI × Code SISE × Promotion` est unique, **0 conflit**, et chacune de ses trois
colonnes est nécessaire. La vérification est faite dans le notebook de l'étape 2, qui teste
cinq clés candidates.

### 3.5 Seuil de publication

INSERSUP ne publie aucun taux sous 20 sortants : l'effectif minimal observé dans le jeu
de modélisation est exactement 20. Les petites formations sont donc structurellement
absentes. À mentionner comme limite du projet.

### 3.6 Autres observations

- `Source de données` compte deux modalités, mais les 886 lignes `IP augmentée` n'ont
  pas de cible. La colonne est constante sur le périmètre retenu et a été écartée.
- Les colonnes `6-Flag` et `6-Exception` documentent la fiabilité statistique
  (`*` = cumul de deux promotions pour effectif insuffisant). Elles sont conservées dans
  le jeu analytique et retirées du jeu de modélisation, où le cas est déjà exclu.

---

## 4. Tableau récapitulatif de la source

| Source | Format | Fichier | Lignes | Colonnes | Observations |
|---|---|---|---|---|---|
| 1 | CSV | `Projet/csv/dataset.csv` | 1 036 781 | 101 | BOM UTF-8, `sep=';'`, manquants `nd`/`ns`, 9 colonnes entièrement vides, agrégats mélangés au détail |

---

## 5. Jeux produits

### Entonnoir de filtrage

| Étape | Lignes restantes |
|---|---|
| Fichier brut | 1 036 781 |
| Cible renseignée | 438 696 |
| + démographie = `ensemble` | 78 535 |
| + obtention du diplôme = `diplômé` | 37 472 |
| + promotion simple (non cumulée) | 27 149 |
| + hors marges géographiques et disciplinaires | **17 065** |

### Livrables

| Fichier | Lignes | Colonnes | Taille | Usage |
|---|---|---|---|---|
| `csv/dataset_phase1_modelisation.csv` | 17 065 | 23 | 5,0 Mo | Phase 7 : une ligne = une formation × promotion, sans double comptage |
| `csv/dataset_phase1_analytique.csv` | 438 696 | 31 | 147 Mo | Phases 2 et 5 : tous niveaux conservés, marqués par `ligne_agregee`, `promotion_cumulee`, `marge_geo_disc` |

Le jeu analytique est exclu du dépôt git par `.gitignore` : il pèse plus que la limite
de 100 Mo par fichier de GitHub et se régénère en une exécution du notebook.

Le jeu analytique conserve les agrégats parce que l'EDA en a besoin, notamment pour la
question business 3 sur le genre, la nationalité et le régime d'inscription. Les
indicateurs de niveau permettent de ne jamais mélanger un total et un détail.

### Colonnes du jeu de modélisation

**Dimensions (11)** : Région, Académie, Établissement, **Code UAI de l'établissement**
(clé de jointure vers une source d'enrichissement), **Code du diplôme SISE**, Type de
diplôme, Domaine disciplinaire, Discipline, Secteur disciplinaire, Libellé du diplôme,
Promotion

**Mesures à 6 mois (7)** : nombre de sortants, nombre de poursuivants, **taux d'emploi
salarié en France (cible)**, nombre et taux de sortants en emploi stable, nombre et taux
de sortants en emploi non salarié

**Suivi longitudinal (4)** : taux d'emploi salarié en France à 12, 18, 24 et 30 mois
(17,2 % de valeurs manquantes sur 24 et 30 mois)

**Dérivée (1)** : `promotion_debut`, année de début de promotion en entier

---

## 6. Validation post-extraction

| Contrôle du guide | Résultat |
|---|---|
| Dimensions cohérentes | 17 065 × 23, conforme à l'entonnoir de filtrage rejoué dans le notebook |
| Types corrects | 10 colonnes catégorielles, 12 colonnes numériques, conversion explicite vérifiée |
| Aperçu correct | `head()` lisible, accents corrects, aucune colonne décalée |
| Valeurs manquantes localisées | Uniquement sur les horizons 24 et 30 mois (17,2 %) |
| Unicité | Clé primaire `Code UAI × Code SISE × Promotion` : unique, 0 conflit (voir 3.4) |

Distribution de la cible : moyenne 55,9 · médiane 56,1 · écart-type 18,5 · min 0 ·
max 100. Unimodale et centrée, adaptée à une régression.

---

## 7. Checklist de la phase 1

- [x] Le fichier source est identifié et accessible
- [x] Le CSV est chargé sans erreur
- [x] Le séparateur, l'encodage et les codes de valeur manquante sont validés
- [x] Les colonnes utiles sont identifiées, et leur existence est vérifiée par `assert`
- [x] Le remplissage réel de chaque colonne numérique a été mesuré
- [x] La colonne cible a été validée sur les données, pas seulement sur l'en-tête
- [x] Les niveaux d'agrégation ont été identifiés et traités
- [x] Les types numériques sont convertis correctement
- [x] Le tableau récapitulatif est complété
- [x] Les problèmes repérés sont documentés
- [x] Les paramètres de chargement sont notés
- [x] Les deux jeux produits sont exportés
- [x] L'entonnoir de filtrage est chiffré et rejoué dans le notebook
- [x] L'origine et la licence des données sont documentées
- [ ] **Une seconde source dans un second format est chargée** : reste à faire

---

## 8. Réponses aux questions de réflexion du guide

**Qualité des sources.** Source unique et institutionnelle, donc fiable sur la collecte,
mais dégradée par la politique de diffusion : 58 % des lignes n'ont pas de cible et rien
n'est publié sous 20 sortants.

**Jointures à venir.** Le pont naturel vers une seconde source est le
`Code UAI de l'établissement`, identifiant national renseigné sur 100 % des lignes et
présent dans la plupart des référentiels d'établissements. Attention : il vaut `all` sur
les lignes d'agrégat national, valeur à exclure avant toute jointure.

**Données manquantes.** Le taux d'emploi global (salarié et non salarié réunis) aurait
été une meilleure cible que le seul emploi salarié. Il est absent de ce millésime. Les
salaires à 6 mois manquent également, ce qui empêche de croiser insertion et rémunération
à cet horizon.

**Granularité.** Le fichier mélange quatre niveaux d'agrégation. C'est le point traité
en 3.2, et la raison d'être des deux jeux produits.

---

## 9. Prochaine étape

Phase 2, EDA diagnostique sur `csv/dataset_phase1_analytique.csv`.
