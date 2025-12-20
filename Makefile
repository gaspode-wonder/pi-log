.PHONY: install start stop restart status logs db-shell

install:
    sudo bash scripts/setup.sh

start:
    sudo systemctl start geiger

stop:
    sudo systemctl stop geiger

restart:
    sudo systemctl restart geiger

status:
    sudo systemctl status geiger

logs:
    sudo journalctl -u geiger -f

db-shell:
    sqlite3 /var/lib/geiger/geiger.db

venv:
    python3 -m venv .venv

activate:
    @echo "Run: source .venv/bin/activate"

install:
    .venv/bin/pip install -r requirements.txt

freeze:
    .venv/bin/pip freeze > requirements.txt
