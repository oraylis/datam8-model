import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator


class QualitySchemaTests(unittest.TestCase):
    def setUp(self):
        schema = json.loads((Path(__file__).parents[1] / "schema/quality.json").read_text())
        self.validator = Draft7Validator(schema)
        self.check = {"id": "required", "execution": "enforcement", "definition": {}}

    def test_different_tool_dialects_and_options_need_no_schema_changes(self):
        for definition in [
            {"check": {"function": "is_not_null", "arguments": {"column": "Id"}}, "criticality": "error"},
            {"assertion": {"expression": "Id IS NOT NULL"}, "level": "fatal"},
            {"future": [None, {"arbitrary": True}], "check": "not a DQX check object"},
            {},
        ]:
            self.validator.validate({"checks": [dict(self.check, definition=definition)],
                                     "settings": {"maxFailureRatePct": 0, "engineOptions": {"anything": [None, 1]}},
                                     "referenceDatasets": {"file": {"uri": "memory://fixture", "format": "custom"},
                                                           "entity": {"entityId": 12, "execution": "monitoring"}}})

    def test_common_structure_rejects_invalid_values(self):
        for patch in [{"id": "has space"}, {"execution": "unknown"}, {"definition": []}, {"definition": None}]:
            self.assertTrue(list(self.validator.iter_errors({"checks": [dict(self.check, **patch)]})), patch)
        for percentage in [-1, 101]:
            self.assertTrue(list(self.validator.iter_errors({"checks": [], "settings": {"maxFailureRatePct": percentage}})))

    def test_legacy_shapes_are_not_an_implicit_runtime_fallback(self):
        for kind in ["not_null", "range", "sql_expression", "completeness", "freshness", "row_count", "dqx"]:
            self.assertTrue(list(self.validator.iter_errors({"checks": [dict(self.check, type=kind)]})), kind)

    def test_only_common_reference_metadata_is_constrained(self):
        for reference in [{"entityId": -1}, {"execution": "invalid"}, "file.csv"]:
            self.assertTrue(list(self.validator.iter_errors({"checks": [], "referenceDatasets": {"ref": reference}})))
        self.validator.validate({"checks": [], "referenceDatasets": {"ref": {"table": None, "dependencies": {"custom": 1}}}})
