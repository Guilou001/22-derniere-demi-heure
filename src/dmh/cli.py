"""La ligne de commande : télécharger, contrôler le découpage, éprouver les affirmations."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from . import donnees, etudes, figures

app = typer.Typer(add_completion=False, help=__doc__)
TABLES = Path("results/tables")


def _ecrire(table, nom: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    chemin = TABLES / f"{nom}.csv"
    table.to_csv(chemin, index=False)
    typer.echo(f"  {chemin}  {len(table)} lignes")
    return chemin


def _tables():
    return {s: etudes.preparer(s) for s in donnees.TOUS}


@app.command()
def fetch() -> None:
    """Les barres d'une minute des huit fonds, de 2016 à aujourd'hui, flux consolidé."""
    for symbole, table in donnees.tout_telecharger().items():
        typer.echo(f"  {symbole}: {len(table):>9,} barres")


@app.command()
def controles() -> None:
    """L'identité que les treize demi-heures doivent vérifier, et le portrait de la séance."""
    tables = _tables()
    controle = etudes.controle_du_decoupage(tables)
    typer.echo(controle.to_string(index=False))
    _ecrire(controle, "controle_du_decoupage")
    profil = etudes.profil_des_demi_heures(tables)
    _ecrire(profil, "profil_des_demi_heures")
    figures.profil(profil)


@app.command()
def verdict() -> None:
    """L'affirmation de tête, éprouvée sur les huit fonds."""
    tables = _tables()
    table = etudes.predictibilite(tables)
    typer.echo(table[["symbole", "signal", "pente", "student", "r_deux", "annualise",
                      "sharpe", "seuil_pb"]].to_string(index=False))
    _ecrire(table, "predictibilite")
    resume = etudes.verdict(table)
    Path("results").mkdir(exist_ok=True)
    Path("results/verdict.json").write_text(json.dumps(resume, indent=2, default=str),
                                            encoding="utf-8")
    for cle, valeur in resume.items():
        typer.echo(f"  {cle:28} {valeur}")
    figures.huit_fonds(table)


@app.command()
def robustesse() -> None:
    """Les sous-périodes, le conditionnement, et ce qui dans la nuit porte le signal."""
    tables = _tables()
    actions = {k: tables[k] for k in ("SPY", "QQQ", "IWM", "DIA")}
    periodes = etudes.par_periode(actions, "r1")
    typer.echo(periodes[["symbole", "periode", "pente", "student", "observations"]]
               .to_string(index=False))
    _ecrire(periodes, "par_periode")
    _ecrire(etudes.conditionnement(actions, "r1"), "conditionnement")
    import pandas as pd

    nuit = pd.concat([etudes.decomposition_de_la_nuit(s)
                      for s in ("SPY", "QQQ", "IWM", "DIA")], ignore_index=True)
    _ecrire(nuit, "decomposition_de_la_nuit")
    typer.echo(nuit.to_string(index=False))
    figures.periodes(periodes)


@app.command()
def cout() -> None:
    """Ce que devient la stratégie quand on la facture, et la matrice complète."""
    tables = _tables()
    sensibilite = etudes.sensibilite_au_cout({k: tables[k] for k in ("SPY", "QQQ", "IWM", "DIA")})
    typer.echo(sensibilite[["symbole", "cout_pb", "annualise", "sharpe"]].to_string(index=False))
    _ecrire(sensibilite, "sensibilite_au_cout")
    matrice = etudes.matrice_de_predictibilite(tables["SPY"])
    _ecrire(matrice, "matrice_de_predictibilite")
    compte = etudes.nombre_de_cases_significatives(matrice)
    typer.echo(json.dumps(compte, indent=2))
    Path("results/matrice.json").write_text(json.dumps(compte, indent=2), encoding="utf-8")
    figures.cout(sensibilite)
    figures.matrice(matrice)


@app.command()
def tout() -> None:
    """Tout, dans l'ordre de la démonstration."""
    controles()
    verdict()
    robustesse()
    cout()


if __name__ == "__main__":      # pragma: no cover
    app()
