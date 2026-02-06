"""
Home Furniture Cross Recommendation Flow
with Dimension Reduction (3048-dim → 128-dim)
FINAL VERSION
"""

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Text,
    Arrow,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_home_furniture_final():
    """Create the complete home furniture flow with dimension reduction."""
    
    diagram = ExcalidrawDiagram("Home Furniture - Dimension Reduction Flow")
    
    # ========================================================================
    # TITLE
    # ========================================================================
    diagram.add(Text(
        pos=Position(x=400, y=-250, width=1400, height=80),
        text="Home Furniture - Cross Recommendation Flow\nwith Dimension Reduction (3048-dim → 128-dim)",
        font_size=48,
        align="center",
        font_family=6
    ))
    
    diagram.add(Text(
        pos=Position(x=450, y=-120, width=1300, height=50),
        text="Goal: Reduce vector size (3048→128) to overcome Elasticsearch 1024-dim limit",
        font_size=24,
        align="center",
        color=Color.ORANGE_DARK,
        font_family=6
    ))
    
    # ========================================================================
    # PHASE 1: DATA PREPARATION
    # ========================================================================
    
    # Source BQ Tables
    source_bq = Box(
        pos=Position(x=250, y=100, width=350, height=120),
        text="📊 Source BQ Tables\n(product_content_tr,\ncategory_hierarchy,\ncvnlp_country_mapping)",
        style=BoxStyle.default()  # Transparent background
    )
    
    # BQ Script
    bq_script_pos = source_bq.pos.below(spacing=80)
    bq_script = Box(
        pos=bq_script_pos,
        text="📝 BQ Scheduled Script\n\nFilters home_furniture products\nwrites to target BQ",
        style=BoxStyle.default()  # Transparent background
    )
    
    # Target BQ
    target_bq_pos = bq_script_pos.right_of(spacing=250)
    target_bq = Box(
        pos=target_bq_pos,
        text="📊 Target BQ\nprod_image_tag_vector_indexing_hf",
        style=BoxStyle.default()  # Transparent background
    )
    
    diagram.add([source_bq, bq_script, target_bq])
    
    # ========================================================================
    # PHASE 2: VECTOR GENERATION (3048-dim)
    # ========================================================================
    
    # GO Indexing API - Job 1
    # Increased spacing for long arrow labels (④ has long parameters)
    go_job1_pos = target_bq_pos.right_of(spacing=300, align="center")
    go_job1 = Box(
        pos=go_job1_pos,
        text="🔧 GO Indexing API\n✅ Existing Job (Implemented)\n\nJob Type: image-tag-vector-indexing\nNote: Multiple jobs (milla/core/cee)\n      but ALL use home_furniture tag set\n\nReads: Target BQ\nCalls: ITSA\n  tag_set=home_furniture_v1\n  apply_l2_norm=false\nWrites: BQ (3048-dim RAW)",
        style=BoxStyle.default()  # Transparent
    )
    
    # ITSA (spacing proportional to go_job1 height)
    itsa_spacing = int(go_job1_pos.height * 1.8)  # 1.8x of box height for better visual spacing
    itsa_pos = go_job1_pos.below(spacing=itsa_spacing)
    itsa = Box(
        pos=itsa_pos,
        text="🎯 Image Tag Similarity API\n📦 SEMAN-857 (Ready for Release)\n\n/v2/image-tag-vector\n(3048-dim RAW)\n\nOR\n\n/v2/image-tag-vector?dense_vector_size=128\n(128-dim reduced)",
        style=BoxStyle.default()  # Transparent
    )
    
    # BQ 3048-dim table
    bq_3048_pos = go_job1_pos.right_of(spacing=250)
    bq_3048 = Box(
        pos=bq_3048_pos,
        text="📊 BQ\nprod_image_tag_vector_hf_3048_raw",
        style=BoxStyle.default()  # Transparent
    )
    
    diagram.add([go_job1, itsa, bq_3048])
    
    # ========================================================================
    # PHASE 2.2: DIMENSION REDUCTION (3048→128) 🆕
    # ========================================================================
    
    # GO Indexing API - Job 2 (Reduction)
    go_job2_pos = bq_3048_pos.below(spacing=150)
    go_job2 = Box(
        pos=go_job2_pos,
        text="🔧 GO Indexing API 🆕\n📦 SEMAN-856 (TO-DO)\n\nJob Type: dimension_reduction\n\nReads: Target BQ (product IDs)\nCalls: ITSA\n  /v2/image-tag-vector\n  dense_vector_size=128\n  → Reduction API → Triton\nWrites: BQ (128-dim)",
        style=BoxStyle.default()  # Transparent
    )
    
    # Reduction API
    reduction_api_pos = go_job2_pos.right_of(spacing=280)
    reduction_api = Box(
        pos=reduction_api_pos,
        text="⚙️ Dimension Reduction API\n📦 SEMAN-855 (DONE)\n\n/v1/reduce/home_furniture_autoencoder/v1\n\nInput: 3048-dim\nTriton gRPC → ONNX\nOutput: 128-dim",
        style=BoxStyle.default()  # Transparent
    )
    
    # Triton
    triton_pos = reduction_api_pos.right_of(spacing=250)
    triton = Box(
        pos=triton_pos,
        text="🔥 Triton Server\n📦 SEMAN-854 (DONE)\n\nModel:\nhome_furniture_autoencoder\n(ONNX)",
        style=BoxStyle.default()  # Transparent
    )
    
    # BQ 128-dim table
    bq_128_pos = go_job2_pos.below(spacing=120)
    bq_128 = Box(
        pos=bq_128_pos,
        text="📊 BQ\nprod_image_tag_vector_hf_128_reduced",
        style=BoxStyle.default()  # Transparent
    )
    
    diagram.add([go_job2, reduction_api, triton, bq_128])
    
    # ========================================================================
    # PHASE 2.3: ES INDEXING
    # ========================================================================
    
    # GO Indexing API - Job 3 (ES)
    go_job3_pos = bq_128_pos.right_of(spacing=280, align="center")
    go_job3 = Box(
        pos=go_job3_pos,
        text="🔧 GO Indexing API\n⏳ Future (After SEMAN-856)\n\nJob Type: image-tag-vector-indexing\nNote: Same jobs as Phase 2.1\n      but with 128-dim input\n\nReads: BQ (128-dim)\nIndexes to: Elasticsearch\n  (128-dim KNN)",
        style=BoxStyle.default()  # Transparent
    )
    
    # Elasticsearch
    elasticsearch_pos = go_job3_pos.right_of(spacing=280)
    elasticsearch = Box(
        pos=elasticsearch_pos,
        text="🔍 Elasticsearch\n\nimage_tag_vectors_hf_128\n(KNN Index)",
        style=BoxStyle.default()  # Transparent
    )
    
    diagram.add([go_job3, elasticsearch])
    
    # ========================================================================
    # PHASE 3: RECOMMENDATION JOB
    # ========================================================================
    
    # Vector Search API
    vector_search_pos = Position(x=go_job3_pos.x - 100, y=go_job3_pos.y + 250, 
                                  width=280, height=140)
    vector_search = Box(
        pos=vector_search_pos,
        text="🔎 Image Tag Vector Search API\n✅ Existing Service\n\n/search (128-dim KNN)\nFilters: Cross L3 categories",
        style=BoxStyle.default()  # Transparent
    )
    
    # Recommendation Job
    reco_job_pos = vector_search_pos.below(spacing=100)
    reco_job = Box(
        pos=reco_job_pos,
        text="🔧 GO Indexing API\n✅ Existing Job (Implemented)\n\nJob Type: product-recommendation\nExample: cross_reco_milla\n\nReads: Product metadata (BQ)\nCalls: Vector Search API\nWrites: 500 similar items to BQ",
        style=BoxStyle.default()  # Transparent
    )
    
    # Results BQ
    results_bq_pos = vector_search_pos.right_of(spacing=280)
    results_bq = Box(
        pos=results_bq_pos,
        text="📊 BQ\nprod_recommendations_hf_cross",
        style=BoxStyle.default()  # Transparent
    )
    
    diagram.add([vector_search, reco_job, results_bq])
    
    # ========================================================================
    # INFO BOXES
    # ========================================================================
    
    # Dimension Reduction Info
    info_box_pos = Position(x=triton_pos.x + 300, y=go_job1_pos.y, width=480, height=360)
    diagram.add(Text(
        pos=info_box_pos,
        text="🆕 DIMENSION REDUCTION DETAILS:\n\n" +
             "• Model: home_furniture_autoencoder v1\n" +
             "• Input: 3048-dim (RAW scores, no L2 norm)\n" +
             "• Output: 128-dim\n" +
             "• Method: Autoencoder via Triton (gRPC)\n" +
             "• Why? Overcome ES 1024-dim limit\n\n" +
             "📦 JIRA TASKS:\n" +
             "✅ SEMAN-854: Triton Server (DONE)\n" +
             "✅ SEMAN-855: Reduction API (DONE)\n" +
             "🟡 SEMAN-857: ITSA Endpoint (Ready for Release)\n" +
             "   → /v2/image-tag-vector?tag_set=X&dense_vector_size=128\n" +
             "❌ SEMAN-856: GO Jobs (TO-DO)\n" +
             "   → dimension_reduction job type\n\n" +
             "🎯 CURRENT STATUS:\n" +
             "Infrastructure ready, waiting for GO job implementation",
        font_size=12,
        color=Color.ORANGE_DARK,
        align="left",
        font_family=6
    ))
    
    # Notes
    notes_pos = Position(x=info_box_pos.x, y=info_box_pos.y + 380, width=480, height=120)
    diagram.add(Text(
        pos=notes_pos,
        text="📝 NOTES:\n" +
             "• ES Limitation: Max 1024-dim for dense_vector field\n" +
             "• home_furniture tags: 3048-dim (exceeds ES limit)\n" +
             "• Solution: Autoencoder reduces 3048 → 128 dims\n" +
             "• RAW scores: no L2 normalization before reduction\n" +
             "• Memory-efficient: lazy loading (page iterator)\n" +
             "• Delta updates: only changed/new products",
        font_size=12,
        color=Color.BLACK,
        align="left",
        font_family=6
    ))
    
    # ========================================================================
    # GITLAB LINKS (on top of relevant boxes)
    # ========================================================================
    
    # Helper function to add link above a box
    def add_link_above_box(box_pos, label, url, offset_y=-35):
        link = Text(
            pos=Position(x=box_pos.x, y=box_pos.y + offset_y, width=250, height=20),
            text=f"🔗 {label}",
            font_size=11,
            color=Color.ORANGE_DARK,
            align="left",
            font_family=6
        )
        link.link = url
        diagram.add(link)
    
    # Add links above relevant boxes (all project components)
    add_link_above_box(go_job1_pos, "GO Indexing API", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/go-indexing-api")
    add_link_above_box(itsa_pos, "ITSA", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/image-tag-similarity-api")
    add_link_above_box(go_job2_pos, "GO Indexing API", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/go-indexing-api")
    add_link_above_box(reduction_api_pos, "Reduction API", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/dimension-reduction-api")
    add_link_above_box(triton_pos, "Home Furniture Autoencoder", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/piper/home-furniture-autoencoder-v1")
    add_link_above_box(go_job3_pos, "GO Indexing API", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/go-indexing-api")
    add_link_above_box(vector_search_pos, "Vector Search API", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/image-tag-vector-search-api")
    add_link_above_box(reco_job_pos, "GO Indexing API (Reco Job)", 
                       "https://gitlab.trendyol.com/discovery/search-intelligence/apis/go-indexing-api")
    
    # ========================================================================
    # CONNECTIONS (ARROWS) + CIRCLES ON MIDPOINTS
    # ========================================================================
    
    # Phase 1: Data Preparation
    diagram.connect(source_bq, bq_script, label="① reads product data\n(home_furniture filter)", style=ArrowStyle.default())
    diagram.connect(bq_script, target_bq, label="② writes filtered products", style=ArrowStyle.default())
    
    # Phase 2.1: Vector Generation (3048-dim)
    diagram.connect(target_bq, go_job1, label="③ reads filtered products", style=ArrowStyle.success())
    diagram.connect(go_job1, itsa, label="④ POST /v2/image-tag-vector\ntag_set=home_furniture_v1\napply_l2_norm=false", 
                    style=ArrowStyle.success())
    diagram.connect(itsa, go_job1, label="⑤ 3048-dim RAW vector\n(no normalization)", style=ArrowStyle.success())
    diagram.connect(go_job1, bq_3048, label="⑥ writes 3048-dim RAW vectors", style=ArrowStyle.success())
    
    # Phase 2.2: Dimension Reduction (128-dim) 🆕
    diagram.connect(bq_3048, go_job2, label="⑦ reads product IDs\n(not vectors)", style=ArrowStyle.warning(bold=True))
    diagram.connect(go_job2, itsa, label="⑧ POST /v2/image-tag-vector\ndense_vector_size=128", style=ArrowStyle.warning())
    diagram.connect(itsa, reduction_api, label="⑨ POST /v1/reduce/home_furniture_autoencoder/v1\n(3048-dim input array)", style=ArrowStyle.warning())
    diagram.connect(reduction_api, triton, label="⑩ gRPC: 3048-dim array\n→ ONNX autoencoder", style=ArrowStyle.warning())
    diagram.connect(triton, reduction_api, label="⑪ 128-dim embedding\n(model output)", style=ArrowStyle.warning())
    diagram.connect(reduction_api, itsa, label="⑫ 128-dim vector", style=ArrowStyle.warning())
    diagram.connect(itsa, go_job2, label="⑬ 128-dim reduced vector\n(in scores field)", style=ArrowStyle.warning())
    diagram.connect(go_job2, bq_128, label="⑭ writes 128-dim reduced vectors", style=ArrowStyle.warning(bold=True))
    
    # Phase 2.3: ES Indexing
    diagram.connect(bq_128, go_job3, label="⑮ reads 128-dim reduced vectors", style=ArrowStyle.success())
    diagram.connect(go_job3, elasticsearch, label="⑯ indexes to KNN field\n(128-dim dense_vector)", style=ArrowStyle.success())
    
    # Phase 3: Recommendation
    diagram.connect(reco_job, target_bq, label="⑰ reads product metadata\n(titles, images, etc.)", style=ArrowStyle.default())
    diagram.connect(reco_job, vector_search, label="⑱ POST /search\n(128-dim query vector)", style=ArrowStyle.error())
    diagram.connect(vector_search, elasticsearch, label="⑲ KNN search query\n(cosine similarity)", style=ArrowStyle.error())
    diagram.connect(elasticsearch, vector_search, label="⑳ top-K similar items\n(product IDs + scores)", style=ArrowStyle.error())
    diagram.connect(vector_search, itsa, label="㉑ enrich with\nimage URLs", style=ArrowStyle.error())
    diagram.connect(itsa, vector_search, label="㉒ image metadata", style=ArrowStyle.error())
    diagram.connect(vector_search, reco_job, label="㉓ 500 similar items\n(enriched)", style=ArrowStyle.error())
    diagram.connect(reco_job, results_bq, label="㉔ writes recommendations", style=ArrowStyle.error())
    
    return diagram


if __name__ == "__main__":
    diagram = create_home_furniture_final()
    
    # Save in both formats
    diagram.save("output/home_furniture_final.excalidraw")
    diagram.save("output/home_furniture_final_clipboard.json", clipboard_format=True)
    
    print(f"✅ Created diagram with {len(diagram.elements)} elements")
    print("\n📊 PHASES:")
    print("  Phase 1: Data Preparation (2 boxes)")
    print("  Phase 2.1: Vector Generation - 3048-dim (3 boxes)")
    print("  Phase 2.2: Dimension Reduction - 128-dim 🆕 (4 boxes)")
    print("  Phase 2.3: ES Indexing (2 boxes)")
    print("  Phase 3: Recommendation Job (3 boxes)")
    print("\n🎯 Key Components:")
    print("  • Triton Server (ONNX autoencoder)")
    print("  • Dimension Reduction API (gRPC wrapper)")
    print("  • 3 GO Indexing API jobs")
    print("  • ITSA with /v2/image-tag-reduced-vector")
    print("\n💾 Output:")
    print("  • home_furniture_final.excalidraw (file format)")
    print("  • home_furniture_final_clipboard.json (clipboard format)")
