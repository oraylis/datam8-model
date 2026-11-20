import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator


class QualitySchemaTests(unittest.TestCase):
    def setUp(self):
        self.validator = Draft7Validator(json.loads((Path(__file__).parents[1] / 'schema/quality.json').read_text()))
        self.check = {'id': 'required', 'execution': 'enforcement', 'expression': 'Id IS NOT NULL'}

    def test_fixed_contract_and_defaults_allow_row_and_aggregate_checks(self):
        self.validator.validate({'checks': [self.check], 'maxFailureRatePct': 0})
        self.validator.validate({'checks': [], 'references': {'allowed': {'entityId': 12}}})
        self.validator.validate({'checks': [{**self.check, 'execution': 'monitoring', 'severity': 'warning',
                                           'sql': 'SELECT COUNT(*) AS checked_rows, COUNT(Id) AS measured_value FROM {target}',
                                           'onEmpty': 'no_data'}]})

    def test_unknown_and_old_fields_are_rejected(self):
        for field in ['definition', 'type', 'arguments', 'function', 'parameters']:
            self.assertTrue(list(self.validator.iter_errors({'checks': [{**self.check, field: {}}]})), field)
        for field in ['settings', 'referenceDatasets', 'unknown']:
            self.assertTrue(list(self.validator.iter_errors({'checks': [], field: {}})), field)

    def test_invalid_check_fields_are_rejected(self):
        for patch in [{'id': 'has space'}, {'execution': 'unknown'}, {'expression': ''}, {'expression': '  \n'},
                      {'expression': 1}, {'severity': 'warn'}, {'severity': None}, {'description': 1},
                      {'sql': ''}, {'sql': 'SELECT 1'}, {'onEmpty': 'evaluate'}, {'onEmpty': 'skip'}]:
            self.assertTrue(list(self.validator.iter_errors({'checks': [{**self.check, **patch}]})), patch)
        for name in ['id', 'execution', 'expression']:
            value = copy.deepcopy(self.check); value.pop(name)
            self.assertTrue(list(self.validator.iter_errors({'checks': [value]})), name)

    def test_query_options_require_monitoring_sql(self):
        for on_empty in ['evaluate', 'no_data']:
            value = {**self.check, 'execution': 'monitoring', 'sql': 'SELECT 1', 'onEmpty': on_empty}
            self.validator.validate({'checks': [value]})
            value.pop('sql')
            self.assertTrue(list(self.validator.iter_errors({'checks': [value]})))

    def test_gate_and_reference_contracts_are_closed(self):
        for value in [-1, 101, True, '5', None]:
            self.assertTrue(list(self.validator.iter_errors({'checks': [], 'maxFailureRatePct': value})), value)
        for binding in [{}, {'entityId': -1}, {'entityId': True}, {'entityId': '12'}, {'entityId': 1, 'table': 'x'}]:
            self.assertTrue(list(self.validator.iter_errors({'checks': [], 'references': {'ref': binding}})), binding)
        self.assertTrue(list(self.validator.iter_errors({'checks': [], 'references': {'bad alias': {'entityId': 1}}})))
