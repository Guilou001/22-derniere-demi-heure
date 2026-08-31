"""Les études qui produisent les tableaux publiés, éprouvées sur des cas fermés.

Chaque réponse attendue se calcule de tête. Aucun test n'ouvre le réseau ni le cache de barres.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from test_demiheures import seance

from dmh import etudes


def seance_avec_ouverture(jour: str, prix: float, ouverture: float) -> pd.DataFrame:
    """Une séance plate au prix donné, dont la seule barre de 9 h 30 ouvre ailleurs."""
    table = seance(jour, [prix] * 391)
    table.loc[0, "ouverture"] = ouverture
    return table


def test_la_nuit_et_la_seance_ne_sont_pas_interverties():
    """La veille ferme à 100, le lendemain ouvre à 110 et vaut 132 à 10 h. La nuit porte donc
    exactement 10 % et la première demi-heure de bourse 20 %, et les deux se composent en les 32 %
    du signal de l'article. Échanger les deux colonnes renverse la section 5.5, et aucun test de
    forme ne le verrait."""
    barres = pd.concat([seance("2026-06-15", [100.0] * 391),
                        seance_avec_ouverture("2026-06-16", 132.0, 110.0)], ignore_index=True)
    cadre = etudes.trois_definitions(barres)
    assert len(cadre) == 1
    assert float(cadre["depuis la veille"].iloc[0]) == pytest.approx(0.32)
    assert float(cadre["la nuit seule"].iloc[0]) == pytest.approx(0.10)
    assert float(cadre["la séance seule"].iloc[0]) == pytest.approx(0.20)


def test_les_deux_morceaux_se_composent_en_le_signal_entier():
    barres = pd.concat([seance("2026-06-15", [100.0] * 391),
                        seance_avec_ouverture("2026-06-16", 132.0, 110.0)], ignore_index=True)
    cadre = etudes.trois_definitions(barres)
    compose = (1 + cadre["la nuit seule"]) * (1 + cadre["la séance seule"]) - 1
    assert float(compose.iloc[0]) == pytest.approx(float(cadre["depuis la veille"].iloc[0]))


def _matrice_fabriquee(students: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"source": range(1, len(students) + 1),
                         "cible": range(2, len(students) + 2),
                         "pente": [0.0] * len(students), "student": students,
                         "r_deux": [0.0] * len(students)})


def test_le_compte_des_cases_significatives_se_fait_sur_la_valeur_absolue():
    """Quatre cases au-delà de deux erreurs types, dans les deux sens, et la case à exactement 2,0
    qui reste en deçà du seuil parce que la comparaison est stricte."""
    compte = etudes.nombre_de_cases_significatives(
        _matrice_fabriquee([3.0, -2.5, 1.0, 0.0, 2.0, -4.0, 2.1]))
    assert compte["cases"] == 7
    assert compte["au_dessus_du_seuil"] == 4
    assert compte["positives"] == 2
    assert compte["negatives"] == 2
    assert compte["attendues_par_hasard"] == pytest.approx(0.3)


def test_la_matrice_porte_les_soixante_dix_huit_paires_et_celle_de_l_article():
    rendements = pd.DataFrame(
        np.random.default_rng(7).normal(0, 0.001, size=(300, 13)),
        columns=[f"r{k}" for k in range(1, 14)])
    matrice = etudes.matrice_de_predictibilite(rendements)
    assert len(matrice) == 78
    assert ((matrice["source"] == 1) & (matrice["cible"] == 13)).sum() == 1
    assert (matrice["cible"] > matrice["source"]).all()


def test_l_ecart_entre_tiers_porte_la_racine_de_la_somme_des_carres():
    """Les tiers étant disjoints, l'erreur type de la différence vaut 5 quand les deux valent 3 et
    4. Sans erreur type, comparer deux pentes à l'œil ne dit rien."""
    tiers = pd.DataFrame({
        "symbole": ["SPY"] * 3, "conditionnement": ["volatilite_premiere"] * 3,
        "tiers": ["bas", "moyen", "haut"], "pente": [0.02, 0.0, -0.03],
        "erreur_pente": [3.0, 1.0, 4.0]})
    ecart = etudes.ecart_entre_tiers(tiers)
    assert len(ecart) == 1
    assert float(ecart["haut_moins_bas"].iloc[0]) == pytest.approx(-0.05)
    assert float(ecart["erreur_de_l_ecart"].iloc[0]) == pytest.approx(5.0)
    assert float(ecart["student"].iloc[0]) == pytest.approx(-0.01)
