# Schema Reference and Compatibility

## Schema map

| Definition | Source |
| --- | --- |
| Solution paths and generator targets | [solution](../schema/solution.json) |
| Base collections | [base](../schema/base.json) |
| Entity, sources, mappings, relationships and transformations | [model](../schema/model.json) |
| Entity quality requirements | [quality](../schema/quality.json) |
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
field accepted by another branch is not necessarily accepted here.

## Source metadata location

`ExternalModelSource.metadataLocation` is an optional string identifying a source's
metadata location separately from its `sourceLocation`. Omitting it preserves the
existing source shape. The schema does not require a nonempty string or define
runtime lookup or fallback behavior; those semantics belong to the consumer.

## Plugin manifest contract

A manifest requires `id`, `version`, `entryPoint` and `capabilities`; `displayName`
is optional. There is no top-level `type` field, and undeclared properties remain
invalid. This matches the backend and frontend manifest types and the sample's
plugin manifests. UI field definitions still require their own `type`.

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
[sample](https://github.com/oraylis/datam8-sample-solution/tree/main) for a complete
concrete example; check its pinned consumer versions before running it.

## Consumer generation

The backend pins this repository as `datam8-model/`. Its
[build hook](https://github.com/oraylis/datam8-cli/blob/main/hatch_build_datamodel.py) generates Pydantic code into
`src/datam8_model` during builds. Follow the backend's `uv build` procedure and
inspect generated diffs. Do not patch generated Python as a substitute for schemas.

Frontend uses `submodules/datam8-generator/datam8-model/schema` and
`npm run generate:schema-types` to generate web schema types. Its hand-written
`packages/types` is a separate shared package. The implementation is
`scripts/generate-schema-types.mjs` in the
[frontend repository](https://github.com/oraylis/datam8-frontend/tree/main).

## Compatibility policy

Pin the exact commit/tag and record it with backend, frontend and sample revisions.
Adding a required field, narrowing a type or rejecting a previously allowed shape
requires coordinated consumers, fixtures and release notes. An optional field still
needs validation against readers using `additionalProperties: false`.

Structural validity is not complete model validity: reference resolution,
property interpretation and runtime semantics belong to the backend/selected target.
Verify compatibility with actual consumer tests.

## Quality requirements

`ModelEntity.quality` is optional. Checks have entity-local stable IDs, a
platform-neutral type, execution mode and severity. Not Null, numeric Range and
SQL Expression support enforcement and monitoring; Completeness, Freshness and
Row Count support monitoring only. Settings optionally define a failure percentage
from 0 to 100. Enforcement retains error rows in quarantine; warning-only rows
remain valid. Omitting quality preserves existing entities.

Range bounds are inclusive and NULL is allowed (use a separate Not Null rule).
Completeness measures non-NULL values, not nonempty strings. Freshness compares
the latest timestamp against the evaluation time in seconds and rejects future
timestamps. The backend owns cross-field bounds, ID uniqueness, attribute
resolution and execution semantics.

For native declarative DQX checks use `type: "dqx"`, a stable `id`, `execution`
and `definition`. The definition retains the native envelope: `check.function`,
optional `check.arguments`, `check.for_each_column`, `criticality`, `filter`,
`message_expr` and `user_metadata`. Functions and argument keys are open-ended;
the deployed DQX version validates them. Omitted criticality means `error`.
The generated `user_metadata.datam8_check_id` is reserved for audit attribution.
The six simpler check types remain valid for existing models.

`referenceDatasets` maps aliases to either an active model `entityId` or a `table`
name. Bindings optionally specify `execution` (otherwise both modes); only the
executing mode loads those DataFrames. Additional native-check dependencies are
declared as PyPI requirements in `settings.dependencies`. These declarations are
model data; no Python implementation per rule is required.
