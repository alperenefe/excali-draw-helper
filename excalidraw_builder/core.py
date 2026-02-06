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
    
    def _detect_existing_arrows(self, from_id: str, to_id: str, bidirectional: bool) -> tuple:
        """Detect existing arrows between elements."""
        existing_same = None
        existing_opposite = None
        
        for elem in self.elements:
            if isinstance(elem, Arrow):
                if elem.start_binding == from_id and elem.end_binding == to_id:
                    existing_same = elem
                elif elem.start_binding == to_id and elem.end_binding == from_id:
                    existing_opposite = elem
        
        existing_for_offset = None
        if bidirectional and existing_opposite:
            existing_for_offset = existing_opposite
        elif existing_same:
            existing_for_offset = existing_same
        
        return existing_for_offset, existing_opposite, existing_same
    
    def _calculate_arrow_direction(self, from_element, to_element) -> dict:
        """Calculate arrow direction."""
        if isinstance(from_element, (Box, Circle)):
            from_center = from_element.pos.center()
        else:
            from_center = (from_element.pos.x, from_element.pos.y)
        
        if isinstance(to_element, (Box, Circle)):
            to_center = to_element.pos.center()
        else:
            to_center = (to_element.pos.x, to_element.pos.y)
        
        dx = to_center[0] - from_center[0]
        dy = to_center[1] - from_center[1]
        
        return {
            'from_center': from_center,
            'to_center': to_center,
            'dx': dx,
            'dy': dy
        }
    
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
        existing_arrow, existing_arrow_opposite, existing_arrow_same = self._detect_existing_arrows(
            from_id, to_id, bidirectional
        )
        
        # STEP 2: Calculate direction
        direction = self._calculate_arrow_direction(from_element, to_element)
        
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
        
        # Multiple arrows offset logic (bidirectional OR same-direction multiple)
        if existing_arrow:
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
                base_offset = avg_width * 0.35  # 35% of box width
            
            # Scale based on distance (closer = more offset)
            if distance < 150:
                offset = base_offset * 1.5  # Very close: 50% more
            elif distance < 300:
                offset = base_offset * 1.2  # Medium: 20% more
            else:
                offset = base_offset  # Far: base offset
            
            # For same-direction multiple arrows (not bidirectional), use full offset for clarity
            if not bidirectional and existing_arrow_same:
                offset = offset * 1.0  # 100% of bidirectional offset (clear separation)
            
            # ADAPTIVE OFFSET: If label doesn't fit on arrow, increase offset
            if label:
                # Calculate label width (approximate)
                label_width = len(label) * 8 + 20  # 8px per char + padding
                
                # Calculate arrow length
                arrow_length = ((to_center[0] - from_center[0]) ** 2 + (to_center[1] - from_center[1]) ** 2) ** 0.5
                
                # If label doesn't fit on arrow (label > 80% of arrow length)
                if label_width > arrow_length * 0.8:
                    # Increase offset so arrows are further apart, giving label more space
                    label_excess_ratio = label_width / arrow_length
                    offset = offset * max(1.5, label_excess_ratio)  # At least 1.5x, scales with label size
            
            # CRITICAL: Update the existing arrow with NEGATIVE offset ONLY for bidirectional
            # For same-direction multiple arrows, we don't update the existing arrow
            if bidirectional and existing_arrow_opposite:
                # Bidirectional: Update the opposite-direction arrow with NEGATIVE offset
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
        
        # Calculate label offset based on arrow offset
        # Label simply follows the arrow with a fixed ratio
        label_offset = (0, 0)
        if offset > 0:
            # Label offset is 80% of arrow offset (follows arrow movement)
            if is_horizontal:
                # Horizontal arrows: labels offset vertically
                label_offset = (0, offset * 0.8)
            else:
                # Vertical arrows: labels offset vertically
                label_offset = (0, offset * 0.8)
        
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
        
        Args:
            verbose: If True, prints warnings for overlaps
            
        Returns:
            List of collision dicts with keys: 'box1', 'box2', 'overlap_area'
        """
        bounding_boxes = [elem for elem in self.elements if isinstance(elem, BoundingBox)]
        collisions = []
        
        for i, box1 in enumerate(bounding_boxes):
            for box2 in bounding_boxes[i+1:]:
                # Calculate overlap
                x1_min = box1.pos.x
                x1_max = box1.pos.x + box1.pos.width
                y1_min = box1.pos.y
                y1_max = box1.pos.y + box1.pos.height
                
                x2_min = box2.pos.x
                x2_max = box2.pos.x + box2.pos.width
                y2_min = box2.pos.y
                y2_max = box2.pos.y + box2.pos.height
                
                # Check for overlap
                x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
                y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
                
                if x_overlap > 0 and y_overlap > 0:
                    overlap_area = x_overlap * y_overlap
                    collision = {
                        'box1': box1,
                        'box2': box2,
                        'overlap_area': overlap_area,
                        'overlap_dims': (x_overlap, y_overlap)
                    }
                    collisions.append(collision)
                    
                    if verbose:
                        box1_title = box1.title or f"BoundingBox@({box1.pos.x:.0f}, {box1.pos.y:.0f})"
                        box2_title = box2.title or f"BoundingBox@({box2.pos.x:.0f}, {box2.pos.y:.0f})"
                        print(f"⚠️  BOUNDING BOX OVERLAP DETECTED:")
                        print(f"   Box 1: {box1_title}")
                        print(f"   Box 2: {box2_title}")
                        print(f"   Overlap: {x_overlap:.0f}x{y_overlap:.0f}px (area: {overlap_area:.0f}px²)")
                        
                        # Suggest fix
                        suggested_offset = y1_max - y2_min + 100  # 100px margin
                        if y2_min < y1_max:  # Box 2 needs to move down
                            print(f"   💡 Suggestion: Move Box 2 down by {suggested_offset:.0f}px")
                        print()
        
        if verbose and len(collisions) == 0:
            print("✅ No bounding box overlaps detected!")
        
        return collisions
    
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
