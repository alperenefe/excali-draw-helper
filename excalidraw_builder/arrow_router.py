"""
Arrow routing and positioning logic.
Handles arrow placement, multi-arrow offset, and label positioning.
"""

from typing import Tuple, Optional
from .elements import Element, Box, Circle, Arrow


class ArrowRouter:
    """Handles arrow routing, offset calculations, and positioning."""
    
    @staticmethod
    def detect_existing_arrows(elements: list, from_id: str, to_id: str, bidirectional: bool) -> dict:
        """
        Detect existing arrows between two elements.
        
        Returns:
            dict with keys: 'same_direction', 'opposite_direction', 'for_offset'
        """
        existing_same = None
        existing_opposite = None
        
        for elem in elements:
            if isinstance(elem, Arrow):
                if elem.start_binding == from_id and elem.end_binding == to_id:
                    existing_same = elem
                elif elem.start_binding == to_id and elem.end_binding == from_id:
                    existing_opposite = elem
        
        # Determine which arrow to use for offset
        existing_for_offset = None
        if bidirectional and existing_opposite:
            existing_for_offset = existing_opposite
        elif existing_same:
            existing_for_offset = existing_same
        
        return {
            'same_direction': existing_same,
            'opposite_direction': existing_opposite,
            'for_offset': existing_for_offset
        }
    
    @staticmethod
    def calculate_direction(from_element: Element, to_element: Element) -> dict:
        """
        Calculate arrow direction and geometry.
        
        Returns:
            dict with: from_center, to_center, dx, dy, is_horizontal, distance
        """
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
        is_horizontal = abs(dx) > abs(dy)
        distance = max(abs(dx), abs(dy))
        
        return {
            'from_center': from_center,
            'to_center': to_center,
            'dx': dx,
            'dy': dy,
            'is_horizontal': is_horizontal,
            'distance': distance
        }
    
    @staticmethod
    def calculate_base_offset(from_element: Element, to_element: Element, 
                            direction: dict, existing_arrow: Optional[Arrow]) -> float:
        """
        Calculate base offset for multiple arrows.
        
        Returns:
            offset value in pixels
        """
        if not existing_arrow:
            return 0.0
        
        # Get box dimensions
        from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
        from_width = from_element.pos.width if isinstance(from_element, (Box, Circle)) else 100
        to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
        to_width = to_element.pos.width if isinstance(to_element, (Box, Circle)) else 100
        
        # Calculate base offset proportional to box size
        if direction['is_horizontal']:
            avg_height = (from_height + to_height) / 2
            base_offset = avg_height * 0.35
        else:
            avg_width = (from_width + to_width) / 2
            base_offset = avg_width * 0.35
        
        # Scale based on distance
        distance = direction['distance']
        if distance < 150:
            offset = base_offset * 1.5
        elif distance < 300:
            offset = base_offset * 1.2
        else:
            offset = base_offset
        
        return offset
    
    @staticmethod
    def apply_adaptive_offset(offset: float, label: str, direction: dict) -> float:
        """
        Apply adaptive offset based on label length vs arrow length.
        If label doesn't fit on arrow, increase offset.
        
        Returns:
            adjusted offset value
        """
        if not label or offset == 0:
            return offset
        
        # Calculate label width
        label_width = len(label) * 8 + 20
        
        # Calculate arrow length
        arrow_length = ((direction['dx']) ** 2 + (direction['dy']) ** 2) ** 0.5
        
        # If label doesn't fit (label > 80% of arrow length)
        if label_width > arrow_length * 0.8:
            label_excess_ratio = label_width / arrow_length
            offset = offset * max(1.5, label_excess_ratio)
        
        return offset
    
    @staticmethod
    def calculate_edge_positions(from_element: Element, to_element: Element, 
                                direction: dict) -> dict:
        """
        Calculate arrow start/end positions at box edges.
        
        Returns:
            dict with: start, end, start_fixed_point, end_fixed_point
        """
        if not (isinstance(from_element, Box) and isinstance(to_element, Box)):
            # Fallback for non-box elements
            return {
                'start': None,
                'end': None,
                'start_fixed_point': None,
                'end_fixed_point': None
            }
        
        from_center = direction['from_center']
        to_center = direction['to_center']
        dx = direction['dx']
        dy = direction['dy']
        is_horizontal = direction['is_horizontal']
        
        if is_horizontal:
            if dx > 0:
                # L→R: RIGHT edge → LEFT edge
                start = (from_element.pos.x + from_element.pos.width, from_center[1])
                end = (to_element.pos.x, to_center[1])
                start_fixed_point = [1.0, 0.5001]
                end_fixed_point = [0.0, 0.5001]
            else:
                # R→L: LEFT edge → RIGHT edge
                start = (from_element.pos.x, from_center[1])
                end = (to_element.pos.x + to_element.pos.width, to_center[1])
                start_fixed_point = [0.0, 0.5001]
                end_fixed_point = [1.0, 0.5001]
        else:
            if dy > 0:
                # T→B: BOTTOM edge → TOP edge
                start = (from_center[0], from_element.pos.y + from_element.pos.height)
                end = (to_center[0], to_element.pos.y)
                start_fixed_point = [0.5001, 1.0]
                end_fixed_point = [0.5001, 0.0]
            else:
                # B→T: TOP edge → BOTTOM edge
                start = (from_center[0], from_element.pos.y)
                end = (to_center[0], to_element.pos.y + to_element.pos.height)
                start_fixed_point = [0.5001, 0.0]
                end_fixed_point = [0.5001, 1.0]
        
        return {
            'start': start,
            'end': end,
            'start_fixed_point': start_fixed_point,
            'end_fixed_point': end_fixed_point
        }
    
    @staticmethod
    def apply_offset_to_arrow(positions: dict, offset: float, from_element: Element,
                             to_element: Element, direction: dict) -> dict:
        """
        Apply offset to arrow positions for multiple arrows.
        
        Returns:
            Updated positions dict
        """
        if offset == 0:
            return positions
        
        is_horizontal = direction['is_horizontal']
        from_center = direction['from_center']
        to_center = direction['to_center']
        
        # Get box dimensions
        from_height = from_element.pos.height if isinstance(from_element, (Box, Circle)) else 100
        from_width = from_element.pos.width if isinstance(from_element, (Box, Circle)) else 100
        to_height = to_element.pos.height if isinstance(to_element, (Box, Circle)) else 100
        to_width = to_element.pos.width if isinstance(to_element, (Box, Circle)) else 100
        
        if is_horizontal:
            # Horizontal: offset vertically
            y_offset_ratio_from = offset / from_height
            y_offset_ratio_to = offset / to_height
            
            positions['start'] = (positions['start'][0], from_center[1] + offset)
            positions['end'] = (positions['end'][0], to_center[1] + offset)
            positions['start_fixed_point'] = [positions['start_fixed_point'][0], 0.5 + y_offset_ratio_from]
            positions['end_fixed_point'] = [positions['end_fixed_point'][0], 0.5 + y_offset_ratio_to]
        else:
            # Vertical: offset horizontally
            x_offset_ratio_from = offset / from_width
            x_offset_ratio_to = offset / to_width
            
            positions['start'] = (from_center[0] + offset, positions['start'][1])
            positions['end'] = (to_center[0] + offset, positions['end'][1])
            positions['start_fixed_point'] = [0.5 + x_offset_ratio_from, positions['start_fixed_point'][1]]
            positions['end_fixed_point'] = [0.5 + x_offset_ratio_to, positions['end_fixed_point'][1]]
        
        return positions
    
    @staticmethod
    def calculate_label_offset(offset: float, direction: dict) -> Tuple[float, float]:
        """
        Calculate label offset based on arrow offset.
        Label follows arrow (80% of arrow offset).
        
        Returns:
            (x_offset, y_offset) tuple
        """
        if offset == 0:
            return (0, 0)
        
        is_horizontal = direction['is_horizontal']
        
        if is_horizontal:
            # Horizontal arrows: labels offset vertically
            return (0, offset * 0.8)
        else:
            # Vertical arrows: labels offset vertically
            return (0, offset * 0.8)
