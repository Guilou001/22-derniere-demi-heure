# Prérequis : uv (https://docs.astral.sh/uv/)
UV ?= uv

setup:
	$(UV) sync --locked --all-extras

test:             ## 21 tests fermés, sans réseau ni données de marché
	$(UV) run pytest

lint:
	$(UV) run ruff check .

data:             ## les huit fonds, barres d'une minute de 2016 à aujourd'hui
	$(UV) run dmh fetch

all:              ## tout : le contrôle, le verdict, la robustesse, le coût
	$(UV) run dmh tout
