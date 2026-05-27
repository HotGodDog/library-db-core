"""Tests for database operations."""

import pytest
from library_db_core import Book, Employee, Loan, Reader


class TestDatabaseSetup:
    """Test database connection and setup."""

    def test_create_tables(self, temp_db):
        """Tables should be created successfully."""
        tables = temp_db._fetchall("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = {row["name"] for row in tables}
        assert "books" in table_names
        assert "readers" in table_names
        assert "employees" in table_names
        assert "loans" in table_names
        assert "authors" in table_names
        assert "categories" in table_names
        assert "publishers" in table_names
        assert "positions" in table_names

    def test_is_seeded_empty(self, temp_db):
        """Empty database should not be seeded."""
        assert not temp_db.is_seeded()

    def test_is_seeded_after_data(self, temp_db, sample_csv_dir):
        """Database with data should be seeded."""
        temp_db.seed_from_csv(sample_csv_dir)
        assert temp_db.is_seeded()


class TestSeedFromCsv:
    """Test CSV seed loading."""

    def test_seed_positions(self, temp_db, sample_csv_dir):
        """Positions should be loaded from CSV."""
        temp_db.seed_from_csv(sample_csv_dir)
        positions = temp_db._fetchall("SELECT * FROM positions")
        assert len(positions) == 2
        assert positions[0]["name"] == "Администратор"
        assert positions[1]["name"] == "Библиотекарь"

    def test_seed_categories(self, temp_db, sample_csv_dir):
        """Categories should be loaded from CSV."""
        temp_db.seed_from_csv(sample_csv_dir)
        categories = temp_db._fetchall("SELECT * FROM categories")
        assert len(categories) == 1
        assert categories[0]["name"] == "Роман"

    def test_seed_authors(self, temp_db, sample_csv_dir):
        """Authors should be loaded from CSV."""
        temp_db.seed_from_csv(sample_csv_dir)
        authors = temp_db._fetchall("SELECT * FROM authors")
        assert len(authors) == 1
        assert authors[0]["last_name"] == "Толстой"

    def test_seed_employees(self, temp_db, sample_csv_dir):
        """Employees should be loaded with correct FK."""
        temp_db.seed_from_csv(sample_csv_dir)
        emp = temp_db.get_employee(1)
        assert emp is not None
        assert emp.last_name == "Иванов"
        assert emp.position_id == 1

    def test_seed_readers(self, temp_db, sample_csv_dir):
        """Readers should be loaded from CSV."""
        temp_db.seed_from_csv(sample_csv_dir)
        reader = temp_db.get_reader(1)
        assert reader is not None
        assert reader.last_name == "Петров"
        assert reader.email == "petrov@lib.ru"

    def test_seed_books(self, temp_db, sample_csv_dir):
        """Books should be loaded with correct FKs."""
        temp_db.seed_from_csv(sample_csv_dir)
        book = temp_db.get_book(1)
        assert book is not None
        assert book.title == "Война и мир"
        assert book.author_id == 1
        assert book.category_id == 1
        assert book.publisher_id == 1

    def test_seed_loans(self, temp_db, sample_csv_dir):
        """Loans should be loaded from CSV."""
        temp_db.seed_from_csv(sample_csv_dir)
        loans = temp_db.get_all_loans()
        assert len(loans) == 1
        assert loans[0].book_id == 1
        assert loans[0].reader_id == 1
        assert loans[0].status == "active"

    def test_seed_idempotent(self, temp_db, sample_csv_dir):
        """Seeding twice should not duplicate data."""
        temp_db.seed_from_csv(sample_csv_dir)
        temp_db.seed_from_csv(sample_csv_dir)

        positions = temp_db._fetchall("SELECT * FROM positions")
        assert len(positions) == 2

        books = temp_db._fetchall("SELECT * FROM books")
        assert len(books) == 1

    def test_seed_missing_csv(self, temp_db, tmp_path):
        """Should raise error for missing CSV files."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            temp_db.seed_from_csv(str(empty_dir))


class TestBookCRUD:
    """Test Book CRUD operations."""

    def test_add_book(self, sample_data):
        db = sample_data['db']
        book = Book(
            title="Война и мир",
            author_id=sample_data['author_id'],
            category_id=sample_data['category_id'],
            publisher_id=sample_data['publisher_id'],
            total_copies=3
        )
        book_id = db.add_book(book)
        assert book_id == 1

    def test_get_book(self, sample_data):
        db = sample_data['db']
        book = Book(
            title="Война и мир",
            author_id=sample_data['author_id'],
            category_id=sample_data['category_id'],
            publisher_id=sample_data['publisher_id'],
            total_copies=3
        )
        book_id = db.add_book(book)

        retrieved = db.get_book(book_id)
        assert retrieved is not None
        assert retrieved.title == "Война и мир"
        assert retrieved.available == 3

    def test_get_book_not_found(self, sample_data):
        db = sample_data['db']
        retrieved = db.get_book(999)
        assert retrieved is None

    def test_get_all_books(self, sample_data):
        db = sample_data['db']
        db.add_book(Book(title="Книга 1", author_id=1, category_id=1, publisher_id=1))
        db.add_book(Book(title="Книга 2", author_id=1, category_id=1, publisher_id=1))

        books = db.get_all_books()
        assert len(books) == 2
        assert books[0].title == "Книга 1"
        assert books[1].title == "Книга 2"


class TestReaderCRUD:
    """Test Reader CRUD operations."""

    def test_add_reader(self, sample_data):
        db = sample_data['db']
        reader = Reader(
            last_name="Смирнов",
            first_name="Алексей",
            middle_name="Иванович",
            passport_num="4515123456",
            phone="89011112233",
            email="smirnov@mail.ru",
            password="qwerty",
            address="Москва"
        )
        reader_id = db.add_reader(reader)
        assert reader_id == 1

    def test_get_reader(self, sample_data):
        db = sample_data['db']
        reader = Reader(
            last_name="Смирнов",
            first_name="Алексей",
            middle_name="Иванович",
            passport_num="4515123456",
            phone="89011112233",
            email="smirnov@mail.ru",
            address="Москва"
        )
        reader_id = db.add_reader(reader)

        retrieved = db.get_reader(reader_id)
        assert retrieved is not None
        assert retrieved.last_name == "Смирнов"


class TestEmployeeCRUD:
    """Test Employee CRUD operations."""

    def test_add_employee(self, sample_data):
        db = sample_data['db']
        emp = Employee(
            last_name="Иванова",
            first_name="Мария",
            middle_name="Петровна",
            position_id=sample_data['position_id'],
            phone="89001234567",
            email="ivanova@lib.ru",
            password="123456"
        )
        emp_id = db.add_employee(emp)
        assert emp_id == 1

    def test_get_employee_by_email(self, sample_data):
        db = sample_data['db']
        emp = Employee(
            last_name="Иванова",
            first_name="Мария",
            middle_name="Петровна",
            position_id=sample_data['position_id'],
            phone="89001234567",
            email="ivanova@lib.ru",
            password="123456"
        )
        db.add_employee(emp)

        retrieved = db.get_employee_by_email("ivanova@lib.ru")
        assert retrieved is not None
        assert retrieved.last_name == "Иванова"


class TestLoanCRUD:
    """Test Loan operations and triggers."""

    def test_issue_book(self, sample_data):
        db = sample_data['db']

        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)

        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)

        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)

        loan = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, due_date="2026-12-31")
        loan_id = db.issue_book(loan)
        assert loan_id == 1

        # Check trigger decreased availability
        book_after = db.get_book(book_id)
        assert book_after.available == 1

    def test_return_book(self, sample_data):
        db = sample_data['db']

        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)

        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)

        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)

        loan = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, due_date="2026-12-31")
        loan_id = db.issue_book(loan)

        db.return_book(loan_id)

        # Check trigger increased availability
        book_after = db.get_book(book_id)
        assert book_after.available == 2

        # Check status updated
        loan_after = db.get_loan(loan_id)
        assert loan_after.status == "returned"

    def test_get_active_loans(self, sample_data):
        db = sample_data['db']

        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)

        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)

        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)

        # Issue one, return one
        loan1 = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, due_date="2026-12-31")
        loan1_id = db.issue_book(loan1)
        db.return_book(loan1_id)

        loan2 = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, due_date="2026-12-31")
        db.issue_book(loan2)

        active = db.get_active_loans()
        assert len(active) == 1
        assert active[0].status == "active"

    def test_get_overdue_loans(self, sample_data):
        db = sample_data['db']

        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)

        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)

        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)

        # Overdue loan (due in the past)
        loan = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, 
                    loan_date="2026-01-01", due_date="2026-01-15")
        db.issue_book(loan)

        overdue = db.get_overdue_loans()
        assert len(overdue) >= 1  # At least our loan is overdue


class TestAuth:
    """Test authentication methods."""

    def test_verify_employee(self, sample_data):
        db = sample_data['db']
        emp = Employee(
            last_name="Иванова",
            first_name="Мария",
            middle_name="Петровна",
            position_id=sample_data['position_id'],
            phone="89001234567",
            email="ivanova@lib.ru",
            password="123456"
        )
        db.add_employee(emp)

        verified = db.verify_employee("ivanova@lib.ru", "123456")
        assert verified is not None
        assert verified.last_name == "Иванова"

        wrong = db.verify_employee("ivanova@lib.ru", "wrong")
        assert wrong is None

        wrong = db.verify_employee("wrong@lib.ru", "123456")
        assert wrong is None

    def test_verify_reader(self, sample_data):
        db = sample_data['db']
        reader = Reader(
            last_name="Смирнов",
            first_name="Алексей",
            middle_name="Иванович",
            passport_num="4515123456",
            phone="89011112233",
            email="smirnov@mail.ru",
            password="qwerty",
            address="Москва"
        )
        db.add_reader(reader)

        verified = db.verify_reader("smirnov@mail.ru", "qwerty")
        assert verified is not None
        assert verified.last_name == "Смирнов"

        wrong = db.verify_reader("smirnov@mail.ru", "wrong")
        assert wrong is None