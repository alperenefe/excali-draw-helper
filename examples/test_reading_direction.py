"""
Test: Reading Direction for Bidirectional Arrows
Demonstrates the natural left→right, top→bottom arrow positioning
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Position,
    BoxStyle,
)


def main():
    """Test reading direction logic for bidirectional arrows."""
    diagram = ExcalidrawDiagram(title="Reading Direction Test")
    
    # HORIZONTAL LAYOUT TEST (side-by-side)
    # Expected: Request arrow TOP, Response arrow BOTTOM
    
    service_a_pos = Position(x=100, y=100, width=200, height=100)
    service_a = Box(
        pos=service_a_pos,
        text="Service A\n(Client)",
        style=BoxStyle.info()
    )
    diagram.add(service_a)
    
    service_b_pos = service_a_pos.right_of(spacing=200)
    service_b = Box(
        pos=service_b_pos,
        text="Service B\n(Server)",
        style=BoxStyle.success()
    )
    diagram.add(service_b)
    
    # First arrow (outgoing): should be TOP
    diagram.connect(service_a, service_b, label="① Request (TOP)")
    
    # Second arrow (return): should be BOTTOM
    diagram.connect(service_b, service_a, label="② Response (BOTTOM)")
    
    # VERTICAL LAYOUT TEST (stacked)
    # Expected: Down arrow LEFT, Up arrow RIGHT
    
    service_c_pos = Position(x=100, y=400, width=200, height=100)
    service_c = Box(
        pos=service_c_pos,
        text="Service C\n(Top)",
        style=BoxStyle.warning()
    )
    diagram.add(service_c)
    
    service_d_pos = service_c_pos.below(spacing=200)
    service_d = Box(
        pos=service_d_pos,
        text="Service D\n(Bottom)",
        style=BoxStyle.error()
    )
    diagram.add(service_d)
    
    # First arrow (down): should be LEFT
    diagram.connect(service_c, service_d, label="③ Call (LEFT)")
    
    # Second arrow (up): should be RIGHT
    diagram.connect(service_d, service_c, label="④ Return (RIGHT)")
    
    # Export
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    file_path = output_dir / "test_reading_direction.excalidraw"
    clipboard_path = output_dir / "test_reading_direction_clipboard.json"
    
    diagram.save(str(file_path), clipboard_format=False)
    diagram.save(str(clipboard_path), clipboard_format=True)
    
    print(f"✅ Test diagram created!")
    print()
    print("📖 READING DIRECTION LOGIC:")
    print()
    print("  Horizontal (side-by-side):")
    print("    • Request arrow:  TOP    (follows ⬆️ reading priority)")
    print("    • Response arrow: BOTTOM")
    print()
    print("  Vertical (stacked):")
    print("    • Down arrow: LEFT  (follows ⬅️➡️ reading flow)")
    print("    • Up arrow:   RIGHT")
    print()
    print(f"💾 Output:")
    print(f"  • {file_path.name}")
    print(f"  • {clipboard_path.name}")


if __name__ == "__main__":
    main()
