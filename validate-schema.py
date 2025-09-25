import json
from pathlib import Path

import jsonschema as jss

for file in Path("./schema").glob("**/*.json"):
    with open(file) as schema_file:
        schema = json.load(schema_file)

    try:
        jss.Draft7Validator.check_schema(schema)
        print("Schema is valid.")

    except jss.SchemaError as e:
        print("Schema error: %s" % e)
