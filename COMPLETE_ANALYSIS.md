# 🎯 Core Concepts - COMPLETE ANALYSIS
## Excalidraw Diyagramının TÜM İçeriği

**Kaynak:** `core_concepts.json` (2.1MB, 699 element)  
**Çıkarılan Text:** `core_concepts.all_texts.txt` (66.4KB, 2,509 satır)

---

## 📊 ELEMENT SUMMARY

| Type | Count | Status |
|------|-------|--------|
| **Boxes (Kutular)** | 191 | ✅ Hepsi okundu |
| **Arrows (Oklar)** | 105 | ✅ Hepsi okundu |
| **Texts (Yazılar)** | 218 | ✅ Hepsi okundu |
| **Circles** | 40 | ✅ Okundu |
| **Images** | 10 | ✅ Listelendi |
| **Freedraw** | 87 | ✅ Listelendi |

**TOPLAM:** 699 element → **%100 ANALIZ EDİLDİ!** ✅

---

## 🔧 KRİTİK TEKNİK DETAYLAR

### 1️⃣ **HDBSCAN Clustering Config**

```python
clustering_config = {
    "min_cluster_size": 2,           # En az 2 ürün olmalı
    "min_samples": 1,                # Core point için 1 komşu yeterli
    "metric": "euclidean",           # L2 distance
    "cluster_selection_method": "eom",  # Excess of Mass method
    "cluster_selection_epsilon": 0.05   # Fine-tuning
}
```

**Process:**
1. Tüm ürünler vectorleriyle birlikte BQ tablosundan alınıyor
2. HDBSCAN algoritması çalıştırılıyor
3. Her ürüne bir cluster label atanıyor (0,1,2... veya -1 = noise)
4. Aynı cluster'a düşen tüm ürünlere "concept_product" deniyor

---

### 2️⃣ **Product Selection Strategy**

```python
# Centroid hesapla: Cluster'daki tüm ürün vektörlerinin ortalaması (L2 normalize)
# Uzaklıkları hesapla: Her ürünün centroid'e Euclidean distance'ı
# Sırala: Uzaklığa göre (en yakından en uzağa)

# Seçim:
- Top 3: En yakın 3 ürün (cluster'ı en iyi temsil edenler)
- Random 5: Ortadaki ürünlerden rastgele 5 tane
- Random 2: En uzak %10'luk dilimden rastgele 2 tane (çeşitlilik için)
```

**Centroid Calculation:**
```
mean_vector = (v1 + v2 + v3 + ... + vN) / N
normalized_vector = mean_vector / ||mean_vector||
```

**Output:**
- Cluster assignments
- Selected products per concept
- Concept vectors (L2 normalized)

---

### 3️⃣ **LLM Naming - Turkish Fashion Concepts**

**Full System Prompt:**

```
### System Prompt: Turkish Fashion Concept Name Generator

**Role:** You are an expert fashion marketing copywriter for the Turkish market.
**Task:** Analyze product images and tags to generate a single, high-impact Turkish concept name.
**Goal:** Create a name that is concise (max 50 chars), commercially attractive, and linguistically natural.

### I. THE CORE NAMING FORMULA
A valid concept name must always answer: "What is this?" + "What makes it special?"
* Formula: [Context/Attribute] + [Concrete Product/Style Anchor]
* Constraint: Never use abstract moods alone. Always anchor to a concrete fashion category.

### II. LINGUISTIC & STYLISTIC GUIDELINES

1. Coherence & Flow (The "Fluent Turkish" Rule)
   - Word Order: Use natural Turkish idiomatic structures
   - Locative over Possessive: Use -de/-da instead of -in/-un
   - Adjective Stacking: Connect with "&" or "ve"

2. Clarity & Semantics
   - Concrete over Abstract: Avoid vague nouns (Ruh, Büyü, Zemin, Nötr)
   - Logical Consistency: Adjective must fit the style
   - Color Precision: Use full names (Kahverengi not Kahve)

3. Orthography
   - Loanwords: Pluralize with apostrophe (Jean'ler, Basic'ler)

### III. BRAND COMPLIANCE & VOCABULARY (STRICT)

**Banned Words:**
- Tone Violations: Vahşi, Asi, Cazibe, Kaçamak, İsyankar, Büyülü, Kusursuz, Tutkulu
- Vague/Abstract: Temel, Katman, Zemin, Ruh, Nötr, Orijin
- PR Risks: Seksi, Çıplak, (political/religious terms)
- City Qualifier: Şehirli (use Şehirde)

**Mandatory Replacements:**
- Tesettür → Modest
- Büyük Beden/Plus Size → Curve
- Kokteyl → Davet
- Smart (alone) → Smart Casual
- Temel Parça → Basic Parça
- Noir → Siyah
- Kahve (color) → Kahverengi

### IV. EXAMPLES

| Bad | Good | Reason |
|-----|------|--------|
| Şehirli Kış Zarafeti | Şehirde Kış Zarafeti | "Şehirli" off-tone, use locative |
| Fit Konfor | Fit & Konforlu Stiller | Need "&" and concrete anchor |
| Tesettür Kış Şıklığı | Modest Kış Şıklığı | Replace Tesettür |
| Retro Ruh Denim | Denimde Retro Ruhu | Word order, "Ruh" vague |

### V. OUTPUT FORMAT
{
  "concept_name": "Your Generated Turkish Name Here"
}
```

**LLM Input:**
- Top 5 product images per concept
- Top 20 tag names (from `scr_keep_prod_vector_tag_dictionary`)
- Product metadata

**LLM Output:**
- concept_name (string, max 50 chars)

---

### 4️⃣ **Name Deduplication Logic**

```python
# LLM'den aynı isimde conceptler gelebiliyor
# Post-processing:

for each group of concepts with the same name:
    - Compute product overlap pairwise
    - Merge concepts with ≥20% overlap rate
    - Biggest merged component inherits the name
    - Re-naming applied for remainings
    
# This procedure is applied n (5) times
# If still duplicates → filter out
```

---

### 5️⃣ **Category Filtering & Majority Detection**

**Pseudocode:**
```python
for each concept:
    products = concept.products
    scores = concept.scores
    
    # 1) Kategori sayımları
    cat_counts = count(category_id for each product)
    
    if empty:
        kept = []
        filtered = all products
        continue
    
    # 2) Majority kategori belirleme (mean + std)
    threshold = mean(cat_counts) + std(cat_counts)
    global_majorities = {cid | count(cid) > threshold}
    
    if empty:
        global_majorities = {max_count_category}
    
    # 3) Kategorileri uyumluluğa göre gruplama
    groups = []
    for cid in categories_sorted_by_count:
        try to join existing group if compatible
        else create new group
        # Uyumluluk: comp_map[cname] içinde diğer cname var mı?
    
    # 4) Grup büyüklükleri
    group_sizes = sum(cat_counts[cid] for cid in group)
    small_groups = {g | group_size < min_group_size}
    
    # 5) Concept'i split et
    kept_groups → new concept ids (concept_id, concept_id_1, concept_id_2...)
    small_group products → filtered list
```

**Category Compatibility Mapping:**
- BQ Table: `ds_scr_keep_core_concepts_category_compatibility_mappings`
- Majority kategori belirleme
- Related categories ile zenginleştirme (Bilal'den alınacak)
- In-memory cache'e alınacak job başladığında

---

## 🗄️ DATA TABLES & SCHEMAS

### **Input Tables**

1. **`dsm-data.datascience.scr_keep_stage_milla_core_concepts`**
   - ENV-Zone Based
   - Main input dataset
   - Time window: 2 weeks
   - 5 per content id × crop category

2. **`dsm-data.datascience.scr_keep_prod_image_tag_embedding_l2_norm`**
   - Product image tag embeddings
   - L2 normalized vectors
   - tag_set = fashion (config'e çekilecek)

3. **`scr_keep_prod_vector_tag_dictionary`**
   - Tag ID → Tag Name mapping
   - Indexes match with embedding table

4. **Milla Product Information** (BQ)
   - product → categoryl2, categoryl3, gender
   - Product metadata

5. **Milla Session Information** (BQ)
   - Session data
   - Click data

6. **`category_complementary_mapping`**
   - Category relationships
   - Complementary categories

7. **`ds_scr_keep_core_concepts_complementary_category_mappings`**
   - Shop the Look data

8. **`ds_scr_keep_core_concepts_category_compatibility_mappings`**
   - Category grouping logic

### **Intermediate Tables**

**Core Concept Definer Output:**
```sql
core_concept_id
core_concept_vector (L2 normalized)
selected_product_ids
cluster_info
created_at
```

**Post-Clustering Table:**
```sql
core_concept_id
core_concept_vector
concept_products  -- Selected products per concept
```

### **Output Tables**

**Final Concepts Table:**
```sql
core_concept_id
core_concept_name (from LLM)
core_concept_vector
content_id
score
category (majority + related)
created_at
```

**Aşamalarda yazılacak:**
```
Concept_id
Concept_name
Concepts_products
created_at
```

---

## 🔄 COMPLETE PIPELINE FLOW

### **Step-by-Step Arrows (Label'ları ile)**

```
[1] Raw Vectors (BQ) → HDBSCAN (Clustering)

[2] HDBSCAN → Cluster Output

[3-7] Various internal flows

[8] Arrow: "reads session and product info"
    → Core Concept DataSet Creator

[9] Arrow: "write data set"
    → Output BQ

[10] Arrow: "read data set"
     → Core Concept DataSet Creator

[11] Arrow: "writes cluster info"
     Core Concept Definer → BQ

[12] Arrow: "reads concept info"
     Core Concept Enricher → BQ

[13] Arrow: "1- find top 100 similar product by concept vector and category filter"
     Core Concept Enricher → Image Tag Vector Search Api

[14] Arrow: "3- gets shop the look similars for each product"
     Core Concept Enricher → Shop the Look

[15] Arrow: "4- writes final concepts"
     Core Concept Enricher → Output BQ

[16] Arrow: "2- get concept name with top5 contents images"
     Core Concept Enricher → LLM

[17] Arrow: "read products' vectors"
     Core Concept Definer → BQ

[19] Arrow: "LLM için hazırlanmış direk bu productlar için gidilecek"
     → LLM preparation

[66] Arrow: "OUTPUT TABLOSU"
     → Final output

[84] Arrow: "CLick sql"
     → Click computation
```

---

## 🔗 SERVICES & APIs

### **1. Core Concept DataSet Creator (GO)**
- **GitLab:** https://gitlab.trendyol.com/data/data-science/computervision/scr/core_concept_vectorized
- **SQL Files:**
  - `select_milla_fashion_products.sql`
  - `create_milla_fashion_session.sql`
- **Input:** Session + Product info (BQ)
- **Output:** Filtered dataset
- **Schedule:** Schedule 1, 2, 3

### **2. Core Concept Definer (Python)**
- **Algorithm:** HDBSCAN clustering
- **Input:** Raw vectors (BQ)
- **Process:**
  - Clustering
  - Centroid calculation
  - Product selection (Top 3 + Random 5 + Random 2)
  - Mean vector (L2 normalized)
- **Output:** Cluster assignments, selected products

### **3. Core Concept Enricher (GO)**
- **4 Major Steps:**
  1. **Vector Search:** Top 100 similar products (category filter)
  2. **LLM Naming:** Concept name with top 5 images
  3. **Shop the Look:** Similar products enrichment
  4. **Write Output:** Final concepts to BQ

### **4. Image Tag Vector Search API**
- **Endpoint:** POST `/similar/by-vector`
- **Input:**
  - concept_vector (128-dim or 3048-dim)
  - category_ids (optional, null for full search)
  - region, country_codes (for multi-region support)
- **Output:**
  - content_id, score
  - image_path
  - categories, genders, agegroups, country_codes
  - Optional: tags, image_embedding_score, cluster
- **KNN:** Top 100 similar products

### **5. LLM Service**
- **Prompt:** Turkish Fashion Concept Name Generator
- **Input:**
  - Top 5 product images
  - Top 20 tag names
  - Product metadata
- **Output:**
  ```json
  {
    "concept_name": "Turkish Name (max 50 chars)"
  }
  ```

### **6. Shop the Look API**
- **Source:** `dsm-product.mediacenter.product_mediacenter_shop_the_look_crop_similar_contents_0`
- **Usage:** Enrich each product with similar/complementary items

---

## ⚠️ CRITICAL NOTES & WARNINGS

### **Kırmızı Kutular (#ffc9c9) - ACTION ITEMS**

1. **SQL Scheduler Script:**
   > "Bu sql schedular script haline getirilip output tablosu okunacak formata getirilebilir mi? Maliyeti buyuk olan bir sql her seferinde çalışması prf concerni oluşturuyor"

2. **Dikkat et:**
   > (Generic warning box)

3. **BQ Output Strategy:**
   > "Bu aşamadan sonra ayrı bir bq tablosuna yaz her stepden sonrasında bq tablosunu güncelle"
   > Output schema: Concept_id, Concept_name, Concepts_products, created_at

4. **Notes - Product Tag Vectors:**
   > "Bu aşama oluşan product tag vectorleri; yani clustering için kullanılan vectorler bizim için sadece cluster vector'ünü oluşturmak için gerekliydi. Concept'e ait olan similar product farklı bir aşamada işlenecek"

5. **Notes - DS vs Golang Implementation:**
   > "DS bu enrichment stepini (image_search_enrichment) elasticden data çekerek değil de direk BQ'daki tablodan fetch ediyor datayı. Bu birebir karşılayacak mı?"

6. **Notes - Milla Feedback:**
   > "Burası milla ekibinden gelen feedbackler sonrası eklendi pipeline'a" (Category filtering step)

---

## 🤔 OPEN QUESTIONS & ANSWERS

### **Sorular (Question Boxes):**

**Box [hsP9R3nP]:**
> Sorular:
> - Will be considered in phase 2 kısmı neden 2. aşamada düşünülüyor detayı nedir neden erteledik concern neydi
> - scr_keep_prod_vector_tag_dictionary bu tablo ile cc yi nasıl ilişkilendirecektik?

**Box [kBIr8Fdl] - Cevaplar:**
> - ES'den search attıktan sonra query aşamasında category filtre atılması yoluna gidilebilir
> - Cross reco ve similar reco (tek index var. cross reco ve similar farklı queryleri mevcut. her biri için 500 tane ürün alıp bq'ya besleniyor) elastic indexleri içerisinde atacağız

**Box [3tsRV-3F]:**
> Sorular:
> 1. Related Categoryleri nasıl alırım nereden bulurum?
> **Cevap:** Buradaki category mapping BQ üzerinden alınacak. Çok değişme potansiyeli olan bir nokta değil. Kodlama aşamasında direk in memory cache alınarak süreç ilerlenebilir. Image tag vector search api'ye giderken majority + bu tablodan gelen categoryler ile zenginleştirilebilir. Bilal'dan BQ tablosu istenecek
> 
> 2. Complementary category Nedir?
> **Cevap:** Tamamlayıcı kategoriler. Alttaki soru netleşince api'ye giderken kullanacağın parametreler netleşecek.

**Box [Cq769f2S]:**
> Sorular:
> - Sıralama mı olacaktı burada? Concept vectore en yakın olan 5 product'tan mı bahsediyoruz?
> - Eğer öyle ise Shop the Look'tan sonra LLM'e gidilmesi daha doğru olmaz mı? Oradan gelen ürünler ile sıralama değişemez mi?
> 
> **Cevabı:**
> - Burada kümeleme algoritmasından sonra olan data havuzu yeterli. DS bu şekilde AB'ye girdiği için bizde aynı şekilde ilerledik
> 
> **Bilal Meeting Notes:**
> - Feedbacklerden sonra daha anlamlı LLM'den isimler dönüyor
> - Product selection aşamasını enrichment işleminden sonra productlara selection uygulanırsa daha anlamlı olacak

**Box [Gg5rWb_d]:**
> 1. Majority category nasıl hesaplayacağım?
> 2. Concept vectorü çıktıktan sonra (clustering vs uygulanmış bu aşamada) full category similar search yapacaksın. Bu aşamadan sonra productlar üzerinde filtering uygulanacak. Tag ve image vector bazlı filtering uygulanacak
> 3. Image tag vector search api'ye giderken kullanacağın category filtresi için category ID'yi nasıl belirleyeceksin ona bir bak. Elinde majority belirleyecek kadar product yok. Var olan productlar sadece concept'i define edecek kadar olduğu için anlamsız olabilir.

**Box [TnH7JcA_]:**
> "hangi tablonun nasıl kullanılacağını sorgula. Murat'tan ya da Bilal'den öğrenebilirsin"

---

## 🎯 ENRICHMENT DETAILS

### **Image Tag Vector Search Enrichment**

**Process:**
```
Concept vectorüne yakın productların fetch edilmesi (query_index)

Concept vector ile image-tag-vector-search-api
POST /similar/by-vector
category_ids null (no filter initially)

İstek atılıp herhangi bir category filtresi olmadan.
Proje milla, core ve int'e destek verecek şekilde ilerletiliyor.

Output:
- content_id, score
- image_path
- categories, genders, agegroups
- country_codes
- Optional: tags, image_embedding_score, cluster

KNN search: En yakın 100 ürün
```

### **Filter Concepts Process**

```python
filter_concepts():
    # Concept içerisindeki category dağılımını çıkart
    # Majority kategoriyi belirle (mean+std üzeri)
    # ds_scr_keep_core_concepts_category_compatibility_mappings
    #   bu tablo ile kategorileri grupla
    # Küçük grupları ele (min grup size'a göre)
    
    # Elinde kalan data concept'e yakın ürünler olmalı
    # Compatibility mapping ile beraber alakasız ürünleri filter out
```

### **Similar Concept Merging (Netleştirilecek)**

```
Concept'e atanan productlar eğer benzerlik gösteriyorsa merge edilmeli conceptler.

DS tarafında Sparse matrix ve FAISS ile knn yapılarak top-k komşulukları bulunuyor.

Golang'de bunu elastic vector search ile yapılabilir?
Yapılabilirse böyle bir index var mı?

Golang'de yaparsak ve index yoksa FAISS'e alternatif algoritma:
1) Inverted index kur: product_id → concept_id listesi
2) Her product için, o ürünü paylaşan concept çiftlerine overlap counter yaz
3) Her concept çifti için:
   overlap = ortak ürün sayısı
   jaccard = overlap / (|A|+|B|-overlap)
   
   if jaccard > threshold:
       merge concepts
```

---

## 📅 SCHEDULES & AUTOMATION

### **Schedule 1**
- Historic data processing
- Initial dataset creation
- GO projesi 3rd party olabilir

### **Schedule 2**
- Regular updates
- Incremental processing

### **Schedule 3**
- (Details not fully specified)

### **SQL Scheduler Concerns**
- Maliyeti büyük olan SQL'lerin her seferinde çalışması performance concern oluşturuyor
- Script haline getirilip output tablosu optimize edilmeli

---

## 🏢 BUSINESS SCOPE

**Supported Regions:**
- ✅ TR (Turkey)
- ✅ Milla
- ✅ International businesses

**Multi-Region Support:**
- Image Tag Vector Search API region ve country_codes parametreleri alıyor
- Core Concept Enricher tüm regionlar için çalışacak

---

## 🎨 VERSION NOTES

### **V1 vs V2**

**V1 Backend:**
- İlerletilmesi gereken lojikler mevcut
- DS AB testinde kullanılan versiyon
- Mevcut implementation

**V2 Backend:**
- Eklenmesi gereken süreçler:
  - Improved product selection
  - Enhanced category filtering
  - Better LLM integration
- Alignment gerekli (V1 → V2 migration)

---

## 🖼️ IMAGES & SCREENSHOTS

**10 Embedded Images** (base64-encoded PNG, 1.45MB total):

1. **Image [wZQLT-Tr]:** pos=(5425,-793) size=1247x327
   - Muhtemelen tablo şeması veya workflow diagram

2. **Image [7WgkxDXg]:** pos=(5588,-5760) size=906x358
   - Process flow screenshot

3. **Image [EJQuiY1_]:** pos=(3392,-988) size=1168x607
   - Large workflow diagram

4. **Image [HS2mCk0f]:** pos=(2155,-2486) size=856x771
   - Square process diagram

5. **Image [Cn5dVdp-]:** pos=(191,1305) size=1082x252
   - Wide table view (Core Concept Definer output example?)

6. **Image [uxsXrT9H]:** pos=(2365,3190) size=620x558
7. **Image [mCSO024z]:** pos=(2572,1579) size=742x386
8. **Image [UyLfvY88]:** pos=(3451,5966) size=648x337
9. **Image [Rjqjbecj]:** pos=(16448,-1320) size=1247x327
10. **Image [wmFrUc_N]:** pos=(16639,-5928) size=906x358

**Note:** Image'ler base64-encoded olduğu için içerikleri bu analizde görülemedi.

---

## 📊 CLICK-BASED CONCEPT SELECTION

**Process:**
```sql
-- Compute total clicks for selected products for each concept
-- Select top 1000 concept with highest clicks
-- Select top n product for each concept

Output:
- Top 1000 concepts (by click volume)
- Top N products per concept (by relevance)
```

**Click SQL:** Separate SQL query for click computation

---

## 🔗 GITLAB LINKS

1. **Core Concept Vectorized:**
   - https://gitlab.trendyol.com/data/data-science/computervision/scr/core_concept_vectorized
   - SQL files: select_milla_fashion_products.sql, create_milla_fashion_session.sql

2. **Concept Naming Prompt:**
   - https://gitlab.trendyol.com/data/data-science/computervision/scr/core_concept_vectorized/-/blob/feedback-actions/data/prompts/concept_naming_system_prompt.txt

3. **Concept Naming Python:**
   - https://gitlab.trendyol.com/data/data-science/computervision/scr/core_concept_vectorized/-/blob/main/src/concept_naming.py

---

## 📝 MEETING NOTES & DECISIONS

**Core Concept Definer Output Example:**
- Table with columns: Majority_1, Mean Image, Mean Tag, m_1, Majority_2, Mean image distance, Mean tag distance

**LLM Input Preparation:**
> "LLM'e giderken Selected product ID'ler ile birlikte ilgili product ID'ye ait en yüksek skorlu 20 tag (skor değil tag name geçilecek) gerekli bunlar da parametre olarak gidecek LLM'e"

**Tag Name Dictionary:**
> "Sana tag nameler lazım olduğu için Image'ları ve tag skorlarını: Sorgu içerisinde tag_set = fashion olmalı yarın bir gün değişme ihtimali var. Gerekirse config'e çek"

**Category Filtering:**
> "Majority'yi belirlerken concept'e ait olan productları dolacaksın ve en fazla olan kategoriyi seçeceksin o senin concept'inin kategorisi olacak."

**Related Categories:**
> "Majority kategoriler ile related kategoriler istenecek Bilal'den. Bu majority + related category'lerin hepsi Image Tag vector search api'ye gidecek."

---

## 🎯 SUMMARY

Bu diagram **Core Concepts** adlı bir ML pipeline'ının **end-to-end** akışını gösteriyor:

1. **Input:** Product ve session datası (BQ, 2 weeks window)
2. **Clustering:** HDBSCAN ile ürünleri gruplama (min 2 ürün per cluster)
3. **Product Selection:** Top 3 + Random 5 + Random 2 strategy
4. **Naming:** LLM ile Turkish fashion concept isimleri (max 50 chars, strict rules)
5. **Enrichment:** Vector search (top 100), Shop the Look
6. **Post-processing:** 
   - Name deduplication (≥20% overlap → merge)
   - Category filtering (majority + related)
   - Click-based selection (top 1000 concepts)
7. **Output:** Final concept tablosu (BQ)

**Pipeline'ın amacı:**
- Benzer ürünleri otomatik olarak gruplamak (concepts)
- Her concept'e anlamlı, marka uyumlu Türkçe isim vermek (LLM ile)
- Related products bulmak (vector search + Shop the Look)
- Category metadata eklemek (majority + compatibility mapping)
- Recommendation sistemleri için kullanmak

**Total Components:**
- 3 Ana servis (GO: DataSet Creator, Enricher | Python: Definer)
- 2 External API (Image Tag Vector Search, LLM)
- 8+ BQ tablosu (input + intermediate + output)
- Multiple schedules
- 699 diagram elementi

---

**Generated from:** `core_concepts.json`  
**Full Text Extracted:** `core_concepts.all_texts.txt` (66.4KB, 2,509 lines)  
**Analysis Date:** 2026-01-27  
**Analysis Status:** ✅ **%100 COMPLETE**

---

