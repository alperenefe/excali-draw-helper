"""
Example: Home Furniture Cross Recommendation Flow
with Dimension Reduction (3048-dim → 128-dim)
"""

from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Text,
    Circle,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_home_furniture_diagram():
    """Create the complete home furniture flow diagram."""
    
    diagram = ExcalidrawDiagram("Home Furniture Cross Reco Flow")
    
    # ========================================================================
    # TITLE
    # ========================================================================
    diagram.add(Text(
        pos=Position(x=400, y=-300, width=1200, height=80),
        text="Home Furniture - Cross Recommendation Flow\nwith Dimension Reduction (3048-dim → 128-dim)",
        font_size=48,
        align="center"
    ))
    
    # ========================================================================
    # PHASE 1: DATA PREPARATION
    # ========================================================================
    
    # Source BQ Tables
    source_bq = Box(
        pos=Position(x=300, y=500, width=350, height=120),
        text="Source BQ Tables\n(product_content_tr, category_hierarchy,\ncvnlp_country_mapping)",
        style=BoxStyle.default()
    )
    
    # BQ Script
    bq_script = Box(
        pos=Position(x=250, y=100, width=230, height=230),
        text="BQ Scheduled Script\n\nFilters home_furniture products\nwrites to target BQ\nwith metadata",
        style=BoxStyle.default()
    )
    
    # Target BQ
    target_bq = Box(
        pos=Position(x=750, y=150, width=250, height=100),
        text="Target BQ\nprod_image_tag_vector_indexing_hf",
        style=BoxStyle.default()
    )
    
    diagram.add([source_bq, bq_script, target_bq])
    
    # Step circles
    diagram.add([
        Circle(pos=Position(x=500, y=380, width=30, height=40), text="1", color=Color.PURPLE_LIGHT),
        Circle(pos=Position(x=630, y=150, width=30, height=40), text="2", color=Color.PURPLE_LIGHT),
    ])
    
    # ========================================================================
    # PHASE 2: VECTOR INDEXING - Job 1 (3048-dim Generation)
    # ========================================================================
    
    # GO Indexing API - Job 1
    go_job1 = Box(
        pos=Position(x=1100, y=100, width=280, height=200),
        text="GO Indexing API\nJob 1: vector_generation_job\n\nReads: Target BQ\nCalls: ITSA (/v2/image-tag-vector)\n  tag_set=home_furniture_v1\n  apply_l2_norm=false\nWrites: BQ (3048-dim RAW)",
        style=BoxStyle.success(bold=True)
    )
    
    # ITSA
    itsa = Box(
        pos=Position(x=1170, y=365, width=180, height=160),
        text="Image Tag Similarity API\n\n/v2/image-tag-vector\n(3048-dim RAW)\n\nOR\n\n/v2/image-tag-reduced-vector\n(128-dim)",
        style=BoxStyle.info()
    )
    
    # BQ 3048-dim table
    bq_3048 = Box(
        pos=Position(x=1500, y=150, width=200, height=100),
        text="BQ\nprod_image_tag_vector_hf_3048_raw",
        style=BoxStyle.data_source()
    )
    
    diagram.add([go_job1, itsa, bq_3048])
    
    # Step circles
    diagram.add([
        Circle(pos=Position(x=1036, y=130, width=30, height=40), text="1", color=Color.GREEN_LIGHT),
        Circle(pos=Position(x=1127, y=330, width=30, height=40), text="2", color=Color.GREEN_LIGHT),
        Circle(pos=Position(x=1311, y=270, width=30, height=40), text="3", color=Color.GREEN_LIGHT),
        Circle(pos=Position(x=1377, y=122, width=30, height=40), text="4", color=Color.GREEN_LIGHT),
    ])
    
    # ========================================================================
    # PHASE 2: VECTOR INDEXING - Job 2 (Dimension Reduction) 🆕 NEW!
    # ========================================================================
    
    # GO Indexing API - Job 2
    go_job2 = Box(
        pos=Position(x=1450, y=350, width=300, height=220),
        text="GO Indexing API 🆕\nJob 2: dimension_reduction_job\n\nReads: BQ (3048-dim)\nCalls: Reduction API\n  /v1/reduce?version=hf_v1\n  → Triton gRPC (ONNX)\n    home_furniture_autoencoder\nWrites: BQ (128-dim)",
        style=BoxStyle.warning(bold=True)
    )
    
    # Reduction API
    reduction_api = Box(
        pos=Position(x=1850, y=400, width=240, height=140),
        text="Dimension Reduction API 🆕\n\n/v1/reduce?version=hf_v1\n\nInput: 3048-dim\nTriton gRPC → ONNX\nOutput: 128-dim",
        style=BoxStyle.warning()
    )
    
    # Triton
    triton = Box(
        pos=Position(x=2130, y=430, width=180, height=80),
        text="Triton Inference Server 🆕\n\nModel: home_furniture_autoencoder\n(ONNX)",
        style=BoxStyle.warning()
    )
    
    # BQ 128-dim table
    bq_128 = Box(
        pos=Position(x=1500, y=650, width=200, height=100),
        text="BQ\nprod_image_tag_vector_hf_128_reduced",
        style=BoxStyle.data_source()
    )
    
    diagram.add([go_job2, reduction_api, triton, bq_128])
    
    # Step circles
    diagram.add([
        Circle(pos=Position(x=1520, y=435, width=30, height=40), text="5", color=Color.ORANGE_LIGHT),
        Circle(pos=Position(x=1830, y=455, width=30, height=40), text="6", color=Color.ORANGE_LIGHT),
        Circle(pos=Position(x=1520, y=655, width=30, height=40), text="7", color=Color.ORANGE_MID),
    ])
    
    # ========================================================================
    # PHASE 2: VECTOR INDEXING - Job 3 (ES Indexing)
    # ========================================================================
    
    # GO Indexing API - Job 3
    go_job3 = Box(
        pos=Position(x=1800, y=600, width=280, height=180),
        text="GO Indexing API\nJob 3: es_indexing_job\n\nReads: BQ (128-dim)\nIndexes to: Elasticsearch\n  (128-dim KNN)",
        style=BoxStyle.success(bold=True)
    )
    
    # Elasticsearch
    elasticsearch = Box(
        pos=Position(x=2150, y=150, width=200, height=100),
        text="Elasticsearch\n\nimage_tag_vectors_hf_128",
        style=BoxStyle.data_source()
    )
    
    diagram.add([go_job3, elasticsearch])
    
    # Step circles
    diagram.add([
        Circle(pos=Position(x=1820, y=675, width=30, height=40), text="8", color=Color.GREEN_LIGHT),
        Circle(pos=Position(x=1768, y=142, width=30, height=40), text="9", color=Color.GREEN_LIGHT),
    ])
    
    # ========================================================================
    # PHASE 3: RECOMMENDATION JOB
    # ========================================================================
    
    # Vector Search API
    vector_search = Box(
        pos=Position(x=1300, y=900, width=250, height=130),
        text="Image Tag Vector Search API\n\n/search (128-dim KNN)\nFilters: Cross L3 categories",
        style=BoxStyle.error()
    )
    
    # Recommendation Job
    reco_job = Box(
        pos=Position(x=1300, y=1150, width=250, height=200),
        text="GO Indexing API\nJob 4: product_recommendation_job\n(Cross Reco)\n\nRecords 500 similar items\nfor all home_furniture products\nto BQ (cross recommendation)",
        style=BoxStyle.error(bold=True)
    )
    
    # Results BQ
    results_bq = Box(
        pos=Position(x=1700, y=940, width=200, height=100),
        text="BQ\nprod_recommendations_hf_cross",
        style=BoxStyle.error()
    )
    
    diagram.add([vector_search, reco_job, results_bq])
    
    # Step circles
    diagram.add([
        Circle(pos=Position(x=1093, y=666, width=30, height=40), text="1", color=Color.RED_LIGHT),
        Circle(pos=Position(x=1252, y=751, width=30, height=40), text="2", color=Color.RED_LIGHT),
        Circle(pos=Position(x=1249, y=535, width=30, height=40), text="3", color=Color.RED_LIGHT),
        Circle(pos=Position(x=1333, y=505, width=30, height=40), text="4", color=Color.RED_LIGHT),
        Circle(pos=Position(x=1311, y=950, width=30, height=40), text="10", color=Color.RED_LIGHT),
        Circle(pos=Position(x=1547, y=790, width=30, height=40), text="7", color=Color.RED_LIGHT),
        Circle(pos=Position(x=1588, y=923, width=30, height=40), text="8", color=Color.RED_LIGHT),
    ])
    
    # ========================================================================
    # INFO BOXES
    # ========================================================================
    
    diagram.add(Text(
        pos=Position(x=1800, y=200, width=450, height=180),
        text="🆕 DIMENSION REDUCTION DETAILS:\n\n" +
             "• Model: home_furniture_autoencoder v1\n" +
             "• Input: 3048-dim (RAW scores, no L2 norm)\n" +
             "• Output: 128-dim\n" +
             "• Why? Reduce storage, faster ES queries\n\n" +
             "📦 NEW COMPONENTS:\n" +
             "• Triton Server (SEMAN-854)\n" +
             "• Dimension Reduction API (SEMAN-855)\n" +
             "• go-indexing-api jobs (SEMAN-856)\n" +
             "• ITSA /v2/image-tag-reduced-vector (SEMAN-857)",
        font_size=13,
        color=Color.ORANGE_DARK
    ))
    
    diagram.add(Text(
        pos=Position(x=1925, y=71, width=600, height=60),
        text="Notlar:\n" +
             "• Memory şişmesin diye lazy loading yapıyoruz (page iterator)\n" +
             "• 3048-dim → 128-dim reduction autoencoder ile yapılıyor",
        font_size=14,
        color=Color.BLACK
    ))
    
    # ========================================================================
    # CONNECTIONS (ARROWS)
    # ========================================================================
    
    # Phase 1: Data Preparation
    diagram.connect(bq_script, source_bq, label="reads")
    diagram.connect(bq_script, target_bq, label="writes")
    
    # Phase 2.1: Vector Generation (3048-dim)
    diagram.connect(target_bq, go_job1, label="reads contents")
    diagram.connect(go_job1, itsa, label="tag_set: home_furniture_v1\nimg_url: xyz\napply_l2_norm: false")
    diagram.connect(itsa, go_job1, label="response\n(3048-dim vector)")
    diagram.connect(go_job1, bq_3048, label="writes\n(3048-dim RAW)")
    
    # Phase 2.2: Dimension Reduction (128-dim) 🆕
    diagram.connect(bq_3048, go_job2, style=ArrowStyle.warning(bold=True))
    diagram.connect(go_job2, reduction_api, style=ArrowStyle.warning())
    diagram.connect(reduction_api, triton, style=ArrowStyle.warning())
    diagram.connect(go_job2, bq_128, label="writes\n(128-dim)", style=ArrowStyle.warning(bold=True))
    
    # Phase 2.3: ES Indexing
    diagram.connect(bq_128, go_job3, label="reads\n(128-dim)", style=ArrowStyle.success())
    diagram.connect(go_job3, elasticsearch, style=ArrowStyle.success())
    
    # Phase 3: Recommendation
    diagram.connect(reco_job, vector_search, label="request with\nimg_url + filters\n(128-dim)", style=ArrowStyle.error())
    diagram.connect(vector_search, reco_job, label="similar items\n(128-dim based)", style=ArrowStyle.error())
    diagram.connect(vector_search, itsa, style=ArrowStyle.error())
    diagram.connect(itsa, vector_search, style=ArrowStyle.error())
    diagram.connect(elasticsearch, vector_search, style=ArrowStyle.error())
    diagram.connect(vector_search, elasticsearch, style=ArrowStyle.error())
    diagram.connect(reco_job, results_bq, style=ArrowStyle.error())
    diagram.connect(reco_job, target_bq, label="reads content data")
    
    return diagram


if __name__ == "__main__":
    diagram = create_home_furniture_diagram()
    diagram.save("output/home_furniture_cross_reco_flow.excalidraw")
    print(f"✅ Created diagram with {len(diagram.elements)} elements")
