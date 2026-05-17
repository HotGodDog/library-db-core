"""Database operations for library management system"""

import sqlite3
import os
from typing import List, Optional, Tuple


class Database:
    """SQLite database manager for library system"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses 'library.db' in current directory
        """
        if db_path is None:
            db_path = "library.db"
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def connect(self) -> "Database":
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        return self
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def _execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query"""
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor
    
    def _fetchall(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute query and fetch all results"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def _fetchone(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one result"""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def create_tables(self) -> None:
        """Create all database tables from schema.sql"""
        schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.cursor.executescript(f.read())
        self.connection.commit()
    
    def __enter__(self) -> "Database":
        """Context manager entry"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.close()