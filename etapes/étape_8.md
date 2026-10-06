# Étape 8 - Documentation et reproductibilité

## Objectif

Un projet d'analyse qui ne se rejoue pas n'est pas un résultat, c'est une anecdote. Cette
étape ne produit pas de nouvelle analyse : elle rassemble les livrables, écrit la procédure
de reprise, et vérifie que la chaîne complète tourne encore de bout en bout.

---

## 1. Les livrables

| Livrable | Fichier | Produit par |
|---|---|---|
| Jeu final nettoyé et enrichi | `csv/dataset_phase3_final.csv`, 17 065 × 28 | Étape 3 |
| Dictionnaire de données | [`DATA_DICTIONARY.md`](../DATA_DICTIONARY.md), 28 colonnes + 3 variables de pipeline | Étape 3, **généré** depuis le DataFrame |
| Protocole commun (variables, découpage, pipeline) | [`modeles/protocole.py`](../modeles/protocole.py) | Rédigé, importé par les étapes 3 à 7 |
| Choix du modèle | `modeles/choix_modele.json` | Étape 5b |
| Modèle entraîné, pipeline complète | `modeles/modele_final.joblib`, 0,26 Mo | Étape 5c |
| Code d'inférence | [`modeles/inference.py`](../modeles/inference.py) | Rédigé, testé à l'étape 7 |
| Fiche modèle | [`MODEL_CARD.md`](../MODEL_CARD.md) | Étape 7, **générée** depuis le modèle chargé |
| Figures | `figures_eda/`, 18 fichiers | Étapes 2, 4, 5, 5b, 5c, 6 |
| Récit visuel | [`Rapport_Visualisation.md`](../Rapport_Visualisation.md) | Étape 6 |
| Journaux | `csv/nettoyage_log.json`, `csv/entonnoir_extraction.json` | Étapes 1 et 3 |
| Documents d'étape | `etapes/`, 13 fichiers | Rédigés |

**Trois de ces livrables sont générés, pas rédigés** : le dictionnaire de données depuis le
DataFrame, la fiche modèle depuis le `.joblib`, et le support de soutenance depuis les
figures. Ils ne peuvent donc pas décrire autre chose que ce qui existe réellement, et un
`assert` échoue si une colonne n'est pas documentée.

---

## 2. Reproduire le projet de zéro

**Prérequis** : Python 3.12, un environnement contenant pandas, scikit-learn, matplotlib,
joblib et jupyter. Les versions utilisées ici sont pandas 3.0.3 et scikit-learn 1.9.0.

```bash
unzip csv.zip -d csv/          # les données ne sont pas versionnées
cd notebooks
jupyter nbconvert --to notebook --execute --inplace etape_1_extraction.ipynb
# puis 2, 3, 4, 5, 5b, 5c, 6, 7 dans cet ordre
```

L'ordre n'est pas indifférent : chaque notebook consomme ce que le précédent a écrit. Les
étape 5c lit le choix de l'étape 5b, les étapes 6 et 7 lisent le modèle sauvegardé par
l'étape 5c.

### Temps mesurés

Chaîne complète rejouée après la révision du protocole, sur un portable, environnement déjà
installé et données décompressées :

| Notebook | Temps | Ce qui coûte |
|---|---:|---|
| `etape_1_extraction` | 8 s | Cache actif ; environ 4 min si l'extraction est forcée |
| `etape_2_eda` | 13 s | Lecture du jeu analytique |
| `etape_3_preparation` | 4 s | Nettoyage et feature engineering |
| `etape_4_modelisation` | 2 min 16 | Six modèles en validation croisée groupée |
| `etape_5_optimisation_erreurs` | 2 min 42 | `GridSearchCV` de la forêt |
| `etape_5b_duel_foret_boosting` | 7 min 08 | Deux grilles complètes, 34 configurations |
| `etape_5c_evaluation_finale` | 25 s | Diagnostic hors pli, test, livraison |
| `etape_6_visualisation` | 5 s | Vue d'ensemble |
| `etape_7_synthese_modele` | 5 s | Contrôles et fiche modèle |
| **Total** | **13 min 06** | |

**Les livrables sont régénérés à l'identique.** Après cette exécution complète, les sommes
de contrôle du jeu final, du dictionnaire de données et du modèle `.joblib` sont inchangées.
Le modèle est donc reproductible au bit près, entraînement compris, et non seulement
« équivalent ».

### Ce que cette exécution a révélé

Le premier passage a **échoué à l'étape 6**, et c'est le contrôle d'inventaire qui l'a
arrêté : l'étape 5b avait produit `fig18_duel_foret_boosting.png` après la rédaction du
notebook 6, et cette figure n'apparaissait dans aucun récit. L'`assert` prévu pour ce cas a
fait exactement ce qu'on attendait de lui.

C'est l'illustration de la différence défendue plus bas : une documentation aurait continué
d'annoncer 17 figures sans que personne ne s'en aperçoive ; un test a bloqué la chaîne
jusqu'à ce que la figure soit intégrée au récit.

---

## 3. Ce qui rend le projet reproductible

**Le hasard est fixé partout.** `random_state=42` sur le découpage, la validation croisée et
tous les modèles. Le découpage, groupé par formation, est défini une seule fois dans
`modeles/protocole.py` et reproduit à l'identique par toutes les étapes.

**L'extraction est mise en cache.** L'étape 1 ne relit les 738 Mo du fichier brut que si les
jeux dérivés sont absents, ou si `FORCE_EXTRACTION` est activé. Rejouer la chaîne ne coûte
donc pas une relecture complète, mais l'extraction reste rejouable à l'identique.

**Les contrôles sont exécutables.** Le projet ne se contente pas d'affirmer ses propriétés :
il les teste, et ces tests échouent si la propriété est perdue.

| Contrôle | Où | Ce qu'il protège |
|---|---|---|
| Permutation de la cible sur les 9 variables créées | Étape 3 | Aucune variable ne dérive de `y` |
| Isolement du transformateur d'agrégats, dans les deux sens | Étape 3 | Le test n'influence pas l'apprentissage |
| Périmètre et disjonction des formations | Étape 3 | Pas de cible ni d'identifiant transmis au modèle |
| Inventaire des figures et couverture des questions | Étape 6 | Aucune figure orpheline |
| Identité entre inférence et pipeline | Étapes 5c et 7 | Aucun écart entre entraînement et inférence |
| 10 contrôles de conformité, dont la lecture unique du test | Étape 7 | Le livrable et le protocole restent conformes |
| Non-régression du module d'inférence | Étape 7 | La démonstration se reproduit |

**Ce que la révision a montré.** Après la refonte du protocole, la chaîne a été rejouée de
bout en bout : les neuf notebooks passent, et le modèle livré est identique au bit près
d'une exécution à l'autre. La première version comportait une limite de reproductibilité,
la forêt sommant ses arbres en parallèle avec un écart d'environ 2×10⁻¹⁴ ; le gradient
boosting retenu n'a pas ce comportement, et l'écart mesuré entre inférence et pipeline est
nul.

---

## 4. Ce qui n'est pas versionné, et pourquoi

| Exclu | Poids | Raison |
|---|---:|---|
| `csv/` | ~940 Mo | Deux fichiers dépassent la limite de 100 Mo par fichier de GitHub |
| `presentation/` | 410 Ko | Choix de projet |

Les données sont distribuées par `csv.zip` (51 Mo) à la racine, dont le contenu est décrit
dans le [README](../README.md). Tout se régénère par une exécution des notebooks, sauf le
fichier brut, qui se retélécharge depuis le portail InserSup.

---

## 5. Maintenance : un nouveau millésime InserSup

1. Remplacer `csv/dataset.csv` par le nouvel export et supprimer les jeux dérivés, ou
   activer `FORCE_EXTRACTION` à l'étape 1.
2. Mettre à jour `MILLESIME` à l'étape 3, qui sert au calcul de l'ancienneté de promotion.
3. Rejouer la chaîne dans l'ordre.
4. Surveiller les points qui bougeront : la couverture de la cible, le périmètre après
   entonnoir, et la part de clés inconnues des agrégats de contexte.

Les contrôles anti-fuite et les dix contrôles de conformité échouent si le nouveau millésime
introduit une colonne problématique. C'est le but : la reprise doit casser bruyamment plutôt
que produire un modèle discrètement faux.

---

## Checklist de la phase 8

- [x] Dataset final exporté
- [x] Data Dictionary complet, généré depuis les données
- [x] Notebooks structurés, commentés, exécutables en une passe
- [x] Pipeline complète sauvegardée en `.joblib`, agrégats compris, avec ses métriques
- [x] Démonstration de prédiction sur de nouvelles données brutes, modalité inconnue comprise
- [x] Procédure de reprise écrite et chronométrée
- [x] Fiche modèle et code d'inférence livrés avec le modèle

---

## Utilisation de l'IA sur cette étape

| Prompt utilisé | Ce que l'IA a produit | Vérification effectuée |
|---|---|---|
| « Comment rendre un projet d'analyse reproductible ? » | Liste classique : graines fixées, versions, ordre d'exécution | Retenue, mais complétée par ce qui manquait : des contrôles qui **échouent**, plutôt qu'une documentation qui affirme |
| « Faut-il versionner les données d'un projet ? » | Non au-delà de quelques Mo, oui pour un échantillon | Tranché par la mesure : 940 Mo décompressés, deux fichiers au-dessus de la limite de GitHub, d'où l'archive |

Le premier échange a produit la distinction utile de cette étape : une documentation décrit
un état passé, un test protège un état présent. Le projet a les deux, et les sépare.
