# Model Release and Documentation Handoff

The `feature/v2-beta-port` candidate combines model documentation with the regular
`v2.0.0` schema release. Relative to `v2.0.0-beta.3`, it adds the optional external
source `metadataLocation`, clarifies the optional `pluginId` description and removes
the contradictory top-level manifest `type` requirement. The description change
does not implement new built-in plugin behavior.

PR #18 already shipped external relationships, source overrides, field
descriptions, `previewData`, UI string enums and schema contract tests in beta.3.
Those remain available; `pluginsPath` remains required with default `Plugins`.
Consumer pins, generated types and target implementations are not changed here.

Run `python validate-schema.py`, `python -m unittest discover -s tests`,
`node --test scripts/check-docs.test.mjs` and `node scripts/check-docs.mjs`.
Use Node 24 and install `jsonschema` for the Python checks. CI runs these checks
without a frontend or sample checkout. Test fixtures are self-contained snapshots
of real plugin manifests; consumer generation is checked in disposable checkouts.

Read the [central handoff](https://github.com/oraylis/datam8/blob/codex/documentation-v2/docs/handoff.md) for branch/workspace mapping,
results and manual merge order. Development links point to published documentation
branches. After their destinations merge, update development links to main;
keep tutorial evidence bound to commits. Public user workflows belong in the handbook.

## Release sequence

1. Review the PR and pass schema, documentation and consumer-generation checks.
2. The maintainer manually squash-merges the approved PR after GitHub's required
   reviews and checks pass. No auto-merge or branch-rule bypass is used.
3. Verify successful main checks for the resulting merge commit.
4. Create the annotated `v2.0.0` tag on that exact commit, without replacing any
   existing tag, and publish `DataM8 Model 2.0.0` as a regular latest GitHub release.

Release notes include the changes since beta.3, the accumulated v2 beta features,
compatibility guidance and PR/changelog links. Beta releases remain published.
The release is limited to this schema repository; CLI, frontend and sample
releases remain separate. Existing consumer evidence does not automatically
certify a new packaged desktop or complete runtime combination.
