.PHONY: setup figures figures-paper figures-extension test notebook clean lint all

PYTHON ?= python3
VENV   ?= .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

setup: $(VENV)/bin/activate

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

# Fig. 2-8: exact reproduction of the paper's M=2 figures.
figures-paper: setup
	mkdir -p results
	$(PY) -m experiments.fig2_time_headway
	$(PY) -m experiments.fig3_zoom
	$(PY) -m experiments.fig4_tour_time
	$(PY) -m experiments.fig5_zoom
	$(PY) -m experiments.fig6_return_map
	$(PY) -m experiments.fig7_mean_rms
	$(PY) -m experiments.fig8_phase_diagram

# Fig. 9-11: our own M=3 extension (not in the paper). See README "Extension".
figures-extension: setup
	mkdir -p results
	$(PY) -m experiments.fig9_three_bus_bifurcation
	$(PY) -m experiments.fig10_three_bus_returnmap
	$(PY) -m experiments.fig11_three_bus_phase

figures: figures-paper figures-extension

test: setup
	$(PY) -m pytest

notebook: setup
	$(VENV)/bin/jupyter lab notebooks/reproduction.ipynb

lint: setup
	$(VENV)/bin/ruff check src experiments tests

clean:
	rm -rf results/*.png $(VENV) **/__pycache__ .pytest_cache

all: figures test
