"""library-db-core: Core database library for library management system"""

from .database import Database
from .models import Author, Book, Category, Employee, Loan, Position, Publisher, Reader

__version__ = "0.1.0"
__all__ = ["Author", "Book", "Category", "Employee", "Loan", "Position", "Publisher", "Reader"]