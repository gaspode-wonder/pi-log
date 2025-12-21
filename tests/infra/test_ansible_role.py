import os
import yaml


def test_ansible_role_structure():
    assert os.path.exists("ansible/roles/pi_log/tasks/main.yml")
    assert os.path.exists("ansible/roles/pi_log/handlers/main.yml")
    assert os.path.exists("ansible/roles/pi_log/templates")


def test_ansible_role_tasks_are_valid_yaml():
    path = "ansible/roles/pi_log/tasks/main.yml"
    with open(path) as f:
        data = yaml.safe_load(f)

    assert isinstance(data, list)
    assert len(data) > 0
