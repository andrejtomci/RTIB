import json
import yaml
import shutil
import os

from parse import compile
import python_terraform as tf

from exceptions import TerraformError


class Orchestrator:
    """
    A class providing configuration orchestration via Terraform.
    """
    terraform = tf.Terraform()

    def __init__(self, infrastructure_description: dict, verbose: bool = False) -> None:
        """
        Orchestrator constructor.

        :param infrastructure_description: dictionary containing infrastructure description
        :param verbose: if True, Terraform output gets printed.
        """
        self.infrastructure_description = infrastructure_description.get("infrastructure")
        self.verbose = verbose

    @staticmethod
    def __changed_infrastructure(apply_output: str) -> bool:
        """
        Checks whether "terraform apply" changed the infrastructure.

        :param apply_output: output of "terraform apply" command
        :return: True if infrastructure changed, False otherwise
        """
        for line in apply_output.split("\n"):
            if "Apply complete!" in line:
                return not all(changed == 0 for changed in [int(s) for s in line.split() if s.isdigit()])

    def __parse_description(self) -> None:
        """
        Parses infrastructure description into input files for Terraform.

        Modules description along with variables is written into "main.tf.json".
        Definition of outputs to capture is stored to "outputs.tf.json".
        """
        global_provider_args = self.infrastructure_description.get("global_arguments", {}).get("provider", {})
        instances = self.infrastructure_description.get("instances")

        modules_dict = {"module": {}}
        output_dict = {"output": {}}

        for instance_dict in instances:
            provider = instance_dict.get("provider")
            name = instance_dict.get("name")

            path = "../providers/{}".format(provider)
            module_dict = {"source": path, "name": name}
            module_dict.update(global_provider_args)

            arguments = instance_dict.get("arguments", {})
            for argument, value in arguments.get("provider", {}).items():
                module_dict.update({argument: value})

            modules_dict.get("module").update({name: module_dict})
            output_dict.get("output").update({name: {"value": "${{module.{}}}".format(name)}})

        main_json = json.dumps(modules_dict, indent=2)
        with open("main.tf.json", "w") as main_tf_json:
            main_tf_json.write(main_json)

        outputs_json = json.dumps(output_dict, indent=2)
        with open("outputs.tf.json", "w") as outputs_tf_json:
            outputs_tf_json.write(outputs_json)

    def __create_inventory(self) -> None:
        """
        Creates inventory file for later use by Ansible.

        The inventory is written into "hosts.yaml".
        """
        # None as empty string
        yaml.SafeDumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', ''))

        tf_output_dict = self.terraform.output(json=tf.IsFlagged)
        children = {}

        for module in tf_output_dict:
            module_dict = tf_output_dict.get(module)
            value_dict = module_dict.get("value")
            hosts = {host: {"ansible_ssh_private_key_file": "ssh_keys/{}_{}".format(module, i)}
                     for i, host in enumerate(value_dict.get("hosts"))}

            other_vars = {var: value for var, value in value_dict.items() if var != "hosts"}
            if other_vars:
                children.update({module: {"hosts": hosts, "vars": other_vars}})
            else:
                children.update({module: {"hosts": hosts, "vars": {}}})

        tf_output = yaml.safe_dump({"all": {"children": children}})
        with open("hosts.yaml", "w") as tf_output_yaml:
            tf_output_yaml.write(tf_output)

    def __list_resources(self) -> list:
        """
        Returns a list of resources orchestrated by Terraform.

        :return: list of resources
        """
        return self.terraform.state_cmd("list")[1].split('\n')

    def orchestrate_infrastructure(self) -> bool:
        """
        Parses infrastructure description, runs Terraform and creates an inventory file.

        If verbosity is set to True, also prints the Terraform output.

        :raises TerraformError: when Terraform error occurs
        :return: True if infrastructure changed, False otherwise
        """
        self.__parse_description()

        ret_init, out_init, err_init = self.terraform.init()
        if ret_init != 0:
            raise TerraformError(err_init)

        ret_apply, out_apply, err_apply = self.terraform.apply(skip_plan=True)
        if ret_apply != 0:
            raise TerraformError(err_apply)

        self.__create_inventory()

        if self.verbose:
            print(out_apply)

        return Orchestrator.__changed_infrastructure(out_apply)

    def destroy_infrastructure(self) -> None:
        """
        Destroys the infrastructure.

        If verbosity is set to True, also prints the Terraform output.

        :raises TerraformError: when Terraform error occurs
        """
        ret_destroy, out_destroy, err_destroy = self.terraform.destroy(force=tf.IsNotFlagged, auto_approve=tf.IsFlagged)
        if ret_destroy == 0:
            shutil.rmtree(os.getcwd())
        else:
            raise TerraformError(err_destroy)

        if self.verbose:
            print(out_destroy)

    def rebuild_instance(self, instance: str) -> None:
        """
        Rebuilds the specified instance.

        :param instance: name of the instance to rebuild
        :raises TerraformError: when Terraform error occurs
        """
        resources = self.__list_resources()
        parser = compile("module.{module_name}.{}")
        for resource in resources:
            if resource == "":
                continue
            parse_res = parser.parse(resource)
            if instance == parse_res["module_name"]:
                self.terraform.taint(resource)
        self.orchestrate_infrastructure()
