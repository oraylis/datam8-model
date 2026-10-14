import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator, RefResolver

SCHEMA_DIR = Path(__file__).parents[1] / "schema"
MANIFEST_DIR = Path(__file__).parent / "fixtures" / "plugin-manifests"
# Fixtures snapshot sample Plugins/Test/test.json at 1e1855e59e2734b3a393f9128193504626ab9380
# and the CLI SQL Server built-in manifest at 7e8a743577097a23e156e281bcd3dbf514a0bd66
# (its configured package version is 2.0.0). Neither fixture needs a consumer checkout.


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


class ExternalSourceSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = definition_validator(
            load_schema("model.json"), "ExternalModelSource"
        )
        self.source = {"dataSource": "crm", "sourceLocation": "sales.customers"}

    def test_metadata_location_is_optional(self) -> None:
        self.validator.validate(self.source)

    def test_metadata_location_accepts_strings(self) -> None:
        for location in ("contracts/customers#id", ""):
            with self.subTest(location=location):
                self.validator.validate({**self.source, "metadataLocation": location})

    def test_metadata_location_rejects_non_strings(self) -> None:
        for location in (None, 12, 1.5, True, [], {}):
            with self.subTest(location=location):
                self.assertFalse(
                    self.validator.is_valid({**self.source, "metadataLocation": location})
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
    def setUp(self) -> None:
        schema = load_schema("plugin.json")
        self.manifest_validator = Draft7Validator(
            schema, resolver=RefResolver.from_schema(schema)
        )
        self.manifests = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in MANIFEST_DIR.glob("*.json")
        }

    def test_real_manifests_without_type_are_valid(self) -> None:
        self.assertEqual({"sample-test.json", "builtin-sqlserver.json"}, set(self.manifests))
        for name, manifest in self.manifests.items():
            with self.subTest(manifest=name):
                self.assertNotIn("type", manifest)
                self.manifest_validator.validate(manifest)

    def test_manifest_rejects_missing_required_fields(self) -> None:
        manifest = self.manifests["sample-test.json"]
        for field in ("id", "version", "entryPoint", "capabilities"):
            with self.subTest(field=field):
                incomplete = {key: value for key, value in manifest.items() if key != field}
                self.assertFalse(self.manifest_validator.is_valid(incomplete))

    def test_manifest_rejects_undeclared_properties(self) -> None:
        for field in ("type", "unexpected"):
            with self.subTest(field=field):
                self.assertFalse(
                    self.manifest_validator.is_valid(
                        {**self.manifests["sample-test.json"], field: "connector"}
                    )
                )

    def test_manifest_rejects_unknown_capability(self) -> None:
        self.assertFalse(
            self.manifest_validator.is_valid(
                {**self.manifests["sample-test.json"], "capabilities": ["unknown"]}
            )
        )

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
