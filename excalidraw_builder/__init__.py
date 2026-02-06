"""
Excalidraw Diagram Builder
A tool to programmatically create Excalidraw diagrams with reusable components.
"""

from .core import ExcalidrawDiagram
from .elements import Box, Arrow, Text, Circle, BoundingBox, Position
from .styles import Color, BoxStyle, ArrowStyle
from .component_registry import ComponentRegistry, ComponentColors, DEFAULT_REGISTRY

__version__ = "1.0.0"
__all__ = [
    "ExcalidrawDiagram",
    "Box",
    "Arrow",
    "Text",
    "Circle",
    "BoundingBox",
    "Position",
    "Color",
    "BoxStyle",
    "ArrowStyle",
    "ComponentRegistry",
    "ComponentColors",
    "DEFAULT_REGISTRY",
]
