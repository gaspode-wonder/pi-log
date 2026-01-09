# ----------------------------------------
# Ansible Deployment & Role Dev Makefile
# ----------------------------------------

INVENTORY=inventory.ini
PLAYBOOK=deploy.yml
ROLE_DIR=roles/pi_log
SCENARIO=default
SERVICE=pi-log.service

.PHONY: deploy restart start stop status logs tail lint converge verify destroy test idempotence

# -------------------------
# Deployment Commands
# -------------------------

deploy:
    ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags pi_log --diff

start:
    ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=started"

stop:
    ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=stopped"

restart:
    ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=restarted"

status:
    ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=started"

logs:
    ansible -i $(INVENTORY) all -m shell -a "journalctl -u $(SERVICE) -n 50"

tail:
    ansible -i $(INVENTORY) all -m shell -a "journalctl -u $(SERVICE) -f"

# -------------------------
# Role Development (Molecule)
# -------------------------

lint:
    ansible-lint $(ROLE_DIR)

converge:
    cd $(ROLE_DIR) && molecule converge -s $(SCENARIO)

verify:
    cd $(ROLE_DIR) && molecule verify -s $(SCENARIO)

destroy:
    cd $(ROLE_DIR) && molecule destroy -s $(SCENARIO)

test:
    cd $(ROLE_DIR) && molecule test -s $(SCENARIO)

idempotence:
    cd $(ROLE_DIR) && molecule converge -s $(SCENARIO)
    cd $(ROLE_DIR) && molecule idempotence -s $(SCENARIO)
