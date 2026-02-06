"""
Inverse Transformer: Excalidraw JSON → Python Code
Converts large Excalidraw JSON files to readable Python code using our builder library.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def hex_to_color_name(hex_color: str) -> str:
    """Map hex colors to our Color class names."""
    color_map = {
        "#1e1e1e": "Color.BLACK",
        "#ffffff": "Color.WHITE",
        "#868e96": "Color.GRAY",
        "#ced4da": "Color.GRAY_LIGHT",
        "#2f9e44": "Color.GREEN_DARK",
        "#b2f2bb": "Color.GREEN_LIGHT",
        "#d3f9d8": "Color.GREEN_PALE",
        "#e8590c": "Color.ORANGE_DARK",
        "#ffe8cc": "Color.ORANGE_LIGHT",
        "#ffd8a8": "Color.ORANGE_MID",
        "#ffec99": "Color.YELLOW_LIGHT",  # Common in your diagram
        "#fff9db": "Color.YELLOW_PALE",   # Common in your diagram
        "#fff4cc": "Color.YELLOW_LIGHT",
        "#fab005": "Color.YELLOW_DARK",
        "#e03131": "Color.RED_DARK",
        "#ffc9c9": "Color.RED_LIGHT",
        "#ffe3e3": "Color.RED_PALE",
        "#1971c2": "Color.BLUE_DARK",
        "#a5d8ff": "Color.BLUE_LIGHT",
        "#d0ebff": "Color.BLUE_PALE",
        "#d0bfff": "Color.PURPLE_LIGHT",
        "#e599f7": "Color.PURPLE_MID",
        "transparent": "Color.TRANSPARENT",
    }
    return color_map.get(hex_color.lower(), f'"{hex_color}"')


def simplify_element(elem: Dict) -> Optional[str]:
    """Convert Excalidraw element to Python code."""
    elem_type = elem.get("type")
    elem_id = elem.get("id", "unknown")[:8]  # Short ID for reference
    
    # Skip text elements that are bound to other elements (they're auto-generated)
    if elem_type == "text" and elem.get("containerId"):
        return None
    
    if elem_type == "rectangle":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        width = elem.get("width", 0)
        height = elem.get("height", 0)
        stroke = hex_to_color_name(elem.get("strokeColor", "#1e1e1e"))
        bg = hex_to_color_name(elem.get("backgroundColor", "transparent"))
        stroke_width = elem.get("strokeWidth", 2)
        
        # Check if it's a bounding box (dashed, large)
        is_bbox = elem.get("strokeStyle") == "dashed" and width > 500
        
        if is_bbox:
            return f"""# Bounding Box (dashed rectangle)
BoundingBox(
    pos=Position(x={x:.0f}, y={y:.0f}, width={width:.0f}, height={height:.0f}),
    title="",  # Add title if needed
    stroke_color={stroke},
    stroke_style="dashed"
)"""
        else:
            return f"""# Box {elem_id}
Box(
    pos=Position(x={x:.0f}, y={y:.0f}, width={width:.0f}, height={height:.0f}),
    text="",  # Add text here
    style=BoxStyle(stroke_color={stroke}, background_color={bg}, stroke_width={stroke_width})
)"""
    
    elif elem_type == "arrow":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        points = elem.get("points", [[0, 0], [100, 0]])
        stroke = hex_to_color_name(elem.get("strokeColor", "#1e1e1e"))
        
        # Calculate end point
        end_x = x + points[-1][0]
        end_y = y + points[-1][1]
        
        start_binding = elem.get("startBinding")
        end_binding = elem.get("endBinding")
        
        start_id = start_binding.get("elementId") if start_binding else None
        end_id = end_binding.get("elementId") if end_binding else None
        
        if start_id and end_id:
            return f"""# Arrow {elem_id} (connected)
diagram.connect(
    from_elem="elem_{start_id[:8]}",  # Replace with actual element variable
    to_elem="elem_{end_id[:8]}",      # Replace with actual element variable
    label="",  # Add label
    style=ArrowStyle(stroke_color={stroke})
)"""
        else:
            return f"""# Arrow {elem_id} (standalone)
Arrow(
    start=({x:.0f}, {y:.0f}),
    end=({end_x:.0f}, {end_y:.0f}),
    label="",  # Add label
    style=ArrowStyle(stroke_color={stroke})
)"""
    
    elif elem_type == "text":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        width = elem.get("width", 200)
        height = elem.get("height", 25)
        text = elem.get("text", "")
        font_size = elem.get("fontSize", 16)
        color = hex_to_color_name(elem.get("strokeColor", "#1e1e1e"))
        align = elem.get("textAlign", "left")
        
        # Escape text
        text_escaped = text.replace('"', '\\"').replace('\n', '\\n')
        text_preview = text[:50] + "..." if len(text) > 50 else text
        
        return f"""# Text {elem_id}: "{text_preview}"
Text(
    pos=Position(x={x:.0f}, y={y:.0f}, width={width:.0f}, height={height:.0f}),
    text="{text_escaped}",
    font_size={font_size},
    color={color},
    align="{align}"
)"""
    
    elif elem_type == "ellipse":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        width = elem.get("width", 40)
        height = elem.get("height", 40)
        bg = hex_to_color_name(elem.get("backgroundColor", "#d0bfff"))
        
        return f"""# Circle {elem_id}
Circle(
    pos=Position(x={x:.0f}, y={y:.0f}, width={width:.0f}, height={height:.0f}),
    text="",  # Add number/text
    color={bg}
)"""
    
    elif elem_type == "image":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        width = elem.get("width", 200)
        height = elem.get("height", 200)
        file_id = elem.get("fileId", "")[:16]
        
        return f"""# Image {elem_id} (file: {file_id}...)
# Note: Images are embedded as base64 data URLs in the JSON
# Position: x={x:.0f}, y={y:.0f}, size={width:.0f}x{height:.0f}
# You may need to handle images separately"""
    
    elif elem_type == "freedraw":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        points = elem.get("points", [])
        stroke = hex_to_color_name(elem.get("strokeColor", "#1e1e1e"))
        stroke_width = elem.get("strokeWidth", 1)
        
        # Get bounding box
        if points:
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            width = max_x - min_x
            height = max_y - min_y
        else:
            width = height = 0
        
        return f"""# Freedraw {elem_id} (hand-drawn)
# Hand-drawn element with {len(points)} points
# Position: x={x:.0f}, y={y:.0f}, bounds={width:.0f}x{height:.0f}
# Stroke: {stroke}, width={stroke_width}
# Note: Freedraw elements are not yet supported in the builder library
# Consider converting to Line or Arrow if needed"""
    
    elif elem_type == "line":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        points = elem.get("points", [[0, 0], [100, 0]])
        stroke = hex_to_color_name(elem.get("strokeColor", "#1e1e1e"))
        stroke_width = elem.get("strokeWidth", 2)
        
        # Calculate end point
        end_x = x + points[-1][0]
        end_y = y + points[-1][1]
        
        start_binding = elem.get("startBinding")
        end_binding = elem.get("endBinding")
        
        start_id = start_binding.get("elementId") if start_binding else None
        end_id = end_binding.get("elementId") if end_binding else None
        
        if start_id and end_id:
            return f"""# Line {elem_id} (connected, no arrowheads)
diagram.connect(
    from_elem="elem_{start_id[:8]}",
    to_elem="elem_{end_id[:8]}",
    label="",
    style=ArrowStyle(stroke_color={stroke}, stroke_width={stroke_width}, end_arrow=False)  # No arrowhead
)"""
        else:
            return f"""# Line {elem_id} (standalone)
# Note: Plain lines (without arrowheads) can be represented as arrows with end_arrow=False
Arrow(
    start=({x:.0f}, {y:.0f}),
    end=({end_x:.0f}, {end_y:.0f}),
    label="",
    style=ArrowStyle(stroke_color={stroke}, stroke_width={stroke_width}, end_arrow=False)
)"""
    
    elif elem_type == "frame":
        x = elem.get("x", 0)
        y = elem.get("y", 0)
        width = elem.get("width", 500)
        height = elem.get("height", 500)
        name = elem.get("name", "")
        
        # Escape name
        name_escaped = name.replace('"', '\\"')
        
        return f"""# Frame {elem_id}: "{name}"
# Frames are used for visual organization/grouping in Excalidraw
# Position: x={x:.0f}, y={y:.0f}, size={width:.0f}x{height:.0f}
# Consider using BoundingBox with dashed style for similar effect:
BoundingBox(
    pos=Position(x={x:.0f}, y={y:.0f}, width={width:.0f}, height={height:.0f}),
    title="{name_escaped}",
    stroke_color=Color.GRAY,
    stroke_style="dashed"
)"""
    
    return None


def generate_python_code(json_data: Dict, max_elements: int = 100) -> str:
    """Generate Python code from Excalidraw JSON."""
    
    elements = json_data.get("elements", [])
    files = json_data.get("files", {})
    
    # Header
    code = '''"""
Auto-generated from Excalidraw JSON using json_to_python.py
This is a SIMPLIFIED version - you'll need to:
1. Add actual text content to boxes
2. Connect arrows properly
3. Adjust positioning as needed
"""

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Arrow,
    Text,
    Circle,
    BoundingBox,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_diagram():
    """Recreate the diagram programmatically."""
    
    diagram = ExcalidrawDiagram("Reconstructed Diagram")
    
    # ========================================================================
    # ELEMENTS
    # ========================================================================
    
'''
    
    # Count elements by type
    type_counts = {}
    for elem in elements:
        elem_type = elem.get("type", "unknown")
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
    
    code += f"    # Total elements: {len(elements)}\n"
    for elem_type, count in sorted(type_counts.items()):
        code += f"    # - {elem_type}: {count}\n"
    
    if len(files) > 0:
        code += f"    # - embedded images: {len(files)} (base64 encoded, total ~{sum(len(f.get('dataURL', '')) for f in files.values()) / 1024 / 1024:.1f} MB)\n"
    
    code += "\n"
    
    # Generate code for elements (limit to avoid huge output)
    processed = 0
    for elem in elements:
        if processed >= max_elements:
            remaining = len(elements) - processed
            code += f"\n    # ... and {remaining} more elements (truncated for brevity)\n"
            code += f"    # Run with max_elements={len(elements)} to see all\n"
            break
        
        elem_code = simplify_element(elem)
        if elem_code:
            code += "\n    " + elem_code.replace("\n", "\n    ") + "\n"
            processed += 1
    
    # Footer
    code += '''
    
    return diagram


if __name__ == "__main__":
    diagram = create_diagram()
    diagram.save("output/reconstructed.excalidraw")
    print(f"✅ Diagram created with {len(diagram.elements)} elements")
'''
    
    return code


def main():
    if len(sys.argv) < 2:
        print("Usage: python json_to_python.py <excalidraw_json_file> [max_elements]")
        print("\nExample:")
        print("  python json_to_python.py core_concepts.json 50")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    max_elements = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print(f"🔄 Converting: {json_file}")
    print(f"📏 Max elements to process: {max_elements}")
    print()
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON loaded successfully!")
        
        # Generate Python code
        python_code = generate_python_code(data, max_elements)
        
        # Save to file
        output_file = json_file.with_suffix('.py')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"✅ Python code saved to: {output_file}")
        print(f"📊 Generated {len(python_code.splitlines())} lines of code")
        
        # Also print summary
        elements = data.get("elements", [])
        files = data.get("files", {})
        
        print("\n" + "=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print(f"Total elements: {len(elements)}")
        
        type_counts = {}
        for elem in elements:
            elem_type = elem.get("type", "unknown")
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        for elem_type, count in sorted(type_counts.items()):
            print(f"  - {elem_type}: {count}")
        
        if files:
            total_size = sum(len(f.get('dataURL', '')) for f in files.values())
            print(f"\nEmbedded images: {len(files)}")
            print(f"  Total size: {total_size / 1024 / 1024:.2f} MB")
            print(f"  Note: Images make up ~{total_size / (json_file.stat().st_size) * 100:.0f}% of JSON size")
        
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
