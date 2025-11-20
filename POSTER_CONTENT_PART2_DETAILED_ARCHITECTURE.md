# 📊 CFO Intelligence Platform - Detailed Technical Architecture (Part 2)

## COMPONENT BREAKDOWN

### **1. STRUCTURED QUERY PIPELINE (SQL)**

#### **Component 1.1: LangGraph State Machine**

**Purpose**: Orchestrate 5-node workflow for SQL queries

**Nodes**:
```
1. PLANNER
   - Input: User question + session context
   - LLM: GPT-4o-mini
   - Output: {intent, tickers, period, metrics}
   - Example: "Show Apple revenue Q1 2023"
     → {intent: "quarter_snapshot", ticker: "AAPL", 
        quarter: 1, fy: 2023, metrics: ["revenue_b"]}

2. TICKER RESOLVER
   - Input: Company names/aliases
   - Process: Fuzzy matching against dim_company table
   - Cache: Session memory for repeated queries
   - Example: "Apple" → "AAPL", "Microsoft" → "MSFT"

3. SQL GENERATOR
   - Template-First: Match to 29 pre-defined templates
   - LLM Fallback: Generate SQL for edge cases
   - Validation: Whitelist check (18 approved views)
   - Safety: Parameterized queries, no SELECT *
   - Example Template:
     SELECT revenue_b FROM quarterly_metrics
     WHERE ticker = :ticker AND quarter = :q AND fy = :fy

4. SQL EXECUTOR
   - Async execution: asyncpg connection pool
   - Timeout: 5 seconds
   - Connection pool: 10 connections
   - Read-only: SELECT-only permissions
   - Output: Raw data rows

5. RESPONSE FORMATTER
   - Input: Raw data + original question
   - LLM: GPT-4o-mini
   - Generate: Natural language + insights
   - Add: Growth deltas, peer ranks, risk flags
   - Append: Citations with provenance
```

**Performance**:
- Latency: 1-2 seconds
- Success rate: 91.9%
- LLM calls: 3 (planner, generator if needed, formatter)

#### **Component 1.2: SQL Templates**

**29 Pre-Defined Templates**:

```sql
-- Template 1: Quarter Snapshot
SELECT ticker, revenue_b, net_income_b, gross_margin_pct, roe
FROM quarterly_metrics
WHERE ticker = :ticker AND quarter = :q AND fy = :fy

-- Template 2: Annual Metrics
SELECT ticker, fy, revenue_b, net_income_b, operating_margin_pct
FROM annual_metrics
WHERE ticker = :ticker AND fy = :fy

-- Template 3: Growth QoQ/YoY
SELECT ticker, quarter, fy, revenue_b, 
       revenue_qoq_pct, revenue_yoy_pct
FROM vw_growth_quarter
WHERE ticker = :ticker AND quarter = :q AND fy = :fy

-- Template 4: Peer Comparison
SELECT ticker, revenue_b, revenue_rank, revenue_percentile
FROM vw_peer_stats_quarter
WHERE quarter = :q AND fy = :fy
ORDER BY revenue_rank

-- Template 5: Macro Context
SELECT ticker, quarter, fy, net_margin_pct, 
       gdp, cpi, unemployment_rate, fed_funds_rate
FROM vw_company_macro_context_quarter
WHERE ticker = :ticker AND quarter = :q AND fy = :fy

-- ... 24 more templates
```

**Coverage**: 90% of queries use templates (no LLM needed)

#### **Component 1.3: Safety & Validation**

**Whitelist Enforcement**:
```python
APPROVED_VIEWS = [
    'quarterly_metrics',
    'annual_metrics',
    'vw_growth_quarter',
    'vw_peer_stats_quarter',
    'vw_company_macro_context_quarter',
    'vw_macro_sensitivity_rolling',
    'vw_financial_health_quarter',
    'vw_outliers_quarter',
    # ... 10 more views
]

def validate_sql(sql_query):
    # Rule 1: SELECT-only
    if not sql_query.strip().upper().startswith('SELECT'):
        raise SecurityError("Only SELECT queries allowed")
    
    # Rule 2: No semicolons (single statement)
    if ';' in sql_query:
        raise SecurityError("Multiple statements not allowed")
    
    # Rule 3: Whitelist check
    for table in extract_tables(sql_query):
        if table not in APPROVED_VIEWS:
            raise SecurityError(f"Table {table} not whitelisted")
    
    # Rule 4: Column validation
    for column in extract_columns(sql_query):
        if not is_valid_column(column):
            raise SecurityError(f"Column {column} not in schema")
    
    # Rule 5: LIMIT enforcement
    if 'LIMIT' not in sql_query.upper():
        sql_query += ' LIMIT 200'
    
    return sql_query
```

---

### **2. UNSTRUCTURED QUERY PIPELINE (RAG)**

#### **Component 2.1: Enhanced Table Retriever**

**5-Step Process**:

```
STEP 1: QUERY ENHANCEMENT
- Add keywords: "table", "segment", "breakdown"
- Expand abbreviations: "GM" → "gross margin"
- Example: "Apple margin" → "Apple gross margin table breakdown"

STEP 2: VECTOR SEARCH
- Embedding model: text-embedding-3-small (1536 dims)
- Database: PostgreSQL with pgvector extension
- Index: HNSW (Hierarchical Navigable Small World)
- Similarity: Cosine similarity
- Retrieve: Top 10 chunks

STEP 3: RE-RANKING (Custom Algorithm)
Score calculation:
  base_score = semantic_similarity (0.0 - 1.0)
  
  # Table indicators
  base_score += 0.1 × count_table_markers(chunk)
  base_score += 0.05 × count_dollar_signs(chunk)
  base_score += 0.02 × count_percentages(chunk)
  
  # Segment breakdown bonus
  if "Products" in chunk AND "Services" in chunk:
      base_score += 0.3
  
  # Numeric density
  base_score += 0.01 × count_numbers(chunk)
  
  # Word count penalty (too short/long)
  if 50 < word_count < 500:
      base_score += 0.1
  
  final_score = base_score

Return: Top 3 chunks

STEP 4: LLM FORMATTING
- Input: Raw text chunks
- LLM: GPT-4o-mini
- Prompt: "Convert to clean markdown table"
- Output: Formatted table

STEP 5: WHITESPACE CLEANUP
- Remove extra blank lines
- Normalize spacing
- Format numbers consistently
```

**Performance**:
- Latency: 3-5 seconds
- Accuracy: 85% (vs 60% without re-ranking)

#### **Component 2.2: Vector Database**

**Schema**:
```sql
CREATE TABLE document_chunks (
    chunk_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100),
    ticker VARCHAR(10),
    fiscal_year INT,
    section VARCHAR(50),        -- "Item 7", "Item 8", etc.
    section_type VARCHAR(50),   -- "MD&A", "Financials", etc.
    chunk_text TEXT,
    embedding vector(1536),     -- OpenAI embeddings
    created_at TIMESTAMP DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Data Volume**:
- 5 companies × 6 years × ~500 chunks/year = ~15,000 chunks
- Average chunk size: 500 words
- Total storage: ~7.5M words

**Query Performance**:
- Vector search: < 100ms
- Re-ranking: < 50ms
- LLM formatting: 2-3s
- Total: 3-5s

---

### **3. HYBRID QUERY PIPELINE (SQL + RAG)**

#### **Component 3.1: Master Orchestrator**

**Architecture**:
```python
class MasterOrchestrator:
    def __init__(self):
        self.query_classifier = QueryClassifier()
        self.sql_agent = StructuredAgent()
        self.rag_agent = UnstructuredAgent()
        self.synthesizer = LLMSynthesizer()
    
    async def process_query(self, question):
        # Step 1: Classify query intent
        intent = self.query_classifier.classify(question)
        
        if intent == "HYBRID":
            # Step 2: Execute both agents sequentially
            sql_result = await self.sql_agent.execute(question)
            rag_result = await self.rag_agent.execute(question)
            
            # Step 3: Synthesize results
            final_response = self.synthesizer.combine(
                question=question,
                sql_result=sql_result,
                rag_result=rag_result
            )
            
            return final_response
        elif intent == "STRUCTURED":
            return await self.sql_agent.execute(question)
        else:  # UNSTRUCTURED
            return await self.rag_agent.execute(question)
```

#### **Component 3.2: Query Classifier**

**Classification Logic**:
```python
HYBRID_KEYWORDS = {
    'what drove', '10-k citations', 'citations',
    'macro context', 'macro', 'show me the numbers',
    'numbers and', 'context and numbers',
    'explain why', 'business drivers', 'strategic'
}

STRUCTURED_KEYWORDS = {
    'revenue', 'margin', 'income', 'roe', 'roa',
    'debt', 'assets', 'liabilities', 'cash flow',
    'q1', 'q2', 'q3', 'q4', 'fy', 'quarter', 'annual'
}

UNSTRUCTURED_KEYWORDS = {
    '10-k', 'strategy', 'risk', 'priorities',
    'segment', 'products', 'services', 'breakdown',
    'table', 'filing', 'disclosure'
}

def classify_query(question):
    question_lower = question.lower()
    
    # Check for hybrid indicators
    hybrid_score = sum(1 for kw in HYBRID_KEYWORDS 
                      if kw in question_lower)
    
    # Check for structured indicators
    structured_score = sum(1 for kw in STRUCTURED_KEYWORDS 
                          if kw in question_lower)
    
    # Check for unstructured indicators
    unstructured_score = sum(1 for kw in UNSTRUCTURED_KEYWORDS 
                            if kw in question_lower)
    
    # Decision logic
    if hybrid_score >= 2:
        return "HYBRID"
    elif structured_score > unstructured_score:
        return "STRUCTURED"
    else:
        return "UNSTRUCTURED"
```

**Accuracy**: 98% on test set

#### **Component 3.3: LLM Synthesizer**

**Synthesis Prompt**:
```python
SYNTHESIS_PROMPT = """
You are a CFO-level financial analyst. Your task is to synthesize 
a comprehensive answer by combining structured data and unstructured insights.

QUESTION:
{question}

STRUCTURED DATA (from SQL database):
{sql_result}

UNSTRUCTURED INSIGHTS (from 10-K filings):
{rag_result}

INSTRUCTIONS:
1. Lead with the numbers (quantitative data from SQL)
2. Explain the context (qualitative insights from 10-K)
3. Connect the dots (how context explains the numbers)
4. Be concise (max 800 tokens)
5. Cite both sources

FORMAT:
### [Metric Name]
**Numbers**: [SQL data with specific values]

**Context**: [10-K insights explaining the numbers]

**Key Takeaway**: [One-sentence synthesis]

**Sources**: SQL Database, SEC 10-K Filing (FY [year])
"""

def synthesize(question, sql_result, rag_result):
    messages = [
        {"role": "system", "content": "You are a CFO analyst."},
        {"role": "user", "content": SYNTHESIS_PROMPT.format(
            question=question,
            sql_result=sql_result,
            rag_result=rag_result
        )}
    ]
    
    response = llm.invoke(messages, max_tokens=800)
    return response.content
```

**Example Output**:
```
### Apple Revenue Growth Analysis (FY 2023)

**Numbers**: Apple reported $383.29B revenue in FY 2023, 
up 7.8% YoY from $355.35B in FY 2022. Gross margin improved 
from 41.8% to 43.3%.

**Context**: According to the 10-K filing, growth was driven by:
1. Services segment expansion (71.7% margin)
2. iPhone ecosystem strength
3. Wearables and accessories growth

**Key Takeaway**: Apple's margin expansion reflects successful 
shift toward high-margin services, offsetting hardware commoditization.

**Sources**: SQL Database (quarterly_metrics), SEC 10-K Filing (FY 2023)
```

---

### **4. VISUALIZATION PIPELINE**

#### **Component 4.1: VizDataFetcher**

**Purpose**: Determine if query is visualizable and fetch extended data

**Logic**:
```python
class VizDataFetcher:
    def is_visualizable(self, query_metadata):
        """
        Check if query can be visualized
        """
        # Must have time series or comparison
        has_time_series = (
            'quarter' in query_metadata or 
            'fy' in query_metadata or
            'multiple periods' in query_metadata
        )
        
        has_comparison = len(query_metadata.get('tickers', [])) > 1
        
        # Must have numeric metrics
        has_metrics = any(
            metric in query_metadata.get('metrics', [])
            for metric in ['revenue_b', 'net_income_b', 'margin']
        )
        
        return (has_time_series or has_comparison) and has_metrics
    
    def fetch_extended_data(self, query_metadata):
        """
        Fetch 5 years of historical data for visualization
        """
        ticker = query_metadata['ticker']
        metric = query_metadata['metrics'][0]
        
        # Query last 20 quarters (5 years)
        sql = f"""
        SELECT quarter, fy, {metric}
        FROM quarterly_metrics
        WHERE ticker = :ticker
        ORDER BY fy DESC, quarter DESC
        LIMIT 20
        """
        
        return execute_query(sql, {'ticker': ticker})
```

#### **Component 4.2: Chart Configuration**

**Chart Types**:
```python
def generate_chart_config(data, query_metadata):
    """
    Generate Plotly chart configuration
    """
    metric = query_metadata['metrics'][0]
    tickers = query_metadata.get('tickers', [])
    
    if len(tickers) > 1:
        # Multi-company comparison (bar chart)
        return {
            'type': 'bar',
            'x': tickers,
            'y': [data[t][metric] for t in tickers],
            'title': f'{metric.replace("_", " ").title()} Comparison',
            'yaxis': {'title': format_metric_name(metric)}
        }
    else:
        # Time series (line chart)
        return {
            'type': 'line',
            'x': [f"Q{q} {fy}" for q, fy in data['periods']],
            'y': data[metric],
            'title': f'{tickers[0]} {metric.replace("_", " ").title()} Trend',
            'yaxis': {'title': format_metric_name(metric)},
            'markers': True
        }
```

**Y-Axis Formatting**:
```python
def format_y_axis(metric_name, values):
    """
    Smart Y-axis formatting
    """
    max_value = max(values)
    
    if 'revenue' in metric_name or 'income' in metric_name:
        # Dollar formatting
        if max_value > 1:  # Billions
            return {'tickformat': '$,.1fB', 'range': [0, max_value * 1.1]}
        else:  # Millions
            return {'tickformat': '$,.0fM', 'range': [0, max_value * 1.1]}
    
    elif 'margin' in metric_name or 'pct' in metric_name:
        # Percentage formatting
        return {'tickformat': '.1%', 'range': [0, max_value * 1.1]}
    
    else:
        # Default numeric
        return {'tickformat': ',.2f', 'range': [0, max_value * 1.1]}
```

---

### **5. DATA SOURCES & CITATIONS**

#### **Component 5.1: Citation Fetcher**

**Purpose**: Track provenance for every data point

**Schema**:
```sql
CREATE TABLE fact_data_sources (
    source_id VARCHAR(50) PRIMARY KEY,
    source_name VARCHAR(100),
    source_type VARCHAR(50),  -- 'API', 'FILE', 'MANUAL'
    description TEXT,
    url VARCHAR(500),
    last_updated TIMESTAMP
);

-- Example rows:
INSERT INTO fact_data_sources VALUES
('ALPHAVANTAGE_FIN', 'Alpha Vantage Financial Statements', 'API', 
 'Quarterly and annual financial statements', 
 'https://www.alphavantage.co', '2025-02-10'),
('FRED', 'Federal Reserve Economic Data', 'API',
 'Macro-economic indicators',
 'https://fred.stlouisfed.org', '2025-02-11'),
('YF', 'Yahoo Finance', 'API',
 'Daily stock prices',
 'https://finance.yahoo.com', '2025-02-10');
```

**Citation Logic**:
```python
def fetch_citations(query_metadata, columns_used):
    """
    Map columns to data sources
    """
    citations = []
    
    # Financial metrics → Alpha Vantage
    financial_columns = ['revenue_b', 'net_income_b', 'gross_margin_pct']
    if any(col in columns_used for col in financial_columns):
        citations.append({
            'source': 'ALPHAVANTAGE_FIN',
            'type': 'as_reported',
            'date': '2025-02-10'
        })
    
    # Stock prices → Yahoo Finance
    if any('price' in col for col in columns_used):
        citations.append({
            'source': 'YF',
            'type': 'stock prices',
            'date': '2025-02-10'
        })
    
    # Macro indicators → FRED
    macro_columns = ['gdp', 'cpi', 'unemployment_rate']
    if any(col in columns_used for col in macro_columns):
        citations.append({
            'source': 'FRED',
            'type': 'macro indicators',
            'date': '2025-02-11'
        })
    
    return format_citation_line(citations)

def format_citation_line(citations):
    """
    Format: "Sources: ALPHAVANTAGE_FIN (as_reported, 2025-02-10); YF; FRED"
    """
    parts = []
    for c in citations:
        if 'type' in c and 'date' in c:
            parts.append(f"{c['source']} ({c['type']}, {c['date']})")
        else:
            parts.append(c['source'])
    
    return "Sources: " + "; ".join(parts)
```

---

## PERFORMANCE OPTIMIZATION

### **1. Caching Strategy**

```python
# Schema cache (loaded at startup)
SCHEMA_CACHE = load_schema_from_db()  # 18 views, 500+ columns

# Ticker cache (loaded at startup)
TICKER_CACHE = {
    'apple': 'AAPL',
    'microsoft': 'MSFT',
    'amazon': 'AMZN',
    'google': 'GOOG',
    'meta': 'META'
}

# Template cache (loaded at startup)
TEMPLATE_CACHE = load_templates_from_json()  # 29 templates

# Session memory (per-user)
SESSION_CACHE = {}  # {session_id: {tickers, period, surfaces}}
```

### **2. Connection Pooling**

```python
# PostgreSQL connection pool
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=2,
    max_size=10,
    command_timeout=5.0
)
```

### **3. Materialized Views**

```sql
-- Pre-computed joins (refreshed daily)
CREATE MATERIALIZED VIEW mv_financials_annual AS
SELECT 
    ticker, fy,
    SUM(revenue_b) as revenue_b,
    SUM(net_income_b) as net_income_b,
    AVG(gross_margin_pct) as gross_margin_pct
FROM quarterly_metrics
GROUP BY ticker, fy;

-- Speedup: 5-10x (complex joins → simple SELECT)
```

---

**End of Part 2**
