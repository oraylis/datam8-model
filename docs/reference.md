# Schema Reference and Compatibility

## Schema map

| Definition | Source |
| --- | --- |
| Solution paths and generator targets | [solution](../schema/solution.json) |
| Base collections | [base](../schema/base.json) |
| Entity, sources, mappings, relationships and transformations | [model](../schema/model.json) |
| Attributes and history metadata | [attribute](../schema/attribute.json) |
| Folder metadata | [folder](../schema/folder.json) |
| Data types and mappings | [data type](../schema/data-type.json) |
| Data-source types and concrete sources | [data source](../schema/data-source.json) |
| Products and modules | [data product](../schema/data-product.json) |
| Properties, values and assignments | [property](../schema/property.json) |
| Zones | [zone](../schema/zone.json) |
| Plugin manifests, UI and capabilities | [plugin](../schema/plugin.json) |
| Shared IDs/definitions | [common](../schema/common.json) |
| Diagrams | [diagram](../schema/diagram.json) |

Read the source's `required`, `additionalProperties` and `$ref` constraints; a
field accepted by another branch is not necessarily accepted here. The plugin
schema currently requires `type` without declaring it among permitted properties;
this inconsistency needs its own schema/consumer regression fix, not a prose workaround.

## Minimal solution descriptor

```json
{
  "schemaVersion": "2.0.0",
  "basePath": "Base",
  "modelPath": "Model",
  "pluginsPath": "Plugins",
  "generatorTargets": [
    {"name": "docs", "sourcePath": "Generate/docs", "outputPath": "Output/docs"}
  ]
}
```

This is a structural descriptor example. It is not a runnable solution without
the referenced Base, Model, Plugins and target files. See the
[sample](https://github.com/oraylis/datam8-sample-solution/blob/codex/documentation-v2/docs/getting-started.md) for a complete concrete example.

## Consumer generation

The backend pins this repository as `datam8-model/`. Its
[build hook](https://github.com/oraylis/datam8-cli/blob/feature/external_refresh/hatch_build_datamodel.py) generates Pydantic code into
`src/datam8_model` during builds. Follow the backend's `uv build` procedure and
inspect generated diffs. Do not patch generated Python as a substitute for schemas.

Frontend uses `submodules/datam8-generator/datam8-model/schema` and
`npm run generate:schema-types` to generate web schema types. Its hand-written
`packages/types` is a separate shared package. Follow
[frontend generation](https://github.com/oraylis/datam8-frontend/blob/feature/external_refresh/scripts/generate-schema-types.mjs).

## Compatibility policy

Pin the exact commit/tag and record it with backend, frontend and sample revisions.
Adding a required field, narrowing a type or rejecting a previously allowed shape
requires coordinated consumers, fixtures and release notes. An optional field still
needs validation against readers using `additionalProperties: false`.

Structural validity is not complete model validity: reference resolution,
property interpretation and runtime semantics belong to the backend/selected target.
Use [central compatibility](https://github.com/oraylis/datam8/blob/codex/documentation-v2/docs/compatibility.md) and actual consumer tests.
Documentation changes here leave schema JSON and consumer pins unchanged.
