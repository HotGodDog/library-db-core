# library-db-core

Библиотека для работы с базой данных автоматизированной системы управления библиотекой.

## Установка

```bash
pip install -i https://test.pypi.org/simple/ library-db-core
```

Для разработки:

```bash
git clone https://github.com/HotGodDog/library-db-core.git
cd library-db-core
make install
```

## Быстрый старт

```python
from library_db_core import Database

db = Database().connect()
db.create_tables()

# Загрузить тестовые данные из CSV
db.seed_from_csv("/путь/к/csv/")

books = db.get_all_books()
stats = db.get_statistics()

db.close()
```

## Конфигурация

Путь к базе данных задаётся переменной окружения:

```bash
export LIBRARY_DB_PATH=/путь/к/library.db
```

По умолчанию: `library.db` в текущей директории.

## CSV-файлы для seed_from_csv()

Метод `seed_from_csv()` загружает 8 CSV-файлов с разделителем `;`:

| Файл | Колонки |
|---|---|
| `positions.csv` | `position_id;name;description` |
| `categories.csv` | `category_id;name;description` |
| `publishers.csv` | `publisher_id;name;city;country` |
| `authors.csv` | `author_id;last_name;first_name;middle_name` |
| `employees.csv` | `employee_id;last_name;first_name;middle_name;position_id;phone;email;password` |
| `readers.csv` | `reader_id;last_name;first_name;middle_name;passport_num;phone;email;password;address;reg_date` |
| `books.csv` | `book_id;title;author_id;category_id;publisher_id;total_copies;year_published;pages;available;description` |
| `loans.csv` | `loan_id;book_id;reader_id;employee_id;loan_date;due_date;return_date` |

Справочные таблицы должны содержать явные `*_id`. Загрузка выполняется в порядке соблюдения внешних ключей.

## Разработка

```bash
make install    # Установка зависимостей
make test       # Запуск тестов
make build      # Сборка пакета
make upload     # Публикация на TestPyPI
make clean      # Очистка кэша и артефактов
make reset      # Полный сброс (clean + удаление БД)
make help       # Справка по командам
```

## Структура проекта

```
library-db-core/
├── src/library_db_core/
│   ├── __init__.py
│   ├── config.py          # Конфигурация (DB_PATH)
│   ├── database.py        # Класс Database
│   ├── models.py          # Модели данных
│   └── sql/
│       └── scheme.sql         # Схема базы данных
├── tests/
│   ├── conftest.py        # Фикстуры pytest
│   ├── test_database.py
│   ├── test_models.py
│   └── test_reports.py
├── Makefile
├── pyproject.toml
└── README.md
```