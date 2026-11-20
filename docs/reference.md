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

`ModelEntity.quality` is optional. When present it requires a `checks` list (which
may be empty). The closed contract has `maxFailureRatePct` and `references` as
optional entity-wide fields. There are no free definition, settings or arguments
objects and no check-type catalogue.

Each check requires a stable `id`, `execution` (`enforcement` or `monitoring`) and
a nonblank SQL `expression`. Optional fields are `severity` (`error` by default,
or `warning`), `description`, `sql` and `onEmpty`. Expressions are passed unchanged
to the target engine. NULL behavior follows that engine; express a desired failure
on NULL explicitly, for example `COALESCE(Amount >= 0, FALSE)`.

`sql` is monitoring-only. It must return exactly one row and exactly two columns:
nonnegative BIGINT-compatible `checked_rows` and numeric-or-NULL `measured_value`.
`onEmpty` is allowed only with `sql`: `evaluate` is the default; `no_data` produces
NO_DATA for `checked_rows = 0` after result validation. Empty row checks report
NO_DATA. The query relations are `{target}` and declared `{references.alias}`.
A reference has exactly `entityId`, pointing to an active model entity.

The gate percentage is an optional finite number from 0 to 100 directly under
`quality`. It counts distinct erroneous rows and fails strictly above the limit,
after valid rows and audit metrics are written. Omission disables the gate.

Solutions own native rule configuration, table bindings and execution. DQX is not
part of this schema. SQL syntax and expression errors can surface at execution;
engines may not expose every invalid rule on empty input. All configurations and
examples use this contract directly; old
shapes are rejected without conversion or implicit compatibility.
