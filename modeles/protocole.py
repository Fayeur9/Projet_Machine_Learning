"""Protocole de modélisation commun aux étapes 3 à 7.

Un seul endroit définit les variables, le découpage, la validation croisée et la pipeline.
Les notebooks l'importent au lieu de recopier ces définitions, ce qui garantit que toutes
les étapes travaillent sur le même découpage et la même pipeline.

Deux principes, issus de la révision du protocole (voir etapes/étape_10_revision.md) :

1. **Le découpage est groupé par formation** (code UAI × code SISE). Une formation apparaît
   jusqu'à six fois, une par promotion : un découpage ligne à ligne place ses autres
   promotions dans l'apprentissage et mesure un score optimiste.
2. **Tout ce qui lit d'autres lignes que la sienne s'ajuste dans la pipeline.** Les
   agrégats de contexte sont appris par `AgregatsContexte` sur les seules lignes
   d'entraînement de chaque pli, et le même objet ajusté sert à l'inférence.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "6-Taux d'emploi salarié en France - 6 mois après le diplôme"
SORTANTS = '6-Nombre de sortants - 6 mois après le diplôme'
POURSUIVANTS = '6-Nombre de poursuivants - 6 mois après le diplôme'
CODE_UAI = "Code UAI de l'établissement"
CODE_SISE = 'Code du diplôme SISE'
SECTEUR = 'Secteur disciplinaire'
MILLESIME = 2026
RANDOM_STATE = 42

DIPLOMES_PROFESSIONNALISANTS = [
    'Licence professionnelle', 'Master MEEF', "Diplôme d'ingénieurs",
    'Bachelor universitaire de technologie',
]
BORNES_EFFECTIF = [0, 25, 45, 90, np.inf]
LIBELLES_EFFECTIF = ['très petite (≤ 25)', 'petite (26-45)',
                     'moyenne (46-90)', 'grande (> 90)']

# Variables calculées ligne à ligne : elles ne lisent que la ligne elle-même, elles peuvent
# donc être calculées avant le découpage sans rien apprendre des autres lignes.
VARIABLES_LIGNE = {
    'anciennete_promotion': lambda d: MILLESIME - d['Promotion'],
    'promotion_choc_sanitaire': lambda d: (d['Promotion'] == 2020).astype(int),
    'est_diplome_professionnalisant': lambda d: (
        d['Type de diplôme'].isin(DIPLOMES_PROFESSIONNALISANTS).astype(int)),
    'taille_formation': lambda d: d[SORTANTS] + d[POURSUIVANTS],
    'ratio_poursuite': lambda d: (d[POURSUIVANTS] / d['taille_formation']).round(4),
    # Bornes fixées à l'avance, jamais déduites des données.
    'tranche_effectif': lambda d: pd.cut(
        d[SORTANTS], bins=BORNES_EFFECTIF, labels=LIBELLES_EFFECTIF).astype(str),
}

# Variables de contexte : elles lisent d'autres lignes, elles sont donc apprises dans la
# pipeline par `AgregatsContexte`, sur les seules lignes d'entraînement.
AGREGATS = ['taille_mediane_secteur', 'nb_formations_etablissement',
            'nb_etablissements_par_diplome']

CATEGORICAL_FEATURES = ['Région', 'Académie', 'Type de diplôme', 'Domaine disciplinaire',
                        'Discipline', SECTEUR, 'Promotion', 'tranche_effectif']
NUMERIC_FEATURES = [SORTANTS, POURSUIVANTS, 'anciennete_promotion',
                    'promotion_choc_sanitaire', 'est_diplome_professionnalisant',
                    'taille_formation', 'ratio_poursuite'] + AGREGATS
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# Ce que reçoit la pipeline : les variables ligne à ligne et les deux identifiants dont
# `AgregatsContexte` a besoin. Les identifiants n'atteignent jamais le modèle : le
# prétraitement ne sélectionne que FEATURES.
COLONNES_ENTREE = [c for c in FEATURES if c not in AGREGATS] + [CODE_UAI, CODE_SISE]

# Validation croisée groupée : les promotions d'une même formation restent dans le même pli.
CV = GroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


def appliquer_variables_ligne(donnees):
    """Ajoute les six variables ligne à ligne, sans modifier l'original."""
    donnees = donnees.copy()
    for nom, calcul in VARIABLES_LIGNE.items():
        donnees[nom] = calcul(donnees)
    return donnees


def identifiant_formation(donnees):
    """Identifiant d'une formation, toutes promotions confondues : UAI|SISE."""
    return donnees[CODE_UAI].astype(str) + '|' + donnees[CODE_SISE].astype(str)


def decouper(donnees, test_size=0.20):
    """Découpage unique apprentissage / test, groupé par formation.

    Renvoie les index (étiquettes) d'apprentissage et de test. Aucune formation n'est
    présente des deux côtés, ce qu'un `assert` vérifie.
    """
    groupes = identifiant_formation(donnees)
    separateur = GroupShuffleSplit(n_splits=1, test_size=test_size,
                                   random_state=RANDOM_STATE)
    positions_train, positions_test = next(separateur.split(donnees, groups=groupes))
    index_train = donnees.index[positions_train]
    index_test = donnees.index[positions_test]
    assert set(groupes.loc[index_train]).isdisjoint(groupes.loc[index_test]), \
        'Une formation est présente à la fois en apprentissage et en test'
    return index_train, index_test


class AgregatsContexte(BaseEstimator, TransformerMixin):
    """Calcule les trois variables de contexte à partir des seules lignes d'ajustement.

    `fit` apprend trois tables (taille médiane des promotions par secteur, nombre de
    diplômes par établissement, nombre d'établissements par diplôme) et une valeur par
    défaut pour les clés inconnues. `transform` les ajoute aux lignes reçues, sans jamais
    les recalculer à partir d'elles : une ligne de test ou d'inférence est décrite avec
    ce qui a été appris sur l'entraînement, et rien d'autre.
    """

    TABLES = {
        'taille_mediane_secteur': SECTEUR,
        'nb_formations_etablissement': CODE_UAI,
        'nb_etablissements_par_diplome': CODE_SISE,
    }

    def fit(self, X, y=None):
        self.tables_ = {
            'taille_mediane_secteur': X.groupby(SECTEUR)[SORTANTS].median().to_dict(),
            'nb_formations_etablissement': X.groupby(CODE_UAI)[CODE_SISE].nunique().to_dict(),
            'nb_etablissements_par_diplome': X.groupby(CODE_SISE)[CODE_UAI].nunique().to_dict(),
        }
        # Une clé inconnue retombe sur la médiane de la table : la valeur typique d'un
        # secteur, d'un établissement ou d'un diplôme de l'apprentissage.
        self.defauts_ = {nom: float(np.median(list(table.values())))
                         for nom, table in self.tables_.items()}
        return self

    def transform(self, X):
        X = X.copy()
        for nom, cle in self.TABLES.items():
            X[nom] = (X[cle].map(self.tables_[nom]).astype(float)
                      .fillna(self.defauts_[nom]))
        return X

    def cles_inconnues(self, X):
        """Variables de contexte retombées sur leur défaut, faute de clé connue."""
        return [nom for nom, cle in self.TABLES.items()
                if not X[cle].isin(self.tables_[nom].keys()).all()]


def creer_pipeline(modele, mettre_a_echelle=False):
    """Pipeline complète : agrégats de contexte, encodage, puis modèle.

    La mise à l'échelle ne sert qu'aux modèles linéaires. `clone` évite que deux
    pipelines partagent le même objet modèle.
    """
    traitement_numerique = StandardScaler() if mettre_a_echelle else 'passthrough'
    pretraitement = ColumnTransformer([
        ('categorielles', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
         CATEGORICAL_FEATURES),
        ('numeriques', traitement_numerique, NUMERIC_FEATURES),
    ])
    return Pipeline([('agregats', AgregatsContexte()),
                     ('pretraitement', pretraitement),
                     ('modele', clone(modele))])
