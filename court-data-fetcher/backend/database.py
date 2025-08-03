import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path='database/court_data.db'):
        self.db_path = db_path.replace('/', '\\')  # Windows path fix
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Execute schema
        schema_path = os.path.join('database', 'init.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
        else:
            # Fallback schema
            schema = """
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
            
            CREATE TABLE IF NOT EXISTS case_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER REFERENCES queries(id),
                parties_names TEXT,
                filing_date DATE,
                next_hearing_date DATE,
                case_status VARCHAR(100),
                pdf_links TEXT,
                additional_info TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        
        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()
        print(f"✓ Database initialized at: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def log_query(self, case_type, case_number, filing_year, raw_response=None, 
                  status='pending', error_message=None, search_duration=None):
        """Log a query attempt"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO queries (case_type, case_number, filing_year, raw_response, 
                                   status, error_message, search_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (case_type, case_number, filing_year, raw_response, 
                  status, error_message, search_duration))
            
            query_id = cursor.lastrowid
            conn.commit()
            return query_id
    
    def update_query_status(self, query_id, status, raw_response=None, error_message=None):
        """Update query status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE queries 
                SET status = ?, raw_response = COALESCE(?, raw_response), 
                    error_message = COALESCE(?, error_message)
                WHERE id = ?
            """, (status, raw_response, error_message, query_id))
            conn.commit()
    
    def save_case_details(self, query_id, parties_names, filing_date, 
                         next_hearing_date, case_status, pdf_links, additional_info=None):
        """Save parsed case details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO case_details (query_id, parties_names, filing_date, 
                                        next_hearing_date, case_status, pdf_links, additional_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (query_id, parties_names, filing_date, next_hearing_date, 
                  case_status, json.dumps(pdf_links), json.dumps(additional_info)))
            conn.commit()
    
    def get_recent_queries(self, limit=10):
        """Get recent successful queries for display"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.*, cd.parties_names, cd.case_status 
                FROM queries q
                LEFT JOIN case_details cd ON q.id = cd.query_id
                WHERE q.status = 'success'
                ORDER BY q.timestamp DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

if __name__ == "__main__":
    # Test database creation
    db = DatabaseManager()
    print("Database test completed successfully!")
