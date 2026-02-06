#!/usr/bin/env python3
"""
Collision Detector for Excalidraw Diagrams

Post-process tool to detect overlapping boxes in generated diagrams.
- Bounding boxes (dashed borders) can overlap with content boxes (normal)
- Bounding boxes should NOT overlap with other bounding boxes
- Content boxes should NOT overlap with other content boxes
"""

import json
import sys
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class BoxInfo:
    """Box information for collision detection"""
    id: str
    x: float
    y: float
    width: float
    height: float
    text: str
    is_bounding_box: bool  # True if dashed border (phase/group box)
    
    @property
    def x2(self) -> float:
        return self.x + self.width
    
    @property
    def y2(self) -> float:
        return self.y + self.height
    
    def overlaps(self, other: 'BoxInfo') -> bool:
        """Check if this box overlaps with another box"""
        return not (
            self.x2 <= other.x or  # This box is completely to the left
            self.x >= other.x2 or  # This box is completely to the right
            self.y2 <= other.y or  # This box is completely above
            self.y >= other.y2     # This box is completely below
        )
    
    def overlap_area(self, other: 'BoxInfo') -> float:
        """Calculate overlap area between two boxes"""
        if not self.overlaps(other):
            return 0.0
        
        overlap_width = min(self.x2, other.x2) - max(self.x, other.x)
        overlap_height = min(self.y2, other.y2) - max(self.y, other.y)
        return overlap_width * overlap_height


def load_diagram(filepath: str) -> dict:
    """Load Excalidraw diagram from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def extract_boxes(diagram_data: dict) -> List[BoxInfo]:
    """Extract all rectangle boxes from diagram"""
    boxes = []
    
    for element in diagram_data.get('elements', []):
        if element.get('type') != 'rectangle':
            continue
        
        # Get text from bound text element
        text = ""
        text_id = None
        for bound in element.get('boundElements', []):
            if bound.get('type') == 'text':
                text_id = bound.get('id')
                break
        
        if text_id:
            for elem in diagram_data.get('elements', []):
                if elem.get('id') == text_id and elem.get('type') == 'text':
                    text = elem.get('text', '')
                    break
        
        # Determine if this is a bounding box (dashed border, no fill)
        is_bounding = (
            element.get('strokeStyle') == 'dashed' and
            element.get('backgroundColor') == 'transparent' and
            (not text or text.strip() == '')  # Bounding boxes have no text or empty text
        )
        
        boxes.append(BoxInfo(
            id=element.get('id'),
            x=element.get('x'),
            y=element.get('y'),
            width=element.get('width'),
            height=element.get('height'),
            text=text[:50],  # First 50 chars for identification
            is_bounding_box=is_bounding
        ))
    
    return boxes


def detect_collisions(
    boxes: List[BoxInfo], 
    bounding_min_margin: int = 150,
    content_min_margin: int = 100
) -> Dict[str, List[Tuple[BoxInfo, BoxInfo]]]:
    """
    Detect collisions between boxes.
    
    Rules:
    1. Bounding boxes CAN overlap with content boxes (they contain them)
    2. Bounding boxes should NOT overlap with other bounding boxes
    3. Content boxes should NOT overlap with other content boxes
    4. Bounding boxes should have minimum margin (default: 150px)
    5. Content boxes should have minimum margin (default: 100px)
    
    Args:
        bounding_min_margin: Minimum distance between bounding boxes (default: 150px)
        content_min_margin: Minimum distance between content boxes (default: 100px)
    
    Returns:
        Dictionary with collision types and list of colliding box pairs
    """
    collisions = {
        'bounding_vs_bounding': [],
        'bounding_too_close': [],
        'content_vs_content': [],
        'content_too_close': []
    }
    
    for i, box1 in enumerate(boxes):
        for box2 in boxes[i+1:]:
            # Both are bounding boxes
            if box1.is_bounding_box and box2.is_bounding_box:
                # Check for overlap - CRITICAL!
                if box1.overlaps(box2):
                    collisions['bounding_vs_bounding'].append((box1, box2))
                else:
                    # Check margin - should have breathing room
                    vertical_gap = min(abs(box1.y - box2.y2), abs(box2.y - box1.y2))
                    horizontal_gap = min(abs(box1.x - box2.x2), abs(box2.x - box1.x2))
                    
                    # If they're stacked vertically (not side-by-side)
                    if horizontal_gap < 200:  # Overlapping horizontally
                        if vertical_gap < bounding_min_margin:
                            collisions['bounding_too_close'].append((box1, box2))
            
            # Both are content boxes
            elif not box1.is_bounding_box and not box2.is_bounding_box:
                # Check for overlap - CRITICAL!
                if box1.overlaps(box2):
                    overlap_area = box1.overlap_area(box2)
                    overlap_percentage = (overlap_area / min(box1.width * box1.height, 
                                                              box2.width * box2.height)) * 100
                    
                    # Only report if significant overlap (>10%)
                    if overlap_percentage > 10:
                        collisions['content_vs_content'].append((box1, box2))
                else:
                    # Check margin - should have breathing room
                    # Determine relative positions
                    # X overlap check: are they vertically aligned (one below the other)?
                    x_overlap = not (box1.x2 < box2.x or box2.x2 < box1.x)
                    
                    # Y overlap check: are they horizontally aligned (side by side)?
                    y_overlap = not (box1.y2 < box2.y or box2.y2 < box1.y)
                    
                    # Calculate gaps
                    vertical_gap = abs(box2.y - box1.y2) if box2.y > box1.y2 else abs(box1.y - box2.y2)
                    horizontal_gap = abs(box2.x - box1.x2) if box2.x > box1.x2 else abs(box1.x - box2.x2)
                    
                    # Check if vertically stacked (same X range, different Y)
                    if x_overlap and vertical_gap < content_min_margin:
                        collisions['content_too_close'].append((box1, box2))
                    
                    # Check if horizontally placed (same Y range, different X)
                    elif y_overlap and horizontal_gap < content_min_margin:
                        collisions['content_too_close'].append((box1, box2))
            
            # Bounding vs content - OK (expected)
    
    return collisions


def print_collision_report(collisions: Dict[str, List[Tuple[BoxInfo, BoxInfo]]]):
    """Print collision detection report"""
    total_issues = sum(len(v) for v in collisions.values())
    
    if total_issues == 0:
        print("\n✅ NO COLLISIONS DETECTED!")
        print("   All bounding boxes and content boxes are properly positioned.")
        return
    
    print(f"\n⚠️  ISSUES DETECTED: {total_issues} issue(s) found\n")
    print("=" * 80)
    
    # Bounding box collisions
    if collisions['bounding_vs_bounding']:
        print("\n🔴 BOUNDING BOX OVERLAPS (Critical):")
        print("-" * 80)
        for box1, box2 in collisions['bounding_vs_bounding']:
            overlap_area = box1.overlap_area(box2)
            print(f"\n  Box 1: [{box1.x:.0f}, {box1.y:.0f}] size: {box1.width:.0f}x{box1.height:.0f}")
            print(f"         Text: {box1.text[:40]}...")
            print(f"  Box 2: [{box2.x:.0f}, {box2.y:.0f}] size: {box2.width:.0f}x{box2.height:.0f}")
            print(f"         Text: {box2.text[:40]}...")
            print(f"  Overlap Area: {overlap_area:.0f} px²")
            print(f"\n  💡 FIX: Adjust y-coordinates to separate phases:")
            print(f"     Phase 1 ends at: {box1.y2:.0f}")
            print(f"     Phase 2 should start at: {box1.y2 + 150:.0f} (with 150px margin)")
    
    # Bounding boxes too close
    if collisions['bounding_too_close']:
        print("\n🟡 BOUNDING BOXES TOO CLOSE (Warning):")
        print("-" * 80)
        for box1, box2 in collisions['bounding_too_close']:
            vertical_gap = min(abs(box1.y - box2.y2), abs(box2.y - box1.y2))
            print(f"\n  Box 1: [{box1.x:.0f}, {box1.y:.0f}] size: {box1.width:.0f}x{box1.height:.0f}")
            print(f"         Ends at: {box1.y2:.0f}")
            print(f"  Box 2: [{box2.x:.0f}, {box2.y:.0f}] size: {box2.width:.0f}x{box2.height:.0f}")
            print(f"         Starts at: {box2.y:.0f}")
            print(f"  Vertical Gap: {vertical_gap:.0f} px (recommended: ≥150px)")
            print(f"\n  💡 FIX: Increase margin between phases:")
            print(f"     Current gap: {vertical_gap:.0f}px")
            print(f"     Recommended: Move Phase 2 to y={box1.y2 + 150:.0f} (+{150-vertical_gap:.0f}px)")
    
    # Content box collisions
    if collisions['content_vs_content']:
        print("\n🔴 CONTENT BOX OVERLAPS (Critical):")
        print("-" * 80)
        for box1, box2 in collisions['content_vs_content']:
            overlap_area = box1.overlap_area(box2)
            overlap_pct = (overlap_area / min(box1.width * box1.height, 
                                               box2.width * box2.height)) * 100
            print(f"\n  Box 1: [{box1.x:.0f}, {box1.y:.0f}] size: {box1.width:.0f}x{box1.height:.0f}")
            print(f"         Text: {box1.text[:40]}...")
            print(f"         Ends at: y={box1.y2:.0f}")
            print(f"  Box 2: [{box2.x:.0f}, {box2.y:.0f}] size: {box2.width:.0f}x{box2.height:.0f}")
            print(f"         Text: {box2.text[:40]}...")
            print(f"  Overlap: {overlap_area:.0f} px² ({overlap_pct:.1f}%)")
            print(f"\n  💡 FIX: Move Box 2 down to y={box1.y2 + 100:.0f} (Box 1 ends + 100px margin)")
            print(f"     Shift needed: +{(box1.y2 + 100 - box2.y):.0f}px")
    
    # Content boxes too close
    if collisions['content_too_close']:
        print("\n🟡 CONTENT BOXES TOO CLOSE (Warning):")
        print("-" * 80)
        for box1, box2 in collisions['content_too_close']:
            # Determine relative positions
            x_overlap = not (box1.x2 < box2.x or box2.x2 < box1.x)
            y_overlap = not (box1.y2 < box2.y or box2.y2 < box1.y)
            
            # Calculate gaps
            vertical_gap = abs(box2.y - box1.y2) if box2.y > box1.y2 else abs(box1.y - box2.y2)
            horizontal_gap = abs(box2.x - box1.x2) if box2.x > box1.x2 else abs(box1.x - box2.x2)
            
            print(f"\n  Box 1: [{box1.x:.0f}, {box1.y:.0f}] size: {box1.width:.0f}x{box1.height:.0f}")
            print(f"         Text: {box1.text[:40]}...")
            print(f"         Ends at: y={box1.y2:.0f}, x={box1.x2:.0f}")
            print(f"  Box 2: [{box2.x:.0f}, {box2.y:.0f}] size: {box2.width:.0f}x{box2.height:.0f}")
            print(f"         Text: {box2.text[:40]}...")
            
            # Check which type of spacing issue
            if x_overlap:  # Vertically stacked
                print(f"  Vertical Gap: {vertical_gap:.0f}px (recommended: ≥100px)")
                print(f"\n  💡 FIX: Increase vertical gap to 100px")
                if box2.y > box1.y:
                    print(f"     Move Box 2 to y={box1.y2 + 100:.0f}")
                    print(f"     Shift needed: +{(box1.y2 + 100 - box2.y):.0f}px")
                else:
                    print(f"     Move Box 1 to y={box2.y2 + 100:.0f}")
                    print(f"     Shift needed: +{(box2.y2 + 100 - box1.y):.0f}px")
            elif y_overlap:  # Side by side
                print(f"  Horizontal Gap: {horizontal_gap:.0f}px (recommended: ≥100px)")
                print(f"\n  💡 FIX: Increase horizontal gap to 100px")
                if box2.x > box1.x:
                    print(f"     Move Box 2 to x={box1.x2 + 100:.0f}")
                    print(f"     Shift needed: +{(box1.x2 + 100 - box2.x):.0f}px")
                else:
                    print(f"     Move Box 1 to x={box2.x2 + 100:.0f}")
                    print(f"     Shift needed: +{(box2.x2 + 100 - box1.x):.0f}px")
    
    print("\n" + "=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python collision_detector.py <diagram.excalidraw>")
        print("\nExample:")
        print("  python collision_detector.py output/fashion_core_complete.excalidraw")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print(f"\n🔍 Analyzing diagram: {filepath}")
    print("=" * 80)
    
    # Load diagram
    try:
        diagram = load_diagram(filepath)
    except Exception as e:
        print(f"❌ Error loading diagram: {e}")
        sys.exit(1)
    
    # Extract boxes
    boxes = extract_boxes(diagram)
    bounding_boxes = [b for b in boxes if b.is_bounding_box]
    content_boxes = [b for b in boxes if not b.is_bounding_box]
    
    print(f"\n📊 Statistics:")
    print(f"   - Total boxes: {len(boxes)}")
    print(f"   - Bounding boxes (dashed): {len(bounding_boxes)}")
    print(f"   - Content boxes: {len(content_boxes)}")
    
    # Detect collisions
    collisions = detect_collisions(boxes)
    
    # Print report
    print_collision_report(collisions)
    
    # Exit code
    total_issues = sum(len(v) for v in collisions.values())
    sys.exit(0 if total_issues == 0 else 1)


if __name__ == '__main__':
    main()
