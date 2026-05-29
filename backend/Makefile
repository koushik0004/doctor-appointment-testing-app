.DEFAULT_GOAL := help

SHELL := /bin/sh

VENV_DIR := .venv
BOOTSTRAP_PYTHON ?= python3.12
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
APP_MODULE := app.main:app
PORT ?= 4001

.PHONY: help venv upgrade-pip install setup run dev

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make venv        Create the local virtual environment' \
		'  make upgrade-pip  Upgrade pip inside the virtual environment' \
		'  make install      Install backend dependencies' \
		'  make setup        Create the venv and install dependencies' \
		'  make run          Start the FastAPI server with Uvicorn' \
		'  make dev          Alias for make run'

venv:
	$(BOOTSTRAP_PYTHON) -m venv $(VENV_DIR)

upgrade-pip: venv
	$(PYTHON) -m pip install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt

setup: upgrade-pip install

run: install
	$(PYTHON) -m uvicorn $(APP_MODULE) --reload --port $(PORT)

dev: run
