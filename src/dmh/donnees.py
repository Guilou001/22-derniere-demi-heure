"""Les barres d'une minute de huit fonds indiciels, téléchargées une fois.

Le téléchargement et le cache vivent dans `gvf.marches`, à un seul endroit pour le portefeuille. Ce
module ne dit que le choix des symboles, de la fenêtre et du flux.

**Le flux consolidé, et pas celui d'IEX.** Le dépôt voisin 24 mesure sur QQQ, du 3 août 2020 au
28 août 2026, qu'IEX porte 1,37 % du volume consolidé et publie une barre dans 91,9 % des minutes de
séance. Les trous ne sont donc pas ce qui gêne : c'est le prix qui diffère, la moyenne pondérée d'IEX
s'écartant de 9,61 cents en médiane. Une mesure antérieure de ce portefeuille annonçait 57 % de
minutes muettes ; ce compte porte sur la journée entière, extensions d'avant et d'après-bourse
comprises, et non sur les 390 minutes de séance où ce dépôt travaille. Le consolidé remonte à
janvier 2016, ce qui fixe le début de la fenêtre.

**Des prix bruts, pas ajustés.** Les deux fournisseurs n'entendent pas la même chose par « ajusté » :
les mêler poserait une marche de onze points de base à chaque détachement trimestriel. Le rendement
de la première demi-heure se mesurant depuis la clôture de la veille, il traverse un détachement
quatre fois l'an. Ces séances ne sont PAS retirées, et aucun filtre de ce genre n'existe dans le
dépôt. Mesuré sur le S&P 500, sur les 41 troisièmes vendredis de trimestre de la fenêtre : le
rendement de la première demi-heure y vaut -55,16 points de base en moyenne contre +4,70 ailleurs. Il
y est négatif 92,7 % du temps contre 43,6 %. Retirer ces 41 séances déplace la pente de -0,055651
(t -2,10) à -0,056856 (t -2,18). Déclaré, non corrigé.
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
