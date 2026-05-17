"""Pytest configuration"""

import pytest
import tempfile
import os

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
    db._execute("INSERT INTO authors (last_name, first_name, middle_name) VALUES ('Толстой', 'Лев', 'Николаевич')")
    author_id = db.cursor.lastrowid
    
    # Category
    db._execute("INSERT INTO categories (name, description) VALUES ('Роман', 'Художественная проза')")
    category_id = db.cursor.lastrowid
    
    # Publisher
    db._execute("INSERT INTO publishers (name, city, country) VALUES ('АСТ', 'Москва', 'Россия')")
    publisher_id = db.cursor.lastrowid
    
    # Position
    db._execute("INSERT INTO positions (name, description) VALUES ('Библиотекарь', 'Выдача книг')")
    position_id = db.cursor.lastrowid
    
    return {
        'db': db,
        'author_id': author_id,
        'category_id': category_id,
        'publisher_id': publisher_id,
        'position_id': position_id
    }