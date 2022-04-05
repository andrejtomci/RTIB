import unittest
import schema
from unittest.mock import MagicMock
from validator import Validator


class TestValidator(unittest.TestCase):
    def test_valid_complete_infrastructure(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test",
                                     "arguments": {"role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        validator.validate()

    def test_valid_missing_global_args(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test",
                                     "arguments": {"role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        validator.validate()

    def test_valid_missing_instance_args(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test"},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        validator.validate()

    def test_invalid_no_instances(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "instances": []}}
        validator = Validator(infrastructure_description)
        with self.assertRaises(schema.SchemaError):
            validator.validate()

    def test_invalid_unexpected_key(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "test_key": None,
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test",
                                     "arguments": {"role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        with self.assertRaises(schema.SchemaError):
            validator.validate()

    def test_invalid_space_in_instance_name(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "instances":
                                   [{"name": "test with space", "role": "test", "provider": "test",
                                     "arguments": {"role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        with self.assertRaises(schema.SchemaError):
            validator.validate()

    def test_invalid_key_in_global_args(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"},
                                                    "invalid key": None},
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test",
                                     "arguments": {"role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        with self.assertRaises(schema.SchemaError):
            validator.validate()

    def test_invalid_key_in_instance_args(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test",
                                     "arguments": {"bad_arg": None, "role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test2", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        with self.assertRaises(schema.SchemaError):
            validator.validate()

    def test_invalid_duplicate_instance_names(self):
        infrastructure_description = {
            "infrastructure": {"name": "test",
                               "global_arguments": {"role": {"arg": "val"},
                                                    "provider": {"arg": "val"}},
                               "instances":
                                   [{"name": "test", "role": "test", "provider": "test",
                                     "arguments": {"role": {"arg": "val"}, "provider": {"arg": "val"}}},
                                    {"name": "test", "role": "test2", "provider": "test2",
                                     "arguments": {"role": {"arg2": "val2"}, "provider": {"arg2": "val2"}}}]}}
        validator = Validator(infrastructure_description)
        with self.assertRaises(schema.SchemaError):
            validator.validate()
