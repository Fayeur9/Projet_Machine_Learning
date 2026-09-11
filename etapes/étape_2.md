# Étape 2 - Diagnostic qualité et EDA analytique

## Objectif

Deux temps distincts, réunis dans un même notebook :
[`Projet/notebooks/etape_2_eda.ipynb`](../notebooks/etape_2_eda.ipynb).

1. **Diagnostic qualité** : analyser les cinq dimensions attendues, puis prioriser les
   problèmes trouvés dans un rapport unique servant de cahier des charges à l'étape 3.
2. **EDA analytique** : répondre aux cinq questions business du cadrage et mesurer le
   lien entre les variables et la cible.

Jeux analysés : `csv/dataset_phase1_modelisation.csv` (17 065 × 23) et, pour la question
business 3 seulement, `csv/dataset_phase1_analytique.csv` (438 696 × 32).

---

# Partie A - Diagnostic qualité

## A1. Complétude

21 colonnes sur 23 sont complètes à 100 %. Les deux seules colonnes incomplètes sont les
taux d'emploi salarié à 24 et 30 mois, remplies à 82,76 % (2 942 valeurs manquantes
chacune).

Le trou n'est pas aléatoire : il est entièrement expliqué par la dimension fraîcheur
(section A5). La cible est complète sur les 17 065 lignes.

## A2. Unicité

Aucun doublon de ligne complète. Cinq clés candidates ont été testées :

| Clé candidate | Colonnes | Lignes en trop | Lignes impliquées | Unique |
|---|---:|---:|---:|---|
| Nom établissement + libellé + promotion | 3 | 758 | 1 487 | Non |
| Clé métier complète, sur le nom établissement | 7 | 144 | 261 | Non |
| Clé métier complète, sur le code UAI | 7 | 107 | 201 | Non |
| Code UAI + promotion | 2 | 15 285 | 16 277 | Non |
| Code SISE + promotion | 2 | 11 371 | 13 106 | Non |
| **Code UAI + code SISE + promotion** | **3** | **0** | **0** | **Oui** |

Le tableau se lit comme une démonstration en trois temps. Remplacer le **nom
d'établissement** par son **code UAI**, à dimensions identiques, fait tomber les conflits de
144 à 107 : une partie des collisions ne venait pas des diplômes mais des établissements
homonymes. Même avec le code UAI, 107 conflits subsistent : deux formations distinctes
peuvent porter le même libellé de diplôme. Remplacer le libellé par le **code SISE** les
élimine tous.

La cause de l'échec des clés fondées sur les libellés est que **les libellés ne sont pas
des identifiants** :

- 1 290 libellés de diplôme pour 1 408 codes SISE : 91 libellés sont portés par plusieurs
  codes, jusqu'à 6 pour `SCIENCES HUMAINES ET SOCIALES : PSYCHOLOGIE` ;
- 329 noms d'établissement pour 365 codes UAI : 29 noms sont des homonymes.

Chacune des trois colonnes de la clé retenue est nécessaire : un établissement propose
plusieurs diplômes, un diplôme est proposé par plusieurs établissements, et une formation
est publiée sur six promotions.

## A3. Cohérence

Le fichier publie à la fois des effectifs et des taux : chaque taux doit se recalculer à
partir des effectifs. C'est le contrôle le plus discriminant du jeu.

| Contrôle | Lignes en défaut |
|---|---:|
| Taux hors du domaine [0, 100] | 0 |
| Effectifs négatifs | 0 |
| Effectif sous le seuil de publication (20) | 0 |
| Nombre en emploi salarié déduit non entier | 190 |
| Taux d'emploi stable non reconstituable (écart > 0,05 pt) | **11** |
| Taux d'emploi non salarié non reconstituable | 0 |
| Emploi stable supérieur à l'emploi salarié | 0 |

Les 190 lignes au nombre non entier viennent de l'arrondi du taux publié à deux décimales,
pas d'une incohérence de la source. Les **11 lignes** où le taux d'emploi stable contredit
les effectifs sont, elles, de vraies anomalies : elles sont traitées à l'étape 3.

Cohérence temporelle des horizons :

| Horizon | Observations | Taux en baisse | Gain moyen |
|---|---:|---:|---:|
| 6 → 12 mois | 17 065 | 11,0 % | +9,75 pt |
| 12 → 18 mois | 17 065 | 33,1 % | +1,38 pt |
| 18 → 24 mois | 14 123 | 20,2 % | +2,88 pt |
| 24 → 30 mois | 14 123 | 40,3 % | −1,27 pt |

L'insertion progresse fortement entre 6 et 12 mois, puis se stabilise.

## A4. Exactitude

Distribution de la cible : moyenne 55,89 · médiane 56,10 · écart-type 18,47 · Q1 43,24 ·
Q3 69,23 · min 0 · max 100.

La règle de l'écart interquartile donne les bornes [4,26 ; 108,22]. La borne haute
dépassant le maximum possible, **seule la queue basse est signalée** : 31 formations, soit
0,18 % du jeu. Leur effectif médian est de 27 sortants contre 37 pour le reste du jeu.

15 lignes portent une cible exactement à 0, 29 exactement à 100. Sur un effectif de 20
sortants, ces valeurs sont réelles. **Aucune suppression n'est effectuée** : retirer ces
lignes reviendrait à écarter les cas les plus difficiles et à surestimer la performance du
modèle.

## A5. Fraîcheur

Millésime de diffusion `2026_S1`, promotions 2019 à 2024.

| Promotion | Lignes | Cible | Taux 12 mois | Taux 24 mois | Taux 30 mois |
|---|---:|---:|---:|---:|---:|
| 2019 | 2 657 | 100 % | 100 % | 100 % | 100 % |
| 2020 | 2 710 | 100 % | 100 % | 100 % | 100 % |
| 2021 | 2 933 | 100 % | 100 % | 100 % | 100 % |
| 2022 | 2 958 | 100 % | 100 % | 100 % | 100 % |
| 2023 | 2 865 | 100 % | 100 % | 100 % | 100 % |
| **2024** | **2 942** | 100 % | 100 % | **0 %** | **0 %** |

La promotion 2024 est la seule à n'avoir aucun taux à 24 et 30 mois : elle n'a pas atteint
cet horizon au moment de la diffusion. Ses 2 942 lignes correspondent exactement aux 2 942
valeurs manquantes de la section A1. Imputer ces valeurs reviendrait à inventer un futur
non observé.

## A6. Rapport de qualité priorisé

| Dimension | Problème | Ampleur | Gravité | Décision |
|---|---|---|---|---|
| Fraîcheur | Taux à 24 et 30 mois absents pour la promotion 2024 | 2 942 lignes | Bloquante | Exclure : mesure postérieure à la cible |
| Cohérence | Horizons 12 et 18 mois corrélés à la cible | r = 0,85 et 0,79 | Bloquante | Exclure : fuite de cible |
| Cohérence | Emploi stable et non salarié mesurés à 6 mois | 2 colonnes | Bloquante | Exclure : même horizon que la cible |
| Unicité | Libellés ambigus | 107 lignes en trop | Majeure | Résolue par la clé UAI × SISE × Promotion |
| Complétude | Cardinalité forte (1 290 libellés, 329 établissements) | 3 colonnes | Majeure | Écarter du modèle ; exploiter par variables dérivées |
| Cohérence | Taux d'emploi stable non reconstituable | 11 lignes | Mineure | Neutraliser à l'étape 3 |
| Exactitude | Cible à 0 ou 100 sur de petits effectifs | 44 lignes | Mineure | Conserver : valeurs réelles |
| Exactitude | Redondance `Promotion` / `promotion_debut` | 2 colonnes | Mineure | Supprimer au nettoyage |
| Complétude | Seuil de publication à 20 sortants | Structurel | Non corrigeable | Documenter comme biais de sélection |

---

# Partie B - EDA analytique

## Q1. Quels types de formations ont les meilleurs taux d'insertion ?

Sur les 9 types de diplôme comptant au moins 100 formations :

| Type de diplôme | Formations | Moyenne | Médiane |
|---|---:|---:|---:|
| Master MEEF | 458 | 80,68 | 85,22 |
| Licence professionnelle | 1 978 | 71,20 | 74,41 |
| Diplôme d'ingénieurs | 2 633 | 62,12 | 63,27 |
| Bachelor universitaire de technologie | 217 | 61,85 | 62,50 |
| Master LMD | 8 388 | 53,21 | 53,57 |
| Diplôme visé niveau bac + 5 grade master | 686 | 46,91 | 48,36 |
| Licence générale | 2 332 | 45,88 | 45,11 |
| Diplôme visé bac + 3 ou bac + 4 grade licence | 131 | 37,47 | 28,57 |
| Diplôme visé niveau bac + 3 | 134 | 34,61 | 33,33 |

**Écart de 46,1 points** entre le premier et le dernier, soit 2,5 fois l'écart-type de la
cible. Le classement oppose deux logiques : les diplômes qui mènent directement à un métier
en tête, ceux qui mènent à une poursuite d'études en queue. Un étudiant qui poursuit ses
études n'est pas en emploi salarié et fait mécaniquement baisser le taux.

**Ce que cela ne dit pas** : les publics, disciplines et territoires diffèrent d'un type de
diplôme à l'autre. Rien ici n'établit de causalité.

## Q2. Différences selon le domaine, la discipline ou l'établissement ?

| Domaine disciplinaire | Formations | Moyenne | Médiane |
|---|---:|---:|---:|
| Sciences, technologies, santé | 7 091 | 59,75 | 60,71 |
| Sciences humaines et sociales | 2 741 | 57,82 | 57,14 |
| Droit, économie, gestion | 5 553 | 54,40 | 54,98 |
| Lettres, langues et arts | 1 680 | 41,38 | 40,97 |

Écart entre domaines : **18,4 points**. Mais sur les 31 secteurs disciplinaires d'au moins
100 formations, l'amplitude atteint **37,2 points**, plus du double. Les trois meilleurs
secteurs sont Sciences de l'éducation, Génie civil et Génie des procédés ; les trois
derniers, Pluridisciplinaire lettres/langues/SHS, Sciences politiques et Langues et
littératures étrangères.

**Conséquence directe pour la modélisation** : agréger au niveau du domaine écrase la
moitié du signal disciplinaire. Le modèle doit recevoir le secteur.

Entre établissements d'au moins 30 formations publiées, l'amplitude est de 41,6 points,
pour un écart-type des moyennes de 8,0 points. Cet écart reste à interpréter avec
prudence : un établissement spécialisé hérite de la performance de son secteur.

## Q3. Genre, nationalité, régime d'inscription

Traitée sur le jeu analytique, en ne faisant varier qu'une dimension à la fois. Périmètre
comparable : 72 970 lignes (promotion simple, hors marges, diplômés).

| Dimension | Modalité | Lignes | Moyenne |
|---|---|---:|---:|
| Genre | ensemble | 17 065 | 55,89 |
| Genre | femme | 8 919 | 54,57 |
| Genre | homme | 7 393 | 57,40 |
| Nationalité | ensemble | 17 065 | 55,89 |
| Nationalité | français | 14 340 | 59,74 |
| Régime | ensemble | 17 065 | 55,89 |
| Régime | apprentissage | 3 793 | **66,57** |

### Découverte inattendue : les deux lectures du genre s'opposent

| Comparaison | Femmes | Hommes | Écart |
|---|---:|---:|---|
| Brute (formations non appariées) | 54,57 | 57,40 | −2,84 pt, en faveur des hommes |
| **Appariée** (4 026 formations où les deux sont publiés) | 55,37 | 52,99 | **+2,38 pt, en faveur des femmes** |

À formation, diplôme et promotion identiques, les femmes sont mieux insérées dans 58,8 %
des formations comparées. L'écart brut est un **effet de composition** : hommes et femmes
ne sont pas répartis de la même façon entre les disciplines, et les disciplines n'ont pas
le même débouché. L'écart brut mesure donc l'orientation, pas l'insertion.

L'apprentissage ressort à +10,7 points au-dessus de l'ensemble, ce qui est cohérent avec
l'idée qu'un contrat d'apprentissage débouche souvent sur une embauche.

**Limite forte** : ces trois variables ne sont pas dans le jeu de modélisation. Le modèle
construit aux étapes 4 et 5 ne peut donc rien dire sur d'éventuelles disparités.

## Q4. Quelles formations sont les plus fragiles ?

Sur 44 couples (type de diplôme × secteur disciplinaire) d'au moins 100 formations :

Les plus fragiles sur le taux d'emploi : Licence générale × Pluridisciplinaire sciences
économiques et gestion (35,76 %), Diplôme visé bac + 3 × Sciences de gestion (36,94 %),
Licence générale × Langues et littératures étrangères (39,91 %).

Les plus fragiles sur la stabilité de l'emploi : Master LMD × Histoire (26,27 % d'emploi
stable), Master LMD × Géographie (31,55 %), Diplôme visé bac + 5 × Génie civil (35,26 %).

La corrélation entre taux d'emploi et taux d'emploi stable n'est que de **0,466** : les
deux mesures ne se recouvrent pas. 22 couples sur 44 sont sous les deux moyennes.

## Q5. Évolution au fil des promotions

| Promotion | Lignes | Moyenne | Médiane | Écart-type |
|---|---:|---:|---:|---:|
| 2019 | 2 657 | 52,70 | 52,63 | 18,54 |
| 2020 | 2 710 | **48,20** | 46,43 | 18,87 |
| 2021 | 2 933 | 59,17 | 60,00 | 17,77 |
| 2022 | 2 958 | **61,60** | 62,16 | 17,56 |
| 2023 | 2 865 | 58,40 | 58,82 | 17,80 |
| 2024 | 2 942 | 54,39 | 54,38 | 17,09 |

Amplitude de **13,4 points** sur six promotions, avec un repli de 7,2 points entre 2022 et
2024. Le creux de 2020 et le rebond de 2021-2022 se retrouvent **dans les quatre domaines
simultanément** : un mouvement commun à des disciplines aussi différentes pointe vers une
cause extérieure aux formations, le marché du travail au moment de la sortie.

**Conséquence** : la promotion porte un effet de conjoncture et doit être fournie au
modèle. Mais un modèle entraîné sur 2019-2024 ne saura pas anticiper un choc inédit : la
validation temporelle de l'étape 5 le chiffre.

## B6. Lien entre les variables et la cible

Corrélations de Pearson avec la cible :

| Variable | r |
|---|---:|
| Taux d'emploi à 12 mois | 0,849 |
| Taux d'emploi à 18 mois | 0,794 |
| Taux d'emploi à 24 mois | 0,760 |
| Taux d'emploi à 30 mois | 0,743 |
| Taux d'emploi stable à 6 mois | 0,324 |
| **Nombre de poursuivants** | **−0,236** |
| Promotion | 0,105 |
| Nombre de sortants | 0,017 |

Les quatre premières sont la **zone de fuite de cible** : elles sont mesurées après
l'horizon à prédire.

Part de la variance de la cible expliquée par chaque variable catégorielle (eta²) :

| Variable | eta² |
|---|---:|
| Code du diplôme SISE | 0,543 |
| Libellé du diplôme | 0,525 |
| Type de diplôme | 0,233 |
| Secteur disciplinaire | 0,194 |
| Code UAI / Établissement | 0,194 / 0,191 |
| Discipline | 0,098 |
| Domaine disciplinaire | 0,083 |
| Académie | 0,076 |
| Région | 0,056 |

### Hypothèses formulées pour la modélisation

1. Le **rapport poursuivants / sortants** portera plus de signal que chacun des effectifs
   pris isolément : c'est une feature à construire à l'étape 3.
2. **Type de diplôme et secteur disciplinaire** domineront, loin devant la région. Le
   domaine n'explique que 0,083 contre 0,194 pour le secteur : fournir l'agrégat plutôt que
   le détail perdrait plus de la moitié du signal.
3. La **promotion** apportera un effet de niveau, pas une tendance.
4. L'erreur sera **plus forte sur les petits effectifs**, où la cible est plus bruitée
   (écart-type de 20,33 sur le premier quintile d'effectif contre 17,13 sur le quatrième).
5. Le plafond de performance sera modeste : un **$R^2$ autour de 0,5** est réaliste.

## B7. Le récit en cinq phrases

1. L'insertion à six mois se joue d'abord sur **ce qu'on étudie** : le secteur
   disciplinaire ouvre un écart deux fois plus large que le domaine.
2. Elle se joue ensuite sur **la vocation du diplôme** : les formations
   professionnalisantes insèrent nettement mieux, et l'apprentissage amplifie l'écart.
3. Elle se joue enfin sur **le moment de la sortie** : la promotion 2020 paie la crise
   sanitaire dans les quatre domaines à la fois.
4. L'écart entre femmes et hommes **change de signe** selon qu'on compare globalement ou à
   formation identique.
5. Les indicateurs mesurés après six mois sont fortement corrélés à la cible et **doivent
   être écartés**.

## B8. Décisions transmises à l'étape 3

1. Conserver la cible telle quelle, sans transformation ni suppression d'extrêmes.
2. Exclure les taux d'emploi à 12, 18, 24 et 30 mois.
3. Exclure les taux d'emploi stable et non salarié à 6 mois.
4. Supprimer `promotion_debut`.
5. Construire un ratio de poursuite et une mesure de taille de formation.
6. Fournir au modèle le secteur disciplinaire, pas seulement le domaine.
7. Ne calculer **aucun agrégat de la cible** hors de la pipeline.
8. Traiter les modalités à forte cardinalité par des variables dérivées.

---

## Figures produites

Onze figures dans `Projet/figures_eda/` :

| Fichier | Contenu |
|---|---|
| `fig01_completude.png` | Taux de remplissage des colonnes incomplètes |
| `fig02_distribution_cible.png` | Histogramme et boxplot de la cible |
| `fig03_fraicheur.png` | Couverture des horizons par promotion |
| `fig04_q1_type_diplome.png` | Taux moyen par type de diplôme |
| `fig05_q2_domaine.png` | Boxplot par domaine disciplinaire |
| `fig06_q2_etablissements.png` | Dix premiers et dix derniers établissements |
| `fig07_q3_genre.png` | Comparaison brute contre comparaison appariée |
| `fig08_q4_fragilite.png` | Insertion contre stabilité de l'emploi |
| `fig09_q5_promotions.png` | Trajectoire globale et par domaine |
| `fig10_correlations.png` | Matrice de corrélation numérique |
| `fig11_effectif_dispersion.png` | Dispersion de la cible selon l'effectif |

## Checklist

- [x] Complétude quantifiée colonne par colonne
- [x] Unicité testée sur cinq clés candidates, clé primaire identifiée
- [x] Cohérence interne vérifiée en recalculant les taux depuis les effectifs
- [x] Cohérence temporelle des horizons contrôlée
- [x] Exactitude : valeurs atypiques détectées, examinées et tranchées
- [x] Fraîcheur : mécanique des trous entièrement expliquée
- [x] Rapport de qualité priorisé produit
- [x] Les 5 questions business reçoivent une réponse chiffrée
- [x] Lien features / cible mesuré (Pearson et eta²)
- [x] Hypothèses formulées sur ce que le modèle devrait apprendre
- [x] 11 figures produites et enregistrées
