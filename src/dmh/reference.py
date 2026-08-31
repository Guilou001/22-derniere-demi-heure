"""Ce que l'article de référence affirme, et ce qu'il n'a pas été possible d'en obtenir.

**L'article.** Lei Gao, Yufeng Han, Sophia Zhengzi Li et Guofu Zhou, « Market intraday momentum »,
Journal of Financial Economics, volume 129, numéro 2, 2018, pages 394 à 414.

**Ce qu'il affirme**, dans les termes de son propre résumé, relevé le 30 août 2026 sur la notice
EconPapers du RePEc :

> Based on high frequency S&P 500 exchange-traded fund (ETF) data from 1993-2013, we show an
> intraday momentum pattern: the first half-hour return on the market as measured from the previous
> day's market close predicts the last half-hour return. This predictability, which is both
> statistically and economically significant, is stronger on more volatile days, on higher volume
> days, on recession days, and on major macroeconomic news release days. Intraday momentum also
> exists for ten other most actively traded domestic and international ETFs.

**Ce qui n'a pas été obtenu, et c'est un résultat.** Les tables chiffrées de l'article n'ont pas pu
être lues. Trois chemins ont été essayés le 30 août 2026 : l'éditeur oppose une vérification
anti-robot, le dépôt SSRN refuse le téléchargement direct, et l'adresse que le registre du
portefeuille tenait pour un PDF universitaire rend en réalité une page HTML de 138 370 octets. Les
coefficients, les statistiques de Student et les ratios de Sharpe publiés ne sont donc **pas**
reproduits ici, et rien dans ce dépôt ne prétend le contraire.

Ce qui est testé, en conséquence, ce sont les **affirmations** du résumé, sur une fenêtre que
l'article ne couvre pas. C'est la démarche de McLean et Pontiff : une anomalie publiée se juge sur
ce qu'elle fait après sa publication, et non sur la reproduction de ses propres chiffres.

**Deux points de comparaison ouverts**, eux, ont été lus en entier.

- Manapon Limkriangkrai, Daniel Chai et Gaoping Zheng, « Market intraday momentum: APAC evidence »,
  Pacific-Basin Finance Journal, volume 80, 2023, article 102086, en accès libre. Réplication
  déclarée, sur cinq marchés d'Asie-Pacifique : l'effet tient en Chine et au Japon, faiblement en
  Corée du Sud, et **pas du tout** à Hong Kong ni à Singapour.
- Mathias Mesfin, « Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures: A Systematic
  Falsification Study », arXiv 2605.04004, mai 2026. Quatorze familles de signaux intrajournaliers
  éprouvées sur 947 séances de 2021 à 2025 : **aucune ne passe**. L'avantage brut plafonne entre
  0,07 et 1,50 point par transaction quand les frais aller-retour en coûtent 2,0. Préimpression non
  revue par les pairs, ce qui est déclaré ici comme là-bas.
"""

from __future__ import annotations

RESUME_PUBLIE = (
    "Based on high frequency S&P 500 exchange-traded fund (ETF) data from 1993-2013, we show an "
    "intraday momentum pattern: the first half-hour return on the market as measured from the "
    "previous day's market close predicts the last half-hour return. This predictability, which is "
    "both statistically and economically significant, is stronger on more volatile days, on higher "
    "volume days, on recession days, and on major macroeconomic news release days. Intraday "
    "momentum also exists for ten other most actively traded domestic and international ETFs."
)

# Les quatre affirmations conditionnelles du résumé, telles qu'elles seront éprouvées une par une.
AFFIRMATIONS = {
    "predictibilite": "la première demi-heure prédit la dernière",
    "volatilite": "l'effet est plus fort les jours plus volatils",
    "volume": "l'effet est plus fort les jours de plus fort volume",
    "autres_fonds": "l'effet existe aussi sur d'autres fonds très échangés",
}

ECHANTILLON_PUBLIE = (1993, 2013)
FENETRE_DU_DEPOT = (2016, 2026)

# Ce que la préimpression de 2026 mesure sur des contrats à terme du Nasdaq, à titre de repère.
PLAFOND_MESFIN = {"avantage_brut_min_points": 0.07, "avantage_brut_max_points": 1.50,
                  "frais_aller_retour_points": 2.0, "seances": 947, "familles_de_signaux": 14}
