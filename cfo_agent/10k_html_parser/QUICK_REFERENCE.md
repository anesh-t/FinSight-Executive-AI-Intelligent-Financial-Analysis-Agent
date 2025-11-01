# ⚡ 10-K PDF Parser - Quick Reference

**Edit this file → Give to AI → Get fast modifications**

---

## 🎛️ **Configuration Knobs (config.py)**

```python
# Chunking
MAX_CHUNK_WORDS = 400           # When to split
OPTIMAL_CHUNK_SIZE = 300        # Target size
MIN_CHUNK_WORDS = 150           # Minimum size

# LLM
LLM_MODEL = "gpt-4o-mini"       # Model choice
LLM_TEMPERATURE = 0.3           # Randomness (0-1)

# Features
ENABLE_TEXT_REWRITING = True     # Fix errors with LLM
ENABLE_AI_SUBHEADINGS = True     # Generate subheadings
ENABLE_CHUNKING = True           # Split long text
```

---

## 🔄 **Pipeline Steps**

```
PDF → Extract Text → Clean Artifacts → Find Sections → 
Chunk Text → Generate Subheadings → Detect Tables → Output JSON
```

### **1. Extract (pdf_parser.py)**
- Uses: pdfplumber
- Output: Full text + potential tables

### **2. Clean (pdf_parser.py → _clean_text)**
Removes:
- URLs: `https://...`
- Timestamps: `10/25/25, 4:27 PM`
- Page numbers: `15/75`
- Standalone numbers
- Duplicates: `Table of Contents Table of Contents`

### **3. Section Detection (pdf_parser.py)**
- Pattern: `ITEM X.` or `Item XA.`
- Splits into 18-21 sections

### **4. Chunking (text_chunker.py)**
- Split at paragraphs (`\n\n`)
- Then sentences (`. `) if needed
- Target: 300 words per chunk
- Result: 150-200 chunks per file

### **5. Subheadings (text_rewriter.py)**
- LLM generates 4-8 word titles
- Context: Section + first 500 chars
- Always generated if missing

### **6. Tables (table_extractor.py)**
- Filters fake layout tables
- Keeps only if:
  - 20%+ numeric values
  - <50% empty cells
  - Consistent columns

---

## 🎯 **Common Modifications**

### **Smaller Chunks (200 words)**
```python
# config.py
OPTIMAL_CHUNK_SIZE = 200
MAX_CHUNK_WORDS = 300
```

### **Larger Chunks (500 words)**
```python
# config.py
OPTIMAL_CHUNK_SIZE = 500
MAX_CHUNK_WORDS = 600
```

### **Disable Subheading Generation**
```python
# config.py
ENABLE_AI_SUBHEADINGS = False
```

### **More Aggressive Cleaning**
```python
# pdf_parser.py → _clean_text()
text = re.sub(r'YOUR_PATTERN', '', text)
```

### **Change Table Threshold**
```python
# table_extractor.py → _is_real_data_table()
numeric_ratio >= 0.30  # More strict (was 0.20)
```

---

## 📊 **Typical Output**

**Input:** 75-page PDF
**Output:**
- 18-21 Items
- 150-200 chunks
- ~300 words per chunk
- All chunks have subheadings
- 0-5 tables (PDFs rarely have structured tables)

**Time:** ~3 minutes
**Cost:** ~$0.05 (GPT-4o-mini)

---

## 🎯 **Prompt Template**

```
Modify 10-K PDF parser:

CHANGE: [What to change]
FILE: [Which file: config.py / pdf_parser.py / text_chunker.py / etc.]
CURRENT: [Current behavior]
DESIRED: [What you want]
```

### **Example:**
```
CHANGE: Make chunks 200 words instead of 300
FILE: config.py
CURRENT: OPTIMAL_CHUNK_SIZE = 300
DESIRED: OPTIMAL_CHUNK_SIZE = 200
```

---

## 📁 **File Map**

```
config.py              → All settings
pdf_parser.py          → PDF extraction + cleaning
table_extractor.py     → Table detection logic
text_rewriter.py       → LLM text fixing + subheadings
text_chunker.py        → Smart chunking
pipeline.py            → Main orchestrator
```

---

## 🐛 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| Chunks too large | Lower `OPTIMAL_CHUNK_SIZE` |
| Too expensive | Disable `ENABLE_AI_SUBHEADINGS` |
| Text being removed | Check `_clean_text()` patterns |
| No tables | Check text - data is preserved |
| Too slow | Increase `OPTIMAL_CHUNK_SIZE` |

---

**🔄 Use this as prompt template for fast modifications!**
