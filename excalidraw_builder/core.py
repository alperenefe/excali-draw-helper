"""
Core Excalidraw diagram builder.
"""

import json
from typing import List, Optional, Union
from pathlib import Path

from .elements import Element, Box, Arrow, Text, Circle, BoundingBox


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
        
        Args:
            elements: List of elements to wrap
            title: Title for the bounding box
            padding: Space around elements (default: 30)
            stroke_style: "solid", "dashed", or "dotted"
            stroke_color: Border color
            stroke_width: Border width
            
        Returns:
            BoundingBox that wraps all elements
        """
        if not elements:
            raise ValueError("Cannot create bounding box for empty element list")
        
        # Find bounds of all elements
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for elem in elements:
            if hasattr(elem, 'pos'):
                # Box, Circle, BoundingBox, etc
                min_x = min(min_x, elem.pos.x)
                min_y = min(min_y, elem.pos.y)
                max_x = max(max_x, elem.pos.x + elem.pos.width)
                max_y = max(max_y, elem.pos.y + elem.pos.height)
            elif isinstance(elem, Arrow):
                # Arrow - consider start and end points
                min_x = min(min_x, elem.start[0], elem.end[0])
                min_y = min(min_y, elem.start[1], elem.end[1])
                max_x = max(max_x, elem.start[0], elem.end[0])
                max_y = max(max_y, elem.start[1], elem.end[1])
        
        # Add padding
        bbox_x = min_x - padding
        bbox_y = min_y - padding
        bbox_width = (max_x - min_x) + (2 * padding)
        bbox_height = (max_y - min_y) + (2 * padding)
        
        # Create bounding box
        from .elements import Position
        bbox = BoundingBox(
            pos=Position(x=bbox_x, y=bbox_y, width=bbox_width, height=bbox_height),
            title=title,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            stroke_style=stroke_style,
        )
        
        return bbox
    
    def _update_existing_arrow_offset(self, arrow, from_element, to_element, offset):
        """Update existing arrow with negative offset (first arrow = top/left per reading direction)."""
        # Get centers
        from_center = from_element.pos.center() if isinstance(from_element, (Box, Circle)) else (from_element.pos.x, from_element.pos.y)
        to_center = to_element.pos.center() if isinstance(to_element, (Box, Circle)) else (to_element.pos.x, to_element.pos.y)
        
        # Calculate direction
        dx = to_center[0] - from_center[0]
        dy = to_center[1] - from_center[1]
        
        # Apply NEGATIVE offset (first arrow = top/left, follows reading direction)
        actual_offset = -offset  # NEGATIVE for first arrow (top or left)
        
        # Determine layout and update arrow
        if abs(dx) > abs(dy):
            # Horizontal layout: offset vertically
            from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
            to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
            from_width = from_element.pos.width if isinstance(from_element, (Box, Circle)) else 100
            to_width = to_element.pos.width if isinstance(to_element, (Box, Circle)) else 100
            
            y_offset_ratio_from = actual_offset / from_height
            y_offset_ratio_to = actual_offset / to_height
            
            # Update arrow coordinates and fixed points
            arrow.start = (from_center[0] + from_width / 2, from_center[1] + actual_offset)
            arrow.end = (to_center[0] - to_width / 2, to_center[1] + actual_offset)
            arrow.start_fixed_point = [1.0, 0.5 + y_offset_ratio_from]
            arrow.end_fixed_point = [0.0, 0.5 + y_offset_ratio_to]
        else:
            # Vertical layout: offset horizontally
            from_width = from_element.pos.width if isinstance(from_element, (Box, Circle)) else 100
            to_width = to_element.pos.width if isinstance(to_element, (Box, Circle)) else 100
            from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
            to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
            
            x_offset_ratio_from = actual_offset / from_width
            x_offset_ratio_to = actual_offset / to_width
            
            # Update arrow coordinates and fixed points
            arrow.start = (from_center[0] + actual_offset, from_center[1] + from_height / 2)
            arrow.end = (to_center[0] + actual_offset, to_center[1] - to_height / 2)
            arrow.start_fixed_point = [0.5 + x_offset_ratio_from, 1.0]
            arrow.end_fixed_point = [0.5 + x_offset_ratio_to, 0.0]
    
    def connect(
        self,
        from_elem: Union[str, Element],
        to_elem: Union[str, Element],
        label: str = "",
        style: Optional["ArrowStyle"] = None,
        bidirectional: bool = False,
    ) -> Arrow:
        """Create an arrow connecting two elements with optional bidirectional offset.
        
        Args:
            bidirectional: If True, automatically offsets second arrow between same boxes
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
        
        # Check for bidirectional arrows ONLY if explicitly requested
        existing_arrow = None
        if bidirectional:
            for elem in self.elements:
                if isinstance(elem, Arrow):
                    # Match arrows in SAME direction (from→to) or OPPOSITE direction (to→from)
                    if ((elem.start_binding == from_id and elem.end_binding == to_id) or
                        (elem.start_binding == to_id and elem.end_binding == from_id)):
                        existing_arrow = elem
                        break
        
        # Get base positions
        if isinstance(from_element, (Box, Circle)):
            from_center = from_element.pos.center()
        else:
            from_center = (from_element.pos.x, from_element.pos.y)
        
        if isinstance(to_element, (Box, Circle)):
            to_center = to_element.pos.center()
        else:
            to_center = (to_element.pos.x, to_element.pos.y)
        
        # Calculate direction
        dx = to_center[0] - from_center[0]
        dy = to_center[1] - from_center[1]
        
        # Determine if arrow is primarily horizontal or vertical
        is_horizontal = abs(dx) > abs(dy)
        
        # Initialize
        offset = 0
        start_fixed_point = None
        end_fixed_point = None
        start = None
        end = None
        
        # Simple Box-to-Box logic: use edge coordinates based on direction
        if isinstance(from_element, Box) and isinstance(to_element, Box):
            if is_horizontal:
                # Horizontal arrow: check if going left-to-right or right-to-left
                if dx > 0:
                    # L→R: start from RIGHT edge, end at LEFT edge
                    start = (from_element.pos.x + from_element.pos.width, from_center[1])
                    end = (to_element.pos.x, to_center[1])
                    start_fixed_point = [1.0, 0.5001]
                    end_fixed_point = [0.0, 0.5001]
                else:
                    # R→L: start from LEFT edge, end at RIGHT edge
                    start = (from_element.pos.x, from_center[1])
                    end = (to_element.pos.x + to_element.pos.width, to_center[1])
                    start_fixed_point = [0.0, 0.5001]
                    end_fixed_point = [1.0, 0.5001]
            else:
                # Vertical arrow: check if going top-to-bottom or bottom-to-top
                if dy > 0:
                    # T→B: start from BOTTOM edge, end at TOP edge
                    start = (from_center[0], from_element.pos.y + from_element.pos.height)
                    end = (to_center[0], to_element.pos.y)
                    start_fixed_point = [0.5001, 1.0]
                    end_fixed_point = [0.5001, 0.0]
                else:
                    # B→T: start from TOP edge, end at BOTTOM edge
                    start = (from_center[0], from_element.pos.y)
                    end = (to_center[0], to_element.pos.y + to_element.pos.height)
                    start_fixed_point = [0.5001, 0.0]
                    end_fixed_point = [0.5001, 1.0]
        
        # Bidirectional offset logic (if enabled)
        if existing_arrow and bidirectional:
            # Calculate box dimensions
            from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
            from_width = from_element.pos.width if isinstance(from_element, (Box, Circle)) else 100
            to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
            to_width = to_element.pos.width if isinstance(to_element, (Box, Circle)) else 100
            
            # Calculate distance between boxes
            distance = max(abs(dx), abs(dy))
            
            # Dynamic offset proportional to box size
            # Horizontal layout → use height for offset
            # Vertical layout → use width for offset
            if abs(dx) > abs(dy):
                # Horizontal: offset vertically
                avg_height = (from_height + to_height) / 2
                base_offset = avg_height * 0.35  # 35% of box height
            else:
                # Vertical: offset horizontally
                avg_width = (from_width + to_width) / 2
                base_offset = avg_width * 0.35  # 35% of box width (increased from 25%)
            
            # Scale based on distance (closer = more offset)
            if distance < 150:
                offset = base_offset * 1.5  # Very close: 50% more
            elif distance < 300:
                offset = base_offset * 1.2  # Medium: 20% more
            else:
                offset = base_offset  # Far: base offset
            
            # CRITICAL: Update the existing arrow with NEGATIVE offset (top/left per reading direction)!
            # This ensures both arrows are separated: first=top/left (-offset), second=bottom/right (+offset)
            self._update_existing_arrow_offset(existing_arrow, from_element, to_element, offset)
            
            # Boxes are horizontal (side by side) → offset vertically
            if abs(dx) > abs(dy):
                # Calculate relative vertical offset (0-1 range)
                from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
                to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
                
                # CRITICAL: Second arrow should use POSITIVE offset (bottom per reading direction)!
                # First arrow goes top (-offset), second arrow goes bottom (+offset)
                actual_offset = offset  # POSITIVE for second bidirectional arrow (bottom)
                
                y_offset_ratio_from = actual_offset / from_height
                y_offset_ratio_to = actual_offset / to_height
                
                # Fixed points: right EDGE with vertical offset
                start_fixed_point = [1.0, 0.5 + y_offset_ratio_from]
                end_fixed_point = [0.0, 0.5 + y_offset_ratio_to]
                
                # CRITICAL: Use EDGE coordinates + vertical offset (not center!)
                # Start from RIGHT EDGE of from_box, end at LEFT EDGE of to_box
                start = (from_element.pos.x + from_element.pos.width, from_center[1] + actual_offset)
                end = (to_element.pos.x, to_center[1] + actual_offset)
                
            # Boxes are vertical (top-bottom) → offset horizontally
            else:
                # Calculate relative horizontal offset (0-1 range)
                from_width = from_element.pos.width if isinstance(from_element, (Box, Circle)) else 100
                to_width = to_element.pos.width if isinstance(to_element, (Box, Circle)) else 100
                
                # CRITICAL: Second arrow should use POSITIVE offset (right per reading direction)!
                # First arrow goes left (-offset), second arrow goes right (+offset)
                actual_offset = offset  # POSITIVE for second bidirectional arrow (right)
                
                x_offset_ratio_from = actual_offset / from_width
                x_offset_ratio_to = actual_offset / to_width
                
                # Fixed points: bottom of from_box, top of to_box, with horizontal offset
                start_fixed_point = [0.5 + x_offset_ratio_from, 1.0]
                end_fixed_point = [0.5 + x_offset_ratio_to, 0.0]
                
                # CRITICAL: Also offset the actual arrow coordinates!
                # This ensures arrow line itself is offset, not just the binding point
                from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
                to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
                
                start = (from_center[0] + actual_offset, from_center[1] + from_height / 2)
                end = (to_center[0] + actual_offset, to_center[1] - to_height / 2)
        
        # Fallback for non-Box elements
        if start is None or end is None:
            if is_horizontal:
                start = (from_center[0] + (from_element.pos.width / 2 if isinstance(from_element, (Box, Circle)) else 0), 
                        from_center[1])
                end = (to_center[0] - (to_element.pos.width / 2 if isinstance(to_element, (Box, Circle)) else 0), 
                      to_center[1])
            else:
                start = (from_center[0], 
                        from_center[1] + (from_element.pos.height / 2 if isinstance(from_element, (Box, Circle)) else 0))
                end = (to_center[0], 
                      to_center[1] - (to_element.pos.height / 2 if isinstance(to_element, (Box, Circle)) else 0))
        
        # Create arrow
        arrow = Arrow(
            start=start,
            end=end,
            style=style or ArrowStyle.default(),
            label=label,
            start_binding=from_id,
            end_binding=to_id,
            start_fixed_point=start_fixed_point,
            end_fixed_point=end_fixed_point,
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
        elements = []
        
        for element in self.elements:
            # Add main element
            elements.append(element.to_dict())
            
            # Add associated text/title elements
            if isinstance(element, (Box, Circle)):
                text_elem = element.get_text_element()
                if text_elem:
                    elements.append(text_elem)
            elif isinstance(element, BoundingBox):
                title_elem = element.get_title_element()
                if title_elem:
                    elements.append(title_elem)
            elif isinstance(element, Arrow):
                label_elem = element.get_label_element()
                if label_elem:
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
