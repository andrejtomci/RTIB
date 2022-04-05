import unittest
import yaml
import json
from unittest.mock import MagicMock, patch, call

from orchestrator import Orchestrator
from exceptions import TerraformError


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator({"infrastructure": {}})

    def test_changed_infrastructure_added(self):
        tf_output = "dummy out\nApply complete! Resources: 22 added, 0 changed, 0 destroyed. \ndummy out"
        self.assertTrue(self.orchestrator._Orchestrator__changed_infrastructure(tf_output))

    def test_changed_infrastructure_changed(self):
        tf_output = "dummy out\nApply complete! Resources: 0 added, 2 changed, 0 destroyed. \ndummy out"
        self.assertTrue(self.orchestrator._Orchestrator__changed_infrastructure(tf_output))

    def test_changed_infrastructure_destroyed(self):
        tf_output = "dummy out\nApply complete! Resources: 0 added, 0 changed, 5 destroyed. \ndummy out"
        self.assertTrue(self.orchestrator._Orchestrator__changed_infrastructure(tf_output))

    def test_changed_infrastructure_not_changed(self):
        tf_output = "dummy out\nApply complete! Resources: 0 added, 0 changed, 0 destroyed. \ndummy out"
        self.assertFalse(self.orchestrator._Orchestrator__changed_infrastructure(tf_output))

    def test_parse_description(self):
        with open("tests/unit_tests/example_infrastructure.yaml") as description_file:
            self.orchestrator.infrastructure_description = yaml.safe_load(description_file).get("infrastructure")

        with open("tests/unit_tests/expected_main.tf.json") as main_tf:
            main_json = main_tf.read()

        with open("tests/unit_tests/expected_outputs.tf.json") as outputs_tf:
            outputs_json = outputs_tf.read()

        with patch("orchestrator.open", unittest.mock.mock_open()) as m:
            self.orchestrator._Orchestrator__parse_description()
            handle = m()
            handle.write.assert_has_calls(
                [call(main_json), call(outputs_json)])  # Check that correct files would be created

    @patch("orchestrator.Orchestrator.terraform.output")
    def test_create_inventory(self, mock_tf_output):
        with open("tests/unit_tests/example_infrastructure.yaml") as description_file:
            self.orchestrator.infrastructure_description = yaml.safe_load(description_file).get("infrastructure")

        with open("tests/unit_tests/expected_hosts_post_orchestration.yaml") as inventory_file:
            hosts = inventory_file.read()

        with open("tests/unit_tests/terraform_output") as tf_out:
            tf_out_json = json.load(tf_out)

        mock_tf_output.return_value = tf_out_json

        with patch("orchestrator.open", unittest.mock.mock_open()) as m:
            self.orchestrator._Orchestrator__create_inventory()
            handle = m()
            handle.write.assert_has_calls([call(hosts)])  # Check that expected inventory file would be created

    @patch("orchestrator.Orchestrator.terraform.state_cmd")
    def test_list_resources(self, mock_tf_state):
        with open("tests/unit_tests/terraform_state_out") as tf_state_file:
            tf_state = tf_state_file.read()

        tf_state_list = tf_state.split("\n")
        mock_tf_state.return_value = (0, tf_state, None)

        ret = self.orchestrator._Orchestrator__list_resources()
        self.assertEqual(ret, tf_state_list)

    @patch("orchestrator.Orchestrator._Orchestrator__parse_description")
    @patch("orchestrator.Orchestrator._Orchestrator__create_inventory")
    @patch("orchestrator.Orchestrator._Orchestrator__changed_infrastructure")
    @patch("orchestrator.Orchestrator.terraform.init")
    @patch("orchestrator.Orchestrator.terraform.apply")
    @patch("orchestrator.print")
    def test_orchestrate_infrastructure(self, mock_print, mock_apply, mock_init, mock_change_infra, mock_create_inv, mock_parse):
        mock_init.return_value = (0, None, None)
        mock_apply.return_value = (0, "terraform out", None)
        mock_change_infra.return_value = True
        self.orchestrator.verbose = True

        ret = self.orchestrator.orchestrate_infrastructure()

        self.assertTrue(ret)
        mock_parse.assert_called_once()
        mock_init.assert_called_once()
        mock_apply.assert_called_once()
        mock_create_inv.assert_called_once()
        mock_print.assert_called_with("terraform out")

    @patch("orchestrator.Orchestrator._Orchestrator__parse_description")
    @patch("orchestrator.Orchestrator._Orchestrator__create_inventory")
    @patch("orchestrator.Orchestrator._Orchestrator__changed_infrastructure")
    @patch("orchestrator.Orchestrator.terraform.init")
    @patch("orchestrator.Orchestrator.terraform.apply")
    @patch("orchestrator.print")
    def test_orchestrate_infrastructure_init_failed(self, mock_print, mock_apply, mock_init, mock_change_infra, mock_create_inv, mock_parse):
        mock_init.return_value = (1, None, "terraform error")
        mock_apply.return_value = (0, "terraform out", None)
        mock_change_infra.return_value = True

        with self.assertRaises(TerraformError) as err:
            self.orchestrator.orchestrate_infrastructure()
            self.assertEquals(err.exception, "terraform error")
            mock_init.assert_called_once()
            mock_apply.assert_not_called()

    @patch("orchestrator.Orchestrator._Orchestrator__parse_description")
    @patch("orchestrator.Orchestrator._Orchestrator__create_inventory")
    @patch("orchestrator.Orchestrator._Orchestrator__changed_infrastructure")
    @patch("orchestrator.Orchestrator.terraform.init")
    @patch("orchestrator.Orchestrator.terraform.apply")
    @patch("orchestrator.print")
    def test_orchestrate_infrastructure_apply_failed(self, mock_print, mock_apply, mock_init, mock_change_infra, mock_create_inv, mock_parse):
        mock_init.return_value = (0, None, None)
        mock_apply.return_value = (1, "terraform out", "terraform error")
        mock_change_infra.return_value = True

        with self.assertRaises(TerraformError) as err:
            self.orchestrator.orchestrate_infrastructure()
            self.assertEquals(err.exception, "terraform error")
            mock_init.assert_called_once()
            mock_apply.assert_called_once()

    @patch("orchestrator.Orchestrator.terraform.destroy")
    @patch("orchestrator.print")
    @patch("shutil.rmtree", MagicMock())
    def test_destroy_infrastructure(self, mock_print, mock_destroy):
        mock_destroy.return_value = (0, "terraform out", None)
        self.orchestrator.verbose = True

        self.orchestrator.destroy_infrastructure()

        mock_print.assert_called_with("terraform out")

    @patch("orchestrator.Orchestrator.terraform.destroy")
    @patch("shutil.rmtree", MagicMock())
    def test_destroy_infrastructure_failed(self, mock_destroy):
        mock_destroy.return_value = (1, "terraform out", "terraform error")

        with self.assertRaises(TerraformError) as err:
            self.orchestrator.destroy_infrastructure()
            self.assertEquals(err.exception, "terraform error")

    @patch("orchestrator.Orchestrator.orchestrate_infrastructure", MagicMock)
    @patch("orchestrator.Orchestrator.terraform.taint")
    @patch("orchestrator.Orchestrator._Orchestrator__list_resources")
    def test_rebuild_instance(self, mock_list_resources, mock_taint):
        mock_list_resources.return_value = ["module.testinstance.dummytext", "module.testinstance2.dummytext"]

        self.orchestrator.rebuild_instance("testinstance")

        mock_taint.assert_called_once_with("module.testinstance.dummytext")


