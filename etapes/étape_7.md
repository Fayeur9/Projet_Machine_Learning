# Étape 7 - Synthèse de modélisation et fiche modèle

## Objectif

Faire le pont entre un modèle qui marche et un modèle qu'on peut livrer. La modélisation
elle-même est faite : l'étape 4 a comparé six modèles à une référence naïve, l'étape 5 a
optimisé, évalué une seule fois sur le jeu de test et interprété.

**Cette étape ne réentraîne rien**, et c'est un choix : réentraîner ici produirait un second
modèle, donc une seconde vérité, pour un projet qui n'en veut qu'une. Elle ajoute les trois
choses qui manquaient entre le modèle et son usage.

Notebook : [`etape_7_synthese_modele.ipynb`](../notebooks/etape_7_synthese_modele.ipynb)
Fiche modèle : [`MODEL_CARD.md`](../MODEL_CARD.md)
Code d'inférence : [`modeles/inference.py`](../modeles/inference.py)

---

## 1. Le protocole en une page

| Décision | Ce qui a été fait | Où |
|---|---|---|
| Périmètre | 17 065 formations, 19 variables, 8 catégorielles et 11 numériques | Étape 3 |
| Découpage | 80 / 20, `random_state=42`, avant tout prétraitement | Étape 3 |
| Prétraitement | One-hot et passthrough, **dans la pipeline** | Étape 4 |
| Référence | `DummyRegressor(strategy='mean')`, mêmes conditions que les modèles | Étape 4 |
| Comparaison | 6 modèles, validation croisée 5 plis, mêmes plis pour tous | Étape 4 |
| Sélection | Forêt aléatoire, sur la stabilité entre plis à score égal | Étape 4 |
| Optimisation | `GridSearchCV`, `cv=5`, puis règle à un écart-type | Étape 5 |
| Évaluation | Test ouvert **une seule fois** : MAE 9,579, RMSE 12,373, R² 0,554 | Étape 5 |
| Interprétation | Importance par impureté et par permutation, confrontées à l'EDA | Étape 5 |
| Robustesse | Recouvrement chiffré, validation temporelle 2023-2024 | Étape 5 |

Le détail, avec les tableaux et les figures, est dans [`étape_4.md`](étape_4.md) et
[`étape_5.md`](étape_5.md).

---

## 2. Huit contrôles de conformité, exécutables

Une case cochée dans un document n'engage rien. Ces huit contrôles portent sur le fichier
`.joblib` réellement livré, et chacun lève une `AssertionError` s'il n'est pas satisfait.

| Contrôle | Ce qu'il vérifie |
|---|---|
| Cible absente des variables | La cible n'est pas dans les 19 entrées |
| Aucune variable postérieure | Ni 12, 18, 24, 30 mois, ni emploi stable ou non salarié |
| Aucun identifiant brut | Les codes UAI et SISE ne servent qu'aux variables dérivées |
| Prétraitement dans la pipeline | Deux étapes : `pretraitement` puis `modele` |
| Hasard fixé | `random_state=42` sur la forêt livrée |
| Prédictions reproductibles | Deux appels identiques à la tolérance flottante |
| Métriques livrées | MAE, RMSE et R² voyagent avec le modèle |
| Référentiel embarqué | Les valeurs de repli viennent du seul jeu d'apprentissage |

**Un résultat inattendu, et instructif.** Le contrôle de reproductibilité a d'abord échoué :
deux appels successifs sur les mêmes entrées ne donnent pas des valeurs identiques au bit
près, mais à environ 2 × 10⁻¹⁴ près. Ce n'est pas un défaut de fixation du hasard. La forêt
somme ses 200 arbres en parallèle (`n_jobs=-1`), et l'addition en virgule flottante n'est
pas associative : l'ordre d'accumulation change le dernier chiffre. L'écart est quinze
ordres de grandeur sous la précision d'une cible qui se mesure en points de pourcentage. Le
contrôle teste donc l'égalité à la tolérance flottante.

**Ce que ces contrôles ne prouvent pas** : que le jeu de test n'a servi qu'une fois. Cela ne
se lit pas dans un fichier, cela se lit dans les notebooks. L'étape 4 supprime le test de la
mémoire dès sa première cellule, l'étape 5 ne l'ouvre qu'à sa section 3, et aucune décision
n'a été prise après. C'est vérifiable en lisant, pas mesurable ici, et il vaut mieux le dire
que le laisser croire.

---

## 3. Un modèle utilisable sans rejouer un notebook

Un modèle qui ne s'utilise qu'en réexécutant le notebook qui l'a produit n'est pas livré.
[`modeles/inference.py`](../modeles/inference.py) prend une formation telle qu'InserSup la
publie, reconstruit les onze variables dérivées à partir du référentiel embarqué, et rend
une prédiction :

```python
from modeles.inference import charger, predire

modele = charger()
predire(modele, {'Région': 'Bretagne', 'Type de diplôme': 'Licence professionnelle', ...})
```

Le notebook vérifie par `assert` que ce module reproduit **exactement** la démonstration de
l'étape 5 : 68,4 %. Si la logique de préparation diverge un jour de celle qui a servi à
l'entraînement, le contrôle échoue.

### Trois cas contrastés

| Cas | Prédiction | Intervalle indicatif |
|---|---:|---|
| Licence pro informatique, Rennes, 2024 | 68,4 % | 58,8 à 78,0 % |
| La même, en licence générale | 53,0 % | 43,4 à 62,6 % |
| Master LMD en langues, promotion 2020 | 29,1 % | 19,6 à 38,7 % |

Seul le paramètre étudié change d'une ligne à l'autre. L'écart de **15,4 points** entre les
deux premières lignes correspond à ce que l'étape 2 avait mesuré sur la vocation du diplôme,
et le troisième cas cumule les facteurs défavorables identifiés : discipline littéraire et
promotion 2020.

**Une prédiction ne se lit jamais seule.** L'intervalle vaut plus ou moins la MAE de test,
soit 9,6 points. Il est indicatif, pas statistique : ce n'est pas un intervalle de confiance,
c'est l'ordre de grandeur de l'erreur habituelle. Sur une formation de moins de 25 sortants,
il faut le lire plus large : l'étape 5 y mesure 12,09 points.

**Les modalités inconnues ne font pas échouer la prédiction.** Un code diplôme absent du
référentiel fait retomber trois variables sur la médiane d'apprentissage, et la réponse le
signale par sa clé `replis` plutôt que de le taire.

---

## 4. La fiche modèle

[`MODEL_CARD.md`](../MODEL_CARD.md) est **générée** depuis le modèle chargé, pour qu'elle ne
puisse pas décrire autre chose que ce qui est livré. Elle couvre ce que fait le modèle, ses
données, ses performances, ses cas d'échec chiffrés, ses biais connus, et une section que le
projet n'avait pas encore : **ce pour quoi il ne doit pas être utilisé**.

Quatre usages y sont explicitement écartés, et chacun pour une raison mesurée :

- **décider du financement ou de la fermeture d'une formation** : l'erreur moyenne dépasse
  9 points, du même ordre que les écarts qu'on voudrait arbitrer ;
- **comparer deux formations proches** : un écart de 5 points prédits est dans le bruit ;
- **évaluer une personne** : l'unité de prédiction est une formation entière ;
- **classer des établissements** : un établissement spécialisé hérite de la performance de
  son secteur, l'étape 2 le montre.

---

## Checklist de la phase 7

**7.1 Rigueur méthodologique**

- [x] `train_test_split` avant tout prétraitement
- [x] `stratify` sans objet : régression
- [x] Tout le prétraitement dans un `ColumnTransformer` / `Pipeline`
- [x] Aucune colonne fuitante ni identifiant dans `X`, vérifié par `assert` sur le livrable
- [x] Jeu de test ouvert une seule fois
- [x] `random_state` fixé partout, et contrôlé sur le modèle sauvegardé

**7.2 Baseline et comparaison**

- [x] `DummyRegressor` calculé dans les mêmes conditions
- [x] 6 modèles comparés, dont deux modèles linéaires
- [x] `GridSearchCV` avec `cv=5`, `cv_results_` commenté
- [x] Choix final justifié, et son coût chiffré (0,073 point de MAE)

**7.3 Évaluation**

- [x] Métrique principale justifiée par le métier
- [x] MAE et RMSE dans l'unité de la cible, R², résidus analysés
- [x] Écart entraînement / validation traduit en nombre de formations
- [x] Score de test reporté honnêtement, gain sur la référence chiffré

**7.4 Interprétation et limites**

- [x] Importance des variables par deux méthodes
- [x] Cohérence avec l'EDA discutée, deux hypothèses infirmées assumées
- [x] Cas d'échec identifiés et mesurés
- [x] Biais de sélection, de représentation et d'interprétation discutés

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Que contient une bonne fiche modèle ? » | Structure en sections, dont « usage prévu » et « hors périmètre » | Retenue, mais la section la plus utile a été réécrite à partir des erreurs mesurées à l'étape 5, pas d'un canevas générique |
| « Écris des tests pour vérifier l'absence de fuite dans un modèle sauvegardé » | Boucle sur les noms de colonnes avec motifs interdits | Conservée et complétée : un test de déterminisme et un contrôle du `random_state`, absents de la proposition |
| « Mon modèle peut-il servir à décider de fermer une formation ? » | Réponse nuancée sur les usages à haut risque | Traduite en critère chiffré : l'erreur moyenne est du même ordre que les écarts à arbitrer, donc non |

Le troisième échange est celui qui a le plus changé le livrable : il a transformé une
intuition, « attention à l'usage », en une limite argumentée par les chiffres du projet.
C'est aussi le test de déterminisme, suggéré par le deuxième, qui a révélé le comportement
de la sommation parallèle.
