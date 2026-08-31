"""Découper la séance en treize demi-heures, et pourquoi le découpage est le vrai travail.

**Ce que l'article étudie.** La séance américaine dure de 9 h 30 à 16 h, soit **treize demi-heures**.
L'article demande si la première prédit la dernière. Mais sa première demi-heure n'est pas celle
qu'on croit : elle se mesure **depuis la clôture de la veille**, donc elle contient la nuit. C'est
écrit dans son résumé, et c'est la première chose qu'une réplication rate.

**Le découpage, en mots simples.** Chaque barre porte l'heure à laquelle elle commence. On range
donc chaque barre dans la demi-heure où elle démarre, et le prix de fin de demi-heure est la clôture
de sa dernière minute. La barre de 16 h, qui porte l'enchère de clôture, rejoint la treizième : c'est
elle qui fait le prix officiel de clôture, et l'exclure retirerait justement le moment que l'article
étudie.

**Ce que l'identité de composition prouve, et ce qu'elle ne prouve pas.** Les treize rendements se
composent en le rendement de clôture à clôture. C'est une identité algébrique : le produit
télescope, les prix de bord s'annulant deux à deux, et les deux membres sont bâtis du même prix de
clôture et de la même veille. Elle tient donc à la précision de la machine quel que soit le rangement
des barres, et un découpage entièrement faux la vérifierait aussi. Elle ne contrôle rien d'autre que
l'arithmétique du code.

**Les deux contrôles qui peuvent échouer.** Le premier compte les barres de chaque demi-heure et les
compare aux 30 attendues, 31 pour la treizième qui reçoit l'enchère de clôture. Le second recalcule
tous les prix de bord depuis une copie des barres remise en désordre. Si le prix de fin dépendait de
l'ordre d'arrivée des lignes plutôt que de l'heure qu'elles portent, les deux passes divergeraient.
C'est le défaut que le portefeuille a déjà rencontré ailleurs, un horodatage mal lu appariant les
prix aux mauvaises minutes sans changer ni le nombre de lignes ni les colonnes.

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
BARRES_PAR_DEMI_HEURE = 30      # 9 h 30 à 9 h 59 pour la première, et ainsi de suite
# Une séance pleine porte 391 barres : les 390 minutes de 9 h 30 à 15 h 59, plus celle de 16 h qui
# porte l'enchère de clôture. Le seuil est posé à 390 et non à 391, donc il retient aussi une séance
# à laquelle il manque une minute en cours de route. Ces séances existent et sont comptées par
# `controle_des_barres` ; la barre de 16 h, elle, est présente sur toutes les séances retenues.
BARRES_ATTENDUES = 390


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

    Les barres sont remises en ordre d'horloge avant l'agrégation. Sans ce tri, le prix de fin
    serait celui de la dernière LIGNE reçue et non celui de la dernière MINUTE, donc il changerait si
    le fournisseur livrait ses barres dans un autre ordre.
    """
    table = seances_completes(barres, fuseau)
    table["rang"] = numero_de_demi_heure(table["local"])
    table = table.sort_values("local", kind="stable")
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

    « La veille » est ici la séance RETENUE précédente, et non le jour de bourse précédent. Dès
    qu'une séance est écartée au filtre de complétude, le premier rendement de la suivante couvre
    plusieurs jours. Mesuré sur le Dow Jones, le plus lacunaire des huit : 144 de ses 1 864 lignes
    ont une veille à plus de quatre jours calendaires, 39 à plus de sept, la pire à cinquante. En
    n'exigeant que la vraie veille de bourse, sa pente passe de -0,040393 (t -1,39, n 1 864) à
    -0,044600 (t -1,35, n 1 720). Déclaré, non corrigé.
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

    L'identité est algébrique et non empirique : le produit télescope en le rapport du dernier prix
    à la veille, et `rendement_du_jour` est bâti de ces deux mêmes prix. L'écart mesure donc l'erreur
    d'arrondi de la machine, rien de plus. Il resterait à 1e-15 sur des barres entièrement mélangées,
    et ne dit rien d'un décalage d'une barre. Les deux contrôles qui peuvent échouer sont dans
    `controle_des_barres`.
    """
    produit = np.ones(len(table))
    for k in range(1, DEMI_HEURES + 1):
        produit = produit * (1.0 + table[f"r{k}"].to_numpy())
    return pd.Series(produit - 1.0 - table["rendement_du_jour"].to_numpy(), index=table.index)


def barres_attendues(rang: np.ndarray) -> np.ndarray:
    """Le nombre de barres d'une demi-heure : 30, et 31 pour la treizième qui reçoit l'enchère."""
    return np.where(rang == DEMI_HEURES - 1, BARRES_PAR_DEMI_HEURE + 1, BARRES_PAR_DEMI_HEURE)


def controle_des_barres(barres: pd.DataFrame, fuseau: str = "America/New_York",
                        graine: int = 0) -> dict:
    """Les deux contrôles du découpage qui peuvent échouer, sur un symbole.

    Le premier compare le nombre de barres de chaque demi-heure aux 30 attendues, 31 pour la
    treizième. Une demi-heure qui en compte 29 a perdu une minute, et son prix de fin est celui d'une
    minute antérieure. Le second recalcule tous les prix de bord depuis une copie des barres remise
    en désordre. Ils doivent coïncider prix par prix, faute de quoi le découpage lit l'ordre
    d'arrivée des lignes au lieu de l'heure qu'elles portent.
    """
    bords = prix_de_bord(barres, fuseau)
    attendu = barres_attendues(bords["rang"].to_numpy())
    hors_compte = bords["barres"].to_numpy() != attendu
    melange = barres.sample(frac=1.0, random_state=graine).reset_index(drop=True)
    autres = prix_de_bord(melange, fuseau)
    apparie = bords.merge(autres, on=["seance", "rang"], suffixes=("", "_melange"))
    deplaces = int((apparie["prix"].to_numpy() != apparie["prix_melange"].to_numpy()).sum())
    return {"demi_heures": int(len(bords)),
            "demi_heures_incompletes": int(hors_compte.sum()),
            "barres_manquantes": int((attendu - bords["barres"].to_numpy())[hors_compte].sum()),
            "bords_deplaces_par_le_melange": deplaces}
