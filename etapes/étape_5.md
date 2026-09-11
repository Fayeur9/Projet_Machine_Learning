# Étape 5 - Optimisation, évaluation finale et interprétation

## Objectif

Optimiser la forêt aléatoire retenue à l'étape 4, l'évaluer **une seule fois** sur le jeu
de test resté fermé, interpréter ce qu'elle a appris, auditer ses biais, et livrer une
pipeline utilisable.

Notebook : [`Projet/notebooks/etape_5_optimisation_erreurs.ipynb`](../notebooks/etape_5_optimisation_erreurs.ipynb)

---

## 1. Recherche d'hyperparamètres

Grille de 16 configurations × 5 plis = 80 entraînements, sur le seul jeu d'apprentissage.
Critère de sélection : **RMSE**, qui pénalise les grosses erreurs, plus coûteuses
qu'une erreur deux fois plus petite sur un taux d'emploi.

| Hyperparamètre | Valeurs testées | Rôle |
|---|---|---|
| `n_estimators` | 200, 400 | Nombre d'arbres moyennés |
| `max_features` | `sqrt`, 0.5 | Variables candidates à chaque coupe |
| `min_samples_leaf` | 1, 2, 5, 10 | Levier direct contre le surapprentissage |

Meilleure configuration brute : `n_estimators=400`, `max_features=0.5`,
`min_samples_leaf=1`, RMSE **12,185 ± 0,182**.

### Choix final : la règle à un écart-type

La meilleure configuration n'est pas forcément celle qu'il faut retenir : son avance doit
d'abord dépasser le bruit de mesure. **6 configurations sur 16** sont à moins d'un
écart-type de la meilleure (seuil 12,367). Parmi elles, on garde la plus simple.

| Configuration retenue | Valeur |
|---|---|
| `n_estimators` | 200 |
| `max_features` | 0.5 |
| `min_samples_leaf` | 2 |
| RMSE validation | 12,281 |

**Coût du choix** : +0,096 point de RMSE, soit 0,53 écart-type, donc non significatif.
**Bénéfice** : écart entraînement / validation ramené de 0,377 à **0,332**, et fichier de
modèle divisé par plus de dix.

### Comparaison des trois configurations

| Configuration | MAE val. | RMSE val. | $R^2$ val. | $R^2$ entraînement | Écart |
|---|---:|---:|---:|---:|---:|
| Étape 4 (n=200, leaf=2, `max_features` défaut) | 9,495 | 12,365 | 0,550 | 0,899 | 0,349 |
| Meilleure de la grille | 9,365 | 12,185 | 0,563 | 0,940 | 0,377 |
| **Retenue (règle à un écart-type)** | 9,438 | 12,281 | 0,557 | 0,889 | **0,332** |

Figure : `figures_eda/fig13_grille_hyperparametres.png`

---

## 2. Évaluation finale sur le jeu de test

**Seule et unique ouverture du jeu de test du projet.**

| Métrique | Référence naïve | Forêt aléatoire retenue | Gain |
|---|---:|---:|---:|
| MAE | 15,069 | **9,579** | −5,490 |
| RMSE | 18,523 | **12,373** | −6,150 |
| $R^2$ | −0,000 | **0,554** | +0,554 |

Sur les 3 413 formations du jeu de test :

- erreur moyenne : **9,58 points** de taux d'emploi, contre 15,07 pour la référence, soit
  **36 % de réduction** ;
- **33 %** des formations sont prédites à moins de 5 points près, contre 20 % pour la
  référence ;
- **697** formations sont ratées de plus de 15 points, contre 1 509 pour la référence.

### Analyse des résidus

Résidu moyen **−0,014 point**, écart-type 12,37 points, pente de la droite
résidus / prédictions **+0,015**.

Le résidu moyen quasi nul confirme l'absence de biais global. Mais le nuage « prédit contre
observé » reste aplati par rapport à la diagonale : **le modèle sous-estime les taux très
élevés et surestime les taux très bas**. C'est le comportement attendu d'un modèle
d'ensemble, qui prédit une moyenne de feuilles, donc une valeur attirée vers le centre.

Conséquence à annoncer : le modèle est le moins fiable exactement sur les formations
extrêmes, celles qui insèrent très bien ou très mal, c'est-à-dire souvent celles qui
intéressent le plus.

Figure : `figures_eda/fig14_residus.png`

---

## 3. Interprétation : importance des variables

Deux mesures, parce qu'elles ne mesurent pas la même chose. L'importance par impureté
favorise les variables à nombreuses valeurs distinctes ; l'importance par permutation
mesure la dégradation réelle du score. La permutation est calculée **après** que le score
final a été reporté : aucune décision n'en découle.

| Variable | Permutation (RMSE) | Impureté |
|---|---:|---:|
| `est_diplome_professionnalisant` | **3,028** | 0,124 |
| `ratio_poursuite` | **1,571** | 0,121 |
| `nb_etablissements_par_diplome` | **1,221** | 0,070 |
| Domaine disciplinaire | 0,811 | 0,046 |
| Type de diplôme | 0,792 | 0,063 |
| `anciennete_promotion` | 0,772 | 0,051 |
| Académie | 0,465 | 0,063 |
| Nombre de poursuivants | 0,407 | 0,059 |
| Secteur disciplinaire | 0,351 | 0,054 |
| `nb_formations_etablissement` | 0,346 | 0,047 |
| ... | ... | ... |
| `promotion_choc_sanitaire` | 0,010 | 0,010 |
| `tranche_effectif` | 0,008 | 0,011 |

**Les trois premières places du classement par permutation sont occupées par des variables
créées à l'étape 3**, et cinq des dix figurent dans la moitié haute.

Figure : `figures_eda/fig15_importance_variables.png`

### Confrontation avec les hypothèses de l'EDA

| Hypothèse de l'étape 2 | Verdict |
|---|---|
| 1. Le ratio de poursuite est le prédicteur numérique le plus prometteur | **Confirmée** : 2e des deux classements |
| 2. Le secteur disciplinaire doit primer sur le domaine | **Infirmée** |
| 3. La promotion apporte un effet de niveau, pas une tendance | **Nuancée** |
| 4. L'erreur sera plus forte sur les petits effectifs | **Confirmée nettement** |
| 5. Un $R^2$ autour de 0,5 est un plafond réaliste | **Confirmée** : 0,554 |

**Hypothèse 2, infirmée.** L'EDA avait mesuré un eta² de 0,194 pour le secteur contre
0,083 pour le domaine et en avait conclu qu'il fallait le niveau fin. La permutation dit
l'inverse : domaine 0,811, secteur 0,351. L'explication n'est pas que l'EDA avait tort,
mais que les deux variables sont **redondantes** : mélanger l'une laisse l'autre
disponible, et le modèle compense. L'importance par permutation sous-estime donc
systématiquement les variables redondantes, et le modèle a préféré couper sur les 4
modalités du domaine, plus robustes, que sur les 49 du secteur.

**Hypothèse 3, nuancée.** `anciennete_promotion` obtient 0,772 contre 0,027 pour
`Promotion`, alors que les deux portent la même information. Le modèle a choisi la forme
**ordonnée** : une coupe sur un axe continu vaut mieux que six indicatrices. C'est la
justification a posteriori de la redondance volontaire introduite à l'étape 3.

### La corrélation linéaire ne dit pas tout

`nb_etablissements_par_diplome` avait une corrélation de Pearson de **0,02** avec la cible.
Elle arrive **3e** en importance par permutation. Cette variable sépare les diplômes
nationaux très répandus des diplômes propres à un établissement, et cette distinction
n'agit pas de façon monotone. Une corrélation de Pearson ne mesure qu'un lien linéaire ;
une forêt exploite des seuils et des interactions.

**Écarter cette variable sur sa seule corrélation aurait été une erreur.** À l'inverse,
`tranche_effectif` et `promotion_choc_sanitaire` ferment les deux classements : le
découpage en tranches n'apporte rien que `taille_formation` ne porte déjà, et l'indicateur
2020 fait doublon avec l'encodage de `Promotion`.

---

## 4. Analyse des erreurs par groupe

### Par promotion

| Promotion | Formations test | MAE | Biais moyen |
|---|---:|---:|---:|
| 2020 | 544 | **10,44** | −0,89 |
| 2019 | 529 | 9,99 | −0,11 |
| 2023 | 553 | 9,61 | −0,01 |
| 2024 | 607 | 9,53 | −0,18 |

La promotion 2020 reste la plus difficile, avec en plus un biais négatif : le modèle la
surestime, faute de pouvoir représenter le choc conjoncturel.

### Par taille de formation : l'hypothèse 4 confirmée

| Tranche d'effectif | Formations test | MAE | Biais moyen |
|---|---:|---:|---:|
| très petite (≤ 25) | 818 | **12,09** | +0,07 |
| petite (26-45) | 1 306 | 9,61 | +0,21 |
| moyenne (46-90) | 852 | 8,32 | −0,23 |
| grande (> 90) | 437 | **6,33** | −0,26 |

**Rapport de près de deux entre les extrêmes.** Sur une formation de moins de 25 sortants,
la prédiction est nettement moins fiable que la moyenne annoncée. C'est mécanique : sur
20 diplômés, un seul individu vaut 5 points de taux.

### Par type de diplôme

MAE la plus élevée sur Master LMD (9,96) et licence professionnelle (9,86) ; la plus basse
sur Master MEEF (5,45, mais sur 89 formations seulement) et BUT (6,92, sur 44 formations).
Les petits groupes sont à interpréter avec prudence.

Figure : `figures_eda/fig16_erreurs_par_groupe.png`

---

## 5. Audit de fuite et robustesse temporelle

### Recouvrement du découpage aléatoire

Une même formation apparaît jusqu'à six fois dans le jeu, une fois par promotion. Le
découpage au hasard place donc certaines de ses promotions dans l'entraînement et d'autres
dans le test.

- 4 638 formations distinctes en apprentissage ;
- **3 073 lignes de test sur 3 413 (90,0 %)** portent sur une formation déjà vue ;
- MAE sur les formations déjà vues : **9,39** points ;
- MAE sur les formations inconnues : **11,28** points ;
- **surcoût pour une formation inconnue : +1,89 point.**

Ce n'est **pas une fuite de cible** : la valeur à prédire du test n'a jamais servi à
ajuster le modèle. C'est un **biais de validation** : le score aléatoire mesure surtout la
capacité à prédire une nouvelle promotion d'une formation déjà connue.

### Validation temporelle

| Scénario | MAE | RMSE | $R^2$ |
|---|---:|---:|---:|
| Découpage aléatoire (test 2019-2024) | 9,579 | 12,373 | 0,554 |
| **Découpage temporel** (train 2019-2022, test 2023-2024) | 9,853 | 12,922 | **0,458** |
| Référence naïve sur le découpage temporel | 14,008 | 17,569 | −0,002 |

**Les deux scores mesurent deux choses différentes et doivent être présentés ensemble.**

Le score aléatoire répond à « connaissant le paysage 2019-2024, sais-je estimer une
formation dont je n'ai pas la mesure ? ». Le score temporel répond à « connaissant le
passé, sais-je prévoir l'avenir ? ». Le second est plus faible, et c'est normal : le modèle
n'a aucun moyen de connaître la conjoncture des années à prédire, alors que l'EDA a montré
que le niveau d'insertion bouge de plus de 13 points d'une promotion à l'autre.

**C'est le score temporel qu'il faut annoncer** si le modèle est présenté comme un outil de
prévision. Le score aléatoire vaut pour de l'imputation.

---

## 6. Limites et biais

**Ce que le modèle prédit.** Un taux agrégé de formation, jamais l'employabilité d'un
individu.

**Erreur moyenne.** Environ 9,5 points. Sur une formation annoncée à 60 %, la réalité se
situe le plus souvent entre 50 % et 70 %. Utilisable pour comparer des familles de
formations, pas pour classer deux formations proches.

**Erreur très inégale.** Rapport de près de deux entre petites et grandes formations, et
prédiction ramenée vers la moyenne sur les taux extrêmes.

**Biais de sélection.** Le seuil de publication de 20 sortants exclut structurellement les
petites formations. Le modèle n'a jamais vu de formation de 10 diplômés.

**Biais de représentation.** Régions et disciplines inégalement représentées ; les régions à
faible effectif de formations sont mécaniquement moins bien apprises.

**Ce que le modèle ne peut pas dire.** `Genre`, `Nationalité` et `Régime d'inscription` ne
sont pas dans le jeu de modélisation. Le modèle ne peut **ni** produire **ni** écarter une
conclusion sur des disparités de genre ou de nationalité. La question 3 de l'EDA a montré
qu'une comparaison naïve sur ces variables donne un résultat de signe opposé à une
comparaison à formation égale : toute analyse d'équité demanderait de reconstruire le jeu
au niveau démographique.

**Risque d'usage.** Appliqué à une décision d'orientation ou d'allocation de moyens, ce
modèle reproduirait les écarts existants entre disciplines et territoires en leur donnant
l'apparence d'une prédiction objective. Son usage raisonnable est descriptif, pas
prescriptif.

---

## 7. Livraison

`modeles/modele_final_random_forest.joblib`, **29,6 Mo** (compressé), contenant :

- la **pipeline complète** : encodage + forêt ;
- le **référentiel** des agrégats, construit sur le seul jeu d'apprentissage ;
- la liste des variables, le nom de la cible et les métriques de test.

Une fonction `preparer_ligne_brute()` transforme une ligne au format de la source en entrée
du modèle, en reconstruisant les dix variables créées à l'étape 3. Sans elle, le fichier
serait inutilisable : dix des dix-neuf variables sont calculées en amont.

### Démonstration

Ligne brute soumise : licence professionnelle en Informatique, académie de Rennes,
promotion 2024, 48 sortants, 6 poursuivants, avec un **code SISE volontairement inconnu**
du référentiel pour tester le repli.

**Prédiction : 68,4 %**, intervalle indicatif à ± la MAE de test : 58,8 % à 78,0 %.

Contrôle de non-régression : le modèle rechargé reproduit les prédictions **à l'identique**
sur les 3 413 lignes de test.

---

## Checklist

**Rigueur méthodologique**

- [x] `train_test_split` avant tout prétraitement, `random_state` fixé partout
- [x] Tout le prétraitement dans un `ColumnTransformer` / `Pipeline`
- [x] Aucune colonne fuitante dans `X`
- [x] **Jeu de test ouvert une seule fois**
- [x] Recherche d'hyperparamètres sur le seul jeu d'apprentissage
- [x] Choix final par la règle à un écart-type, pas sur le seul meilleur score

**Évaluation**

- [x] Métrique principale justifiée
- [x] MAE et RMSE dans l'unité de la cible, $R^2$ reporté
- [x] Résidus analysés graphiquement et commentés
- [x] Écart entraînement / validation traduit en nombre de formations
- [x] Gain sur la baseline chiffré sur le même jeu de test

**Interprétation et limites**

- [x] Importance des variables par deux méthodes
- [x] Résultats confrontés aux hypothèses de l'EDA, y compris les deux infirmées
- [x] Cas d'échec identifiés : formations inconnues, taux extrêmes, petits effectifs, prévision temporelle
- [x] Biais de sélection, de représentation et risque d'usage discutés

**Documentation et reproductibilité**

- [x] Pipeline sauvegardée en `.joblib` avec son référentiel
- [x] Rechargement vérifié par un contrôle de non-régression
- [x] Démonstration de prédiction sur une donnée brute, modalité inconnue comprise
