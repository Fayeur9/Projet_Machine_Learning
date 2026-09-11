# Dictionnaire de données

Jeu : `dataset_phase3_final.csv` · 17065 lignes × 32 colonnes

**Cible** : `6-Taux d'emploi salarié en France - 6 mois après le diplôme` (régression, taux en %)  
**Clé primaire** : `Code UAI de l'établissement × Code du diplôme SISE × Promotion` (unique, 0 conflit)  
**Source** : INSERSUP, millésime 2026_S1, ministère de l'Enseignement supérieur, Licence Ouverte Etalab

| Colonne | Type | Rôle | Manquants | Modalités | Exemple | Description |
|---|---|---|---:|---:|---|---|
| `Région` | str | Variable explicative | 0 | 19 | Pays de la Loire | Région administrative de l'établissement |
| `Académie` | str | Variable explicative | 0 | 32 | Nantes | Académie de rattachement de l'établissement |
| `Établissement` | str | Exclue du modèle | 0 | 329 | École de gestion et de commerce de Ven | Nom de l'établissement (non identifiant : 329 noms, 365 codes UAI) |
| `Type de diplôme` | str | Variable explicative | 0 | 11 | Diplôme visé niveau bac + 3 | Nature du diplôme délivré (11 modalités) |
| `Domaine disciplinaire` | str | Variable explicative | 0 | 4 | Droit, économie, gestion | Domaine disciplinaire (4 modalités, agrégat de la discipline) |
| `Discipline` | str | Variable explicative | 0 | 14 | Sciences économiques, gestion | Discipline (14 modalités) |
| `Secteur disciplinaire` | str | Variable explicative | 0 | 49 | Sciences de gestion | Secteur disciplinaire (49 modalités, niveau le plus fin) |
| `Libellé du diplôme` | str | Exclue du modèle | 0 | 1289 | DIPLOME DE L'ECOLE DE GESTION ET DE CO | Intitulé du diplôme (non identifiant : plusieurs codes SISE partagent un même libellé) |
| `Promotion` | int64 | Variable explicative | 0 | 6 | 2019 | Année de la promotion sortante (2019 à 2024) |
| `Code UAI de l'établissement` | str | Clé primaire | 0 | 365 | 0851465F | Identifiant national de l'établissement ; 1re partie de la clé primaire |
| `Code du diplôme SISE` | str | Clé primaire | 0 | 1408 | M000025 | Identifiant national du diplôme ; 2e partie de la clé primaire |
| `6-Nombre de sortants - 6 mois après le diplôme` | int64 | Variable explicative | 0 | 538 | 22 | Nombre de diplômés sortis de formation, mesuré 6 mois après le diplôme |
| `6-Nombre de poursuivants - 6 mois après le diplôme` | int64 | Variable explicative | 0 | 582 | 10 | Nombre de diplômés ayant poursuivi leurs études |
| `6-Taux d'emploi salarié en France - 6 mois après le diplôme` | float64 | Cible | 0 | 2833 | 90.91 | CIBLE : part des sortants en emploi salarié en France 6 mois après le diplôme (%) |
| `12-Taux d'emploi salarié en France - 12 mois après le diplôme` | float64 | Exclue du modèle | 0 | 2769 | 90.91 | Même mesure à 12 mois (exclue du modèle) |
| `18-Taux d'emploi salarié en France - 18 mois après le diplôme` | float64 | Exclue du modèle | 0 | 2750 | 90.91 | Même mesure à 18 mois (exclue du modèle) |
| `24-Taux d'emploi salarié en France - 24 mois après le diplôme` | float64 | Exclue du modèle | 2942 | 2438 | 95.45 | Même mesure à 24 mois (exclue, absente pour 2024) |
| `30-Taux d'emploi salarié en France - 30 mois après le diplôme` | float64 | Exclue du modèle | 2942 | 2461 | 77.27 | Même mesure à 30 mois (exclue, absente pour 2024) |
| `6-Nombre de sortants en emploi non salarié - 6 mois après le diplôme` | int64 | Exclue du modèle | 0 | 39 | 0 | Sortants en emploi non salarié (exclu du modèle) |
| `6-Taux de sortants en emploi non salarié - 6 mois après le diplôme` | float64 | Exclue du modèle | 0 | 574 | 0.0 | Part des sortants en emploi non salarié (exclue du modèle) |
| `6-Nombre de sortants en emploi stable - 6 mois après le diplôme` | int64 | Exclue du modèle | 0 | 357 | 6 | Sortants en emploi stable (CDI, fonctionnaire) parmi les salariés (exclu du modèle) |
| `6-Taux de sortants en emploi stable - 6 mois après le diplôme` | float64 | Exclue du modèle | 11 | 1798 | 30.0 | Part d'emploi stable parmi les salariés (exclue ; 11 valeurs neutralisées) |
| `anciennete_promotion` | int64 | Variable explicative | 0 | 6 | 7 | CRÉÉE · Années écoulées entre la promotion et le millésime 2026 |
| `promotion_choc_sanitaire` | int64 | Variable explicative | 0 | 2 | 0 | CRÉÉE · Vaut 1 pour la promotion 2020, sortie pendant la crise sanitaire |
| `est_diplome_professionnalisant` | int64 | Variable explicative | 0 | 2 | 0 | CRÉÉE · Vaut 1 pour licence pro, MEEF, ingénieur, BUT |
| `taille_formation` | int64 | Variable explicative | 0 | 790 | 32 | CRÉÉE · Sortants + poursuivants : effectif total de la promotion |
| `ratio_poursuite` | float64 | Variable explicative | 0 | 4335 | 0.3125 | CRÉÉE · Part de la promotion qui poursuit ses études (0 à 1) |
| `tranche_effectif` | str | Variable explicative | 0 | 4 | très petite (≤ 25) | CRÉÉE · Classe de taille de la formation, en quatre tranches |
| `taille_mediane_secteur` | float64 | Variable explicative | 0 | 28 | 40.0 | CRÉÉE · Nombre médian de sortants dans le secteur disciplinaire |
| `nb_formations_etablissement` | int64 | Variable explicative | 0 | 68 | 1 | CRÉÉE · Nombre de diplômes distincts offerts par l'établissement |
| `part_sortants_etablissement` | float64 | Variable explicative | 0 | 2397 | 1.0 | CRÉÉE · Part des sortants de l'établissement issus de cette formation |
| `nb_etablissements_par_diplome` | int64 | Variable explicative | 0 | 41 | 1 | CRÉÉE · Nombre d'établissements délivrant ce diplôme |

## Jointure vers une source externe

`Code UAI de l'établissement` est l'identifiant national des établissements : c'est la clé de jointure vers l'annuaire de l'éducation ou tout référentiel d'établissements.

## Généré automatiquement

Ce fichier est produit par `notebooks/etape_3_preparation.ipynb` à partir du jeu final : il ne peut pas être désynchronisé des données.