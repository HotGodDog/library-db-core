"""Tests for database operations"""

from library_db_core import Book, Employee, Loan, Reader


class TestBookCRUD:
    """Test Book CRUD operations"""
    
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
        assert book_id > 0
    
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


class TestReaderCRUD:
    """Test Reader CRUD operations"""
    
    def test_add_reader(self, sample_data):
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
        assert reader_id > 0
    
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
    """Test Employee CRUD operations"""
    
    def test_add_employee(self, sample_data):
        db = sample_data['db']
        emp = Employee(
            last_name="Иванова",
            first_name="Мария",
            middle_name="Петровна",
            position_id=sample_data['position_id'],
            phone="89001234567",
            email="ivanova@lib.ru"
        )
        emp_id = db.add_employee(emp)
        assert emp_id > 0


class TestLoanCRUD:
    """Test Loan operations and triggers"""
    
    def test_issue_book(self, sample_data):
        db = sample_data['db']
        
        # Add book with 2 copies
        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)
        
        # Add reader
        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)
        
        # Add employee
        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)
        
        # Issue book
        loan = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, due_date="2024-12-31")
        loan_id = db.issue_book(loan)
        assert loan_id > 0
        
        # Check available decreased (trigger)
        book_after = db.get_book(book_id)
        assert book_after.available == 1
    
    def test_return_book(self, sample_data):
        db = sample_data['db']
        
        # Setup
        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)
        
        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)
        
        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)
        
        # Issue and return
        loan = Loan(book_id=book_id, reader_id=reader_id, employee_id=emp_id, due_date="2024-12-31")
        loan_id = db.issue_book(loan)
        
        db.return_book(loan_id)
        
        # Check available increased (trigger)
        book_after = db.get_book(book_id)
        assert book_after.available == 2
        
        # Check status changed
        loan_after = db.get_loan(loan_id)
        assert loan_after.status == "returned"
    
    def test_get_active_loans(self, sample_data):
        db = sample_data['db']
        
        # Setup
        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=2)
        book_id = db.add_book(book)
        
        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)
        
        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")