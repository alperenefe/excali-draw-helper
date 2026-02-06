"""
Example: Place numbered circles on arrow midpoints
"""

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Circle,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_arrow_midpoint_example():
    """Demonstrate placing circles on arrow midpoints."""
    
    diagram = ExcalidrawDiagram("Arrow Midpoint Circles")
    
    # Create boxes
    box1 = Box(
        pos=Position(x=200, y=300, width=200, height=100),
        text="Service A",
        style=BoxStyle.success()
    )
    
    box2 = Box(
        pos=Position(x=600, y=300, width=200, height=100),
        text="Service B",
        style=BoxStyle.info()
    )
    
    box3 = Box(
        pos=Position(x=200, y=500, width=200, height=100),
        text="Service C",
        style=BoxStyle.warning()
    )
    
    diagram.add([box1, box2, box3])
    
    # Create arrows and place circles on midpoints
    
    # Arrow 1: A -> B (horizontal)
    arrow1 = diagram.connect(box1, box2, label="", style=ArrowStyle.success())
    circle1 = Circle(
        pos=arrow1.midpoint_pos(),  # 👈 Otomatik ortada!
        text="1",
        color=Color.GREEN_LIGHT
    )
    diagram.add(circle1)
    
    # Arrow 2: A -> C (vertical)
    arrow2 = diagram.connect(box1, box3, label="", style=ArrowStyle.warning())
    circle2 = Circle(
        pos=arrow2.midpoint_pos(),  # 👈 Otomatik ortada!
        text="2",
        color=Color.ORANGE_LIGHT
    )
    diagram.add(circle2)
    
    # Arrow 3: C -> B (diagonal)
    arrow3 = diagram.connect(box3, box2, label="", style=ArrowStyle.info())
    circle3 = Circle(
        pos=arrow3.midpoint_pos(),  # 👈 Otomatik ortada!
        text="3",
        color=Color.BLUE_LIGHT
    )
    diagram.add(circle3)
    
    return diagram


if __name__ == "__main__":
    diagram = create_arrow_midpoint_example()
    diagram.save("output/arrow_midpoint_circles.excalidraw")
    diagram.save("output/arrow_midpoint_circles_clipboard.json", clipboard_format=True)
    
    print(f"✅ Created {len(diagram.elements)} elements")
    print("🎯 Circles automatically placed on arrow midpoints!")
    print("\nUsage:")
    print("  arrow = diagram.connect(box1, box2)")
    print("  circle = Circle(pos=arrow.midpoint_pos(), text='1')")
