import jsonschema as jss
import json

with open("./schema/functions/Source.json") as schema_file:
    schema = json.load(schema_file)


try:
    jss.Draft7Validator.check_schema(schema)
    print("Schema is valid.")

except jss.SchemaError as e:
    print("Schema error: %s" % e)
