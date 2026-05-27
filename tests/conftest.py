"""Pytest configuration."""

import os
import pytest
import tempfile

from library_db_core import Database


@pytest.fixture
def temp_db():
    """Create temporary database for tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    db = Database(path).connect()
    db.create_tables()

    yield db

    db.close()
    os.unlink(path)


@pytest.fixture
def sample_data(temp_db):
    """Create sample reference data for tests."""
    db = temp_db

    # Author
    db._execute("INSERT INTO authors (author_id, last_name, first_name, middle_name) VALUES (1, 'Толстой', 'Лев', 'Николаевич')")

    # Category
    db._execute("INSERT INTO categories (category_id, name, description) VALUES (1, 'Роман', 'Художественная проза')")

    # Publisher
    db._execute("INSERT INTO publishers (publisher_id, name, city, country) VALUES (1, 'АСТ', 'Москва', 'Россия')")

    # Position
    db._execute("INSERT INTO positions (position_id, name, description) VALUES (1, 'Библиотекарь', 'Выдача книг')")

    return {
        'db': db,
        'author_id': 1,
        'category_id': 1,
        'publisher_id': 1,
        'position_id': 1
    }


@pytest.fixture
def sample_csv_dir(tmp_path):
    """Create temporary CSV files for seed testing."""
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()

    (csv_dir / "positions.csv").write_text(
        "position_id;name;description\n"
        "1;Администратор;Руководитель\n"
        "2;Библиотекарь;Выдача книг\n",
        encoding="utf-8"
    )

    (csv_dir / "categories.csv").write_text(
        "category_id;name;description\n"
        "1;Роман;Художественная проза\n",
        encoding="utf-8"
    )

    (csv_dir / "publishers.csv").write_text(
        "publisher_id;name;city;country\n"
        "1;АСТ;Москва;Россия\n",
        encoding="utf-8"
    )

    (csv_dir / "authors.csv").write_text(
        "author_id;last_name;first_name;middle_name\n"
        "1;Толстой;Лев;Николаевич\n",
        encoding="utf-8"
    )

    (csv_dir / "employees.csv").write_text(
        "employee_id;last_name;first_name;middle_name;position_id;phone;email;password\n"
        "1;Иванов;Иван;Иванович;1;89000000000;ivanov@lib.ru;pass123\n",
        encoding="utf-8"
    )

    (csv_dir / "readers.csv").write_text(
        "reader_id;last_name;first_name;middle_name;passport_num;phone;email;password;address;reg_date\n"
        "1;Петров;Пётр;Петрович;1234 567890;89001112233;petrov@lib.ru;reader1;г. Москва;2026-01-01\n",
        encoding="utf-8"
    )

    (csv_dir / "books.csv").write_text(
        "book_id;title;author_id;category_id;publisher_id;total_copies;year_published;pages;available;description\n"
        "1;Война и мир;1;1;1;3;2020;1360;3;Эпопея\n",
        encoding="utf-8"
    )

    (csv_dir / "loans.csv").write_text(
        "loan_id;book_id;reader_id;employee_id;loan_date;due_date;return_date\n"
        "1;1;1;1;2026-01-01;2026-01-15;\n",
        encoding="utf-8"
    )

    return str(csv_dir)