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

`ModelEntity.quality` is optional. Every check uses the same structure: stable
entity-local `id`, `execution` (`enforcement` or `monitoring`), an open object
`definition`, and optional `description`. There is no check type catalogue and
no prescribed tool-specific definition format. A target may interpret a native
DQX rule, a different tool's rule, or its own declarative configuration.

`settings.maxFailureRatePct` is an optional percentage from 0 to 100. Additional
settings are open target options. `referenceDatasets` maps aliases to open binding
objects; optional `entityId` and `execution` provide shared reference metadata.
Targets own other binding details, dependency formats and execution semantics.
The core validates unique IDs, finite JSON values and active entity references.
Function names, arguments, SQL and engine-specific metadata are target concerns.

The previous six specialized check shapes and `type: "dqx"` are no longer accepted.
Convert existing metadata explicitly before loading it with this schema. Keep
check IDs and audit history; the new configuration produces a new rule-set hash.
