# Étape 10 - Révision du protocole après relecture

## Objectif

La formatrice a relu le projet et relevé quatre erreurs techniques dans la chaîne de
modélisation. Elles étaient toutes fondées. Ce document dit ce qui était faux, ce qui a
été corrigé, et ce que la correction a changé dans les résultats.

Les quatre erreurs ont une racine commune : **le protocole était ligne à ligne, alors que
l'unité réelle du jeu est la formation**. Une formation (code UAI × code SISE) apparaît
jusqu'à six fois, une par promotion. Tout ce qui découle de ce point a été repris.

---

## 1. Les quatre retours, et leur correction

| # | Retour | Ce qui était faux | Correction |
|---|---|---|---|
| 1 | Agrégats calculés sur tout le jeu avant le split | `etape_3`, cellule 18 : quatre variables lisaient d'autres lignes que la leur, test compris | Les agrégats sont appris par un transformateur, `AgregatsContexte`, **dans la pipeline**, sur les seules lignes d'entraînement de chaque pli |
| 2 | Écart entre l'entraînement et l'inférence | Le modèle apprenait avec des agrégats du jeu complet, le référentiel livré était recalculé sur le train. `part_sortants_etablissement` changeait même de définition entre les deux | Plus de référentiel séparé : la pipeline livrée embarque ses tables d'agrégats. `part_sortants_etablissement`, non reconstructible pour une formation nouvelle, est retirée |
| 3 | Test réutilisé après la mesure finale | Importance par permutation, résidus et erreurs par groupe calculés sur le test, après le score | Tous ces diagnostics sont faits **en validation croisée**, sur des prédictions hors pli. Le test n'est lu que dans une cellule, à l'étape 5c |
| 4 | Split aléatoire sur des entités répétées | 90 % des lignes de test portaient sur une formation déjà vue à l'entraînement | Découpage et validation croisée **groupés par formation** : aucune formation n'a de promotion des deux côtés |

### Ce qui garantit désormais ces propriétés

Elles ne sont pas seulement affirmées : chacune est vérifiée par du code qui échoue si
elle est perdue.

| Propriété | Vérification | Où |
|---|---|---|
| Aucune formation des deux côtés | `assert` dans `decouper()`, puis contrôle sur le modèle livré | `modeles/protocole.py`, étapes 3 et 7 |
| Les agrégats n'apprennent que sur l'entraînement | Des lignes de test altérées ne changent pas les agrégats de l'apprentissage ; mélanger le test ne change aucune ligne | Étape 3 |
| Aucun agrégat calculé hors pipeline | `assert` : aucun agrégat dans le jeu exporté | Étape 3 |
| Inférence identique à l'entraînement | `predire` et `pipeline.predict` comparés sur 200 lignes brutes, écart nul | Étapes 5c et 7 |
| Le test n'est lu qu'une fois | Lecture du code de tous les notebooks : `X_test` et `y_test` n'apparaissent qu'au découpage (étape 3) et dans la cellule de mesure (étape 5c) | Étape 7 |

### Un module commun

Variables, découpage, validation croisée, transformateur et pipeline sont désormais définis
une seule fois, dans [`modeles/protocole.py`](../modeles/protocole.py). Les notebooks 3 à 7
et le module d'inférence l'importent au lieu de recopier ces définitions : une divergence
entre deux étapes, comme celle qui avait touché `part_sortants_etablissement`, n'est plus
possible.

---

## 2. Nouvelle organisation des étapes de modélisation

| Étape | Avant | Après |
|---|---|---|
| 4 | Comparaison de six modèles, plis aléatoires | Même comparaison, **plis groupés**, et mesure de l'optimisme des plis aléatoires |
| 5 | Optimisation, évaluation sur le test, interprétation, livraison | **Optimisation de la forêt** seulement, sans test |
| 5b | Duel forêt contre boosting, forêt conservée faute de score de test pour le boosting | **Duel** en plis groupés, choix par une règle écrite avant le calcul |
| 5c | (n'existait pas) | **Diagnostic** du modèle retenu en validation croisée, **unique ouverture du test**, livraison |

---

## 3. Ce que la correction a changé dans les résultats

### Le score

| Mesure | Protocole initial | Protocole corrigé |
|---|---:|---:|
| Découpage | aléatoire, ligne à ligne | groupé par formation |
| Modèle livré | forêt aléatoire | **gradient boosting** |
| MAE de test | 9,579 | **10,090** |
| R² de test | 0,554 | **0,484** |
| Référence naïve (MAE de test) | 15,069 | 14,765 |
| Réduction de l'erreur | 36 % | **32 %** |
| Formations de test déjà vues | 90 % | **0 %** |
| Validation temporelle, R² | 0,458 | 0,448 |
| Taille du modèle livré | 29,6 Mo | 0,26 Mo |

**Le nouveau score est moins bon, et c'est le bon.** L'ancien mesurait surtout la capacité
à reconnaître une formation déjà vue. L'étape 4 chiffre cet optimisme sur les mêmes lignes
et la même forêt : **0,84 point de MAE**, environ quatre fois l'écart-type entre plis.
L'ancien protocole le laissait déjà entrevoir : 11,28 de MAE sur les seules formations
inconnues du test, contre 9,39 sur les formations déjà vues.

**Le nouveau score est confirmé.** La MAE de test (10,090) rejoint à 0,006 point celle de
la validation croisée groupée (10,084). Le protocole mesure ce qu'il prétend mesurer.

### Le modèle livré

Le gradient boosting remplace la forêt aléatoire. Ce n'est pas un changement d'avis, c'est
l'application d'une règle :

- en plis groupés, le boosting devance la forêt dès l'étape 4 (10,02 contre 10,28), puis
  après optimisation des deux à l'étape 5b (10,08 contre 10,26), sur les cinq plis et sur
  13 des 14 découpages par groupe ;
- l'ancienne raison de garder la forêt, « seul modèle mesuré sur le test », disparaît avec
  un test neuf : le choix se fait désormais avant toute ouverture du test.

### Ce qui n'a pas changé

Les conclusions qualitatives tiennent, ce qui est rassurant sur leur solidité :

- la vocation du diplôme domine (`est_diplome_professionnalisant`, 1re variable), suivie du
  ratio de poursuite d'études ;
- l'hypothèse « le secteur prime sur le domaine » reste infirmée ;
- l'erreur reste nettement plus forte sur les petites formations (11,8 contre 7,5) ;
- les variables créées à l'étape 3 apportent un gain mesurable (0,22 point de MAE), et la
  seconde source n'en apporte pas (0,014 point, quinze fois moins que le bruit).

---

## 4. Ce qu'il faut dire honnêtement

**L'ancien jeu de test a été consulté.** Le nouveau découpage est différent, mais il porte
sur les mêmes données : certaines de ses lignes avaient déjà été vues comme lignes de test
dans la première version. Aucune décision de la version corrigée n'a été prise en regardant
un score de test : le modèle est choisi par la règle de l'étape 5b, en validation croisée,
et le test n'est lu qu'à l'étape 5c. Mais la première version existait, et la connaissance
du projet qu'elle a donnée ne s'efface pas.

**Les leçons de la première version restent valables.** Elle avait correctement identifié
le recouvrement (90 %) et son coût (+1,89 point sur les formations inconnues), sans en
tirer la conséquence : le score principal restait le score aléatoire. C'est le pas que la
relecture a fait franchir.

---

## Checklist

- [x] Agrégats appris dans la pipeline, sur l'entraînement de chaque pli
- [x] Plus d'écart entre entraînement et inférence, vérifié sur 200 lignes brutes
- [x] Test lu dans une seule cellule, vérifié en lisant le code des notebooks
- [x] Découpage et validation croisée groupés par formation
- [x] Optimisme de l'ancien protocole chiffré
- [x] Modèle choisi par une règle fixée avant le calcul, avant l'ouverture du test
- [x] Chaîne complète rejouée après correction
- [x] Résultats avant / après reportés, y compris la baisse du score
