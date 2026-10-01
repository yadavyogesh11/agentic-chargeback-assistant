import json
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError


BASE_DIR = Path(__file__).resolve().parent.parent

SCHEMA_FILE = BASE_DIR / "src" / "case_schema.json"
CASE_FILE = BASE_DIR / "data" / "cases" / "CASE-001.json"


def main():

    print("=== FULL CASE SCHEMA VALIDATION ===")
    print()

    # Check files
    if not SCHEMA_FILE.exists():
        print("ERROR: case_schema.json not found")
        return

    if not CASE_FILE.exists():
        print("ERROR: CASE-001.json not found")
        return

    print(f"Schema: {SCHEMA_FILE}")
    print(f"Case:   {CASE_FILE}")
    print()

    # Load schema
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)

        print("Schema JSON loaded successfully.")

    except Exception as e:
        print(f"ERROR loading schema: {e}")
        return

    # Load case
    try:
        with open(CASE_FILE, "r", encoding="utf-8") as f:
            case = json.load(f)

        print("Case JSON loaded successfully.")

    except Exception as e:
        print(f"ERROR loading case: {e}")
        return

    print()
    print("Case ID:", case.get("case_id"))
    print("Reason Code:", case.get("reason_code"))
    print()

    # Full JSON Schema validation
    try:
        validate(instance=case, schema=schema)

        print("===================================")
        print("VALIDATION PASSED")
        print("CASE-001 matches the case schema.")
        print("===================================")

    except ValidationError as e:

        print("===================================")
        print("VALIDATION FAILED")
        print("===================================")

        print()
        print("Error:")
        print(e.message)

        if e.absolute_path:
            field_path = " -> ".join(str(x) for x in e.absolute_path)
            print()
            print("Field causing the problem:")
            print(field_path)

        print()
        print("Fix the case data or schema before continuing.")


if __name__ == "__main__":
    main()