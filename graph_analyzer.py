"""
Graph Analyzer - Complete connection and grouping analysis
Shows WHO connects to WHO, where are the groups, flow structure
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class GraphAnalyzer:
    def __init__(self, json_data):
        self.elements = json_data.get("elements", [])
        self.elem_map = {e.get("id"): e for e in self.elements}
        
        # Organize by type
        self.boxes = []
        self.arrows = []
        self.texts = []
        self.frames = []
        self.bounding_boxes = []
        
        for elem in self.elements:
            elem_type = elem.get("type")
            if elem_type == "rectangle":
                if elem.get("strokeStyle") == "dashed":
                    self.bounding_boxes.append(elem)
                else:
                    self.boxes.append(elem)
            elif elem_type == "arrow":
                self.arrows.append(elem)
            elif elem_type == "text" and not elem.get("containerId"):
                self.texts.append(elem)
            elif elem_type == "frame":
                self.frames.append(elem)
    
    def get_element_text(self, elem_id):
        """Get text content of an element."""
        elem = self.elem_map.get(elem_id)
        if not elem:
            return ""
        
        # If it's a box/rectangle, find bound text
        if elem.get("type") == "rectangle":
            bound_elems = elem.get("boundElements", [])
            for bound in bound_elems:
                if bound.get("type") == "text":
                    text_elem = self.elem_map.get(bound.get("id"))
                    if text_elem:
                        text = text_elem.get("text", "")
                        # Truncate for display
                        return text[:50] + "..." if len(text) > 50 else text
        
        return ""
    
    def build_connection_graph(self):
        """Build full connection graph."""
        graph = defaultdict(list)  # from_id -> [(to_id, label), ...]
        reverse_graph = defaultdict(list)  # to_id -> [(from_id, label), ...]
        
        for arrow in self.arrows:
            arrow_id = arrow.get("id", "")[:8]
            
            start_binding = arrow.get("startBinding")
            end_binding = arrow.get("endBinding")
            
            start_id = start_binding.get("elementId") if start_binding else None
            end_id = end_binding.get("elementId") if end_binding else None
            
            # Get arrow label
            label = ""
            bound_elems = arrow.get("boundElements", [])
            for bound in bound_elems:
                if bound.get("type") == "text":
                    text_elem = self.elem_map.get(bound.get("id"))
                    if text_elem:
                        label = text_elem.get("text", "")
                        # Clean up label
                        label = label.replace("\n", " ")[:60]
            
            if start_id and end_id:
                graph[start_id].append((end_id, label, arrow_id))
                reverse_graph[end_id].append((start_id, label, arrow_id))
        
        return graph, reverse_graph
    
    def find_root_nodes(self, graph, reverse_graph):
        """Find nodes with no incoming connections (roots)."""
        all_nodes = set(graph.keys()) | set(reverse_graph.keys())
        nodes_with_incoming = set(reverse_graph.keys())
        roots = all_nodes - nodes_with_incoming
        return roots
    
    def find_leaf_nodes(self, graph, reverse_graph):
        """Find nodes with no outgoing connections (leaves)."""
        all_nodes = set(graph.keys()) | set(reverse_graph.keys())
        nodes_with_outgoing = set(graph.keys())
        leaves = all_nodes - nodes_with_outgoing
        return leaves
    
    def detect_groups(self):
        """Detect grouping structures (bounding boxes, frames)."""
        groups = []
        
        # Frames
        for frame in self.frames:
            frame_id = frame.get("id", "")[:8]
            frame_name = frame.get("name", "Unnamed")
            x, y = frame.get("x", 0), frame.get("y", 0)
            w, h = frame.get("width", 0), frame.get("height", 0)
            
            # Find elements inside frame
            contained = []
            for elem in self.elements:
                if elem.get("frameId") == frame.get("id"):
                    elem_id = elem.get("id", "")[:8]
                    elem_type = elem.get("type", "")
                    contained.append((elem_id, elem_type))
            
            groups.append({
                "type": "frame",
                "id": frame_id,
                "name": frame_name,
                "bounds": (x, y, w, h),
                "contains": contained
            })
        
        # Bounding boxes (dashed rectangles)
        for bbox in self.bounding_boxes:
            bbox_id = bbox.get("id", "")[:8]
            x, y = bbox.get("x", 0), bbox.get("y", 0)
            w, h = bbox.get("width", 0), bbox.get("height", 0)
            
            # Find bound text (title)
            title = ""
            bound_elems = bbox.get("boundElements", [])
            for bound in bound_elems:
                if bound.get("type") == "text":
                    text_elem = self.elem_map.get(bound.get("id"))
                    if text_elem:
                        title = text_elem.get("text", "")[:50]
            
            # Find elements spatially inside (rough heuristic)
            contained = []
            for elem in self.elements:
                if elem.get("id") == bbox.get("id"):
                    continue
                ex, ey = elem.get("x", 0), elem.get("y", 0)
                ew, eh = elem.get("width", 0), elem.get("height", 0)
                
                # Check if elem center is inside bbox
                center_x = ex + ew / 2
                center_y = ey + eh / 2
                
                if (x <= center_x <= x + w) and (y <= center_y <= y + h):
                    elem_id = elem.get("id", "")[:8]
                    elem_type = elem.get("type", "")
                    contained.append((elem_id, elem_type))
            
            groups.append({
                "type": "bounding_box",
                "id": bbox_id,
                "title": title or "(no title)",
                "bounds": (x, y, w, h),
                "contains": contained[:10]  # Limit to 10 for display
            })
        
        return groups
    
    def analyze(self):
        """Full analysis."""
        output = []
        
        output.append("=" * 100)
        output.append("🔗 COMPLETE GRAPH ANALYSIS")
        output.append("=" * 100)
        output.append("")
        
        # Build graph
        graph, reverse_graph = self.build_connection_graph()
        
        output.append(f"📊 STATISTICS")
        output.append(f"  Total Boxes: {len(self.boxes)}")
        output.append(f"  Total Arrows: {len(self.arrows)}")
        output.append(f"  Connected Nodes: {len(set(graph.keys()) | set(reverse_graph.keys()))}")
        output.append(f"  Frames: {len(self.frames)}")
        output.append(f"  Bounding Boxes: {len(self.bounding_boxes)}")
        output.append("")
        
        # Root and leaf nodes
        roots = self.find_root_nodes(graph, reverse_graph)
        leaves = self.find_leaf_nodes(graph, reverse_graph)
        
        output.append(f"🌱 ROOT NODES (no incoming): {len(roots)}")
        for root_id in list(roots)[:10]:
            text = self.get_element_text(root_id)
            output.append(f"  • {root_id[:8]}: {text}")
        if len(roots) > 10:
            output.append(f"  ... and {len(roots) - 10} more")
        output.append("")
        
        output.append(f"🍃 LEAF NODES (no outgoing): {len(leaves)}")
        for leaf_id in list(leaves)[:10]:
            text = self.get_element_text(leaf_id)
            output.append(f"  • {leaf_id[:8]}: {text}")
        if len(leaves) > 10:
            output.append(f"  ... and {len(leaves) - 10} more")
        output.append("")
        
        # Full connection map
        output.append("=" * 100)
        output.append("🔗 FULL CONNECTION MAP")
        output.append("=" * 100)
        output.append("")
        
        for from_id in sorted(graph.keys()):
            from_text = self.get_element_text(from_id)
            connections = graph[from_id]
            
            output.append(f"📦 [{from_id[:8]}] {from_text}")
            
            for to_id, label, arrow_id in connections:
                to_text = self.get_element_text(to_id)
                if label:
                    output.append(f"  └─➡️  [{to_id[:8]}] {to_text}")
                    output.append(f"      Label: {label}")
                else:
                    output.append(f"  └─➡️  [{to_id[:8]}] {to_text}")
            
            output.append("")
        
        # Grouping analysis
        output.append("=" * 100)
        output.append("📦 GROUPING STRUCTURE")
        output.append("=" * 100)
        output.append("")
        
        groups = self.detect_groups()
        
        if not groups:
            output.append("No groups detected")
        else:
            for i, group in enumerate(groups, 1):
                group_type = group["type"]
                group_id = group["id"]
                
                if group_type == "frame":
                    output.append(f"[{i}] 🖼️  FRAME: {group['name']}")
                    output.append(f"    ID: {group_id}")
                    output.append(f"    Bounds: x={group['bounds'][0]:.0f}, y={group['bounds'][1]:.0f}, "
                                f"w={group['bounds'][2]:.0f}, h={group['bounds'][3]:.0f}")
                    output.append(f"    Contains {len(group['contains'])} elements:")
                    for elem_id, elem_type in group['contains'][:10]:
                        output.append(f"      • {elem_id} ({elem_type})")
                    if len(group['contains']) > 10:
                        output.append(f"      ... and {len(group['contains']) - 10} more")
                
                elif group_type == "bounding_box":
                    output.append(f"[{i}] 📦 BOUNDING BOX: \"{group['title']}\"")
                    output.append(f"    ID: {group_id}")
                    output.append(f"    Bounds: x={group['bounds'][0]:.0f}, y={group['bounds'][1]:.0f}, "
                                f"w={group['bounds'][2]:.0f}, h={group['bounds'][3]:.0f}")
                    output.append(f"    Contains ~{len(group['contains'])} elements (spatial detection):")
                    for elem_id, elem_type in group['contains']:
                        output.append(f"      • {elem_id} ({elem_type})")
                
                output.append("")
        
        # Flow analysis - find main pipeline
        output.append("=" * 100)
        output.append("🔄 MAIN FLOW PATHS")
        output.append("=" * 100)
        output.append("")
        
        # Find key service boxes (white background boxes)
        key_services = []
        for box in self.boxes:
            bg = box.get("backgroundColor", "transparent")
            if bg == "#ffffff":  # White boxes are main services
                box_id = box.get("id")
                text = self.get_element_text(box_id)
                if text and ("Creator" in text or "Definer" in text or "Enricher" in text 
                           or "API" in text or "LLM" in text):
                    key_services.append((box_id, text))
        
        output.append(f"🔧 KEY SERVICES ({len(key_services)}):")
        for i, (service_id, service_text) in enumerate(key_services, 1):
            output.append(f"  [{i}] {service_text}")
            output.append(f"      ID: {service_id[:8]}")
            
            # Incoming
            if service_id in reverse_graph:
                incoming = reverse_graph[service_id]
                output.append(f"      Incoming: {len(incoming)} connections")
                for from_id, label, _ in incoming[:3]:
                    from_text = self.get_element_text(from_id)
                    output.append(f"        ← {from_text[:40]}")
            
            # Outgoing
            if service_id in graph:
                outgoing = graph[service_id]
                output.append(f"      Outgoing: {len(outgoing)} connections")
                for to_id, label, _ in outgoing[:3]:
                    to_text = self.get_element_text(to_id)
                    output.append(f"        → {to_text[:40]}")
            
            output.append("")
        
        return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python graph_analyzer.py <json_file>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print(f"📖 Reading: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON loaded!")
        print("🔍 Analyzing graph structure...")
        
        analyzer = GraphAnalyzer(data)
        analysis = analyzer.analyze()
        
        # Save to file
        output_file = json_file.with_name(json_file.stem + ".graph_analysis.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(analysis)
        
        print(f"✅ Graph analysis saved to: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
        
        # Print first part
        lines = analysis.split('\n')
        print(f"\n📄 First 100 lines:\n")
        print('\n'.join(lines[:100]))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
