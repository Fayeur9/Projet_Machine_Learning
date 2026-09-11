# Étape 9 - Préparation de la soutenance

## Objectif

La grille note la soutenance sur 7 points, dont **4 sur la défense** : « défend ses choix,
assume ses limites, répond aux objections ». Ces 4 points ne se gagnent pas en écrivant un
fichier, mais ils se préparent. Ce document contient le minutage, et surtout les questions
probables avec leurs réponses chiffrées.

**Support** : 10 diapositives, `presentation/soutenance.pptx` et son PDF. Volontairement
hors dépôt git.

---

## 1. Minutage : 7 minutes, 10 diapositives

| # | Diapositive | Temps | Ce qu'il faut avoir dit en sortant |
|---|---|---:|---|
| 1 | Couverture | 15 s | Régression, 17 065 formations, InserSup |
| 2 | La question | 40 s | La cible, et **pourquoi la MAE** plutôt que le R² |
| 3 | La cible vide | 35 s | La colonne du cadrage était vide sur 1 036 781 lignes |
| 4 | Deux sources | 40 s | CSV et JSON, et la mise au grain à 17 065 |
| 5 | Anti-fuite | 50 s | Colonnes exclues, split d'abord, deux tests exécutables |
| 6 | Six modèles | 50 s | **Toujours partir de la référence naïve** |
| 7 | Le résultat | 55 s | 9,58 contre 15,07, soit 36 % d'erreur en moins |
| 8 | Ce qu'il a appris | 50 s | Deux hypothèses de l'EDA infirmées |
| 9 | Les limites | 60 s | Recouvrement, validation temporelle, contemporanéité |
| 10 | La suite | 25 s | Trois pistes, puis se taire |

Total : 420 secondes. **Prévoir de finir à 6 min 30** : on parle toujours plus lentement
devant un jury que seul.

La diapositive 9 est celle qui rapporte le plus. Ne pas l'expédier, et surtout ne pas
attendre qu'on demande les limites pour les donner.

---

## 2. Les questions du jury, et les réponses

### Sur la méthode

**« Quelle accuracy obtenez-vous ? »**
Il n'y a pas d'accuracy : c'est une régression, la cible est un taux continu. L'erreur
moyenne est de **9,58 points** de taux d'emploi, le R² de 0,554, contre **15,07 points** pour
une référence naïve qui prédirait la moyenne partout. Si le jury veut un pourcentage : 33 %
des formations sont prédites à moins de 5 points près, contre 20 % pour la référence.

**« Comment savez-vous qu'il n'y a pas de fuite de données ? »**
Trois niveaux, et le dernier est exécutable.
1. Six colonnes exclues par construction : les taux d'emploi à 12, 18, 24 et 30 mois, et
   l'emploi stable et non salarié à 6 mois. Toutes mesurées au même horizon que la cible ou
   après elle. Celle à 12 mois corrèle à 0,849 : c'était la plus prédictive du jeu.
2. Le découpage précède tout prétraitement ; encodage et imputation vivent dans la pipeline,
   réajustés à chaque pli.
3. Deux tests qui échouent si la propriété est perdue : permutation de la cible puis
   recalcul des dix variables créées, et recalcul des quatre agrégats sur le seul jeu
   d'apprentissage. Plus huit contrôles sur le modèle livré, à l'étape 7.

**« Votre R² de 0,55 n'est pas très élevé. »**
Non, et c'est attendu. Les variables les plus corrélées à la cible sont précisément celles
qu'il fallait exclure : les garder aurait donné un R² flatteur et un modèle inutilisable. Le
plafond réaliste est donc bas. Le bon repère n'est pas 1, c'est la référence naïve : 36 %
d'erreur en moins. Les 46 % de variance inexpliquée tiennent en partie au marché local de
l'emploi, absent des données.

**« Le jeu de test a-t-il servi une seule fois ? »**
Oui. L'étape 4 le supprime de la mémoire dès sa première cellule, l'étape 5 ne l'ouvre qu'à
la section 3, après le choix définitif. Toute l'optimisation, y compris la comparaison avec
le gradient boosting, s'est tenue en validation croisée sur l'apprentissage.

### Sur le modèle

**« Pourquoi la forêt aléatoire ? »**
Six modèles comparés sur les mêmes plis. La forêt et le gradient boosting arrivent à
égalité, 9,495 contre 9,518, pour un écart-type entre plis de 0,147 : l'écart est six fois
plus petit que le bruit. La forêt a été retenue sur sa stabilité, pas sur une troisième
décimale.

**« Et si on optimisait le boosting ? »**
C'est fait, à l'étape 5b, chacun avec sa propre grille. Le boosting passe alors devant :
9,241 contre 9,439 de MAE, et il gagne 13 des 14 découpages. La forêt est **quand même
conservée**, pour trois raisons : elle détient le seul score jamais mesuré sur le jeu de test,
rouvrir ce jeu coûterait plus que les 2 % de gain, et les deux modèles se ressemblent
énormément (prédictions corrélées à 0,953, divergentes de plus de 10 points sur 2,4 % des
cas). Le coût de ce choix est écrit dans le document d'étape.

**« Pourquoi pas un modèle linéaire, plus simple à expliquer ? »**
Il a été testé : 10,41 de MAE contre 9,50, soit près d'un point de plus. L'écart se paie en
interprétabilité, et le projet compense par l'importance des variables, mesurée par deux
méthodes.

**« Quels hyperparamètres avez-vous explorés ? »**
`min_samples_leaf` est le levier dominant : 0,700 point de RMSE d'amplitude, contre 0,244
pour `max_features`. Le nombre d'arbres n'en est pas un, la courbe plafonne après 200. Et la
configuration retenue n'est pas la meilleure de la grille : la règle à un écart-type a été
appliquée, au prix de 0,073 point de MAE, pour un écart entraînement-validation ramené de
0,377 à 0,332.

### Sur les résultats

**« 90 % de vos formations de test sont dans l'entraînement. N'est-ce pas une fuite ? »**
Non, pas une fuite de cible : aucune valeur à prédire du test n'a servi à ajuster le modèle.
C'est un **biais de validation** : le score mesure surtout la capacité à prédire une nouvelle
promotion d'une formation déjà connue. Il est chiffré : 9,39 points d'erreur sur les
formations déjà vues, 11,28 sur les inconnues, soit 1,89 point de surcoût. Et la validation
temporelle, entraînée sur 2019-2022 et testée sur 2023-2024, donne un R² de 0,458 au lieu de
0,554.

**« Votre modèle est-il utilisable en production ? »**
Pour situer une formation face à ses comparables, oui. Pour décider d'un financement ou
d'une fermeture, non : l'erreur moyenne dépasse 9 points et double sur les formations de
moins de 25 sortants, donc elle est du même ordre que les écarts qu'on voudrait arbitrer.
C'est écrit dans la fiche modèle, avec trois autres usages écartés.

**« Qu'est-ce qui vous a le plus surpris ? »**
L'écart entre femmes et hommes **change de signe** selon la façon de comparer. En brut, les
hommes sont devant de 2,84 points. À diplôme, établissement et promotion identiques, sur les
4 026 formations où les deux sont publiés, les femmes repassent devant de 2,38 points, et
elles sont mieux insérées dans 58,8 % des formations comparées. L'écart brut mesure
l'orientation, pas l'insertion. À dire aussi : ces variables ne sont pas dans le modèle,
il ne peut donc rien affirmer sur ces disparités.

**« Vos résultats sont-ils reproductibles ? »**
`random_state=42` partout, chaîne exécutable de bout en bout, et le modèle rechargé
reproduit ses prédictions. Une nuance mesurée : deux appels successifs diffèrent de 2×10⁻¹⁴,
parce que la forêt somme ses arbres en parallèle et que l'addition flottante n'est pas
associative. Quinze ordres de grandeur sous la précision de la cible.

### Sur les données

**« Pourquoi 17 065 lignes sur 1 036 781 ? »**
Le fichier mêle le détail et ses agrégats. Retenir les formations d'une promotion simple,
hors marges géographiques et disciplinaires, hors ventilations démographiques, donne des
lignes comparables entre elles et supprime le double comptage. Chaque filtre est chiffré
dans l'entonnoir d'extraction.

**« Votre seconde source sert-elle à quelque chose ? »**
Elle apporte le clivage public / privé, invisible dans InserSup : 4,5 points d'écart. Mais
testée dans le modèle, elle ne gagne que 0,020 point de MAE, six fois moins que le bruit
entre plis. Elle n'a donc pas été retenue, et ce résultat négatif est reporté plutôt que
masqué.

---

## 3. Trois pièges à éviter

1. **Annoncer un score sans son repère.** Jamais « R² de 0,55 » seul, toujours « contre une
   référence naïve qui fait 15,07 de MAE ».
2. **Dire « accuracy ».** Le mot n'a pas de sens ici, et l'employer suggère qu'on n'a pas vu
   la différence entre régression et classification.
3. **Défendre un choix qu'on n'a pas fait.** Si une question porte sur un point non traité,
   le dire, et enchaîner sur ce qui a été mesuré. Un « je ne l'ai pas testé » assumé coûte
   moins qu'une improvisation.

---

## Checklist de la phase 9

- [x] Support prêt : 10 diapositives, avec notes d'orateur
- [x] Minutage établi, avec une marge sur les 7 minutes
- [x] Limites annoncées **proactivement**, diapositive dédiée
- [x] Questions probables anticipées, avec réponses chiffrées
- [ ] **Répétition à voix haute, chronométrée** : reste à faire, et ne peut pas être délégué
- [ ] Vérifier que le PDF s'ouvre sur la machine de présentation
