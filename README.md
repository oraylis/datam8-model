# DataM8 Model

This repository owns the JSON Schema definitions for DataM8 v2 solutions, Base,
model entities, attributes, sources, relationships, folder metadata and plugins.
Schemas use JSON Schema draft-07 and reside in [schema](schema).
This repository defines the `2.0.0` schema contract.

## Start with your task

| I want to… | Begin here | First result |
| --- | --- | --- |
| Use DataM8 to model or generate | [App/CLI installation](https://github.com/oraylis/datam8/blob/main/docs/installation.md) | Work with a solution using the product; no schema checkout is needed |
| Author or understand metadata JSON | [Schema map and minimal descriptor](docs/reference.md#schema-map) | Find the canonical definition and required fields for the entity you are editing |
| Generate consumer types | [Consumer generation](docs/reference.md#consumer-generation) | Use the schema revision pinned by the backend or frontend |
| Change the schema contract | [Compatibility policy](docs/reference.md#compatibility-policy), then [checks](#checks) | Review consumer impact and validate a change before regenerating types |

For a concrete model with Base definitions and templates, explore the
[public sample](https://github.com/oraylis/datam8-sample-solution). The descriptor
in the reference is a structural example, not a standalone runnable solution.

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

Pull requests against `main` and pushes to `main` run the same CI. Feature pushes
do not start duplicate jobs. Root Markdown and Markdown/images under `docs/` need
only documentation checks; signing files, scripts, schemas and all other changes
also run schema validation and unit tests. Manual CI always runs every check.
The required `CI result` rejects failures, cancellations and unexpected skips.
Newer PR/Main runs supersede stale runs. CodeQL retains its existing default setup.
This repository does not build or publish application packages.

Issues are tracked in [DataM8](https://github.com/oraylis/datam8/issues).
For sensitive reports, see [SECURITY.md](SECURITY.md).
