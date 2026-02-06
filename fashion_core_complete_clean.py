#!/usr/bin/env python3
"""Fashion AS-IS Pipeline - CORE Region (Complete & Validated)"""
import sys
sys.path.insert(0, '/Users/alperen.uretmen/excalidraw-diagram-builder')

from excalidraw_builder import (
    ExcalidrawDiagram, Box, Text, Position,
    BoxStyle, ArrowStyle, Color
)

# Note: Box.calculate_height() is now built-in to the library!
# Optimized defaults: line_height=19, padding=40
# Usage: height = Box.calculate_height(text)  # Auto-calculated!

# Define custom arrow styles
ARROW_WRITES = ArrowStyle(
    stroke_color=Color.GREEN_DARK,
    stroke_width=3,
    stroke_style="solid"
)

ARROW_READS = ArrowStyle(
    stroke_color=Color.GRAY,
    stroke_width=1,
    stroke_style="dashed"
)

diagram = ExcalidrawDiagram("Fashion CORE Complete Pipeline")

# TITLE
diagram.add(Text(
    pos=Position(x=900, y=40, width=1800, height=70),
    text="FASHION AS-IS PIPELINE - CORE REGION (Complete & Validated - 2026-02-05)",
    font_size=38, align="center", color=Color.BLACK
))

diagram.add(Text(
    pos=Position(x=900, y=110, width=1600, height=40),
    text="Production Data Validated | All SQLs Retrieved from GCP Console",
    font_size=16, align="center", color=Color.GRAY
))

# ============================================================================
# STEP 1: METADATA ENRICHMENT
# ============================================================================
y = 200

# Phase 1 Bounding Box
phase1_box = Box(
    pos=Position(x=50, y=y-50, width=1750, height=550),
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, border_style="dashed", 
                   background_color="transparent", rounded=True)
)
diagram.add(phase1_box)

phase1_label = Text(
    pos=Position(x=70, y=y-40, width=400, height=30),
    text="Phase 1: Metadata Enrichment",
    font_size=18,
    align="left",
    color=Color.GRAY
)
diagram.add(phase1_label)

source_box = Box(
    pos=Position(x=100, y=y, width=300, height=120),
    text=" [0] Couchbase Source\n\n"
         "ods_couchbase.product_content_tr\n\n"
         "Fashion products\n"
         "(categories, genders, regions)",
    style=BoxStyle.default()
)
diagram.add(source_box)

sq1_text = """ [1] Scheduled Query #1
Metadata Enrichment

scr_keep_prod_image_tag_indexing_
incremental_core_scheduler

Every 6 hours | europe

Filter: tag_set='fashion', region=CORE
Fingerprint change detection
Soft delete | Incremental"""

sq1 = Box(
    pos=Position(x=500, y=y, width=480, height=Box.calculate_height(sq1_text)),
    text=sq1_text,
    style=BoxStyle.warning(bold=True)
)
diagram.add(sq1)

out1 = Box(
    pos=Position(x=1080, y=y, width=350, height=200),
    text=" [2] BQ: Metadata\n\n"
         "scr_keep_prod_image_tag_indexing\n_incremental_core\n\n"
         "11.2M rows | 2.5 GB\n"
         "Updated: 2026-02-05 08:36\n\n"
         "content_id, image_path,\n"
         "categories, genders, regions",
    style=BoxStyle.success(bold=True)
)
diagram.add(out1)

# Step 1: Scheduler reads from source
diagram.connect(sq1, source_box, "(1) reads", ARROW_READS)
# Step 2: Scheduler writes to output
diagram.connect(sq1, out1, "(2) WRITES", ARROW_WRITES)

# ============================================================================
# STEP 2: IMAGE EMBEDDING GENERATION
# ============================================================================
y = 900  # Start after Phase 1 ends (700) + 200px margin

# Phase 2 Bounding Box
phase2_box = Box(
    pos=Position(x=1200, y=y-50, width=1100, height=1000),
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, border_style="dashed", 
                   background_color="transparent", rounded=True)
)
diagram.add(phase2_box)

phase2_label = Text(
    pos=Position(x=1220, y=y-40, width=500, height=30),
    text="Phase 2: Image Embedding Generation",
    font_size=18,
    align="left",
    color=Color.GRAY
)
diagram.add(phase2_label)

go_job1_text = """ [3] GO JOB #1
Image Embedding Generation

Module: product-image-embedding
Job: image_embedding_core
Schedule: daily 01:00, 07:00

READS FROM:
- OUTPUT TABLE 1

PROCESS:
- Fetches content_id + image_paths
- Calls image-embedding-api
- Generates 256-dim embeddings
- Fingerprint-based dedup

CONFIG (Production):
- batchSize: 1000
- workerCount: 50
- Model: dinov2 v20250202"""

go_job1 = Box(
    pos=Position(x=1250, y=y, width=500, height=Box.calculate_height(go_job1_text)),
    text=go_job1_text,
    style=BoxStyle.warning(bold=True)
)
diagram.add(go_job1)

api1 = Box(
    pos=Position(x=1900, y=y+100, width=350, height=180),
    text=" [4] IMAGE-EMBEDDING-API\n\n"
         "discovery-scr-image-\n"
         "embedding-api.mars\n\n"
         "Model: dinov2\n"
         "Version: v20250202\n"
         "Output: 256-dim\n"
         "dense vector",
    style=BoxStyle.default()
)
diagram.add(api1)

out2 = Box(
    pos=Position(x=1250, y=y+520, width=500, height=420),
    text=" [5] OUTPUT TABLE 2\nImage Embeddings\n\n"
         "scr_keep_prod_full_image_embeddings_core\n\n"
         "FIELDS:\n"
         "- content_id\n"
         "- image_embedding ARRAY<STRUCT<\n"
         "    rank, image_path,\n"
         "    embedding ARRAY<FLOAT64>\n"
         "  >>\n"
         "- model_name, model_version\n"
         "- internal_version\n"
         "- created_at, updated_at\n"
         "- finger_print\n\n"
         "STATUS:  ACTIVE\n"
         "ROWS: 41,311,277\n"
         "SIZE: 85 GB\n"
         "LAST MODIFIED: 2026-02-05 11:00 ",
    style=BoxStyle.success(bold=True)
)
diagram.add(out2)

# Step 3: Job reads from output table
diagram.connect(go_job1, out1, "(3) reads", ARROW_READS)
# Step 4: Job calls API
diagram.connect(go_job1, api1, "(4) calls API", ArrowStyle.default())
# Step 5: Job writes to output
diagram.connect(go_job1, out2, "(5) WRITES", ARROW_WRITES)

# ============================================================================
# STEP 3: TAG EMBEDDING GENERATION
# ============================================================================
y_tag = 900  # Same level as Phase 2 (side-by-side)

# Phase 3 Bounding Box
phase3_box = Box(
    pos=Position(x=50, y=y_tag-50, width=1100, height=2000),
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, border_style="dashed", 
                   background_color="transparent", rounded=True)
)
diagram.add(phase3_box)

phase3_label = Text(
    pos=Position(x=70, y=y_tag-40, width=500, height=30),
    text="Phase 3: Tag Embedding Generation",
    font_size=18,
    align="left",
    color=Color.GRAY
)
diagram.add(phase3_label)

# Category hierarchy table (used by image tagging job)
category_hierarchy = Box(
    pos=Position(x=650, y=y_tag, width=400, height=160),
    text=" [6] BQ TABLE\nCategory Hierarchy\n\n"
         "dsm-data.pbl_trendyol\n.category_hierarchy\n\n"
         "PURPOSE:\n"
         "- Category levels (level1-9)\n"
         "- Used to determine tag_set:\n"
         "  'fashion' or 'home_furniture'\n\n"
         "STATUS:  ACTIVE (reference table)",
    style=BoxStyle.default()
)
diagram.add(category_hierarchy)

# Image Tag Similarity API (used by image tagging job)
api_tag_similarity = Box(
    pos=Position(x=650, y=y_tag+280, width=400, height=180),
    text=" [7] IMAGE-TAG-SIMILARITY-API\n\n"
         "discovery-scr-image-tag-\n"
         "similarity-api.external\n\n"
         "Model: blip2\n"
         "Version: v1\n"
         "doNormalize: false\n"
         "returnTags: true\n\n"
         "OUTPUT:\n"
         "Unnormalized tag scores",
    style=BoxStyle.default()
)
diagram.add(api_tag_similarity)

# Upstream job for tag predictions (added based on validation)
tag_job_text = """ [8] GO/PYTHON JOB
Image Tagging

Project: scr-tagging-jobs
Job: image-tagging-unnormalized
Schedule: daily 02:00

PROCESS:
1. Fetch products (JOIN categories)
2. Filter: sellable, in-stock, has images
3. Dedup: skip already processed
4. Call API for tag scores
5. MERGE results to output table

CONFIG:
- Batch: 1000
- Workers: 50
- Internal Version: v1"""

tag_job = Box(
    pos=Position(x=100, y=y_tag+240, width=450, height=Box.calculate_height(tag_job_text)),
    text=tag_job_text,
    style=BoxStyle.warning(bold=True)
)
diagram.add(tag_job)

tag_source_text = """ [9] BQ TABLE
Tag Predictions

dsm-data.team_search
.image_tagging_unnormalized
_outputs_prod

FIELDS:
- content_id: INT64
- category_id: INT64
- data: ARRAY<STRUCT<
    url, tag_set, tags>>
- internal_version: STRING
- created_at, last_modified: TIMESTAMP

PURPOSE:
- Stores unnormalized tag scores
- Filter: tag_set = 'fashion'
- Used by Scheduler #2 for L2 normalization

STATUS:  ACTIVE
SIZE: Large (production table)"""

tag_source = Box(
    pos=Position(x=100, y=y_tag+722, width=450, height=Box.calculate_height(tag_source_text)),
    text=tag_source_text,
    style=BoxStyle.success(bold=True)
)
diagram.add(tag_source)

sq2_text = """ [10] SCHEDULED QUERY #2
Tag Embedding Generation

scr_keep_prod_image_tag_embedding
_l2_norm_incremental_scheduler

Every 1 hour | europe

PROCESS:
- CROSS JOIN with tag dictionary
- L2-normalize (ML.NORMALIZER)
- Fingerprint change detection
- Hard delete (not soft)

WATERMARK: last_modified"""

sq2 = Box(
    pos=Position(x=100, y=y_tag+1280, width=450, height=Box.calculate_height(sq2_text)),
    text=sq2_text,
    style=BoxStyle.warning(bold=True)
)
diagram.add(sq2)

tag_dict = Box(
    pos=Position(x=100, y=y_tag+1705, width=450, height=180),
    text=" [11] TAG DICTIONARY\n\n"
         "scr_keep_prod_vector_tag_dictionary\n\n"
         "ROWS:  415 tags (VERIFIED)\n"
         "SIZE: 0.01 MB\n"
         "LAST MODIFIED: 2025-11-04\n\n"
         "Contains:\n"
         "- tag_key (alphabetically sorted)\n"
         "- Used for consistent vector ordering",
    style=BoxStyle.success(bold=True)
)
diagram.add(tag_dict)

out3 = Box(
    pos=Position(x=100, y=y_tag+1985, width=450, height=400),
    text=" [12] OUTPUT TABLE 3\nTag Embeddings (L2 Normalized)\n\n"
         "scr_keep_prod_image_tag_embedding_l2_norm\n\n"
         "FIELDS:\n"
         "- content_id: INT64\n"
         "- image_path: STRING\n"
         "- tag_score_vector: ARRAY<FLOAT64>\n"
         "  (415 dimensions, alphabetically ordered)\n"
         "- internal_version: STRING\n"
         "- finger_print: STRING\n"
         "- created_at, updated_at: TIMESTAMP\n\n"
         "STATUS:  ACTIVE\n"
         "ROWS: 21,342,450\n"
         "LAST MODIFIED: 2026-02-05 10:44\n\n"
         "NOTE: Region-agnostic\n"
         "(shared across core/milla/intl)",
    style=BoxStyle.success(bold=True)
)
diagram.add(out3)

# Image Tagging Job connections
# Step 6a: REMOVED - backward arrow clutters diagram (Couchbase is implicit source)
# Tag job reads from couchbase (implicit via metadata table flow)
# Step 6b: Tag job reads from category hierarchy
diagram.connect(tag_job, category_hierarchy, "(6b) reads categories", ARROW_READS)
# Step 6c: Tag job calls image-tag-similarity-api
diagram.connect(tag_job, api_tag_similarity, "(6c) calls API", ArrowStyle.default())
# Step 6d: Tag job reads from tag source (for dedup)
diagram.connect(tag_job, tag_source, "(6d) reads (dedup)", ARROW_READS)
# Step 6e: Tag job writes to tag source table
diagram.connect(tag_job, tag_source, "(6e) WRITES", ARROW_WRITES)

# Step 7: Scheduler reads from tag source
diagram.connect(sq2, tag_source, "(7) reads", ARROW_READS)
# Step 8: Scheduler joins with dictionary
diagram.connect(sq2, tag_dict, "(8) joins", ARROW_READS)
# Step 9: Scheduler writes to output
diagram.connect(sq2, out3, "(9) WRITES", ARROW_WRITES)

# ============================================================================
# STEP 4: MERGE ALL TABLES (3-WAY JOIN)
# ============================================================================
y_merge = 3050  # Start after Phase 3 ends (2850) + 200px margin

# Phase 4 Bounding Box
phase4_box = Box(
    pos=Position(x=650, y=y_merge-50, width=800, height=1450),
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, border_style="dashed", 
                   background_color="transparent", rounded=True)
)
diagram.add(phase4_box)

phase4_label = Text(
    pos=Position(x=670, y=y_merge-40, width=600, height=30),
    text="Phase 4: 3-Way Merge (Metadata + Images + Tags)",
    font_size=18,
    align="left",
    color=Color.GRAY
)
diagram.add(phase4_label)

sq3 = Box(
    pos=Position(x=700, y=y_merge, width=700, height=650),
    text=" [13] SCHEDULED QUERY #3\nMerge All Tables (3-Way JOIN)\n\n"
         "scr_keep_prod_image_tag_indexing_with_embeddings_incremental_core_scheduler\n\n"
         "Schedule: every 6 hours | Region: europe\n"
         "STATUS:  ERROR (see GCP Console screenshot)\n\n"
         "READS FROM:\n"
         "- Table 1: scr_keep_prod_image_tag_indexing_incremental_core\n"
         "- Table 2: scr_keep_prod_image_tag_embedding_l2_norm\n"
         "- Table 3: scr_keep_prod_full_image_embeddings_core \n\n"
         " CONFIRMED: Uses _prod_ table (not _stage_)\n"
         " Git repo SQL has outdated _stage_ reference\n\n"
         "JOIN STRATEGY:\n"
         "- INNER JOIN on content_id AND image_path\n"
         "- Only includes records present in ALL 3 tables\n"
         "- Filters table3 by image_path match\n\n"
         "PROCESS:\n"
         "- Detects changes via watermark\n"
         "- Combines fingerprints from 3 tables\n"
         "- Soft delete if missing in ANY source\n"
         "- QUALIFY ROW_NUMBER for deduplication",
    style=BoxStyle.error(bold=True)
)
diagram.add(sq3)

final_table = Box(
    pos=Position(x=700, y=y_merge+750, width=700, height=580),
    text=" [14] OUTPUT TABLE 4\nFinal Merged Table (All Data Combined)\n\n"
         "scr_keep_prod_image_tag_indexing_with_embeddings_incremental_core\n\n"
         "FIELDS (Combined from 3 tables):\n"
         "- content_id: INT64\n"
         "- image_path: STRING\n"
         "- regions: ARRAY<STRING> (Table 1)\n"
         "- country_codes: ARRAY<STRING> (Table 1)\n"
         "- categories: ARRAY<STRUCT<id, name>> (Table 1)\n"
         "- genders: ARRAY<STRUCT<id, name>> (Table 1)\n"
         "- agegroups: ARRAY<STRUCT<id, name>> (Table 1)\n"
         "- tag_score_vector: ARRAY<FLOAT64>[415] (Table 2)\n"
         "- tag_embedding_internal_version: v1 (Table 2)\n"
         "- image_embedding: ARRAY<STRUCT<\n"
         "    image_path, embedding[256], rank>> (Table 3)\n"
         "- image_embedding_model: dinov2 v20250202 (Table 3)\n"
         "- image_embedding_internal_version: 1.0 (Table 3)\n"
         "- finger_print: STRING (combined from 3)\n"
         "- is_deleted: BOOL (soft delete flag)\n"
         "- created_at, updated_at: TIMESTAMP\n\n"
         "STATUS:  STALE (scheduler failing)\n"
         "ROWS: 10,808,437 | SIZE: 57 GB\n"
         "LAST MODIFIED: 2026-02-03 20:44\n"
         "(2 days ago - merge scheduler ERROR blocks updates)\n\n"
         "NOTE: Core region only\n"
         "(milla/intl have separate tables)",
    style=BoxStyle.warning(bold=True)
)
diagram.add(final_table)

# Step 10-12: Merge scheduler reads from 3 input tables
diagram.connect(sq3, out1, "(10) reads T1", ARROW_READS)
diagram.connect(sq3, out3, "(11) reads T2", ARROW_READS)
diagram.connect(sq3, out2, "(12) reads T3", ARROW_READS)
# Step 13: Merge scheduler writes merged data
diagram.connect(sq3, final_table, "(13) WRITES", ARROW_WRITES)

# ============================================================================
# STEP 5: ELASTICSEARCH INDEXING
# ============================================================================
y_es = 4650  # Start after Phase 4 ends (4450) + 200px margin

# Phase 5 Bounding Box
phase5_box = Box(
    pos=Position(x=650, y=y_es-50, width=1600, height=1400),
    text="",
    style=BoxStyle(stroke_color=Color.GRAY, stroke_width=2, border_style="dashed", 
                   background_color="transparent", rounded=True)
)
diagram.add(phase5_box)

phase5_label = Text(
    pos=Position(x=670, y=y_es-40, width=600, height=30),
    text="Phase 5: Elasticsearch Indexing (Vector Search)",
    font_size=18,
    align="left",
    color=Color.GRAY
)
diagram.add(phase5_label)

go_job2 = Box(
    pos=Position(x=700, y=y_es, width=750, height=580),
    text=" [15] GO JOB #2: ES Indexing\n"
         "Project: go-indexing-api-scr\n\n"
         "Module: image-tag-vector-indexing\n"
         "Job: core\n"
         "Schedule: 4x daily (1am, 7am, 1pm, 7pm)\n\n"
         "PROCESS (2 PHASES):\n"
         "Phase 1: DLQ Processing\n"
         "- Fetch failed records from DLQ (JOIN main table)\n"
         "- Re-index to ES\n"
         "- DELETE successful from DLQ\n"
         "- UPDATE failed in DLQ\n\n"
         "Phase 2: Main Table Processing\n"
         "- Get watermark from ES\n"
         "- Fetch new/updated (WHERE updated_at > watermark)\n"
         "- Bulk index to ES\n"
         "- ONLY write failed records to DLQ\n"
         "- Update watermark on success\n\n"
         "CONFIG:\n"
         "- Batch Size: 200 | Workers: 100\n"
         "- Query Batch Limit: 200,000\n"
         "- ES Host: discovery-scr-vectorsearch-elastic-v9\n"
         "- Index: image_tag_vector-v2-core\n"
         "- Alias: read-image_tag_vector-v2-core\n"
         "- DLQ: scr_keep_prod_image_tag_vector_indexing_failed_records",
    style=BoxStyle.info(bold=True)
)
diagram.add(go_job2)

es_box = Box(
    pos=Position(x=700, y=y_es+680, width=800, height=620),
    text=" [17] ELASTICSEARCH INDEX\nFashion Vector Search (CORE Region)\n\n"
         "Cluster: discovery-scr-vectorsearch-elastic-v9.external:80\n"
         "Index: image_tag_vector-v2-core\n"
         "Alias: read-image_tag_vector-v2-core\n\n"
         "SHARD SETTINGS:\n"
         "- Shards: 8 | Replicas: 2\n"
         "- Initial replicas: 0 (set to 2 after indexing)\n\n"
         "DENSE VECTOR MAPPINGS:\n"
         "1. image_tag_vector (415-dim):\n"
         "   - Type: dense_vector, index: true\n"
         "   - Similarity: dot_product\n"
         "   - Algorithm: HNSW (m=64, ef_construction=200)\n\n"
         "2. image_embedding (256-dim):\n"
         "   - Type: dense_vector, index: true\n"
         "   - Similarity: dot_product\n"
         "   - Algorithm: HNSW (m=64, ef_construction=200)\n\n"
         "STANDARD FIELDS (Metadata):\n"
         "- content_id: keyword (indexed)\n"
         "- image_path: keyword (indexed)\n"
         "- categories: nested (id indexed, name not)\n"
         "- genders: nested (id indexed, name not)\n"
         "- agegroups: nested (id indexed, name not)\n"
         "- regions: keyword (indexed)\n"
         "- country_codes: keyword (indexed)\n"
         "- created_at, updated_at: date\n\n"
         "USED FOR:\n"
         "- Fashion image search (visual similarity)\n"
         "- Tag-based product discovery\n"
         "- Multi-vector search (image + tags)",
    style=BoxStyle.success(bold=True)
)
diagram.add(es_box)

# DLQ Table (Dead Letter Queue for failed records)
dlq_table = Box(
    pos=Position(x=1600, y=y_es+200, width=580, height=500),
    text=" [16] OUTPUT TABLE 5\nDead Letter Queue (DLQ)\n\n"
         "scr_keep_prod_image_tag_vector_indexing_failed_records\n\n"
         "PURPOSE:\n"
         "Stores failed ES indexing records for retry\n\n"
         "FIELDS:\n"
         "- id: STRING (document ID / content_id)\n"
         "- index: STRING (ES index name)\n"
         "- environment: STRING (mars/venus/etc.)\n"
         "- operation_status: STRING (success/failed)\n"
         "- error_message: STRING\n"
         "- action: STRING (index/delete/etc.) [optional]\n"
         "- status: INT (HTTP status code) [optional]\n"
         "- processed_at: TIMESTAMP\n\n"
         "LIFECYCLE (MERGE-based):\n"
         "1. Phase 2: Failed records INSERTED/UPDATED\n"
         "2. Phase 1: Retry (JOIN with main table)\n"
         "3. Success: DELETED from DLQ (MERGE)\n"
         "4. Fail: UPDATED in DLQ (MERGE)\n\n"
         "STATUS:  EMPTY (no failures)\n"
         "ROWS: 0 | SIZE: 0 MB\n"
         "CREATED: 2025-11-12 (3 months ago)\n"
         "LAST MODIFIED: 2025-11-12 13:30\n\n"
         "NOTE: Shared across all regions/jobs",
    style=BoxStyle.success(bold=True)
)
diagram.add(dlq_table)

# Step 14: Job reads from final table
diagram.connect(go_job2, final_table, "(14) reads main", ARROW_READS)
# Step 15: Job reads from DLQ (for retry)
diagram.connect(go_job2, dlq_table, "(15) reads DLQ", ARROW_READS)
# Step 16: Job indexes to Elasticsearch
diagram.connect(go_job2, es_box, "(16) INDEXES", ARROW_WRITES)
# Step 17: Job writes failed records to DLQ
diagram.connect(go_job2, dlq_table, "(17) WRITES (failed)", ARROW_WRITES)

# ============================================================================
# SUMMARY & FINDINGS
# ============================================================================
summary = Box(
    pos=Position(x=1600, y=6100, width=700, height=920),
    text=" VALIDATION SUMMARY\nFashion AS-IS Pipeline (CORE Region)\n\n"
         " VALIDATED (15 Components):\n"
         "- 2 Upstream components (Tag Predictions + Job)\n"
         "- 3 Scheduled Queries (Metadata, Tags, Merge)\n"
         "- 5 BigQuery Tables (validated schemas)\n"
         "- 2 Go Jobs (Image Embedding, ES Indexing)\n"
         "- 1 External API (Image Embedding API)\n"
         "- 1 Elasticsearch Index (CORE region)\n"
         "- 1 DLQ Table (Dead Letter Queue)\n\n"
         " CRITICAL ISSUES FOUND:\n"
         "1. Merge Scheduler ERROR (2 days stale)\n"
         "   - Final table: 10.8M rows (2026-02-03)\n"
         "   - Blocking ES indexing updates\n"
         "2. Git repo has outdated _stage_ reference\n"
         "   - Should use _prod_ table\n\n"
         " DIAGRAM CORRECTIONS MADE:\n"
         "- Image embedding: 768-dim -> 256-dim\n"
         "- ES Job batch: 1000 -> 200\n"
         "- ES Job workers: 50 -> 100\n"
         "- Final table schema: Fixed nested structures\n"
         "- DLQ schema: Validated all fields\n"
         "- Arrow directions: Active -> Passive\n\n"
         " CURRENT DATA STATUS:\n"
         "- Source (Couchbase): Active (indirect validation)\n"
         "- Metadata Table: 11.2M rows, 2.51 GB (2026-02-05)\n"
         "- Tag Predictions: Active (large production table)\n"
         "- Tag Dictionary: 415 tags, 0.01 MB (VERIFIED)\n"
         "- Image Embeddings: 41.1M rows, 85 GB (2026-02-05)\n"
         "- Tag Embeddings: 21.3M rows (2026-02-05)\n"
         "- Final Merged: 10.8M rows, 57 GB (2026-02-03) STALE\n"
         "- DLQ Table: 0 rows (EMPTY - no failures)\n\n"
         " NEXT ACTIONS:\n"
         "1. Fix merge scheduler ERROR (priority!)\n"
         "2. Update git repo SQL (_stage_ -> _prod_)\n"
         "3. Verify final table updates resume\n"
         "4. Monitor ES indexing job",
    style=BoxStyle.warning(bold=True)
)
diagram.add(summary)

# Legend
legend = Box(
    pos=Position(x=1600, y=7120, width=700, height=480),
    text=" LEGEND\n\n"
         "BOX COLORS:\n"
         "- Yellow: Scheduled Queries (BigQuery)\n"
         "- Blue: Go Jobs (Batch Processing)\n"
         "- Green: Active Data Tables\n"
         "- Orange: Warning/Stale Tables\n"
         "- Gray: Source/Reference Tables\n\n"
         "ARROW TYPES & DIRECTION:\n"
         "Rule: Active Component -> Passive Component\n\n"
         "- SOLID GREEN (bold): WRITES / INDEXES\n"
         "  Job/Scheduler -> Table/Index\n"
         "  (Active component writes TO passive store)\n\n"
         "- DASHED GRAY (thin): reads / joins\n"
         "  Job/Scheduler -> Table\n"
         "  (Active component reads FROM passive store)\n\n"
         "- SOLID BLACK: calls API\n"
         "  Job -> API\n"
         "  (Active service calls active service)\n\n"
         "ARROW NUMBERING:\n"
         "- All arrows numbered (1) to (17)\n"
         "- Shows complete data flow sequence\n"
         "- Both reads and writes are numbered\n"
         "- Sequential processing order",
    style=BoxStyle.default()
)
diagram.add(legend)

# Save
output_file = 'output/fashion_core_complete.excalidraw'
diagram.save(output_file)
print(f" Complete diagram saved: {output_file}")
print(f"\n Copy to clipboard: cat {output_file} | pbcopy")
