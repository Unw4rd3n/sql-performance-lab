SHELL := /bin/zsh

-include .env

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: venv up down seed run test

venv:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

up:
	docker compose up -d

down:
	docker compose down

seed: venv
	$(PY) scripts/seed_data.py

run: venv
	$(PY) scripts/run_benchmarks.py

test: venv
	$(VENV)/bin/pytest -q
