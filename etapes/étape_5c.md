# Étape 5c - Diagnostic du modèle retenu et évaluation finale

## Objectif

Diagnostiquer le modèle choisi à l'étape 5b, l'évaluer **une seule fois** sur le jeu de
test, puis livrer une pipeline utilisable.

Notebook : [`etape_5c_evaluation_finale.ipynb`](../notebooks/etape_5c_evaluation_finale.ipynb)

**La règle du jeu de test.** Tout ce qui sert à comprendre le modèle (résidus, importances,
erreurs par groupe, robustesse temporelle) est calculé **avant** l'ouverture du test, en
validation croisée groupée, sur des prédictions hors pli. Le test n'est construit que dans
la cellule de la section 6, qui ne fait que mesurer. Le contrôle de rechargement porte sur
des lignes d'apprentissage. L'étape 7 vérifie cette règle en lisant le code des notebooks.

Modèle : **gradient boosting** (`HistGradientBoostingRegressor`), 400 itérations, pas
d'apprentissage 0,03, arbres de 15 feuilles au plus, feuilles d'au moins 20 formations.
Choisi à l'étape 5b, enregistré dans `modeles/choix_modele.json`.

---

## 1. Diagnostic en validation croisée

Une seule boucle sur les cinq plis groupés produit, pour chaque ligne d'apprentissage, une
prédiction par un modèle qui n'a vu aucune promotion de sa formation, et une importance par
permutation mesurée sur le pli tenu à l'écart.

| Métrique hors pli | Valeur |
|---|---:|
| MAE | 10,084 |
| RMSE | 13,097 |
| $R^2$ | 0,500 |

### Résidus

Résidu moyen **+0,13 point**, écart-type 13,10. Pas de biais global, mais une prédiction
**ramenée vers la moyenne** :

| Formations | Résidu moyen |
|---|---:|
| Taux observé ≥ 85 % | **+15,0 points** (sous-estimées) |
| Taux observé ≤ 25 % | **−23,2 points** (surestimées) |

Le modèle est le moins fiable exactement sur les formations extrêmes, souvent celles qui
intéressent le plus.

Figure : `figures_eda/fig14_residus.png`

### Importance des variables

Importance par permutation sur les 18 variables du modèle, agrégats compris, moyennée sur
les cinq plis groupés.

| Rang | Variable | RMSE perdue (points) |
|---:|---|---:|
| 1 | `est_diplome_professionnalisant` | **3,93** |
| 2 | `ratio_poursuite` | 1,32 |
| 3 | `anciennete_promotion` | 0,95 |
| 4 | `nb_etablissements_par_diplome` | 0,86 |
| 5 | Domaine disciplinaire | 0,76 |
| 6 | Secteur disciplinaire | 0,49 |
| ... | ... | ... |
| 17 | `tranche_effectif` | 0,001 |
| 18 | `promotion_choc_sanitaire` | 0,000 |

**Les quatre premières places sont tenues par des variables créées à l'étape 3.**

Figure : `figures_eda/fig15_importance_variables.png`

### Confrontation avec les hypothèses de l'EDA

| Hypothèse de l'étape 2 | Verdict |
|---|---|
| 1. Le ratio de poursuite est le prédicteur numérique le plus prometteur | **Confirmée** : 2e variable du modèle |
| 2. Le secteur disciplinaire doit primer sur le domaine | **Infirmée** : domaine 0,76, secteur 0,49 |
| 3. La promotion apporte un effet de niveau, pas une tendance | **Nuancée** : la forme ordonnée sert (0,95), l'encodage par année beaucoup moins (0,39) |
| 4. L'erreur sera plus forte sur les petits effectifs | **Confirmée** : 11,8 contre 7,5 |
| 5. Un $R^2$ autour de 0,5 est un plafond réaliste | **Confirmée** : 0,50 en validation, 0,48 sur le test |

**Hypothèse 2, infirmée.** Le domaine est l'agrégat du secteur : les deux variables sont
redondantes, et mélanger l'une laisse l'autre disponible. Le modèle préfère couper sur les
4 modalités du domaine plutôt que sur les 49 du secteur.

**La corrélation linéaire ne dit pas tout.** `nb_etablissements_par_diplome` corrèle à 0,02
avec la cible, mais arrive 4e : elle sépare les diplômes nationaux répandus des diplômes
propres à un établissement, une distinction non monotone. L'écarter sur sa corrélation
aurait été une erreur.

### Erreurs par groupe

| Tranche d'effectif | Formations | MAE |
|---|---:|---:|
| très petite (≤ 25) | 3 259 | **11,75** |
| petite (26-45) | 5 149 | 10,55 |
| moyenne (46-90) | 3 475 | 9,21 |
| grande (> 90) | 1 835 | **7,47** |

Rapport de 1,6 entre les extrêmes : sur 20 diplômés, un seul individu vaut 5 points de taux.
La promotion 2020 est la plus difficile (10,75). Les diplômes visés des écoles privées sont
les plus mal prédits (14 à 16 points), sur de petits groupes ; le master MEEF est le mieux
prédit (6,7).

Figure : `figures_eda/fig16_erreurs_par_groupe.png`

### Robustesse temporelle

Sur le seul apprentissage : entraînement sur 2019-2022, évaluation sur 2023-2024.

| Scénario | MAE | $R^2$ |
|---|---:|---:|
| Validation groupée (hors pli) | 10,084 | 0,500 |
| **Temporel : 2019-2022 → 2023-2024** | 10,005 | **0,448** |
| Référence naïve, même découpage | 14,049 | −0,001 |

Prévoir l'avenir coûte surtout en $R^2$. Le modèle bat toujours largement la référence.

---

## 2. Évaluation finale : l'unique ouverture du jeu de test

**990 formations, 3 347 lignes, dont aucune promotion n'a été vue à l'entraînement.**

| Métrique | Référence naïve | Gradient boosting | Gain |
|---|---:|---:|---:|
| MAE | 14,765 | **10,090** | −4,675 |
| RMSE | 18,215 | **13,081** | −5,134 |
| $R^2$ | −0,000 | **0,484** | +0,484 |

- **32 % d'erreur en moins** que la référence naïve ;
- **33 %** des lignes prédites à moins de 5 points près, contre 21 % ;
- **779** lignes ratées de plus de 15 points, contre 1 445.

**Le score de test confirme la validation à 0,006 point près** (10,090 contre 10,084) : avec
des plis groupés, la validation n'est plus optimiste. Le score est plus faible que celui de
la première version du projet (9,58), et c'est le bon : l'ancien mesurait surtout la
capacité à reconnaître des formations déjà vues. Voir l'[étape 10](étape_10_revision.md).

---

## 3. Limites et biais

- **Ce que le modèle prédit** : un taux agrégé de formation, jamais l'employabilité d'un
  individu.
- **Erreur moyenne** : environ 10 points sur une formation inconnue. Utilisable pour situer
  une formation face à ses comparables, pas pour classer deux formations proches.
- **Erreur inégale** : rapport de 1,6 entre petites et grandes formations, et taux extrêmes
  ramenés vers la moyenne.
- **Variables contemporaines** : sortants et poursuivants viennent de la même enquête que la
  cible ; le modèle prédit au moment de l'enquête, pas avant la sortie de la promotion.
- **Biais de sélection** : aucun taux publié sous 20 sortants.
- **Biais de représentation** : diplômes visés des écoles privées mal prédits.
- **Angle mort** : genre, nationalité et régime d'inscription absents du modèle.
- **Risque d'usage** : appliqué à des décisions d'orientation ou de moyens, le modèle
  reproduirait les écarts existants. Son usage raisonnable est descriptif.

---

## 4. Livraison

`modeles/modele_final.joblib`, **0,26 Mo**, contenant :

- la **pipeline complète** : agrégats de contexte, encodage, gradient boosting. Les tables
  d'agrégats apprises sur l'apprentissage voyagent dans la pipeline : il n'y a plus de
  référentiel séparé ;
- les colonnes d'entrée, la cible, les métriques de test et de validation, les importances
  et les relevés du diagnostic, que lit la fiche modèle.

**Contrôles :**

- le modèle rechargé reproduit les prédictions sur 500 lignes d'apprentissage ;
- `predire` (module `modeles/inference.py`) donne exactement `pipeline.predict` sur 200
  lignes brutes : plus d'écart entre entraînement et inférence.

**Démonstration** : licence professionnelle en Informatique, académie de Rennes, promotion
2024, 48 sortants, 6 poursuivants, établissement et diplôme inconnus de l'apprentissage.
**Prédiction : 63,3 %**, intervalle indicatif de 53,2 % à 73,4 %. Les deux agrégats
concernés retombent sur leur médiane, et la fonction le signale.

---

## Checklist

- [x] Modèle chargé depuis le choix de l'étape 5b, sans nouvelle sélection
- [x] Résidus, importances, erreurs par groupe et temporel calculés hors pli, **avant** le test
- [x] Importance par permutation moyennée sur 5 plis groupés, avec son écart-type
- [x] Résultats confrontés aux hypothèses de l'EDA
- [x] **Jeu de test construit et lu dans une seule cellule**
- [x] Gain sur la référence naïve chiffré sur le même test
- [x] Score de test comparé à la validation : écart de 0,006 point
- [x] Pipeline sauvegardée, rechargement vérifié sur l'apprentissage
- [x] Inférence identique à l'entraînement, vérifiée sur 200 lignes brutes

---

## Utilisation de l'IA sur cette étape

Cette étape est issue de la révision demandée par la formatrice, menée avec Claude Code.

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| Les quatre retours de la formatrice, collés tels quels | Un plan : transformateur d'agrégats dans la pipeline, découpage groupé, diagnostics en validation croisée, test ouvert une fois | Plan relu et amendé avant exécution : retrait de `part_sortants_etablissement`, choix du modèle par le duel avant le test |
| « Le test ne doit être lu que dans une seule cellule » | Restructuration en 5 / 5b / 5c | Vérifié par un script qui cherche `X_test` et `y_test` dans tous les notebooks |
| « Comment prouver qu'il n'y a plus d'écart entre entraînement et inférence ? » | Comparer `predire` et `pipeline.predict` sur les mêmes lignes | Ajouté comme `assert` exécutable, sur 200 lignes brutes |
