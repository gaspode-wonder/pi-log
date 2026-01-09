# ------------------------------------------------------------
# pi-log Unified Makefile (Python + Ansible + Pi Ops)
# ------------------------------------------------------------

PI_HOST=beamrider-0001.local
PI_USER=jeb

ANSIBLE_DIR=ansible
INVENTORY=$(ANSIBLE_DIR)/inventory.ini
PLAYBOOK=$(ANSIBLE_DIR)/deploy.yml
ROLE_DIR=$(ANSIBLE_DIR)/roles/pi_log
SERVICE=pi-log

PYTHON := /opt/homebrew/bin/python3.12
VENV := .venv

# ------------------------------------------------------------
# Help
# ------------------------------------------------------------

help: ## Show help
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""

.PHONY: help

# ------------------------------------------------------------
# Python environment
# ------------------------------------------------------------

bootstrap: ## Create venv and install dependencies (first-time setup)
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "Bootstrap complete. Activate with: source $(VENV)/bin/activate"

install: check-venv ## Install dependencies into existing venv
	$(VENV)/bin/pip install -r requirements.txt

freeze: ## Freeze dependencies to requirements.txt
	$(VENV)/bin/pip freeze > requirements.txt

check-venv:
	@test -n "$$VIRTUAL_ENV" || (echo "ERROR: .venv not activated"; exit 1)

run: check-venv ## Run ingestion loop locally
	$(VENV)/bin/python -m app.ingestion_loop

clean-pyc:
	find . -type d -name "__pycache__" -exec rm -rf {} +

# ------------------------------------------------------------
# Linting, type checking, tests
# ------------------------------------------------------------

lint: check-venv ## Run ruff lint + ruff format check
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

typecheck: check-venv ## Run mypy type checking
	$(VENV)/bin/mypy app

test: check-venv ## Run pytest suite
	$(VENV)/bin/pytest -q

ci: clean-pyc check-venv ## Run full local CI suite (lint + typecheck + tests)
	$(VENV)/bin/ruff check .
	$(VENV)/bin/mypy .
	$(VENV)/bin/pytest -q
	@echo ""
	@echo "✔ Local CI passed"

# ------------------------------------------------------------
# Deployment to Raspberry Pi (via Ansible)
# ------------------------------------------------------------

check-ansible: ## Validate Ansible syntax, inventory, lint, and dry-run
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --syntax-check
	ansible-inventory -i $(INVENTORY) --list >/dev/null
	ansible-lint $(ANSIBLE_DIR)
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --check

deploy: ## Deploy to Raspberry Pi via Ansible
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK)

# ------------------------------------------------------------
# Pi service management
# ------------------------------------------------------------

restart: ## Restart pi-log service on the Pi
	ansible pi1 -i $(INVENTORY) -m systemd -a "name=$(SERVICE) state=restarted"

start: ## Start pi-log service
	ansible pi1 -i $(INVENTORY) -m systemd -a "name=$(SERVICE) state=started"

stop: ## Stop pi-log service
	ansible pi1 -i $(INVENTORY) -m systemd -a "name=$(SERVICE) state=stopped"

status: ## Show pi-log systemd status
	ssh $(PI_USER)@$(PI_HOST) "systemctl status $(SERVICE)"

logs: ## Show last 50 log lines
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u $(SERVICE) -n 50"

tail: ## Follow live logs
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u $(SERVICE) -f"

db-shell: ## Open SQLite shell on the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo sqlite3 /opt/pi-log/readings.db"

# ------------------------------------------------------------
# Pi health + maintenance
# ------------------------------------------------------------

ping: ## Ping the Raspberry Pi via Ansible
	ansible pi1 -i $(INVENTORY) -m ping

hosts: ## Show parsed Ansible inventory
	ansible-inventory -i $(INVENTORY) --list

ssh: ## SSH into the Raspberry Pi
	ssh $(PI_USER)@$(PI_HOST)

doctor: ## Run full environment + Pi health checks
	@echo "Checking Python..."; python3 --version; echo ""
	@echo "Checking virtual environment..."; \
		[ -d ".venv" ] && echo "venv OK" || echo "venv missing"; echo ""
	@echo "Checking Python dependencies..."; $(VENV)/bin/pip --version; echo ""
	@echo "Checking Ansible..."; ansible --version; \
		ansible-inventory -i $(INVENTORY) --list >/dev/null && echo "Inventory OK"; echo ""
	@echo "Checking SSH connectivity..."; \
		ssh -o BatchMode=yes -o ConnectTimeout=5 $(PI_USER)@$(PI_HOST) "echo SSH OK" || echo "SSH FAILED"; echo ""
	@echo "Checking systemd service..."; \
		ssh $(PI_USER)@$(PI_HOST) "systemctl is-active $(SERVICE)" || true

clean: ## Remove virtual environment and Python cache files
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

reset-pi: ## Wipe /opt/pi-log on the Pi and redeploy
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl stop $(SERVICE) || true"
	ssh $(PI_USER)@$(PI_HOST) "sudo rm -rf /opt/pi-log/*"
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK)
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl restart $(SERVICE)"

# ------------------------------------------------------------
# Patch utilities
# ------------------------------------------------------------

apply-patch: ## Apply a patch: make apply-patch FILE=YYYYMMDD-slug.patch
	@if [ -z "$(FILE)" ]; then \
		echo "ERROR: You must specify FILE=<YYYYMMDD-slug.patch>"; exit 1; \
	fi
	git apply patches/$(FILE)

diff: ## Generate a patch of uncommitted changes
	@mkdir -p patches
	@ts=$$(date +"%Y%m%d"); \
		git diff > patches/$$ts-changes.patch; \
		echo "Created patches/$$ts-changes.patch"

# ------------------------------------------------------------
# Delegation to ansible/Makefile (optional)
# ------------------------------------------------------------

ansible-deploy: ## Run ansible/Makefile deploy
	cd ansible && make deploy
