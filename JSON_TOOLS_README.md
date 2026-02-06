# 🔄 Inverse Transformer & JSON Analysis Tools

Excalidraw JSON dosyalarını analiz etmek ve anlaşılır formata çevirmek için araçlar.

## 🎯 Problem

Büyük Excalidraw JSON dosyaları (örn: `core_concepts.json` - 2.1MB) manuel olarak anlamak çok zor:
- ✅ 699 element var
- ✅ 5 adet base64-encoded PNG image (1.5MB)
- ✅ Binlerce satır JSON kodu

## 💡 Çözüm: 3 Araç

### 1️⃣ **JSON Analyzer** - Yapı Analizi

```bash
python3 json_analyzer.py core_concepts.json
```

**Ne yapar:**
- JSON yapısını recursive olarak analiz eder
- Element tiplerini sayar
- Dosya boyutu, key sayıları gibi istatistikleri gösterir

**Çıktı:**
```
📊 STRUCTURE ANALYSIS
  Type: excalidraw/clipboard
  Elements: 699
  Files: 5 embedded images

📈 STATISTICS
  dicts: 1,546
  strings: 7,530
  numbers: 17,362
  ...
```

---

### 2️⃣ **JSON Summarizer** - Okunabilir Özet

```bash
# İlk 50 elementi göster
python3 json_summarizer.py core_concepts.json

# TÜM elementleri göster
python3 json_summarizer.py core_concepts.json --all
```

**Ne yapar:**
- Her elementi tek satırda özetler
- Box, Arrow, Text, Circle vs. gruplar
- Metin içeriklerini gösterir
- Bağlantıları (`from → to`) gösterir

**Çıktı:**
```
📦 BOXES & RECTANGLES (191 total)
🔲 Box [Rlc8Gf0K]: pos=(6004,-2199) size=636x1402 bg=#ffec99
  └─ Text (bound): "Raw Vectors (BQ)..."
🔲 Box [ZzyKu_bB]: pos=(6208,-2177) size=143x72 bg=#ffec99
  └─ Text (bound): "HDBSCAN (Clustering)..."

➡️  ARROWS & CONNECTIONS (105 total)
➡️  Arrow [FbR4Hifb]: ZzyKu_bB → S0sC1-nq
➡️  Arrow [IrpyUMsL]: S0sC1-nq → Rlc8Gf0K

📝 STANDALONE TEXTS (50 total)
📝 Text [SQg7Ath7]: "Input table : dsm-data.datascience.scr..."
```

**Dosya çıktısı:** `core_concepts.summary.txt` (2.1MB → 17KB!)

---

### 3️⃣ **Inverse Transformer** - JSON → Python Kodu

```bash
# İlk 50 elementi Python koduna çevir
python3 json_to_python.py core_concepts.json 50

# İlk 100 elementi çevir
python3 json_to_python.py core_concepts.json 100

# TÜM elementleri çevir (699)
python3 json_to_python.py core_concepts.json 699
```

**Ne yapar:**
- Excalidraw JSON'unu bizim kütüphanemizin Python koduna çevirir
- Box, Arrow, Text, Circle'ları `excalidraw_builder` sınıflarına map eder
- Renkleri `Color.*` sabitelerine çevirir
- Bağlantıları `diagram.connect()` çağrılarına dönüştürür

**Çıktı:** `core_concepts.py` dosyası

```python
from excalidraw_builder import (
    ExcalidrawDiagram,
    Box, Arrow, Text, Circle,
    Position, BoxStyle, ArrowStyle, Color,
)

def create_diagram():
    diagram = ExcalidrawDiagram("Reconstructed Diagram")
    
    # Box Rlc8Gf0K
    Box(
        pos=Position(x=6004, y=-2199, width=636, height=1402),
        text="",  # Add text here
        style=BoxStyle(stroke_color=Color.BLACK, 
                      background_color="#ffec99", 
                      stroke_width=1)
    )
    
    # Arrow FbR4Hifb (connected)
    diagram.connect(
        from_elem="elem_ZzyKu_bB",
        to_elem="elem_S0sC1-nq",
        label="",
        style=ArrowStyle(stroke_color=Color.BLACK)
    )
    
    # ... 697 more elements
    
    return diagram
```

---

## 📊 Örnek: `core_concepts.json`

### Boyut Karşılaştırması

| Format | Boyut | İçerik |
|--------|-------|--------|
| **Orijinal JSON** | 2.1 MB | 699 element + 5 embedded image |
| **Python Kodu** | ~430 satır | İlk 50 element (parametrize edilebilir) |
| **Text Özeti** | 17 KB | Tüm elementlerin tek satır özeti |

### Element İçeriği

```
Total Elements: 699
  • text            : 218
  • rectangle       : 191
  • arrow           : 105
  • freedraw        :  87  (hand-drawn)
  • ellipse         :  40
  • line            :  39
  • image           :  10
  • frame           :   9

Embedded Images: 5 (1.45 MB base64-encoded PNG)
```

---

## 🚀 Kullanım Senaryoları

### Senaryo 1: Diyagramı Hızlıca Anlamak

```bash
# 1. Önce genel yapıyı gör
python3 json_analyzer.py big_diagram.json

# 2. Element detaylarını oku
python3 json_summarizer.py big_diagram.json

# 3. Özet dosyası (17KB) AI'ye ver, JSON (2.1MB) yerine!
cat big_diagram.summary.txt
```

### Senaryo 2: Diyagramı Programatik Olarak Yeniden Yaratmak

```bash
# JSON'u Python'a çevir
python3 json_to_python.py big_diagram.json 100

# Çıkan kodu düzenle ve çalıştır
python3 big_diagram.py
```

### Senaryo 3: AI'ye Diyagramı Anlatmak

**❌ KÖTÜ:**
```
# 2.1MB JSON'u AI'ye vermek (token limiti aşar)
AI: "Bu dosyayı anlayamıyorum, çok büyük!"
```

**✅ İYİ:**
```bash
# Önce özet çıkar (17KB)
python3 json_summarizer.py core_concepts.json

# Özeti AI'ye ver
cat core_concepts.summary.txt

AI: "Anladım! 699 elementli bir diagram:
- 191 kutu (data pipeline steps)
- 105 ok (bağlantılar)
- 218 text (açıklamalar)
- Core Concepts workflow'u gösteriyor"
```

---

## 🎯 Faydalar

### ✅ Hız
- 2.1MB JSON → 17KB özet (123x daha küçük)
- Manuel JSON okumak yerine 1 komut

### ✅ Anlaşılabilirlik
- JSON syntax yerine düz metin
- Her element tek satırda
- Bağlantılar görünür (`Box1 → Box2`)

### ✅ AI-Friendly
- Token limitlerine takılmaz
- Context window'a sığar
- AI daha iyi anlayabilir

### ✅ Programatik
- JSON → Python kodu dönüşümü
- Diyagramı kod olarak versiyonlayabilirsin
- Otomatik diagram generation

---

## 🛠️ Teknik Detaylar

### JSON Yapısı (Excalidraw)

```json
{
  "type": "excalidraw/clipboard",
  "elements": [
    {
      "id": "abc123...",
      "type": "rectangle",
      "x": 100, "y": 200,
      "width": 300, "height": 150,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffec99",
      "boundElements": [{"id": "text_xyz", "type": "text"}]
    },
    {
      "id": "text_xyz",
      "type": "text",
      "text": "My Box",
      "containerId": "abc123...",
      "fontSize": 16
    },
    {
      "id": "arrow_123",
      "type": "arrow",
      "startBinding": {"elementId": "abc123..."},
      "endBinding": {"elementId": "def456..."}
    }
  ],
  "files": {
    "image_hash": {
      "mimeType": "image/png",
      "dataURL": "data:image/png;base64,iVBOR..."  // 95KB+
    }
  }
}
```

### Renk Mapping

```python
# JSON renkleri → Color class
"#1e1e1e" → Color.BLACK
"#2f9e44" → Color.GREEN_DARK
"#b2f2bb" → Color.GREEN_LIGHT
"#e8590c" → Color.ORANGE_DARK
"#ffe8cc" → Color.ORANGE_LIGHT
"#1971c2" → Color.BLUE_DARK
# ... vs.
```

---

## 📝 Notlar

### Image Handling
- Embedded image'ler base64-encoded (~70% dosya boyutu)
- Inverse transformer sadece pozisyon/boyut bilgisini çıkarır
- Gerçek image datası Python koduna dahil edilmez

### Supported Element Types

✅ **Fully Supported:**
- `rectangle` → `Box` or `BoundingBox` (dashed rectangles)
- `arrow` → `diagram.connect()` or `Arrow`
- `text` → `Text` (standalone texts only, bound texts are comments)
- `ellipse` → `Circle`
- `line` → `Arrow` (with `end_arrow=False`)
- `frame` → `BoundingBox` (with dashed style)

⚠️ **Partially Supported:**
- `freedraw` → Comment (builder library doesn't support hand-drawn paths)
- `image` → Comment (embedded base64 images, position/size only)

### Element Filtering
- Bound text elementleri (kutu içi yazılar) otomatik gruplama
- Arrow label'ları ok ile birlikte gösterilir
- Freedraw/line elementleri comment olarak işaretlenir

### Limitations
- Freedraw elementleri tam olarak yeniden oluşturulamaz (path data kaydedilmez)
- Embedded image'ler Python koduna dahil edilmez (sadece pozisyon/boyut)
- Custom font'lar map edilmeyebilir
- Çok karmaşık grouping'ler manuel düzenleme gerektirebilir

---

## 🎓 Öğrendiklerim

1. **Excalidraw JSON formatı** aslında oldukça temiz ve iyi yapılandırılmış
2. **Base64 image'ler** dosya boyutunu çok şişiriyor (70%)
3. **Element binding sistemi** (arrows, text containers) çok güçlü
4. **Python'da recursive JSON parsing** çok efektif
5. **AI context optimization** için data transformation kritik

---

## 🚧 Gelecek İyileştirmeler

- [ ] Image'leri ayrı dosyalara extract etme
- [ ] Freedraw'ları SVG path olarak export
- [ ] Frame/grouping'leri bounding box'lara çevirme
- [ ] Interaktif web UI (JSON upload → preview)
- [ ] Diff tool (iki JSON'u karşılaştır)

---

## 📚 Kaynaklar

- [Excalidraw GitHub](https://github.com/excalidraw/excalidraw)
- [Excalidraw JSON Schema](https://docs.excalidraw.com/)
- [excalidraw-builder README](./README.md)

---

**Made with ❤️ for large diagram analysis**
