import json

def load_schema_context(path="configs/schema_context.json"):
    with open(path, "r") as f:
        return json.load(f)

def format_schema_context(schema_data):
    parts = []
    for table, table_info in schema_data["tables"].items():
        parts.append(f"Table `{table}`: {table_info['description']}")
        for column, desc in table_info["columns"].items():
            parts.append(f"  - `{column}`: {desc}")
    return "\n".join(parts)
