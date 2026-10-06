# Étape 9 - Préparation de la soutenance

## Objectif

La grille note la soutenance sur 7 points, dont **4 sur la défense** : « défend ses choix,
assume ses limites, répond aux objections ». Ces 4 points ne se gagnent pas en écrivant un
fichier, mais ils se préparent. Ce document contient le minutage, et surtout les questions
probables avec leurs réponses chiffrées.

**Support** : 11 diapositives, `presentation/soutenance.pptx` et son PDF, avec le script
complet dans `presentation/script_soutenance.md`. Volontairement hors dépôt git.

---

## 1. Minutage : 7 minutes, 11 diapositives

| # | Diapositive | Temps | Ce qu'il faut avoir dit en sortant |
|---|---|---:|---|
| 1 | Couverture | 15 s | Régression, 17 065 lignes, InserSup |
| 2 | La question | 35 s | La cible, et **pourquoi la MAE** plutôt que le R² |
| 3 | La cible vide | 30 s | La colonne du cadrage était vide sur 1 036 781 lignes |
| 4 | Deux sources | 35 s | CSV et JSON, et la mise au grain à 17 065 |
| 5 | Anti-fuite | 45 s | Colonnes exclues, **découpage par formation**, agrégats dans la pipeline |
| 6 | Six modèles | 35 s | **Toujours partir de la référence naïve** |
| 7 | Le duel | 40 s | Le boosting gagne, sur une règle fixée avant le test |
| 8 | Le résultat | 45 s | 10,09 contre 14,77 sur des formations jamais vues, 32 % d'erreur en moins |
| 9 | Ce qu'il a appris | 35 s | Top 4 = variables créées, une hypothèse de l'EDA infirmée |
| 10 | Les limites | 60 s | Extrêmes, temporel, petits effectifs, portée |
| 11 | La suite | 25 s | Trois pistes, puis se taire |

Total : 400 secondes. **Prévoir de finir à 6 min 40** : on parle toujours plus lentement
devant un jury que seul.

La diapositive 10 est celle qui rapporte le plus. Ne pas l'expédier, et surtout ne pas
attendre qu'on demande les limites pour les donner.

---

## 2. Les questions du jury, et les réponses

### Sur la méthode

**« Quelle accuracy obtenez-vous ? »**
Il n'y a pas d'accuracy : c'est une régression, la cible est un taux continu. L'erreur
moyenne est de **10,09 points** de taux d'emploi, le R² de 0,484, contre **14,77 points**
pour une référence naïve qui prédirait la moyenne partout. Et ce sur des formations dont le
modèle n'a vu aucune promotion. Si le jury veut un pourcentage : 33 % des lignes sont
prédites à moins de 5 points près, contre 21 % pour la référence.

**« Comment savez-vous qu'il n'y a pas de fuite de données ? »**
Quatre niveaux, et ils sont exécutables.
1. Six colonnes exclues par construction : les taux d'emploi à 12, 18, 24 et 30 mois, et
   l'emploi stable et non salarié à 6 mois. Celle à 12 mois corrèle à 0,849 : c'était la
   plus prédictive du jeu.
2. Le découpage est **groupé par formation** : aucune formation n'a de promotion à la fois
   en apprentissage et en test.
3. Tout ce qui apprend sur les données est dans la pipeline, **agrégats compris** : ils
   sont appris sur l'entraînement de chaque pli, et le même objet sert à l'inférence.
4. Des tests qui échouent si la propriété est perdue : permutation de la cible, isolement
   du transformateur d'agrégats, et dix contrôles sur le modèle livré, dont un qui lit le
   code des notebooks pour vérifier que le test n'est lu qu'une fois.

**« Votre R² de 0,48 n'est pas très élevé. »**
Non, et c'est attendu. Les variables les plus corrélées à la cible sont précisément celles
qu'il fallait exclure. Et le score est mesuré sur des formations jamais vues, ce qui est
plus dur que de reconnaître une formation connue. Le bon repère n'est pas 1, c'est la
référence naïve : 32 % d'erreur en moins. Le reste tient en partie au marché local de
l'emploi, absent des données.

**« Le jeu de test a-t-il servi une seule fois ? »**
Oui, et c'est vérifié par du code : l'étape 7 lit tous les notebooks et échoue si `X_test`
ou `y_test` apparaissent ailleurs qu'au découpage et dans la cellule de mesure de
l'étape 5c. Résidus, importances et erreurs par groupe sont calculés avant, en validation
croisée. **À dire aussi** : dans la première version, ce n'était pas le cas, la relecture de
la formatrice l'a relevé, et c'est corrigé.

### Sur le modèle

**« Pourquoi le gradient boosting ? »**
Par une règle écrite avant le calcul : le meilleur des deux en validation croisée groupée,
après optimisation de chacun. Le boosting fait 10,08 de MAE contre 10,26 pour la forêt. Ce
n'est que 1,2 écart-type entre plis, mais il gagne **les cinq plis** et **13 des 14
découpages** par taille, domaine et promotion. La moyenne des deux n'apporte rien.

**« Vous aviez d'abord choisi la forêt. Pourquoi avoir changé ? »**
La première version gardait la forêt parce qu'elle seule avait un score de test, et rouvrir
le test pour départager l'aurait rendu optimiste. Avec le découpage groupé, il fallait un
test neuf : cet argument disparaissait, et le choix s'est fait avant d'ouvrir ce test. Ce
n'est pas un changement d'avis, c'est la même règle appliquée à un protocole correct.

**« Pourquoi pas un modèle linéaire, plus simple à expliquer ? »**
Il a été testé : 10,62 de MAE contre 10,02 pour le boosting à l'étape 4. L'écart se paie en
interprétabilité, et le projet compense par l'importance par permutation, moyennée sur cinq
plis.

**« Quels hyperparamètres avez-vous explorés ? »**
Pour le boosting : le pas d'apprentissage, la taille des arbres et la taille minimale des
feuilles, 18 configurations. En validation groupée, 16 sont équivalentes à la meilleure à
un écart-type près : la règle à un écart-type retient la plus simple. L'optimisation n'a pas
fait baisser l'erreur, elle a confirmé que le classement tenait.

### Sur les résultats

**« Votre score est-il optimiste ? »**
Non, et c'est mesuré. Sur les mêmes lignes et la même forêt, une validation aléatoire
annonçait 0,84 point d'erreur en moins qu'une validation groupée : c'était de la mémoire,
pas de la performance. Le protocole groupé élimine ce biais, et le score de test (10,090)
rejoint celui de la validation (10,084) à 0,006 point près.

**« Pourquoi votre score a-t-il baissé depuis la première version ? »**
Parce que la première version mesurait autre chose. 90 % des lignes de test portaient sur
des formations déjà vues à l'entraînement, par une autre promotion. Le nouveau score porte
sur des formations jamais vues : 10,09 au lieu de 9,58. Il est moins flatteur, et c'est le
bon. Le détail est dans l'étape 10.

**« Votre modèle est-il utilisable en production ? »**
Pour situer une formation face à ses comparables, oui. Pour décider d'un financement ou
d'une fermeture, non : l'erreur moyenne avoisine 10 points et monte à 11,8 sur les
formations de 25 sortants ou moins. Elle est du même ordre que les écarts qu'on voudrait
arbitrer. C'est écrit dans la fiche modèle, avec trois autres usages écartés.

**« Qu'est-ce qui vous a le plus surpris ? »**
L'écart entre femmes et hommes **change de signe** selon la façon de comparer. En brut, les
hommes sont devant de 2,84 points. À diplôme, établissement et promotion identiques, sur les
4 026 formations où les deux sont publiés, les femmes repassent devant de 2,38 points.
L'écart brut mesure l'orientation, pas l'insertion. À dire aussi : ces variables ne sont pas
dans le modèle, il ne peut donc rien affirmer sur ces disparités.

**« Qu'est-ce que la relecture vous a appris ? »**
Que l'unité d'un jeu de données n'est pas forcément sa ligne. Le projet avait identifié le
recouvrement des formations et l'avait même chiffré, sans en tirer la conséquence : le
score principal restait le score aléatoire. Tout le protocole a été repris à partir de ce
point, et les contrôles qui vérifient désormais ces propriétés échouent si elles sont
perdues.

**« Vos résultats sont-ils reproductibles ? »**
`random_state=42` partout, chaîne exécutable de bout en bout, rejouée après la révision.
Le modèle rechargé reproduit ses prédictions, et une ligne brute passée par le module
d'inférence reçoit exactement la prédiction de la pipeline.

### Sur les données

**« Pourquoi 17 065 lignes sur 1 036 781 ? »**
Le fichier mêle le détail et ses agrégats. Retenir les formations d'une promotion simple,
hors marges géographiques et disciplinaires, hors ventilations démographiques, donne des
lignes comparables entre elles et supprime le double comptage. Chaque filtre est chiffré
dans l'entonnoir d'extraction.

**« Votre seconde source sert-elle à quelque chose ? »**
Elle apporte le clivage public / privé, invisible dans InserSup : 4,5 points d'écart. Mais
testée dans le modèle, elle ne gagne que 0,014 point de MAE, quinze fois moins que le bruit
entre plis. Elle n'a donc pas été retenue, et ce résultat négatif est reporté plutôt que
masqué.

---

## 3. Trois pièges à éviter

1. **Annoncer un score sans son repère.** Jamais « R² de 0,48 » seul, toujours « contre une
   référence naïve qui fait 14,77 de MAE », et « sur des formations jamais vues ».
2. **Dire « accuracy ».** Le mot n'a pas de sens ici, et l'employer suggère qu'on n'a pas vu
   la différence entre régression et classification.
3. **Défendre un choix qu'on n'a pas fait.** Si une question porte sur un point non traité,
   le dire, et enchaîner sur ce qui a été mesuré. Un « je ne l'ai pas testé » assumé coûte
   moins qu'une improvisation. De même pour la révision : la présenter comme une correction
   reçue et appliquée, pas comme une idée de départ.

---

## Checklist de la phase 9

- [x] Support prêt : 11 diapositives, avec notes d'orateur et script complet
- [x] Minutage établi, avec une marge sur les 7 minutes
- [x] Limites annoncées **proactivement**, diapositive dédiée
- [x] Questions probables anticipées, avec réponses chiffrées, révision comprise
- [ ] **Répétition à voix haute, chronométrée** : reste à faire, et ne peut pas être délégué
- [ ] Vérifier que le PDF s'ouvre sur la machine de présentation
