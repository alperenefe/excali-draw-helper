"""
Extract ALL text content from Excalidraw JSON
Shows FULL text of every element (boxes, arrows, standalone texts)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def extract_all_texts(json_data):
    """Extract all text content with context."""
    elements = json_data.get("elements", [])
    
    # Organize elements
    boxes = []
    arrows = []
    texts = []
    
    # Create ID to element map
    elem_map = {e.get("id"): e for e in elements}
    
    for elem in elements:
        elem_type = elem.get("type")
        
        if elem_type == "rectangle":
            boxes.append(elem)
        elif elem_type == "arrow":
            arrows.append(elem)
        elif elem_type == "text":
            texts.append(elem)
    
    output = []
    output.append("=" * 100)
    output.append("📦 ALL BOX CONTENTS (191 total)")
    output.append("=" * 100)
    output.append("")
    
    for i, box in enumerate(boxes, 1):
        box_id = box.get("id", "")[:8]
        bg = box.get("backgroundColor", "transparent")
        
        output.append(f"[{i}] Box {box_id} (bg={bg})")
        
        # Find bound text
        bound_elems = box.get("boundElements", [])
        for bound in bound_elems:
            if bound.get("type") == "text":
                text_id = bound.get("id")
                text_elem = elem_map.get(text_id)
                if text_elem:
                    text_content = text_elem.get("text", "")
                    if text_content:
                        output.append(f"📝 Text: {text_content}")
        
        output.append("")
    
    output.append("")
    output.append("=" * 100)
    output.append("➡️  ALL ARROW LABELS (105 total)")
    output.append("=" * 100)
    output.append("")
    
    for i, arrow in enumerate(arrows, 1):
        arrow_id = arrow.get("id", "")[:8]
        
        # Get connected elements
        start_binding = arrow.get("startBinding")
        end_binding = arrow.get("endBinding")
        
        start_id = start_binding.get("elementId")[:8] if start_binding else "none"
        end_id = end_binding.get("elementId")[:8] if end_binding else "none"
        
        output.append(f"[{i}] Arrow {arrow_id}: {start_id} → {end_id}")
        
        # Find arrow label
        bound_elems = arrow.get("boundElements", [])
        for bound in bound_elems:
            if bound.get("type") == "text":
                text_id = bound.get("id")
                text_elem = elem_map.get(text_id)
                if text_elem:
                    label = text_elem.get("text", "")
                    if label:
                        output.append(f"   Label: {label}")
        
        output.append("")
    
    output.append("")
    output.append("=" * 100)
    output.append("📝 ALL STANDALONE TEXTS (218 total)")
    output.append("=" * 100)
    output.append("")
    
    standalone_count = 0
    for text in texts:
        # Skip if bound to something
        if text.get("containerId"):
            continue
        
        standalone_count += 1
        text_id = text.get("id", "")[:8]
        content = text.get("text", "")
        
        output.append(f"[{standalone_count}] Text {text_id}:")
        output.append(f"{content}")
        output.append("")
    
    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_all_texts.py <json_file>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print(f"📖 Reading: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON loaded!")
        print("🔍 Extracting all texts...")
        
        all_texts = extract_all_texts(data)
        
        # Save to file
        output_file = json_file.with_name(json_file.stem + ".all_texts.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(all_texts)
        
        print(f"✅ All texts saved to: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
        
        # Also print first 100 lines
        lines = all_texts.split('\n')
        print(f"\n📄 First 100 lines:\n")
        print('\n'.join(lines[:100]))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
