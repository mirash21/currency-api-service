import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from logger import logger, log_error, log_info
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            log_info(logger, "Successful connection to PostgreSQL database")
            return True
        except Exception as e:
            log_error(logger, "Database connection error", e)
            return False
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            log_info(logger, "Database connection closed")
        except Exception as e:
            log_error(logger, "Error closing connection", e)
    
    def create_tables(self):
        """Create database tables"""
        try:
            create_requests_table = """
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                error_message TEXT
            );
            """
            
            create_responses_table = """
            CREATE TABLE IF NOT EXISTS responses (
                id SERIAL PRIMARY KEY,
                request_id INTEGER REFERENCES requests(id) ON DELETE CASCADE,
                currency_code VARCHAR(3) NOT NULL,
                rate NUMERIC(16, 8) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            create_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON requests(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_responses_request_id ON responses(request_id);",
                "CREATE INDEX IF NOT EXISTS idx_responses_currency_code ON responses(currency_code);",
                "CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON responses(timestamp);"
            ]
            
            self.cursor.execute(create_requests_table)
            self.cursor.execute(create_responses_table)
            
            for index_query in create_indexes:
                self.cursor.execute(index_query)
            
            self.connection.commit()
            log_info(logger, "Tables created successfully in database")
            return True
            
        except Exception as e:
            log_error(logger, "Error creating tables", e)
            if self.connection:
                self.connection.rollback()
            return False
    
    def insert_request(self, request_type: str, status: str, error_message: Optional[str] = None) -> Optional[int]:
        """Insert request record and return its ID"""
        try:
            query = """
            INSERT INTO requests (request_type, status, error_message)
            VALUES (%s, %s, %s)
            RETURNING id;
            """
            self.cursor.execute(query, (request_type, status, error_message))
            request_id = self.cursor.fetchone()['id']
            self.connection.commit()
            return request_id
        except Exception as e:
            log_error(logger, "Error inserting request", e)
            if self.connection:
                self.connection.rollback()
            return None
    
    def insert_currency_rates(self, request_id: int, rates: Dict[str, float]) -> bool:
        """Insert currency rates"""
        try:
            query = """
            INSERT INTO responses (request_id, currency_code, rate)
            VALUES (%s, %s, %s);
            """
            
            for currency, rate in rates.items():
                self.cursor.execute(query, (request_id, currency, float(rate)))
            
            self.connection.commit()
            log_info(logger, f"Successfully saved {len(rates)} currency rates")
            return True
            
        except Exception as e:
            log_error(logger, "Error inserting currency rates", e)
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_request_history(self) -> List[Dict]:
        """Get request history with JOIN data"""
        try:
            query = """
            SELECT 
                r.id as request_id,
                r.timestamp as request_time,
                r.request_type,
                r.status,
                r.error_message,
                COUNT(res.id) as currency_count,
                STRING_AGG(
                    res.currency_code || ': ' || res.rate::TEXT, 
                    ', '
                ) as currency_rates
            FROM requests r
            LEFT JOIN responses res ON r.id = res.request_id
            GROUP BY r.id, r.timestamp, r.request_type, r.status, r.error_message
            ORDER BY r.timestamp DESC
            LIMIT 100;
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            log_error(logger, "Error getting request history", e)
            return []
    
    def get_latest_rates(self) -> List[Dict]:
        """Get latest currency rates"""
        try:
            query = """
            WITH latest_requests AS (
                SELECT DISTINCT ON (res.currency_code) 
                    res.currency_code,
                    res.rate,
                    res.timestamp,
                    r.status
                FROM responses res
                JOIN requests r ON res.request_id = r.id
                WHERE r.status = 'success'
                ORDER BY res.currency_code, res.timestamp DESC
            )
            SELECT * FROM latest_requests
            ORDER BY currency_code;
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            log_error(logger, "Error getting latest rates", e)
            return []

db_manager = DatabaseManager()