import unittest
import yaml
import os
from unittest.mock import MagicMock, patch, call

from manager import Manager
from exceptions import AnsibleError


class TestManager(unittest.TestCase):
    def setUp(self):
        self.manager = Manager({"infrastructure": {}})

    def test_generate_playbook(self):
        with open("tests/unit_tests/example_infrastructure.yaml") as description_file:
            self.manager.infrastructure_description = yaml.safe_load(description_file).get("infrastructure")

        with open("tests/unit_tests/expected_playbook.yaml") as playbook_file:
            playbook = playbook_file.read()

        with patch("manager.open", unittest.mock.mock_open()) as m:
            self.manager._Manager__generate_playbook()
            handle = m()
            handle.write.assert_has_calls([call(playbook)])  # Check that correct files would be created

    def test_get_role_variables(self):
        with open("tests/unit_tests/example_infrastructure.yaml") as description_file:
            self.manager.infrastructure_description = yaml.safe_load(description_file).get("infrastructure")

        ret = self.manager._Manager__get_role_variables("interactive_c2_redirector")

        self.assertEqual(ret, {"ansible_user": "admin", "accept_from": ["147.251.0.0/16"],
                               "redirect_ports": [80], "redirect_to": "interactive_c2"})

    def test_add_variables_to_inventory(self):
        with open("tests/unit_tests/example_infrastructure.yaml") as description_file:
            self.manager.infrastructure_description = yaml.safe_load(description_file).get("infrastructure")

        self.manager.inventory_path = "tests/unit_tests/expected_hosts_post_orchestration.yaml"

        with open("tests/unit_tests/expected_hosts_post_orchestration.yaml") as hosts_before_file:
            old_hosts = hosts_before_file.read()

        with open("tests/unit_tests/expected_hosts.yaml") as hosts_file:
            hosts = hosts_file.read()

        self.manager._Manager__add_variables_to_inventory()

        with open("tests/unit_tests/expected_hosts_post_orchestration.yaml", "r+") as new_hosts:
            self.assertEqual(yaml.safe_load(hosts), yaml.safe_load(new_hosts))
            new_hosts.seek(0)
            new_hosts.write(old_hosts)
            new_hosts.truncate()

    @patch("manager.subprocess.run")
    def test_run_ansible(self, mock_run):
        fake_process = MagicMock()
        fake_process.returncode = 0
        mock_run.return_value = fake_process
        env = os.environ.copy()
        env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        env["ANSIBLE_ROLES_PATH"] = os.getcwd() + "/../roles"
        env["ANSIBLE_PYTHON_INTERPRETER"] = "/usr/bin/python3"
        self.manager.inventory_path = "hosts.yaml"

        self.manager._Manager__run_ansible()

        mock_run.assert_called_once_with("ansible-playbook playbook.yaml -i \"hosts.yaml\"", shell=True, env=env,
                                         capture_output=True)

    @patch("manager.subprocess.run")
    def test_run_ansible_failed(self, mock_run):
        fake_process = MagicMock()
        fake_process.returncode = 1
        mock_run.return_value = fake_process
        env = os.environ.copy()
        env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        env["ANSIBLE_ROLES_PATH"] = os.getcwd() + "/../roles"
        env["ANSIBLE_PYTHON_INTERPRETER"] = "/usr/bin/python3"
        self.manager.inventory_path = "hosts.yaml"

        with self.assertRaises(AnsibleError):
            self.manager._Manager__run_ansible()

            mock_run.assert_called_once_with("ansible-playbook playbook.yaml -i \"hosts.yaml\"", shell=True, env=env,
                                             capture_output=True)

    @patch("manager.Manager._Manager__generate_playbook")
    @patch("manager.Manager._Manager__add_variables_to_inventory")
    @patch("manager.Manager._Manager__run_ansible")
    def test_manage(self, mock_run, mock_add_variables, mock_generate_playbook):
        self.manager.manage()

        mock_run.assert_called_once()
        mock_add_variables.assert_called_once()
        mock_generate_playbook.assert_called_once()
