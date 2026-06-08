.DEFAULT_GOAL := help

SHELL := /bin/sh

BACKEND_DIR := backend
FRONTEND_DIR := frontend
RUN_DIR := .run
BACKEND_PID_FILE := $(RUN_DIR)/backend.pid
FRONTEND_PID_FILE := $(RUN_DIR)/frontend.pid
BACKEND_LOG_FILE := $(RUN_DIR)/backend.log
FRONTEND_LOG_FILE := $(RUN_DIR)/frontend.log

BOOTSTRAP_PYTHON ?= python3.12
BACKEND_VENV_DIR := $(BACKEND_DIR)/.venv
BACKEND_PYTHON := $(BACKEND_VENV_DIR)/bin/python
BACKEND_PIP := $(BACKEND_VENV_DIR)/bin/pip
BACKEND_APP := app.main:app
BACKEND_PORT ?= 4001
FRONTEND_PORT ?= 4002
FRONTEND_NPM ?= npm

.PHONY: help setup backend-setup frontend-setup dev stop backend-start frontend-start backend-stop frontend-stop backend-restart frontend-restart restart backend-dev frontend-dev

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make setup         Install backend dependencies first, then frontend dependencies' \
		'  make backend-setup Install backend dependencies only' \
		'  make frontend-setup Install frontend dependencies only' \
		'  make dev           Start backend first, then start the frontend dev server in the background' \
		'  make stop          Stop both background servers started by make dev' \
		'  make backend-restart Restart only the backend server in the background' \
		'  make frontend-restart Restart only the frontend server in the background' \
		'  make restart       Restart both servers in the background' \
		'  make backend-dev   Start only the backend dev server' \
		'  make frontend-dev  Start only the frontend dev server'

$(BACKEND_VENV_DIR):
	$(BOOTSTRAP_PYTHON) -m venv $(BACKEND_VENV_DIR)

$(RUN_DIR):
	mkdir -p $(RUN_DIR)

backend-setup: $(BACKEND_VENV_DIR)
	cd $(BACKEND_DIR) && .venv/bin/python -m pip install --upgrade pip
	cd $(BACKEND_DIR) && .venv/bin/pip install -e ".[dev]"

frontend-setup:
	cd $(FRONTEND_DIR) && $(FRONTEND_NPM) install

setup: backend-setup frontend-setup

backend-start: $(RUN_DIR)
	@set -e; \
	backend_pid=""; \
	if [ -f "$(BACKEND_PID_FILE)" ]; then backend_pid="$$(cat "$(BACKEND_PID_FILE)")"; fi; \
	if [ -n "$$backend_pid" ] && kill -0 "$$backend_pid" 2>/dev/null; then \
		echo "Backend is already running (pid $$backend_pid)."; \
	else \
		cd $(BACKEND_DIR) && nohup sh -c 'exec .venv/bin/python -m uvicorn $(BACKEND_APP) --host 0.0.0.0 --port $(BACKEND_PORT)' > "../$(BACKEND_LOG_FILE)" 2>&1 < /dev/null & \
		echo $$! > "$(BACKEND_PID_FILE)"; \
		echo "Starting backend on http://127.0.0.1:$(BACKEND_PORT) ..."; \
	fi; \
	for _ in $$(seq 1 60); do \
		if curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/health >/dev/null 2>&1; then \
			break; \
		fi; \
		sleep 1; \
	done; \
	if ! curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/health >/dev/null 2>&1; then \
		echo "Backend did not become ready. See $(BACKEND_LOG_FILE)"; \
		exit 1; \
	fi

frontend-start: $(RUN_DIR)
	@set -e; \
	frontend_pid=""; \
	if [ -f "$(FRONTEND_PID_FILE)" ]; then frontend_pid="$$(cat "$(FRONTEND_PID_FILE)")"; fi; \
	if [ -n "$$frontend_pid" ] && kill -0 "$$frontend_pid" 2>/dev/null; then \
		echo "Frontend is already running (pid $$frontend_pid)."; \
	else \
		cd $(FRONTEND_DIR) && nohup sh -c 'exec $(FRONTEND_NPM) run dev -- -H 0.0.0.0' > "../$(FRONTEND_LOG_FILE)" 2>&1 < /dev/null & \
		echo $$! > "$(FRONTEND_PID_FILE)"; \
		echo "Starting frontend on http://127.0.0.1:$(FRONTEND_PORT) ..."; \
	fi

backend-dev:
	cd $(BACKEND_DIR) && .venv/bin/python -m uvicorn $(BACKEND_APP) --host 0.0.0.0 --port $(BACKEND_PORT)

frontend-dev:
	cd $(FRONTEND_DIR) && $(FRONTEND_NPM) run dev

dev:
	@$(MAKE) --no-print-directory backend-start && $(MAKE) --no-print-directory frontend-start && printf '%s\n' \
		"Backend log: $(BACKEND_LOG_FILE)" \
		"Frontend log: $(FRONTEND_LOG_FILE)"

backend-stop: $(RUN_DIR)
	@set -e; \
	if [ -f "$(BACKEND_PID_FILE)" ]; then \
		pid=$$(cat "$(BACKEND_PID_FILE)"); \
		if kill -0 "$$pid" 2>/dev/null; then \
			kill "$$pid"; \
			for _ in $$(seq 1 10); do \
				if ! kill -0 "$$pid" 2>/dev/null; then \
					break; \
				fi; \
				sleep 1; \
			done; \
			if kill -0 "$$pid" 2>/dev/null; then \
				kill -9 "$$pid"; \
			fi; \
			echo "Stopped backend (pid $$pid)."; \
		else \
			echo "No running backend process."; \
		fi; \
		rm -f "$(BACKEND_PID_FILE)"; \
	fi

frontend-stop: $(RUN_DIR)
	@set -e; \
	if [ -f "$(FRONTEND_PID_FILE)" ]; then \
		pid=$$(cat "$(FRONTEND_PID_FILE)"); \
		if kill -0 "$$pid" 2>/dev/null; then \
			kill "$$pid"; \
			for _ in $$(seq 1 10); do \
				if ! kill -0 "$$pid" 2>/dev/null; then \
					break; \
				fi; \
				sleep 1; \
			done; \
			if kill -0 "$$pid" 2>/dev/null; then \
				kill -9 "$$pid"; \
			fi; \
			echo "Stopped frontend (pid $$pid)."; \
		else \
			echo "No running frontend process."; \
		fi; \
		rm -f "$(FRONTEND_PID_FILE)"; \
	fi

stop:
	@$(MAKE) --no-print-directory frontend-stop && $(MAKE) --no-print-directory backend-stop

backend-restart:
	@$(MAKE) --no-print-directory backend-stop && $(MAKE) --no-print-directory backend-start

frontend-restart:
	@$(MAKE) --no-print-directory frontend-stop && $(MAKE) --no-print-directory frontend-start

restart:
	@$(MAKE) --no-print-directory stop && $(MAKE) --no-print-directory dev
