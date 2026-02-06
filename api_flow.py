from excalidraw_builder import (
    ExcalidrawDiagram,
    Box,
    Position,
    BoxStyle,
    ArrowStyle,
    Color,
)


def create_api_flow_diagram():
    """Mobile BFF'den Triton'a kadar API akışı"""
    
    diagram = ExcalidrawDiagram("API Flow: Mobile BFF → Triton")
    
    # ========================================================================
    # SERVICES
    # ========================================================================
    
    # 1. Mobile BFF (Client)
    mobile_bff = Box(
        pos=Position(x=100, y=100, width=250, height=120),
        text="Mobile BFF\n(Media Center)",
        style=BoxStyle(
            stroke_color="#6741d9",
            background_color="#e5dbff",
            stroke_width=3
        )
    )
    
    # 2. Image Search Service
    image_search = Box(
        pos=Position(x=100, y=300, width=250, height=140),
        text="Image Search Service\n\n(Media Center Team)\n\nCalls Triton for embedding\n+ ES for similar products",
        style=BoxStyle(
            stroke_color=Color.GREEN_DARK,
            background_color=Color.GREEN_PALE,
            stroke_width=2
        )
    )
    
    # 2b. Triton - Image Embedding
    triton_embedding = Box(
        pos=Position(x=450, y=300, width=220, height=100),
        text="Triton\n(Image Embedding Model)\n\n(SCR trained)",
        style=BoxStyle(
            stroke_color=Color.RED_DARK,
            background_color=Color.RED_PALE,
            stroke_width=2
        )
    )
    
    # 3. Search Fusion API
    search_fusion = Box(
        pos=Position(x=100, y=520, width=250, height=120),
        text="Search Fusion API\n(Search Deep)\n\n(Search Fusion Team)\n\nPagination: 20'şer ürün",
        style=BoxStyle(
            stroke_color=Color.BLUE_DARK,
            background_color=Color.BLUE_LIGHT,
            stroke_width=2
        )
    )
    
    # 4. Search API
    search_api = Box(
        pos=Position(x=100, y=720, width=250, height=100),
        text="Search API\n\n(Search Core Team)",
        style=BoxStyle(
            stroke_color=Color.BLUE_DARK,
            background_color=Color.BLUE_PALE,
            stroke_width=2
        )
    )
    
    # 5. Rerank API (A/B Test)
    rerank_api = Box(
        pos=Position(x=100, y=900, width=250, height=120),
        text="Rerank API\n(Currently in A/B)\n\n(Relevance Team)",
        style=BoxStyle(
            stroke_color=Color.ORANGE_DARK,
            background_color=Color.ORANGE_LIGHT,
            stroke_width=3
        )
    )
    
    # 6. Triton - Rerank Model
    triton_rerank = Box(
        pos=Position(x=450, y=900, width=220, height=100),
        text="Triton\n(Rerank Model)\n\n(SCR trained)",
        style=BoxStyle(
            stroke_color=Color.RED_DARK,
            background_color=Color.RED_LIGHT,
            stroke_width=2
        )
    )
    
    # Add all services at once
    diagram.add([mobile_bff, image_search, triton_embedding, search_fusion, search_api, rerank_api, triton_rerank])
    
    # ========================================================================
    # CONNECTIONS
    # ========================================================================
    
    # 1. Mobile BFF → Image Search Service (ONLY FIRST PAGE)
    diagram.connect(
        mobile_bff, image_search,
        label="1. Search Request\n(FIRST PAGE ONLY)",
        style=ArrowStyle(stroke_color=Color.PURPLE_MID, stroke_width=3)
    )
    
    # 2. Image Search Service ↔ Triton Embedding
    diagram.connect(
        image_search, triton_embedding,
        label="2. Get embedding",
        style=ArrowStyle(stroke_color=Color.RED_DARK, stroke_width=2)
    )
    diagram.connect(
        triton_embedding, image_search,
        label="Return embedding",
        style=ArrowStyle(stroke_color=Color.RED_DARK, stroke_width=2)
    )
    
    # 3. Image Search Service → Search Fusion API
    diagram.connect(
        image_search, search_fusion,
        label="3. 100 ürün\n(crops + similar)",
        style=ArrowStyle(stroke_color=Color.BLACK, stroke_width=3)
    )
    
    # 4. Mobile BFF → Search Fusion (NEXT PAGES)
    diagram.connect(
        mobile_bff, search_fusion,
        label="4. Next Pages\n(PAGE 2, 3, 4, 5...)\n(skips Media Center)",
        style=ArrowStyle(stroke_color=Color.BLUE_DARK, stroke_width=3)
    )
    
    # 5. Search Fusion API → Search API
    diagram.connect(
        search_fusion, search_api,
        label="5. 20 ürün per page",
        style=ArrowStyle(stroke_color=Color.BLACK, stroke_width=2)
    )
    
    # 6. Search API → Rerank API
    diagram.connect(
        search_api, rerank_api,
        label="6. Send for Reranking\n(A/B Test)",
        style=ArrowStyle(stroke_color=Color.ORANGE_DARK, stroke_width=3)
    )
    
    # 7. Rerank API ↔ Triton Rerank
    diagram.connect(
        rerank_api, triton_rerank,
        label="7. Rerank request",
        style=ArrowStyle(stroke_color=Color.RED_DARK, stroke_width=2)
    )
    diagram.connect(
        triton_rerank, rerank_api,
        label="Return reranked",
        style=ArrowStyle(stroke_color=Color.RED_DARK, stroke_width=2)
    )
    
    # ========================================================================
    # ANNOTATIONS
    # ========================================================================
    
    # Notes
    notes = Box(
        pos=Position(x=450, y=520, width=300, height=200),
        text="📝 FLOW NOTES:\n\n" +
             "🟣 FIRST PAGE (Page 1):\n" +
             "  Mobile BFF → Media Center\n" +
             "  → 100 products → Fusion\n" +
             "  → 20 products returned\n\n" +
             "🔵 NEXT PAGES (Page 2-5):\n" +
             "  Mobile BFF → Fusion DIRECTLY\n" +
             "  (skips Media Center!)\n" +
             "  → 20 products returned\n\n" +
             "• Total: 100 products (5 pages)",
        style=BoxStyle(
            stroke_color=Color.BLUE_DARK,
            background_color=Color.BLUE_PALE,
            stroke_width=2
        )
    )
    
    # A/B Test Note
    ab_note = Box(
        pos=Position(x=100, y=1100, width=250, height=60),
        text="⚠️ A/B Test\nCurrently rolling out",
        style=BoxStyle(
            stroke_color=Color.ORANGE_DARK,
            background_color=Color.YELLOW_LIGHT,
            stroke_width=2
        )
    )
    diagram.add([notes, ab_note])
    
    return diagram


if __name__ == "__main__":
    diagram = create_api_flow_diagram()
    diagram.save("output/api_flow.excalidraw")
    print(f"✅ API Flow diagram created with {len(diagram.elements)} elements")
    print(f"📁 Saved to: output/api_flow.excalidraw")
