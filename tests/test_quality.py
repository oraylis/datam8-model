import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator


class QualitySchemaTests(unittest.TestCase):
    def setUp(self):
        schema = json.loads((Path(__file__).parents[1] / "schema/quality.json").read_text())
        self.validator = Draft7Validator(schema)
        self.check = {"id": "id_required", "type": "not_null", "attribute": "Id", "execution": "enforcement", "severity": "error"}

    def test_six_types_and_optional_settings(self):
        for kind, params, attribute in [
            ("not_null", None, "Id"), ("range", {"min": 0}, "Amount"),
            ("sql_expression", {"expression": "Id > 0"}, None),
            ("completeness", {"minCompleteness": 0.95}, "Email"),
            ("freshness", {"maxAgeSeconds": 60}, "Updated"),
            ("row_count", {"maxCount": 100}, None),
        ]:
            check = dict(self.check, type=kind, execution="monitoring")
            if attribute: check["attribute"] = attribute
            else: check.pop("attribute")
            if params is not None: check["parameters"] = params
            self.assertFalse(list(self.validator.iter_errors({"checks": [check]})), kind)
        self.validator.validate({"checks": [], "settings": {"maxFailureRatePct": 0}})

    def test_invalid_combinations_and_bounds(self):
        for patch in [
            {"id": "has space"}, {"severity": "warn"},
            {"type": "completeness", "parameters": {"minCompleteness": 1.1}},
            {"type": "freshness", "parameters": {"maxAgeSeconds": 60}},
            {"type": "range", "parameters": {}},
        ]:
            check = copy.deepcopy(self.check); check.update(patch)
            self.assertTrue(list(self.validator.iter_errors({"checks": [check]})), patch)

    def test_native_dqx_is_open_and_reference_bindings_are_modelled(self):
        for function, arguments in [("is_in_list", {"column": "Id", "allowed": [1, 2]}),
                                    ("future_dqx_function", {"arbitrary": {"nested": [True, None]}})]:
            check = {"id": "native", "type": "dqx", "execution": "monitoring",
                     "definition": {"check": {"function": function, "arguments": arguments},
                                    "filter": None, "name": None, "message_expr": None, "user_metadata": None}}
            self.validator.validate({"checks": [check], "settings": {"dependencies": ["package==1.0"]},
                                     "referenceDatasets": {"other": {"entityId": 12, "execution": "monitoring"},
                                                           "external": {"table": "catalog.schema.table"}}})

    def test_native_dqx_rejects_malformed_common_fields(self):
        definition = {"check": {"function": "is_unique", "arguments": {"columns": ["Id"]}}}
        for patch in [{"check": {"function": ""}}, {"check": {"function": "is_unique", "arguments": []}},
                      {"criticality": "warning"}, {"filter": 42}, {"user_metadata": []}]:
            check = {"id": "native", "type": "dqx", "execution": "enforcement",
                     "definition": dict(definition, **patch)}
            self.assertTrue(list(self.validator.iter_errors({"checks": [check]})), patch)
