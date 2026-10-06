# Étape 7 - Synthèse de modélisation et fiche modèle

## Objectif

Faire le pont entre un modèle qui marche et un modèle qu'on peut livrer. La modélisation
elle-même est faite : l'étape 4 a comparé six modèles à une référence naïve, l'étape 5 a
optimisé la forêt, l'étape 5b a choisi entre forêt et boosting, l'étape 5c a diagnostiqué
le modèle retenu puis l'a évalué une seule fois sur le jeu de test.

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
| Périmètre | 17 065 formations, 18 variables, 8 catégorielles et 10 numériques | Étape 3 |
| Découpage | 80 / 20 **groupé par formation**, `random_state=42` : aucune formation des deux côtés | Étape 3 |
| Prétraitement | Agrégats de contexte, one-hot et passthrough, **tous dans la pipeline** | Étapes 3 et 4 |
| Référence | `DummyRegressor(strategy='mean')`, mêmes conditions que les modèles | Étape 4 |
| Comparaison | 6 modèles, validation croisée **groupée** à 5 plis, mêmes plis pour tous | Étape 4 |
| Optimisation | `GridSearchCV` en plis groupés, puis règle à un écart-type | Étapes 5 et 5b |
| Sélection | Gradient boosting, vainqueur du duel sur une règle fixée avant le calcul | Étape 5b |
| Diagnostic | Résidus, importance par permutation, erreurs par groupe, temporel, **hors pli** | Étape 5c |
| Évaluation | Test ouvert **une seule fois** : MAE 10,090, RMSE 13,081, R² 0,484 | Étape 5c |

Le détail est dans [`étape_4.md`](étape_4.md), [`étape_5b.md`](étape_5b.md) et
[`étape_5c.md`](étape_5c.md). La révision du protocole est décrite dans
[`étape_10_revision.md`](étape_10_revision.md).

---

## 2. Dix contrôles de conformité, exécutables

Une case cochée dans un document n'engage rien. Ces dix contrôles portent sur le fichier
`.joblib` réellement livré et sur le code qui l'a produit, et chacun lève une
`AssertionError` s'il n'est pas satisfait.

| Contrôle | Ce qu'il vérifie |
|---|---|
| Cible absente des entrées | La cible n'est pas dans les 17 colonnes reçues par la pipeline |
| Aucune variable postérieure | Ni 12, 18, 24, 30 mois, ni emploi stable ou non salarié |
| Aucun identifiant ne parvient au modèle | Les codes UAI et SISE ne servent qu'aux agrégats |
| Tout ce qui apprend est dans la pipeline | Trois étapes : `agregats`, `pretraitement`, `modele` |
| Agrégats embarqués | Tables et valeurs de repli dans la pipeline, sans référentiel séparé |
| Hasard fixé | `random_state=42` sur le modèle livré |
| Aucune formation des deux côtés | 3 958 formations en apprentissage, 990 en test, aucune en commun |
| Inférence identique à l'entraînement | `predire` et `pipeline.predict` sur 200 lignes brutes : écart nul |
| Métriques livrées | MAE, RMSE et R² voyagent avec le modèle |
| Test lu une seule fois | Le code des notebooks ne touche `X_test` et `y_test` qu'au découpage et dans la cellule de mesure de l'étape 5c |

**La règle « le test s'ouvre une fois » devient vérifiable.** Dans la première version,
elle ne se lisait qu'en relisant les notebooks, et elle était d'ailleurs entamée : le test
avait servi à l'importance des variables et à l'analyse des erreurs après la mesure finale.
Le dernier contrôle lit désormais le code de tous les notebooks, et toute analyse qui
réutiliserait le test ferait échouer celui-ci.

**Plus d'écart entre entraînement et inférence.** Le contrôle compare une ligne brute
préparée par le module d'inférence et la même ligne passée directement à la pipeline :
l'écart est nul. Ce n'était pas le cas dans la première version, où le modèle avait appris
avec des agrégats du jeu complet et l'inférence lisait un référentiel recalculé sur le
train.

---

## 3. Un modèle utilisable sans rejouer un notebook

Un modèle qui ne s'utilise qu'en réexécutant le notebook qui l'a produit n'est pas livré.
[`modeles/inference.py`](../modeles/inference.py) prend une formation telle qu'InserSup la
publie, reconstruit les six variables ligne à ligne avec les définitions de
[`modeles/protocole.py`](../modeles/protocole.py), et laisse la pipeline calculer les trois
agrégats avec les tables apprises sur l'apprentissage :

```python
from modeles.inference import charger, predire

modele = charger()
predire(modele, {'Région': 'Bretagne', 'Type de diplôme': 'Licence professionnelle', ...})
```

Le notebook vérifie par `assert` que ce module reproduit la démonstration de l'étape 5c :
63,3 %.

### Trois cas contrastés

| Cas | Prédiction | Intervalle indicatif |
|---|---:|---|
| Licence pro informatique, Rennes, 2024 | 63,3 % | 53,2 à 73,4 % |
| La même, en licence générale | 56,9 % | 46,8 à 67,0 % |
| Master LMD en langues, promotion 2020 | 36,1 % | 26,0 à 46,2 % |

Seul le paramètre étudié change d'une ligne à l'autre. Passer d'une licence professionnelle
à une licence générale coûte **6,4 points**, et le troisième cas cumule les facteurs
défavorables identifiés à l'étape 2 : discipline littéraire et promotion 2020.

**Une prédiction ne se lit jamais seule.** L'intervalle vaut plus ou moins la MAE de test,
soit 10,1 points. Il est indicatif, pas statistique : c'est l'ordre de grandeur de l'erreur
habituelle. Sur une formation de 25 sortants ou moins, il faut le lire plus large :
l'étape 5c y mesure 11,75 points.

**Les modalités inconnues ne font pas échouer la prédiction.** Ni l'établissement ni le
diplôme de l'exemple ne figurent dans l'apprentissage : les deux agrégats concernés
retombent sur leur médiane, et la réponse le signale par sa clé `replis`.

---

## 4. La fiche modèle

[`MODEL_CARD.md`](../MODEL_CARD.md) est **générée** depuis le modèle chargé : métriques,
relevés du diagnostic et importances sont lus dans le fichier livré, rien n'est recopié à
la main. Elle couvre ce que fait le modèle, ses données, ses performances, ses cas d'échec
chiffrés, ses biais connus, et **ce pour quoi il ne doit pas être utilisé** :

- **décider du financement ou de la fermeture d'une formation** : l'erreur moyenne avoisine
  10 points, du même ordre que les écarts qu'on voudrait arbitrer ;
- **comparer deux formations proches** : un écart de 5 points prédits est dans le bruit ;
- **évaluer une personne** : l'unité de prédiction est une formation entière ;
- **classer des établissements** : un établissement spécialisé hérite de la performance de
  son secteur, l'étape 2 le montre.

---

## Checklist de la phase 7

**7.1 Rigueur méthodologique**

- [x] Découpage groupé par formation avant tout ce qui apprend sur les données
- [x] `stratify` sans objet : régression
- [x] Tout le prétraitement, agrégats compris, dans une `Pipeline`
- [x] Aucune colonne fuitante ni identifiant transmis au modèle, vérifié sur le livrable
- [x] Jeu de test ouvert une seule fois, vérifié en lisant le code des notebooks
- [x] `random_state` fixé partout, et contrôlé sur le modèle sauvegardé

**7.2 Baseline et comparaison**

- [x] `DummyRegressor` calculé dans les mêmes conditions
- [x] 6 modèles comparés, dont deux modèles linéaires
- [x] `GridSearchCV` avec 5 plis groupés, `cv_results_` commentés
- [x] Choix final par une règle fixée avant le calcul, réglages par la règle à un écart-type

**7.3 Évaluation**

- [x] Métrique principale justifiée par le métier
- [x] MAE et RMSE dans l'unité de la cible, R², résidus analysés hors pli
- [x] Écart entraînement / validation traduit en nombre de formations
- [x] Score de test reporté honnêtement, gain sur la référence chiffré

**7.4 Interprétation et limites**

- [x] Importance par permutation, moyennée sur 5 plis groupés
- [x] Cohérence avec l'EDA discutée : une hypothèse infirmée, une nuancée
- [x] Cas d'échec identifiés et mesurés
- [x] Biais de sélection, de représentation et d'interprétation discutés

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Que contient une bonne fiche modèle ? » | Structure en sections, dont « usage prévu » et « hors périmètre » | Retenue, mais la section la plus utile a été réécrite à partir des erreurs mesurées, pas d'un canevas générique |
| « Écris des tests pour vérifier l'absence de fuite dans un modèle sauvegardé » | Boucle sur les noms de colonnes avec motifs interdits | Conservée et complétée : un test de déterminisme et un contrôle du `random_state`, absents de la proposition |
| « Mon modèle peut-il servir à décider de fermer une formation ? » | Réponse nuancée sur les usages à haut risque | Traduite en critère chiffré : l'erreur moyenne est du même ordre que les écarts à arbitrer, donc non |

Le troisième échange est celui qui a le plus changé le livrable : il a transformé une
intuition, « attention à l'usage », en une limite argumentée par les chiffres du projet.

**Révision.** Les contrôles de disjonction des formations, d'identité entre inférence et
entraînement, et de lecture unique du test ont été ajoutés avec Claude Code, à partir des
retours de la formatrice.
