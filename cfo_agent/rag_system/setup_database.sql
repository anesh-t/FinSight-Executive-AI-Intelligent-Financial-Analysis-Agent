-- ============================================================================
-- SEC 10-K RAG SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Purpose: Complete schema for hybrid RAG system with vector embeddings
-- Database: PostgreSQL with pgvector extension (Supabase)
-- Date: 2025-10-26
-- ============================================================================

-- Enable pgvector extension (run once)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- TABLE 1: MAIN EMBEDDINGS TABLE
-- ============================================================================
-- Stores all 10-K text chunks with vector embeddings for semantic search

CREATE TABLE IF NOT EXISTS sec_10k_embeddings (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Company identification
    company TEXT NOT NULL,                      -- Original: "2024AMZN_10K"
    company_name TEXT NOT NULL,                 -- Normalized: "Amazon"
    ticker TEXT,                                -- Stock ticker: "AMZN"
    
    -- Temporal information
    fiscal_year INTEGER NOT NULL,               -- 2019-2024
    fiscal_year_end DATE,                       -- Exact fiscal year end date
    
    -- Section classification
    section TEXT NOT NULL,                      -- Raw: "Item 1A"
    section_type TEXT NOT NULL,                 -- Human-readable: "Risk Factors"
    
    -- Content hierarchy
    heading TEXT NOT NULL,                      -- Main section heading
    subheading TEXT,                            -- AI-generated subheading
    chunk_text TEXT NOT NULL,                   -- Full chunk content
    word_count INTEGER,                         -- Number of words
    
    -- Vector embedding
    embedding VECTOR(384) NOT NULL,             -- MiniLM-L6-v2 output (384 dims)
    
    -- Full-text search support
    full_text_search TSVECTOR,                  -- For hybrid search
    
    -- Chunk positioning (for context expansion)
    chunk_index INTEGER,                        -- Position in section (1, 2, 3...)
    chunk_total INTEGER,                        -- Total chunks in section
    
    -- Metadata
    source_file TEXT,                           -- Original JSON filename
    processing_date TIMESTAMP DEFAULT NOW(),    -- When processed
    pipeline_version TEXT DEFAULT '1.0.0',      -- Pipeline version
    
    -- Constraints
    CONSTRAINT unique_chunk UNIQUE (company, fiscal_year, section, chunk_index)
);

-- ============================================================================
-- TABLE 2: COMPANY MASTER
-- ============================================================================
-- Normalize company names and aliases for accurate matching

CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,              -- For matching: "Apple"
    aliases TEXT[],                             -- ["Apple", "Apple Inc", "AAPL"]
    industry TEXT,
    sector TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert company data
INSERT INTO companies (ticker, company_name, normalized_name, aliases, sector) VALUES
('AMZN', 'Amazon.com, Inc.', 'Amazon', 
 ARRAY['Amazon', 'AMZN', 'Amazon.com', 'Amazon Inc'], 'Technology'),
('AAPL', 'Apple Inc.', 'Apple', 
 ARRAY['Apple', 'AAPL', 'Apple Inc', 'Apple Inc.'], 'Technology'),
('GOOGL', 'Alphabet Inc.', 'Google', 
 ARRAY['Google', 'Alphabet', 'GOOGL', 'GOOG', 'Alphabet Inc'], 'Technology'),
('META', 'Meta Platforms, Inc.', 'Meta', 
 ARRAY['Meta', 'Facebook', 'META', 'FB', 'Meta Platforms'], 'Technology'),
('MSFT', 'Microsoft Corporation', 'Microsoft', 
 ARRAY['Microsoft', 'MSFT', 'Microsoft Corp'], 'Technology')
ON CONFLICT (ticker) DO NOTHING;

-- ============================================================================
-- TABLE 3: SECTION MAPPING
-- ============================================================================
-- Maps 10-K sections to human-readable names and keywords

CREATE TABLE IF NOT EXISTS section_mapping (
    section_code TEXT PRIMARY KEY,              -- "Item 1A"
    section_name TEXT NOT NULL,                 -- "Risk Factors"
    description TEXT,                           -- Detailed description
    keywords TEXT[],                            -- Search keywords
    typical_queries TEXT[]                      -- Example user queries
);

-- Insert section mappings
INSERT INTO section_mapping (section_code, section_name, description, keywords, typical_queries) VALUES
('Item 1', 'Business', 
 'Description of business operations, products, and services',
 ARRAY['business', 'operations', 'products', 'services', 'strategy', 'model'],
 ARRAY['What does the company do?', 'Business model', 'Products and services', 'Company operations']),

('Item 1A', 'Risk Factors',
 'Risk factors that could materially affect the business',
 ARRAY['risk', 'risks', 'uncertainty', 'factors', 'challenges', 'threats', 'concerns'],
 ARRAY['What are the risks?', 'Risk factors', 'Challenges faced', 'Threats', 'Uncertainties']),

('Item 1B', 'Unresolved Staff Comments',
 'Unresolved comments from SEC staff',
 ARRAY['sec', 'comments', 'staff'],
 ARRAY['SEC comments', 'Staff comments']),

('Item 2', 'Properties',
 'Physical properties and facilities',
 ARRAY['properties', 'facilities', 'real estate', 'offices', 'locations'],
 ARRAY['Office locations', 'Facilities', 'Real estate']),

('Item 3', 'Legal Proceedings',
 'Material pending legal proceedings',
 ARRAY['legal', 'litigation', 'lawsuits', 'proceedings', 'cases'],
 ARRAY['Lawsuits', 'Legal issues', 'Litigation']),

('Item 4', 'Mine Safety Disclosures',
 'Mine safety violations or other regulatory matters',
 ARRAY['mine', 'safety'],
 ARRAY['Mine safety']),

('Item 5', 'Market for Registrant Common Equity',
 'Market information about common equity',
 ARRAY['stock', 'equity', 'market', 'shares', 'dividends'],
 ARRAY['Stock information', 'Share price', 'Dividends']),

('Item 6', 'Selected Financial Data',
 'Selected financial data for the past 5 years',
 ARRAY['financial', 'data', 'historical', 'five year'],
 ARRAY['Historical financials', 'Five year data']),

('Item 7', 'MD&A',
 'Management Discussion and Analysis of financial condition and results',
 ARRAY['management', 'discussion', 'analysis', 'performance', 'results', 'revenue', 'mda'],
 ARRAY['Financial performance', 'Revenue analysis', 'Management discussion', 'How did they perform?']),

('Item 7A', 'Quantitative and Qualitative Disclosures',
 'Disclosures about market risk',
 ARRAY['market risk', 'quantitative', 'qualitative', 'disclosures'],
 ARRAY['Market risk', 'Risk disclosures']),

('Item 8', 'Financial Statements',
 'Financial statements and supplementary data',
 ARRAY['financial', 'statements', 'balance sheet', 'income', 'cash flow'],
 ARRAY['Financial statements', 'Balance sheet', 'Income statement']),

('Item 9', 'Changes and Disagreements',
 'Changes in and disagreements with accountants',
 ARRAY['accounting', 'disagreements', 'changes'],
 ARRAY['Accounting changes', 'Auditor changes']),

('Item 9A', 'Controls and Procedures',
 'Controls and procedures for financial reporting',
 ARRAY['controls', 'procedures', 'internal controls', 'sox'],
 ARRAY['Internal controls', 'SOX compliance']),

('Item 9B', 'Other Information',
 'Other information not reported elsewhere',
 ARRAY['other', 'additional'],
 ARRAY['Other information']),

('Item 10', 'Directors and Officers',
 'Information about directors, executive officers and corporate governance',
 ARRAY['directors', 'officers', 'executives', 'governance', 'board'],
 ARRAY['Board of directors', 'Executives', 'Leadership']),

('Item 11', 'Executive Compensation',
 'Executive compensation information',
 ARRAY['compensation', 'salary', 'pay', 'executive'],
 ARRAY['Executive pay', 'Compensation', 'Salaries']),

('Item 12', 'Security Ownership',
 'Security ownership of certain beneficial owners and management',
 ARRAY['ownership', 'shareholders', 'beneficial owners'],
 ARRAY['Stock ownership', 'Major shareholders']),

('Item 13', 'Certain Relationships',
 'Certain relationships and related transactions',
 ARRAY['relationships', 'related party', 'transactions'],
 ARRAY['Related party transactions']),

('Item 14', 'Principal Accountant Fees',
 'Principal accountant fees and services',
 ARRAY['accountant', 'audit', 'fees'],
 ARRAY['Audit fees', 'Accountant fees']),

('Item 15', 'Exhibits',
 'Exhibits and financial statement schedules',
 ARRAY['exhibits', 'schedules'],
 ARRAY['Exhibits']),

('Item 16', 'Form 10-K Summary',
 'Summary of Form 10-K',
 ARRAY['summary', 'signatures'],
 ARRAY['Summary', 'Signatures'])
ON CONFLICT (section_code) DO NOTHING;

-- ============================================================================
-- TABLE 4: QUERY CACHE (Optional - for performance)
-- ============================================================================
-- Cache common queries to reduce LLM/embedding costs

CREATE TABLE IF NOT EXISTS query_cache (
    id BIGSERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash TEXT UNIQUE NOT NULL,            -- MD5 hash of query
    query_embedding VECTOR(384),                -- Cached embedding
    parsed_query JSONB,                         -- Cached parse result
    response JSONB,                             -- Cached full response
    created_at TIMESTAMP DEFAULT NOW(),
    hit_count INTEGER DEFAULT 1,
    last_accessed TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Metadata indexes for filtering
CREATE INDEX IF NOT EXISTS idx_company_name ON sec_10k_embeddings(company_name);
CREATE INDEX IF NOT EXISTS idx_ticker ON sec_10k_embeddings(ticker);
CREATE INDEX IF NOT EXISTS idx_fiscal_year ON sec_10k_embeddings(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_section ON sec_10k_embeddings(section);
CREATE INDEX IF NOT EXISTS idx_section_type ON sec_10k_embeddings(section_type);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_company_year 
    ON sec_10k_embeddings(company_name, fiscal_year);

CREATE INDEX IF NOT EXISTS idx_company_year_section 
    ON sec_10k_embeddings(company_name, fiscal_year, section_type);

CREATE INDEX IF NOT EXISTS idx_year_section 
    ON sec_10k_embeddings(fiscal_year, section_type);

-- Vector similarity search index (HNSW - fast but uses more memory)
CREATE INDEX IF NOT EXISTS idx_embedding_hnsw 
    ON sec_10k_embeddings 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat index (less memory, slightly slower)
-- Uncomment if HNSW uses too much memory
-- CREATE INDEX IF NOT EXISTS idx_embedding_ivfflat 
--     ON sec_10k_embeddings 
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_full_text_search 
    ON sec_10k_embeddings 
    USING GIN(full_text_search);

-- Chunk positioning index (for context expansion)
CREATE INDEX IF NOT EXISTS idx_chunk_position 
    ON sec_10k_embeddings(company, fiscal_year, section, chunk_index);

-- ============================================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- ============================================================================

-- Function to update full-text search vector automatically
CREATE OR REPLACE FUNCTION update_full_text_search()
RETURNS TRIGGER AS $$
BEGIN
    NEW.full_text_search := 
        setweight(to_tsvector('english', COALESCE(NEW.heading, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.subheading, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.chunk_text, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update full-text search on insert/update
CREATE TRIGGER trigger_update_full_text_search
BEFORE INSERT OR UPDATE ON sec_10k_embeddings
FOR EACH ROW
EXECUTE FUNCTION update_full_text_search();

-- Function to get similar chunks (helper for semantic search)
CREATE OR REPLACE FUNCTION semantic_search(
    query_embedding VECTOR(384),
    match_company TEXT DEFAULT NULL,
    match_year INTEGER DEFAULT NULL,
    match_section TEXT DEFAULT NULL,
    match_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    company_name TEXT,
    fiscal_year INTEGER,
    section TEXT,
    section_type TEXT,
    heading TEXT,
    subheading TEXT,
    chunk_text TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.company_name,
        e.fiscal_year,
        e.section,
        e.section_type,
        e.heading,
        e.subheading,
        e.chunk_text,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM sec_10k_embeddings e
    WHERE 
        (match_company IS NULL OR e.company_name = match_company)
        AND (match_year IS NULL OR e.fiscal_year = match_year)
        AND (match_section IS NULL OR e.section_type = match_section)
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Latest year data for each company
CREATE OR REPLACE VIEW latest_company_data AS
SELECT DISTINCT ON (company_name)
    company_name,
    fiscal_year,
    COUNT(*) as total_chunks
FROM sec_10k_embeddings
GROUP BY company_name, fiscal_year
ORDER BY company_name, fiscal_year DESC;

-- View: Section statistics
CREATE OR REPLACE VIEW section_statistics AS
SELECT 
    section_type,
    company_name,
    fiscal_year,
    COUNT(*) as chunk_count,
    SUM(word_count) as total_words,
    AVG(word_count) as avg_words_per_chunk
FROM sec_10k_embeddings
GROUP BY section_type, company_name, fiscal_year
ORDER BY company_name, fiscal_year, section_type;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
    AND tablename IN ('sec_10k_embeddings', 'companies', 'section_mapping');

-- Check if pgvector extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- ============================================================================
-- CLEANUP (Optional - use with caution!)
-- ============================================================================

-- Uncomment below to drop all tables and start fresh
-- DROP TABLE IF EXISTS query_cache CASCADE;
-- DROP TABLE IF EXISTS sec_10k_embeddings CASCADE;
-- DROP TABLE IF EXISTS section_mapping CASCADE;
-- DROP TABLE IF EXISTS companies CASCADE;
-- DROP FUNCTION IF EXISTS semantic_search CASCADE;
-- DROP FUNCTION IF EXISTS update_full_text_search CASCADE;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
