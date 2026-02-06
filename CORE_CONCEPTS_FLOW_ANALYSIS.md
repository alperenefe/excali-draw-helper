# 🎯 Core Concepts Diagram - Akış Analizi

**Kaynak:** `core_concepts.json` (2.1MB, 699 element)

---

## 📊 Genel Bakış

Bu diagram **Core Concepts** adlı bir ML/Data pipeline'ının tüm akışını gösteriyor. 

### İstatistikler
- **699 toplam element**
- **191 kutu** (servisler, data sources, notlar)
- **105 ok** (data flow, bağlantılar)
- **218 text** (açıklamalar, notlar)
- **40 circle** (step numaraları, vurgular)
- **10 image** (screenshot'lar, örnekler)
- **87 freedraw** (el çizimi vurgular)

---

## 🔄 Ana Pipeline Akışı

### **Phase 1: Data Preparation & Clustering**

#### 1️⃣ **Core Concept DataSet Creator (GO)**
```
📍 Box Position: (467, 340)
🎨 Background: #ffffff (white)
📦 GitLab: https://gitlab.trendyol.com/data/data-science/computervision...
```

**Input:**
- `dsm-data.datascience.scr_keep_stage_milla_core_concepts`
- Milla Product Information
- Milla Session Information
- Time window: 2 weeks
- 5 per content id x crop category

**Görev:**
- Session ve product bilgilerini okur
- Dataset oluşturur
- Output: BQ tablosuna yazar

**Oklar:**
- ➡️ "reads session and product info" → Input tables
- ➡️ "write data set" → Output BQ

---

#### 2️⃣ **Core Concept Definer (Python)**
```
📍 Box Position: (1413, 319)
🎨 Background: #ffffff (white)
```

**Input:**
- Raw Vectors (BQ)
- Product image tag embeddings
- `dsm-data.datascience.scr_keep_prod_image_tag_embedding_l2_norm`

**Algoritma:**
- **HDBSCAN Clustering** kullanır
- Cluster'lar oluşturur (concepts)
- Her cluster = 1 concept

**Process:**
```
Raw Vectors (BQ) 
    ↓
HDBSCAN (Clustering)
    ↓
Clusters (Concepts)
```

**Output:**
- Cluster assignments
- Selected products per concept
- Concept vectors

**Detaylar (mavi kutularda #e7f5ff):**

**Kutu [uscuZGLb]:**
> "HDBSCAN clustering sonucunda atanan gruplanan productlar"
> 1. Her cluster için centroid hesaplama
> 2. Cluster'daki tüm ürün vektörlerinin ortalaması

**Kutu [T89dTTgh]:**
> Centroid hesaplama:
> - Cluster'daki tüm ürün vektörlerinin ortalaması
> - Mean image distance
> - Mean tag distance

**Kutu [f3jejhix]:**
> Clustering sonrasında:
> 1. Cluster'daki tüm ürün vektörlerinin ortalaması
> 2. Majority category belirleme

**Oklar:**
- ➡️ "read products' vectors" → BQ
- ➡️ "writes cluster info" → Output

---

### **Phase 2: Concept Enrichment & Naming**

#### 3️⃣ **Core Concept Enricher (GO)**
```
📍 Box Position: (2193, 312)
🎨 Background: #ffffff (white)
```

**Input:**
- Core Concept Definer output
- Selected products
- Concept vectors

**4 Major Steps (circle'larla numaralandırılmış):**

**Step 1:** ➡️ Image Tag Vector Search API
```
Label: "1- find top 100 similar product by concept vector and category..."
Target: Image Tag Vector Search Api [UTxWbET7]
```
- Concept vector ile ES'den search
- Category filter ile top 100 benzer ürün bul

**Step 2:** ➡️ LLM
```
Label: "2- get concept name with top5 contents images..."
Target: LLM [cXHLgxHL]
```
- Top 5 product'ın image'leri ile LLM'e git
- LLM'den concept name al

**Step 3:** ➡️ Shop the Look
```
Label: "3- gets shop the look similars for each product..."
```
- Her product için Shop the Look similar'ları çek

**Step 4:** ➡️ Final Concepts
```
Label: "4- writes final concepts..."
Target: Output BQ [JiDj7OGt]
```
- Final concept tablosunu yaz

**Detaylar (sarı kutularda #ffec99):**

**Kutu [sQ_Z4NWF]:**
> **"Concept Name Creations"**
> Core-Concept-Definer'ın output'unda olan selected_products

---

### **Phase 3: LLM & Name Generation**

#### 📝 **LLM Input Hazırlığı**

**Kutu [bz03jTya]:**
> "LLM e giderken Selected product id ler ile birlikte ilgili product metadata gidecek"

**Kutu [_PW6XE7b]:**
> "Sana tag nameler lazim oldugu için Image'ları ve tag skorları lazım"

**Kutu [PBhQb3h9]:** (Sarı #ffec99)
> **LLM'e ne gidecek?**
> - LLM seçilen productların image'leri ve tag name'leri ile gidilecek
> - Selected product IDs
> - Product metadata

**Kutu [scT7YtOB]:**
> "Concept e ait olan top 5 product'ın image'i ile birlikte LLM'e gidilecek"

**Akış:**
```
Concept Top 5 Products (with images)
    ↓
LLM API
    ↓
Concept Name (string)
```

---

### **Phase 4: Post-LLM Processing**

#### 🔍 **Vector Search & Similarity**

**Kutu [nAby3_5P]:**
> "Concept vector ile Image Tag Vector Search api'ya gidip 100 benzer ürün çekilecek"

**Akış:**
```
scT7YtOB (LLM results)
    ↓
nAby3_5P (Vector Search - 100 similar products)
    ↓
NsX7rw1p (Shop the Look)
    ↓
s4lRrVpb (Name Deduplication)
```

**Kutu [NsX7rw1p]:**
> "Shop the Look'a gidilecek her product için ve concept bir aşama daha olacak"

**Kutu [s4lRrVpb]:**
> "Name deduplication adımı implement edilecek"

**Kutu [4vXNUpcJ]:**
> "In some concepts we received same name from LLM. So we applied name deduplication"

---

### **Phase 5: Category & Metadata Enrichment**

#### 📊 **Majority Category Hesaplama**

**Kutu [EeeTScY6]:** (Sarı #ffec99)
> "Conceptler oluştuktan sonra concept'in majority category'sini belirleyeceğiz"

**Kutu [48HCYN_E]:** (Sarı #ffec99)
> "Majority'yi belirlerken concept'e ait olan productları dolanan şekilde category'lerine göre grupluyoruz"

**Kutu [26O60bHF]:** (Sarı #ffec99)
> "Majority kategoriler ile related kategoriler istenecek"
> Bilal'den sorulacak

**Akış:**
```
nAby3_5P (100 similar products)
    ↓
EeeTScY6 (Majority Category)
    ↓
48HCYN_E (Category Grouping)
    ↓
26O60bHF (Related Categories)
```

**Sorular Kutusu [3tsRV-3F]:**
> 1. Related Categoryleri nasıl alırım nereden buluruz?
> 2. Concept vector nasıl hesaplanıyor?

---

## 🗄️ Data Sources & Tables

### **Input Tables**

1. **`dsm-data.datascience.scr_keep_stage_milla_core_concepts`**
   - Text: "Input table : dsm-data.datascience.scr_keep_stage_milla_core_concepts ENV-Zone Based"
   - Main input dataset

2. **`dsm-data.datascience.scr_keep_prod_image_tag_embedding_l2_norm`**
   - Product image tag embeddings
   - L2 normalized vectors

3. **image search table**
   - Elasticsearch index
   - Tag vectors stored here
   - Used for top 1000 similar products

4. **category_complementary_mapping**
   - Category relationships
   - Complementary category mapping

5. **Milla Product Information** (BQ)
   - Product metadata
   - Categories, gender, etc.

6. **Milla Session Information** (BQ)
   - User session data
   - Click data

---

### **Output Tables**

1. **Cluster Info (BQ)**
   - Core Concept Definer output
   - Cluster assignments
   - Selected products

2. **Final Concepts (BQ)**
   - Core Concept Enricher output
   - Concept names (from LLM)
   - Concept vectors
   - Majority categories
   - Related products

**Output Schema (text'ten):**
```
core_concept_id, core_concept_vector, content_id, score, category...
```

---

## 🔧 Services & APIs

### **1. Image Tag Vector Search API**
```
📍 Box Position: (2649, 309)
🎨 Background: #ffffff
```

**Usage:**
- Concept vector ile KNN search
- Category filter
- Top 100 similar products

**Endpoint (muhtemel):**
- Elasticsearch index query
- 128-dim or 3048-dim vectors

---

### **2. LLM Service**
```
📍 Box Position: (2697, 522)
🎨 Background: #ffffff
```

**Input:**
- Top 5 product images per concept
- Tag names
- Product metadata

**Output:**
- Concept name (string)
- Description (possibly)

**Note:**
- Some concepts get same name
- Name deduplication needed

---

### **3. Shop the Look API**
```
Mentioned in: Kutu [NsX7rw1p]
```

**Usage:**
- Get similar/complementary products
- For each product in concept
- Enrichment step

---

## 📋 Schedules & Automation

### **Schedule 1**
- Text: "Schedule 1"
- Historic data processing
- Initial dataset creation

### **Schedule 2**
- Text: "Schedule 2"
- Regular updates

### **Schedule 3**
- Text: "Schedule 3"
- (Details not specified)

### **SQL Scheduler Script**

**Kutu [bE6E4Ipn]:** (Kırmızı #ffc9c9 - Dikkat!)
> "Bu sql schedular script haline getirilip output tablosu okunacak"

---

## ⚠️ Notlar & Uyarılar

### **Kırmızı Kutular (Dikkat!)** (#ffc9c9)

**Kutu [arjX7h_L]:**
> "Dikkat et..."

**Kutu [bE6E4Ipn]:**
> "Bu sql schedular script haline getirilip output tablosu okunacak"

**Kutu [imT5q9Rq]:**
> "Bu aşamadan sonra ayrı bir bq tablosuna yaz her stepden sonra"

---

### **Sarı Kutular (Bilgi/Notlar)** (#ffec99)

**Concept Name Creation Box [sQ_Z4NWF]:**
> "Concept Name Creations"

**LLM Info Box [PBhQb3h9]:**
> "LLM e giderken hangi bilgiyle gidiyoruz?"

**Sıralama Question Box [Cq769f2S]:**
> "Sıralama mı olacaktı burada? Concept vectore en yakın olan 5 product mı?"

**Majority Category Boxes:**
- [EeeTScY6]: Majority category belirleme
- [48HCYN_E]: Category grouping logic
- [26O60bHF]: Related categories

**Questions Box [Gg5rWb_d]:**
> 1. Majority category nasıl hesaplayacağım?
> 2. Concept vector nasıl hesaplanacak?

---

### **Mavi Kutular (Process Details)** (#e7f5ff)

**HDBSCAN Details:**
- [uscuZGLb]: Clustering results & product grouping
- [T89dTTgh]: Centroid calculation
- [f3jejhix]: Post-clustering steps

---

## 🖼️ Images & Screenshots

Diagram içinde **10 image** var (base64-encoded PNG):

1. **Image [wZQLT-Tr]:** pos=(5425,-793) size=1247x327
   - Muhtemelen tablo örneği veya schema

2. **Image [7WgkxDXg]:** pos=(5588,-5760) size=906x358
   - Process flow screenshot?

3. **Image [EJQuiY1_]:** pos=(3392,-988) size=1168x607
   - Large screenshot (workflow?)

4. **Image [HS2mCk0f]:** pos=(2155,-2486) size=856x771
   - Square screenshot

5. **Image [Cn5dVdp-]:** pos=(191,1305) size=1082x252
   - Wide screenshot (table view?)

6-10. Diğer image'ler (farklı pozisyonlarda)

**Not:** Image'ler base64-encoded olduğu için içerikleri görülemiyor.

---

## 🎯 Version Notes

### **V1 vs V2**

**Text [vtLQ0sJ5]:**
> "V1 de olan backend de ilerletilmesi gereken lojikler"

**Text [xWcraHoF]:**
> "V2 de eklenmesi gereken sürecler"

**Text [5q-sAgTw]:**
> "V1 backend Alignment"

**Text [EiU-9lbu]:**
> "V2 backend Alignment"

---

### **Meeting Notes**

**Text [CzRCA-O5]:**
> "Meeting notes"

**Core Concept Definer Output Example:**
- Text [eC26Tvfq]: "Core Concept definer output ornek cıktısı"
- Table with columns:
  - Majority_1
  - Mean Image
  - Mean Tag
  - m_1
  - Majority_2
  - Mean image distance
  - Mean tag distance

---

## 📊 Concept Selection & Filtering

### **Click-Based Selection**

**Text [qd9k3MCM]:**
> "Compute total clicks for selected products for each concept"

**Text [_bT4L-ug]:**
> "Select top 1000 concept with highest clicks"

**Text [ZCGTIWTP]:**
> "select top n product for each concept"

**Akış:**
```
All Concepts
    ↓
Compute Total Clicks per Concept
    ↓
Select Top 1000 Concepts (by clicks)
    ↓
Select Top N Products per Concept
    ↓
Final Output
```

---

## 🏢 Business Scope

**Text [pndOgHtB]:**
> "tr, milla ve international businesslarının hepsi için çalışıyor"

**Scope:**
- ✅ TR (Turkey)
- ✅ Milla
- ✅ International businesses

---

## 🗂️ Frames (Organizational Grouping)

**Frame [YvuYKOX9]:** "Core-Concept-Definer"
- Groups all Core Concept Definer related elements
- Visual organization

**8 more frames** exist in the diagram for grouping

---

## 🎨 Color Coding

### **White (#ffffff)**
- Main service boxes
- Core components
- Primary pipeline steps

### **Yellow (#ffec99)**
- Notes
- Important information
- Questions
- Planning sections

### **Light Blue (#e7f5ff)**
- Algorithm details
- Process explanations
- Technical notes

### **Light Red (#ffc9c9)**
- Warnings
- Action items
- Critical reminders

### **Transparent**
- Additional notes
- Supplementary information
- GitLab links
- Questions

---

## 🔗 External Links

**GitLab Repositories (text'lerden):**
- Core Concept DataSet Creator
- Core Concept Definer
- Multiple computer vision repos

**Format:**
```
https://gitlab.trendyol.com/data/data-science/computervision...
```

---

## 📈 Data Flow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT DATA SOURCES                        │
│  • Product Info (BQ)                                        │
│  • Session Info (BQ)                                        │
│  • Image Tag Embeddings (BQ)                                │
│  • Category Mapping (BQ)                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 1: DATASET CREATION                       │
│  Component: Core Concept DataSet Creator (GO)               │
│  • Time window: 2 weeks                                     │
│  • 5 per content id x crop category                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│             PHASE 2: CLUSTERING (HDBSCAN)                    │
│  Component: Core Concept Definer (Python)                   │
│  • Cluster products into concepts                           │
│  • Calculate centroids                                      │
│  • Compute mean distances                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 3: ENRICHMENT & NAMING                    │
│  Component: Core Concept Enricher (GO)                      │
│  Step 1: Vector Search (top 100 similar)                    │
│  Step 2: LLM (concept naming with top 5 images)            │
│  Step 3: Shop the Look (similar products)                   │
│  Step 4: Write final concepts                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           PHASE 4: POST-PROCESSING                           │
│  • Name deduplication                                       │
│  • Majority category calculation                            │
│  • Related categories                                       │
│  • Click-based filtering (top 1000)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT TABLES (BQ)                         │
│  • Final concepts with names                                │
│  • Concept vectors                                          │
│  • Related products                                         │
│  • Metadata & categories                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤔 Open Questions (from diagram)

### **Technical Questions**

**Box [hsP9R3nP]:**
> "Sorular: Will be considered in phase 2 kısmı neden 2. aşamada?"

**Box [kBIr8Fdl]:**
> "Cevaplar: ES'den search attıktan sonra query aşamasında category filter..."

**Box [3tsRV-3F]:**
> 1. Related Categoryleri nasıl alırım nereden buluruz?
> 2. Concept vector nasıl hesaplanıyor?
> 3. (More questions...)

### **Process Questions**

**Box [Cq769f2S]:**
> "Sıralama mı olacaktı burada? Concept vectore en yakın olan 5 product mı?"

**Box [TnH7JcA_]:**
> "hangi tablonun nasıl kullanılacağını sorgula. Murat'tan ya da..."

---

## 📝 TODO Items (from diagram)

1. ⚠️ SQL scheduler script haline getir
2. ⚠️ Her stepden sonra ayrı BQ tablosuna yaz
3. ⚠️ Name deduplication implement et
4. ⚠️ Majority category hesaplama logic
5. ⚠️ Related categories entegrasyonu
6. ⚠️ V2 backend alignment
7. ⚠️ Tag name dictionary oluştur

---

## 🎯 Summary

Bu diagram **Core Concepts** adlı bir ML pipeline'ının **end-to-end akışını** gösteriyor:

1. **Input:** Product ve session datası (BQ)
2. **Clustering:** HDBSCAN ile ürünleri gruplama
3. **Naming:** LLM ile concept isimleri üretme
4. **Enrichment:** Vector search, Shop the Look
5. **Post-processing:** Deduplication, category enrichment
6. **Output:** Final concept tablosu (BQ)

**Pipeline'ın amacı:**
- Benzer ürünleri otomatik olarak gruplamak (concepts)
- Her concept'e anlamlı isim vermek (LLM ile)
- Related products bulmak
- Category metadata eklemek
- Recommendation sistemleri için kullanmak

**Total Components:**
- 3 Ana servis (GO + Python)
- 2 External API (Vector Search, LLM)
- 5+ BQ tablosu
- Multiple schedules
- 699 diagram elementi

---

**Generated from:** `core_concepts.json`  
**Analysis Date:** 2026-01-27  
**Tool Used:** `json_summarizer.py`
