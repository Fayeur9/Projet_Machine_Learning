# Étape 6 - Visualisation et storytelling

## Objectif

Rendre lisible par un tiers ce que les étapes 2 à 5 ont établi. La phase ne demande pas
de nouveaux calculs : elle demande que les figures existent, qu'elles soient correctes,
qu'elles se tiennent entre elles, et qu'elles racontent quelque chose.

Notebook : [`etape_6_visualisation.ipynb`](../notebooks/etape_6_visualisation.ipynb)
Récit complet : [`Rapport_Visualisation.md`](../Rapport_Visualisation.md)

---

## 1. Pourquoi cette étape ne retrace rien

Les seize premières figures sont produites dans les notebooks des étapes 2, 4 et 5, là où
les données sont déjà chargées, nettoyées et où le modèle est en mémoire. Les retracer ici
imposerait de tout recharger pour un résultat identique.

Cette étape fait donc les trois choses qu'aucune autre ne peut faire, parce qu'elles
supposent de regarder l'ensemble :

1. **justifier les choix de graphiques**, y compris les types écartés ;
2. **contrôler l'inventaire** par des `assert`, plutôt que de le déclarer ;
3. **produire la vue d'ensemble**, la seule figure qui a besoin des données *et* du modèle.

---

## 2. Choix des types de graphiques

| Question | Type retenu | Pourquoi pas un autre |
|---|---|---|
| Répartition de la cible | Histogramme + boîte | La forme et les extrêmes sont deux questions distinctes |
| Comparaison entre catégories nommées | Barres horizontales triées | Libellés longs lisibles sans rotation ; un camembert ferait comparer des angles |
| Comparaison de distributions | Boîtes à moustaches | La dispersion est le message : deux domaines de même moyenne diffèrent par l'étalement |
| Évolution dans le temps | Courbes + bande | La continuité fait voir un mouvement là où des barres montreraient six valeurs isolées |
| Liens entre variables | Heatmap divergente | Toutes les paires d'un coup, le signe lisible avant l'intensité |
| Comparaison de modèles | Barres + barres d'erreur | Sans les barres d'erreur, 9,49 contre 9,52 passerait pour un écart réel |

**Écartés volontairement** : aucun camembert (toutes les répartitions dépassent cinq
catégories), aucune 3D (elle déforme les proportions sans rien ajouter).

**Cas limite assumé** : la figure des établissements ne montre que les dix premiers et les
dix derniers. Tronquer un classement se défend ici parce que la figure sert à montrer une
amplitude, pas à classer 365 établissements, et le texte le précise.

---

## 3. Inventaire

**17 figures, 8 types de graphiques distincts**, pour un seuil d'excellence fixé à 7 par la
grille. Le notebook vérifie par `assert` que chaque fichier existe, qu'aucune figure
produite n'a été oubliée du récit, et que les cinq questions business ont chacune la leur.

| Rattachement | Figures |
|---|---|
| Qualité des données | `fig01`, `fig03` |
| Cadrage | `fig02` |
| Q1 à Q5 | `fig04` à `fig09` |
| Décisions de modélisation | `fig10`, `fig11` |
| Modélisation et évaluation | `fig12` à `fig16` |
| Vue d'ensemble | `fig17` |

---

## 4. Le fil narratif

Cinq actes, chacun ouvrant sur la question du suivant :

1. **Ces données sont-elles exploitables ?** Oui : cible complète, manquants datés et
   expliqués, distribution unimodale qui appelle une régression.
2. **Qu'est-ce qui sépare une formation d'une autre ?** La vocation du diplôme (46 points
   d'écart) et le secteur disciplinaire, deux fois plus discriminant que le domaine.
3. **Deux résultats contre-intuitifs.** L'écart femmes/hommes change de signe une fois la
   comparaison appariée ; le creux de 2020 frappe les quatre domaines simultanément.
4. **Que refuser de donner au modèle ?** Les mesures postérieures à six mois, précisément
   les plus corrélées à la cible.
5. **Que vaut le modèle, et où échoue-t-il ?** 36 % d'erreur en moins que la référence
   naïve, mais une erreur qui double sur les petites formations.

Le développement figure par figure, avec les chiffres et les transitions, est dans
[`Rapport_Visualisation.md`](../Rapport_Visualisation.md).

---

## 5. La vue d'ensemble

![Vue d'ensemble](../figures_eda/fig17_vue_ensemble.png)

Quatre panneaux, un par étape du raisonnement : l'objet à prédire, le facteur dominant, le
contexte temporel, et ce que le modèle retient.

Le point à souligner est la correspondance entre les panneaux (b) et (d) : le facteur que
l'analyse exploratoire avait identifié comme dominant est aussi celui que le modèle utilise
le plus. L'analyse et le modèle racontent la même histoire, et c'est ce qui rend le résultat
crédible.

Les métriques affichées sont **lues dans le modèle sauvegardé**, jamais recalculées : le jeu
de test n'a été ouvert qu'une fois, à l'étape 5.

---

## 6. Conventions graphiques

Une même charte dans les quatre notebooks producteurs, ce qui rend les figures
reconnaissables comme appartenant au même projet :

- **Titres porteurs de message** : « L'écart entre types de diplôme atteint 46 points »
  plutôt que « Taux par type de diplôme ». Qui ne lit que les titres suit déjà le récit.
- **Palette** : bleu `#2f6f9f` pour la série principale, orange `#d1793c` pour l'élément
  mis en avant, gris `#9aa5ad` pour les repères.
- **Axes** labellisés avec unités, **jamais tronqués** sur une échelle de taux.
- **Source et période** apposées sur chaque figure exportée, par la fonction
  `annoter_source()` : une figure finit toujours par circuler seule.
- **Export** en 150 ppp, cadrage serré.

---

## Checklist

- [x] Au moins 7 visualisations produites : **17**, de 8 types distincts
- [x] Chaque question business a sa figure, vérifié par `assert`
- [x] Une vue d'ensemble existe : `fig17_vue_ensemble.png`
- [x] Titres clairs et porteurs de message
- [x] Axes labellisés avec unités
- [x] Sources et périodes indiquées sur chaque figure
- [x] Aucune mauvaise pratique : ni 3D, ni camembert, ni axe de taux tronqué
- [x] Cohérence visuelle entre les quatre notebooks
- [x] Un fil narratif relie les visualisations
- [x] L'audience peut comprendre sans explication orale
- [x] Choix des types justifiés, y compris ceux écartés

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Quel graphique pour comparer une distribution entre quatre groupes ? » | Boîte à moustaches plutôt que barres de moyennes | Retenu après avoir constaté que deux domaines de moyennes proches ont des dispersions différentes |
| « Relis mes titres de figures » | Réécriture des titres descriptifs en titres d'insight | Chaque titre revérifié contre le chiffre de sa figure, pour qu'aucun n'annonce plus que ce qui est montré |
| « Comment signaler la source sur une figure matplotlib ? » | `figure.text` en coordonnées figure | Testé, puis vérifié qu'avec `bbox_inches='tight'` la mention n'est pas rognée à l'export |
| « Construis-moi un dashboard des résultats » | Proposition à six panneaux, dont deux redondants | Refusée en l'état, ramenée à quatre panneaux, un par étape du raisonnement |

Le point utile a été le dernier : la première proposition remplissait l'espace au lieu de
servir le propos. Quatre panneaux qui se répondent valent mieux que six qui se répètent.
