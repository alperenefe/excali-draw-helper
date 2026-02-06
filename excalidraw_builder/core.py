"""
Core Excalidraw diagram builder.
"""

import json
from typing import List, Optional, Union
from pathlib import Path

from .elements import Element, Box, Arrow, Text, Circle, BoundingBox
from .arrow_router import ArrowRouter
from .layout_engine import LayoutEngine


class ExcalidrawDiagram:
    """Main diagram builder class."""
    
    def __init__(self, title: str = "Untitled Diagram"):
        self.title = title
        self.elements: List[Element] = []
        self.element_map = {}  # id -> element mapping for quick lookup
    
    def add(self, element: Union[Element, List[Element]]) -> "ExcalidrawDiagram":
        """Add element(s) to the diagram."""
        if isinstance(element, list):
            for elem in element:
                self._add_single(elem)
        else:
            self._add_single(element)
        return self
    
    def _add_single(self, element: Element) -> None:
        """Add a single element."""
        self.elements.append(element)
        self.element_map[element.id] = element
    
    def add_to_back(self, element: Union[Element, List[Element]]) -> "ExcalidrawDiagram":
        """Add element(s) to the BACK (beginning) of the diagram.
        
        Useful for bounding boxes that should stay in the background.
        """
        if isinstance(element, list):
            for elem in reversed(element):  # Reverse to maintain order
                self._add_to_back_single(elem)
        else:
            self._add_to_back_single(element)
        return self
    
    def _add_to_back_single(self, element: Element) -> None:
        """Add a single element to the back."""
        self.elements.insert(0, element)  # Insert at beginning
        self.element_map[element.id] = element
    
    def get_element(self, element_id: str) -> Optional[Element]:
        """Get element by ID."""
        return self.element_map.get(element_id)
    
    def create_bounding_box_for_elements(
        self,
        elements: List[Element],
        title: str = "",
        padding: float = 30,
        stroke_style: str = "dashed",
        stroke_color: str = "#1e1e1e",
        stroke_width: int = 2,
    ) -> "BoundingBox":
        """Create a bounding box that wraps given elements with padding.
        
        Uses LayoutEngine for calculation.
        """
        return LayoutEngine.create_bounding_box_for_elements(
            elements, title, padding, stroke_style, stroke_color, stroke_width
        )
    
    def connect(
        self,
        from_elem: Union[str, Element],
        to_elem: Union[str, Element],
        label: str = "",
        style: Optional["ArrowStyle"] = None,
        bidirectional: bool = False,
    ) -> Arrow:
        """Create an arrow connecting two elements with optional bidirectional offset.
        
        PIPELINE:
        1. Detect existing arrows
        2. Calculate direction
        3. Calculate base offset
        4. Apply adaptive offset (label-based)
        5. Calculate arrow positions
        6. Calculate label offset
        7. Create and add arrow
        """
        from .styles import ArrowStyle
        
        # Get element IDs
        from_id = from_elem if isinstance(from_elem, str) else from_elem.id
        to_id = to_elem if isinstance(to_elem, str) else to_elem.id
        
        # Get elements
        from_element = self.get_element(from_id)
        to_element = self.get_element(to_id)
        
        if not from_element or not to_element:
            raise ValueError("Both elements must exist in the diagram")
        
        # STEP 1: Detect existing arrows
        arrows_info = ArrowRouter.detect_existing_arrows(self.elements, from_id, to_id, bidirectional)
        existing_arrow = arrows_info['for_offset']
        existing_arrow_opposite = arrows_info['opposite_direction']
        existing_arrow_same = arrows_info['same_direction']
        
        # STEP 2: Calculate direction
        direction = ArrowRouter.calculate_direction(from_element, to_element)
        
        # STEP 3: Calculate edge positions
        positions = ArrowRouter.calculate_edge_positions(from_element, to_element, direction)
        
        # STEP 4: Calculate base offset (if multiple arrows exist)
        offset = ArrowRouter.calculate_base_offset(from_element, to_element, direction, existing_arrow)
        
        # For same-direction multiple arrows (not bidirectional), use full offset for clarity
        if not bidirectional and existing_arrow_same:
            offset = offset * 1.0
        
        # STEP 5: Apply adaptive offset (label-based)
        offset = ArrowRouter.apply_adaptive_offset(offset, label, direction)
        
        # STEP 6: Update existing arrow if bidirectional
        if bidirectional and existing_arrow_opposite:
            ArrowRouter.update_existing_arrow_offset(existing_arrow, from_element, to_element, offset)
        
        # STEP 7: Apply offset to arrow positions
        positions = ArrowRouter.apply_offset_to_arrow(positions, offset, from_element, to_element, direction)
        
        # STEP 8: Calculate label offset
        label_offset = ArrowRouter.calculate_label_offset(offset, direction)
        
        # Handle None positions (fallback for non-Box elements)
        if positions['start'] is None or positions['end'] is None:
            from_center = direction['from_center']
            to_center = direction['to_center']
            is_horizontal = direction['is_horizontal']
            
            if is_horizontal:
                positions['start'] = (from_center[0] + (from_element.pos.width / 2 if isinstance(from_element, (Box, Circle)) else 0), 
                        from_center[1])
                positions['end'] = (to_center[0] - (to_element.pos.width / 2 if isinstance(to_element, (Box, Circle)) else 0), 
                      to_center[1])
            else:
                positions['start'] = (from_center[0], 
                        from_center[1] + (from_element.pos.height / 2 if isinstance(from_element, (Box, Circle)) else 0))
                positions['end'] = (to_center[0], 
                      to_center[1] - (to_element.pos.height / 2 if isinstance(to_element, (Box, Circle)) else 0))
        
        # STEP 9: Create arrow
        arrow = Arrow(
            start=positions['start'],
            end=positions['end'],
            style=style or ArrowStyle.default(),
            label=label,
            start_binding=from_id,
            end_binding=to_id,
            start_fixed_point=positions['start_fixed_point'],
            end_fixed_point=positions['end_fixed_point'],
            label_offset=label_offset,
        )
        
        # Add arrow to diagram
        self.add(arrow)
        
        # CRITICAL: Add arrow to boundElements of connected boxes
        # This makes boxes move together with arrows
        if hasattr(from_element, 'bound_elements'):
            from_element.bound_elements.append({"id": arrow.id, "type": "arrow"})
        if hasattr(to_element, 'bound_elements'):
            to_element.bound_elements.append({"id": arrow.id, "type": "arrow"})
        
        return arrow
    
    def to_json(self, indent: int = 2, clipboard_format: bool = False) -> str:
        """Convert diagram to Excalidraw JSON format.
        
        Args:
            indent: JSON indentation level
            clipboard_format: If True, uses "excalidraw/clipboard" format (for copy-paste)
                            If False, uses "excalidraw" format (for file save)
        """
        # Separate bounding boxes from other elements for proper z-ordering
        bounding_boxes = []
        other_elements = []
        
        for element in self.elements:
            if isinstance(element, BoundingBox):
                bounding_boxes.append(element)
            else:
                other_elements.append(element)
        
        # Render bounding boxes FIRST (so they appear in background)
        # Then render all other elements (they will appear on top)
        elements = []
        
        # First: Add all bounding boxes and their titles (with lower index for z-order)
        for element in bounding_boxes:
            bbox_dict = element.to_dict()
            bbox_dict["index"] = "a0"  # Lower index = background
            elements.append(bbox_dict)
            title_elem = element.get_title_element()
            if title_elem:
                title_elem["index"] = "a0"
                elements.append(title_elem)
        
        # Then: Add all other elements (with higher index for z-order)
        for element in other_elements:
            # Add main element
            elem_dict = element.to_dict()
            elem_dict["index"] = "a1"  # Higher index = foreground
            elements.append(elem_dict)
            
            # Add associated text/title elements
            if isinstance(element, (Box, Circle)):
                text_elem = element.get_text_element()
                if text_elem:
                    text_elem["index"] = "a1"
                    elements.append(text_elem)
            elif isinstance(element, Arrow):
                label_elem = element.get_label_element()
                if label_elem:
                    label_elem["index"] = "a1"
                    elements.append(label_elem)
        
        if clipboard_format:
            # Clipboard format (for copy-paste in Excalidraw)
            diagram_data = {
                "type": "excalidraw/clipboard",
                "elements": elements,
                "files": {}
            }
        else:
            # File format (for saving .excalidraw files)
            diagram_data = {
                "type": "excalidraw",
                "version": 2,
                "source": "https://excalidraw.com",
                "elements": elements,
                "appState": {
                    "gridSize": None,
                    "viewBackgroundColor": "#ffffff"
                },
                "files": {}
            }
        
        return json.dumps(diagram_data, indent=indent, ensure_ascii=False)
    
    def validate_bounding_box_overlaps(self, verbose: bool = True) -> List[dict]:
        """Detect overlapping bounding boxes and return collision info.
        
        Uses LayoutEngine for overlap detection.
        """
        return LayoutEngine.detect_bounding_box_overlaps(self.elements, verbose)
    
    def save(self, filepath: Union[str, Path], indent: int = 2, clipboard_format: bool = False) -> None:
        """Save diagram to file.
        
        Args:
            filepath: Path to save file
            indent: JSON indentation
            clipboard_format: If True, saves in clipboard format (excalidraw/clipboard)
        """
        filepath = Path(filepath)
        
        # Ensure .excalidraw or .json extension
        if filepath.suffix not in ['.excalidraw', '.json']:
            filepath = filepath.with_suffix('.excalidraw')
        
        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent=indent, clipboard_format=clipboard_format))
        
        format_type = "clipboard" if clipboard_format else "file"
        print(f"✅ Diagram saved to: {filepath} ({format_type} format)")
    
    def __repr__(self) -> str:
        return f"ExcalidrawDiagram(title='{self.title}', elements={len(self.elements)})"
