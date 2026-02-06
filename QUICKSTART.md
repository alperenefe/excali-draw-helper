# ⚡ Quick Start Guide

## 🚀 Installation

No installation required! Just copy the `excalidraw_builder` folder to your project.

```bash
# Clone or download this project
cd excalidraw-diagram-builder
```

## ✅ Run Examples

### Simple Example (3-tier architecture):

```bash
PYTHONPATH=/Users/alperen.uretmen/excalidraw-diagram-builder python3 examples/simple_example.py
```

**Output:** `output/simple_architecture.excalidraw` (15 KB, 9 elements)

### Complex Example (Home Furniture Flow):

```bash
PYTHONPATH=/Users/alperen.uretmen/excalidraw-diagram-builder python3 examples/home_furniture_flow.py
```

**Output:** `output/home_furniture_cross_reco_flow.excalidraw` (96 KB, 56 elements)

## 📖 Create Your Own Diagram

### Step 1: Import

```python
from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Text,
    Position,
    BoxStyle,
    ArrowStyle,
)
```

### Step 2: Create Diagram

```python
diagram = ExcalidrawDiagram("My Diagram")
```

### Step 3: Add Elements

```python
# Add title
diagram.add(Text(
    pos=Position(x=400, y=100, width=800, height=60),
    text="My System Architecture",
    font_size=48,
    align="center"
))

# Add boxes
db = Box(
    pos=Position(x=300, y=300, width=200, height=100),
    text="Database\n(PostgreSQL)",
    style=BoxStyle.data_source()
)

api = Box(
    pos=Position(x=600, y=300, width=200, height=100),
    text="API\n(FastAPI)",
    style=BoxStyle.success(bold=True)
)

diagram.add([db, api])
```

### Step 4: Connect Elements

```python
diagram.connect(db, api, label="queries", style=ArrowStyle.success())
```

### Step 5: Save

```python
diagram.save("output/my_diagram.excalidraw")
```

## 🎨 Style Presets

### Box Styles
- `BoxStyle.success()` → Green (completed/successful)
- `BoxStyle.warning()` → Orange (in-progress/warning)
- `BoxStyle.error()` → Red (error/critical)
- `BoxStyle.info()` → Blue (information)
- `BoxStyle.data_source()` → Light green (databases)
- `BoxStyle.default()` → White (generic)

### Arrow Styles
- `ArrowStyle.success()` → Green arrow
- `ArrowStyle.warning()` → Orange arrow
- `ArrowStyle.error()` → Red arrow
- `ArrowStyle.info()` → Blue arrow
- `ArrowStyle.default()` → Black arrow

**Make bold:** Add `bold=True` parameter:
```python
BoxStyle.success(bold=True)  # Thick border (3px instead of 2px)
```

## 📍 Positioning

### Basic Position

```python
pos = Position(x=100, y=100, width=200, height=100)
```

### Anchor Points

```python
# Get connection points
center = pos.center()           # (200, 150)
top_center = pos.top_center()   # (200, 100)
bottom_center = pos.bottom_center()  # (200, 200)
left_center = pos.left_center()      # (100, 150)
right_center = pos.right_center()    # (300, 150)
```

## 🔗 Auto-Connection

The `diagram.connect()` method automatically calculates connection points:

```python
# Connects right side of box1 to left side of box2
diagram.connect(box1, box2, label="data flow")
```

## 📂 Output Format

Generated files are in Excalidraw JSON format (`.excalidraw`).

**Open in Excalidraw:**
1. Go to [excalidraw.com](https://excalidraw.com)
2. Click **Open** or drag & drop the `.excalidraw` file
3. Edit, export as PNG/SVG, or share!

## 💡 Tips

### Keep Diagrams Clean
- Use consistent spacing (e.g., 300px between elements)
- Group related elements with similar colors
- Use numbered circles to show flow steps

### Reusable Layouts
```python
# Define a grid layout
START_X = 300
START_Y = 300
SPACING = 300

boxes = []
for i in range(3):
    box = Box(
        pos=Position(x=START_X + i * SPACING, y=START_Y, width=200, height=100),
        text=f"Service {i+1}",
        style=BoxStyle.success()
    )
    boxes.append(box)

diagram.add(boxes)
```

### Complex Flows
```python
# Create flow with multiple paths
diagram.connect(source, service1, style=ArrowStyle.success())
diagram.connect(source, service2, style=ArrowStyle.warning())
diagram.connect(service1, target, style=ArrowStyle.success())
diagram.connect(service2, target, style=ArrowStyle.warning())
```

## 🐛 Troubleshooting

### ModuleNotFoundError

```bash
# Make sure to set PYTHONPATH
PYTHONPATH=/path/to/excalidraw-diagram-builder python3 your_script.py
```

### Invalid JSON Error in Excalidraw

Check if:
- All element IDs are unique
- All referenced element IDs exist
- JSON is valid (use `python3 -m json.tool output.excalidraw`)

## 📚 More Examples

See the `examples/` folder:
- `simple_example.py` - Basic 3-tier architecture
- `home_furniture_flow.py` - Complex data pipeline with 56 elements

## 🤝 Need Help?

Check the full README.md for detailed API documentation!

---

Happy diagramming! 🎨
