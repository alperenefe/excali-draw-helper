#!/usr/bin/env python3
"""
Home Furniture Vector Pipeline - CURRENT STATE
Shows what exists vs what's missing compared to Fashion flow
"""
import sys
sys.path.insert(0, '/Users/alperen.uretmen/excalidraw-diagram-builder')

from excalidraw_builder import (
    ExcalidrawDiagram, Box, Text, Position,
    BoxStyle, ArrowStyle, Color
)

diagram = ExcalidrawDiagram("Home Furniture Current State")

# Title
diagram.add(Text(
    pos=Position(x=500, y=50, width=1400, height=80),
    text="Home Furniture: Vector Pipeline - CURRENT STATE vs NEEDED",
    font_size=58,
    align="center",
    color=Color.BLACK
))

# Subtitle
diagram.add(Text(
    pos=Position(x=500, y=150, width=1000, height=40),
    text='Goal: Same pattern as Fashion (categories, genders, finger_print, etc.)',
    font_size=20,
    align="center",
    color=Color.ORANGE_DARK
))

# ============= PHASE 1: TAGGING (SEMAN-856) ✅ =============
diagram.add(Text(
    pos=Position(x=100, y=250, width=450, height=30),
    text="PHASE 1: Tagging (SEMAN-856) ✅",
    font_size=24,
    align="left",
    color=Color.GREEN_DARK
))

# Source
source_box = Box(
    pos=Position(x=100, y=300, width=400, height=150),
    text="📊 Source BQ Tables\n\n"
         "• product_content_tr\n"
         "• category_hierarchy",
    style=BoxStyle.default()
)
diagram.add(source_box)

# Tagging Job
tagging_pos = source_box.pos.right_of(spacing=150)
tagging_job = Box(
    pos=tagging_pos,
    text="🏷️ scr-tagging-jobs\n\n"
         "home-furniture-core-\nunnormalized\n\n"
         "3048-dim vectors",
    style=BoxStyle.success()
)
diagram.add(tagging_job)

diagram.connect(source_box, tagging_job,
                label="① reads products",
                style=ArrowStyle.success())

# Tagging Output BQ
tagging_output_pos = tagging_job.pos.right_of(spacing=150)
tagging_output = Box(
    pos=tagging_output_pos,
    text="🗄️ BQ Table\n\n"
         "home_furniture_core_\nunnormalized_outputs\n\n"
         "✅ Has: 3048-dim vectors\n"
         "❌ Missing: categories array\n"
         "❌ Missing: genders, agegroups\n"
         "❌ Missing: finger_print\n"
         "❌ Missing: is_deleted",
    style=BoxStyle.error()
)
diagram.add(tagging_output)

diagram.connect(tagging_job, tagging_output,
                label="② writes",
                style=ArrowStyle.success())

# ============= PHASE 2: DIMENSION REDUCTION (SEMAN-858) ✅ =============
diagram.add(Text(
    pos=Position(x=100, y=550, width=500, height=30),
    text="PHASE 2: Dimension Reduction (SEMAN-858) ✅",
    font_size=24,
    align="left",
    color=Color.GREEN_DARK
))

# Reduction Job
reduction_pos = Position(x=100, y=600, width=400, height=150)
reduction_job = Box(
    pos=reduction_pos,
    text="🔧 go-indexing-api\n\n"
         "vector_dimension_\nreduction\n\n"
         "3048 → 128 dim",
    style=BoxStyle.success()
)
diagram.add(reduction_job)

diagram.connect(tagging_output, reduction_job,
                label="③ reads 3048-dim",
                style=ArrowStyle.success())

# Reduction API
reduction_api_pos = reduction_job.pos.right_of(spacing=150)
reduction_api = Box(
    pos=reduction_api_pos,
    text="🤖 Dimension\nReduction API\n\n"
         "Triton Autoencoder",
    style=BoxStyle.success()
)
diagram.add(reduction_api)

diagram.connect(reduction_job, reduction_api,
                label="④ request",
                style=ArrowStyle.success())
diagram.connect(reduction_api, reduction_job,
                label="⑤ 128-dim",
                style=ArrowStyle.success())

# Reduction Output BQ
reduction_output_pos = reduction_api.pos.right_of(spacing=150)
reduction_output = Box(
    pos=reduction_output_pos,
    text="🗄️ BQ Table\n\n"
         "home_furniture_\nreduced_vectors\n\n"
         "✅ Has: 128-dim vectors\n"
         "✅ Has: category_id (INT64)\n"
         "❌ Missing: categories ARRAY\n"
         "❌ Missing: genders, agegroups\n"
         "❌ Missing: finger_print\n"
         "❌ Missing: is_deleted",
    style=BoxStyle.error()
)
diagram.add(reduction_output)

diagram.connect(reduction_job, reduction_output,
                label="⑥ writes",
                style=ArrowStyle.success())

# ============= PHASE 3: ES INDEXING (SEMAN-860) ❌ =============
diagram.add(Text(
    pos=Position(x=100, y=850, width=500, height=30),
    text="PHASE 3: ES Indexing (SEMAN-860) ❌ BLOCKED",
    font_size=24,
    align="left",
    color=Color.RED_DARK
))

# ES Indexing Job
es_job_pos = Position(x=100, y=900, width=400, height=180)
es_job = Box(
    pos=es_job_pos,
    text="⚠️ go-indexing-api\n\n"
         "image_tag_vector_indexing\n\n"
         "❌ NEEDS:\n"
         "• categories ARRAY\n"
         "• genders, agegroups\n"
         "• finger_print\n"
         "• is_deleted",
    style=BoxStyle.error()
)
diagram.add(es_job)

diagram.connect(reduction_output, es_job,
                label="⑦ reads (MISSING FIELDS!)",
                style=ArrowStyle.error())

# Elasticsearch
es_pos = es_job.pos.right_of(spacing=150)
es_box = Box(
    pos=es_pos,
    text="🔍 Elasticsearch\n\n"
         "❌ BLOCKED",
    style=BoxStyle.error()
)
diagram.add(es_box)

diagram.connect(es_job, es_box,
                label="⑧ cannot index",
                style=ArrowStyle.error())

# ============= MISSING STEP: SCHEDULED QUERY =============
diagram.add(Text(
    pos=Position(x=1400, y=250, width=600, height=30),
    text="❌ MISSING: BQ Scheduled Query",
    font_size=28,
    align="left",
    color=Color.RED_DARK
))

missing_query_pos = Position(x=1400, y=300, width=500, height=250)
missing_query = Box(
    pos=missing_query_pos,
    text="❌ SCHEDULED QUERY NEEDED\n\n"
         "Should enrich:\n"
         "reduced_vectors_prod\n\n"
         "Add these fields:\n"
         "• categories (ARRAY<STRUCT>)\n"
         "• genders (ARRAY<STRUCT>)\n"
         "• agegroups (ARRAY<STRUCT>)\n"
         "• country_codes (ARRAY)\n"
         "• regions (ARRAY)\n"
         "• finger_print (STRING)\n"
         "• is_deleted (BOOL)",
    style=BoxStyle.error()
)
diagram.add(missing_query)

# Arrow from reduction output to missing step
diagram.connect(reduction_output, missing_query,
                label="NEEDS ENRICHMENT",
                style=ArrowStyle.error())

# ============= SOLUTION BOX =============
solution_pos = Position(x=1400, y=650, width=500, height=250)
solution_box = Box(
    pos=solution_pos,
    text="✅ SOLUTION OPTIONS:\n\n"
         "1. Add enrichment to SEMAN-858\n"
         "   (dimension reduction output)\n\n"
         "2. Create new scheduled query\n"
         "   (separate enrichment step)\n\n"
         "3. JOIN in ES indexing SQL\n"
         "   (not recommended - overhead)",
    style=BoxStyle(
        background_color=Color.ORANGE_LIGHT,
        stroke_color=Color.ORANGE_DARK
    )
)
diagram.add(solution_box)

# ============= LEGEND =============
diagram.add(Text(
    pos=Position(x=100, y=1150, width=300, height=30),
    text="LEGEND:",
    font_size=24,
    align="left",
    color=Color.BLACK
))

legend_y = 1200
diagram.add(Box(
    pos=Position(x=100, y=legend_y, width=150, height=50),
    text="✅ Exists",
    style=BoxStyle.success()
))
diagram.add(Box(
    pos=Position(x=280, y=legend_y, width=150, height=50),
    text="❌ Missing",
    style=BoxStyle.error()
))
diagram.add(Box(
    pos=Position(x=460, y=legend_y, width=150, height=50),
    text="⚠️ Needs Fix",
    style=BoxStyle.warning()
))

# Save
output_path = "/Users/alperen.uretmen/excalidraw-diagram-builder/output/home_furniture_current_state.excalidraw"
diagram.save(output_path)
print(f"✅ Saved: {output_path}")
print(f"📋 Clipboard: {output_path.replace('.excalidraw', '_clipboard.json')}")
