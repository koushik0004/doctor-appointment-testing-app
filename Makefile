.DEFAULT_GOAL := help

SHELL := /bin/sh

BACKEND_DIR := backend
FRONTEND_DIR := frontend
RUN_DIR := .run
BACKEND_PID_FILE := $(RUN_DIR)/backend.pid
FRONTEND_PID_FILE := $(RUN_DIR)/frontend.pid
BACKEND_LOG_FILE := $(RUN_DIR)/backend.log
FRONTEND_LOG_FILE := $(RUN_DIR)/frontend.log

BOOTSTRAP_PYTHON_CANDIDATES ?= $(if $(CONDA_PREFIX),$(CONDA_PREFIX)/bin/python) python3.13 python3.12 python3.11 python3
BACKEND_VENV_DIR := $(BACKEND_DIR)/.venv
BACKEND_PYTHON := $(abspath $(BACKEND_VENV_DIR))/bin/python
BACKEND_PIP := $(abspath $(BACKEND_VENV_DIR))/bin/pip
BACKEND_APP := app.main:app
BACKEND_PORT ?= 4001
FRONTEND_PORT ?= 4002
FRONTEND_NPM ?= npm
SESSION_PYTHON ?= /usr/bin/python3

.PHONY: help setup backend-setup frontend-setup dev dev-detached stop backend-start frontend-start backend-stop frontend-stop backend-restart frontend-restart restart backend-dev frontend-dev

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make setup         Install backend dependencies first, then frontend dependencies' \
		'  make backend-setup Install backend dependencies only' \
		'  make frontend-setup Install frontend dependencies only' \
		'  make dev           Run backend and frontend together in the foreground' \
		'  make dev-detached  Start backend first, then start the frontend dev server in the background' \
		'  make stop          Stop both background servers started by make dev-detached' \
		'  make backend-restart Restart only the backend server in the background' \
		'  make frontend-restart Restart only the frontend server in the background' \
		'  make restart       Restart both servers in the background' \
		'  make backend-dev   Start only the backend dev server' \
		'  make frontend-dev  Start only the frontend dev server'

$(BACKEND_VENV_DIR):
	@set -e; \
	bootstrap_python=""; \
	venv_flags=""; \
	is_supported_version() { \
		major="$${1%%.*}"; \
		minor="$${1#*.}"; \
		[ "$$major" = 3 ] && [ "$$minor" -ge 11 ] && [ "$$minor" -le 13 ]; \
	}; \
	for candidate in $(BOOTSTRAP_PYTHON_CANDIDATES); do \
		if [ -n "$$candidate" ] && command -v "$$candidate" >/dev/null 2>&1; then \
			version="$$( "$$candidate" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' )"; \
			if is_supported_version "$$version"; then \
				bootstrap_python="$$candidate"; \
				break; \
			fi; \
		fi; \
	done; \
	if [ -z "$$bootstrap_python" ]; then \
		echo "No supported Python interpreter found. Need Python 3.11, 3.12, or 3.13."; \
		exit 1; \
	fi; \
	if [ -n "$${CONDA_PREFIX:-}" ] && [ "$$bootstrap_python" = "$${CONDA_PREFIX}/bin/python" ]; then \
		venv_flags="--system-site-packages"; \
	fi; \
	if [ -n "$$venv_flags" ]; then \
		"$$bootstrap_python" -m venv $$venv_flags "$(BACKEND_VENV_DIR)"; \
	else \
		"$$bootstrap_python" -m venv "$(BACKEND_VENV_DIR)"; \
	fi; \
	"$$bootstrap_python" -m ensurepip --upgrade >/dev/null

$(RUN_DIR):
	mkdir -p $(RUN_DIR)

backend-setup: $(BACKEND_VENV_DIR)
	@set -e; \
	bootstrap_python=""; \
	venv_flags=""; \
	is_supported_version() { \
		major="$${1%%.*}"; \
		minor="$${1#*.}"; \
		[ "$$major" = 3 ] && [ "$$minor" -ge 11 ] && [ "$$minor" -le 13 ]; \
	}; \
	if [ -x "$(BACKEND_PYTHON)" ]; then \
		current_version="$$( $(BACKEND_PYTHON) -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' )"; \
		if ! is_supported_version "$$current_version" || ! "$(BACKEND_PYTHON)" -m pip show setuptools wheel >/dev/null 2>&1; then \
			rm -rf "$(BACKEND_VENV_DIR)"; \
		fi; \
	fi; \
	if [ ! -x "$(BACKEND_PYTHON)" ]; then \
		for candidate in $(BOOTSTRAP_PYTHON_CANDIDATES); do \
			if [ -n "$$candidate" ] && command -v "$$candidate" >/dev/null 2>&1; then \
				version="$$( "$$candidate" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' )"; \
				if is_supported_version "$$version"; then \
					bootstrap_python="$$candidate"; \
					break; \
				fi; \
			fi; \
		done; \
		if [ -z "$$bootstrap_python" ]; then \
			echo "No supported Python interpreter found. Need Python 3.11, 3.12, or 3.13."; \
			exit 1; \
		fi; \
		if [ -n "$${CONDA_PREFIX:-}" ] && [ "$$bootstrap_python" = "$${CONDA_PREFIX}/bin/python" ]; then \
			venv_flags="--system-site-packages"; \
		fi; \
		if [ -n "$$venv_flags" ]; then \
			"$$bootstrap_python" -m venv $$venv_flags "$(BACKEND_VENV_DIR)"; \
		else \
			"$$bootstrap_python" -m venv "$(BACKEND_VENV_DIR)"; \
		fi; \
		"$$bootstrap_python" -m ensurepip --upgrade >/dev/null; \
	fi; \
	cd $(BACKEND_DIR) && $(BACKEND_PIP) install --no-build-isolation -e ".[dev]"

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
		stale_pid="$$(lsof -tiTCP:$(BACKEND_PORT) -sTCP:LISTEN 2>/dev/null | head -n 1 || true)"; \
		if [ -n "$$stale_pid" ]; then \
			echo "Stopping stale backend listener on port $(BACKEND_PORT) (pid $$stale_pid)."; \
			kill -TERM "-$$stale_pid" 2>/dev/null || kill -TERM "$$stale_pid" 2>/dev/null || true; \
			sleep 1; \
			if lsof -tiTCP:$(BACKEND_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
				kill -KILL "-$$stale_pid" 2>/dev/null || kill -KILL "$$stale_pid" 2>/dev/null || true; \
			fi; \
		fi; \
		cd $(BACKEND_DIR); \
		nohup $(SESSION_PYTHON) -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' "$(BACKEND_PYTHON)" -m uvicorn $(BACKEND_APP) --host 0.0.0.0 --port $(BACKEND_PORT) > "../$(BACKEND_LOG_FILE)" 2>&1 < /dev/null & \
		backend_pid=$$!; \
		cd ..; \
		echo "$$backend_pid" > "$(BACKEND_PID_FILE)"; \
		echo "Starting backend on http://127.0.0.1:$(BACKEND_PORT) ..."; \
	fi; \
	for _ in $$(seq 1 60); do \
		if curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/health >/dev/null 2>&1; then \
			break; \
		fi; \
		sleep 1; \
	done; \
	if ! curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/health >/dev/null 2>&1; then \
		rm -f "$(BACKEND_PID_FILE)"; \
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
		stale_pid="$$(lsof -tiTCP:$(FRONTEND_PORT) -sTCP:LISTEN 2>/dev/null | head -n 1 || true)"; \
		if [ -n "$$stale_pid" ]; then \
			echo "Stopping stale frontend listener on port $(FRONTEND_PORT) (pid $$stale_pid)."; \
			kill -TERM "-$$stale_pid" 2>/dev/null || kill -TERM "$$stale_pid" 2>/dev/null || true; \
			sleep 1; \
			if lsof -tiTCP:$(FRONTEND_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
				kill -KILL "-$$stale_pid" 2>/dev/null || kill -KILL "$$stale_pid" 2>/dev/null || true; \
			fi; \
		fi; \
		cd $(FRONTEND_DIR); \
		nohup $(SESSION_PYTHON) -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' "$(FRONTEND_NPM)" run dev -- -H 0.0.0.0 > "../$(FRONTEND_LOG_FILE)" 2>&1 < /dev/null & \
		frontend_pid=$$!; \
		cd ..; \
		echo "$$frontend_pid" > "$(FRONTEND_PID_FILE)"; \
		echo "Starting frontend on http://127.0.0.1:$(FRONTEND_PORT) ..."; \
	fi; \
	for _ in $$(seq 1 60); do \
		if curl -fsS http://127.0.0.1:$(FRONTEND_PORT) >/dev/null 2>&1; then \
			break; \
		fi; \
		sleep 1; \
	done; \
	if ! curl -fsS http://127.0.0.1:$(FRONTEND_PORT) >/dev/null 2>&1; then \
		rm -f "$(FRONTEND_PID_FILE)"; \
		echo "Frontend did not become ready. See $(FRONTEND_LOG_FILE)"; \
		exit 1; \
	fi

backend-dev:
	cd $(BACKEND_DIR) && $(BACKEND_PYTHON) -m uvicorn $(BACKEND_APP) --host 0.0.0.0 --port $(BACKEND_PORT)

frontend-dev:
	cd $(FRONTEND_DIR) && $(FRONTEND_NPM) run dev

dev:
	@set -e; \
	trap 'kill $$backend_pid $$frontend_pid 2>/dev/null || true; wait $$backend_pid $$frontend_pid 2>/dev/null || true' INT TERM EXIT; \
	cd $(BACKEND_DIR) && $(BACKEND_PYTHON) -m uvicorn $(BACKEND_APP) --host 0.0.0.0 --port $(BACKEND_PORT) & \
	backend_pid=$$!; \
	for _ in $$(seq 1 60); do \
		if curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/health >/dev/null 2>&1; then \
			break; \
		fi; \
		sleep 1; \
	done; \
	if ! curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/health >/dev/null 2>&1; then \
		echo "Backend did not become ready."; \
		exit 1; \
	fi; \
	cd $(FRONTEND_DIR) && $(FRONTEND_NPM) run dev -- -H 0.0.0.0 & \
	frontend_pid=$$!; \
	wait $$backend_pid $$frontend_pid

dev-detached:
	@$(MAKE) --no-print-directory backend-start && $(MAKE) --no-print-directory frontend-start && printf '%s\n' \
		"Backend log: $(BACKEND_LOG_FILE)" \
		"Frontend log: $(FRONTEND_LOG_FILE)"

backend-stop: $(RUN_DIR)
	@set -e; \
	if [ -f "$(BACKEND_PID_FILE)" ]; then \
		pid=$$(cat "$(BACKEND_PID_FILE)"); \
		if kill -0 "$$pid" 2>/dev/null; then \
			kill -TERM "-$$pid" 2>/dev/null || kill -TERM "$$pid" 2>/dev/null || true; \
			for _ in $$(seq 1 10); do \
				if ! kill -0 "$$pid" 2>/dev/null; then \
					break; \
				fi; \
				sleep 1; \
			done; \
			if kill -0 "$$pid" 2>/dev/null; then \
				kill -KILL "-$$pid" 2>/dev/null || kill -KILL "$$pid" 2>/dev/null || true; \
			fi; \
			echo "Stopped backend (pid $$pid)."; \
		else \
			echo "No running backend process."; \
		fi; \
		rm -f "$(BACKEND_PID_FILE)"; \
	fi; \
	stale_pid="$$(lsof -tiTCP:$(BACKEND_PORT) -sTCP:LISTEN 2>/dev/null | head -n 1 || true)"; \
	if [ -n "$$stale_pid" ]; then \
		echo "Stopping stale backend listener on port $(BACKEND_PORT) (pid $$stale_pid)."; \
		kill -TERM "-$$stale_pid" 2>/dev/null || kill -TERM "$$stale_pid" 2>/dev/null || true; \
		sleep 1; \
		if lsof -tiTCP:$(BACKEND_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
			kill -KILL "-$$stale_pid" 2>/dev/null || kill -KILL "$$stale_pid" 2>/dev/null || true; \
		fi; \
	fi

frontend-stop: $(RUN_DIR)
	@set -e; \
	if [ -f "$(FRONTEND_PID_FILE)" ]; then \
		pid=$$(cat "$(FRONTEND_PID_FILE)"); \
		if kill -0 "$$pid" 2>/dev/null; then \
			kill -TERM "-$$pid" 2>/dev/null || kill -TERM "$$pid" 2>/dev/null || true; \
			for _ in $$(seq 1 10); do \
				if ! kill -0 "$$pid" 2>/dev/null; then \
					break; \
				fi; \
				sleep 1; \
			done; \
			if kill -0 "$$pid" 2>/dev/null; then \
				kill -KILL "-$$pid" 2>/dev/null || kill -KILL "$$pid" 2>/dev/null || true; \
			fi; \
			echo "Stopped frontend (pid $$pid)."; \
		else \
			echo "No running frontend process."; \
		fi; \
		rm -f "$(FRONTEND_PID_FILE)"; \
	fi; \
	stale_pid="$$(lsof -tiTCP:$(FRONTEND_PORT) -sTCP:LISTEN 2>/dev/null | head -n 1 || true)"; \
	if [ -n "$$stale_pid" ]; then \
		echo "Stopping stale frontend listener on port $(FRONTEND_PORT) (pid $$stale_pid)."; \
		kill -TERM "-$$stale_pid" 2>/dev/null || kill -TERM "$$stale_pid" 2>/dev/null || true; \
		sleep 1; \
		if lsof -tiTCP:$(FRONTEND_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
			kill -KILL "-$$stale_pid" 2>/dev/null || kill -KILL "$$stale_pid" 2>/dev/null || true; \
		fi; \
	fi

stop:
	@$(MAKE) --no-print-directory frontend-stop && $(MAKE) --no-print-directory backend-stop

backend-restart:
	@$(MAKE) --no-print-directory backend-stop && $(MAKE) --no-print-directory backend-start

frontend-restart:
	@$(MAKE) --no-print-directory frontend-stop && $(MAKE) --no-print-directory frontend-start

restart:
	@$(MAKE) --no-print-directory stop && $(MAKE) --no-print-directory dev-detached
