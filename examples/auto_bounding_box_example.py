"""
Example: Automatic bounding box calculation based on contained elements
"""

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Text,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_auto_bounding_box_diagram():
    """Demonstrate automatic bounding box sizing based on contents."""
    
    diagram = ExcalidrawDiagram("Auto Bounding Box Example")
    
    # Title
    diagram.add(Text(
        pos=Position(x=300, y=50, width=800, height=60),
        text="Automatic Bounding Box Example",
        font_size=36,
        align="center"
    ))
    
    # =================================================================
    # GROUP 1: Data Processing Pipeline (will be auto-wrapped)
    # =================================================================
    
    source = Box(
        pos=Position(x=100, y=200, width=200, height=100),
        text="Data Source\n(Kafka)",
        style=BoxStyle.data_source()
    )
    
    processor = Box(
        pos=Position(x=400, y=200, width=200, height=100),
        text="Processor\n(Spark)",
        style=BoxStyle.warning()
    )
    
    storage = Box(
        pos=Position(x=700, y=200, width=200, height=100),
        text="Storage\n(HDFS)",
        style=BoxStyle.success()
    )
    
    # Add elements first
    diagram.add([source, processor, storage])
    
    # Connect
    diagram.connect(source, processor, label="stream", style=ArrowStyle.default())
    diagram.connect(processor, storage, label="write", style=ArrowStyle.success())
    
    # Create automatic bounding box for Group 1
    # No need to call add_to_back() - bounding boxes are automatically rendered in background!
    group1_bbox = diagram.create_bounding_box_for_elements(
        elements=[source, processor, storage],
        title="Phase 1: Data Ingestion",
        padding=50,  # Space around elements
        stroke_style="dashed",
        stroke_color=Color.BLUE_DARK,
        stroke_width=2
    )
    diagram.add(group1_bbox)
    
    # =================================================================
    # GROUP 2: Analytics Layer (different size, auto-calculated)
    # =================================================================
    
    analytics1 = Box(
        pos=Position(x=150, y=450, width=180, height=80),
        text="Analytics\nEngine 1",
        style=BoxStyle.info()
    )
    
    analytics2 = Box(
        pos=Position(x=400, y=450, width=180, height=80),
        text="Analytics\nEngine 2",
        style=BoxStyle.info()
    )
    
    dashboard = Box(
        pos=Position(x=650, y=450, width=180, height=80),
        text="Dashboard\n(Grafana)",
        style=BoxStyle.default()
    )
    
    api = Box(
        pos=Position(x=900, y=450, width=150, height=80),
        text="API\n(REST)",
        style=BoxStyle.default()
    )
    
    # Add elements
    diagram.add([analytics1, analytics2, dashboard, api])
    
    # Connect
    diagram.connect(analytics1, dashboard, label="data")
    diagram.connect(analytics2, dashboard, label="data")
    diagram.connect(dashboard, api, label="query")
    
    # Create automatic bounding box for Group 2 (different size, auto-calculated!)
    group2_bbox = diagram.create_bounding_box_for_elements(
        elements=[analytics1, analytics2, dashboard, api],
        title="Phase 2: Analytics & Visualization",
        padding=40,  # Different padding
        stroke_style="dashed",
        stroke_color=Color.GREEN_DARK,
        stroke_width=2
    )
    diagram.add(group2_bbox)
    
    # =================================================================
    # GROUP 3: Small monitoring box (auto-sized to tiny contents)
    # =================================================================
    
    monitor = Box(
        pos=Position(x=1150, y=200, width=120, height=60),
        text="Monitor",
        style=BoxStyle.error()
    )
    
    alert = Box(
        pos=Position(x=1150, y=300, width=120, height=60),
        text="Alerts",
        style=BoxStyle.warning()
    )
    
    diagram.add([monitor, alert])
    diagram.connect(monitor, alert, label="trigger")
    
    # Small bounding box (auto-sized to small contents)
    group3_bbox = diagram.create_bounding_box_for_elements(
        elements=[monitor, alert],
        padding=30,
        stroke_style="dotted",
        stroke_color=Color.RED_DARK,
        stroke_width=1
    )
    diagram.add(group3_bbox)
    
    # Cross-group connections
    diagram.connect(storage, analytics1, label="feed", style=ArrowStyle(stroke_style="dashed"))
    diagram.connect(storage, analytics2, label="feed", style=ArrowStyle(stroke_style="dashed"))
    diagram.connect(processor, monitor, label="metrics", style=ArrowStyle.error())
    
    return diagram


if __name__ == "__main__":
    diagram = create_auto_bounding_box_diagram()
    diagram.save("output/auto_bounding_box_example.excalidraw")
    print(f"✅ Created diagram with {len(diagram.elements)} elements")
    print("📦 Bounding boxes automatically sized based on contents!")
    print("   - Group 1: 3 boxes with 50px padding")
    print("   - Group 2: 4 boxes with 40px padding (different size!)")
    print("   - Group 3: 2 small boxes with 30px padding")
