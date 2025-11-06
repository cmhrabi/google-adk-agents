"""
Configuration for persistent memory and session storage using SQLite.
"""
import os
from pathlib import Path

# Database file location - stores in the my_agent directory
DB_DIR = Path(__file__).parent
SESSION_DB_PATH = DB_DIR / "sessions.db"
MEMORY_DB_PATH = DB_DIR / "memory.db"

# SQLAlchemy connection strings
SESSION_SERVICE_URI = f"sqlite:///{SESSION_DB_PATH}"
MEMORY_SERVICE_URI = f"sqlite:///{MEMORY_DB_PATH}"

# Ensure database directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)
