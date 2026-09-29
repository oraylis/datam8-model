import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator, RefResolver

SCHEMA_DIR = Path(__file__).parents[1] / "schema"


def load_schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def definition_validator(schema: dict, definition: str) -> Draft7Validator:
    store = {}
    for schema_path in SCHEMA_DIR.glob("*.json"):
        candidate = load_schema(schema_path.name)
        if schema_id := candidate.get("$id"):
            store[schema_id] = candidate

    resolver = RefResolver(
        base_uri=schema["$id"],
        referrer=schema,
        store=store,
    )
    return Draft7Validator(schema["definitions"][definition], resolver=resolver)


class DataSourceSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load_schema("data-source.json")

    def test_source_object_accepts_override(self) -> None:
        validator = definition_validator(self.schema, "SourceObject")
        validator.validate(
            {
                "name": "orders",
                "type": "table",
                "description": "Imported orders",
                "sourceOverride": {
                    "dataSource": "archive",
                    "sourceLocation": "sales.orders_2025",
                },
            }
        )

    def test_source_field_accepts_description_and_scale_zero(self) -> None:
        validator = definition_validator(self.schema, "SourceField")
        validator.validate(
            {
                "name": "quantity",
                "ordinal": 1,
                "dataType": "decimal",
                "numbericScale": 0,
                "isNullable": False,
                "description": "Ordered item count",
            }
        )


class RelationshipSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = definition_validator(
            load_schema("model.json"),
            "ModelRelationship",
        )
        self.attributes = [{"sourceName": "customer_id", "targetName": "id"}]

    def test_internal_relationship_uses_integer_target(self) -> None:
        self.validator.validate(
            {"targetLocation": 12, "attributes": self.attributes}
        )

    def test_external_relationship_uses_data_source_and_string_target(self) -> None:
        self.validator.validate(
            {
                "dataSource": "crm",
                "targetLocation": "sales.customers",
                "attributes": self.attributes,
            }
        )

    def test_internal_relationship_rejects_string_target(self) -> None:
        self.assertFalse(
            self.validator.is_valid(
                {
                    "targetLocation": "sales.customers",
                    "attributes": self.attributes,
                }
            )
        )

    def test_external_relationship_rejects_integer_target(self) -> None:
        self.assertFalse(
            self.validator.is_valid(
                {
                    "dataSource": "crm",
                    "targetLocation": 12,
                    "attributes": self.attributes,
                }
            )
        )

    def test_external_relationship_rejects_empty_values(self) -> None:
        self.assertFalse(
            self.validator.is_valid(
                {
                    "dataSource": "",
                    "targetLocation": "",
                    "attributes": self.attributes,
                }
            )
        )


class PluginAndSolutionSchemaTests(unittest.TestCase):
    def test_plugin_schema_exposes_preview_and_string_enums(self) -> None:
        schema = load_schema("plugin.json")
        self.assertIn("previewData", schema["definitions"]["Capability"]["enum"])

        ui_field = schema["definitions"]["UiSchema"]["properties"]["authModes"][
            "items"
        ]["properties"]["fields"]["items"]["properties"]
        self.assertEqual({"type": "string"}, ui_field["enum"]["items"])

    def test_plugins_path_is_required_with_documented_default(self) -> None:
        schema = load_schema("solution.json")
        self.assertIn("pluginsPath", schema["required"])
        self.assertEqual("Plugins", schema["properties"]["pluginsPath"]["default"])


if __name__ == "__main__":
    unittest.main()
