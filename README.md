# DataM8 Model

This repository owns the JSON Schema definitions for DataM8 v2 solutions, Base,
model entities, attributes, sources, relationships, folder metadata and plugins.
Schemas use JSON Schema draft-07 and reside in [schema](schema).
These schemas target the regular release `v2.0.0`; publication
follows maintainer review, manual merge and checks on the merged commit.

- [Schema map, minimal example and consumer generation](docs/reference.md)
- [Central concepts](https://github.com/oraylis/datam8/blob/codex/documentation-v2/docs/concepts.md)
- [Compatibility and evidence](https://github.com/oraylis/datam8/blob/codex/documentation-v2/docs/compatibility.md)
- [Documentation handoff](docs/documentation-handoff.md)

Pin a tag or commit in each consumer; `schemaVersion` alone does not identify the
exact schema revision. Change schemas here before regenerating Python/TypeScript
types. Backend runtime validation may add semantic checks beyond structural schemas.

## Checks

```sh
python validate-schema.py
python -m unittest discover -s tests
node --test scripts/check-docs.test.mjs
node scripts/check-docs.mjs
```

Install `jsonschema` for schema checks and use Node 24 for documentation checks.
Issues are tracked in [DataM8](https://github.com/oraylis/datam8/issues).
For sensitive reports, see [SECURITY.md](SECURITY.md).
