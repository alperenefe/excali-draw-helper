"""
JSON Summarizer - Create a human-readable summary of Excalidraw JSON
Perfect for quickly understanding large diagrams without reading all JSON.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def get_element_summary(elem: Dict) -> str:
    """Get one-line summary of an element."""
    elem_type = elem.get("type", "unknown")
    elem_id = elem.get("id", "")[:8]
    
    if elem_type == "text":
        text = elem.get("text", "")
        text_preview = text[:60].replace("\n", " ") if len(text) > 60 else text.replace("\n", " ")
        container_id = elem.get("containerId")
        if container_id:
            return f"  └─ Text (bound): \"{text_preview}...\""
        return f"📝 Text [{elem_id}]: \"{text_preview}\""
    
    elif elem_type == "rectangle":
        x, y = elem.get("x", 0), elem.get("y", 0)
        w, h = elem.get("width", 0), elem.get("height", 0)
        bg = elem.get("backgroundColor", "transparent")
        stroke_style = elem.get("strokeStyle", "solid")
        
        if stroke_style == "dashed":
            return f"📦 BoundingBox [{elem_id}]: pos=({x:.0f},{y:.0f}) size={w:.0f}x{h:.0f}"
        return f"🔲 Box [{elem_id}]: pos=({x:.0f},{y:.0f}) size={w:.0f}x{h:.0f} bg={bg}"
    
    elif elem_type == "arrow":
        start_id = elem.get("startBinding", {}).get("elementId", "")[:8] if elem.get("startBinding") else "none"
        end_id = elem.get("endBinding", {}).get("elementId", "")[:8] if elem.get("endBinding") else "none"
        return f"➡️  Arrow [{elem_id}]: {start_id} → {end_id}"
    
    elif elem_type == "ellipse":
        x, y = elem.get("x", 0), elem.get("y", 0)
        w, h = elem.get("width", 0), elem.get("height", 0)
        return f"⭕ Circle [{elem_id}]: pos=({x:.0f},{y:.0f}) size={w:.0f}x{h:.0f}"
    
    elif elem_type == "image":
        x, y = elem.get("x", 0), elem.get("y", 0)
        w, h = elem.get("width", 0), elem.get("height", 0)
        file_id = elem.get("fileId", "")[:16]
        return f"🖼️  Image [{elem_id}]: pos=({x:.0f},{y:.0f}) size={w:.0f}x{h:.0f} file={file_id}..."
    
    elif elem_type == "freedraw":
        return f"✏️  Freedraw [{elem_id}]: hand-drawn element"
    
    elif elem_type == "line":
        return f"━  Line [{elem_id}]"
    
    elif elem_type == "frame":
        name = elem.get("name", "Unnamed")
        return f"🖼️  Frame [{elem_id}]: \"{name}\""
    
    else:
        return f"❓ {elem_type} [{elem_id}]"


def summarize_json(json_data: Dict, show_all: bool = False, max_elements: int = 50) -> str:
    """Create human-readable summary."""
    
    output = []
    output.append("=" * 80)
    output.append("📊 EXCALIDRAW DIAGRAM SUMMARY")
    output.append("=" * 80)
    output.append("")
    
    # Basic info
    diagram_type = json_data.get("type", "unknown")
    output.append(f"Format: {diagram_type}")
    output.append("")
    
    # Elements
    elements = json_data.get("elements", [])
    output.append(f"Total Elements: {len(elements)}")
    output.append("")
    
    # Count by type
    type_counts = defaultdict(int)
    for elem in elements:
        elem_type = elem.get("type", "unknown")
        type_counts[elem_type] += 1
    
    output.append("Element Breakdown:")
    for elem_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        output.append(f"  • {elem_type:15s} : {count:3d}")
    output.append("")
    
    # Files/Images
    files = json_data.get("files", {})
    if files:
        total_size = sum(len(f.get('dataURL', '')) for f in files.values())
        output.append(f"Embedded Images: {len(files)}")
        output.append(f"  Total size: {total_size / 1024 / 1024:.2f} MB (base64 encoded)")
        output.append("")
    
    # Element details
    output.append("=" * 80)
    output.append("🔍 ELEMENT DETAILS")
    output.append("=" * 80)
    output.append("")
    
    # Group related elements
    boxes = []
    arrows = []
    texts = []
    circles = []
    images = []
    others = []
    
    for elem in elements:
        elem_type = elem.get("type", "unknown")
        # Skip bound text elements (they're shown with their parent)
        if elem_type == "text" and elem.get("containerId"):
            continue
        
        if elem_type == "rectangle":
            boxes.append(elem)
        elif elem_type == "arrow":
            arrows.append(elem)
        elif elem_type == "text":
            texts.append(elem)
        elif elem_type == "ellipse":
            circles.append(elem)
        elif elem_type == "image":
            images.append(elem)
        else:
            others.append(elem)
    
    # Show boxes
    if boxes:
        output.append(f"📦 BOXES & RECTANGLES ({len(boxes)} total)")
        output.append("-" * 80)
        for i, box in enumerate(boxes[:max_elements if not show_all else len(boxes)]):
            output.append(get_element_summary(box))
            # Show bound text if exists
            box_id = box.get("id")
            for elem in elements:
                if elem.get("type") == "text" and elem.get("containerId") == box_id:
                    output.append(get_element_summary(elem))
        
        if not show_all and len(boxes) > max_elements:
            output.append(f"  ... and {len(boxes) - max_elements} more boxes (use --all to see)")
        output.append("")
    
    # Show texts
    if texts:
        output.append(f"📝 STANDALONE TEXTS ({len(texts)} total)")
        output.append("-" * 80)
        for i, text in enumerate(texts[:max_elements if not show_all else len(texts)]):
            output.append(get_element_summary(text))
        
        if not show_all and len(texts) > max_elements:
            output.append(f"  ... and {len(texts) - max_elements} more texts")
        output.append("")
    
    # Show arrows
    if arrows:
        output.append(f"➡️  ARROWS & CONNECTIONS ({len(arrows)} total)")
        output.append("-" * 80)
        for i, arrow in enumerate(arrows[:max_elements if not show_all else len(arrows)]):
            output.append(get_element_summary(arrow))
            # Show label if exists
            arrow_id = arrow.get("id")
            for elem in elements:
                if elem.get("type") == "text" and elem.get("containerId") == arrow_id:
                    output.append(get_element_summary(elem))
        
        if not show_all and len(arrows) > max_elements:
            output.append(f"  ... and {len(arrows) - max_elements} more arrows")
        output.append("")
    
    # Show circles
    if circles:
        output.append(f"⭕ CIRCLES ({len(circles)} total)")
        output.append("-" * 80)
        for circle in circles[:max_elements if not show_all else len(circles)]:
            output.append(get_element_summary(circle))
        
        if not show_all and len(circles) > max_elements:
            output.append(f"  ... and {len(circles) - max_elements} more circles")
        output.append("")
    
    # Show images
    if images:
        output.append(f"🖼️  IMAGES ({len(images)} total)")
        output.append("-" * 80)
        for image in images:
            output.append(get_element_summary(image))
        output.append("")
    
    # Show others
    if others:
        output.append(f"❓ OTHER ELEMENTS ({len(others)} total)")
        output.append("-" * 80)
        for other in others[:20]:
            output.append(get_element_summary(other))
        output.append("")
    
    output.append("=" * 80)
    output.append("✅ Summary Complete")
    output.append("=" * 80)
    
    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python json_summarizer.py <excalidraw_json_file> [--all]")
        print("\nExample:")
        print("  python json_summarizer.py core_concepts.json")
        print("  python json_summarizer.py core_concepts.json --all  # Show all elements")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    show_all = "--all" in sys.argv
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print(f"📖 Reading: {json_file}")
    print(f"📏 Size: {json_file.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = summarize_json(data, show_all=show_all)
        
        # Print to console
        print(summary)
        
        # Save to file
        output_file = json_file.with_suffix('.summary.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n💾 Summary saved to: {output_file}")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
