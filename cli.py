import os
import time
import yaml
from pathlib import Path

import click

from orchestrator import Orchestrator
from manager import Manager
from validator import Validator


class CLI:
    def __init__(self, infrastructure_description_file, verbose):
        self.infrastructure_description = self.read_infrastructure_description(infrastructure_description_file)
        self.validator = Validator(self.infrastructure_description)
        self.orchestrator = Orchestrator(self.infrastructure_description, verbose)
        self.manager = Manager(self.infrastructure_description, verbose)

    @staticmethod
    def read_infrastructure_description(infrastructure_description):
        with open(infrastructure_description) as description:
            return yaml.safe_load(description)


@click.group(invoke_without_command=True)
@click.option("-v", "--verbose", is_flag=True, help="Print terraform and ansible outputs")
@click.argument("infrastructure", type=click.Path(exists=True))
@click.pass_context
def main(ctx, infrastructure, verbose):
    """
    Tool for configuration orchestration (terraform) and management (ansible).

    If no command is specified, validation, orchestration and management are run.

    INFRASTRUCTURE is the name of the file that contains infrastructure description.
    """
    ctx.obj = CLI(infrastructure, verbose)
    if ctx.invoked_subcommand != "validate":

        ctx.obj.validator.validate()
        print("VALIDATION OK")

        working_dir = ctx.obj.infrastructure_description.get("infrastructure").get("name")
        Path(working_dir).mkdir(exist_ok=True)
        Path(working_dir + "/ssh_keys").mkdir(exist_ok=True, mode=0o700)
        os.chdir(working_dir)
        ctx.obj.manager.inventory_path = os.getcwd() + "/hosts.yaml"

    if ctx.invoked_subcommand is None:
        if ctx.obj.orchestrator.orchestrate_infrastructure():
            print("WAITING 60 SECONDS FOR MACHINES TO BOOT...")
            time.sleep(60)
        print("CONFIGURATION ORCHESTRATION DONE")

        ctx.obj.manager.manage()
        print("CONFIGURATION MANAGEMENT DONE")


@main.command()
@click.pass_obj
def validate(ctx):
    """
    Validates the infrastructure description
    """
    ctx.validator.validate()
    print("VALIDATION OK")


@main.command()
@click.pass_obj
def orchestrate(cli_obj):
    """
    Runs configuration orchestration (terraform)
    """
    cli_obj.orchestrator.orchestrate_infrastructure()
    print("CONFIGURATION ORCHESTRATION DONE")


@main.command()
@click.argument("inventory_file")
@click.pass_obj
def manage(cli_obj, inventory_file):
    """
    Runs configuration management (ansible)
    """
    cli_obj.manager.inventory_path = "../" + inventory_file
    cli_obj.manager.manage()
    print("CONFIGURATION MANAGEMENT DONE")


@main.command()
@click.pass_obj
def destroy(cli_obj):
    """
    Destroys the infrastructure
    """
    cli_obj.orchestrator.destroy_infrastructure()
    print("DESTROY DONE")


@main.command()
@click.argument("instance")
@click.pass_obj
def rebuild(cli_obj, instance):
    """
    Rebuilds a single instance in the infrastructure
    """
    cli_obj.orchestrator.rebuild_instance(instance)
    print("REBUILD DONE")
    print("WAITING 60 SECONDS FOR MACHINES TO BOOT...")
    time.sleep(60)
    cli_obj.manager.manage()
    print("CONFIGURATION MANAGEMENT DONE")


if __name__ == '__main__':
    main()
