"""Configuration for library database core

Database path can be set via LIBRARY_DB_PATH environment variable
Defaults to 'library.db' in current working directory
"""

import os

DB_PATH = os.getenv("LIBRARY_DB_PATH", "library.db")