"""
Layout engine for bounding boxes and spacing calculations.
"""

from typing import List, Tuple
from .elements import Element, Box, Arrow, BoundingBox, Position
from .styles import Color


class LayoutEngine:
    """Handles layout calculations, bounding boxes, and spacing."""
    
    @staticmethod
    def calculate_bounding_box_bounds(elements: List[Element], padding: float = 30) -> dict:
        """
        Calculate min/max bounds for a bounding box.
        
        Args:
            elements: List of elements to wrap
            padding: Padding around elements
            
        Returns:
            dict with: x, y, width, height
        """
        if not elements:
            raise ValueError("Cannot calculate bounds for empty element list")
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for elem in elements:
            if hasattr(elem, 'pos'):
                min_x = min(min_x, elem.pos.x)
                min_y = min(min_y, elem.pos.y)
                max_x = max(max_x, elem.pos.x + elem.pos.width)
                max_y = max(max_y, elem.pos.y + elem.pos.height)
            elif isinstance(elem, Arrow):
                min_x = min(min_x, elem.start[0], elem.end[0])
                min_y = min(min_y, elem.start[1], elem.end[1])
                max_x = max(max_x, elem.start[0], elem.end[0])
                max_y = max(max_y, elem.start[1], elem.end[1])
        
        bbox_x = min_x - padding
        bbox_y = min_y - padding
        bbox_width = (max_x - min_x) + (2 * padding)
        bbox_height = (max_y - min_y) + (2 * padding)
        
        return {
            'x': bbox_x,
            'y': bbox_y,
            'width': bbox_width,
            'height': bbox_height
        }
    
    @staticmethod
    def create_bounding_box_for_elements(elements: List[Element], title: str = "",
                                        padding: float = 30, stroke_style: str = "dashed",
                                        stroke_color: str = "#1e1e1e", 
                                        stroke_width: int = 2) -> BoundingBox:
        """
        Create an auto-sized bounding box around elements.
        
        Args:
            elements: Elements to wrap
            title: Optional title
            padding: Space around elements
            stroke_style: Border style
            stroke_color: Border color
            stroke_width: Border width
            
        Returns:
            BoundingBox element
        """
        bounds = LayoutEngine.calculate_bounding_box_bounds(elements, padding)
        
        from .styles import BoxStyle
        bbox = BoundingBox(
            pos=Position(x=bounds['x'], y=bounds['y'], 
                        width=bounds['width'], height=bounds['height']),
            title=title,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            stroke_style=stroke_style,
        )
        
        return bbox
    
    @staticmethod
    def detect_bounding_box_overlaps(elements: List[Element], verbose: bool = True) -> List[dict]:
        """
        Detect overlapping bounding boxes.
        
        Args:
            elements: All diagram elements
            verbose: Print warnings
            
        Returns:
            List of collision dicts
        """
        bounding_boxes = [elem for elem in elements if isinstance(elem, BoundingBox)]
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
                        suggested_offset = y1_max - y2_min + 100
                        if y2_min < y1_max:
                            print(f"   💡 Suggestion: Move Box 2 down by {suggested_offset:.0f}px")
                        print()
        
        if verbose and len(collisions) == 0:
            print("✅ No bounding box overlaps detected!")
        
        return collisions
