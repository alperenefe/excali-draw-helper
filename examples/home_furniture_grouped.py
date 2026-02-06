"""
Home Furniture Cross Reco Flow - Grouped Version
3 separate groups wrapped in bounding boxes + main container
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    BoundingBox,
    Position,
    BoxStyle,
    ArrowStyle,
    Text,
    ComponentRegistry,
    ComponentColors,
)


def main():
    """Create the grouped home furniture flow diagram."""
    diagram = ExcalidrawDiagram(title="Home Furniture Cross Reco Flow (Grouped)")
    
    # ==================== COMPONENT REGISTRY ====================
    # Register components that appear in multiple phases with consistent colors
    registry = ComponentRegistry()
    registry.register("target_bq", ComponentColors.PURPLE)       # Phase 1 & 2
    registry.register("itsa", ComponentColors.GREEN)             # Phase 2 & 3
    registry.register("elasticsearch", ComponentColors.BLUE)     # Phase 2 & 3
    
    # ==================== GROUP 1: DATA PREPARATION ====================
    
    # Starting position for Group 1
    group1_x, group1_y = 100, 150
    
    # Scheduled Script
    scheduled_script_pos = Position(x=group1_x, y=group1_y, width=200, height=179)
    scheduled_script = Box(
        pos=scheduled_script_pos,
        text="📅 Scheduled Script - weekly\n(prod_image_tag_vector_indexing_core)\nReady For Core\n\nRuns daily\nFilters home_furniture products",
        style=BoxStyle.default()
    )
    diagram.add(scheduled_script)
    
    # Target BQ (Phase 1's own copy)
    target_bq_pos = scheduled_script_pos.below(spacing=80)
    target_bq = Box(
        pos=target_bq_pos,
        text="💾 Target BQ Table\n\nhome_furniture products\n(product_id, metadata)",
        style=registry.get_style("target_bq")  # Purple - consistent across phases
    )
    diagram.add(target_bq)
    
    # Connect Group 1 elements
    arrow1 = diagram.connect(scheduled_script, target_bq, label="① writes")
    
    # Group 1 Bounding Box (AUTOMATIC - wraps ONLY group 1 elements)
    group1_elements = [scheduled_script, target_bq, arrow1]
    group1_bbox = diagram.create_bounding_box_for_elements(
        elements=group1_elements,
        title="📦 Phase 1: Data Preparation",
        padding=40,
        stroke_style="dashed"
    )
    diagram.add_to_back(group1_bbox)  # Add to BACK so elements are selectable
    
    # ==================== GROUP 2: VECTOR INDEXING ====================
    
    # Starting position for Group 2 (to the right of Group 1)
    group2_x = group1_x + 350
    group2_y = 150
    
    # DUPLICATE: Target BQ (Group 2's own copy - SAME COLOR as Group 1)
    target_bq_g2_pos = Position(x=group2_x, y=group2_y, width=250, height=100)
    target_bq_g2 = Box(
        pos=target_bq_g2_pos,
        text="💾 Target BQ Table\n\nhome_furniture products\n(product_id, metadata)",
        style=registry.get_style("target_bq")  # Purple - matches Group 1
    )
    diagram.add(target_bq_g2)
    
    # GO Job 1 (3048-dim)
    go_job1_pos = target_bq_g2_pos.below(spacing=80)
    go_job1_pos.width = 280
    go_job1_pos.height = 142
    go_job1 = Box(
        pos=go_job1_pos,
        text="🔧 GO Job 1\nproject: go-indexing-api\nimage-tag-vector-indexing\nReads: Target BQ\nCalls: ITSA (3048-dim)\nWrites: BQ (3048-dim RAW)",
        style=BoxStyle.default()
    )
    diagram.add(go_job1)
    
    # ITSA (Group 2)
    itsa_pos = go_job1_pos.right_of(spacing=200, align="center")
    itsa = Box(
        pos=itsa_pos,
        text="🎯 ITSA\n\n/v2/image-tag-vector\ntag_set=home_furniture_v1\napply_l2_norm=false",
        style=registry.get_style("itsa")  # Green - consistent across phases
    )
    diagram.add(itsa)
    
    # BQ 3048-dim
    bq_3048_pos = go_job1_pos.below(spacing=100)
    bq_3048 = Box(
        pos=bq_3048_pos,
        text="💾 BQ (3048-dim RAW)\n\nFull vectors stored",
        style=BoxStyle.default()
    )
    diagram.add(bq_3048)
    
    # GO Job 2 (Reduction)
    go_job2_pos = bq_3048_pos.below(spacing=80)
    go_job2 = Box(
        pos=go_job2_pos,
        text="🔧 GO Job 2 🆕\n📦 SEMAN-856 (TO-DO)\nproject: go-indexing-api\ndimension_reduction (NEW)\nCalls: Reduction API\nWrites: BQ (128-dim)",
        style=BoxStyle.default()
    )
    diagram.add(go_job2)
    
    # Reduction API
    reduction_api_pos = go_job2_pos.right_of(spacing=200, align="center")
    reduction_api = Box(
        pos=reduction_api_pos,
        text="⚙️ Reduction API\n🟡 SEMAN-855 (Ready)\n\n/v1/reduce/home_furniture_autoencoder/v1\ngRPC → Triton",
        style=BoxStyle.default()
    )
    diagram.add(reduction_api)
    
    # Triton
    triton_pos = reduction_api_pos.right_of(spacing=180, align="center")
    triton = Box(
        pos=triton_pos,
        text="🖥️ Triton Server\n✅ Deployed\n\nONNX Autoencoder\n3048 → 128",
        style=BoxStyle.default()
    )
    diagram.add(triton)
    
    # BQ 128-dim
    bq_128_pos = go_job2_pos.below(spacing=80)
    bq_128 = Box(
        pos=bq_128_pos,
        text="💾 BQ (128-dim)\n\nReduced vectors\n(Fits ES 1024-dim limit)",
        style=BoxStyle.default()
    )
    diagram.add(bq_128)
    
    # GO Job 3 (ES Indexing)
    go_job3_pos = bq_128_pos.below(spacing=80)
    go_job3 = Box(
        pos=go_job3_pos,
        text="🔧 GO Job 3\n⏳ Future\nproject:go-indexing-api\nimage-tag-vector-indexing\nReads: BQ (128-dim)\nIndexes: Elasticsearch",
        style=BoxStyle.default()
    )
    diagram.add(go_job3)
    
    # Elasticsearch (Group 2)
    es_pos = go_job3_pos.right_of(spacing=200, align="center")
    es = Box(
        pos=es_pos,
        text="🔍 Elasticsearch\n\n128-dim KNN index\n(Within 1024-dim limit)",
        style=registry.get_style("elasticsearch")  # Blue - consistent across phases
    )
    diagram.add(es)
    
    # Connect Group 2 elements
    arrow2 = diagram.connect(target_bq_g2, go_job1, label="① reads")
    arrow3 = diagram.connect(go_job1, itsa, label="② fetches 3048-dim")
    arrow4 = diagram.connect(itsa, go_job1, label="③ returns vectors")
    arrow5 = diagram.connect(go_job1, bq_3048, label="④ writes")
    arrow6 = diagram.connect(bq_3048, go_job2, label="⑤ reads")
    arrow7 = diagram.connect(go_job2, reduction_api, label="⑥ POST 3048-dim")
    arrow8 = diagram.connect(reduction_api, triton, label="⑦ gRPC")
    arrow9 = diagram.connect(triton, reduction_api, label="⑧ 128-dim")
    arrow10 = diagram.connect(reduction_api, go_job2, label="⑨ returns")
    arrow11 = diagram.connect(go_job2, bq_128, label="⑩ writes")
    arrow12 = diagram.connect(bq_128, go_job3, label="⑪ reads")
    arrow13 = diagram.connect(go_job3, es, label="⑫ indexes")
    
    # Group 2 Bounding Box (AUTOMATIC - wraps ONLY group 2 elements)
    group2_elements = [
        target_bq_g2, go_job1, itsa, bq_3048, go_job2, reduction_api, triton, bq_128, go_job3, es,
        arrow2, arrow3, arrow4, arrow5, arrow6, arrow7, arrow8, arrow9, arrow10, arrow11, arrow12, arrow13
    ]
    group2_bbox = diagram.create_bounding_box_for_elements(
        elements=group2_elements,
        title="🔄 Phase 2: Vector Indexing (3048 → 128 → ES)",
        padding=40,
        stroke_style="dashed"
    )
    diagram.add_to_back(group2_bbox)  # Add to BACK so elements are selectable
    
    # ==================== GROUP 3: RECOMMENDATION ====================
    
    # Starting position for Group 3 (below GO Job 3 - last element of Group 2)
    group3_x = group2_x
    group3_y = go_job3_pos.y + go_job3_pos.height + 150  # 150px spacing after Group 2
    
    # Metadata BQ
    metadata_bq_pos = Position(x=group3_x, y=group3_y, width=250, height=100)
    metadata_bq = Box(
        pos=metadata_bq_pos,
        text="💾 Product Metadata (BQ)\n\nProduct attributes for filtering",
        style=BoxStyle.default()
    )
    diagram.add(metadata_bq)
    
    # Reco Job
    reco_job_pos = metadata_bq_pos.below(spacing=80)
    reco_job = Box(
        pos=reco_job_pos,
        text="🔧 Reco Job\n✅ Existing\n\nproduct-recommendation\nExample: cross_reco_milla\nFinds 500 similar items",
        style=BoxStyle.default()
    )
    diagram.add(reco_job)
    
    # Vector Search API
    vector_search_pos = reco_job_pos.right_of(spacing=280, align="center")
    vector_search = Box(
        pos=vector_search_pos,
        text="🔎 Image Tag Vector Search API\n✅ Existing Service\n\n/search (128-dim KNN)\n1️⃣ Check ES first\n2️⃣ If not found → ITSA (fallback)\nFilters: Cross L3 categories",
        style=BoxStyle.default()
    )
    diagram.add(vector_search)
    
    # Similar Items BQ
    similar_items_pos = reco_job_pos.below(spacing=80)
    similar_items = Box(
        pos=similar_items_pos,
        text="💾 Similar Items (BQ)\n\n500 recommendations per\nproduct",
        style=BoxStyle.default()
    )
    diagram.add(similar_items)
    
    # DUPLICATE: Elasticsearch (Group 3's own copy - SAME COLOR as Group 2)
    es_g3_pos = vector_search_pos.right_of(spacing=200, align="center")
    es_g3 = Box(
        pos=es_g3_pos,
        text="🔍 Elasticsearch\n\n128-dim KNN index\n(Within 1024-dim limit)",
        style=registry.get_style("elasticsearch")  # Blue - matches Group 2
    )
    diagram.add(es_g3)
    
    # DUPLICATE: ITSA (Group 3's own copy - SAME COLOR as Group 2)
    itsa_g3_pos = es_g3_pos.below(spacing=100)
    itsa_g3 = Box(
        pos=itsa_g3_pos,
        text="🎯 ITSA\n\n/v2/image-tag-vector\ntag_set=home_furniture_v1\napply_l2_norm=false",
        style=registry.get_style("itsa")  # Green - matches Group 2
    )
    diagram.add(itsa_g3)
    
    # Connect Group 3 elements (ALL LOCAL - NO cross-group arrows!)
    arrow14 = diagram.connect(metadata_bq, reco_job, label="① reads")
    arrow15 = diagram.connect(reco_job, vector_search, label="② POST /search")
    arrow16 = diagram.connect(vector_search, es_g3, label="③ First: KNN query")
    arrow17 = diagram.connect(es_g3, vector_search, label="④ results (if found)")
    arrow18 = diagram.connect(vector_search, itsa_g3, label="⑤ Fallback: GET vector")
    arrow19 = diagram.connect(itsa_g3, vector_search, label="⑥ returns vector")
    arrow20 = diagram.connect(vector_search, reco_job, label="⑦ returns")
    arrow21 = diagram.connect(reco_job, similar_items, label="⑧ writes")
    
    # Group 3 Bounding Box (AUTOMATIC - ALL Group 3 elements, NO cross-group arrows!)
    group3_elements = [
        metadata_bq, reco_job, vector_search, similar_items, es_g3, itsa_g3,
        arrow14, arrow15, arrow16, arrow17, arrow18, arrow19, arrow20, arrow21
    ]
    group3_bbox = diagram.create_bounding_box_for_elements(
        elements=group3_elements,
        title="🎁 Phase 3: Recommendation Generation",
        padding=40,
        stroke_style="dashed"
    )
    diagram.add_to_back(group3_bbox)  # Add to BACK so elements are selectable
    
    # ==================== EXPORT ====================
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Save both formats
    file_path = output_dir / "home_furniture_grouped.excalidraw"
    clipboard_path = output_dir / "home_furniture_grouped_clipboard.json"
    
    diagram.save(str(file_path), clipboard_format=False)
    diagram.save(str(clipboard_path), clipboard_format=True)
    
    print(f"✅ Diagram saved to: {file_path} (file format)")
    print(f"✅ Diagram saved to: {clipboard_path} (clipboard format)")
    print(f"✅ Created diagram with {len(diagram.elements)} elements")
    print()
    print("📊 STRUCTURE (3 Independent Groups):")
    print("  ├─ Group 1: Data Preparation (2 boxes, 1 arrow)")
    print("  ├─ Group 2: Vector Indexing (10 boxes, 12 arrows)")
    print("  └─ Group 3: Recommendation (6 boxes, 8 arrows)")
    print()
    print("✨ FEATURES:")
    print("  ✅ Auto-calculated bounding boxes (perfect fit!)")
    print("  ✅ Elements inside boxes are fully selectable")
    print("  ✅ NO cross-group arrows - fully self-contained!")
    print("  ✅ Duplicate items have matching colors:")
    print("      • Target BQ = purple (Group 1 & 2)")
    print("      • ITSA = green (Group 2 & 3)")
    print("      • Elasticsearch = blue (Group 2 & 3)")
    print("  ✅ Arrow numbering resets per phase (①②③...)")
    print("  ✅ Clean separation - no overlapping")
    print()
    print("💾 Output:")
    print(f"  • {file_path.name} (file format)")
    print(f"  • {clipboard_path.name} (clipboard format)")


if __name__ == "__main__":
    main()
