# Étape 4 - Baseline et comparaison de modèles

## Objectif

Comparer des modèles à une référence naïve et retenir des candidats. Pas les mesurer :
l'évaluation finale appartient à l'étape 5c.

Notebook : [`etape_4_modelisation.ipynb`](../notebooks/etape_4_modelisation.ipynb)

**La règle du jeu de test.** Le jeu de test n'est jamais construit dans ce notebook : seuls
les index d'apprentissage du découpage de l'étape 3 sont repris. Toutes les comparaisons se
font par validation croisée sur le seul jeu d'apprentissage. Un jeu de test consulté pour
choisir un modèle cesse d'être un jeu de test.

> **Révision du protocole** (voir [étape 10](étape_10_revision.md)). La première version
> validait sur des plis aléatoires, ligne à ligne, avec des agrégats calculés sur le jeu
> complet. Les chiffres ci-dessous sont ceux du protocole corrigé ; la section 5 mesure ce
> que coûtait l'ancien.

---

## 1. Protocole

- Validation croisée : `GroupKFold(n_splits=5, shuffle=True, random_state=42)`, **groupée
  par formation** (code UAI × code SISE). Un modèle n'est jamais validé sur une promotion
  d'une formation dont il a vu les autres.
- Pipeline définie dans [`modeles/protocole.py`](../modeles/protocole.py) : agrégats de
  contexte (`AgregatsContexte`), puis `OneHotEncoder(handle_unknown='ignore')` dans un
  `ColumnTransformer`, `StandardScaler` sur les numériques pour les seuls modèles linéaires
- 18 variables, **149 colonnes après encodage**
- Métriques : MAE, RMSE et $R^2$, avec `return_train_score=True`

Tout ce qui apprend sur les données est dans la pipeline : agrégats, encodage et mise à
l'échelle sont réajustés sur les seules données d'entraînement de chaque pli.

---

## 2. Référence naïve

`DummyRegressor(strategy='mean')`, évalué **par la même validation croisée que les autres
modèles**, avec la moyenne apprise dans chaque pli.

| Métrique | Valeur |
|---|---:|
| MAE | 15,045 points de taux |
| RMSE | 18,527 points de taux |
| $R^2$ | −0,000 |

Sans rien apprendre, on se trompe en moyenne de 15 points de taux d'emploi. Tout modèle
doit faire mieux que cela pour justifier son existence.

---

## 3. Comparaison de six modèles

| Modèle | MAE | Écart-type MAE | RMSE | $R^2$ validation | $R^2$ entraînement | Écart | Temps |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Gradient boosting** | **10,017** | 0,162 | **13,013** | **0,506** | 0,662 | 0,156 | 0,42 s |
| Forêt aléatoire | 10,283 | 0,215 | 13,437 | 0,473 | 0,900 | 0,427 | 1,85 s |
| Ridge (alpha=1) | 10,616 | 0,163 | 13,755 | 0,448 | 0,478 | 0,030 | 0,04 s |
| Régression linéaire | 10,622 | 0,167 | 13,767 | 0,447 | 0,478 | 0,031 | 0,07 s |
| Arbre de décision | 14,253 | 0,404 | 18,476 | 0,004 | 1,000 | 0,996 | 0,15 s |
| Référence naïve | 15,045 | 0,210 | 18,527 | −0,000 | 0,000 | 0,000 | 0,03 s |

---

## 4. Diagnostic de surapprentissage

L'écart de $R^2$ ne parle pas : on le traduit en points de taux et en nombre de formations
ratées de plus de 15 points, seuil au-delà duquel un utilisateur ne suivrait plus la
prédiction.

| Modèle | MAE entraînement | MAE validation | Dégradation |
|---|---:|---:|---:|
| Arbre de décision | 0,002 | 14,253 | +14,250 pt |
| Forêt aléatoire | 4,341 | 10,283 | +5,942 pt |
| Gradient boosting | 8,321 | 10,017 | +1,697 pt |
| Ridge | 10,357 | 10,616 | +0,259 pt |
| Référence naïve | 15,044 | 15,045 | +0,001 pt |

Sur les 13 718 lignes du jeu d'apprentissage, en validation croisée groupée :

| Modèle | Erreur > 15 pts | Part | Erreur > 25 pts | Erreur médiane |
|---|---:|---:|---:|---:|
| Référence naïve | 6 021 | 43,9 % | 2 550 | 13,10 pt |
| Ridge | 3 388 | 24,7 % | 962 | 8,59 pt |
| Forêt aléatoire | 3 199 | 23,3 % | 880 | 8,19 pt |
| Gradient boosting | 3 050 | 22,2 % | 799 | 8,05 pt |

Le boosting rate **2 971 lignes de moins** que la référence naïve, soit 49 % de réduction.

---

## 5. Ce que coûtait la validation aléatoire

Même forêt, mêmes lignes d'apprentissage ; seuls les plis changent.

| Validation | MAE | Écart-type | $R^2$ |
|---|---:|---:|---:|
| Plis aléatoires (protocole initial) | 9,440 | 0,148 | 0,560 |
| **Plis groupés par formation** | **10,283** | 0,215 | **0,473** |

**La validation aléatoire était optimiste de 0,84 point de MAE**, environ quatre fois
l'écart-type entre plis. Ce n'était pas du bruit, mais de la mémoire : un pli aléatoire
contient des promotions de formations dont les autres promotions sont à l'entraînement, et
le modèle les reconnaît. Le protocole groupé mesure ce qui intéresse vraiment : l'erreur
sur une formation jamais vue.

---

## 6. Les variables créées servent-elles ?

Même modèle, mêmes plis, seul le périmètre de variables change.

| Périmètre | Variables | MAE | RMSE | $R^2$ |
|---|---:|---:|---:|---:|
| Variables brutes seules | 9 | 10,504 | 13,740 | 0,449 |
| Brutes + 9 variables créées | 18 | **10,283** | **13,437** | **0,473** |
| + 4 variables du référentiel | 22 | 10,269 | 13,422 | 0,475 |

**Apport des variables créées : +0,221 point de MAE et +0,024 de $R^2$.** Le feature
engineering de l'étape 3 est utile, au-delà de l'écart-type entre plis (0,215).

---

## 7. La seconde source apporte-t-elle quelque chose au modèle ?

Même protocole : modalité `non référencé` pour les catégorielles, imputation par la médiane
dans la pipeline pour l'effectif d'inscrits.

**Apport mesuré : +0,014 point de MAE et +0,002 de $R^2$.** La MAE varie de 0,21 point
d'un pli à l'autre : le gain est **quinze fois plus petit que le bruit** de la validation
croisée. Autrement dit, il n'y a pas de gain.

L'explication la plus plausible est la redondance. Le référentiel décrit l'établissement,
quand le modèle connaît déjà son académie, sa région et son nombre de formations. Le
clivage public / privé de l'étape 1 est réel, mais recoupe probablement la discipline et le
type de diplôme.

**Décision : les quatre variables ne sont pas retenues**, le modèle reste à 18 variables.
C'est un résultat négatif, reporté comme tel. La jointure garde son intérêt en analyse, où
l'écart de 4,5 points entre public et privé est un résultat en soi.

---

## 8. Décision

**Performance.** Les deux modèles d'ensemble se détachent : 10,02 de MAE pour le gradient
boosting, 10,28 pour la forêt, contre 10,62 pour les modèles linéaires et 15,05 pour la
référence naïve. L'écart avec les modèles linéaires indique que la relation n'est pas
additive : l'effet d'un secteur disciplinaire dépend du type de diplôme.

**Écart entre les deux modèles d'ensemble.** Le boosting devance la forêt de 0,27 point,
soit environ 1,3 fois l'écart-type entre plis de la forêt. L'avance est nette mais pas
écrasante, et les deux modèles sont réglés par défaut.

**Surapprentissage.** L'arbre seul est le contre-exemple utile : $R^2$ d'entraînement de
1,000 pour 0,004 en validation. Sur des formations inconnues, il ne fait presque pas mieux
que la référence naïve. La forêt garde un écart important (0,900 contre 0,473), le boosting
ne perd que 0,16. **Sur ce critère, le gradient boosting généralise mieux.**

**Décision : deux candidats, départagés après optimisation.** La forêt est optimisée à
l'étape 5, puis les deux s'affrontent à l'étape 5b, chacun avec sa grille. Le modèle livré
est le vainqueur de ce duel, choisi **avant** toute ouverture du jeu de test.

**Ce que cette étape ne dit pas.** Aucun chiffre ci-dessus n'est le score du modèle. Ce sont
des scores de validation, obtenus sur des données ayant servi à choisir.

Figure : `figures_eda/fig12_comparaison_modeles.png`

---

## Checklist

- [x] Baseline `DummyRegressor` calculée, dans les mêmes conditions que les modèles
- [x] Six modèles comparés, dont deux modèles simples
- [x] Validation croisée groupée à 5 plis, `shuffle=True`, `random_state` fixé
- [x] Tout le prétraitement, agrégats compris, dans une `Pipeline`
- [x] Mêmes variables, mêmes plis, mêmes métriques pour tous
- [x] Écart-type entre plis reporté
- [x] Surapprentissage diagnostiqué et traduit en nombre de formations
- [x] Optimisme de la validation aléatoire chiffré
- [x] Apport des variables créées mesuré explicitement
- [x] Apport de la seconde source mesuré, et le résultat négatif reporté
- [x] **Le jeu de test n'est pas construit**

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Comment comparer plusieurs modèles sklearn proprement ? » | `cross_validate` avec un dictionnaire de scoring | Ajout de `return_train_score=True`, absent de la proposition, sans lequel le surapprentissage est invisible |
| « Ma baseline doit-elle être calculée sur le test ou sur le train ? » | Sur le train, en validation croisée | Recodée avec `DummyRegressor` dans la même pipeline et les mêmes plis que les autres modèles |
| « Comment savoir si mes features servent ? » | Suggestion de regarder `feature_importances_` | Insuffisant : l'importance classe les variables mais ne dit pas si le modèle est meilleur. Remplacé par une comparaison avec et sans, à conditions identiques |
| « Explique-moi l'écart entre R² train et R² validation » | Explication générale du surapprentissage | Traduit en une mesure exploitable : nombre de formations ratées de plus de 15 points |

Le troisième échange est le plus instructif : la réponse de l'IA était correcte mais
répondait à une autre question. L'importance des variables dit *ce que le modèle utilise*,
pas *si le modèle est meilleur*.

**Révision.** Le passage aux plis groupés et la mesure de l'optimisme de l'ancien protocole
ont été menés avec Claude Code, à partir des retours de la formatrice.
