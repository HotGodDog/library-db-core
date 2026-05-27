"""Database operations for library management system"""

import csv
import os
import sqlite3

from typing import List, Optional, Tuple
from datetime import datetime
from .config import DB_PATH
from .models import Book, Employee, Reader, Loan


class Database:
    """SQLite database manager for library system"""

    def __init__(self, db_path: str = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses DB_PATH from config
        """
        self.db_path = db_path or DB_PATH
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
        """Create all database tables from scheme.sql"""
        scheme_path = os.path.join(os.path.dirname(__file__), "sql", "scheme.sql")
        with open(scheme_path, "r", encoding="utf-8") as f:
            self.cursor.executescript(f.read())
        # executescript() already commits

    def is_seeded(self) -> bool:
        """Check if database already contains seed data"""
        try:
            result = self._fetchone("SELECT COUNT(*) FROM positions")
            return result[0] > 0
        except sqlite3.OperationalError:
            return False

    def seed_from_csv(self, csv_dir: str) -> None:
        """Load seed data from CSV files in given directory

        CSV files must follow naming convention:
        - positions.csv, categories.csv, publishers.csv, authors.csv
        - employees.csv, readers.csv, books.csv, loans.csv

        Reference tables (positions, categories, publishers, authors)
        must have explicit *_id columns. Dependent tables use FKs.

        Args:
            csv_dir: Path to directory containing CSV files
        """
        if self.is_seeded():
            return

        def _load_csv(filename: str) -> list[dict]:
            path = os.path.join(csv_dir, filename)
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=";")
                return list(reader)

        # 1. Positions (no dependencies)
        for row in _load_csv("positions.csv"):
            self._execute(
                "INSERT INTO positions (position_id, name, description) VALUES (?, ?, ?)",
                (int(row["position_id"]), row["name"], row["description"]),
            )

        # 2. Categories (no dependencies)
        for row in _load_csv("categories.csv"):
            self._execute(
                "INSERT INTO categories (category_id, name, description) VALUES (?, ?, ?)",
                (int(row["category_id"]), row["name"], row["description"]),
            )

        # 3. Publishers (no dependencies)
        for row in _load_csv("publishers.csv"):
            self._execute(
                "INSERT INTO publishers (publisher_id, name, city, country) VALUES (?, ?, ?, ?)",
                (int(row["publisher_id"]), row["name"], row["city"], row["country"]),
            )

        # 4. Authors (no dependencies)
        for row in _load_csv("authors.csv"):
            self._execute(
                "INSERT INTO authors (author_id, last_name, first_name, middle_name) VALUES (?, ?, ?, ?)",
                (int(row["author_id"]), row["last_name"], row["first_name"], row["middle_name"]),
            )

        # 5. Employees (depends on positions)
        for row in _load_csv("employees.csv"):
            self.add_employee(Employee(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                position_id=int(row["position_id"]),
                phone=row["phone"],
                email=row["email"],
                password=row["password"],
            ))

        # 6. Readers (no dependencies)
        for row in _load_csv("readers.csv"):
            self.add_reader(Reader(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                passport_num=row["passport_num"],
                phone=row["phone"],
                email=row["email"],
                password=row["password"],
                address=row["address"],
                reg_date=row.get("reg_date"),
            ))

        # 7. Books (depends on authors, categories, publishers)
        for row in _load_csv("books.csv"):
            self.add_book(Book(
                title=row["title"],
                author_id=int(row["author_id"]),
                category_id=int(row["category_id"]),
                publisher_id=int(row["publisher_id"]),
                total_copies=int(row["total_copies"]),
                year_published=int(row["year_published"]) if row.get("year_published") else None,
                pages=int(row["pages"]) if row.get("pages") else None,
                available=int(row["available"]),
                description=row.get("description", ""),
            ))

        # 8. Loans (depends on books, readers, employees)
        for row in _load_csv("loans.csv"):
            loan_id = self.issue_book(Loan(
                book_id=int(row["book_id"]),
                reader_id=int(row["reader_id"]),
                employee_id=int(row["employee_id"]),
                loan_date=row.get("loan_date"),
                due_date=row["due_date"],
            ))

            if row.get("return_date"):
                self._execute(
                    "UPDATE loans SET return_date = ? WHERE loan_id = ?",
                    (row["return_date"], loan_id),
                )

    # BOOK CRUD

    def add_book(self, book: Book) -> int:
        """Add new book to database"""
        self._execute("""
            INSERT INTO books (title, author_id, category_id, publisher_id, year_published, pages, total_copies, available, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (book.title, book.author_id, book.category_id, book.publisher_id,
              book.year_published, book.pages, book.total_copies, book.available, 
              book.description))
        return self.cursor.lastrowid

    def get_book(self, book_id: int) -> Optional[Book]:
        """Get book by ID"""
        row = self._fetchone("""
            SELECT book_id, title, author_id, category_id, publisher_id, year_published, pages, total_copies, available, description
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
        """Get all books"""
        rows = self._fetchall("""
            SELECT book_id, title, author_id, category_id, publisher_id, year_published, pages, total_copies, available, description
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
        """Add new reader to database"""
        self._execute("""
            INSERT INTO readers (last_name, first_name, middle_name, passport_num, phone, email, password, address, reg_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (reader.last_name, reader.first_name, reader.middle_name,
              reader.passport_num, reader.phone, reader.email, reader.password,
              reader.address, reader.reg_date, 1 if reader.is_active else 0))
        return self.cursor.lastrowid

    def get_reader(self, reader_id: int) -> Optional[Reader]:
        """Get reader by ID"""
        row = self._fetchone("""
            SELECT reader_id, last_name, first_name, middle_name, passport_num, phone, email, address, reg_date, is_active
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
            SELECT reader_id, last_name, first_name, middle_name, passport_num, phone, email, address, reg_date, is_active
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
        """Add new employee to database"""
        self._execute("""
            INSERT INTO employees (last_name, first_name, middle_name, position_id, phone, email, password, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (employee.last_name, employee.first_name, employee.middle_name,
              employee.position_id, employee.phone, employee.email, employee.password,
              1 if employee.is_active else 0))
        return self.cursor.lastrowid

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        row = self._fetchone("""
            SELECT employee_id, last_name, first_name, middle_name, position_id, phone, email, is_active
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
            SELECT employee_id, last_name, first_name, middle_name, position_id, phone, email, is_active
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
        """Issue book to reader"""
        self._execute("""
            INSERT INTO loans (book_id, reader_id, employee_id, loan_date, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (loan.book_id, loan.reader_id, loan.employee_id,
              loan.loan_date or datetime.now().strftime("%Y-%m-%d"),
              loan.due_date, "active"))
        return self.cursor.lastrowid

    def return_book(self, loan_id: int) -> None:
        """Return book by loan ID"""
        return_date = datetime.now().strftime("%Y-%m-%d")
        self._execute("""
            UPDATE loans SET return_date = ? WHERE loan_id = ?
        """, (return_date, loan_id))

    def get_loan(self, loan_id: int) -> Optional[Loan]:
        """Get loan by ID."""
        row = self._fetchone("""
            SELECT loan_id, book_id, reader_id, employee_id, loan_date, due_date, return_date, status
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
            SELECT loan_id, book_id, reader_id, employee_id, loan_date, due_date, return_date, status
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
            SELECT loan_id, book_id, reader_id, employee_id, loan_date, due_date, return_date, status
            FROM loans WHERE status IN ('active', 'overdue')
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
            SELECT loan_id, book_id, reader_id, employee_id, loan_date, due_date, return_date, status
            FROM loans WHERE due_date < DATE('now') AND return_date IS NULL AND status = 'active'
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

    # REPORTS

    def get_statistics(self) -> dict:
        """Get library statistics"""
        stats = {}
        stats['total_books'] = self._fetchone("SELECT COUNT(*) FROM books")[0]
        stats['total_copies'] = self._fetchone("SELECT COALESCE(SUM(total_copies), 0) FROM books")[0]
        stats['available_copies'] = self._fetchone("SELECT COALESCE(SUM(available), 0) FROM books")[0]
        stats['total_readers'] = self._fetchone("SELECT COUNT(*) FROM readers WHERE is_active = 1")[0]
        stats['total_employees'] = self._fetchone("SELECT COUNT(*) FROM employees WHERE is_active = 1")[0]
        stats['active_loans'] = self._fetchone("SELECT COUNT(*) FROM loans WHERE status = 'active'")[0]
        stats['overdue_loans'] = self._fetchone("SELECT COUNT(*) FROM loans WHERE status = 'overdue'")[0]
        stats['total_loans'] = self._fetchone("SELECT COUNT(*) FROM loans")[0]
        return stats

    def get_popular_books(self, limit: int = 5) -> List[dict]:
        """Get most popular books by loan count"""
        rows = self._fetchall("""
            SELECT b.title, a.last_name || ' ' || a.first_name AS author_name, COUNT(l.loan_id) AS loan_count
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            LEFT JOIN loans l ON b.book_id = l.book_id
            GROUP BY b.book_id
            ORDER BY loan_count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in rows]

    def search_books(self, search_term: str) -> List[Book]:
        """Search books by title or author name (case-insensitive)"""
        pattern_lower = f"%{search_term.lower()}%"
        pattern_upper = f"%{search_term.upper()}%"
        pattern_title = f"%{search_term.capitalize()}%"

        rows = self._fetchall("""
            SELECT b.book_id, b.title, b.author_id, b.category_id, b.publisher_id,
                   b.year_published, b.pages, b.total_copies, b.available, b.description
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE b.title LIKE ? OR b.title LIKE ? OR b.title LIKE ?
               OR a.last_name LIKE ? OR a.last_name LIKE ? OR a.last_name LIKE ?
               OR a.first_name LIKE ? OR a.first_name LIKE ? OR a.first_name LIKE ?
            ORDER BY b.title
        """, (pattern_lower, pattern_upper, pattern_title,
              pattern_lower, pattern_upper, pattern_title,
              pattern_lower, pattern_upper, pattern_title))

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

    # AUTH METHODS

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        row = self._fetchone("""
            SELECT employee_id, last_name, first_name, middle_name, position_id,
                   phone, email, password, is_active
            FROM employees WHERE email = ? AND is_active = 1
        """, (email,))

        if row:
            return Employee(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                position_id=row["position_id"],
                phone=row["phone"],
                email=row["email"],
                password=row["password"],
                employee_id=row["employee_id"],
                is_active=bool(row["is_active"])
            )
        return None

    def get_reader_by_email(self, email: str) -> Optional[Reader]:
        """Get reader by email"""
        row = self._fetchone("""
            SELECT reader_id, last_name, first_name, middle_name, passport_num,
                   phone, email, password, address, reg_date, is_active
            FROM readers WHERE email = ? AND is_active = 1
        """, (email,))

        if row:
            return Reader(
                last_name=row["last_name"],
                first_name=row["first_name"],
                middle_name=row["middle_name"],
                passport_num=row["passport_num"],
                phone=row["phone"],
                email=row["email"],
                password=row["password"],
                address=row["address"],
                reader_id=row["reader_id"],
                reg_date=row["reg_date"],
                is_active=bool(row["is_active"])
            )
        return None

    def verify_employee(self, email: str, password: str) -> Optional[Employee]:
        """Verify employee credentials"""
        employee = self.get_employee_by_email(email)
        if employee and employee.password == password:
            return employee
        return None

    def verify_reader(self, email: str, password: str) -> Optional[Reader]:
        """Verify reader credentials"""
        reader = self.get_reader_by_email(email)
        if reader and reader.password == password:
            return reader
        return None

    def __enter__(self) -> "Database":
        """Context manager entry"""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.close()