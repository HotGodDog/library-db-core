"""Data models for library database"""


class Category:
    """Book category/genre"""
    
    def __init__(self, name: str, description: str = "", category_id: int = None):
        self.category_id = category_id
        self.name = name
        self.description = description
    
    def __repr__(self):
        return f"Category({self.category_id}, '{self.name}')"


class Publisher:
    """Book publisher"""
    
    def __init__(self, name: str, city: str = "", country: str = "", publisher_id: int = None):
        self.publisher_id = publisher_id
        self.name = name
        self.city = city
        self.country = country
    
    def __repr__(self):
        return f"Publisher({self.publisher_id}, '{self.name}')"


class Author:
    """Book author"""
    
    def __init__(self, last_name: str, first_name: str, middle_name: str = "", author_id: int = None):
        self.author_id = author_id
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
    
    @property
    def full_name(self) -> str:
        """Return full name"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
    
    def __repr__(self):
        return f"Author({self.author_id}, '{self.full_name}')"
    

class Position:
    """Employee position"""
    
    def __init__(self, name: str, description: str = "", position_id: int = None):
        self.position_id = position_id
        self.name = name
        self.description = description
    
    def __repr__(self):
        return f"Position({self.position_id}, '{self.name}')"


class Employee:
    """Library employee"""
    
    def __init__(self, last_name: str, first_name: str, middle_name: str,
                 position_id: int, phone: str, email: str,
                 employee_id: int = None, is_active: bool = True):
        self.employee_id = employee_id
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.position_id = position_id
        self.phone = phone
        self.email = email
        self.is_active = is_active
    
    @property
    def full_name(self) -> str:
        """Return full name"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
    
    def __repr__(self):
        return f"Employee({self.employee_id}, '{self.full_name}')"
    

class Book:
    """Library book"""
    
    def __init__(self, title: str, author_id: int, category_id: int,
                 publisher_id: int, total_copies: int = 1,
                 year_published: int = None, pages: int = None,
                 description: str = "", book_id: int = None,
                 available: int = None):
        self.book_id = book_id
        self.title = title
        self.author_id = author_id
        self.category_id = category_id
        self.publisher_id = publisher_id
        self.year_published = year_published
        self.pages = pages
        self.total_copies = total_copies
        self.available = available if available is not None else total_copies
        self.description = description
    
    def __repr__(self):
        return f"Book({self.book_id}, '{self.title}')"


class Reader:
    """Library reader"""
    
    def __init__(self, last_name: str, first_name: str, middle_name: str,
                 passport_num: str, phone: str, email: str, address: str,
                 reader_id: int = None, reg_date: str = None,
                 is_active: bool = True):
        self.reader_id = reader_id
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.passport_num = passport_num
        self.phone = phone
        self.email = email
        self.address = address
        self.reg_date = reg_date
        self.is_active = is_active
    
    @property
    def full_name(self) -> str:
        """Return full name"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
    
    def __repr__(self):
        return f"Reader({self.reader_id}, '{self.full_name}')"


class Loan:
    """Book loan record"""
    
    def __init__(self, book_id: int, reader_id: int, employee_id: int,
                 due_date: str, loan_id: int = None,
                 loan_date: str = None, return_date: str = None,
                 status: str = "active"):
        self.loan_id = loan_id
        self.book_id = book_id
        self.reader_id = reader_id
        self.employee_id = employee_id
        self.loan_date = loan_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status
    
    def __repr__(self):
        return f"Loan({self.loan_id}, book={self.book_id}, reader={self.reader_id})"