# Fiche du modèle : insertion professionnelle des formations

*Fiche générée par [`etape_7_synthese_modele.ipynb`](notebooks/etape_7_synthese_modele.ipynb)
à partir du modèle livré. Ne pas modifier à la main.*

## Ce que fait ce modèle

Il prédit le **taux d'emploi salarié en France six mois après le diplôme** d'une formation
de l'enseignement supérieur, à partir de 19 caractéristiques connues
avant l'enquête d'insertion.

- **Tâche** : régression, cible continue de 0 à 100 %.
- **Algorithme** : RandomForestRegressor, 200 arbres,
  `min_samples_leaf=2`, `random_state=42`.
- **Unité de prédiction** : une formation, c'est-à-dire un diplôme d'un établissement pour
  une promotion donnée. **Jamais une personne.**

## Données d'entraînement

- **Source** : InserSup, millésime 2026_S1, ministère de l'Enseignement supérieur, Licence
  Ouverte Etalab.
- **Périmètre** : 17 065 formations, promotions 2019 à 2024, France.
- **Découpage** : 80 % apprentissage, 20 % test, `random_state=42`, effectué avant tout
  prétraitement.
- **Exclusions volontaires** : tous les indicateurs d'emploi mesurés à 12, 18, 24 et
  30 mois, ainsi que l'emploi stable et non salarié à 6 mois. Mesurés au même horizon que la
  cible ou après elle, ils constitueraient une fuite de données.

## Performance

| Métrique | Valeur | Lecture |
|---|---|---|
| MAE | **9.579 points** | Erreur moyenne sur 3413 formations jamais vues |
| RMSE | 12.373 points | Pénalise les grosses erreurs |
| R² | 0.554 | Part de la variance expliquée |
| Référence naïve | 15.069 points de MAE | Prédire la moyenne pour tout le monde |
| **Gain** | **5.49 points, soit 36 %** | Ce que le modèle apporte réellement |

Le jeu de test n'a été ouvert qu'une fois, après le choix définitif du modèle.

## Où ce modèle échoue

| Situation | Effet mesuré |
|---|---|
| Formations de 25 sortants ou moins | MAE de 12.09 points, contre 6.33 au-delà de 90 sortants |
| Formation jamais vue à l'entraînement | MAE de 11.28 points, soit +1,89 point |
| Prédire une promotion future | R² de 0.458 en entraînant sur 2019-2022 et testant sur 2023-2024 |
| Choc conjoncturel inédit | La promotion 2020 est systématiquement surestimée |

Le score global est optimiste : 90 % des
formations du jeu de test apparaissent aussi à l'entraînement, par une autre promotion.

## Limites d'usage

1. **Le modèle décrit, il n'explique pas.** Une variable importante n'est pas une cause. Le
   type de diplôme prédit bien parce qu'il résume un public, une discipline et un marché.
2. **Variables contemporaines de la cible.** Les effectifs de sortants et de poursuivants
   proviennent de la même enquête à six mois : le modèle prédit au moment de l'enquête, pas
   avant la sortie de promotion.
3. **Seuil de publication.** Aucun taux n'est publié sous 20 sortants : les petites
   formations sont absentes des données, et donc hors du domaine de validité.
4. **Un taux d'emploi salarié n'est pas un taux d'insertion.** L'emploi non salarié est
   mesuré séparément et exclu.

## Ce pour quoi ce modèle ne doit pas être utilisé

- **Décider du financement ou de la fermeture d'une formation.** L'erreur moyenne dépasse
  9 points et double sur les petites formations : elle est du même ordre que les écarts qu'on
  voudrait arbitrer.
- **Comparer deux formations proches.** Un écart de 5 points prédits est dans le bruit.
- **Évaluer une personne.** L'unité de prédiction est une formation entière.
- **Classer des établissements.** Un établissement spécialisé hérite de la performance de
  son secteur, l'étape 2 le montre.

## Biais connus

- **Biais de sélection** : les formations sous 20 sortants sont exclues par la source. Les
  petites formations, souvent rurales ou spécialisées, ne sont pas représentées.
- **Biais de représentation** : 58 % des lignes du fichier brut n'ont pas de cible et
  disparaissent du périmètre.
- **Biais d'interprétation** : le taux d'emploi salarié pénalise mécaniquement les formations
  qui mènent à une poursuite d'études. Un taux bas n'y signale aucun échec.
- **Angle mort** : genre, nationalité et régime d'inscription ne sont pas dans le modèle. Il
  ne peut rien dire des disparités, et ne doit pas être invoqué pour les nier.

## Utilisation

```python
from modeles.inference import charger, predire

modele = charger()
predire(modele, {
    'Région': 'Bretagne',
    'Académie': 'Rennes',
    'Type de diplôme': 'Licence professionnelle',
    'Domaine disciplinaire': 'Sciences, technologies, santé',
    'Discipline': 'Sciences fondamentales et applications',
    'Secteur disciplinaire': 'Informatique',
    'Promotion': 2024,
    "Code UAI de l'établissement": '0350936C',
    'Code du diplôme SISE': '99999',
    '6-Nombre de sortants - 6 mois après le diplôme': 48,
    '6-Nombre de poursuivants - 6 mois après le diplôme': 6,
})
```

Une modalité inconnue ne fait pas échouer la prédiction : la variable concernée retombe sur
la médiane d'apprentissage, et la clé `replis` de la réponse dit lesquelles.

## Maintenance

Le modèle est lié au millésime 2026_S1. À chaque nouveau millésime InserSup, réexécuter les
notebooks des étapes 1 à 5 dans l'ordre, puis ce notebook : les contrôles de conformité
échouent si une fuite ou un identifiant s'est glissé dans les variables.
