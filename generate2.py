import json
from collections import deque

def extract_fields(schema, type_name):
    for type_def in schema["data"]["__schema"]["types"]:
        if type_def["name"] == type_name:
            return type_def.get("fields", [])
    return []

def parse_graphql_operations(schema_json, specific_operation=None):
    schema = json.loads(schema_json)
    
    def bfs_operations(start_field, parent_path):
        queue = deque([(start_field, parent_path)])
        visited_paths = set()

        while queue:
            field, current_path = queue.popleft()
            new_path = f"{current_path}.{field['name']}"
            
            if field['name'] in visited_paths:
                print(f"Potential loop detected: {new_path}")
                continue
            visited_paths.add(field['name'])
            
            if specific_operation and not new_path.startswith(specific_operation):
                continue
            
            if current_path.startswith("Query"):
                print(new_path)
            elif current_path.startswith("Mutation"):
                print(new_path)
            
            field_type = field["type"]
            while field_type.get("ofType"):
                field_type = field_type["ofType"]

            if field_type["kind"] in ["OBJECT", "INTERFACE"]:
                new_fields = extract_fields(schema, field_type["name"])
                for new_field in new_fields:
                    queue.append((new_field, new_path))

    for type_def in schema["data"]["__schema"]["types"]:
        if type_def["kind"] == "OBJECT" and type_def["name"] in ["Query", "Mutation"]:
            for field in type_def.get("fields", []):
                bfs_operations(field, type_def["name"])

# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python script.py <schema.json> [-o specific_operation]")
        sys.exit(1)

    specific_operation = None
    if "-o" in sys.argv:
        specific_operation = sys.argv[sys.argv.index("-o") + 1]

    with open(sys.argv[1], 'r') as file:
        schema_json = file.read()

    parse_graphql_operations(schema_json, specific_operation)
