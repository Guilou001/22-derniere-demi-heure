"""La régression et la stratégie, éprouvées sur des séries dont la réponse se calcule à la main."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dmh import momentum


@pytest.fixture
def serie():
    rng = np.random.default_rng(20260830)
    n = 1_500
    x = pd.Series(rng.standard_normal(n) * 0.005)
    y = 0.3 * x + pd.Series(rng.standard_normal(n) * 0.005)
    return pd.DataFrame({"r1": x, "r13": y})


def test_la_regression_retrouve_une_pente_connue(serie):
    r = momentum.regresser(serie["r13"], serie["r1"])
    assert r.pente == pytest.approx(0.3, abs=0.05)
    assert r.student_pente > 5
    assert 0 < r.r_deux < 1


def test_une_serie_sans_lien_ne_donne_pas_de_pente():
    rng = np.random.default_rng(7)
    n = 2_000
    table = pd.DataFrame({"r1": rng.standard_normal(n), "r13": rng.standard_normal(n)})
    r = momentum.regresser(table["r13"], table["r1"])
    assert abs(r.student_pente) < 3


def test_l_erreur_type_de_newey_west_depasse_celle_qui_ignore_l_autocorrelation():
    """C'est tout l'intérêt de la correction, et elle porte sur le PRODUIT du régresseur par le
    résidu, non sur le résidu seul. Avec un régresseur indépendant d'un jour à l'autre, ce produit
    l'est aussi et il n'y a rien à corriger : il faut donc que les deux soient persistants pour que
    la correction morde. C'est exactement le cas des rendements intrajournaliers, dont les jours
    agités arrivent en grappes."""
    rng = np.random.default_rng(3)
    n = 1_200
    lisser = lambda v: pd.Series(v).rolling(30, min_periods=1).mean()  # noqa: E731
    x = lisser(rng.standard_normal(n))
    y = lisser(rng.standard_normal(n))
    r_court = momentum.regresser(y, x, retards=0)
    r_long = momentum.regresser(y, x, retards=30)
    # mesuré sur cette série : l'erreur type passe de 0,0816 à 0,1179, soit 44 % de plus, et la
    # statistique de Student tombe de 1,03 à 0,71
    assert r_long.erreur_pente > 1.3 * r_court.erreur_pente
    assert abs(r_long.student_pente) < abs(r_court.student_pente)


def test_la_regression_refuse_un_echantillon_minuscule():
    petite = pd.Series(np.arange(10, dtype=float))
    with pytest.raises(ValueError):
        momentum.regresser(petite, petite)


def test_la_position_suit_le_signe_du_signal():
    signal = pd.Series([0.01, -0.01, 0.0])
    assert list(momentum.position(signal)) == [1.0, -1.0, 0.0]


def test_un_signal_parfait_donne_un_rendement_toujours_positif():
    """Si le signal a le même signe que la cible, la stratégie gagne chaque jour. C'est le cas
    limite qui vérifie que le signe est pris dans le bon sens."""
    table = pd.DataFrame({"r1": [0.01, -0.02, 0.03], "r13": [0.002, -0.004, 0.006]})
    r = momentum.rendements_de_la_strategie(table, "r1", "r13")
    assert (r > 0).all()
    assert float(r.sum()) == pytest.approx(0.012)


def test_un_signal_inverse_donne_l_oppose():
    table = pd.DataFrame({"r1": [0.01, -0.02], "r13": [-0.002, 0.004]})
    r = momentum.rendements_de_la_strategie(table, "r1", "r13")
    assert (r < 0).all()


def test_le_cout_retire_deux_passages_par_jour():
    """Ouvrir et fermer une position en fait deux. Ne compter qu'un passage sous-estimerait le coût
    de moitié, ce qui change le verdict sur une stratégie dont le seuil vaut un quart de point de
    base."""
    table = pd.DataFrame({"r1": [0.01, 0.01], "r13": [0.001, 0.001]})
    brut = momentum.rendements_de_la_strategie(table, "r1", "r13", cout_par_passage=0.0)
    net = momentum.rendements_de_la_strategie(table, "r1", "r13", cout_par_passage=1e-4)
    assert float((brut - net).iloc[0]) == pytest.approx(2e-4)


def test_le_seuil_de_rentabilite_annule_bien_le_rendement():
    table = pd.DataFrame({"r1": [0.01, -0.02, 0.03, 0.01],
                          "r13": [0.002, -0.001, 0.004, -0.001]})
    seuil = momentum.cout_de_rentabilite(table)
    net = momentum.rendements_de_la_strategie(table, cout_par_passage=seuil)
    assert float(net.mean()) == pytest.approx(0.0, abs=1e-15)


def test_les_mesures_se_calculent_a_la_main():
    r = pd.Series([0.001] * 252)
    m = momentum.mesures(r)
    assert m["seances"] == 252
    assert m["moyenne_pb"] == pytest.approx(10.0)
    assert m["annualise"] == pytest.approx(0.252)
    assert m["part_gagnante"] == pytest.approx(1.0)


def test_le_conditionnement_par_tiers_partage_l_echantillon():
    rng = np.random.default_rng(11)
    n = 900
    table = pd.DataFrame({"r1": rng.standard_normal(n) * 0.01,
                          "r13": rng.standard_normal(n) * 0.01,
                          "critere": rng.standard_normal(n)})
    sortie = momentum.par_tercile(table, "critere")
    assert list(sortie["tiers"]) == ["bas", "moyen", "haut"]
    assert int(sortie["observations"].sum()) == n
