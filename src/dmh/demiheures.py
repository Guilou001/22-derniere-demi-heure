"""Découper la séance en treize demi-heures, et pourquoi le découpage est le vrai travail.

**Ce que l'article étudie.** La séance américaine dure de 9 h 30 à 16 h, soit **treize demi-heures**.
L'article demande si la première prédit la dernière. Mais sa première demi-heure n'est pas celle
qu'on croit : elle se mesure **depuis la clôture de la veille**, donc elle contient la nuit. C'est
écrit dans son résumé, et c'est la première chose qu'une réplication rate.

**Le découpage, en mots simples.** Chaque barre porte l'heure à laquelle elle commence. On range
donc chaque barre dans la demi-heure où elle démarre, et le prix de fin de demi-heure est la clôture
de sa dernière barre. La barre de 16 h, qui porte l'enchère de clôture, rejoint la treizième : c'est
elle qui fait le prix officiel de clôture, et l'exclure retirerait justement le moment que l'article
étudie.

**L'identité qui garde le découpage honnête.** Les treize rendements doivent se composer en le
rendement de clôture à clôture. C'est vrai par construction, les prix de bord s'annulant deux à
deux, et un écart visible signalerait un décalage d'une barre. Le test le vérifie sur chaque séance.

**Les séances écourtées.** La veille de certains congés, la bourse ferme à 13 h. La séance ne compte
alors que sept demi-heures, la dernière étant tronquée. Ces séances sont retirées plutôt que
rabotées : y mesurer « la dernière demi-heure » comparerait deux choses différentes.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

OUVERTURE = dt.time(9, 30)
FERMETURE = dt.time(16, 0)
DEMI_HEURES = 13
BARRES_ATTENDUES = 390          # une séance pleine, 9 h 30 à 15 h 59, plus l'enchère de clôture


def _en_heure_de_new_york(barres: pd.DataFrame, fuseau: str = "America/New_York") -> pd.DataFrame:
    table = barres.copy()
    table["local"] = table["horodatage"].dt.tz_convert(fuseau)
    table["seance"] = table["local"].dt.date
    return table


def seances_completes(barres: pd.DataFrame, fuseau: str = "America/New_York") -> pd.DataFrame:
    """Les barres de la séance régulière, séance par séance, écourtées retirées.

    Une séance est retenue si elle porte au moins 390 barres entre 9 h 30 et 16 h. Le compte est
    délibérément strict : une séance à 210 barres est une demi-journée de veille de congé, et la
    dernière demi-heure n'y existe pas.
    """
    table = _en_heure_de_new_york(barres, fuseau)
    heure = table["local"].dt.time
    dedans = (heure >= OUVERTURE) & (heure <= FERMETURE)
    table = table[dedans].copy()
    compte = table.groupby("seance")["cloture"].transform("size")
    return table[compte >= BARRES_ATTENDUES].copy()


def numero_de_demi_heure(local: pd.Series) -> pd.Series:
    """Le rang de la demi-heure, de 0 à 12, d'après l'heure de début de la barre.

    La barre de 16 h tomberait au rang 13 : elle est ramenée au rang 12, parce qu'elle porte
    l'enchère de clôture et appartient donc à la dernière demi-heure.
    """
    minutes = local.dt.hour * 60 + local.dt.minute - (OUVERTURE.hour * 60 + OUVERTURE.minute)
    return np.clip(minutes // 30, 0, DEMI_HEURES - 1)


def prix_de_bord(barres: pd.DataFrame, fuseau: str = "America/New_York") -> pd.DataFrame:
    """Le prix et le volume de chaque demi-heure, séance par séance.

    Rend une ligne par séance et par demi-heure, avec le prix de fin, le volume et le nombre de
    barres. Une séance pleine en compte treize.
    """
    table = seances_completes(barres, fuseau)
    table["rang"] = numero_de_demi_heure(table["local"])
    groupes = table.groupby(["seance", "rang"], sort=True)
    sortie = groupes.agg(prix=("cloture", "last"), volume=("volume", "sum"),
                         barres=("cloture", "size"),
                         haut=("haut", "max"), bas=("bas", "min")).reset_index()
    return sortie


def rendements(barres: pd.DataFrame, fuseau: str = "America/New_York") -> pd.DataFrame:
    """Les treize rendements de demi-heure de chaque séance, plus la clôture de la veille.

    Le premier rendement se mesure depuis la clôture de la veille : c'est la définition de
    l'article, et elle fait entrer la nuit dans le signal. La première séance de l'échantillon n'a
    pas de veille et disparaît donc.
    """
    bords = prix_de_bord(barres, fuseau)
    large = bords.pivot(index="seance", columns="rang", values="prix").sort_index()
    large = large.dropna()
    volumes = bords.pivot(index="seance", columns="rang", values="volume").reindex(large.index)
    veille = large[DEMI_HEURES - 1].shift(1)

    colonnes = {}
    colonnes["r1"] = large[0] / veille - 1.0
    for k in range(1, DEMI_HEURES):
        colonnes[f"r{k + 1}"] = large[k] / large[k - 1] - 1.0
    table = pd.DataFrame(colonnes, index=large.index)
    table["cloture_veille"] = veille
    table["cloture"] = large[DEMI_HEURES - 1]
    table["rendement_du_jour"] = table["cloture"] / veille - 1.0
    table["volume_premiere"] = volumes[0]
    table["volume_du_jour"] = volumes.sum(axis=1)
    return table.dropna().copy()


def ecart_a_l_identite(table: pd.DataFrame) -> pd.Series:
    """De combien les treize rendements ne se composent pas en le rendement du jour.

    Ils le doivent exactement : les prix de bord s'annulent deux à deux le long du produit. Un écart
    visible signifierait un décalage d'une barre, ou une séance dont une demi-heure manque.
    """
    produit = np.ones(len(table))
    for k in range(1, DEMI_HEURES + 1):
        produit = produit * (1.0 + table[f"r{k}"].to_numpy())
    return pd.Series(produit - 1.0 - table["rendement_du_jour"].to_numpy(), index=table.index)
