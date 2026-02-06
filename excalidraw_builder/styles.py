"""
Style definitions for Excalidraw elements.
"""

from dataclasses import dataclass
from typing import Optional


class Color:
    """Common colors used in diagrams."""
    BLACK = "#1e1e1e"
    WHITE = "#ffffff"
    TRANSPARENT = "transparent"
    
    # Grays (for neutral/grouping elements)
    GRAY = "#868e96"
    GRAY_LIGHT = "#ced4da"
    
    # Greens (for successful/completed states)
    GREEN_DARK = "#2f9e44"
    GREEN_LIGHT = "#b2f2bb"
    GREEN_PALE = "#d3f9d8"
    
    # Orange (for in-progress/warning states)
    ORANGE_DARK = "#e8590c"
    ORANGE_LIGHT = "#ffe8cc"
    ORANGE_MID = "#ffd8a8"
    
    # Red (for errors/critical states)
    RED_DARK = "#e03131"
    RED_LIGHT = "#ffc9c9"
    RED_PALE = "#ffe3e3"
    
    # Blue (for info states)
    BLUE_DARK = "#1971c2"
    BLUE_LIGHT = "#a5d8ff"
    BLUE_PALE = "#d0ebff"
    
    # Purple (for special states)
    PURPLE_LIGHT = "#d0bfff"
    PURPLE_MID = "#e599f7"
    
    # Yellow (for external/third-party services)
    YELLOW_LIGHT = "#fff4cc"
    YELLOW_PALE = "#fff9db"
    YELLOW_DARK = "#fab005"


@dataclass
class BoxStyle:
    """Style configuration for boxes."""
    stroke_color: str = Color.BLACK
    background_color: str = Color.TRANSPARENT
    stroke_width: int = 2
    border_style: str = "solid"  # solid, dashed, dotted
    roughness: int = 1
    opacity: int = 100
    rounded: bool = True
    
    @classmethod
    def success(cls, bold: bool = False, filled: bool = False) -> "BoxStyle":
        """Green style for successful/completed states."""
        return cls(
            stroke_color=Color.GREEN_DARK,
            background_color=Color.GREEN_LIGHT if filled else Color.TRANSPARENT,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def warning(cls, bold: bool = False, filled: bool = False) -> "BoxStyle":
        """Orange style for in-progress/warning states."""
        return cls(
            stroke_color=Color.ORANGE_DARK,
            background_color=Color.ORANGE_LIGHT if filled else Color.TRANSPARENT,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def error(cls, bold: bool = False, filled: bool = False) -> "BoxStyle":
        """Red style for error/critical states."""
        return cls(
            stroke_color=Color.RED_DARK,
            background_color=Color.RED_LIGHT if filled else Color.TRANSPARENT,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def info(cls, bold: bool = False, filled: bool = False) -> "BoxStyle":
        """Blue style for info states."""
        return cls(
            stroke_color=Color.BLUE_DARK,
            background_color=Color.BLUE_LIGHT if filled else Color.TRANSPARENT,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def data_source(cls, filled: bool = False) -> "BoxStyle":
        """Light green for data sources (BQ, DB, etc)."""
        return cls(
            stroke_color=Color.GREEN_DARK,
            background_color=Color.GREEN_PALE if filled else Color.TRANSPARENT,
        )
    
    @classmethod
    def default(cls) -> "BoxStyle":
        """Default transparent box (fashion flow style)."""
        return cls(
            stroke_color=Color.BLACK,
            background_color=Color.TRANSPARENT,
        )
    
    @classmethod
    def service_itsa(cls) -> "BoxStyle":
        """Green style for ITSA (existing service)."""
        return cls(
            stroke_color=Color.GREEN_DARK,
            background_color=Color.GREEN_PALE,
            stroke_width=2,
        )
    
    @classmethod
    def service_elasticsearch(cls) -> "BoxStyle":
        """Blue style for Elasticsearch (data store)."""
        return cls(
            stroke_color=Color.BLUE_DARK,
            background_color=Color.BLUE_LIGHT,
            stroke_width=2,
        )
    
    @classmethod
    def service_new(cls) -> "BoxStyle":
        """Orange style for new services/APIs."""
        return cls(
            stroke_color=Color.ORANGE_DARK,
            background_color=Color.ORANGE_LIGHT,
            stroke_width=2,
        )
    
    @classmethod
    def component(cls, color_pair: tuple[str, str]) -> "BoxStyle":
        """
        Generic style for duplicate components across phases.
        
        Args:
            color_pair: Tuple of (stroke_color, background_color)
        
        Example:
            BoxStyle.component(("#6741d9", "#e5dbff"))  # Purple
        """
        return cls(
            stroke_color=color_pair[0],
            background_color=color_pair[1],
            stroke_width=2,
        )


@dataclass
class ArrowStyle:
    """Style configuration for arrows."""
    stroke_color: str = Color.BLACK
    stroke_width: int = 2
    stroke_style: str = "solid"  # solid, dashed, dotted
    roughness: int = 1
    opacity: int = 100
    
    @classmethod
    def success(cls, bold: bool = False) -> "ArrowStyle":
        """Green arrow for successful flows."""
        return cls(
            stroke_color=Color.GREEN_DARK,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def warning(cls, bold: bool = False) -> "ArrowStyle":
        """Orange arrow for warning flows."""
        return cls(
            stroke_color=Color.ORANGE_DARK,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def error(cls, bold: bool = False) -> "ArrowStyle":
        """Red arrow for error flows."""
        return cls(
            stroke_color=Color.RED_DARK,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def info(cls, bold: bool = False) -> "ArrowStyle":
        """Blue arrow for info flows."""
        return cls(
            stroke_color=Color.BLUE_DARK,
            stroke_width=3 if bold else 2,
        )
    
    @classmethod
    def default(cls) -> "ArrowStyle":
        """Default black arrow."""
        return cls()
