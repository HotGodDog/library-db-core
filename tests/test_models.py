"""Tests for data models."""

from library_db_core import Author, Book, Employee, Reader


class TestAuthor:
    """Test Author model."""

    def test_creation(self):
        author = Author(last_name="Толстой", first_name="Лев", middle_name="Николаевич")
        assert author.last_name == "Толстой"
        assert author.first_name == "Лев"
        assert author.middle_name == "Николаевич"
        assert author.author_id is None

    def test_full_name(self):
        author = Author(last_name="Толстой", first_name="Лев", middle_name="Николаевич")
        assert author.full_name == "Толстой Лев Николаевич"

    def test_full_name_without_middle(self):
        author = Author(last_name="Роулинг", first_name="Джоан")
        assert author.full_name == "Роулинг Джоан"

    def test_repr(self):
        author = Author(last_name="Толстой", first_name="Лев", author_id=1)
        assert repr(author) == "Author(1, 'Толстой Лев')"


class TestBook:
    """Test Book model."""

    def test_creation(self):
        book = Book(
            title="Война и мир",
            author_id=1,
            category_id=1,
            publisher_id=1,
            total_copies=3
        )
        assert book.title == "Война и мир"
        assert book.total_copies == 3
        assert book.available == 3

    def test_creation_with_available(self):
        book = Book(
            title="Война и мир",
            author_id=1,
            category_id=1,
            publisher_id=1,
            total_copies=3,
            available=1
        )
        assert book.available == 1

    def test_repr(self):
        book = Book(title="Война и мир", author_id=1, category_id=1, publisher_id=1, book_id=1)
        assert repr(book) == "Book(1, 'Война и мир')"


class TestReader:
    """Test Reader model."""

    def test_full_name(self):
        reader = Reader(
            last_name="Смирнов",
            first_name="Алексей",
            middle_name="Иванович",
            passport_num="4515123456",
            phone="89011112233",
            email="smirnov@mail.ru",
            address="Москва, ул. Ленина 1"
        )
        assert reader.full_name == "Смирнов Алексей Иванович"

    def test_full_name_without_middle(self):
        reader = Reader(
            last_name="Иванов",
            first_name="Иван",
            middle_name="",
            passport_num="4515111111",
            phone="89011111111",
            email="ivanov@mail.ru",
            address="Москва"
        )
        assert reader.full_name == "Иванов Иван"


class TestEmployee:
    """Test Employee model."""

    def test_creation(self):
        emp = Employee(
            last_name="Иванова",
            first_name="Мария",
            middle_name="Петровна",
            position_id=1,
            phone="89001234567",
            email="ivanova@lib.ru"
        )
        assert emp.full_name == "Иванова Мария Петровна"
        assert emp.is_active is True