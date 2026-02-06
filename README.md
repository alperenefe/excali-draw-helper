# 🎨 Excalidraw Diagram Builder

Python library to programmatically create [Excalidraw](https://excalidraw.com) diagrams with smart auto-sizing and collision detection.

## ✨ Key Features

- 🤖 **Auto-sizing**: Width/height calculated automatically from text content
- 📏 **Smart text wrapping**: Auto-wraps lines >70 chars (configurable)
- 🎯 **Collision detection**: Enforces 100px+ spacing between all elements
- 🔗 **Smart arrows**: Auto-binding, bidirectional offset, parallel detection
- 🎨 **Style presets**: Success, Warning, Error, Info, DataSource
- 📍 **Relative positioning**: `.below()`, `.right_of()`, etc.

## 🚀 Quick Start

```python
from excalidraw_builder import ExcalidrawDiagram, Box, Position, BoxStyle

diagram = ExcalidrawDiagram("My Pipeline")

# Auto-sizing: width=0, height=0
box1 = Box(
    pos=Position(x=100, y=100, width=0, height=0),  # Auto!
    text="""[1] Scheduler
scr_keep_prod_table_name

Every 6 hours | europe""",
    style=BoxStyle.warning(bold=True)
)
diagram.add(box1)

# Position relative + auto-size
box2 = Box(
    pos=box1.pos.below(spacing=100).with_size(width=0, height=0),
    text="[2] Output Table\n\ndsm-data.dataset.table",
    style=BoxStyle.success(bold=True)
)
diagram.add(box2)

# Smart arrow (auto-binds to box edges)
diagram.connect(box1, box2, "WRITES", style=ArrowStyle.success())

diagram.save("output/pipeline.excalidraw")
```

## 📦 Core Components

### Automatic Bounding Boxes

Bounding boxes automatically calculate their size based on contained elements:

```python
# Create elements
box1 = Box(pos=Position(x=100, y=200, width=200, height=100), text="Source")
box2 = Box(pos=Position(x=400, y=200, width=200, height=100), text="Process")
box3 = Box(pos=Position(x=700, y=200, width=200, height=100), text="Output")

diagram.add([box1, box2, box3])
diagram.connect(box1, box2, "flow")
diagram.connect(box2, box3, "flow")

# Auto-sized bounding box wraps all 3 boxes!
phase_bbox = diagram.create_bounding_box_for_elements(
    elements=[box1, box2, box3],
    title="Phase 1: Data Pipeline",
    padding=50,  # Space around elements
    stroke_style="dashed",
    stroke_color=Color.BLUE_DARK,
    stroke_width=2
)

# Add to background (renders behind elements)
diagram.add_to_back(phase_bbox)
```

**Benefits:**
- ✅ **Auto-calculates** min/max bounds from all elements
- ✅ **Configurable padding** around contents
- ✅ **Arrows included** in bound calculation
- ✅ **Z-order control** via `add_to_back()`

See `examples/auto_bounding_box_example.py` for full demo.

**Converting manual to automatic:**

```python
# ❌ BEFORE (manual - brittle, needs updates when contents change)
phase1_box = Box(
    pos=Position(x=50, y=100, width=1750, height=550),  # Hard-coded!
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, 
                   border_style="dashed", background_color="transparent")
)
diagram.add(phase1_box)

# ✅ AFTER (automatic - adapts to contents)
# First add all phase 1 elements
diagram.add([source_box, scheduler, output_table])
diagram.connect(source_box, scheduler, "reads")
diagram.connect(scheduler, output_table, "writes")

# Then create auto-sized bounding box
phase1_bbox = diagram.create_bounding_box_for_elements(
    elements=[source_box, scheduler, output_table],
    padding=50,
    stroke_style="dashed",
    stroke_color=Color.GRAY
)
diagram.add_to_back(phase1_bbox)  # Renders behind elements
```

### Box - Smart Auto-Sizing

```python
# Full auto (recommended)
box = Box(
    pos=Position(x=100, y=200, width=0, height=0),  # Auto-calculate
    text="Long table: scr_keep_prod_image_tag_indexing_incremental_core",
    max_chars=70  # Auto-wrap lines >70 chars (default)
)

# Manual size
box = Box(
    pos=Position(x=100, y=200, width=500, height=300),
    text="Fixed size box",
    auto_wrap=False  # Disable wrapping
)
```

**How it works:**
1. ✅ Lines >70 chars → Auto-wrapped (safety)
2. ✅ Width → Longest line × 9px + 30px padding
3. ✅ Height → Line count × 19px + 40px padding
4. ✅ Manual splits preserved

### Arrow - Smart Binding

```python
# Auto-binding (recommended)
diagram.connect(source_box, target_box, "label", ArrowStyle.success())

# Manual arrow
arrow = Arrow(start=(100, 150), end=(300, 150), label="flow")
diagram.add(arrow)
```

**Smart features:**
- Auto-binds to box edges (stays connected when moved)
- Auto-offsets parallel arrows (prevents overlap)
- Bidirectional detection (A→B and B→A get offset)

### Text

```python
Text(pos=Position(x=400, y=50, width=800, height=60),
     text="Diagram Title", font_size=48, align="center")
```

## 🎨 Style Presets

```python
BoxStyle.success(bold=True)    # Green - completed/active
BoxStyle.warning(bold=True)    # Orange - in-progress
BoxStyle.error(bold=True)      # Red - errors/critical
BoxStyle.info(bold=True)       # Blue - information
BoxStyle.data_source()         # Light green - databases
BoxStyle.default()             # White - generic

ArrowStyle.success()  # Green solid
ArrowStyle.default()  # Gray dashed (reads)
```

## 📍 Relative Positioning

```python
box2_pos = box1.pos.below(spacing=100)       # Below box1
box3_pos = box1.pos.right_of(spacing=150)    # Right of box1
box4_pos = box1.pos.left_of(spacing=100)     # Left of box1

# Chainable
pos = box1.pos.below(100).with_size(width=0, height=0)
```

## 🔍 Collision Detection

Validates spacing after diagram generation:

```bash
python collision_detector.py output/diagram.excalidraw
```

**Rules enforced:**
- Bounding boxes: 150px minimum margin
- Content boxes: 100px minimum margin

**Output:**
```
✅ NO COLLISIONS DETECTED!

# Or if issues found:
🟡 CONTENT BOXES TOO CLOSE:
  Box 1: [100, 1140] Ends at: y=1522
  Box 2: [100, 1560]
  Vertical Gap: 38px (recommended: ≥100px)
  
  💡 FIX: Move Box 2 to y=1622 (shift: +62px)
```

## 🎯 Best Practices

### 1. Use Auto-Sizing
```python
# ✅ Good - auto-calculates
Box(pos=Position(x=100, y=200, width=0, height=0), text="...")

# ❌ Avoid - manual size can overflow
Box(pos=Position(x=100, y=200, width=300, height=100), text="...")
```

### 2. Manual Split + Safety
```python
# ✅ Best - you control splits, auto-wrap as safety
text = """[1] Title
Line 1 (manually split)
Line 2 (manually split)"""

box = Box(pos=Position(x=100, y=200, width=0, height=0), text=text)
# If you forget and add 80-char line → auto-wraps it
```

### 3. Phase Grouping
```python
# Bounding box for phase
phase_box = Box(
    pos=Position(x=50, y=50, width=1500, height=800),
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, 
                   border_style="dashed", background_color="transparent")
)

# Add content boxes inside (x: 100-1400, y: 100-750)
```

### 4. Validate Spacing
```python
diagram.save("output/diagram.excalidraw")

# Validate
import subprocess
result = subprocess.run(["python3", "collision_detector.py", 
                        "output/diagram.excalidraw"])
if result.returncode != 0:
    print("⚠️ Spacing issues - review collision report")
```

## 🛠️ API Reference

### ExcalidrawDiagram
```python
diagram = ExcalidrawDiagram("Title")
diagram.add(element)                    # Add element
diagram.connect(box1, box2, "label")    # Smart arrow
diagram.save("file.excalidraw")         # Save
```

### Box
```python
Box(pos, text, style, auto_wrap=True, max_chars=70)
Box.calculate_height(text) → int        # Manual height calc
Box.calculate_width(text) → int         # Manual width calc
Box.wrap_text(text, max_chars) → str    # Manual wrapping
Box.auto_size(text, max_chars) → (w, h, wrapped_text)
```

### Position
```python
Position(x, y, width, height)
pos.below(spacing) → Position
pos.right_of(spacing) → Position
pos.left_of(spacing) → Position
pos.with_size(width, height) → Position
pos.center() → (x, y)
```

### Arrow
```python
Arrow(start, end, label, style, start_binding, end_binding)
```

### ArrowStyle
```python
ArrowStyle(color, width, style, arrow_start, arrow_end)
ArrowStyle.success()  # Green solid
ArrowStyle.default()  # Gray dashed
```

## 📝 Complete Example

```python
from excalidraw_builder import *

diagram = ExcalidrawDiagram("Fashion Pipeline")

# Title
diagram.add(Text(
    pos=Position(x=800, y=50, width=1600, height=60),
    text="FASHION AS-IS PIPELINE", font_size=38, align="center"
))

# Phase 1: Scheduled Query
sq = Box(
    pos=Position(x=500, y=200, width=0, height=0),
    text="""[1] Scheduled Query
scr_keep_prod_image_tag_indexing
_incremental_core_scheduler

Every 6 hours | europe-west1""",
    style=BoxStyle.warning(bold=True)
)
diagram.add(sq)

# Output table
table = Box(
    pos=sq.pos.below(120).with_size(width=0, height=0),
    text="""[2] BQ Table
dsm-data.datascience.table

11.2M rows | 2.5 GB
Updated: 2026-02-05""",
    style=BoxStyle.success(bold=True)
)
diagram.add(table)

# Connect
diagram.connect(sq, table, "(1) WRITES", ArrowStyle.success())

# Validate
diagram.save("output/pipeline.excalidraw")
subprocess.run(["python3", "collision_detector.py", "output/pipeline.excalidraw"])
```

## 🔧 Configuration

### Text Wrapping
```python
box = Box(..., max_chars=70)    # Default: 70 chars
box = Box(..., max_chars=50)    # Shorter lines
box = Box(..., auto_wrap=False) # Disable
```

### Sizing Parameters
```python
# Width calculation: longest_line × char_width + padding
Box.calculate_width(text, char_width=9, padding=30, min_width=200, max_width=800)

# Height calculation: line_count × line_height + padding
Box.calculate_height(text, line_height=19, padding=40, min_height=80)
```

### Collision Detection
```python
# Adjust minimum margins (defaults: bounding=150px, content=100px)
python collision_detector.py diagram.excalidraw  # Uses defaults
```

## 📄 License

MIT - Use freely!

---

**Generated diagrams are compatible with [Excalidraw](https://excalidraw.com)** - open, edit, and export as PNG/SVG.
