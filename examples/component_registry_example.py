"""
Component Registry Example: Multi-Phase Architecture

Demonstrates how to use ComponentRegistry to maintain consistent colors
for components that appear in multiple phases.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    BoundingBox,
    Position,
    BoxStyle,
    ComponentRegistry,
    ComponentColors,
)


def main():
    """Create a multi-phase diagram with consistent component colors."""
    diagram = ExcalidrawDiagram(title="Component Registry Example")
    
    # ==================== COMPONENT REGISTRY ====================
    # Register components that appear in multiple phases
    registry = ComponentRegistry()
    registry.register("shared_database", ComponentColors.PURPLE)
    registry.register("api_service", ComponentColors.GREEN)
    registry.register("cache_layer", ComponentColors.BLUE)
    
    # ==================== PHASE 1: DATA INGESTION ====================
    
    phase1_x, phase1_y = 100, 100
    
    # Shared Database (first appearance)
    db_p1_pos = Position(x=phase1_x, y=phase1_y, width=200, height=100)
    db_p1 = Box(
        pos=db_p1_pos,
        text="📦 Shared Database\n\nUser Data",
        style=registry.get_style("shared_database")  # Purple - from registry
    )
    diagram.add(db_p1)
    
    # Ingestion Job (unique to Phase 1)
    job_pos = db_p1_pos.below(spacing=80)
    job = Box(
        pos=job_pos,
        text="⚙️ Ingestion Job\n\nCollects data",
        style=BoxStyle.default()  # Not shared - default color
    )
    diagram.add(job)
    
    arrow1 = diagram.connect(job, db_p1, label="① writes")
    
    phase1_elements = [db_p1, job, arrow1]
    phase1_bbox = diagram.create_bounding_box_for_elements(
        elements=phase1_elements,
        title="Phase 1: Data Ingestion",
        padding=30
    )
    diagram.add_to_back(phase1_bbox)
    
    # ==================== PHASE 2: PROCESSING ====================
    
    phase2_x = phase1_x + 400
    phase2_y = 100
    
    # Shared Database (duplicate - automatically same purple!)
    db_p2_pos = Position(x=phase2_x, y=phase2_y, width=200, height=100)
    db_p2 = Box(
        pos=db_p2_pos,
        text="📦 Shared Database\n\nUser Data",
        style=registry.get_style("shared_database")  # Same purple!
    )
    diagram.add(db_p2)
    
    # API Service (first appearance)
    api_pos = db_p2_pos.below(spacing=80)
    api = Box(
        pos=api_pos,
        text="🔧 API Service\n\nProcesses requests",
        style=registry.get_style("api_service")  # Green - from registry
    )
    diagram.add(api)
    
    # Cache (first appearance)
    cache_pos = api_pos.below(spacing=80)
    cache = Box(
        pos=cache_pos,
        text="💾 Cache Layer\n\nRedis",
        style=registry.get_style("cache_layer")  # Blue - from registry
    )
    diagram.add(cache)
    
    arrow2 = diagram.connect(db_p2, api, label="① reads")
    arrow3 = diagram.connect(api, cache, label="② updates")
    
    phase2_elements = [db_p2, api, cache, arrow2, arrow3]
    phase2_bbox = diagram.create_bounding_box_for_elements(
        elements=phase2_elements,
        title="Phase 2: Processing",
        padding=30
    )
    diagram.add_to_back(phase2_bbox)
    
    # ==================== PHASE 3: SERVING ====================
    
    phase3_x = phase2_x + 400
    phase3_y = 100
    
    # API Service (duplicate - automatically same green!)
    api_p3_pos = Position(x=phase3_x, y=phase3_y, width=200, height=100)
    api_p3 = Box(
        pos=api_p3_pos,
        text="🔧 API Service\n\nProcesses requests",
        style=registry.get_style("api_service")  # Same green!
    )
    diagram.add(api_p3)
    
    # Cache (duplicate - automatically same blue!)
    cache_p3_pos = api_p3_pos.below(spacing=80)
    cache_p3 = Box(
        pos=cache_p3_pos,
        text="💾 Cache Layer\n\nRedis",
        style=registry.get_style("cache_layer")  # Same blue!
    )
    diagram.add(cache_p3)
    
    # Client (unique to Phase 3)
    client_pos = cache_p3_pos.below(spacing=80)
    client = Box(
        pos=client_pos,
        text="👤 Client\n\nEnd user",
        style=BoxStyle.default()  # Not shared - default color
    )
    diagram.add(client)
    
    arrow4 = diagram.connect(api_p3, cache_p3, label="① checks")
    arrow5 = diagram.connect(cache_p3, api_p3, label="② returns")
    arrow6 = diagram.connect(api_p3, client, label="③ serves")
    
    phase3_elements = [api_p3, cache_p3, client, arrow4, arrow5, arrow6]
    phase3_bbox = diagram.create_bounding_box_for_elements(
        elements=phase3_elements,
        title="Phase 3: Serving",
        padding=30
    )
    diagram.add_to_back(phase3_bbox)
    
    # ==================== EXPORT ====================
    
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    file_path = output_dir / "component_registry_example.excalidraw"
    clipboard_path = output_dir / "component_registry_example_clipboard.json"
    
    diagram.save(str(file_path), clipboard_format=False)
    diagram.save(str(clipboard_path), clipboard_format=True)
    
    print(f"✅ Diagram created with {len(diagram.elements)} elements")
    print()
    print("🎨 COMPONENT REGISTRY USAGE:")
    print()
    print("  Shared Components (consistent colors across phases):")
    print("    • Shared Database: 🟣 Purple (Phase 1 & 2)")
    print("    • API Service:     🟢 Green  (Phase 2 & 3)")
    print("    • Cache Layer:     🔵 Blue   (Phase 2 & 3)")
    print()
    print("  Unique Components (default color):")
    print("    • Ingestion Job: ⚪ Default (Phase 1 only)")
    print("    • Client:        ⚪ Default (Phase 3 only)")
    print()
    print("💾 Output:")
    print(f"  • {file_path.name}")
    print(f"  • {clipboard_path.name}")


if __name__ == "__main__":
    main()
