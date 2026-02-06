"""
JSON Analyzer - Analyze large JSON files and extract structure/summary.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set
from collections import defaultdict


def analyze_json_structure(data: Any, path: str = "root", depth: int = 0, max_depth: int = 5) -> Dict:
    """Recursively analyze JSON structure."""
    
    if depth > max_depth:
        return {"type": "...", "note": "max depth reached"}
    
    result = {
        "path": path,
        "type": type(data).__name__,
    }
    
    if isinstance(data, dict):
        result["keys"] = len(data.keys())
        result["sample_keys"] = list(data.keys())[:5]  # First 5 keys
        
        # Analyze children
        children = {}
        for key in list(data.keys())[:3]:  # Analyze first 3 keys
            children[key] = analyze_json_structure(data[key], f"{path}.{key}", depth + 1, max_depth)
        result["children"] = children
        
    elif isinstance(data, list):
        result["length"] = len(data)
        if len(data) > 0:
            result["first_item"] = analyze_json_structure(data[0], f"{path}[0]", depth + 1, max_depth)
            if len(data) > 1:
                result["item_types"] = list(set(type(item).__name__ for item in data[:10]))
    
    elif isinstance(data, str):
        result["sample"] = data[:100] if len(data) > 100 else data
        result["length"] = len(data)
    
    elif isinstance(data, (int, float, bool, type(None))):
        result["value"] = data
    
    return result


def print_structure(structure: Dict, indent: int = 0):
    """Pretty print structure analysis."""
    prefix = "  " * indent
    
    print(f"{prefix}📍 Path: {structure.get('path', 'unknown')}")
    print(f"{prefix}📦 Type: {structure.get('type', 'unknown')}")
    
    if "keys" in structure:
        print(f"{prefix}🔑 Keys: {structure['keys']}")
        print(f"{prefix}   Sample keys: {structure['sample_keys']}")
    
    if "length" in structure:
        print(f"{prefix}📊 Length: {structure['length']}")
    
    if "sample" in structure:
        print(f"{prefix}💬 Sample: '{structure['sample']}'")
    
    if "value" in structure:
        print(f"{prefix}💎 Value: {structure['value']}")
    
    if "item_types" in structure:
        print(f"{prefix}🔖 Item types: {structure['item_types']}")
    
    if "children" in structure:
        print(f"{prefix}👶 Children:")
        for key, child in structure["children"].items():
            print(f"{prefix}  ▶️ {key}:")
            print_structure(child, indent + 2)
    
    if "first_item" in structure:
        print(f"{prefix}🎯 First item:")
        print_structure(structure["first_item"], indent + 1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python json_analyzer.py <json_file>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print(f"🔍 Analyzing: {json_file}")
    print(f"📏 Size: {json_file.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON loaded successfully!")
        print()
        
        # Analyze structure
        print("=" * 80)
        print("📊 STRUCTURE ANALYSIS")
        print("=" * 80)
        structure = analyze_json_structure(data, max_depth=4)
        print_structure(structure)
        
        # Additional stats
        print()
        print("=" * 80)
        print("📈 STATISTICS")
        print("=" * 80)
        
        def count_items(obj, counts=None):
            if counts is None:
                counts = defaultdict(int)
            
            if isinstance(obj, dict):
                counts['dicts'] += 1
                counts['total_keys'] += len(obj.keys())
                for value in obj.values():
                    count_items(value, counts)
            elif isinstance(obj, list):
                counts['lists'] += 1
                counts['list_items'] += len(obj)
                for item in obj:
                    count_items(item, counts)
            elif isinstance(obj, str):
                counts['strings'] += 1
            elif isinstance(obj, (int, float)):
                counts['numbers'] += 1
            elif isinstance(obj, bool):
                counts['booleans'] += 1
            elif obj is None:
                counts['nulls'] += 1
            
            return counts
        
        stats = count_items(data)
        for key, value in sorted(stats.items()):
            print(f"  {key}: {value:,}")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
