"""Code d'inférence du modèle d'insertion professionnelle.

Permet d'utiliser le modèle sans rejouer un seul notebook : on charge le bundle produit
par l'étape 5c, on lui passe une formation telle qu'InserSup la publie, il renvoie une
prédiction de taux d'emploi salarié à six mois.

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

Seules les six variables ligne à ligne sont reconstruites ici, avec les définitions de
`modeles/protocole.py`, celles-là mêmes qui ont servi à l'entraînement. Les trois agrégats
de contexte sont calculés par la pipeline elle-même, avec les tables apprises sur le jeu
d'apprentissage : il n'y a pas de référentiel séparé, donc pas d'écart possible entre
l'entraînement et l'inférence. Une clé inconnue (établissement ou diplôme jamais vu) ne
fait pas échouer la prédiction : elle retombe sur la valeur médiane, et `predire` le
signale.
"""
from pathlib import Path

import joblib
import pandas as pd

from modeles.protocole import (CODE_SISE, CODE_UAI, POURSUIVANTS, SORTANTS,
                               appliquer_variables_ligne)

CHEMIN_MODELE = Path(__file__).resolve().parent / 'modele_final.joblib'

COLONNES_ATTENDUES = [
    'Région', 'Académie', 'Type de diplôme', 'Domaine disciplinaire', 'Discipline',
    'Secteur disciplinaire', 'Promotion', CODE_UAI, CODE_SISE, SORTANTS, POURSUIVANTS,
]


def charger(chemin=CHEMIN_MODELE):
    """Charge le bundle du modèle.

    Le fichier est produit par l'étape 5c de ce projet : il n'est pas destiné à être
    chargé depuis une source tierce, `joblib.load` exécutant le code qu'il contient.
    """
    return joblib.load(chemin)


def preparer_ligne_brute(ligne, modele):
    """Transforme une formation brute en entrée de la pipeline.

    Renvoie le DataFrame d'une ligne, avec les colonnes attendues par la pipeline : les
    variables ligne à ligne et les deux codes dont la pipeline tire ses agrégats.
    """
    manquantes = [colonne for colonne in COLONNES_ATTENDUES if colonne not in ligne]
    if manquantes:
        raise KeyError(f'Colonnes absentes de la ligne soumise : {manquantes}')

    brute = pd.DataFrame([{colonne: ligne[colonne] for colonne in COLONNES_ATTENDUES}])
    brute['Promotion'] = brute['Promotion'].astype(int)
    brute[[SORTANTS, POURSUIVANTS]] = brute[[SORTANTS, POURSUIVANTS]].astype(float)
    brute[[CODE_UAI, CODE_SISE]] = brute[[CODE_UAI, CODE_SISE]].astype(str)
    return appliquer_variables_ligne(brute)[modele['colonnes_entree']]


def predire(modele, ligne):
    """Prédit le taux d'emploi salarié à six mois d'une formation.

    Renvoie un dictionnaire : la prédiction, l'intervalle indicatif à plus ou moins la
    MAE de test, et les variables de contexte retombées sur leur valeur par défaut.
    """
    preparee = preparer_ligne_brute(ligne, modele)
    pipeline = modele['pipeline']
    prediction = float(pipeline.predict(preparee)[0])
    marge = modele['metriques_test']['MAE']
    return {
        'prediction': round(prediction, 1),
        'intervalle': (round(max(prediction - marge, 0.0), 1),
                       round(min(prediction + marge, 100.0), 1)),
        'marge': marge,
        'replis': pipeline.named_steps['agregats'].cles_inconnues(preparee),
    }
