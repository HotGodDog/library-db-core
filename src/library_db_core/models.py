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