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