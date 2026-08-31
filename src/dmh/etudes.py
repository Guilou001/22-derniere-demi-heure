"""Les études du dépôt, chacune rendant le tableau qu'elle produit."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import demiheures, donnees, momentum, reference

PERIODES = [("2016-2019", 2016, 2019), ("2020-2021", 2020, 2021), ("2022-2026", 2022, 2026)]


def preparer(symbole: str, cache=donnees.CACHE) -> pd.DataFrame:
    """Les rendements de demi-heure d'un symbole, avec les variables de conditionnement."""
    table = demiheures.rendements(donnees.telecharger(symbole, cache))
    table["volatilite_premiere"] = table["r1"].abs()
    table["symbole"] = symbole
    return table


def controle_du_decoupage(tables: dict[str, pd.DataFrame], cache=donnees.CACHE) -> pd.DataFrame:
    """Les trois contrôles du découpage, symbole par symbole.

    Le premier est l'identité de composition, qui ne mesure que l'arrondi de la machine et ne peut
    pas échouer. Les deux autres le peuvent : le compte des barres de chaque demi-heure, et la
    coïncidence des prix de bord avec ceux d'une copie des barres remise en désordre.
    """
    lignes = []
    for symbole, table in tables.items():
        ecart = demiheures.ecart_a_l_identite(table).abs()
        barres = demiheures.controle_des_barres(donnees.telecharger(symbole, cache))
        lignes.append({"symbole": symbole, "seances": int(len(table)),
                       "premiere": str(table.index.min()), "derniere": str(table.index.max()),
                       "pire_ecart": float(ecart.max()), "ecart_median": float(ecart.median()),
                       **barres})
    return pd.DataFrame(lignes)


def predictibilite(tables: dict[str, pd.DataFrame], signaux=("r1", "r12")) -> pd.DataFrame:
    """La régression de la dernière demi-heure sur chaque signal, symbole par symbole."""
    lignes = []
    for symbole, table in tables.items():
        for signal in signaux:
            r = momentum.regresser(table["r13"], table[signal])
            m = momentum.mesures(momentum.rendements_de_la_strategie(table, signal))
            lignes.append({"symbole": symbole, "nom": donnees.NOMS.get(symbole, symbole),
                           "signal": signal, **r.en_ligne(),
                           "annualise": m["annualise"], "sharpe": m["sharpe"],
                           "part_gagnante": m["part_gagnante"],
                           "seuil_pb": 1e4 * momentum.cout_de_rentabilite(table, signal)})
    return pd.DataFrame(lignes)


def par_periode(tables: dict[str, pd.DataFrame], signal: str = "r1") -> pd.DataFrame:
    lignes = []
    for symbole, table in tables.items():
        sous = momentum.par_periode(table, PERIODES, signal=signal)
        sous.insert(0, "symbole", symbole)
        lignes.append(sous)
        annees = pd.Index([d.year for d in table.index])
        hors_covid = table[annees != 2020]
        r = momentum.regresser(hors_covid["r13"], hors_covid[signal])
        m = momentum.mesures(momentum.rendements_de_la_strategie(hors_covid, signal))
        lignes.append(pd.DataFrame([{"symbole": symbole, "periode": "sans 2020",
                                     "debut": 2016, "fin": 2026, **r.en_ligne(),
                                     **{f"strategie_{k}": v for k, v in m.items()}}]))
    return pd.concat(lignes, ignore_index=True)


def conditionnement(tables: dict[str, pd.DataFrame], signal: str = "r1") -> pd.DataFrame:
    """Les deux affirmations conditionnelles du résumé, éprouvées par tiers."""
    lignes = []
    for symbole, table in tables.items():
        for colonne in ("volatilite_premiere", "volume_premiere"):
            sous = momentum.par_tercile(table, colonne, signal=signal)
            sous.insert(0, "symbole", symbole)
            lignes.append(sous)
    return pd.concat(lignes, ignore_index=True)


def ecart_entre_tiers(table: pd.DataFrame) -> pd.DataFrame:
    """La différence entre le tiers haut et le tiers bas, avec son erreur type.

    Comparer deux pentes à l'œil ne dit pas si elles diffèrent. Les trois tiers étant disjoints,
    leurs pentes sont estimées sur des séances distinctes, et l'erreur type de leur différence est la
    racine de la somme des carrés des deux erreurs types.
    """
    lignes = []
    for (symbole, colonne), sous in table.groupby(["symbole", "conditionnement"], sort=False):
        indexe = sous.set_index("tiers")
        if not {"bas", "haut"} <= set(indexe.index):
            continue
        haut, bas = indexe.loc["haut"], indexe.loc["bas"]
        difference = float(haut["pente"]) - float(bas["pente"])
        erreur = float(np.hypot(haut["erreur_pente"], bas["erreur_pente"]))
        lignes.append({"symbole": symbole, "conditionnement": colonne,
                       "pente_bas": float(bas["pente"]), "pente_haut": float(haut["pente"]),
                       "haut_moins_bas": difference, "erreur_de_l_ecart": erreur,
                       "student": difference / erreur if erreur > 0 else float("nan")})
    return pd.DataFrame(lignes)


def trois_definitions(barres: pd.DataFrame) -> pd.DataFrame:
    """Les trois versions du signal, séance par séance, avant toute régression.

    La première demi-heure de l'article vaut le prix de 10 h sur la clôture de la veille. La nuit
    seule s'arrête au prix d'ouverture de 9 h 30, la séance seule part de ce même prix d'ouverture
    pour aller au prix de 10 h. Le produit des deux dernières redonne la première, à un près.
    """
    bords = demiheures.prix_de_bord(barres)
    large = bords.pivot(index="seance", columns="rang", values="prix").dropna().sort_index()

    locales = barres.copy()
    locales["local"] = locales["horodatage"].dt.tz_convert(donnees.FUSEAU)
    locales["seance"] = locales["local"].dt.date
    ouvertures = locales[locales["local"].dt.time == demiheures.OUVERTURE]
    ouverture = ouvertures.set_index("seance")["ouverture"].reindex(large.index)

    veille = large[demiheures.DEMI_HEURES - 1].shift(1)
    cadre = pd.DataFrame({
        "r13": large[demiheures.DEMI_HEURES - 1] / large[demiheures.DEMI_HEURES - 2] - 1,
        "depuis la veille": large[0] / veille - 1,
        "la nuit seule": ouverture / veille - 1,
        "la séance seule": large[0] / ouverture - 1,
    }).dropna()
    return cadre


DEFINITIONS = ("depuis la veille", "la nuit seule", "la séance seule")


def decomposition_de_la_nuit(symbole: str, cache=donnees.CACHE) -> pd.DataFrame:
    """Ce qui, dans la première demi-heure, porte le signal : la nuit ou la séance.

    L'article mesure sa première demi-heure depuis la clôture de la veille, donc elle contient deux
    choses : l'écart d'ouverture et la première demi-heure de bourse. Les séparer dit laquelle
    prédit, et la réponse n'est pas celle qu'on attendrait d'un effet dit « intrajournalier ».
    """
    cadre = trois_definitions(donnees.telecharger(symbole, cache))
    lignes = []
    for colonne in DEFINITIONS:
        r = momentum.regresser(cadre["r13"], cadre[colonne])
        lignes.append({"symbole": symbole, "definition": colonne, **r.en_ligne()})
    return pd.DataFrame(lignes)


def sensibilite_au_cout(tables: dict[str, pd.DataFrame], signal: str = "r12",
                        couts_pb=(0.0, 0.25, 0.5, 1.0, 2.0)) -> pd.DataFrame:
    """Ce que devient la stratégie quand on la facture.

    Le coût s'exprime en points de base par passage de marché, et la stratégie en fait deux par jour.
    """
    lignes = []
    for symbole, table in tables.items():
        for cout in couts_pb:
            m = momentum.mesures(
                momentum.rendements_de_la_strategie(table, signal, cout_par_passage=cout * 1e-4))
            lignes.append({"symbole": symbole, "signal": signal, "cout_pb": cout, **m})
    return pd.DataFrame(lignes)


def verdict(predictions: pd.DataFrame) -> dict:
    """Le compte qui répond à l'affirmation de tête, sur les huit fonds."""
    r1 = predictions[predictions["signal"] == "r1"]
    r12 = predictions[predictions["signal"] == "r12"]
    return {
        "fonds": int(len(r1)),
        "pente_positive_r1": int((r1["pente"] > 0).sum()),
        "pente_negative_r1": int((r1["pente"] < 0).sum()),
        "significatifs_positifs_r1": int(((r1["pente"] > 0) & (r1["student"] > 2)).sum()),
        "significatifs_negatifs_r1": int(((r1["pente"] < 0) & (r1["student"] < -2)).sum()),
        "pente_mediane_r1": float(r1["pente"].median()),
        "pente_positive_r12": int((r12["pente"] > 0).sum()),
        "significatifs_positifs_r12": int(((r12["pente"] > 0) & (r12["student"] > 2)).sum()),
        "pente_mediane_r12": float(r12["pente"].median()),
        "echantillon_publie": reference.ECHANTILLON_PUBLIE,
        "fenetre_du_depot": reference.FENETRE_DU_DEPOT,
    }


def profil_des_demi_heures(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Le rendement moyen et la volatilité de chacune des treize demi-heures.

    C'est le portrait de la séance : la première demi-heure porte le plus grand rendement moyen et
    la plus forte volatilité des treize, ce qui explique pourquoi la littérature s'y intéresse.
    """
    lignes = []
    for symbole, table in tables.items():
        for k in range(1, demiheures.DEMI_HEURES + 1):
            colonne = table[f"r{k}"]
            lignes.append({"symbole": symbole, "demi_heure": k,
                           "moyenne_pb": 1e4 * float(colonne.mean()),
                           "volatilite_pb": 1e4 * float(colonne.std(ddof=1)),
                           "part_positive": float((colonne > 0).mean())})
    return pd.DataFrame(lignes)


def matrice_de_predictibilite(table: pd.DataFrame) -> pd.DataFrame:
    """La pente de chaque demi-heure prédisant chacune des suivantes.

    L'article ne regarde qu'une case de cette matrice. La regarder en entier dit si la case choisie
    était la bonne, ou si elle a été trouvée en cherchant.
    """
    lignes = []
    for source in range(1, demiheures.DEMI_HEURES + 1):
        for cible in range(source + 1, demiheures.DEMI_HEURES + 1):
            r = momentum.regresser(table[f"r{cible}"], table[f"r{source}"])
            lignes.append({"source": source, "cible": cible, "pente": r.pente,
                           "student": r.student_pente, "r_deux": r.r_deux})
    return pd.DataFrame(lignes)


def nombre_de_cases_significatives(matrice: pd.DataFrame, seuil: float = 2.0) -> dict:
    """Combien de cases de la matrice passent le seuil, et combien on en attendrait par hasard.

    Soixante-dix-huit cases éprouvées au seuil de deux écarts types en donneraient environ quatre
    par pur hasard, dans les deux sens confondus. C'est le repère qui empêche de prendre une case
    isolée pour une découverte.
    """
    n = int(len(matrice))
    return {"cases": n,
            "au_dessus_du_seuil": int((matrice["student"].abs() > seuil).sum()),
            "positives": int((matrice["student"] > seuil).sum()),
            "negatives": int((matrice["student"] < -seuil).sum()),
            "attendues_par_hasard": round(0.0455 * n, 1)}


def compter_par_hasard(matrice: pd.DataFrame) -> float:
    return float(np.mean(matrice["student"].abs() > 2.0))
