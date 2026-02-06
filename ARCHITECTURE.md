# 🏗️ Architecture Overview

## 📦 Project Structure

```
excalidraw-diagram-builder/
├── excalidraw_builder/       # Main library
│   ├── __init__.py           # Public API exports
│   ├── core.py               # ExcalidrawDiagram class
│   ├── elements.py           # Element classes (Box, Arrow, Text, Circle)
│   └── styles.py             # Style presets and colors
├── examples/                 # Usage examples
│   ├── simple_example.py
│   ├── home_furniture_flow.py
│   └── clipboard_format_example.py
├── output/                   # Generated diagrams
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
└── ARCHITECTURE.md           # This file
```

## 🎯 Core Concepts

### 1. **Diagram (core.py)**
Main container for all elements.

```python
class ExcalidrawDiagram:
    def add(element) → Add element to diagram
    def connect(from, to) → Create arrow between elements
    def to_json() → Convert to Excalidraw JSON
    def save(path) → Save to file
```

### 2. **Elements (elements.py)**
Visual components.

```python
class Box(Element):          # Rectangle with text
class Arrow(Element):        # Connecting arrow
class Text(Element):         # Standalone text
class Circle(Element):       # Circle/ellipse (for numbering)
class Position:              # Position + size helper
```

Each element has:
- `to_dict()` → Converts to Excalidraw JSON format
- `id`, `seed`, `version` → Excalidraw metadata

### 3. **Styles (styles.py)**
Predefined color schemes and styles.

```python
class Color:                 # Color constants
class BoxStyle:              # Box style presets
    - success() → Green
    - warning() → Orange
    - error() → Red
    - info() → Blue
    - data_source() → Light green

class ArrowStyle:            # Arrow style presets
```

## 🔄 Data Flow

```
User Code
    ↓
ExcalidrawDiagram
    ↓
Elements (Box, Arrow, Text)
    ↓
to_dict() → JSON
    ↓
save() → .excalidraw file
    ↓
Excalidraw.com (render)
```

## 📝 How It Works

### 1. **Element Creation**
```python
box = Box(
    pos=Position(x=100, y=100, width=200, height=100),
    text="My Service",
    style=BoxStyle.success()
)
```

### 2. **Add to Diagram**
```python
diagram = ExcalidrawDiagram("My Flow")
diagram.add(box)
```

### 3. **Connect Elements**
```python
diagram.connect(box1, box2, label="calls")
# Automatically calculates start/end points
# Creates Arrow with bindings
```

### 4. **Export**
```python
diagram.save("output.excalidraw")
# Calls to_dict() on all elements
# Wraps in Excalidraw format
# Writes JSON to file
```

## 🎨 Excalidraw JSON Format

### File Format
```json
{
  "type": "excalidraw",
  "version": 2,
  "elements": [...],
  "appState": {...},
  "files": {}
}
```

### Clipboard Format (for copy-paste)
```json
{
  "type": "excalidraw/clipboard",
  "elements": [...],
  "files": {}
}
```

### Element Format
```json
{
  "id": "xI1SaM0uQkFW3q7VTQtLN",    // Random 21-char ID
  "type": "rectangle",               // rectangle, arrow, text, ellipse
  "x": 100, "y": 100,               // Position
  "width": 200, "height": 100,      // Size
  "strokeColor": "#2f9e44",         // Border color
  "backgroundColor": "#b2f2bb",     // Fill color
  "text": "My Service",              // Text content (for boxes)
  "fontSize": 16,
  "fontFamily": 6,                  // 1=hand-drawn, 6=system font
  "roundness": {"type": 3},         // Rounded corners
  "seed": 123456,                   // Random seed for rendering
  "version": 1,
  "versionNonce": 987654,
  ...
}
```

## 🔧 Key Design Decisions

### 1. **Fashion Flow Compatible**
- Uses `fontFamily: 6` (system font)
- Uses `roundness: {type: 3}` for rectangles
- Generates 21-char random IDs (like Excalidraw)
- Supports both file and clipboard formats

### 2. **No External Dependencies**
- Pure Python stdlib
- Works with Python 3.8+
- No installation needed

### 3. **Immutable-ish Design**
- Elements don't change after creation
- Diagram builds up incrementally
- Easy to reason about

### 4. **Type Safety**
- Full type hints
- Clear interfaces
- IDE autocomplete works

## 🚀 Usage Pattern

### Simple Flow
```python
# 1. Create diagram
diagram = ExcalidrawDiagram("Title")

# 2. Create elements
box1 = Box(pos=..., text=..., style=...)
box2 = Box(pos=..., text=..., style=...)

# 3. Add to diagram
diagram.add([box1, box2])

# 4. Connect
diagram.connect(box1, box2, label="data flow")

# 5. Save
diagram.save("output.excalidraw")
```

### Complex Flow (Home Furniture Example)
See `examples/home_furniture_flow.py` for:
- Multiple phases with colors
- Numbered step circles
- GitLab links
- Info boxes
- 56 elements

## 📚 Further Reading

- **README.md** → Full feature documentation
- **QUICKSTART.md** → Getting started guide
- **examples/** → Working examples
- **Excalidraw Docs** → https://docs.excalidraw.com

## 🤔 Common Questions

**Q: Can I modify elements after adding to diagram?**
A: No, elements are effectively immutable. Create new ones instead.

**Q: How do I position elements?**
A: Use `Position(x, y, width, height)`. Helper methods like `center()`, `right_center()` are available.

**Q: What if I want custom colors?**
A: Use hex codes directly:
```python
BoxStyle(stroke_color="#ff0000", background_color="#ffcccc")
```

**Q: Can I load existing Excalidraw files?**
A: Not yet. This is a write-only library for now.

**Q: How do I test if my JSON is valid?**
A: Upload to excalidraw.com or use:
```bash
python3 -m json.tool output.excalidraw
```

---

**Need help?** Check README.md or the examples/ folder.
