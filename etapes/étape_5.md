# Étape 5 - Optimisation de la forêt aléatoire

## Objectif

Régler les hyperparamètres de la forêt aléatoire, l'un des deux candidats de l'étape 4, par
validation croisée groupée sur le seul jeu d'apprentissage : quels hyperparamètres
comptent, quelle configuration retenir, et ce que l'optimisation change.

Notebook : [`etape_5_optimisation_erreurs.ipynb`](../notebooks/etape_5_optimisation_erreurs.ipynb)

Le jeu de test n'est pas construit dans cette étape.

> **Révision du protocole** (voir [étape 10](étape_10_revision.md)). La première version de
> cette étape évaluait aussi le modèle sur le test, puis réutilisait ce même test pour
> l'importance des variables et l'analyse des erreurs. Le choix du modèle se fait désormais
> à l'étape 5b, entre la forêt et le boosting optimisés ; le diagnostic du modèle retenu et
> l'unique ouverture du test ont lieu à l'étape 5c.

---

## 1. Recherche d'hyperparamètres

Grille de 16 configurations × 5 plis groupés = 80 entraînements. Critère de sélection :
**RMSE**, qui pénalise les grosses erreurs, plus coûteuses qu'une erreur deux fois plus
petite sur un taux d'emploi.

| Hyperparamètre | Valeurs testées | Rôle |
|---|---|---|
| `n_estimators` | 200, 400 | Nombre d'arbres moyennés |
| `max_features` | `sqrt`, 0.5 | Variables candidates à chaque coupe |
| `min_samples_leaf` | 1, 2, 5, 10 | Levier direct contre le surapprentissage |

Meilleure configuration brute : `n_estimators=400`, `max_features='sqrt'`,
`min_samples_leaf=2`, RMSE **13,169 ± 0,304**.

**`min_samples_leaf` reste le levier du surapprentissage.** De 1 à 10, l'écart de R² entre
entraînement et validation passe de 0,46 à 0,18 avec `max_features=0.5`, alors que la RMSE
ne bouge que de quelques centièmes.

Figure : `figures_eda/fig13_grille_hyperparametres.png`

### Choix final : la règle à un écart-type

La meilleure configuration n'est pas forcément celle qu'il faut retenir : son avance doit
d'abord dépasser le bruit de mesure. **14 configurations sur 16** sont à moins d'un
écart-type de la meilleure (seuil 13,473). Parmi elles, on garde la plus simple.

| Configuration retenue | Valeur |
|---|---|
| `n_estimators` | 200 |
| `max_features` | 0.5 |
| `min_samples_leaf` | 10 |
| RMSE validation | 13,360 |

**Coût du choix** : +0,191 point de RMSE, soit 0,63 écart-type, donc non significatif.
**Bénéfice** : écart entraînement / validation ramené de 0,289 à **0,180**.

---

## 2. Ce que l'optimisation a changé

| Configuration | MAE val. | RMSE val. | $R^2$ val. | $R^2$ entraînement | Écart |
|---|---:|---:|---:|---:|---:|
| Étape 4 (n=200, leaf=2, `max_features` par défaut) | 10,283 | 13,437 | 0,473 | 0,900 | 0,427 |
| Meilleure de la grille | 10,148 | 13,169 | 0,494 | 0,783 | 0,289 |
| **Retenue (règle à un écart-type)** | 10,271 | 13,360 | 0,480 | 0,660 | **0,180** |

**L'optimisation réduit le surapprentissage, pas l'erreur.** La MAE ne bouge presque pas
par rapport à l'étape 4 (10,271 contre 10,283), mais l'écart de R² entre entraînement et
validation est divisé par plus de deux.

**La forêt semble proche de son plafond.** Aucun réglage ne la fait passer sous 10,1 de
MAE, alors que le boosting non optimisé faisait déjà 10,02 à l'étape 4. Le duel de
l'étape 5b dit si cet écart résiste à l'optimisation des deux modèles : il y résiste.

---

## Checklist

- [x] Recherche d'hyperparamètres en validation croisée groupée, sur le seul apprentissage
- [x] `cv_results_` mis à plat et commenté
- [x] Choix par la règle à un écart-type, pas sur le seul meilleur score, coût chiffré
- [x] Effet de l'optimisation mesuré contre la configuration de départ
- [x] Jeu de test non construit

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Quelle grille d'hyperparamètres pour un RandomForestRegressor ? » | Grille large sur cinq paramètres | Réduite à trois paramètres et seize configurations, en ciblant `min_samples_leaf`, seul levier contre le surapprentissage mesuré à l'étape 4 |
| « Pourquoi mon modèle sous-estime-t-il les valeurs hautes ? » | Explication de la régression vers la moyenne des modèles d'ensemble | Vérifiée sur le graphique des résidus et quantifiée par la pente de la droite résidus / prédictions |
| « `feature_importances_` est-elle fiable ? » | Mise en garde sur le biais en faveur des variables à forte cardinalité | Traduite en action : ajout de l'importance par permutation et comparaison des deux classements |
| « Comment livrer un modèle utilisable par quelqu'un d'autre ? » | `joblib.dump` de la pipeline | Insuffisant : dix variables sont calculées en amont. Ajout du référentiel et d'une fonction de préparation, testés sur une modalité volontairement inconnue |

Le dernier point est celui qui a le plus changé le livrable. Sauvegarder la pipeline
seule aurait donné un fichier qu'aucun utilisateur n'aurait su alimenter.

**Révision.** Les échanges sur les résidus, l'importance des variables et la livraison
portent désormais sur l'étape 5c, où ces analyses ont été déplacées. Le référentiel séparé
a disparu : les agrégats sont appris dans la pipeline, qui suffit à elle seule.
