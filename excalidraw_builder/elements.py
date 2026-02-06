"""
Excalidraw diagram elements (Box, Arrow, Text, Circle, etc).
"""

import random
import time
import string
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

from .styles import BoxStyle, ArrowStyle, Color


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID for elements (Excalidraw format)."""
    # Excalidraw uses random alphanumeric strings like "TeKan1wgKFAYcZeYSjzaP"
    chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(chars, k=21))
    return f"{prefix}{random_id}" if prefix else random_id


def generate_seed() -> int:
    """Generate a random seed for element rendering."""
    return random.randint(1, 2147483647)


@dataclass
class Position:
    """Position and size for elements."""
    x: float
    y: float
    width: float = 0
    height: float = 0
    
    def center(self) -> Tuple[float, float]:
        """Get center point of the element."""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def top_center(self) -> Tuple[float, float]:
        """Get top center point."""
        return (self.x + self.width / 2, self.y)
    
    def bottom_center(self) -> Tuple[float, float]:
        """Get bottom center point."""
        return (self.x + self.width / 2, self.y + self.height)
    
    def left_center(self) -> Tuple[float, float]:
        """Get left center point."""
        return (self.x, self.y + self.height / 2)
    
    def right_center(self) -> Tuple[float, float]:
        """Get right center point."""
        return (self.x + self.width, self.y + self.height / 2)
    
    # ========== RELATIVE POSITIONING ==========
    
    def below(self, spacing: float = 50, align: str = "left") -> "Position":
        """Create a new position below this one.
        
        Args:
            spacing: Vertical space between elements
            align: "left", "center", or "right" alignment
        """
        new_y = self.y + self.height + spacing
        
        if align == "left":
            new_x = self.x
        elif align == "center":
            new_x = self.x + (self.width - self.width) / 2  # Same width assumed
        elif align == "right":
            new_x = self.x + self.width - self.width  # Right-aligned
        else:
            new_x = self.x
        
        return Position(x=new_x, y=new_y, width=self.width, height=self.height)
    
    def above(self, spacing: float = 50, align: str = "left") -> "Position":
        """Create a new position above this one."""
        new_y = self.y - self.height - spacing
        
        if align == "left":
            new_x = self.x
        elif align == "center":
            new_x = self.x + (self.width - self.width) / 2
        elif align == "right":
            new_x = self.x + self.width - self.width
        else:
            new_x = self.x
        
        return Position(x=new_x, y=new_y, width=self.width, height=self.height)
    
    def right_of(self, spacing: float = 50, align: str = "top") -> "Position":
        """Create a new position to the right of this one.
        
        Args:
            spacing: Horizontal space between elements
            align: "top", "center", or "bottom" alignment
        """
        new_x = self.x + self.width + spacing
        
        if align == "top":
            new_y = self.y
        elif align == "center":
            new_y = self.y + (self.height - self.height) / 2
        elif align == "bottom":
            new_y = self.y + self.height - self.height
        else:
            new_y = self.y
        
        return Position(x=new_x, y=new_y, width=self.width, height=self.height)
    
    def left_of(self, spacing: float = 50, align: str = "top") -> "Position":
        """Create a new position to the left of this one."""
        new_x = self.x - self.width - spacing
        
        if align == "top":
            new_y = self.y
        elif align == "center":
            new_y = self.y + (self.height - self.height) / 2
        elif align == "bottom":
            new_y = self.y + self.height - self.height
        else:
            new_y = self.y
        
        return Position(x=new_x, y=new_y, width=self.width, height=self.height)
    
    def offset(self, dx: float = 0, dy: float = 0) -> "Position":
        """Create a new position with x/y offset."""
        return Position(
            x=self.x + dx,
            y=self.y + dy,
            width=self.width,
            height=self.height
        )
    
    @staticmethod
    def midpoint(start: Tuple[float, float], end: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate midpoint between two points."""
        return ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)


class Element:
    """Base class for all Excalidraw elements."""
    
    def __init__(self, element_id: Optional[str] = None):
        self.id = element_id or generate_id()
        self.version = 1
        self.version_nonce = generate_seed()
        self.is_deleted = False
        self.seed = generate_seed()
        self.group_ids: List[str] = []
        self.frame_id: Optional[str] = None
        self.updated = int(time.time() * 1000)
        self.link: Optional[str] = None
        self.locked = False
    
    def to_dict(self) -> dict:
        """Convert element to Excalidraw JSON format."""
        raise NotImplementedError


class Box(Element):
    """Rectangle/Box element."""
    
    @staticmethod
    def calculate_height(
        text: str,
        line_height: int = 19,
        padding: int = 40,
        min_height: int = 80
    ) -> int:
        """
        Calculate optimal box height based on text content.
        
        Formula: height = (lines × line_height) + padding
        
        Args:
            text: Box text content
            line_height: Height per line in pixels (default: 19)
            padding: Top + bottom padding (default: 40)
            min_height: Minimum height (default: 80)
        
        Returns:
            Calculated height in pixels
        
        Example:
            text = "Line 1\\nLine 2\\nLine 3"
            height = Box.calculate_height(text)
            box = Box(pos=Position(x=100, y=100, width=300, height=height), text=text)
        
        Note:
            Defaults (L=19, P=40) provide optimal text fit:
            - 3 lines: 97px
            - 10 lines: 230px
            - 20 lines: 420px
        """
        lines = text.count('\n') + 1
        calculated = lines * line_height + padding
        return max(calculated, min_height)
    
    @staticmethod
    def wrap_text(text: str, max_chars: int = 70) -> str:
        """
        Wrap text to fit within specified character width.
        Intelligently breaks at spaces, preserving existing line breaks.
        For long words with underscores, breaks at underscore boundaries.
        
        Args:
            text: Text to wrap
            max_chars: Maximum characters per line (default: 70)
            
        Returns:
            Wrapped text with \\n line breaks
            
        Example:
            >>> long_text = "scr_keep_prod_image_tag_indexing_incremental_core_scheduler"
            >>> wrapped = Box.wrap_text(long_text, max_chars=40)
            >>> print(wrapped)
            scr_keep_prod_image_tag_indexing
            _incremental_core_scheduler
        """
        # Preserve existing line breaks
        paragraphs = text.split('\n')
        wrapped_paragraphs = []
        
        for para in paragraphs:
            if not para.strip():
                wrapped_paragraphs.append(para)
                continue
                
            # Wrap this paragraph
            words = para.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= max_chars:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    # If single word is too long, try splitting at underscore
                    if len(word) > max_chars and '_' in word:
                        parts = word.split('_')
                        temp = ""
                        for part in parts:
                            test = temp + ("_" if temp else "") + part
                            if len(test) <= max_chars:
                                temp = test
                            else:
                                if temp:
                                    lines.append(temp)
                                temp = part
                        current_line = temp
                    else:
                        current_line = word
            
            if current_line:
                lines.append(current_line)
            
            wrapped_paragraphs.append('\n'.join(lines))
        
        return '\n'.join(wrapped_paragraphs)
    
    @staticmethod
    def calculate_width(text: str, char_width: int = 9, padding: int = 30, 
                       min_width: int = 200, max_width: int = 800) -> int:
        """
        Calculate optimal box width based on text content.
        Measures the longest line and calculates required width.
        
        Args:
            text: The text content (with \\n line breaks)
            char_width: Average character width in pixels (default: 9px)
            padding: Left + right padding (default: 30px total)
            min_width: Minimum width (default: 200px)
            max_width: Maximum width (default: 800px)
            
        Returns:
            Calculated width in pixels
            
        Example:
            >>> text = "Short text"
            >>> width = Box.calculate_width(text)  # ~120px
        """
        lines = text.split('\n')
        longest_line = max(len(line) for line in lines) if lines else 0
        calculated = longest_line * char_width + padding
        return max(min_width, min(calculated, max_width))
    
    @staticmethod
    def auto_size(text: str, max_chars: int = 70) -> tuple:
        """
        Automatically calculate both width and height for a box.
        Wraps text if needed and returns optimal dimensions.
        
        Args:
            text: The text content
            max_chars: Maximum characters per line (default: 70)
            
        Returns:
            Tuple of (width, height, wrapped_text)
            
        Example:
            >>> text = "My very long text here that needs proper wrapping and sizing"
            >>> width, height, wrapped = Box.auto_size(text, max_chars=70)
            >>> box = Box(
            ...     pos=Position(x=100, y=200, width=width, height=height),
            ...     text=wrapped
            ... )
        """
        wrapped = Box.wrap_text(text, max_chars)
        width = Box.calculate_width(wrapped)
        height = Box.calculate_height(wrapped)
        return width, height, wrapped
    
    def __init__(
        self,
        pos: Position,
        text: str = "",
        style: Optional[BoxStyle] = None,
        element_id: Optional[str] = None,
        auto_wrap: bool = True,
        max_chars: int = 70,
    ):
        super().__init__(element_id)
        
        # Auto-wrap text as safety (if any line exceeds max_chars)
        if auto_wrap and text:
            needs_wrap = any(len(line) > max_chars for line in text.split('\n'))
            if needs_wrap:
                text = Box.wrap_text(text, max_chars)
        
        # Auto-calculate width if not provided (width=0 means auto)
        if pos.width == 0 and text:
            pos.width = Box.calculate_width(text)
        
        # Auto-calculate height if not provided (height=0 means auto)
        if pos.height == 0 and text:
            pos.height = Box.calculate_height(text)
        
        self.pos = pos
        self.text = text
        self.style = style or BoxStyle.default()
        self.text_id = generate_id("text_") if text else None
        self.bound_elements: List[dict] = []
        
        if text:
            self.bound_elements.append({"id": self.text_id, "type": "text"})
    
    def to_dict(self) -> dict:
        """Convert box to Excalidraw JSON."""
        return {
            "id": self.id,
            "type": "rectangle",
            "x": self.pos.x,
            "y": self.pos.y,
            "width": self.pos.width,
            "height": self.pos.height,
            "angle": 0,
            "strokeColor": self.style.stroke_color,
            "backgroundColor": self.style.background_color,
            "fillStyle": "solid",
            "strokeWidth": self.style.stroke_width,
            "strokeStyle": self.style.border_style,
            "roughness": self.style.roughness,
            "opacity": self.style.opacity,
            "groupIds": self.group_ids,
            "frameId": self.frame_id,
            "index": "a0",  # Will be updated when adding to diagram
            "roundness": {"type": 3} if self.style.rounded else None,
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.version_nonce,
            "isDeleted": self.is_deleted,
            "boundElements": self.bound_elements,
            "updated": self.updated,
            "link": self.link,
            "locked": self.locked,
        }
    
    def get_text_element(self) -> Optional[dict]:
        """Get the text element for this box."""
        if not self.text:
            return None
        
        # Calculate text position (centered in box)
        text_x = self.pos.x + 10
        text_y = self.pos.y + 20
        
        return {
            "type": "text",
            "version": 1,
            "versionNonce": generate_seed(),
            "isDeleted": False,
            "id": self.text_id,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "x": text_x,
            "y": text_y,
            "strokeColor": Color.BLACK,
            "backgroundColor": "transparent",
            "width": self.pos.width - 20,
            "height": self.pos.height - 40,
            "seed": generate_seed(),
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "boundElements": [],
            "updated": self.updated,
            "link": None,
            "locked": False,
            "fontSize": 15,
            "fontFamily": 1,
            "text": self.text,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": self.id,
            "originalText": self.text,
            "lineHeight": 1.25,
            "baseline": 0,
        }


class Text(Element):
    """Standalone text element."""
    
    def __init__(
        self,
        pos: Position,
        text: str,
        font_size: int = 16,
        color: str = Color.BLACK,
        align: str = "left",
        font_family: int = 6,  # 1: Hand-drawn, 6: Code/System font (fashion flow uses 6)
        element_id: Optional[str] = None,
    ):
        super().__init__(element_id)
        self.pos = pos
        self.text = text
        self.font_size = font_size
        self.color = color
        self.align = align
        self.font_family = font_family
    
    def to_dict(self) -> dict:
        """Convert text to Excalidraw JSON."""
        return {
            "id": self.id,
            "type": "text",
            "x": self.pos.x,
            "y": self.pos.y,
            "width": self.pos.width or 400,
            "height": self.pos.height or 25,
            "angle": 0,
            "strokeColor": self.color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": self.group_ids,
            "frameId": self.frame_id,
            "index": "a0",
            "roundness": None,
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.version_nonce,
            "isDeleted": self.is_deleted,
            "boundElements": [],
            "updated": self.updated,
            "link": self.link,
            "locked": self.locked,
            "text": self.text,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "textAlign": self.align,
            "verticalAlign": "top",
            "containerId": None,
            "originalText": self.text,
            "autoResize": True,
            "lineHeight": 1.25,
        }


class Arrow(Element):
    """Arrow element connecting two points or elements."""
    
    def __init__(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        style: Optional[ArrowStyle] = None,
        label: str = "",
        start_binding: Optional[str] = None,
        end_binding: Optional[str] = None,
        start_fixed_point: Optional[list] = None,
        end_fixed_point: Optional[list] = None,
        element_id: Optional[str] = None,
    ):
        super().__init__(element_id)
        self.start = start
        self.end = end
        self.style = style or ArrowStyle.default()
        self.label = label
        self.start_binding = start_binding
        self.end_binding = end_binding
        self.start_fixed_point = start_fixed_point
        self.end_fixed_point = end_fixed_point
        self.label_id = generate_id("arrow_label_") if label else None
    
    def midpoint_pos(self, circle_size: Tuple[float, float] = (28, 42)) -> Position:
        """Get position for a circle/element at the arrow's midpoint.
        
        Args:
            circle_size: (width, height) of the circle to place
        
        Returns:
            Position centered on arrow's midpoint
        """
        mid_x = (self.start[0] + self.end[0]) / 2
        mid_y = (self.start[1] + self.end[1]) / 2
        
        # Center the circle on midpoint
        return Position(
            x=mid_x - circle_size[0] / 2,
            y=mid_y - circle_size[1] / 2,
            width=circle_size[0],
            height=circle_size[1]
        )
    
    def to_dict(self) -> dict:
        """Convert arrow to Excalidraw JSON."""
        # Calculate relative points
        points = [[0, 0], [self.end[0] - self.start[0], self.end[1] - self.start[1]]]
        
        bound_elements = []
        if self.label:
            bound_elements.append({"id": self.label_id, "type": "text"})
        
        # Note: fixedPoint is relative to element (0-1 range)
        # If provided, use custom fixed point, otherwise let Excalidraw auto-calculate
        bindings = {}
        if self.start_binding:
            bindings["startBinding"] = {
                "elementId": self.start_binding,
                "mode": "orbit",
                "fixedPoint": self.start_fixed_point  # Custom or None for auto
            }
        if self.end_binding:
            bindings["endBinding"] = {
                "elementId": self.end_binding,
                "mode": "orbit",
                "fixedPoint": self.end_fixed_point  # Custom or None for auto
            }
        
        return {
            "type": "arrow",
            "version": self.version,
            "versionNonce": self.version_nonce,
            "isDeleted": self.is_deleted,
            "id": self.id,
            "fillStyle": "solid",
            "strokeWidth": self.style.stroke_width,
            "strokeStyle": self.style.stroke_style,
            "roughness": self.style.roughness,
            "opacity": self.style.opacity,
            "angle": 0,
            "x": self.start[0],
            "y": self.start[1],
            "strokeColor": self.style.stroke_color,
            "backgroundColor": "transparent",
            "width": abs(self.end[0] - self.start[0]),
            "height": abs(self.end[1] - self.start[1]),
            "seed": self.seed,
            "groupIds": self.group_ids,
            "frameId": self.frame_id,
            "roundness": {"type": 2},
            "boundElements": bound_elements,
            "updated": self.updated,
            "link": None,
            "locked": False,
            "points": points,
            "lastCommittedPoint": None,
            **bindings,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": False,
            "moveMidPointsWithElement": False,
        }
    
    def get_label_element(self) -> Optional[dict]:
        """Get the label text element for this arrow."""
        if not self.label:
            return None
        
        # Calculate label position (middle of arrow)
        label_x = (self.start[0] + self.end[0]) / 2 - 50
        label_y = (self.start[1] + self.end[1]) / 2 - 10
        
        return {
            "type": "text",
            "version": 1,
            "versionNonce": generate_seed(),
            "isDeleted": False,
            "id": self.label_id,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "x": label_x,
            "y": label_y,
            "strokeColor": Color.BLACK,
            "backgroundColor": "transparent",
            "width": 100,
            "height": 20,
            "seed": generate_seed(),
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "boundElements": [],
            "updated": self.updated,
            "link": None,
            "locked": False,
            "fontSize": 14,
            "fontFamily": 1,
            "text": self.label,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": self.id,
            "originalText": self.label,
            "lineHeight": 1.25,
            "baseline": 0,
        }


class BoundingBox(Element):
    """Bounding box to group related elements visually."""
    
    def __init__(
        self,
        pos: Position,
        title: str = "",
        stroke_color: str = "#1e1e1e",
        background_color: str = "transparent",
        stroke_width: int = 2,
        stroke_style: str = "dashed",  # "solid", "dashed", "dotted"
        element_id: Optional[str] = None,
    ):
        super().__init__(element_id)
        self.pos = pos
        self.title = title
        self.stroke_color = stroke_color
        self.background_color = background_color
        self.stroke_width = stroke_width
        self.stroke_style = stroke_style
        self.title_id = generate_id("bbox_title_") if title else None
    
    def to_dict(self) -> dict:
        """Convert bounding box to Excalidraw JSON."""
        bound_elements = []
        if self.title:
            bound_elements.append({"id": self.title_id, "type": "text"})
        
        return {
            "id": self.id,
            "type": "rectangle",
            "x": self.pos.x,
            "y": self.pos.y,
            "width": self.pos.width,
            "height": self.pos.height,
            "angle": 0,
            "strokeColor": self.stroke_color,
            "backgroundColor": self.background_color,
            "fillStyle": "solid",
            "strokeWidth": self.stroke_width,
            "strokeStyle": self.stroke_style,
            "roughness": 1,
            "opacity": 100,
            "groupIds": self.group_ids,
            "frameId": self.frame_id,
            "index": "a0",
            "roundness": {"type": 3},
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.version_nonce,
            "isDeleted": self.is_deleted,
            "boundElements": bound_elements,
            "updated": self.updated,
            "link": self.link,
            "locked": self.locked,
        }
    
    def get_title_element(self) -> Optional[dict]:
        """Get the title text element for this bounding box."""
        if not self.title:
            return None
        
        # Place title at top-left inside the box
        title_x = self.pos.x + 15
        title_y = self.pos.y + 10
        
        return {
            "type": "text",
            "version": 1,
            "versionNonce": generate_seed(),
            "isDeleted": False,
            "id": self.title_id,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "x": title_x,
            "y": title_y,
            "strokeColor": self.stroke_color,
            "backgroundColor": "transparent",
            "width": self.pos.width - 30,
            "height": 25,
            "seed": generate_seed(),
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "boundElements": [],
            "updated": self.updated,
            "link": None,
            "locked": False,
            "fontSize": 18,
            "fontFamily": 1,
            "text": self.title,
            "textAlign": "left",
            "verticalAlign": "top",
            "containerId": None,
            "originalText": self.title,
            "autoResize": True,
            "lineHeight": 1.25,
            "baseline": 18,
        }


class Circle(Element):
    """Circle/Ellipse element."""
    
    def __init__(
        self,
        pos: Position,
        text: str = "",
        color: str = Color.PURPLE_LIGHT,
        element_id: Optional[str] = None,
    ):
        super().__init__(element_id)
        self.pos = pos
        self.text = text
        self.color = color
        self.text_id = generate_id("circle_text_") if text else None
    
    def to_dict(self) -> dict:
        """Convert circle to Excalidraw JSON."""
        bound_elements = []
        if self.text:
            bound_elements.append({"id": self.text_id, "type": "text"})
        
        return {
            "type": "ellipse",
            "version": self.version,
            "versionNonce": self.version_nonce,
            "isDeleted": self.is_deleted,
            "id": self.id,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "x": self.pos.x,
            "y": self.pos.y,
            "strokeColor": Color.BLACK,
            "backgroundColor": self.color,
            "width": self.pos.width,
            "height": self.pos.height,
            "seed": self.seed,
            "groupIds": self.group_ids,
            "frameId": self.frame_id,
            "roundness": {"type": 2},
            "boundElements": bound_elements,
            "updated": self.updated,
            "link": None,
            "locked": False,
        }
    
    def get_text_element(self) -> Optional[dict]:
        """Get the text element for this circle."""
        if not self.text:
            return None
        
        text_x = self.pos.x + self.pos.width / 2 - 10
        text_y = self.pos.y + self.pos.height / 2 - 10
        
        return {
            "type": "text",
            "version": 1,
            "versionNonce": generate_seed(),
            "isDeleted": False,
            "id": self.text_id,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "x": text_x,
            "y": text_y,
            "strokeColor": Color.BLACK,
            "backgroundColor": "transparent",
            "width": 20,
            "height": 20,
            "seed": generate_seed(),
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "boundElements": [],
            "updated": self.updated,
            "link": None,
            "locked": False,
            "fontSize": 16,
            "fontFamily": 1,
            "text": self.text,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": self.id,
            "originalText": self.text,
            "lineHeight": 1.25,
            "baseline": 0,
        }
