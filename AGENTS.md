# Working in DataM8 Model

This repository owns v2 JSON schemas in `schema/`, not generator or UI behavior.

- Read [the reference](docs/reference.md) and affected schemas/tests.
- Preserve schema IDs and relative references. Coordinate breaking shapes with
  backend/frontend consumers before changing them.
- Change schema source first; consumers regenerate their own Python/TypeScript types.
- Documentation-only changes do not regenerate types or update submodule pins.
- Run `node scripts/check-docs.mjs` for prose; schema changes also run
  `python validate-schema.py` and `python -m unittest discover -s tests`.
- User workflows belong in the central handbook; field constraints remain here.
- Preserve unrelated work. The maintainer merges feature branches manually.
