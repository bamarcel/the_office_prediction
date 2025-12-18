import sqlite3
import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "app_database.db"

def connect_db():
    try:
        print("[" + str(datetime.datetime.now()) + "] — Connecting to the database...")
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"[" + str(datetime.datetime.now()) + "] — Database connection error: {e}")
        return None