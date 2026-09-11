"""Code d'inférence du modèle d'insertion professionnelle.

Permet d'utiliser le modèle sans rejouer un seul notebook : on charge le bundle produit
par l'étape 5, on lui passe une formation telle qu'InserSup la publie, il renvoie une
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

Les onze variables dérivées attendues par la pipeline sont reconstruites ici, à partir du
référentiel calculé sur le seul jeu d'apprentissage et embarqué dans le bundle. Une
modalité inconnue ne fait pas échouer la prédiction : elle retombe sur la valeur médiane
d'apprentissage, et `predire` le signale.
"""
from pathlib import Path

import joblib
import pandas as pd

CHEMIN_MODELE = Path(__file__).resolve().parent / 'modele_final_random_forest.joblib'

CIBLE = "6-Taux d'emploi salarié en France - 6 mois après le diplôme"
SORTANTS = '6-Nombre de sortants - 6 mois après le diplôme'
POURSUIVANTS = '6-Nombre de poursuivants - 6 mois après le diplôme'
CODE_UAI = "Code UAI de l'établissement"
CODE_SISE = 'Code du diplôme SISE'

COLONNES_ATTENDUES = [
    'Région', 'Académie', 'Type de diplôme', 'Domaine disciplinaire', 'Discipline',
    'Secteur disciplinaire', 'Promotion', CODE_UAI, CODE_SISE, SORTANTS, POURSUIVANTS,
]

TRANCHES = [(25, 'très petite (≤ 25)'), (45, 'petite (26-45)'), (90, 'moyenne (46-90)')]


def charger(chemin=CHEMIN_MODELE):
    """Charge le bundle du modèle.

    Le fichier est produit par l'étape 5 de ce projet : il n'est pas destiné à être
    chargé depuis une source tierce, `joblib.load` exécutant le code qu'il contient.
    """
    return joblib.load(chemin)


def tranche_effectif(sortants):
    """Classe un effectif de sortants, avec les bornes fixées à l'étape 3."""
    for borne, libelle in TRANCHES:
        if sortants <= borne:
            return libelle
    return 'grande (> 90)'


def preparer_ligne_brute(ligne, modele):
    """Reconstruit les 19 variables du modèle à partir d'une formation brute.

    Renvoie le DataFrame d'une ligne, et la liste des valeurs retombées sur un défaut
    faute de correspondance dans le référentiel d'apprentissage.
    """
    manquantes = [colonne for colonne in COLONNES_ATTENDUES if colonne not in ligne]
    if manquantes:
        raise KeyError(f'Colonnes absentes de la ligne soumise : {manquantes}')

    referentiel = modele['referentiel']
    defauts = referentiel['defauts']
    replis = []

    def lire(table, cle):
        """Lit le référentiel, et note le repli quand la clé est inconnue."""
        if cle in referentiel[table]:
            return referentiel[table][cle]
        replis.append(table)
        return defauts[table]

    sortants = float(ligne[SORTANTS])
    poursuivants = float(ligne[POURSUIVANTS])
    taille = sortants + poursuivants
    promotion = int(ligne['Promotion'])
    total_etablissement = lire('sortants_etablissement', ligne[CODE_UAI])

    preparee = {
        'Région': ligne['Région'],
        'Académie': ligne['Académie'],
        'Type de diplôme': ligne['Type de diplôme'],
        'Domaine disciplinaire': ligne['Domaine disciplinaire'],
        'Discipline': ligne['Discipline'],
        'Secteur disciplinaire': ligne['Secteur disciplinaire'],
        'Promotion': promotion,
        'tranche_effectif': tranche_effectif(sortants),
        SORTANTS: sortants,
        POURSUIVANTS: poursuivants,
        'anciennete_promotion': referentiel['millesime'] - promotion,
        'promotion_choc_sanitaire': int(promotion == 2020),
        'est_diplome_professionnalisant': int(
            ligne['Type de diplôme'] in referentiel['diplomes_professionnalisants']),
        'taille_formation': taille,
        'ratio_poursuite': round(poursuivants / taille, 4) if taille else 0.0,
        'taille_mediane_secteur': lire('taille_mediane_secteur',
                                       ligne['Secteur disciplinaire']),
        'nb_formations_etablissement': lire('nb_formations_etablissement',
                                            ligne[CODE_UAI]),
        'part_sortants_etablissement': round(sortants / total_etablissement, 4),
        'nb_etablissements_par_diplome': lire('nb_etablissements_par_diplome',
                                              ligne[CODE_SISE]),
    }
    return pd.DataFrame([preparee])[modele['features']], replis


def predire(modele, ligne):
    """Prédit le taux d'emploi salarié à six mois d'une formation.

    Renvoie un dictionnaire : la prédiction, l'intervalle indicatif à plus ou moins la
    MAE de test, et les variables reconstruites par défaut faute de référence connue.
    """
    preparee, replis = preparer_ligne_brute(ligne, modele)
    prediction = float(modele['pipeline'].predict(preparee)[0])
    marge = modele['metriques_test']['MAE']
    return {
        'prediction': round(prediction, 1),
        'intervalle': (round(max(prediction - marge, 0.0), 1),
                       round(min(prediction + marge, 100.0), 1)),
        'marge': marge,
        'replis': sorted(set(replis)),
    }
