"""Tests for reports and statistics"""

from library_db_core import Book, Employee, Loan, Reader


class TestStatistics:
    """Test library statistics"""
    
    def test_empty_statistics(self, sample_data):
        db = sample_data['db']
        stats = db.get_statistics()
        
        assert stats['total_books'] == 0
        assert stats['total_readers'] == 0
        assert stats['active_loans'] == 0
        assert stats['overdue_loans'] == 0
    
    def test_statistics_with_data(self, sample_data):
        db = sample_data['db']
        
        # Add book
        book = Book(title="Тест", author_id=1, category_id=1, publisher_id=1, total_copies=5)
        db.add_book(book)
        
        # Add reader
        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        db.add_reader(reader)
        
        # Add employee
        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        db.add_employee(emp)
        
        stats = db.get_statistics()
        assert stats['total_books'] == 1
        assert stats['total_copies'] == 5
        assert stats['available_copies'] == 5
        assert stats['total_readers'] == 1
        assert stats['total_employees'] == 1


class TestSearch:
    """Test book search"""
    
    def test_search_by_title(self, sample_data):
        db = sample_data['db']
        db.add_book(Book(title="Война и мир", author_id=1, category_id=1, publisher_id=1))
        db.add_book(Book(title="Мир и война", author_id=1, category_id=1, publisher_id=1))
        
        # Register-independent search
        results = db.search_books("война")
        assert len(results) == 2
    
    def test_search_not_found(self, sample_data):
        db = sample_data['db']
        db.add_book(Book(title="Война и мир", author_id=1, category_id=1, publisher_id=1))
        
        results = db.search_books("несуществующая")
        assert len(results) == 0


class TestPopularBooks:
    """Test popular books report"""
    
    def test_popular_books_empty(self, sample_data):
        db = sample_data['db']
        popular = db.get_popular_books()
        assert len(popular) == 0
    
    def test_popular_books_sorted(self, sample_data):
        db = sample_data['db']
        
        # Add two books with enough copies
        book1 = Book(title="Популярная", author_id=1, category_id=1, publisher_id=1, total_copies=5)
        book1_id = db.add_book(book1)
        
        book2 = Book(title="Непопулярная", author_id=1, category_id=1, publisher_id=1, total_copies=5)
        book2_id = db.add_book(book2)
        
        # Add reader and employee
        reader = Reader("Иванов", "Иван", "Иванович", "4515111111", "89011111111", "ivanov@test.ru", "Москва")
        reader_id = db.add_reader(reader)
        
        emp = Employee("Петров", "Петр", "Петрович", sample_data['position_id'], "89022222222", "petrov@test.ru")
        emp_id = db.add_employee(emp)
        
        # Issue first book twice, second once
        db.issue_book(Loan(book_id=book1_id, reader_id=reader_id, employee_id=emp_id, due_date="2024-12-31"))
        db.issue_book(Loan(book_id=book1_id, reader_id=reader_id, employee_id=emp_id, due_date="2024-12-31"))
        db.issue_book(Loan(book_id=book2_id, reader_id=reader_id, employee_id=emp_id, due_date="2024-12-31"))
        
        popular = db.get_popular_books(limit=2)
        assert len(popular) == 2
        assert popular[0]['title'] == "Популярная"
        assert popular[0]['loan_count'] == 2
        assert popular[1]['loan_count'] == 1