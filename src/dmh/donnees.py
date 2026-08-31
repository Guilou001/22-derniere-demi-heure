"""Les barres d'une minute de deux fonds indiciels, téléchargées une fois.

Le téléchargement et le cache vivent dans `gvf.marches`, à un seul endroit pour le portefeuille. Ce
module ne dit que le choix des symboles, de la fenêtre et du flux.

**Le flux consolidé, et pas celui d'IEX.** Mesuré le 30 août 2026 : le flux IEX ne capte que 1,81 %
du volume consolidé et n'a vu aucune transaction sur 57 % des minutes. Un prix de fin de demi-heure
tiré d'IEX serait donc souvent le prix d'une minute antérieure, ce qui décalerait le signal étudié.
Le consolidé remonte à janvier 2016, ce qui fixe le début de la fenêtre.

**Des prix bruts, pas ajustés.** Le dividende n'a pas d'effet à l'intérieur d'une séance, et les
deux fournisseurs n'entendent pas la même chose par « ajusté » : les mêler poserait une marche de
onze points de base à chaque détachement trimestriel. Le rendement de la première demi-heure se
mesurant depuis la clôture de la veille, il traverse un détachement quatre fois l'an, et le dépôt
retire donc ces quatre séances par an plutôt que d'y laisser un saut de prix qui n'est pas un
rendement.
"""

from __future__ import annotations

from pathlib import Path

from gvf.marches import Requete, barres_alpaca

CACHE = Path("data/marches")
# Les deux fonds de tête, puis six autres parmi les plus échangés. Le résumé de l'article affirme
# que l'effet existe aussi sur « dix autres fonds indiciels très échangés, nationaux et
# internationaux » : c'est cette affirmation-là que la seconde liste éprouve.
SYMBOLES = ("SPY", "QQQ")
AUTRES = ("IWM", "DIA", "EEM", "EFA", "GLD", "TLT")
TOUS = SYMBOLES + AUTRES
NOMS = {
    "SPY": "S&P 500", "QQQ": "Nasdaq 100", "IWM": "Russell 2000",
    "DIA": "Dow Jones", "EEM": "marchés émergents", "EFA": "marchés développés hors Amérique",
    "GLD": "or", "TLT": "obligations du Trésor à long terme",
}
PREMIER_EXERCICE = 2016
DERNIER_JOUR = "2026-08-29"
FUSEAU = "America/New_York"


def telecharger(symbole: str, cache: Path = CACHE, premier: int = PREMIER_EXERCICE,
                dernier_jour: str = DERNIER_JOUR):
    """Toutes les barres d'un symbole, année par année pour que le cache reste maniable."""
    import pandas as pd

    dernier = int(dernier_jour[:4])
    morceaux = []
    for an in range(premier, dernier + 1):
        fin = f"{an}-12-31" if an < dernier else dernier_jour
        morceaux.append(barres_alpaca(Requete(symbole, f"{an}-01-01", fin, flux="sip"),
                                      cache=cache))
    table = pd.concat(morceaux, ignore_index=True)
    return table.drop_duplicates("horodatage").sort_values("horodatage").reset_index(drop=True)


def tout_telecharger(cache: Path = CACHE, symboles: tuple[str, ...] = TOUS) -> dict:
    return {s: telecharger(s, cache) for s in symboles}
