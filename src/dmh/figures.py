"""Les cinq figures du dépôt. Chacune reçoit un tableau déjà calculé et n'invente aucun nombre."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from gvf.style import GRIS, OKABE_ITO, appliquer, enregistrer, formateur, fr

from .demiheures import DEMI_HEURES

DOSSIER = Path("results/figures")


def _fin(fig, nom: str, dossier: Path = DOSSIER) -> list[Path]:
    # pas de `tight_layout` : la feuille de style partagée active la mise en page sous contrainte
    chemins = enregistrer(fig, dossier, nom)
    plt.close(fig)
    return chemins


def huit_fonds(table, dossier: Path = DOSSIER) -> list[Path]:
    """La pente de chaque fonds, pour les deux signaux, avec deux erreurs types."""
    appliquer()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8), sharey=True)
    for i, (signal, titre) in enumerate((
            ("r1", "La première demi-heure prédit-elle la dernière ?"),
            ("r12", "Et l'avant-dernière ?"))):
        ax = axes[i]
        sous = table[table["signal"] == signal].sort_values("pente")
        y = np.arange(len(sous))
        couleurs = [OKABE_ITO[2] if p > 0 else OKABE_ITO[3] for p in sous["pente"]]
        ax.barh(y, sous["pente"], color=couleurs, height=0.7)
        ax.errorbar(sous["pente"], y, xerr=2 * sous["erreur_pente"], fmt="none",
                    ecolor=GRIS, elinewidth=1.1, capsize=3)
        ax.axvline(0, color=GRIS, lw=1.1)
        ax.set_yticks(y, list(sous["symbole"]), fontsize=9)
        ax.set_title(titre, fontsize=10)
        ax.set_xlabel("pente de la régression")
        ax.xaxis.set_major_formatter(formateur(decimales=2))
    return _fin(fig, "huit_fonds", dossier)


def matrice(table, dossier: Path = DOSSIER) -> list[Path]:
    """Toutes les paires de demi-heures, et la case que l'article a retenue."""
    appliquer()
    grille = np.full((DEMI_HEURES, DEMI_HEURES), np.nan)
    for _, ligne in table.iterrows():
        grille[int(ligne["source"]) - 1, int(ligne["cible"]) - 1] = ligne["student"]
    fig, ax = plt.subplots(figsize=(8.2, 6.4))
    limite = float(np.nanmax(np.abs(grille)))
    image = ax.imshow(grille, cmap="RdBu_r", vmin=-limite, vmax=limite, origin="upper")
    for i in range(DEMI_HEURES):
        for j in range(DEMI_HEURES):
            if not np.isnan(grille[i, j]) and abs(grille[i, j]) > 2:
                ax.text(j, i, fr(grille[i, j], 1), ha="center", va="center", fontsize=7.4,
                        color="black")
    ax.add_patch(plt.Rectangle((DEMI_HEURES - 1.5, -0.5), 1, 1, fill=False,
                               edgecolor="black", lw=2.2))
    # la note passe SOUS la case plutôt qu'au-dessus : au-dessus, elle recouvrait le titre
    ax.annotate("la case que l'article retient", (DEMI_HEURES - 1, 0.4),
                textcoords="offset points", xytext=(-18, -34), ha="right", fontsize=8.5,
                color=GRIS, arrowprops={"arrowstyle": "->", "color": GRIS, "lw": 1.0})
    ax.set_xticks(range(DEMI_HEURES), [str(k + 1) for k in range(DEMI_HEURES)], fontsize=8)
    ax.set_yticks(range(DEMI_HEURES), [str(k + 1) for k in range(DEMI_HEURES)], fontsize=8)
    ax.set_xlabel("demi-heure prédite")
    ax.set_ylabel("demi-heure qui prédit")
    ax.grid(False)
    barre = fig.colorbar(image, ax=ax, shrink=0.82)
    barre.set_label("statistique de Student de la pente")
    ax.set_title("Les 78 paires de demi-heures du S&P 500, 2016-2026")
    return _fin(fig, "matrice", dossier)


def periodes(table, dossier: Path = DOSSIER) -> list[Path]:
    """La pente de la première demi-heure, période par période et fonds par fonds."""
    appliquer()
    ordre = ["2016-2019", "2020-2021", "2022-2026", "sans 2020"]
    t = table[table["periode"].isin(ordre)]
    fonds = list(dict.fromkeys(t["symbole"]))
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    largeur = 0.2
    x = np.arange(len(ordre))
    for i, fonds_nom in enumerate(fonds):
        sous = t[t["symbole"] == fonds_nom].set_index("periode").reindex(ordre)
        ax.bar(x + (i - (len(fonds) - 1) / 2) * largeur, sous["pente"], width=largeur,
               color=OKABE_ITO[i % len(OKABE_ITO)], label=fonds_nom)
    ax.axhline(0, color=GRIS, lw=1.1)
    ax.set_xticks(x, ordre)
    ax.set_ylabel("pente de la première demi-heure\nsur la dernière")
    ax.yaxis.set_major_formatter(formateur(decimales=2))
    ax.legend(fontsize=8, ncols=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    return _fin(fig, "periodes", dossier)


def cout(table, dossier: Path = DOSSIER) -> list[Path]:
    """Ce que devient la stratégie quand on la facture."""
    appliquer()
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    for i, symbole in enumerate(dict.fromkeys(table["symbole"])):
        sous = table[table["symbole"] == symbole].sort_values("cout_pb")
        ax.plot(sous["cout_pb"], sous["annualise"], marker="o", lw=1.9,
                color=OKABE_ITO[i % len(OKABE_ITO)], label=symbole)
    ax.axhline(0, color=GRIS, lw=1.1, ls="--")
    ax.set_xlabel("coût par passage de marché, en points de base")
    ax.set_ylabel("rendement annualisé de la stratégie")
    ax.yaxis.set_major_formatter(formateur(decimales=0, suffixe=" %", facteur=100))
    ax.legend(fontsize=8, ncols=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    return _fin(fig, "cout", dossier)


def profil(table, dossier: Path = DOSSIER) -> list[Path]:
    """Le rendement moyen et la volatilité de chacune des treize demi-heures."""
    appliquer()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    fonds = [s for s in ("SPY", "QQQ", "IWM", "DIA") if s in set(table["symbole"])]
    for i, symbole in enumerate(fonds):
        sous = table[table["symbole"] == symbole].sort_values("demi_heure")
        axes[0].plot(sous["demi_heure"], sous["moyenne_pb"], marker="o", ms=4, lw=1.7,
                     color=OKABE_ITO[i % len(OKABE_ITO)], label=symbole)
        axes[1].plot(sous["demi_heure"], sous["volatilite_pb"], marker="o", ms=4, lw=1.7,
                     color=OKABE_ITO[i % len(OKABE_ITO)], label=symbole)
    axes[0].axhline(0, color=GRIS, lw=1.0, ls="--")
    axes[0].set_title("Rendement moyen", fontsize=10)
    axes[1].set_title("Volatilité", fontsize=10)
    for ax in axes:
        ax.set_xlabel("demi-heure de la séance")
        ax.set_xticks(range(1, DEMI_HEURES + 1))
        ax.yaxis.set_major_formatter(formateur(decimales=0, suffixe=" pb"))
    axes[0].set_ylabel("points de base")
    axes[0].legend(fontsize=8, ncols=4, frameon=False, loc="lower center",
                   bbox_to_anchor=(1.1, -0.42))
    return _fin(fig, "profil", dossier)
