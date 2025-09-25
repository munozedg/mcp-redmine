#!/usr/bin/env python3
"""
Simple validator to check for circular dependencies in OpenAPI schema
"""
import json
import sys
from collections import defaultdict, deque

def find_circular_dependencies(schema_file):
    """Find circular dependencies in OpenAPI schema components"""
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    components = schema.get('components', {}).get('schemas', {})
    
    # Build dependency graph
    dependencies = defaultdict(set)
    
    def extract_refs(obj, current_schema):
        """Extract $ref dependencies from an object"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == '$ref' and isinstance(value, str) and value.startswith('#/components/schemas/'):
                    ref_name = value.split('/')[-1]
                    if ref_name in components:
                        dependencies[current_schema].add(ref_name)
                else:
                    extract_refs(value, current_schema)
        elif isinstance(obj, list):
            for item in obj:
                extract_refs(item, current_schema)
    
    # Extract all dependencies
    for schema_name, schema_def in components.items():
        extract_refs(schema_def, schema_name)
    
    print(f"Found {len(components)} schemas with dependencies:")
    for schema_name, deps in dependencies.items():
        if deps:
            print(f"  {schema_name} -> {', '.join(sorted(deps))}")
    
    # Check for circular dependencies using DFS
    def has_cycle(node, visited, rec_stack, path):
        visited.add(node)
        rec_stack.add(node)
        current_path = path + [node]
        
        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack, current_path):
                    return True
            elif neighbor in rec_stack:
                cycle = current_path[current_path.index(neighbor):] + [neighbor]
                print(f"CIRCULAR DEPENDENCY FOUND: {' -> '.join(cycle)}")
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check all components for cycles
    visited = set()
    cycles_found = False
    
    for schema_name in components:
        if schema_name not in visited:
            rec_stack = set()
            if has_cycle(schema_name, visited, rec_stack, []):
                cycles_found = True
    
    if not cycles_found:
        print("✅ No circular dependencies found!")
        return True
    else:
        print("❌ Circular dependencies detected!")
        return False

if __name__ == '__main__':
    schema_file = sys.argv[1] if len(sys.argv) > 1 else 'sensai_projects_schema_improved.json'
    
    print(f"Validating circular dependencies in: {schema_file}")
    print("-" * 60)
    
    try:
        success = find_circular_dependencies(schema_file)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)