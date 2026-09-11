# Étape 3 - Nettoyage, feature engineering et séparation

## Objectif

Exécuter le cahier des charges produit par le rapport de qualité de l'étape 2, enrichir le
jeu, le documenter, puis le séparer en apprentissage et test.

Notebook : [`Projet/notebooks/etape_3_preparation.ipynb`](../notebooks/etape_3_preparation.ipynb)

La règle qui gouverne l'étape : **rien de ce qui s'apprend sur les données ne se fait ici**.
Imputation, encodage et mise à l'échelle appartiennent à la pipeline des étapes 4 et 5. Ce
qui se fait ici, ce sont des corrections d'erreurs et des calculs déterministes ligne à
ligne.

---

## 1. Nettoyage

Le jeu d'origine est chargé une fois et n'est jamais modifié : toutes les transformations
travaillent sur une copie, ce qui rend le comparatif avant / après possible.

### Journal de nettoyage

Chaque action est journalisée avec sa dimension qualité, son volume et sa justification.
Le journal est écrit dans `csv/nettoyage_log.json`.

| Action | Dimension | Lignes | Justification |
|---|---|---:|---|
| Suppression des doublons de ligne complète | Unicité | 0 | Le filtrage des marges à l'étape 1 les avait déjà écartés |
| Contrôle de la clé primaire UAI × SISE × Promotion | Unicité | 0 | Clé unique validée à l'étape 2, aucune agrégation nécessaire |
| Normalisation des espaces multiples et de bord | Cohérence | 13 | Espaces doubles internes issus de la saisie |
| Passage des libellés de diplôme en majuscules | Cohérence | 390 | Convention de publication de la source, trois libellés y dérogeaient |
| Mise à `NaN` du taux d'emploi stable incohérent | Cohérence | 11 | Taux publié contredit par les effectifs publiés |
| Conservation des valeurs atypiques de la cible | Exactitude | 31 | Valeurs réelles sur petits effectifs |
| Suppression de la colonne redondante `promotion_debut` | Exactitude | 17 065 | Strictement identique à `Promotion` |

### Détail des décisions

**Formats.** Les 13 libellés à espaces doubles produisaient deux écritures d'un même
diplôme, comptées comme deux libellés distincts. Après normalisation, le nombre de libellés
distincts passe de 1 290 à 1 289.

**Les 11 anomalies de taux d'emploi stable.** Le taux publié et l'effectif publié se
contredisent, et rien ne permet de savoir lequel est faux. Décision : mettre le taux à
`NaN` et **conserver la ligne**. La cible n'est pas concernée par l'anomalie, il n'y a donc
aucune raison de perdre l'observation ; propager une valeur dont on sait qu'elle est fausse
serait pire que l'absence de valeur.

**Valeurs atypiques.** Aucune suppression. Les 31 formations signalées ont un effectif
médian de 27 sortants : sur un si petit effectif, un taux extrême est réel. Les supprimer
retirerait du jeu les cas les plus difficiles et gonflerait artificiellement le score.

### Comparatif avant / après

| Indicateur | Avant | Après | Écart |
|---|---:|---:|---:|
| Lignes | 17 065 | 17 065 | 0 |
| Colonnes | 23 | 22 | −1 |
| Doublons complets | 0 | 0 | 0 |
| Doublons sur la clé primaire | 0 | 0 | 0 |
| Libellés de diplôme distincts | 1 290 | 1 289 | −1 |
| Valeurs manquantes | 5 884 | 5 895 | +11 |
| Moyenne de la cible | 55,889 | 55,889 | 0 |
| Écart-type de la cible | 18,469 | 18,469 | 0 |

Aucune ligne perdue, distribution de la cible inchangée : le nettoyage n'a pas déformé ce
qu'on cherche à prédire. Le gros du travail de mise en forme avait été fait à l'étape 1 en
écartant les marges du cube ; le jeu arrivait déjà propre, et le dire est plus honnête que
d'inventer des corrections pour remplir un journal.

---

## 2. Feature engineering

Dix variables créées, couvrant les cinq familles attendues. Chacune répond à une hypothèse
formulée à la fin de l'étape 2.

| Famille | Variable | Lien avec la cible |
|---|---|---:|
| Indicateur | `est_diplome_professionnalisant` | **+0,407** |
| Calculée | `ratio_poursuite` | **−0,311** |
| Agrégée | `taille_mediane_secteur` | **+0,239** |
| Indicateur | `promotion_choc_sanitaire` | −0,181 |
| Calculée | `taille_formation` | −0,151 |
| Temporelle | `anciennete_promotion` | −0,105 |
| Agrégée | `part_sortants_etablissement` | −0,032 |
| Agrégée | `nb_formations_etablissement` | +0,032 |
| Agrégée | `nb_etablissements_par_diplome` | +0,020 |
| Catégorielle | `tranche_effectif` | eta² = 0,003 |

Trois variables portent un signal net. `ratio_poursuite` confirme directement l'hypothèse 1
de l'étape 2 : plus la part de diplômés qui poursuivent leurs études est élevée, plus le
taux d'emploi salarié baisse.

Les quatre dernières sont presque plates. Elles sont **conservées quand même** : une
corrélation linéaire faible n'exclut pas un apport en interaction dans une forêt. L'étape 5
tranche sur l'importance réelle des variables, et le résultat est instructif :
`nb_etablissements_par_diplome`, dont la corrélation vaut 0,02, ressort parmi les variables
les plus utiles au modèle.

### Redondances assumées

`anciennete_promotion` et `promotion_choc_sanitaire` se déduisent toutes deux de
`Promotion`, elle-même fournie comme variable catégorielle. Ce n'est pas un oubli :
l'encodage one-hot donne un effet libre par année, `anciennete_promotion` donne une
variable ordonnée sur laquelle un arbre peut couper une fois pour toutes, et
`promotion_choc_sanitaire` isole explicitement l'hypothèse testée. L'étape 5 dit laquelle
des trois formes le modèle utilise réellement.

### Contrôle anti-fuite

Aucune variable créée n'utilise la cible. Deux tests exécutables le vérifient.

1. **Indépendance à la cible.** La cible est permutée aléatoirement, puis les variables sont
   recalculées : elles sont strictement identiques. Un `assert` échoue sinon.
2. **Sensibilité au découpage.** Trois variables sont des agrégats calculés sur l'ensemble
   du jeu. Recalculées sur le seul jeu d'apprentissage, l'écart relatif médian de
   `taille_mediane_secteur` est de **0,00 %** (maximum 15,79 %), et la corrélation entre les
   deux calculs de `nb_formations_etablissement` est de **0,9986**.

Ces variables décrivent le catalogue d'un établissement ou la taille usuelle d'un secteur :
elles seraient connues d'un référentiel avant toute prédiction. Aucune information sur la
cible du test ne transite par elles.

---

## 3. Périmètre du modèle

**19 variables explicatives** : 8 catégorielles, 11 numériques, dont 10 créées à cette
étape. Aucune valeur manquante.

### Variables exclues

| Colonnes | Motif | Détail |
|---|---|---|
| Taux d'emploi à 12, 18, 24 et 30 mois | Fuite de cible | Mesuré après les 6 mois à prédire (r = 0,85 à 12 mois) |
| Taux et nombre en emploi stable | Fuite de cible | Résultat d'insertion au même horizon que la cible |
| Taux et nombre en emploi non salarié | Fuite de cible | Résultat d'insertion au même horizon que la cible |
| `Établissement`, `Libellé du diplôme` | Cardinalité | 329 et 1 290 modalités : le modèle mémoriserait |
| `Code UAI`, `Code SISE` | Identifiant | Exploités via les variables agrégées dérivées |
| `promotion_debut` | Redondance | Supprimé au nettoyage |

---

## 4. Dictionnaire de données

Généré depuis le jeu final, donc impossible à désynchroniser des données réelles. Un
`assert` échoue si une colonne n'est pas décrite. 32 colonnes documentées avec type, rôle,
manquants, modalités, exemple et description.

Fichier : [`Projet/DATA_DICTIONARY.md`](../DATA_DICTIONARY.md)

---

## 5. Export et séparation

Jeu final exporté : `csv/dataset_phase3_final.csv`, 17 065 × 32.

Découpage unique, réutilisé à l'identique aux étapes 4 et 5 :

```python
train_test_split(X, y, test_size=0.20, random_state=42)
```

| Sous-ensemble | Lignes | Part | Moyenne de la cible | Écart-type |
|---|---:|---:|---:|---:|
| Apprentissage | 13 652 | 80 % | 55,89 | 18,45 |
| Test | 3 413 | 20 % | 55,89 | 18,53 |

Six `assert` verrouillent le périmètre : cible absente de `X`, aucune variable postérieure
à 6 mois, aucun identifiant, aucune valeur manquante, aucune ligne perdue, aucun
recouvrement entre apprentissage et test.

### Ce qui n'est volontairement pas fait ici

Aucun encodage, aucune mise à l'échelle, aucune imputation. Ces trois opérations apprennent
quelque chose sur les données : les modalités présentes, la moyenne et l'écart-type, la
valeur de remplacement. Les appliquer avant le découpage laisserait fuir dans
l'apprentissage une information issue du test. Elles sont définies à l'étape 4 **à
l'intérieur d'un `Pipeline`**, réajusté sur les seules données d'entraînement de chaque pli.

---

## Checklist

**Nettoyage**

- [x] Doublons détectés et traités (0 à supprimer, clé primaire vérifiée)
- [x] Valeurs aberrantes traitées, décision de conservation justifiée
- [x] Formats standardisés
- [x] Valeurs manquantes gérées avec une stratégie explicite
- [x] Types de données corrigés et contrôlés
- [x] Données originales préservées
- [x] Journal de nettoyage complet écrit
- [x] Comparatif avant / après produit

**Transformation et feature engineering**

- [x] 10 variables créées, couvrant les 5 familles attendues
- [x] Chaque variable répond à une hypothèse formulée à l'étape 2
- [x] Force du lien avec la cible mesurée pour chacune
- [x] Contrôle anti-fuite par permutation de la cible
- [x] Sensibilité des agrégats au découpage mesurée
- [x] Dictionnaire de données généré depuis le jeu réel
- [x] Jeu final exporté
- [x] Découpage apprentissage / test unique et reproductible
