
import json
import yaml
import pathlib

def main():
    root_dir = pathlib.Path(__file__).parent.parent
    input_file = root_dir / 'sensai_projects_schema.json'
    output_file = root_dir / 'mcp_redmine' / 'redmine_openapi.yml'

    print(f"Reading from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Adjustment for OpenAPI version compatibility
    if data.get('openapi') == '3.1.0':
        print("Downgrading OpenAPI version to 3.0.3")
        data['openapi'] = '3.0.3'

    # Ensure tags are present and roughly correct (they seem okay in the JSON)
    
    print(f"Writing to {output_file}", flush=True)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=4096)
        print("Conversion complete.", flush=True)
    except Exception as e:
        print(f"Error writing file: {e}", flush=True)

if __name__ == "__main__":
    main()
