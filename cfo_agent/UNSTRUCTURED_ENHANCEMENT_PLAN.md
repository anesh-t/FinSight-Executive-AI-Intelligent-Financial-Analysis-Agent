# 🚀 Unstructured Agent Enhancement Plan

**Goal:** Transform the RAG agent into a comprehensive 10-K analysis powerhouse

**Date:** October 30, 2025

---

## 📊 CURRENT CAPABILITIES (What We Have)

### ✅ **Working Now:**

1. **Semantic Search** - Find relevant sections from 10-K filings
2. **Risk Analysis** - Extract and prioritize risk factors
3. **Strategic Insights** - Analyze business strategies
4. **Comparison** - Compare risks/strategies across companies
5. **Source Attribution** - Cite specific 10-K sections
6. **Direct Answers** - Provide concise responses

### 📁 **Data Available:**

- **Companies:** Apple, Microsoft, Amazon, Google, Meta
- **Years:** 2019-2022 (4 years of data)
- **Sections:** All 10-K items (Risk Factors, MD&A, Business, etc.)
- **Format:** Structured JSON with embeddings in PostgreSQL

---

## 🎯 TARGET CAPABILITIES (What We Want to Add)

### **8 Advanced Capabilities:**

| # | Capability | Example Query | Complexity | Priority |
|---|------------|---------------|------------|----------|
| 1 | **Financial Extraction** | "What was Apple's net cash flow last year?" | MEDIUM | HIGH |
| 2 | **Disclosure Summarization** | "Summarize all major risk factors in 2024" | LOW | HIGH |
| 3 | **Historical Comparison** | "How did R&D expense compare over 3 years?" | HIGH | HIGH |
| 4 | **Peer Benchmarking** | "Compare debt-to-equity vs top 3 competitors" | HIGH | MEDIUM |
| 5 | **Sentiment Analysis** | "Analyze CEO tone in MD&A vs last year" | MEDIUM | MEDIUM |
| 6 | **Compliance Review** | "List SOX disclosures and material weaknesses" | LOW | LOW |
| 7 | **Board Briefing** | "Create executive overview for board meeting" | MEDIUM | HIGH |
| 8 | **ESG & Regulatory** | "Summarize ESG and regulatory risk disclosures" | LOW | HIGH |

---

## 🏗️ ARCHITECTURE ENHANCEMENTS

### **Phase 1: Query Classification & Routing** ⭐

**What:** Detect query type and route to specialized handlers

**Components:**
```python
class EnhancedQueryClassifier:
    """Classify queries into 8 capability types"""
    
    def classify(self, query: str) -> QueryType:
        """
        Returns one of:
        - FINANCIAL_EXTRACTION
        - DISCLOSURE_SUMMARY
        - HISTORICAL_COMPARISON
        - PEER_BENCHMARK
        - SENTIMENT_ANALYSIS
        - COMPLIANCE_REVIEW
        - BOARD_BRIEFING
        - ESG_REGULATORY
        - GENERAL (fallback)
        """
```

**Implementation:**
- Keyword matching (fast, simple)
- Pattern detection (e.g., "compare over X years")
- Entity extraction (companies, years, metrics)

---

### **Phase 2: Specialized Retrievers** ⭐⭐

**What:** Different retrieval strategies for different query types

**Components:**

#### **2.1 Multi-Year Retriever**
```python
class MultiYearRetriever:
    """Retrieve same section across multiple years"""
    
    def retrieve_temporal(
        self,
        company: str,
        section: str,
        years: List[int]
    ) -> Dict[int, List[Chunk]]:
        """Get same section for multiple years"""
```

**Use Cases:**
- Historical comparison
- Trend analysis
- Year-over-year changes

#### **2.2 Multi-Company Retriever**
```python
class MultiCompanyRetriever:
    """Retrieve same section across multiple companies"""
    
    def retrieve_peer(
        self,
        companies: List[str],
        section: str,
        year: int
    ) -> Dict[str, List[Chunk]]:
        """Get same section for multiple companies"""
```

**Use Cases:**
- Peer benchmarking
- Competitive analysis
- Industry comparison

#### **2.3 Section-Specific Retriever**
```python
class SectionRetriever:
    """Target specific 10-K sections"""
    
    SECTION_MAP = {
        'financial': ['Item 8', 'Item 7'],  # Financials, MD&A
        'risk': ['Item 1A'],                 # Risk Factors
        'business': ['Item 1'],              # Business Description
        'compliance': ['Item 9A'],           # Controls & Procedures
        'esg': ['Item 1', 'Item 1A'],       # Business + Risks
    }
```

---

### **Phase 3: Specialized Analyzers** ⭐⭐⭐

**What:** Different analysis logic for different capabilities

#### **3.1 Financial Extractor**
```python
class FinancialExtractor:
    """Extract financial data from narrative sections"""
    
    def extract_metrics(self, chunks: List[Chunk]) -> Dict:
        """
        Extract mentioned financial metrics:
        - Cash flow figures
        - Revenue numbers
        - Expense amounts
        - Ratios and percentages
        """
```

**Approach:**
- Regex patterns for numbers + currency
- Context understanding (LLM)
- Table extraction (if available)

#### **3.2 Historical Comparator**
```python
class HistoricalComparator:
    """Compare data across years"""
    
    def compare_years(
        self,
        data: Dict[int, Any],
        metric: str
    ) -> ComparisonResult:
        """
        Returns:
        - Year-over-year changes
        - Trends (increasing/decreasing)
        - Inflection points
        - Statistical summary
        """
```

**Features:**
- Calculate % changes
- Identify trends
- Detect anomalies
- Provide context

#### **3.3 Sentiment Analyzer**
```python
class SentimentAnalyzer:
    """Analyze tone and sentiment"""
    
    def analyze_tone(
        self,
        text_current: str,
        text_previous: str
    ) -> SentimentResult:
        """
        Returns:
        - Sentiment score (-1 to +1)
        - Tone shift (more/less optimistic)
        - Key phrases driving sentiment
        - Confidence level
        """
```

**Approach:**
- Financial sentiment lexicon
- LLM-based analysis
- Comparative assessment

#### **3.4 Peer Benchmarker**
```python
class PeerBenchmarker:
    """Compare across companies"""
    
    def benchmark(
        self,
        company_data: Dict[str, Any],
        metric: str
    ) -> BenchmarkResult:
        """
        Returns:
        - Ranking (best to worst)
        - Statistical position (percentile)
        - Outliers
        - Industry context
        """
```

---

### **Phase 4: Enhanced Response Generation** ⭐⭐

**What:** Specialized prompts and formatting for each capability

#### **4.1 New Prompt Templates**

```python
# Financial Extraction Prompt
FINANCIAL_EXTRACTION_PROMPT = """
Extract and present financial metrics with context...

OUTPUT FORMAT:
📊 FINANCIAL METRIC: [Metric Name]

Current Value: [Amount with year]
Context: [Where it appears in filing]
Trend: [If historical data available]
Significance: [Why this matters]

📝 DIRECT ANSWER:
[Concise answer to the question]
"""

# Historical Comparison Prompt
HISTORICAL_COMPARISON_PROMPT = """
Compare the metric across years with trend analysis...

OUTPUT FORMAT:
📈 HISTORICAL ANALYSIS: [Metric Name]

Year-by-Year Data:
• 2022: [Value] - [Context]
• 2021: [Value] - [Context]
• 2020: [Value] - [Context]

Trend Analysis:
• Overall Direction: [Increasing/Decreasing/Stable]
• % Change: [YoY changes]
• Inflection Points: [Key changes]

Strategic Context:
[Why these changes occurred]

📝 DIRECT ANSWER:
[Summary of trend]
"""

# Peer Benchmarking Prompt
PEER_BENCHMARK_PROMPT = """
Compare across companies with competitive context...

OUTPUT FORMAT:
🏆 PEER BENCHMARKING: [Metric]

Company Rankings:
1. [Company A]: [Value] - [Context]
2. [Company B]: [Value] - [Context]
3. [Company C]: [Value] - [Context]

Competitive Analysis:
• Industry Leader: [Who and why]
• Laggards: [Who and why]
• Key Differentiators: [What sets them apart]

📝 DIRECT ANSWER:
[Ranking summary]
"""
```

---

## 🎯 IMPLEMENTATION PHASES

### **Phase 1: Foundation (Week 1)** ⭐

**Goal:** Set up classification and routing

**Tasks:**
1. Create `EnhancedQueryClassifier`
2. Add capability detection logic
3. Test with sample queries
4. Update routing in master agent

**Deliverables:**
- `enhanced_classifier.py`
- Unit tests for classification
- Integration with existing system

**Effort:** 2-3 days

---

### **Phase 2: Quick Wins (Week 1-2)** ⭐⭐

**Goal:** Implement 3 easiest capabilities first

**Priority Capabilities:**
1. ✅ **Disclosure Summarization** (easiest - already mostly working)
2. ✅ **ESG & Regulatory** (easy - section filtering)
3. ✅ **Board Briefing** (medium - formatting)

**Why These First:**
- Already 80% working
- Just need better prompts/formatting
- Can deliver in 3-4 days
- Build confidence and momentum

**Tasks:**
1. Create specialized prompts
2. Add section filtering
3. Test with sample queries
4. Document usage

**Deliverables:**
- 3 working capabilities
- Test suite
- Documentation
- Example queries

**Effort:** 3-4 days

---

### **Phase 3: High-Value Capabilities (Week 2-3)** ⭐⭐⭐

**Goal:** Add most requested capabilities

**Capabilities:**
4. ✅ **Financial Extraction** (medium - number extraction)
5. ✅ **Historical Comparison** (harder - multi-year retrieval)

**Why These Next:**
- High user value
- Enable trend analysis
- Core CFO functionality

**Tasks:**
1. Build `MultiYearRetriever`
2. Create `FinancialExtractor`
3. Build `HistoricalComparator`
4. Add specialized prompts
5. Comprehensive testing

**Deliverables:**
- Multi-year retrieval working
- Financial extraction working
- Trend analysis working
- Test suite
- Documentation

**Effort:** 5-7 days

---

### **Phase 4: Advanced Capabilities (Week 3-4)** ⭐⭐⭐

**Goal:** Add remaining capabilities

**Capabilities:**
6. ✅ **Peer Benchmarking** (harder - multi-company)
7. ✅ **Sentiment Analysis** (medium - LLM-based)
8. ✅ **Compliance Review** (easy - section filtering)

**Tasks:**
1. Build `MultiCompanyRetriever`
2. Create `SentimentAnalyzer`
3. Build `PeerBenchmarker`
4. Add compliance filters
5. Complete testing

**Deliverables:**
- All 8 capabilities working
- Complete test coverage
- Full documentation

**Effort:** 5-7 days

---

### **Phase 5: Polish & Production (Week 4)** ⭐

**Goal:** Production-ready system

**Tasks:**
1. Performance optimization
2. Error handling
3. UI updates (Streamlit examples)
4. Comprehensive testing
5. Documentation
6. Demo creation

**Deliverables:**
- Production-ready code
- Complete test suite
- User documentation
- Demo notebook/video

**Effort:** 3-4 days

---

## 📊 EXAMPLE IMPLEMENTATIONS

### **Example 1: Disclosure Summarization (Quick Win)**

```python
class DisclosureSummarizer:
    """Summarize specific disclosure types"""
    
    DISCLOSURE_TYPES = {
        'risk': 'Item 1A',
        'business': 'Item 1',
        'mda': 'Item 7',
        'controls': 'Item 9A',
        'legal': 'Item 3'
    }
    
    def summarize(
        self,
        company: str,
        year: int,
        disclosure_type: str
    ) -> Summary:
        # 1. Retrieve relevant section
        section = self.DISCLOSURE_TYPES[disclosure_type]
        chunks = self.retriever.retrieve(
            query=f"summarize {disclosure_type}",
            companies=[company],
            years=[year],
            sections=[section]
        )
        
        # 2. Generate summary with specialized prompt
        summary = self.generator.generate(
            query=f"Summarize all {disclosure_type} disclosures",
            chunks=chunks,
            prompt_type='disclosure_summary'
        )
        
        return summary
```

### **Example 2: Historical Comparison**

```python
class HistoricalComparator:
    """Compare metrics across years"""
    
    def compare(
        self,
        company: str,
        metric: str,
        years: List[int]
    ) -> ComparisonResult:
        # 1. Retrieve same section for all years
        data = {}
        for year in years:
            chunks = self.retriever.retrieve(
                query=f"{metric} {year}",
                companies=[company],
                years=[year],
                sections=['Item 7']  # MD&A
            )
            data[year] = self._extract_metric(chunks, metric)
        
        # 2. Calculate changes
        changes = {}
        years_sorted = sorted(years)
        for i in range(1, len(years_sorted)):
            prev_year = years_sorted[i-1]
            curr_year = years_sorted[i]
            if data[prev_year] and data[curr_year]:
                change = ((data[curr_year] - data[prev_year]) / 
                         data[prev_year] * 100)
                changes[f"{prev_year}-{curr_year}"] = change
        
        # 3. Identify trend
        if len(changes) > 0:
            avg_change = sum(changes.values()) / len(changes)
            if avg_change > 5:
                trend = "Increasing"
            elif avg_change < -5:
                trend = "Decreasing"
            else:
                trend = "Stable"
        else:
            trend = "Unknown"
        
        # 4. Generate insights with LLM
        insights = self.generator.generate(
            query=f"Analyze {metric} trend for {company}",
            chunks=chunks,
            prompt_type='historical_comparison',
            context={
                'data': data,
                'changes': changes,
                'trend': trend
            }
        )
        
        return ComparisonResult(
            data=data,
            changes=changes,
            trend=trend,
            insights=insights
        )
```

### **Example 3: Peer Benchmarking**

```python
class PeerBenchmarker:
    """Compare across companies"""
    
    def benchmark(
        self,
        companies: List[str],
        metric: str,
        year: int
    ) -> BenchmarkResult:
        # 1. Retrieve for all companies
        data = {}
        all_chunks = []
        
        for company in companies:
            chunks = self.retriever.retrieve(
                query=f"{company} {metric} {year}",
                companies=[company],
                years=[year],
                sections=['Item 7']
            )
            data[company] = self._extract_metric(chunks, metric)
            all_chunks.extend(chunks)
        
        # 2. Rank companies
        ranking = sorted(
            data.items(),
            key=lambda x: x[1] if x[1] else 0,
            reverse=True
        )
        
        # 3. Calculate statistics
        values = [v for v in data.values() if v is not None]
        if values:
            stats = {
                'mean': sum(values) / len(values),
                'max': max(values),
                'min': min(values),
                'range': max(values) - min(values)
            }
        else:
            stats = {}
        
        # 4. Generate competitive insights
        insights = self.generator.generate(
            query=f"Compare {metric} across {', '.join(companies)}",
            chunks=all_chunks,
            prompt_type='peer_benchmark',
            context={
                'ranking': ranking,
                'stats': stats
            }
        )
        
        return BenchmarkResult(
            ranking=ranking,
            stats=stats,
            insights=insights
        )
```

---

## 🧪 TESTING STRATEGY

### **Test Queries for Each Capability:**

```python
TEST_QUERIES = {
    'disclosure_summary': [
        "Summarize all major risk factors for Apple in 2022",
        "What are the key risks disclosed by Microsoft?",
        "Give me an overview of Google's business description"
    ],
    
    'esg_regulatory': [
        "Summarize Apple's ESG commitments in 2022",
        "What regulatory risks did Microsoft disclose?",
        "Show environmental and social disclosures for Google"
    ],
    
    'board_briefing': [
        "Create an executive overview of Apple's 2022 10-K",
        "Generate a board briefing from Microsoft's filing",
        "Summarize key points for executive presentation"
    ],
    
    'financial_extraction': [
        "What was Apple's net cash flow in 2022?",
        "What was Microsoft's R&D expense last year?",
        "Show me Amazon's capital expenditure in 2021"
    ],
    
    'historical_comparison': [
        "How did Apple's R&D expense change over the last 3 years?",
        "Compare Microsoft's revenue growth from 2020 to 2022",
        "Show Amazon's CAPEX trend over 4 years"
    ],
    
    'peer_benchmark': [
        "Compare Apple and Microsoft's debt-to-equity ratios",
        "How does Google's R&D spending compare to peers?",
        "Rank tech companies by revenue growth"
    ],
    
    'sentiment_analysis': [
        "Analyze the CEO's tone in Apple's 2022 MD&A vs 2021",
        "How did Microsoft's outlook change year-over-year?",
        "Compare sentiment in risk sections across years"
    ],
    
    'compliance_review': [
        "List SOX compliance disclosures for Apple",
        "What material weaknesses did Microsoft report?",
        "Summarize internal control assessments"
    ]
}
```

---

## 💡 QUICK WINS (Start Here) ⭐

### **Week 1 Quick Wins - 3 Capabilities in 3-4 Days:**

#### **1. Disclosure Summarization** ✅
**Why Easy:**
- Already mostly working
- Just add better formatting
- Use existing retrieval

**Implementation:**
```python
# Just add new prompt template
DISCLOSURE_SUMMARY_PROMPT = """
Provide a comprehensive summary of all disclosures...
[Structured format with key points]
"""
```

**Effort:** 1 day

---

#### **2. ESG & Regulatory** ✅
**Why Easy:**
- Filter by section keywords
- Use existing retrieval
- Simple prompt

**Implementation:**
```python
# Filter for ESG keywords
esg_keywords = ['environmental', 'climate', 'sustainability', 
                'social', 'governance', 'ESG']

# Retrieve and summarize
chunks = retriever.retrieve(
    query=query,
    sections=['Item 1', 'Item 1A']
)
```

**Effort:** 1 day

---

#### **3. Board Briefing** ✅
**Why Easy:**
- New prompt template
- Executive summary format
- Use existing data

**Implementation:**
```python
BOARD_BRIEFING_PROMPT = """
Create an executive overview suitable for board presentation...

FORMAT:
- Executive Summary (3-5 bullets)
- Key Highlights
- Risk Overview
- Strategic Priorities
- Financial Snapshot
"""
```

**Effort:** 1 day

---

**Total Week 1:** 3 capabilities, 3-4 days, immediate value!

---

## 🚀 RECOMMENDED APPROACH

### **4-Week Plan (Recommended)**

**Week 1: Quick Wins** (3 capabilities)
- Disclosure Summarization
- ESG & Regulatory
- Board Briefing
- **Deliverable:** 3 working capabilities

**Week 2: High-Value** (2 capabilities)
- Financial Extraction
- Historical Comparison
- **Deliverable:** 5 total capabilities

**Week 3: Advanced** (3 capabilities)
- Peer Benchmarking
- Sentiment Analysis
- Compliance Review
- **Deliverable:** 8 total capabilities

**Week 4: Polish**
- Testing
- Documentation
- UI updates
- **Deliverable:** Production-ready system

---

## 📈 SUCCESS METRICS

### **Quality Metrics:**

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Accuracy** | >90% | Manual review of answers |
| **Completeness** | >85% | All relevant data included |
| **Relevance** | >90% | Answer addresses question |
| **Source Quality** | 100% | All claims cited |
| **Format Quality** | >95% | Professional presentation |

### **Performance Metrics:**

| Metric | Target | Current |
|--------|--------|---------|
| **Response Time** | <20s | ~17s |
| **Retrieval Time** | <3s | ~2s |
| **Generation Time** | <15s | ~15s |
| **Success Rate** | >95% | 100% |

---

## 📋 DECISION POINTS

### **Questions to Answer:**

1. **Which approach?**
   - ✅ Recommended: 4-week incremental (all 8 capabilities)
   - Or: 2-week MVP (top 5 capabilities only)

2. **Start with quick wins?**
   - ✅ Recommended: Yes (build momentum, early wins)
   - Or: Start with high-value (financial extraction first)

3. **How deep?**
   - ✅ Recommended: Basic first (keyword + LLM)
   - Or: Advanced (NLP extraction + statistics)

4. **UI updates?**
   - ✅ Recommended: Update Streamlit with examples
   - Or: Keep UI same, just add capabilities

---

## 🎯 NEXT STEPS

### **To Get Started:**

1. **✅ Confirm approach** - 4-week plan with quick wins first?
2. **✅ Create directory structure** - Set up new components
3. **✅ Start with classifier** - Build capability detection
4. **✅ Implement first 3** - Quick wins in Week 1
5. **✅ Test and iterate** - Validate each capability

### **Immediate Action:**

```bash
# Create new directory structure
mkdir -p rag_system/4_enhanced_capabilities
mkdir -p rag_system/4_enhanced_capabilities/classifiers
mkdir -p rag_system/4_enhanced_capabilities/retrievers
mkdir -p rag_system/4_enhanced_capabilities/analyzers
mkdir -p rag_system/4_enhanced_capabilities/prompts

# Start with classifier
cd rag_system/4_enhanced_capabilities/classifiers
touch enhanced_classifier.py
```

---

## 📊 SUMMARY

**Current State:**
- ✅ Basic RAG working perfectly
- ✅ Risk analysis excellent
- ✅ Comparison working
- ✅ Direct answers added

**Target State:**
- ✅ 8 advanced capabilities
- ✅ Multi-year analysis
- ✅ Peer benchmarking
- ✅ Sentiment analysis
- ✅ Financial extraction
- ✅ Board-ready outputs

**Path Forward:**
- **Week 1:** 3 quick wins (Disclosure, ESG, Briefing)
- **Week 2:** Financial + Historical
- **Week 3:** Peer + Sentiment + Compliance
- **Week 4:** Polish + Production

**Effort:** 4 weeks, 8 capabilities, production-ready

**First Step:** Create directory structure and start with quick wins

---

**🎯 Ready to start? Confirm the approach and we'll begin implementation!**
