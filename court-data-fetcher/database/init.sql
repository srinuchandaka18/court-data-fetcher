-- Queries table to log all search attempts
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type VARCHAR(100) NOT NULL,
    case_number VARCHAR(100) NOT NULL,
    filing_year INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_response TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    search_duration REAL
);

-- Case details table for parsed information
CREATE TABLE IF NOT EXISTS case_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER REFERENCES queries(id),
    parties_names TEXT,
    filing_date DATE,
    next_hearing_date DATE,
    case_status VARCHAR(100),
    pdf_links TEXT, -- JSON array of PDF URLs
    additional_info TEXT, -- JSON for extra fields
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for better query performance
CREATE INDEX IF NOT EXISTS idx_queries_case ON queries(case_type, case_number, filing_year);
CREATE INDEX IF NOT EXISTS idx_case_details_query ON case_details(query_id);
