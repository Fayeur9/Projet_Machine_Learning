# Guide du Projet Final — Machine Learning

Bienvenue dans le guide méthodologique du **projet final** du cours de Machine Learning.

---

## Objectif

Vous choisissez **votre propre dataset** et vous menez un projet complet de bout en bout : nettoyage, analyse exploratoire, visualisation, puis **construction et évaluation d'un modèle de Machine Learning**.

Ce guide vous accompagne à chaque phase. Il n'y a pas d'autre cas pratique avant : ce projet **est** la mise en pratique du cours, et il **est** l'évaluation.

**Volume : 12 heures** — 8 h de travail encadré (Bloc 6) + 4 h de finalisation et soutenance (Bloc 8).

---

## Données : à décompresser avant de lancer les notebooks

Le dossier `csv/` pèse environ **940 Mo** décompressé : il n'est donc **pas versionné** (voir [.gitignore](.gitignore)). Toutes les données sont regroupées dans l'archive [`csv.zip`](csv.zip) (51 Mo), à la racine du dépôt. Décompressez-la dans `csv/` avant de lancer les notebooks, qui lisent tous depuis ce dossier :

```bash
unzip csv.zip -d csv/
```

L'archive contient les quatre CSV du pipeline, la seconde source en JSON, et les deux
journaux :

| Fichier | Lignes | Poids | Rôle |
|---|---:|---:|---|
| `dataset.csv` | 1 036 781 | 738 Mo | Export brut INSERSUP (millésime 2026_S1), tel que téléchargé |
| `dataset_phase1_analytique.csv` | 438 696 | 148 Mo | Après filtre « cible renseignée » : base des analyses par genre et par ventilation |
| `dataset_phase1_modelisation.csv` | 17 065 | 4,7 Mo | Périmètre de modélisation après l'entonnoir d'extraction complet |
| `dataset_phase3_final.csv` | 17 065 | 5,5 Mo | Jeu final nettoyé et enrichi (32 colonnes), utilisé pour l'entraînement |
| `referentiel_etablissements.json` | 245 | 805 Ko | Seconde source : référentiel des établissements, joint par `Code UAI` |
| `entonnoir_extraction.json` | · | 4 Ko | Effectifs à chaque étape du filtrage |
| `nettoyage_log.json` | · | 4 Ko | Journal des décisions de nettoyage |

Le référentiel se retélécharge tout seul depuis l'API si le fichier est absent : la
section 6 de [etape_1_extraction.ipynb](notebooks/etape_1_extraction.ipynb) le récupère au
besoin, et le notebook reste exécutable hors ligne tant que le fichier est là.

Les colonnes de `dataset_phase3_final.csv` sont documentées dans [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

---

## Structure du guide

Le projet est divisé en **10 phases** + des ressources complémentaires :

```
📁 Guide_Projet_Final/
│
├── 📄 README.md                          ← Vous êtes ici
│
├── 🎯 PHASES DU PROJET
│   ├── 00_Introduction_et_Cadrage.md     ← Choisir son dataset, sa cible, ses questions
│   ├── 01_Extraction_Multi_Sources.md    ← Charger les données
│   ├── 02_EDA_Diagnostique.md            ← Diagnostiquer la qualité
│   ├── 03_Nettoyage_Donnees.md           ← Nettoyer les problèmes
│   ├── 04_Transformation_Feature_Eng.md  ← Enrichir les données
│   ├── 05_EDA_Analytique.md              ← Analyser et répondre aux questions
│   ├── 06_Visualisation_Storytelling.md  ← Visualiser et raconter
│   ├── 07_Modelisation_ML.md             ← ⭐ Construire et évaluer le modèle
│   ├── 08_Chargement_Documentation.md    ← Exporter, documenter, sauvegarder
│   └── 09_Presentation_Soutenance.md     ← Livrables finaux et soutenance
│
└── 📚 RESSOURCES
    ├── Ressource_Workflow_ML_Complet.ipynb  ← ⭐ Le squelette de code à adapter
    ├── Demo_Prof_Titanic/                    ← Exemple déroulé en cours
    ├── Annexe_Idees_Sujets.md                ← Idées de sujets par domaine
    └── Grille_Evaluation.md                  ← Critères de notation détaillés
```

---

## Workflow visuel

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PHASE 0   │     │   PHASE 1   │     │   PHASE 2   │
│   Cadrage   │ ──▶ │  Extraction │ ──▶ │  Diagnostic │
│  + la CIBLE │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PHASE 3   │     │   PHASE 4   │     │   PHASE 5   │
│  Nettoyage  │ ──▶ │ Transforma- │ ──▶ │     EDA     │
│             │     │    tion     │     │  analytique │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌═════════════┐     ┌─────────────┐
│   PHASE 6   │     ║   PHASE 7   ║     │   PHASE 8   │
│ Visualisa-  │ ──▶ ║ MODÉLISATION║ ──▶ │  Documen-   │
│    tion     │     ║     ML      ║     │   tation    │
└─────────────┘     └═════════════┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐
│   PHASE 9   │
│ Soutenance  │
└─────────────┘
```

---

## Planning indicatif

| Bloc | Séance | Durée | Phases couvertes |
|---|---|---|---|
| **6** | 6.1 — Cadrage & validation des sujets | 2 h | Phases 0-1 |
| **6** | 6.2 — Nettoyage & feature engineering | 2 h | Phases 2-4 |
| **6** | 6.3 — EDA analytique & visualisation | 2 h | Phases 5-6 |
| **6** | 6.4 — Modélisation encadrée | 2 h | Phase 7 |
| **8** | 8.1 — Finalisation en autonomie | 2 h | Phases 7-8 |
| **8** | 8.2 — Soutenances notées | 2 h | Phase 9 |

Les 8 h du Bloc 6 sont **encadrées** : le formateur passe de groupe en groupe. Les 4 h du Bloc 8 sont en **autonomie**, puis notées.

---

## Choisir son dataset : critères obligatoires

Votre sujet doit être **validé par le formateur** à la fin de la première heure. Sans validation, on ne démarre pas la Phase 1.

| Critère | Seuil |
|---|---|
| Volume | ≥ 1 000 lignes |
| Colonnes exploitables | ≥ 8, dont au moins une catégorielle |
| Colonne cible | Identifiée et présente dans les données |
| Type de problème | Classification **ou** régression, tranché |
| Accessibilité | Données **déjà téléchargées** sur votre machine |

**Refusés d'office** : données à scraper depuis zéro, sources payantes, séries temporelles pures, images ou texte brut, dataset < 1 000 lignes.

Où chercher : Kaggle, data.gouv.fr, UCI ML Repository, Google Dataset Search. Voir [Annexe_Idees_Sujets.md](Annexe_Idees_Sujets.md).

---

## Comment utiliser ce guide

### 1. Cadrez avant de coder

Phase 0 d'abord. Un projet sans colonne cible identifiée n'est pas un projet de ML.

### 2. Avancez phase par phase

Chaque phase se termine par une checklist de validation. Ne passez à la suivante que si elle est cochée.

### 3. Le code de la Phase 7 vous est fourni

[`Ressource_Workflow_ML_Complet.ipynb`](Ressource_Workflow_ML_Complet.ipynb) contient tout le squelette : split, `ColumnTransformer`, `Pipeline`, `GridSearchCV`, évaluation, sauvegarde. **Trois zones seulement sont à adapter**, marquées `# <-- A ADAPTER`. Ce qui est évalué, ce n'est pas votre capacité à réécrire ce code, c'est votre capacité à l'adapter **et à l'expliquer**.

### 4. Utilisez l'IA — et vérifiez-la

Chaque phase contient des prompts prêts à l'emploi. Documentez ceux que vous utilisez. Attention : du code IA que vous ne savez pas expliquer en soutenance est **pénalisé**, pas valorisé.

### 5. Documentez au fur et à mesure

Ne remettez pas la documentation à la fin. Le notebook doit rester exécutable de bout en bout à tout moment.

---

## Chaque phase contient

- **Objectif** : ce que vous devez accomplir
- **Checklists** : actions à cocher au fur et à mesure
- **Templates** : documents à compléter
- **Prompts IA** : suggestions d'utilisation de l'IA générative
- **Questions de réflexion** : pour approfondir votre compréhension
- **Critères d'évaluation** : comment savoir si l'étape est réussie

---

## Livrables attendus

| Livrable | Format | Fichier produit | Vérifié |
|----------|--------|---|---------|
| Dataset final nettoyé | .csv | `csv/dataset_phase3_final.csv`, 17 065 × 32 | ☑ |
| Data Dictionary | .md | [DATA_DICTIONARY.md](DATA_DICTIONARY.md), 32 colonnes | ☑ |
| Notebooks documentés et exécutables | .ipynb | [notebooks/](notebooks/), 5 notebooks, 0 erreur | ☑ |
| **Modèle entraîné (pipeline complète)** | .joblib | `modeles/modele_final_random_forest.joblib` | ☑ |
| Visualisations (7 min.) | .png | [figures_eda/](figures_eda/), 16 figures | ☑ |
| Présentation / rapport | .pdf ou .pptx | hors dépôt | ☐ |

---

## Notation

Le projet est évalué sur **100 points**. C'est la note du Bloc 8.

| Phase | Points |
|-------|--------|
| Cadrage (business + prédictif) | 6 |
| Extraction | 4 |
| Diagnostic qualité | 8 |
| Nettoyage | 12 |
| Transformation | 8 |
| EDA analytique | 12 |
| Visualisation | 8 |
| **Modélisation ML** | **25** |
| Documentation & reproductibilité | 5 |
| Soutenance | 7 |
| Utilisation de l'IA | 5 |
| **Total** | **100** |

### Trois règles éliminatoires

| Manquement | Plafond |
|---|---|
| Fuite de données non détectée | Phase 7 plafonnée à 8/25 |
| Notebook non exécutable de bout en bout | Note finale plafonnée à 50/100 |
| Aucune baseline calculée | Phase 7 plafonnée à 15/25 |

Voir [Grille_Evaluation.md](Grille_Evaluation.md) pour les critères détaillés.

---

## Conseils pour réussir

### À faire

- ✅ Choisir un sujet qui vous motive **et** dont la cible est évidente
- ✅ Calculer une baseline avant de se réjouir d'un score
- ✅ Comparer au moins 3 modèles, dont un modèle simple
- ✅ Mettre **tout** le preprocessing dans la pipeline
- ✅ Traduire les écarts de score en nombre de lignes avant de crier au surapprentissage
- ✅ Assumer les limites de votre modèle : c'est un signe de maturité, pas de faiblesse

### À éviter

- ❌ Choisir un dataset sans colonne cible claire
- ❌ Scaler ou imputer avant le `train_test_split`
- ❌ Garder une colonne qui contient la réponse (fuite de données)
- ❌ Regarder le jeu de test plusieurs fois pour choisir son modèle
- ❌ Reporter une accuracy sans savoir ce que ferait un modèle bête
- ❌ Présenter un modèle qu'on ne sait pas expliquer

---

## Besoin d'aide ?

1. **Consultez le guide** de la phase concernée
2. **Regardez la démo Titanic** déroulée en cours (`Demo_Prof_Titanic/`)
3. **Relisez le notebook de référence** pour la partie modélisation
4. **Utilisez les prompts IA** fournis
5. **Posez vos questions** à votre formateur pendant les 8 h encadrées

---

**Bon projet !**

---

*Guide du projet final — Machine Learning (Blocs 6 et 8), LiveCampus.*
