import json

def load_contract(path):
    with open(path, "r") as f:
        return json.load(f)

def validate_payload(payload, contract):
    errors = []

    fields = contract["fields"]

    for field_name, rules in fields.items():
        if rules.get("required") and field_name not in payload:
            errors.append(f"Missing required field: {field_name}")

        if field_name in payload:
            value = payload[field_name]
            expected_type = rules.get("type")

            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Field {field_name} must be string")

            if expected_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field {field_name} must be number")

            if expected_type == "number" and "minimum" in rules:
                if value < rules["minimum"]:
                    errors.append(f"Field {field_name} must be >= {rules['minimum']}")

    return errors