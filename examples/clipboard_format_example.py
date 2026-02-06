"""
Example: Generate in clipboard format (for copy-paste to Excalidraw)
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


def create_clipboard_example():
    """Create a simple diagram in clipboard format."""
    
    diagram = ExcalidrawDiagram("Clipboard Format Example")
    
    # Title
    diagram.add(Text(
        pos=Position(x=400, y=100, width=800, height=60),
        text="Clipboard Format Test",
        font_size=48,
        align="center",
        font_family=6  # System font (fashion flow style)
    ))
    
    # Box 1
    box1 = Box(
        pos=Position(x=300, y=300, width=200, height=100),
        text="Service A",
        style=BoxStyle.success()
    )
    
    # Box 2
    box2 = Box(
        pos=Position(x=600, y=300, width=200, height=100),
        text="Service B",
        style=BoxStyle.info()
    )
    
    diagram.add([box1, box2])
    
    # Connect
    diagram.connect(box1, box2, label="calls", style=ArrowStyle.success())
    
    # Add numbered circle
    diagram.add(Circle(
        pos=Position(x=270, y=320, width=30, height=40),
        text="1",
        color=Color.GREEN_LIGHT
    ))
    
    return diagram


if __name__ == "__main__":
    diagram = create_clipboard_example()
    
    # Save in both formats
    diagram.save("output/clipboard_format.excalidraw", clipboard_format=False)
    diagram.save("output/clipboard_format_clipboard.json", clipboard_format=True)
    
    print(f"✅ Created {len(diagram.elements)} elements")
    print("📋 clipboard_format.excalidraw → File format (for Excalidraw.com)")
    print("📋 clipboard_format_clipboard.json → Clipboard format (for copy-paste)")
