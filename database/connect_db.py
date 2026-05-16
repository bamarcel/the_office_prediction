import sqlite3
import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "app_database.db"


def connect_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("PRAGMA journal_mode=WAL")   # meilleure concurrence
        conn.execute("PRAGMA foreign_keys=ON")    # contraintes FK actives
        return conn
    except sqlite3.Error as e:
        print(f"[{datetime.datetime.now()}] — Database connection error: {e}")
        return None
