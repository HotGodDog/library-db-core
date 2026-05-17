"""Database operations for library management system"""

import sqlite3
import os
from typing import List, Optional, Tuple

from .models import Book


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
    
    # КНИГА
    
    def add_book(self, book: Book) -> int:
        """Add new book to database
        
        Args:
            book: Book instance to add
            
        Returns:
            ID of created book
        """
        self._execute("""
            INSERT INTO books (title, author_id, category_id, publisher_id, 
                             year_published, pages, total_copies, available, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (book.title, book.author_id, book.category_id, book.publisher_id,
              book.year_published, book.pages, book.total_copies, book.available, 
              book.description))
        return self.cursor.lastrowid
    
    def get_book(self, book_id: int) -> Optional[Book]:
        """Get book by ID
        
        Args:
            book_id: Book ID
            
        Returns:
            Book instance or None if not found
        """
        row = self._fetchone("""
            SELECT book_id, title, author_id, category_id, publisher_id,
                   year_published, pages, total_copies, available, description
            FROM books WHERE book_id = ?
        """, (book_id,))
        
        if row:
            return Book(
                title=row["title"],
                author_id=row["author_id"],
                category_id=row["category_id"],
                publisher_id=row["publisher_id"],
                year_published=row["year_published"],
                pages=row["pages"],
                total_copies=row["total_copies"],
                description=row["description"],
                book_id=row["book_id"],
                available=row["available"]
            )
        return None
    
    def get_all_books(self) -> List[Book]:
        """Get all books
        
        Returns:
            List of Book instances
        """
        rows = self._fetchall("""
            SELECT book_id, title, author_id, category_id, publisher_id,
                   year_published, pages, total_copies, available, description
            FROM books ORDER BY title
        """)
        
        return [
            Book(
                title=row["title"],
                author_id=row["author_id"],
                category_id=row["category_id"],
                publisher_id=row["publisher_id"],
                year_published=row["year_published"],
                pages=row["pages"],
                total_copies=row["total_copies"],
                description=row["description"],
                book_id=row["book_id"],
                available=row["available"]
            )
            for row in rows
        ]
    


    def __enter__(self) -> "Database":
        """Context manager entry"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.close()