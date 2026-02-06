"""
Simple example: Basic architecture diagram
"""

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Text,
    Circle,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_simple_diagram():
    """Create a simple 3-tier architecture diagram."""
    
    diagram = ExcalidrawDiagram("Simple Architecture")
    
    # Title
    diagram.add(Text(
        pos=Position(x=400, y=100, width=800, height=60),
        text="3-Tier Architecture",
        font_size=48,
        align="center"
    ))
    
    # Frontend
    frontend = Box(
        pos=Position(x=300, y=300, width=200, height=100),
        text="Frontend\n(React)",
        style=BoxStyle.info()
    )
    
    # Backend
    backend = Box(
        pos=Position(x=600, y=300, width=200, height=100),
        text="Backend\n(FastAPI)",
        style=BoxStyle.success(bold=True)
    )
    
    # Database
    database = Box(
        pos=Position(x=900, y=300, width=200, height=100),
        text="Database\n(PostgreSQL)",
        style=BoxStyle.data_source()
    )
    
    diagram.add([frontend, backend, database])
    
    # Add step numbers
    diagram.add([
        Circle(pos=Position(x=270, y=320, width=30, height=40), text="1", color=Color.BLUE_LIGHT),
        Circle(pos=Position(x=570, y=320, width=30, height=40), text="2", color=Color.GREEN_LIGHT),
        Circle(pos=Position(x=870, y=320, width=30, height=40), text="3", color=Color.GREEN_PALE),
    ])
    
    # Connect with arrows
    diagram.connect(frontend, backend, label="API calls", style=ArrowStyle.info())
    diagram.connect(backend, database, label="queries", style=ArrowStyle.success())
    
    return diagram


if __name__ == "__main__":
    diagram = create_simple_diagram()
    diagram.save("output/simple_architecture.excalidraw")
    print(f"✅ Created simple diagram with {len(diagram.elements)} elements")
