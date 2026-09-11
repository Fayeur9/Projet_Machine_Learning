# Étape 5b - Duel : forêt aléatoire contre gradient boosting

## Objectif

L'étape 4 n'avait pas vraiment départagé les deux premiers modèles : 9,495 contre 9,518 de
MAE, pour un écart-type entre plis de 0,147. **L'écart était six fois plus petit que le
bruit de mesure.** La forêt avait été retenue sur sa stabilité, ce qui se défend, mais
aucun des deux n'était alors optimisé : c'était un départage par défaut.

Cette étape optimise chacun séparément, mesure ce qui les sépare réellement, et teste si
les combiner vaut mieux que choisir.

Notebook : [`etape_5b_duel_foret_boosting.ipynb`](../notebooks/etape_5b_duel_foret_boosting.ipynb)

**Règle du jeu de test** : tout se joue en validation croisée sur les seules 13 652
formations d'apprentissage. Le jeu de test n'est pas ouvert. S'il l'était pour départager,
il cesserait d'être un jeu de test.

---

## 1. Dimensionner avant d'explorer

| Famille | Paramètre | RMSE | Écart train − validation |
|---|---|---:|---:|
| Forêt | 50 arbres | 12,654 | 0,363 |
| Forêt | 100 arbres | 12,591 | 0,362 |
| Forêt | 200 arbres | 12,568 | 0,361 |
| Forêt | 400 arbres | 12,554 | 0,361 |
| Boosting | 100 itérations | 12,422 | 0,122 |
| Boosting | 200 itérations | 12,215 | 0,187 |
| Boosting | 400 itérations | 12,172 | 0,271 |
| Boosting | 800 itérations | 12,247 | **0,359** |

Les deux familles ne se comportent pas du tout pareil, et c'est ce qui justifie de leur
donner des grilles différentes.

**La forêt plafonne.** Elle gagne l'essentiel entre 50 et 200 arbres, puis 0,014 point de
RMSE en doublant encore. Son écart entraînement / validation ne bouge pas d'un millième :
ajouter des arbres à une forêt ne la fait pas surapprendre, cela ne fait que stabiliser la
moyenne. Le nombre d'arbres n'est donc pas un levier, c'est un budget de calcul.

**Le boosting, lui, finit par surapprendre.** Son écart triple de 100 à 800 itérations, et
sa RMSE **remonte** après 400 : les dernières itérations ne corrigent plus des erreurs, elles
corrigent du bruit. Ses vrais leviers sont le taux d'apprentissage et la taille des arbres.

---

## 2. Deux grilles, un protocole de sélection identique

| Forêt aléatoire | Valeurs explorées |
|---|---|
| `max_features` | `sqrt`, 0.3, 0.5, 0.8 |
| `min_samples_leaf` | 1, 2, 5, 10 |
| `n_estimators` | 300, fixé d'après la courbe ci-dessus |

| Gradient boosting | Valeurs explorées |
|---|---|
| `learning_rate` | 0.03, 0.06, 0.1 |
| `max_leaf_nodes` | 15, 31, 63 |
| `min_samples_leaf` | 10, 20 |
| `max_iter` | 400, fixé d'après la courbe ci-dessus |

Même sélection pour les deux, celle de l'étape 5 : meilleure RMSE, puis **règle à un
écart-type**, puis la configuration la plus simple parmi les équivalentes.

| | Meilleure de la grille | Seuil à 1 écart-type | Équivalentes | Retenue |
|---|---:|---:|---:|---|
| Forêt | 12,168 (± 0,191) | 12,359 | 7 sur 16 | `max_features=0.3`, `min_samples_leaf=2` |
| Boosting | 11,848 (± 0,169) | 12,017 | 10 sur 18 | `learning_rate=0.1`, `max_leaf_nodes=15`, `min_samples_leaf=10` |

---

## 3. Le résultat : deux modèles très proches, un léger avantage au boosting

| Modèle | MAE | RMSE | R² | à ±5 pts | ratées de +15 pts |
|---|---:|---:|---:|---:|---:|
| Forêt optimisée | 9,439 | 12,278 | 0,557 | 35,2 % | 20,6 % |
| **Boosting optimisé** | **9,241** | **12,005** | **0,577** | 35,3 % | 19,4 % |
| Moyenne des deux | 9,199 | 11,963 | 0,580 | 35,8 % | 19,5 % |

**L'avantage du boosting est faible mais systématique.** 0,198 point de MAE, soit environ
1,3 fois l'écart-type entre plis : pris isolément, l'écart serait discutable. Ce qui lui
donne du poids, c'est sa régularité : sur 14 découpages par taille de formation, domaine et
promotion, le boosting en remporte **13**. La forêt n'en garde qu'un, Lettres langues et
arts, pour 0,03 point. Un écart faible mais présent partout est plus solide qu'un écart
global isolé.

**L'optimisation ne profite pas également aux deux.** La forêt gagne 0,056 point entre sa
version de l'étape 4 et sa version optimisée ; le boosting en gagne 0,277, cinq fois plus.
La courbe de convergence l'annonçait : la forêt était déjà proche de son plafond avec ses
réglages par défaut, le boosting était mal réglé. **Comparer deux modèles non optimisés ne
dit rien de leur potentiel** : c'est la leçon principale de cette étape, et elle vaut
au-delà de ce projet.

**Les deux modèles se ressemblent énormément**, et c'est le résultat principal de cette
étape. Quatre mesures indépendantes concordent : leurs prédictions corrèlent à **0,953**
pour un écart absolu moyen de **3,16 points**, elles ne divergent de plus de 10 points que
sur **2,4 %** des formations, leurs rangs d'importance de variables corrèlent à **0,905**, et
l'écart médian entre eux sur les 14 découpages est de **0,15 point de MAE** quand l'erreur
elle-même vaut 9,4. Sur une formation donnée, il est rare que le choix du modèle change la
réponse de plus d'un ou deux points.

**Les combiner n'apporte rien.** La moyenne des deux gagne 0,042 point sur le boosting seul,
très en dessous du bruit. C'est cohérent : leurs prédictions corrèlent à 0,953, leur écart
absolu moyen est de 3,16 points, et elles ne divergent de plus de 10 points que sur 2,4 %
des formations. Deux modèles qui se trompent aux mêmes endroits ne se corrigent pas l'un
l'autre. Doubler le temps d'entraînement et la taille du livrable pour 0,042 point ne se
justifie pas.

**Ils exploitent le même signal, plus ou moins fort.** La corrélation des rangs d'importance
est de 0,905. Le boosting s'appuie deux fois plus sur `est_diplome_professionnalisant`
(4,04 contre 2,04 points de RMSE) et tire davantage des variables d'établissement. Rien
n'indique qu'il ait trouvé un signal que la forêt aurait manqué : il exploite mieux le même.

![Duel](../figures_eda/fig18_duel_foret_boosting.png)

---

## 4. Décision : la forêt aléatoire est conservée

L'écart mesuré penche pour le boosting, mais il est ténu : 0,198 point de MAE, soit 2 % de
l'erreur. La forêt reste néanmoins le modèle livré, pour trois raisons.

**1. Le seul score mesuré sur le jeu de test est celui de la forêt : 9,579 points de MAE.**
Celui du boosting n'existe qu'en validation croisée. Échanger un résultat mesuré contre une
estimation, pour 2 %, c'est troquer une certitude contre une promesse.

**2. Le jeu de test n'a été ouvert qu'une fois.** Le rouvrir pour départager rendrait le
score final légèrement optimiste et ferait perdre une garantie méthodologique qui vaut plus
que 0,2 point de MAE. C'est aussi un critère explicite de la grille d'évaluation.

**3. Le gain serait invisible à l'usage.** L'erreur passerait de 9,58 à environ 9,4 points
sur une cible qui varie de 0 à 100. Aucun utilisateur ne lirait la différence, alors que
tous liraient l'incohérence d'un protocole abandonné en cours de route.

**Ce que ce choix coûte**, et il faut l'assumer : environ 0,2 point de MAE, et le fait que
le modèle livré n'est probablement pas le meilleur atteignable sur ces données. C'est écrit
plutôt que masqué : un choix documenté se défend, un choix caché se découvre.

---

## Checklist

- [x] Chaque famille optimisée avec sa propre grille, sur ses vrais leviers
- [x] Nombre d'arbres et d'itérations dimensionnés avant l'exploration
- [x] Même protocole de sélection pour les deux, règle à un écart-type comprise
- [x] Comparaison sur les mêmes plis, avec la même pipeline
- [x] Écart mesuré contre le bruit entre plis, pas commenté en valeur absolue
- [x] Analyse par groupe : qui gagne où, et sur combien de formations
- [x] Piste de l'ensemble testée et rejetée sur preuve, pas par principe
- [x] Importances comparées entre les deux familles
- [x] Jeu de test non ouvert
- [x] Décision tranchée et argumentée, avec son coût assumé

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Quels hyperparamètres comptent vraiment pour une forêt, pour un boosting ? » | `max_features` et `min_samples_leaf` d'un côté, `learning_rate` et `max_leaf_nodes` de l'autre | Vérifié par la courbe de convergence avant de bâtir les grilles : le nombre d'arbres ne discrimine effectivement plus au-delà de 200 |
| « Faut-il combiner deux modèles proches ? » | Réponse générale favorable au moyennage | Testée plutôt que crue : le gain est de 0,042 point, dans le bruit, parce que les deux modèles corrèlent à 0,953. La proposition ne tenait pas ici |
| « Comment savoir si un écart de MAE est significatif ? » | Comparaison à l'écart-type entre plis | Complétée par une analyse en 14 groupes : c'est la régularité de l'avantage, pas sa taille, qui a emporté la conclusion |

Le deuxième échange est le plus instructif : une recommandation correcte en général s'est
révélée fausse dans ce cas précis, et seule la mesure permettait de le voir.
