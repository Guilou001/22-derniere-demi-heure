"""Le découpage de la séance : c'est là que se joue la réplication, et c'est là qu'on se trompe."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from dmh import demiheures


def seance(jour: str, prix: list[float], debut: str = "09:30", minutes: int = 391,
           volume: float = 1000.0) -> pd.DataFrame:
    """Une séance fabriquée : une barre par minute, avec les clôtures qu'on lui donne."""
    depart = pd.Timestamp(f"{jour} {debut}", tz="America/New_York")
    horodatage = pd.date_range(depart, periods=minutes, freq="1min").tz_convert("UTC")
    cloture = np.asarray(prix, dtype=float)
    return pd.DataFrame({"horodatage": horodatage, "ouverture": cloture, "haut": cloture,
                         "bas": cloture, "cloture": cloture,
                         "volume": np.full(minutes, volume), "transactions": 1.0,
                         "prix_moyen": cloture})


def deux_seances(pente: float = 0.0) -> pd.DataFrame:
    """Deux séances consécutives, dont la seconde monte linéairement."""
    plate = seance("2026-06-15", [100.0] * 391)
    montante = seance("2026-06-16", list(100.0 + pente * np.arange(391)))
    return pd.concat([plate, montante], ignore_index=True)


def test_une_seance_pleine_donne_treize_demi_heures():
    bords = demiheures.prix_de_bord(deux_seances())
    par_seance = bords.groupby("seance").size()
    assert set(par_seance) == {demiheures.DEMI_HEURES}


def test_la_barre_de_seize_heures_rejoint_la_derniere_demi_heure():
    """Elle porte l'enchère de clôture, donc le prix officiel. L'exclure retirerait exactement le
    moment que l'article étudie."""
    local = pd.Series(pd.to_datetime(["2026-06-15 15:59", "2026-06-15 16:00"]))
    rangs = demiheures.numero_de_demi_heure(local)
    assert list(rangs) == [12, 12]


def test_les_bornes_de_demi_heure_tombent_aux_bons_rangs():
    heures = ["09:30", "09:59", "10:00", "10:29", "10:30", "15:29", "15:30", "15:59"]
    local = pd.Series(pd.to_datetime([f"2026-06-15 {h}" for h in heures]))
    assert list(demiheures.numero_de_demi_heure(local)) == [0, 0, 1, 1, 2, 11, 12, 12]


def test_les_treize_rendements_se_composent_en_le_rendement_du_jour():
    """L'identité qui garde le découpage honnête. Un décalage d'une barre la briserait, alors que
    la table garderait le bon nombre de lignes et les bonnes colonnes."""
    table = demiheures.rendements(deux_seances(pente=0.01))
    assert len(table) == 1
    assert abs(float(demiheures.ecart_a_l_identite(table).iloc[0])) < 1e-12


def test_le_premier_rendement_part_de_la_cloture_de_la_veille():
    """C'est la définition de l'article, et elle fait entrer la nuit dans le signal. Partir de
    l'ouverture donnerait un autre nombre, et c'est la première chose qu'une réplication rate."""
    veille = seance("2026-06-15", [100.0] * 391)
    lendemain = seance("2026-06-16", [110.0] * 391)
    table = demiheures.rendements(pd.concat([veille, lendemain], ignore_index=True))
    assert float(table["r1"].iloc[0]) == pytest.approx(0.10)
    assert float(table["cloture_veille"].iloc[0]) == pytest.approx(100.0)


def test_la_premiere_seance_disparait_faute_de_veille():
    table = demiheures.rendements(deux_seances())
    assert len(table) == 1
    assert table.index[0] == dt.date(2026, 6, 16)


def test_une_seance_ecourtee_est_retiree():
    """La veille de certains congés, la bourse ferme à 13 h. La dernière demi-heure n'y existe pas,
    et y mesurer l'effet comparerait deux choses différentes."""
    pleine = seance("2026-06-15", [100.0] * 391)
    courte = seance("2026-06-16", [100.0] * 211, minutes=211)
    bords = demiheures.prix_de_bord(pd.concat([pleine, courte], ignore_index=True))
    assert set(bords["seance"]) == {dt.date(2026, 6, 15)}


def test_les_barres_hors_seance_sont_ecartees():
    """Les barres d'avant-bourse et d'après-bourse existent dans les données et n'appartiennent pas
    à la séance régulière."""
    avant = seance("2026-06-15", [99.0] * 60, debut="08:00", minutes=60)
    pendant = seance("2026-06-15", [100.0] * 391)
    table = demiheures.seances_completes(pd.concat([avant, pendant], ignore_index=True))
    assert len(table) == 391
    assert table["local"].dt.time.min() == demiheures.OUVERTURE


def test_le_dernier_rendement_est_bien_la_derniere_demi_heure():
    prix = [100.0] * 361 + [101.0] * 30
    table = demiheures.rendements(pd.concat(
        [seance("2026-06-15", [100.0] * 391), seance("2026-06-16", prix)], ignore_index=True))
    assert float(table["r13"].iloc[0]) == pytest.approx(0.01)


def test_le_volume_de_la_premiere_demi_heure_est_bien_celui_de_trente_barres():
    table = demiheures.rendements(deux_seances())
    assert float(table["volume_premiere"].iloc[0]) == pytest.approx(30 * 1000.0)
