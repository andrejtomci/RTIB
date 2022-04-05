from schema import Schema, And, Optional, SchemaError


class Validator:
    """
    A class used for infrastructure description validation.
    """
    global_schema = Schema({"infrastructure": dict})
    infrastructure_schema = Schema({"name": str,
                                    "instances": And(list, lambda l: len(l) > 0,
                                                     error="There must be at least one instance"),
                                    Optional("global_arguments"): dict})
    arguments_schema = Schema({Optional("role"): dict,
                               Optional("provider"): dict})

    instance_schema = Schema(
        {"name": And(str, lambda name: " " not in name, error="Instance name cannot contain spaces"),
         "role": str,
         "provider": str,
         Optional("arguments"): dict})

    def __init__(self, infrastructure_description: dict) -> None:
        """
        Validator constructor.

        :param infrastructure_description: dictionary containing infrastructure description
        """
        self.infrastructure_description = infrastructure_description

    def validate(self) -> None:
        """
        Validates the infrastructure description.

        :raises SchemaError: when schema validation fails
        """
        self.global_schema.validate(self.infrastructure_description)
        self.infrastructure_schema.validate(self.infrastructure_description.get("infrastructure"))
        if self.infrastructure_description.get("infrastructure").get("global_arguments") is not None:
            self.arguments_schema.validate(self.infrastructure_description.get("infrastructure").get("global_arguments"))

        for instance in self.infrastructure_description.get("infrastructure").get("instances"):
            self.instance_schema.validate(instance)
            if instance.get("arguments") is not None:
                self.arguments_schema.validate(instance.get("arguments"))

        # check that instance names are unique
        names = [instance.get("name") for instance in self.infrastructure_description.get("infrastructure").get("instances")]
        if len(names) != len(set(names)):
            raise SchemaError("Instance names must be unique")
