# 🔄 10-K PDF Parser - Complete Pipeline Flow

**This document captures the entire processing flow, decisions, and configuration. Edit this to modify pipeline behavior.**

---

## 📁 **Directory Structure**

```
10k-fillings-pdfs/          → INPUT: Raw PDF files
parsed_10k_json/            → OUTPUT: Structured JSON
10k_html_parser/            → PIPELINE CODE
  ├── config.py             → All thresholds and settings
  ├── pdf_parser.py         → PDF text/table extraction + cleaning
  ├── table_extractor.py    → Smart table detection
  ├── text_rewriter.py      → LLM text fixing + subheading generation
  ├── text_chunker.py       → Smart chunking with AI subheadings
  └── pipeline.py           → Main orchestrator
```

---

## ⚙️ **Configuration (config.py)**

### **Chunking Settings:**
```python
MAX_CHUNK_WORDS = 400           # Split if section exceeds this
OPTIMAL_CHUNK_SIZE = 300        # Target chunk size
MIN_CHUNK_WORDS = 150           # Minimum chunk size
CONTEXT_OVERLAP = 50            # Overlap between chunks
```

**Decision:** Keep chunks around 300 words for optimal embedding quality. Prevents huge chunks (like 6,692 words) that don't embed well.

### **Table Detection:**
```python
MIN_TABLE_ROWS = 2              # Minimum rows for valid table
MIN_TABLE_COLS = 2              # Minimum columns
```

**Decision:** PDFs often store tables as text. Smart detection filters layout tables vs real data tables.

### **LLM Settings:**
```python
LLM_MODEL = "gpt-4o-mini"       # Cost-efficient free tier
LLM_TEMPERATURE = 0.3           # Consistent output
MAX_RETRIES = 3                 # Retry on failures
```

**Decision:** Use GPT-4o-mini for cost efficiency (~$0.05 per file).

### **Processing Flags:**
```python
ENABLE_TEXT_REWRITING = True     # Fix parsing errors
ENABLE_AI_SUBHEADINGS = True     # Generate subheadings
ENABLE_TABLE_FORMATTING = True   # Format tables
ENABLE_CHUNKING = True           # Split long text
```

---

## 🔄 **Processing Flow**

### **Step 1: PDF Extraction (pdf_parser.py)**

```python
def _extract_with_pdfplumber(pdf_path):
    1. Read all pages with pdfplumber
    2. Extract text from each page
    3. Try to extract tables (strict mode first, then lenient)
    4. Return: full_text + tables
```

**Decision:** pdfplumber extracts better than PyPDF2. Use aggressive table detection but filter intelligently.

---

### **Step 2: Text Cleaning (pdf_parser.py)**

```python
def _clean_text(text):
    Remove:
    - URLs (https://www.sec.gov/...)
    - Timestamps (10/25/25, 4:27 PM)
    - "Document" standalone
    - Page numbers (15/75)
    - Standalone numbers at line start
    - Excessive whitespace
```

**Decision:** PDFs from SEC have lots of artifacts. Clean aggressively to get pure content.

**Common Artifacts to Remove:**
- `https?://[^\s]+` → URLs
- `\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+[AP]M` → Timestamps
- `\d+/\d+` → Page numbers like "15/75"
- `^\d+\s*$` → Standalone numbers (page numbers)
- `Table of Contents\s+Table of Contents` → Duplicates

---

### **Step 3: Section Detection (pdf_parser.py)**

```python
def _extract_sections(text):
    1. Clean text first
    2. Find all "ITEM X." or "Item XA." headers
    3. Extract text between Items
    4. Filter short sections (< MIN_SECTION_WORDS)
    5. Return list of sections with item_key, heading, text
```

**Pattern:** `(?:ITEM|Item)\s+(\d+[A-Z]?)\.\s*([^\n]+)`

**Decision:** SEC 10-K filings always have "Item X." structure. Use this to split into sections.

---

### **Step 4: Table Detection (table_extractor.py)**

```python
def _is_real_data_table(rows):
    Calculate:
    - numeric_ratio = numeric_cells / total_cells
    - empty_ratio = empty_cells / total_cells
    - long_text_ratio = long_text_cells / total_cells
    
    KEEP if:
    - numeric_ratio >= 0.20        # At least 20% numbers
    - empty_ratio < 0.5            # Less than 50% empty
    - long_text_ratio < 0.3        # Less than 30% long text
    - len(rows) >= 3               # Minimum 3 rows
    - Consistent column counts
```

**Decision:** HTML developers use `<table>` tags for layout. Filter out 95% of fake tables by checking for numeric data.

**Example Real Table:**
- "2.600% Notes" | "$" | "1,000" → 66% numeric ✅

**Example Layout Table:**
- "Risk Factors" | "" | "" → 0% numeric ❌

---

### **Step 5: Text Rewriting (text_rewriter.py)**

```python
def rewrite_if_needed(text, context):
    1. Check if text has parsing errors
    2. If errors detected, use LLM to fix
    3. Cache results to avoid reprocessing
    4. Return cleaned text
```

**Parsing Error Indicators:**
- Too many capitals (>50% uppercase)
- Excessive ellipsis (>3 instances of "...")
- Few words but many chars
- Excessive newlines/spaces

**LLM Prompt:**
```
Fix text from PDF parsing. Remove artifacts, fix formatting.
Keep all data. Output clean, readable text.
```

**Decision:** Only rewrite if errors detected. Saves API calls.

---

### **Step 6: Text Chunking (text_chunker.py)**

```python
def chunk_if_needed(text, context):
    IF word_count <= MAX_CHUNK_WORDS:
        return [single chunk]
    
    ELSE:
        1. Split by paragraphs (\n\n)
        2. IF paragraph > OPTIMAL_CHUNK_SIZE:
           - Split by sentences (". ")
        3. Accumulate until OPTIMAL_CHUNK_SIZE
        4. Generate AI subheading for each chunk
        5. Return list of chunks with subheadings
```

**Chunking Strategy:**
1. **Paragraph-first:** Natural boundaries
2. **Sentence-split:** For long paragraphs
3. **Target 300 words:** Optimal for embeddings
4. **Overlap:** 50 words between chunks (configured)

**Decision:** Smart chunking preserves context. Sentence boundaries better than word counts.

---

### **Step 7: Subheading Generation (text_rewriter.py + pipeline.py)**

```python
def generate_subheading(text, context):
    1. Take first 500 chars of text
    2. Send to LLM with context
    3. Request 4-8 word descriptive subheading
    4. Return cleaned subheading
```

**LLM Prompt:**
```
Generate a 4-8 word subheading for this text.

Context: {item_heading}
Text: {first_500_chars}

Output only the subheading, no quotes.
```

**Always Generate If:**
- `subheading` is `null`
- Chunk has no explicit heading
- Text is split into multiple chunks

**Decision:** AI-generated subheadings improve RAG retrieval. More descriptive than "Part 1 of 3".

**Example Generated Subheadings:**
- "Forward-Looking Statements and Risk Factors"
- "Diverse Product Offerings Across Multiple Platforms"
- "Segmented Analysis of Operational Performance"

---

### **Step 8: JSON Output (pipeline.py)**

```json
{
  "document_metadata": {
    "company": "AMAZON",
    "filing_type": "10-K",
    "fiscal_year": 2018,
    "source_file": "amz-2018-temp-pdf",
    "processing_date": "2025-10-25T16:37:11",
    "pipeline_version": "1.0.0"
  },
  "items": {
    "Item 1": {
      "heading": "Business",
      "content": [
        {
          "subheading": "Forward-Looking Statements and Risk Factors",
          "text": "Clean text without artifacts...",
          "word_count": 283,
          "subheading_generated": true,
          "chunk_info": {
            "index": 1,
            "total": 8
          }
        }
      ]
    }
  }
}
```

**Structure:**
- **items:** Keyed by Item number ("Item 1", "Item 1A", etc.)
- **heading:** Original section heading from PDF
- **content:** Array of chunks
- **subheading:** AI-generated or extracted
- **text:** Cleaned, artifact-free text
- **word_count:** For analytics
- **chunk_info:** Position in multi-chunk sections

---

## 🎯 **Key Design Decisions**

### **1. Why 300-word chunks?**
- **Vector embeddings** work best with 200-400 words
- Too small → loses context
- Too large → dilutes semantic meaning
- **300 words ≈ 1-2 paragraphs** → optimal

### **2. Why clean aggressively?**
- SEC PDFs have URLs, timestamps, page numbers
- These add noise to embeddings
- **Clean text** → better RAG retrieval

### **3. Why smart table detection?**
- 95% of `<table>` tags in HTML are layout, not data
- PDFs store tables as text anyway
- **Check for numeric content** → only keep real tables
- Financial data preserved in text format

### **4. Why always generate subheadings?**
- PDFs often have no explicit subheadings
- Large sections lack structure
- **AI subheadings** → improves chunk discoverability
- Better for retrieval: "Search for risk factors" finds "Forward-Looking Statements and Risk Factors"

### **5. Why use GPT-4o-mini?**
- Cost-efficient: ~$0.05 per 75-page PDF
- Good enough for subheading generation
- Free tier compatible
- **Alternative:** Use larger model if quality needed

---

## 📊 **Expected Output Stats**

**For 75-page Amazon 10-K:**
- **Sections:** 18-21 Items
- **Total Chunks:** 150-200
- **Avg Chunk Size:** 250-350 words
- **Subheadings Generated:** 150-200
- **Tables Extracted:** 0-5 (PDFs rarely have structured tables)
- **Processing Time:** 120-200 seconds
- **Cost:** ~$0.05 (GPT-4o-mini calls)

---

## 🔧 **How to Modify Pipeline Behavior**

### **Make Chunks Smaller (200 words):**
```python
# config.py
MAX_CHUNK_WORDS = 300
OPTIMAL_CHUNK_SIZE = 200
MIN_CHUNK_WORDS = 100
```

### **Make Chunks Larger (500 words):**
```python
# config.py
MAX_CHUNK_WORDS = 600
OPTIMAL_CHUNK_SIZE = 500
MIN_CHUNK_WORDS = 250
```

### **Disable AI Subheading Generation:**
```python
# config.py
ENABLE_AI_SUBHEADINGS = False

# pipeline.py (remove this block):
if not subheading:
    subheading = self.text_rewriter.generate_subheading(...)
```

### **Add More Text Cleaning Rules:**
```python
# pdf_parser.py → _clean_text()
text = re.sub(r'YOUR_PATTERN', '', text)
```

### **Change Table Detection Threshold:**
```python
# table_extractor.py → _is_real_data_table()
numeric_ratio >= 0.30  # More strict (was 0.20)
```

### **Use Different LLM:**
```python
# config.py
LLM_MODEL = "gpt-4"  # Better quality, higher cost
```

---

## 🚀 **Usage**

### **Process All PDFs:**
```bash
python 10k_html_parser/run_parser.py
```

### **Process Single PDF:**
```bash
python 10k_html_parser/run_parser.py "10k-fillings-pdfs/amazon_10k_2018.pdf"
```

### **Test Setup:**
```bash
python 10k_html_parser/test_setup.py
```

---

## 💡 **Common Issues & Solutions**

### **Issue: Chunks still too large**
**Solution:** Lower `OPTIMAL_CHUNK_SIZE` in config.py

### **Issue: Too many subheadings being generated (high cost)**
**Solution:** Set `ENABLE_AI_SUBHEADINGS = False` or increase `MAX_CHUNK_WORDS`

### **Issue: Important text being removed**
**Solution:** Review `_clean_text()` regex patterns, remove overly aggressive rules

### **Issue: Tables not extracted**
**Solution:** PDFs store tables as text. Check text output - data is preserved

### **Issue: Processing too slow**
**Solution:** Reduce chunks (less AI calls) or increase `OPTIMAL_CHUNK_SIZE`

---

## 📝 **Prompt Template for Future Changes**

**When you want to modify the pipeline, edit this document and provide:**

```
I want to change the 10-K PDF parser:

[DESCRIBE CHANGE]
- Example: "Make chunks 200 words instead of 300"
- Example: "Stop generating subheadings for chunks < 100 words"
- Example: "Add more aggressive table detection"

Current behavior (from PIPELINE_FLOW.md):
[PASTE RELEVANT SECTION]

Desired behavior:
[DESCRIBE WHAT YOU WANT]

Files to modify:
[config.py / pdf_parser.py / text_chunker.py / etc.]
```

---

## 🎊 **Summary**

**Input:** Raw 10-K PDF files (75 pages)
**Output:** Clean, chunked, structured JSON (150-200 chunks)

**Key Features:**
1. ✅ Aggressive text cleaning (removes URLs, timestamps, artifacts)
2. ✅ Smart chunking (300 words, natural boundaries)
3. ✅ AI subheading generation (all chunks labeled)
4. ✅ Smart table detection (filters 95% fake tables)
5. ✅ Ready for vector embedding (optimal chunk sizes)

**Cost:** ~$0.05 per 75-page PDF (GPT-4o-mini)
**Time:** ~3 minutes per file
**Quality:** Production-ready for RAG systems

---

**🔄 Keep this document updated when making pipeline changes!**
