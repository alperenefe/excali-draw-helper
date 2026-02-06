"""
Component Registry for consistent styling across diagram phases.

This module provides a centralized way to define component colors that should remain
consistent when the same component appears in multiple phases/groups.
"""

from typing import Dict, Tuple
from .styles import BoxStyle


# Predefined color palettes (stroke, background)
class ComponentColors:
    """Predefined color pairs for common component types."""
    PURPLE = ("#6741d9", "#e5dbff")    # Data stores
    GREEN = ("#2f9e44", "#d3f9d8")     # APIs/Services
    BLUE = ("#1971c2", "#a5d8ff")      # Search engines
    ORANGE = ("#e8590c", "#ffe8cc")    # New/developing
    RED = ("#e03131", "#ffe3e3")       # Critical
    YELLOW = ("#fab005", "#fff4cc")    # External/third-party


class ComponentRegistry:
    """
    Registry for managing component styles across diagram phases.
    
    Usage:
        registry = ComponentRegistry()
        registry.register("target_bq", ComponentColors.PURPLE)
        registry.register("itsa", ComponentColors.GREEN)
        
        # Later, when creating duplicate components:
        target_bq_style = registry.get_style("target_bq")
        itsa_style = registry.get_style("itsa")
    """
    
    def __init__(self):
        self._components: Dict[str, Tuple[str, str]] = {}
    
    def register(self, component_id: str, color_pair: Tuple[str, str]) -> None:
        """
        Register a component with its color scheme.
        
        Args:
            component_id: Unique identifier for the component (e.g., "target_bq", "itsa")
            color_pair: Tuple of (stroke_color, background_color)
        """
        self._components[component_id] = color_pair
    
    def get_style(self, component_id: str) -> BoxStyle:
        """
        Get consistent style for a registered component.
        
        Args:
            component_id: The component identifier
            
        Returns:
            BoxStyle with the registered colors, or default style if not registered
        """
        if component_id in self._components:
            return BoxStyle.component(self._components[component_id])
        return BoxStyle.default()
    
    def is_registered(self, component_id: str) -> bool:
        """Check if a component is registered."""
        return component_id in self._components
    
    def get_all_components(self) -> Dict[str, Tuple[str, str]]:
        """Get all registered components and their colors."""
        return self._components.copy()


# Global default registry (can be used across examples)
DEFAULT_REGISTRY = ComponentRegistry()

# Register common components
DEFAULT_REGISTRY.register("target_bq", ComponentColors.PURPLE)
DEFAULT_REGISTRY.register("itsa", ComponentColors.GREEN)
DEFAULT_REGISTRY.register("elasticsearch", ComponentColors.BLUE)
