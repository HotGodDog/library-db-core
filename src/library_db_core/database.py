"""Database operations for library management system"""

import sqlite3
import os
from typing import List, Optional, Tuple
from datetime import datetime
from .models import Book, Employee, Reader, Loan


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
    
    # BOOK CRUD
    
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
    
    # READER CRUD
    
    def add_reader(self, reader: Reader) -> int:
        """Add new reader to database
        
        Args:
            reader: Reader instance to add
            
        Returns:
            ID of created reader
        """
        self._execute("""
            INSERT INTO readers (last_name, first_name, middle_name, passport_num,
                               phone, email, address, reg_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (reader.last_name, reader.first_name, reader.middle_name,
              reader.passport_num, reader.phone, reader.email, reader.address,
              reader.reg_date, 1 if reader.is_active else 0))
        return self.cursor.lastrowid
    
    def get_reader(self, reader_id: int) -> Optional[Reader]:
        """Get reader by ID"""
        row = self._fetchone("""
            SELECT reader_id, last_name, first_name, middle_name, passport_num,
                   phone, email, address, reg_date, is_active
            FROM readers WHERE reader_id = ?
        """, (reader_id,))
        
        if row:
            return Reader(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                passport_num=row["passport_num"],
                phone=row["phone"],
                email=row["email"],
                address=row["address"],
                reader_id=row["reader_id"],
                reg_date=row["reg_date"],
                is_active=bool(row["is_active"])
            )
        return None
    
    def get_all_readers(self) -> List[Reader]:
        """Get all readers"""
        rows = self._fetchall("""
            SELECT reader_id, last_name, first_name, middle_name, passport_num,
                   phone, email, address, reg_date, is_active
            FROM readers ORDER BY last_name
        """)
        
        return [
            Reader(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                passport_num=row["passport_num"],
                phone=row["phone"],
                email=row["email"],
                address=row["address"],
                reader_id=row["reader_id"],
                reg_date=row["reg_date"],
                is_active=bool(row["is_active"])
            )
            for row in rows
        ]
    
    # EMPLOYEE CRUD
    
    def add_employee(self, employee: Employee) -> int:
        """Add new employee to database
        
        Args:
            employee: Employee instance to add
            
        Returns:
            ID of created employee
        """
        self._execute("""
            INSERT INTO employees (last_name, first_name, middle_name, position_id,
                                 phone, email, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (employee.last_name, employee.first_name, employee.middle_name,
              employee.position_id, employee.phone, employee.email,
              1 if employee.is_active else 0))
        return self.cursor.lastrowid
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        row = self._fetchone("""
            SELECT employee_id, last_name, first_name, middle_name, position_id,
                   phone, email, is_active
            FROM employees WHERE employee_id = ?
        """, (employee_id,))
        
        if row:
            return Employee(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                position_id=row["position_id"],
                phone=row["phone"],
                email=row["email"],
                employee_id=row["employee_id"],
                is_active=bool(row["is_active"])
            )
        return None
    
    def get_all_employees(self) -> List[Employee]:
        """Get all employees"""
        rows = self._fetchall("""
            SELECT employee_id, last_name, first_name, middle_name, position_id,
                   phone, email, is_active
            FROM employees ORDER BY last_name
        """)
        
        return [
            Employee(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                position_id=row["position_id"],
                phone=row["phone"],
                email=row["email"],
                employee_id=row["employee_id"],
                is_active=bool(row["is_active"])
            )
            for row in rows
        ]

    # LOAN CRUD
    
    def issue_book(self, loan: Loan) -> int:
        """Issue book to reader
        
        Args:
            loan: Loan instance with book_id, reader_id, employee_id, due_date
            
        Returns:
            ID of created loan
        """
        self._execute("""
            INSERT INTO loans (book_id, reader_id, employee_id, loan_date, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (loan.book_id, loan.reader_id, loan.employee_id,
              loan.loan_date or datetime.now().strftime("%Y-%m-%d"),
              loan.due_date, "active"))
        return self.cursor.lastrowid
    
    def return_book(self, loan_id: int) -> None:
        """Return book by loan ID
        
        Args:
            loan_id: Loan ID to return
        """
        return_date = datetime.now().strftime("%Y-%m-%d")
        self._execute("""
            UPDATE loans SET return_date = ? WHERE loan_id = ?
        """, (return_date, loan_id))
    
    def get_loan(self, loan_id: int) -> Optional[Loan]:
        """Get loan by ID."""
        row = self._fetchone("""
            SELECT loan_id, book_id, reader_id, employee_id, loan_date,
                   due_date, return_date, status
            FROM loans WHERE loan_id = ?
        """, (loan_id,))
        
        if row:
            return Loan(
                book_id=row["book_id"],
                reader_id=row["reader_id"],
                employee_id=row["employee_id"],
                due_date=row["due_date"],
                loan_id=row["loan_id"],
                loan_date=row["loan_date"],
                return_date=row["return_date"],
                status=row["status"]
            )
        return None
    
    def get_all_loans(self) -> List[Loan]:
        """Get all loans"""
        rows = self._fetchall("""
            SELECT loan_id, book_id, reader_id, employee_id, loan_date,
                   due_date, return_date, status
            FROM loans ORDER BY loan_date DESC
        """)
        
        return [
            Loan(
                book_id=row["book_id"],
                reader_id=row["reader_id"],
                employee_id=row["employee_id"],
                due_date=row["due_date"],
                loan_id=row["loan_id"],
                loan_date=row["loan_date"],
                return_date=row["return_date"],
                status=row["status"]
            )
            for row in rows
        ]
    
    def get_active_loans(self) -> List[Loan]:
        """Get active (not returned) loans"""
        rows = self._fetchall("""
            SELECT loan_id, book_id, reader_id, employee_id, loan_date,
                   due_date, return_date, status
            FROM loans WHERE status = 'active' OR (return_date IS NULL AND status != 'returned')
            ORDER BY due_date
        """)
        
        return [
            Loan(
                book_id=row["book_id"],
                reader_id=row["reader_id"],
                employee_id=row["employee_id"],
                due_date=row["due_date"],
                loan_id=row["loan_id"],
                loan_date=row["loan_date"],
                return_date=row["return_date"],
                status=row["status"]
            )
            for row in rows
        ]
    
    def get_overdue_loans(self) -> List[Loan]:
        """Get overdue loans"""
        rows = self._fetchall("""
            SELECT loan_id, book_id, reader_id, employee_id, loan_date,
                   due_date, return_date, status
            FROM loans WHERE due_date < DATE('now') AND return_date IS NULL
            ORDER BY due_date
        """)
        
        return [
            Loan(
                book_id=row["book_id"],
                reader_id=row["reader_id"],
                employee_id=row["employee_id"],
                due_date=row["due_date"],
                loan_id=row["loan_id"],
                loan_date=row["loan_date"],
                return_date=row["return_date"],
                status=row["status"]
            )
            for row in rows
        ]


    def __enter__(self) -> "Database":
        """Context manager entry"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.close()