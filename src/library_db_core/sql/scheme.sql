-- БАЗА ДАННЫХ: Автоматизированная система управления библиотекой


--  Справочник жанров
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

-- Справочник издательств
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT,
    country TEXT
);

-- Справочник авторов
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT
);

-- Справочник должностей
CREATE TABLE IF NOT EXISTS positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Книги
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER REFERENCES authors(author_id),
    category_id INTEGER REFERENCES categories(category_id),
    publisher_id INTEGER REFERENCES publishers(publisher_id),
    year_published INTEGER,
    pages INTEGER,
    total_copies INTEGER NOT NULL DEFAULT 1,
    available INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    CHECK (available >= 0),
    CHECK (available <= total_copies)
);

-- Сотрудники
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT NOT NULL,
    position_id INTEGER NOT NULL REFERENCES positions(position_id),
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);

-- Читатели
CREATE TABLE IF NOT EXISTS readers (
    reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT NOT NULL,
    passport_num TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    address TEXT NOT NULL,
    reg_date DATE DEFAULT CURRENT_DATE,
    is_active INTEGER DEFAULT 1
);

-- Выдачи
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(book_id),
    reader_id INTEGER NOT NULL REFERENCES readers(reader_id),
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
    loan_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status TEXT CHECK(status IN ('active', 'returned', 'overdue')) DEFAULT 'active'
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category_id);
CREATE INDEX IF NOT EXISTS idx_books_publisher ON books(publisher_id);
CREATE INDEX IF NOT EXISTS idx_employees_position ON employees(position_id);
CREATE INDEX IF NOT EXISTS idx_loans_book ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_reader ON loans(reader_id);
CREATE INDEX IF NOT EXISTS idx_loans_employee ON loans(employee_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);

-- Триггеры
CREATE TRIGGER IF NOT EXISTS trg_loan_insert
AFTER INSERT ON loans
WHEN NEW.status = 'active'
BEGIN
    UPDATE books SET available = available - 1 WHERE book_id = NEW.book_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_loan_return
AFTER UPDATE OF return_date ON loans
WHEN NEW.return_date IS NOT NULL AND OLD.return_date IS NULL
BEGIN
    UPDATE books SET available = available + 1 WHERE book_id = NEW.book_id;
    UPDATE loans SET status = 'returned' WHERE loan_id = NEW.loan_id;
END;