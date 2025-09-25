#!/usr/bin/env python3
"""
Validate OpenAPI schema for common issues
"""
import json
import sys
from pathlib import Path

def validate_schema(schema_file):
    """Validate OpenAPI schema for common issues"""
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    issues = []
    
    # Check for missing SearchResult schema
    if 'SearchResult' not in schema.get('components', {}).get('schemas', {}):
        issues.append("Missing SearchResult schema")
    
    # Check parameters section
    params = schema.get('components', {}).get('parameters', {})
    required_params = ['offset', 'limit', 'include', 'issueId', 'timeEntryId']
    
    for param in required_params:
        if param not in params:
            issues.append(f"Missing parameter definition: {param}")
        elif 'name' not in params[param]:
            issues.append(f"Parameter {param} missing 'name' property")
    
    # Check for circular dependencies in Issue schema
    issue_schema = schema.get('components', {}).get('schemas', {}).get('Issue', {})
    issue_props = issue_schema.get('properties', {})
    
    # Check if parent references Issue schema (circular)
    parent_prop = issue_props.get('parent', {})
    if parent_prop.get('$ref') == '#/components/schemas/Issue':
        issues.append("Circular dependency: Issue.parent references Issue")
        
    # Check if children references Issue schema (circular)
    children_prop = issue_props.get('children', {})
    children_items = children_prop.get('items', {})
    if children_items.get('$ref') == '#/components/schemas/Issue':
        issues.append("Circular dependency: Issue.children references Issue")
    
    # Check paths for parameter reference issues
    paths = schema.get('paths', {})
    for path, path_obj in paths.items():
        for method, method_obj in path_obj.items():
            if isinstance(method_obj, dict) and 'parameters' in method_obj:
                for i, param in enumerate(method_obj['parameters']):
                    if isinstance(param, dict) and '$ref' in param:
                        # Parameter references should only have $ref, no other properties
                        if len(param.keys()) > 1:
                            issues.append(f"Parameter in {path} {method} has extra properties along with $ref: {param}")
    
    return issues

def main():
    schema_file = Path('sensai_projects_schema_improved.json')
    
    if not schema_file.exists():
        print(f"Schema file not found: {schema_file}")
        return 1
    
    try:
        issues = validate_schema(schema_file)
        
        if not issues:
            print("✅ Schema validation passed - no issues found!")
            return 0
        else:
            print("❌ Schema validation found issues:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            return 1
            
    except Exception as e:
        print(f"❌ Error validating schema: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())