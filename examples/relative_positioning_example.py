"""
Example: Relative positioning for easy layout
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


def create_relative_layout():
    """Create a diagram using relative positioning."""
    
    diagram = ExcalidrawDiagram("Relative Positioning Demo")
    
    # Title
    diagram.add(Text(
        pos=Position(x=400, y=50, width=800, height=60),
        text="🎯 Search Image Tagging Flow (Simplified)",
        font_size=48,
        align="center",
        font_family=6
    ))
    
    # ========== VERTICAL FLOW ==========
    
    # Box 1: BigQuery (start point)
    bq1_pos = Position(x=300, y=200, width=200, height=100)
    bq1 = Box(pos=bq1_pos, text="📊 BigQuery\n\nProduct Data", style=BoxStyle.default())
    
    # Box 2: 50 birim aşağıda
    tagging_job_pos = bq1_pos.below(spacing=50)
    tagging_job = Box(
        pos=tagging_job_pos,
        text="🔧 Tagging Jobs\n(Go)\nimage tagging",
        style=BoxStyle.success()
    )
    
    # Box 3: 50 birim daha aşağıda
    itsa_pos = tagging_job_pos.below(spacing=50)
    itsa = Box(
        pos=itsa_pos,
        text="🎯 Image Tag\nSimilarity API",
        style=BoxStyle.info()
    )
    
    diagram.add([bq1, tagging_job, itsa])
    
    # ========== HORIZONTAL FLOW ==========
    
    # Box 4: tagging_job'un 300 birim sağında
    bq2_pos = tagging_job_pos.right_of(spacing=300, align="center")
    bq2 = Box(pos=bq2_pos, text="📊 BigQuery\n\nOutput", style=BoxStyle.data_source())
    
    # Box 5: bq2'nin 300 birim sağında
    another_job_pos = bq2_pos.right_of(spacing=300, align="top")
    another_job = Box(
        pos=another_job_pos,
        text="🔧 Tagging Jobs\n(Go)\nsearch_image_tagging",
        style=BoxStyle.warning(bold=True)
    )
    
    diagram.add([bq2, another_job])
    
    # ========== CUSTOM OFFSET ==========
    
    # Numbered circle: tagging_job'un 10 birim üstünde, 20 birim solunda
    circle_pos = tagging_job_pos.offset(dx=-30, dy=-10)
    circle = Circle(
        pos=Position(x=circle_pos.x, y=circle_pos.y, width=28, height=42),
        text="1",
        color=Color.GREEN_LIGHT
    )
    diagram.add(circle)
    
    # GitLab link text: itsa'nın 20 birim altında
    link_pos = itsa_pos.below(spacing=20)
    link = Text(
        pos=Position(x=link_pos.x, y=link_pos.y, width=200, height=20),
        text="Gitlab Link",
        font_size=14,
        color=Color.ORANGE_DARK,
        font_family=6
    )
    link.link = "https://gitlab.trendyol.com/discovery/search-intelligence"
    diagram.add(link)
    
    # Connect boxes
    diagram.connect(bq1, tagging_job, label="read items", style=ArrowStyle.default())
    diagram.connect(tagging_job, itsa, label="get tags", style=ArrowStyle.success())
    diagram.connect(itsa, tagging_job, label="response", style=ArrowStyle.success())
    diagram.connect(tagging_job, bq2, label="writes", style=ArrowStyle.default())
    diagram.connect(bq2, another_job, label="read items", style=ArrowStyle.default())
    
    return diagram


if __name__ == "__main__":
    diagram = create_relative_layout()
    diagram.save("output/relative_positioning.excalidraw")
    diagram.save("output/relative_positioning_clipboard.json", clipboard_format=True)
    
    print(f"✅ Created {len(diagram.elements)} elements")
    print("📍 Used relative positioning:")
    print("  • .below(spacing=50) → 50 birim aşağıda")
    print("  • .right_of(spacing=300) → 300 birim sağında")
    print("  • .offset(dx=-30, dy=-10) → 30 sol, 10 yukarı")
