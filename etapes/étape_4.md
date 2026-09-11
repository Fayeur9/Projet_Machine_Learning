# Étape 4 - Baseline et comparaison de modèles

## Objectif

Choisir un modèle. Pas le mesurer : l'évaluation finale appartient à l'étape 5.

Notebook : [`Projet/notebooks/etape_4_modelisation.ipynb`](../notebooks/etape_4_modelisation.ipynb)

**La règle du jeu de test.** Le jeu de test est mis de côté dès la première cellule, puis
retiré de la mémoire (`del X_test, y_test`). Toutes les comparaisons se font par validation
croisée à cinq plis sur le seul jeu d'apprentissage. Un jeu de test consulté pour choisir un
modèle cesse d'être un jeu de test : il devient un second jeu de validation, et le score
qu'il produit est optimiste.

---

## 1. Protocole

- Validation croisée : `KFold(n_splits=5, shuffle=True, random_state=42)`
- Prétraitement : `OneHotEncoder(handle_unknown='ignore')` dans un `ColumnTransformer`,
  `StandardScaler` sur les numériques pour les seuls modèles linéaires
- 19 variables en entrée, **150 colonnes après encodage**
- Métriques : MAE, RMSE et $R^2$, avec `return_train_score=True`

Tout le prétraitement est dans la pipeline : encodage et mise à l'échelle sont réajustés sur
les seules données d'entraînement de chaque pli.

---

## 2. Référence naïve

`DummyRegressor(strategy='mean')`, évalué **par la même validation croisée que les autres
modèles**, avec la moyenne apprise dans chaque pli.

| Métrique | Valeur |
|---|---:|
| MAE | 14,971 points de taux |
| RMSE | 18,455 points de taux |
| $R^2$ | −0,001 |

Sans rien apprendre, on se trompe en moyenne de 15 points de taux d'emploi. Tout modèle
doit faire mieux que cela pour justifier son existence.

---

## 3. Comparaison de six modèles

| Modèle | MAE | Écart-type MAE | RMSE | $R^2$ validation | $R^2$ entraînement | Écart | Temps |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Forêt aléatoire** | **9,495** | 0,147 | **12,365** | **0,550** | 0,899 | 0,349 | 1,84 s |
| Gradient boosting | 9,518 | 0,124 | 12,362 | 0,551 | 0,653 | **0,102** | 0,38 s |
| Ridge (alpha=1) | 10,411 | 0,168 | 13,451 | 0,468 | 0,479 | 0,011 | 0,04 s |
| Régression linéaire | 10,414 | 0,170 | 13,458 | 0,468 | 0,480 | 0,012 | 0,11 s |
| Arbre de décision | 13,168 | 0,100 | 17,321 | 0,118 | 1,000 | 0,882 | 0,16 s |
| Référence naïve | 14,971 | 0,159 | 18,455 | −0,001 | 0,000 | 0,001 | 0,02 s |

---

## 4. Diagnostic de surapprentissage

L'écart de $R^2$ ne parle pas : on le traduit en points de taux et en nombre de formations
ratées de plus de 15 points, seuil au-delà duquel un utilisateur ne suivrait plus la
prédiction.

| Modèle | MAE entraînement | MAE validation | Dégradation |
|---|---:|---:|---:|
| Arbre de décision | 0,006 | 13,168 | +13,162 pt |
| Forêt aléatoire | 4,334 | 9,495 | +5,161 pt |
| Gradient boosting | 8,390 | 9,518 | +1,128 pt |
| Ridge | 10,315 | 10,411 | +0,096 pt |
| Référence naïve | 14,970 | 14,971 | +0,002 pt |

Sur les 13 652 formations du jeu d'apprentissage, en validation croisée :

| Modèle | Erreur > 15 pts | Part | Erreur > 25 pts | Erreur médiane |
|---|---:|---:|---:|---:|
| Référence naïve | 5 940 | 43,5 % | 2 551 | 13,01 pt |
| Ridge | 3 318 | 24,3 % | 905 | 8,39 pt |
| Forêt aléatoire | 2 853 | 20,9 % | 656 | 7,55 pt |
| Gradient boosting | 2 771 | 20,3 % | 667 | 7,58 pt |

La forêt rate **3 087 formations de moins** que la référence naïve, soit 52 % de réduction.

---

## 5. Les variables créées servent-elles ?

Même modèle, mêmes plis, seul le périmètre de variables change.

| Périmètre | Variables | MAE | RMSE | $R^2$ |
|---|---:|---:|---:|---:|
| Variables brutes seules | 9 | 9,983 | 13,049 | 0,499 |
| Brutes + 10 variables créées | 19 | **9,495** | **12,365** | **0,550** |
| + 4 variables du référentiel | 23 | 9,475 | 12,331 | 0,553 |

**Apport des variables créées : +0,488 point de MAE et +0,051 de $R^2$.** Le feature
engineering de l'étape 3 est donc utile, et l'écart dépasse largement l'écart-type entre
plis (0,147).

---

## 6. La seconde source apporte-t-elle quelque chose au modèle ?

L'étape 1 avait chargé le référentiel des établissements sans le verser dans le modèle,
faute d'une décision sur les 20 % de lignes non appariées. La question est tranchée ici,
avec le même protocole que ci-dessus : modalité `non référencé` pour les catégorielles,
imputation par la médiane dans la pipeline pour l'effectif d'inscrits.

**Apport mesuré : +0,020 point de MAE et +0,003 de $R^2$.** La MAE varie de 0,125 point
d'un pli à l'autre : le gain est **six fois plus petit que le bruit** de la validation
croisée. Autrement dit, il n'y a pas de gain.

L'explication la plus plausible est la redondance. Le référentiel décrit l'établissement,
quand le modèle connaît déjà son académie, sa région et son nombre de formations. Le
clivage public / privé de l'étape 1 est réel, mais recoupe probablement la discipline et le
type de diplôme : une école de commerce privée et une université ne délivrent pas les mêmes
diplômes.

**Décision : les quatre variables ne sont pas retenues**, le modèle final reste à 19
variables. C'est un résultat négatif, reporté comme tel : ajouter une source n'améliore pas
mécaniquement un modèle. Les 23 variables auraient donné un tableau plus fourni et un
modèle strictement équivalent. La jointure garde son intérêt en analyse, où l'écart de
4,5 points entre public et privé est un résultat en soi.

---

## 7. Décision

**Performance.** Les deux modèles d'ensemble se détachent : 9,50 de MAE contre 10,41 pour
les modèles linéaires et 14,97 pour la référence naïve. L'écart indique que la relation
n'est pas additive : l'effet d'un secteur disciplinaire dépend du type de diplôme, et une
régression linéaire ne peut pas représenter cela. Ridge et régression linéaire donnent le
même score : avec 13 652 lignes pour 150 colonnes, il n'y a pas d'instabilité à pénaliser.

**Stabilité.** Forêt aléatoire et gradient boosting sont **à égalité** : 9,495 contre 9,518,
pour un écart-type entre plis de 0,15. L'écart de 0,02 point est vingt fois plus petit que
la variabilité entre plis : il ne signifie rien. Le choix ne peut donc pas se faire sur le
score.

**Surapprentissage.** L'arbre seul est le contre-exemple utile : $R^2$ d'entraînement de
1,000 pour 0,118 en validation, et une MAE d'entraînement de 0,006 point. Il a appris ses
données par cœur. La forêt corrige largement ce défaut mais conserve un écart notable
(0,899 contre 0,550), là où le gradient boosting ne perd que 0,10. **Sur ce critère, le
gradient boosting généralise mieux.**

**Modèle retenu : la forêt aléatoire.** Le score ne départage pas les deux modèles
d'ensemble ; la décision se prend sur la lisibilité de l'importance des variables, exploitée
à l'étape 5 pour relier le modèle aux constats de l'EDA, et sur le nombre réduit
d'hyperparamètres critiques.

Il faut assumer ce que cela coûte : le gradient boosting est cinq fois plus rapide et
surapprend nettement moins. Il reste l'alternative à citer en soutenance, et l'écart
d'entraînement de la forêt est précisément ce que la recherche d'hyperparamètres de
l'étape 5 tente de réduire via `min_samples_leaf`.

**Ce que cette étape ne dit pas.** Aucun chiffre ci-dessus n'est le score du modèle. Ce sont
des scores de validation, obtenus sur des données ayant servi à choisir.

Figure : `figures_eda/fig12_comparaison_modeles.png`

---

## Checklist

- [x] Baseline `DummyRegressor` calculée, dans les mêmes conditions que les modèles
- [x] Six modèles comparés, dont deux modèles simples
- [x] Validation croisée à 5 plis, `shuffle=True`, `random_state` fixé
- [x] Tout le prétraitement dans un `ColumnTransformer` / `Pipeline`
- [x] Mêmes variables, mêmes plis, mêmes métriques pour tous
- [x] Écart-type entre plis reporté
- [x] Surapprentissage diagnostiqué et traduit en nombre de formations
- [x] Apport des variables créées mesuré explicitement
- [x] Apport de la seconde source mesuré, et le résultat négatif reporté
- [x] Choix argumenté, et coût du choix assumé
- [x] **Le jeu de test n'a pas été ouvert**
