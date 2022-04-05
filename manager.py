import yaml
import os
import subprocess

from exceptions import AnsibleError


class Manager:
    """
    A class providing configuration management via Ansible.
    """
    def __init__(self, infrastructure_description: dict, verbose: bool = False) -> None:
        """
        Manager constructor.

        :param infrastructure_description: dictionary containing infrastructure description
        :param verbose: if True, Ansible output gets printed.
        """
        self.infrastructure_description = infrastructure_description.get("infrastructure")
        self.verbose = verbose
        self.inventory_path = None

    def __generate_playbook(self) -> None:
        """
        Generates Ansible playbook from infrastructure description.

        The playbook is written into "playbook.yaml".
        """
        instances = self.infrastructure_description.get("instances")

        hosts_list = []
        for instance_dict in instances:
            name = instance_dict.get("name")
            role = instance_dict.get("role")
            hosts_list.append({"hosts": name, "roles": [role, "network"]})  # network role is applied to all instances

        playbook = yaml.safe_dump(hosts_list)
        with open("playbook.yaml", "w") as playbook_yaml:
            playbook_yaml.write(playbook)

    def __get_role_variables(self, name: str) -> dict:
        """
        Parses role variables from infrastructure description.

        :param name: name of the desired role
        :return: variables for given role
        """
        for instance_dict in self.infrastructure_description.get("instances"):
            if instance_dict.get("name") == name:
                return instance_dict.get("arguments").get("role")

    def __add_variables_to_inventory(self) -> None:
        """
        Adds variables from infrastructure description to inventory file.
        """
        # None as empty string
        yaml.SafeDumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', ''))

        with open(self.inventory_path) as inventory_file:
            inventory = yaml.safe_load(inventory_file)

        # Add vars from infrastructure description to existing vars in inventory
        for module, module_dict in inventory.get("all").get("children").items():
            module_vars = module_dict.get("vars")
            module_vars.update(self.__get_role_variables(module))

        # Add global vars from infrastructure description
        global_vars = {var: value for var, value in self.infrastructure_description.get("global_arguments", {}).get("role", {}).items()}
        inventory.get("all").update({"vars": global_vars})

        updated_inventory = yaml.safe_dump(inventory)
        with open(self.inventory_path, "w") as inventory_file:
            inventory_file.write(updated_inventory)

    def __run_ansible(self) -> None:
        """
        Sets environment variables and runs Ansible.

        If verbosity is set to True, also prints the Ansible output.

        :raises AnsibleError: when Ansible error occurs
        """
        cmd = 'ansible-playbook playbook.yaml -i "{}"'.format(self.inventory_path)
        env = os.environ.copy()
        env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        env["ANSIBLE_ROLES_PATH"] = os.getcwd() + "/../roles"
        env["ANSIBLE_PYTHON_INTERPRETER"] = "/usr/bin/python3"
        p = subprocess.run(cmd, shell=True, env=env, capture_output=not self.verbose)
        if p.returncode != 0:
            raise AnsibleError(p.stdout.decode("utf-8"), p.stderr.decode("utf-8"))

    def manage(self) -> None:
        """
        Generates playbook, adds variables to inventory file and runs Ansible.
        """
        self.__generate_playbook()
        self.__add_variables_to_inventory()
        self.__run_ansible()
