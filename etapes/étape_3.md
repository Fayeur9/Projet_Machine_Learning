# Étape 3 - Nettoyage, feature engineering et séparation

## Objectif

Exécuter le cahier des charges produit par le rapport de qualité de l'étape 2, enrichir le
jeu, le documenter, puis le séparer en apprentissage et test.

Notebook : [`etape_3_preparation.ipynb`](../notebooks/etape_3_preparation.ipynb)

La règle qui gouverne l'étape : **rien de ce qui s'apprend sur les données ne se fait ici**.
Imputation, encodage, mise à l'échelle et agrégats de contexte appartiennent à la pipeline,
définie dans [`modeles/protocole.py`](../modeles/protocole.py). Ce qui se fait ici, ce sont
des corrections d'erreurs et des calculs déterministes ligne à ligne.

> **Révision du protocole** (voir [étape 10](étape_10_revision.md)). La première version
> calculait ici quatre variables agrégées sur le jeu complet, test compris, et découpait
> ligne à ligne alors qu'une formation apparaît jusqu'à six fois. Les agrégats sont
> désormais appris dans la pipeline, sur les seules lignes d'entraînement, et le découpage
> est groupé par formation.

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

Neuf variables enrichissent le jeu, couvrant les cinq familles attendues. Chacune répond à
une hypothèse formulée à la fin de l'étape 2. Six se calculent ici, ligne à ligne ; trois
lisent d'autres lignes que la leur et sont donc apprises **dans la pipeline**.

| Famille | Variable | Calculée | Lien avec la cible |
|---|---|---|---:|
| Indicateur | `est_diplome_professionnalisant` | ici | **+0,407** |
| Calculée | `ratio_poursuite` | ici | **−0,311** |
| Indicateur | `promotion_choc_sanitaire` | ici | −0,181 |
| Calculée | `taille_formation` | ici | −0,151 |
| Temporelle | `anciennete_promotion` | ici | −0,105 |
| Catégorielle | `tranche_effectif` | ici | eta² = 0,003 |
| Agrégée | `taille_mediane_secteur` | pipeline | +0,234 |
| Agrégée | `nb_formations_etablissement` | pipeline | +0,043 |
| Agrégée | `nb_etablissements_par_diplome` | pipeline | +0,019 |

Les liens des trois agrégées sont mesurés sur le seul jeu d'apprentissage, après ajustement
du transformateur.

Deux variables portent un signal net. `ratio_poursuite` confirme directement l'hypothèse 1
de l'étape 2 : plus la part de diplômés qui poursuivent leurs études est élevée, plus le
taux d'emploi salarié baisse.

Les variables presque plates sont **conservées quand même** : une corrélation linéaire
faible n'exclut pas un apport en interaction dans un modèle d'arbres. L'étape 5c tranche
sur l'importance réelle des variables, et le résultat est instructif :
`nb_etablissements_par_diplome`, dont la corrélation vaut 0,02, arrive 4e des 18.

### Pourquoi les agrégats sont dans la pipeline

Les trois agrégées lisent d'autres lignes, dont des lignes qui finiront dans le jeu de
test. Calculées ici, sur le jeu complet, elles feraient entrer dans l'apprentissage une
information tirée du test, et créeraient un écart entre la valeur vue à l'entraînement et
celle calculée à l'inférence. Elles sont donc apprises par le transformateur
`AgregatsContexte`, première étape de la pipeline, sur les seules lignes d'entraînement de
chaque pli. Le même objet ajusté sert ensuite à l'inférence : une clé inconnue
(établissement ou diplôme jamais vu) retombe sur la médiane de la table.

`part_sortants_etablissement`, quatrième agrégat de la première version, est **retirée** :
son dénominateur, les sortants de l'établissement pour la promotion, n'est pas
reconstructible pour une formation nouvelle. Elle ne pesait que 14e sur 19.

### Redondances assumées

`anciennete_promotion` et `promotion_choc_sanitaire` se déduisent toutes deux de
`Promotion`, elle-même fournie comme variable catégorielle. Ce n'est pas un oubli :
l'encodage one-hot donne un effet libre par année, `anciennete_promotion` donne une
variable ordonnée sur laquelle un arbre peut couper une fois pour toutes, et
`promotion_choc_sanitaire` isole explicitement l'hypothèse testée. L'étape 5c montre que le
modèle utilise surtout la forme ordonnée.

### Découpage et contrôles anti-fuite

Le découpage est fait **avant** tout ce qui lit d'autres lignes que la sienne, et il est
**groupé par formation** (code UAI × code SISE), par `decouper()` dans
`modeles/protocole.py`.

| Sous-ensemble | Lignes | Part | Formations | Moyenne de la cible | Écart-type |
|---|---:|---:|---:|---:|---:|
| Apprentissage | 13 718 | 80,4 % | 3 958 | 55,90 | 18,53 |
| Test | 3 347 | 19,6 % | 990 | 55,83 | 18,22 |

**Aucune formation n'est présente des deux côtés**, ce qu'un `assert` vérifie.

Trois contrôles exécutables suivent, et rejouent les définitions réelles des variables :

1. **Indépendance à la cible.** La cible est permutée, puis les six variables ligne à ligne
   et les trois agrégats sont recalculés : aucun ne bouge.
2. **Isolement du transformateur, côté apprentissage.** Des lignes de test volontairement
   altérées (effectifs multipliés par 100, codes inconnus) ne changent rien aux agrégats
   calculés pour l'apprentissage.
3. **Isolement du transformateur, côté test.** Mélanger l'ordre des lignes de test ne
   change la valeur d'aucune : chaque ligne est décrite avec ce qui a été appris sur
   l'apprentissage, jamais avec les autres lignes de test.

Conséquence concrète du découpage groupé : `taille_mediane_secteur` est connue pour 100 %
des lignes de test, `nb_formations_etablissement` pour 96,7 %, mais
`nb_etablissements_par_diplome` pour 80,8 % seulement. Un diplôme propre à un seul
établissement n'a, par construction, jamais été vu à l'apprentissage. C'est exactement la
situation d'une formation nouvelle en usage réel.

---

## 3. Périmètre du modèle

**18 variables explicatives** : 8 catégorielles, 10 numériques, dont 6 créées à cette étape
et 3 apprises dans la pipeline. La pipeline reçoit 17 colonnes : les variables ligne à
ligne et les deux codes dont le transformateur d'agrégats a besoin. Aucune valeur
manquante.

### Variables exclues

| Colonnes | Motif | Détail |
|---|---|---|
| Taux d'emploi à 12, 18, 24 et 30 mois | Fuite de cible | Mesuré après les 6 mois à prédire (r = 0,85 à 12 mois) |
| Taux et nombre en emploi stable | Fuite de cible | Résultat d'insertion au même horizon que la cible |
| Taux et nombre en emploi non salarié | Fuite de cible | Résultat d'insertion au même horizon que la cible |
| `Établissement`, `Libellé du diplôme` | Cardinalité | 329 et 1 290 modalités : le modèle mémoriserait |
| `Code UAI`, `Code SISE` | Identifiant | Lus par le transformateur d'agrégats, jamais transmis au modèle |
| `part_sortants_etablissement` | Non reproductible | Dénominateur impossible à reconstituer pour une formation nouvelle |
| `promotion_debut` | Redondance | Supprimé au nettoyage |

---

## 4. Dictionnaire de données

Généré depuis le jeu final, donc impossible à désynchroniser des données réelles. Un
`assert` échoue si une colonne n'est pas décrite. 28 colonnes documentées avec type, rôle,
manquants, modalités, exemple et description, plus une section sur les trois variables
calculées dans la pipeline.

Fichier : [`DATA_DICTIONARY.md`](../DATA_DICTIONARY.md)

---

## 5. Export

Jeu final exporté : `csv/dataset_phase3_final.csv`, 17 065 × 28. Il ne contient aucun
agrégat, ce qu'un `assert` vérifie.

Six autres `assert` verrouillent le périmètre : cible absente des entrées, aucune variable
postérieure à 6 mois, aucun identifiant transmis au modèle, aucune valeur manquante, aucune
ligne perdue, aucun recouvrement de lignes ni de formations entre apprentissage et test.

### Ce qui n'est volontairement pas fait ici

Aucun encodage, aucune mise à l'échelle, aucune imputation, aucun agrégat. Ces opérations
apprennent quelque chose sur les données : les modalités présentes, la moyenne et
l'écart-type, la valeur de remplacement, les tailles typiques par groupe. Les appliquer
avant le découpage laisserait fuir dans l'apprentissage une information issue du test.
Elles sont toutes **à l'intérieur de la `Pipeline`**, réajustée sur les seules données
d'entraînement de chaque pli.

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

- [x] 9 variables créées, couvrant les 5 familles attendues
- [x] Chaque variable répond à une hypothèse formulée à l'étape 2
- [x] Force du lien avec la cible mesurée pour chacune
- [x] Agrégats appris dans la pipeline, sur l'apprentissage seul
- [x] Contrôle anti-fuite par permutation de la cible
- [x] Isolement du transformateur vérifié dans les deux sens
- [x] Dictionnaire de données généré depuis le jeu réel
- [x] Jeu final exporté
- [x] Découpage apprentissage / test unique, reproductible et groupé par formation

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Quelles features créer à partir d'effectifs de sortants et de poursuivants ? » | Ratio de poursuite, effectif total, tranches | Corrélation de chaque piste mesurée avant de la retenir ; le ratio ressort à −0,31, les tranches beaucoup moins |
| « Est-ce une fuite de données de calculer une moyenne par groupe avant le split ? » | Distinction entre agrégat de `X` et agrégat de `y` | Traduite en test exécutable : permutation de la cible, puis recalcul des agrégats sur le seul train |
| « Comment journaliser un nettoyage de façon traçable ? » | Structure de log JSON par action | Fonction `journaliser` écrite à la main pour forcer une justification à chaque appel |
| « Génère-moi un data dictionary » | Tableau Markdown statique rédigé à la main | Refusé : remplacé par une génération depuis le DataFrame, avec un `assert` qui échoue si une colonne n'est pas décrite |

Le point le plus utile a été le deuxième : la réponse initiale de l'IA affirmait que tout
agrégat calculé avant le découpage est une fuite. C'est faux tant que l'agrégat ne touche
pas la cible, et la nuance a été transformée en deux tests plutôt qu'en affirmation.

**Révision.** Cette nuance était incomplète, et la relecture de la formatrice l'a relevé :
un agrégat de `X` calculé sur le jeu complet ne fait pas fuir la cible, mais il fait entrer
dans l'apprentissage une information tirée des lignes de test, et il crée un écart entre
l'entraînement et l'inférence. La réponse initiale de l'IA était donc plus prudente que la
nuance retenue. Les agrégats sont désormais appris dans la pipeline, travail mené avec
Claude Code à partir des retours de la formatrice.
