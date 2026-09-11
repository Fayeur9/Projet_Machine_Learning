# Étape 0 - Introduction et cadrage du projet

> **Révision** : la colonne cible initialement retenue s'est révélée entièrement vide
> lors de l'extraction (phase 1). Ce document a été mis à jour en conséquence, les
> sections concernées portent la mention *révisé*.

## 1. Mon projet en quelques lignes

- Domaine : Éducation / insertion professionnelle
- Sujet précis : Analyse de l'insertion professionnelle des diplômés de l'enseignement supérieur français à partir du jeu de données public INSERSUP.
- Contexte / Problématique : Les établissements et les organismes de suivi de l'emploi souhaitent mieux comprendre les facteurs associés à une bonne insertion professionnelle après l'obtention d'un diplôme. Ce projet vise à identifier les caractéristiques des formations qui sont liées à de meilleurs résultats d'emploi à court terme.
- Public cible : Responsables pédagogiques, établissements d'enseignement supérieur, observatoires de l'emploi, enseignants et étudiants intéressés par l'analyse de données.
- Période d'analyse : Promotions 2019 à 2024 (millésime de diffusion `2026_S1`).

---

## 2. Questions business

| # | Question business | Impact potentiel | Faisabilité vérifiée |
|---|---|---|---|
| 1 | Quels types de formations présentent les meilleurs taux d'insertion professionnelle 6 mois après l'obtention du diplôme ? | Permet d'identifier les formations les plus performantes sur le plan de l'emploi. | Oui : 11 types de diplôme, 1 290 libellés distincts |
| 2 | Existe-t-il des différences d'insertion selon l'établissement, la discipline ou le domaine de formation ? | Aide à comprendre les écarts entre formations et établissements. | Oui : 329 établissements, 4 domaines, 14 disciplines, 49 secteurs |
| 3 | Quels facteurs sont associés à de meilleurs résultats d'emploi : genre, nationalité, régime d'inscription, promotion ? | Permet d'analyser les inégalités ou différences observées. | Oui, mais sur le **jeu analytique** uniquement (voir étape 1) |
| 4 | Quelles formations ont les plus faibles taux d'emploi ou les plus faibles taux d'emploi stable ? | Aide à repérer les formations qui pourraient nécessiter un accompagnement particulier. | Oui : le taux d'emploi stable à 6 mois est disponible |
| 5 | Les performances d'insertion ont-elles évolué au fil des promotions ? | Permet de suivre l'évolution des résultats dans le temps. | Oui : 6 promotions simples (2019 à 2024) |

---

## 3. Question prédictive *(révisé)*

- Question prédictive : Peut-on prédire le niveau d'insertion professionnelle d'une formation à partir de ses caractéristiques ?
- **Colonne cible (y) : `6-Taux d'emploi salarié en France - 6 mois après le diplôme`**
- Type de problème : Régression
- Répartition de la cible (mesurée sur le jeu de modélisation, 17 065 lignes) :

| Statistique | Valeur |
|---|---|
| Moyenne | 55,9 |
| Médiane | 56,1 |
| Écart-type | 18,5 |
| 1er quartile | 43,2 |
| 3e quartile | 69,2 |
| Min / Max | 0 / 100 |

  Distribution unimodale, centrée, sans classe minoritaire à gérer : adaptée à une régression.
- À qui servirait cette prédiction : Aux établissements, aux responsables de formation et aux observatoires de l'emploi.

### Pourquoi la cible a changé

La cible initiale était `6-Taux d'emploi - 6 mois après le diplôme`. Le diagnostic de
remplissage réalisé en phase 1 montre que cette colonne est **vide sur les 1 036 781
lignes** du millésime `2026_S1`, comme ses variantes à 12 et 18 mois. Elle existe dans
l'en-tête du CSV mais n'a jamais été alimentée.

`6-Taux d'emploi salarié en France - 6 mois après le diplôme` est la mesure d'emploi à
6 mois la mieux couverte du fichier (438 696 valeurs, 42,3 % des lignes). Elle répond à
la même question prédictive, avec une nuance à mentionner en soutenance : elle exclut
l'emploi non salarié, mesuré séparément par
`6-Taux de sortants en emploi non salarié - 6 mois après le diplôme`.

---

## 4. Sources de données

### Source 1 - Principale (acquise)
- Nom : INSERSUP, insertion professionnelle des diplômés de l'enseignement supérieur
- Fichier : `Projet/csv/dataset.csv`
- Format : CSV (séparateur `;`, encodage UTF-8 avec BOM)
- Volume : 773 Mo, 1 036 781 lignes × 101 colonnes
- Origine : Données publiques du ministère de l'Enseignement supérieur
- Accès : Libre, déjà téléchargé localement

### Source 2 - Complémentaire (à acquérir)
- **Statut : non acquise.** C'est le principal manque du cadrage actuel.
- Piste retenue : API JSON de data.gouv.fr / data.enseignementsup-recherche.gouv.fr,
  qui expose le même jeu INSERSUP en JSON. Cela fournirait le **second format** exigé
  par le guide sans changer de sujet.
- Piste alternative : référentiel des établissements (annuaire de l'éducation) pour
  enrichir par la géographie précise, la taille ou le statut public/privé.

### Source 3 - Enrichissement (optionnelle)
- Données régionales sur le marché de l'emploi, pour rapporter le taux d'insertion au
  contexte économique local.

---

## 5. Validation du dataset

| Critère | Seuil du guide | Constaté | Verdict |
|---|---|---|---|
| Volume | ≥ 10 000 lignes | 1 036 781 lignes brutes, 17 065 après mise au grain de modélisation | Conforme |
| Colonnes exploitables | ≥ 8, dont une catégorielle | 22 colonnes retenues : 10 catégorielles, 12 numériques | Conforme |
| Colonne cible | Identifiée, présente | `6-Taux d'emploi salarié en France - 6 mois` | Conforme après révision |
| Type de problème | Tranché | Régression | Conforme |
| Accessibilité | Déjà téléchargée | Oui, en local | Conforme |
| Répartition | Pas de classe ultra-minoritaire | Sans objet (régression), distribution centrée | Conforme |
| Nombre de sources | ≥ 2 sources, ≥ 2 formats | 1 source, 1 format | **Non conforme** |

---

## 6. Checklist de validation du cadrage

### Sujet et contexte
- [x] J'ai choisi un domaine qui m'intéresse
- [x] J'ai défini un sujet précis
- [x] J'ai rédigé le contexte et la problématique
- [x] J'ai identifié un public cible

### Questions business
- [x] J'ai formulé 5 questions business
- [x] Mes questions sont spécifiques et mesurables
- [x] J'ai vérifié que les données permettent d'y répondre

### Question prédictive
- [x] J'ai formulé une question prédictive claire
- [x] J'ai identifié la colonne cible et **vérifié qu'elle contient des valeurs**
- [x] J'ai choisi un type de problème adapté (régression)
- [x] J'ai mesuré la répartition de la cible
- [x] Mon dataset a été validé par le formateur

### Sources de données
- [x] J'ai identifié une source principale, téléchargée et chargée
- [ ] **J'ai au moins 2 sources de données** : une seule à ce jour
- [ ] **J'ai au moins 2 formats différents** : CSV uniquement
- [x] Les données couvrent la période souhaitée (2019-2024)

### Faisabilité
- [x] Le projet est réalisable dans le temps imparti
- [x] J'ai utilisé l'IA pour affiner mon cadrage

---

## 7. Limites identifiées

1. **Couverture de la cible** : seules 42,3 % des lignes ont un taux d'emploi renseigné.
   Les formations à faible effectif sont sous-représentées, ce qui biaise l'analyse vers
   les grandes formations.
2. **Seuil de publication** : INSERSUP ne publie aucun taux sous 20 sortants. Le jeu de
   modélisation a donc un effectif minimal de 20, ce qui exclut structurellement les
   petites formations.
3. **Granularité de la cible** : la cible est un taux agrégé par formation, pas une
   observation individuelle. Le modèle prédit une performance de formation, pas
   l'employabilité d'une personne. À dire explicitement en soutenance.
4. **Une seule source** à ce stade, voir section 4.

---

## 8. Conclusion

Le cadrage reste valide après révision de la cible. Le projet repose sur un dataset
volumineux et accessible, permet de répondre à cinq questions business vérifiables et
aboutit à un problème de régression bien posé. Le point à traiter en priorité est
l'ajout d'une seconde source dans un second format.
