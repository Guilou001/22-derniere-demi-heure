"""La régression qui teste l'effet, et la stratégie qui le monnaie.

**La régression.** L'article affirme que la première demi-heure prédit la dernière. Cela s'écrit :

    r13 = α + β·r1 + ε

et l'affirmation est que β est positif et significatif. Rien de plus. Un coefficient positif dit que
lorsque le marché monte le matin, il tend à monter encore en fin de séance.

**Pourquoi Newey et West.** Les erreurs types ordinaires supposent que les résidus sont indépendants
et de variance constante. Sur des rendements intrajournaliers, la variance change beaucoup d'un jour
à l'autre, et les jours agités arrivent en grappes. La correction de Newey et West laisse la
variance varier et laisse les résidus se corréler sur quelques jours. Elle gonfle donc honnêtement
l'erreur type, au lieu de trouver de la significativité là où il n'y a que de la persistance.

**La stratégie, en mots simples.** À 10 h, on regarde si le marché a monté depuis la veille au soir.
Si oui, on achète pour la dernière demi-heure ; sinon, on vend à découvert. On sort à la clôture. Le
rendement de la journée est donc le signe de la première demi-heure multiplié par la dernière.

**Ce qui la tue ou la sauve.** Une position par jour, ouverte et fermée : deux passages de marché par
jour, soit environ cinq cents aller-retours par an. Un coût d'un point de base par passage retire
donc deux points de base par jour à un rendement moyen qui se compte lui aussi en points de base.
C'est pourquoi le seuil de rentabilité, exprimé en coût par passage, est le vrai chiffre du dépôt.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

SEANCES_PAR_AN = 252


@dataclass(frozen=True)
class Regression:
    """Une régression simple, avec ses erreurs types corrigées."""

    constante: float
    pente: float
    erreur_constante: float
    erreur_pente: float
    student_pente: float
    r_deux: float
    observations: int
    retards: int

    def en_ligne(self) -> dict:
        return {"constante_pb": 1e4 * self.constante, "pente": self.pente,
                "erreur_pente": self.erreur_pente, "student": self.student_pente,
                "r_deux": self.r_deux, "observations": self.observations}


def _newey_west(X: np.ndarray, residus: np.ndarray, retards: int) -> np.ndarray:
    """La matrice de covariance des coefficients, robuste à l'hétéroscédasticité et à
    l'autocorrélation jusqu'à `retards` jours.

    Le noyau de Bartlett décroît linéairement avec le retard : le premier voisin compte pour presque
    tout, le dernier pour presque rien. C'est ce qui garantit que la matrice reste définie positive,
    ce qu'une somme non pondérée ne garantit pas.
    """
    n, k = X.shape
    S = (X * residus[:, None]).T @ (X * residus[:, None])
    for retard in range(1, retards + 1):
        poids = 1.0 - retard / (retards + 1.0)
        avant = (X[retard:] * residus[retard:, None])
        apres = (X[:-retard] * residus[:-retard, None])
        gamma = avant.T @ apres
        S += poids * (gamma + gamma.T)
    XtX_inv = np.linalg.inv(X.T @ X)
    return XtX_inv @ S @ XtX_inv * n / max(n - k, 1)


def regresser(y: pd.Series, x: pd.Series, retards: int | None = None) -> Regression:
    """La régression de y sur x, avec une constante et des erreurs types de Newey et West.

    Le nombre de retards suit, si l'appelant n'en impose pas, la règle 4 (n/100)^(1/4) arrondie vers
    le bas, celle qu'on trouve dans les manuels d'économétrie. Elle donne 9 retards à 2 649 séances
    et 8 à 1 864. La règle de Newey et West 1994, 4 (n/100)^(2/9), en donnerait 8 et 7 : les deux
    existent dans la littérature, et c'est la première qui est retenue ici.
    """
    donnees = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
    n = len(donnees)
    if n < 30:
        raise ValueError("moins de trente observations : la régression n'a pas de sens")
    if retards is None:
        retards = int(4 * (n / 100) ** 0.25)
    X = np.column_stack([np.ones(n), donnees["x"].to_numpy()])
    yv = donnees["y"].to_numpy()
    coefficients, *_ = np.linalg.lstsq(X, yv, rcond=None)
    residus = yv - X @ coefficients
    covariance = _newey_west(X, residus, retards)
    erreurs = np.sqrt(np.diag(covariance))
    total = float(((yv - yv.mean()) ** 2).sum())
    return Regression(constante=float(coefficients[0]), pente=float(coefficients[1]),
                      erreur_constante=float(erreurs[0]), erreur_pente=float(erreurs[1]),
                      student_pente=float(coefficients[1] / erreurs[1]),
                      r_deux=float(1 - (residus ** 2).sum() / total) if total > 0 else float("nan"),
                      observations=n, retards=retards)


def position(signal: pd.Series) -> pd.Series:
    """La position prise pour la dernière demi-heure : un si le signal monte, moins un s'il baisse.

    Un signal exactement nul, cas rare mais réel sur des prix arrondis au cent, donne une position
    nulle plutôt qu'un pari arbitraire.
    """
    return np.sign(signal).astype(float)


def rendements_de_la_strategie(table: pd.DataFrame, signal: str = "r1",
                               cible: str = "r13", cout_par_passage: float = 0.0) -> pd.Series:
    """Le rendement quotidien de la stratégie, net du coût de deux passages de marché.

    Le coût s'exprime en fraction du montant échangé et par passage. Ouvrir et fermer une position
    en fait deux, chaque jour où l'on prend position.
    """
    p = position(table[signal])
    brut = p * table[cible]
    return brut - 2.0 * cout_par_passage * p.abs()


def mesures(rendements: pd.Series) -> dict:
    """Les sept nombres qui décrivent une série de rendements quotidiens."""
    r = rendements.dropna()
    if r.empty:
        raise ValueError("aucun rendement à mesurer")
    moyenne = float(r.mean())
    ecart = float(r.std(ddof=1))
    return {
        "seances": int(len(r)),
        "moyenne_pb": 1e4 * moyenne,
        "annualise": SEANCES_PAR_AN * moyenne,
        "volatilite_annualisee": ecart * np.sqrt(SEANCES_PAR_AN),
        "sharpe": (moyenne / ecart * np.sqrt(SEANCES_PAR_AN)) if ecart > 0 else float("nan"),
        "part_gagnante": float((r > 0).mean()),
        "pire_seance_pb": 1e4 * float(r.min()),
    }


def cout_de_rentabilite(table: pd.DataFrame, signal: str = "r1",
                        cible: str = "r13") -> float:
    """Le coût par passage qui annule le rendement moyen de la stratégie.

    C'est le chiffre qui décide : au-delà, la stratégie perd de l'argent. Il se calcule en forme
    fermée, le coût entrant linéairement dans le rendement net.
    """
    p = position(table[signal])
    brut = float((p * table[cible]).mean())
    passages = float(p.abs().mean())
    if passages <= 0:
        return 0.0
    return brut / (2.0 * passages)


def par_periode(table: pd.DataFrame, bornes: list[tuple[str, int, int]], signal: str = "r1",
                cible: str = "r13", cout_par_passage: float = 0.0) -> pd.DataFrame:
    """La régression et la stratégie, période par période."""
    lignes = []
    annees = pd.Index([d.year for d in table.index])
    for nom, debut, fin in bornes:
        sous = table[(annees >= debut) & (annees <= fin)]
        if len(sous) < 30:
            continue
        r = regresser(sous[cible], sous[signal])
        m = mesures(rendements_de_la_strategie(sous, signal, cible, cout_par_passage))
        lignes.append({"periode": nom, "debut": debut, "fin": fin, **r.en_ligne(),
                       **{f"strategie_{k}": v for k, v in m.items()}})
    return pd.DataFrame(lignes)


def par_tercile(table: pd.DataFrame, colonne: str, signal: str = "r1",
                cible: str = "r13") -> pd.DataFrame:
    """L'effet mesuré séparément dans chaque tiers d'une variable de conditionnement.

    L'article affirme que l'effet est plus fort les jours volatils et les jours de fort volume. Le
    découpage en tiers d'effectif égal est le test le plus simple de cette affirmation, et il ne
    suppose aucune forme fonctionnelle.

    Les deux bornes de tiers sont calculées sur l'échantillon entier. Les pentes rendues sont donc
    descriptives et non exécutables : un opérateur de 2016 ne connaissait pas la distribution de
    2026. Les colonnes de stratégie de ce tableau portent la même fuite, et le README ne publie que
    les pentes.
    """
    valeurs = table[colonne]
    bornes = valeurs.quantile([1 / 3, 2 / 3]).to_numpy()
    rangs = np.digitize(valeurs.to_numpy(), bornes)
    lignes = []
    for tiers, etiquette in enumerate(("bas", "moyen", "haut")):
        sous = table[rangs == tiers]
        if len(sous) < 30:
            continue
        r = regresser(sous[cible], sous[signal])
        m = mesures(rendements_de_la_strategie(sous, signal, cible))
        lignes.append({"conditionnement": colonne, "tiers": etiquette, **r.en_ligne(),
                       **{f"strategie_{k}": v for k, v in m.items()}})
    return pd.DataFrame(lignes)
