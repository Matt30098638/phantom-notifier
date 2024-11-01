# database.py
import sqlite3
from datetime import datetime

DB_NAME = 'media_monitoring.db'

def initialize_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notified_releases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_date TEXT NOT NULL,
                age_rating TEXT,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def store_notified_release(title, release_date, age_rating):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notified_releases (title, release_date, age_rating)
            VALUES (?, ?, ?)
        ''', (title, release_date, age_rating))
        conn.commit()

def was_notified(title, release_date):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM notified_releases WHERE title = ? AND release_date = ?
        ''', (title, release_date))
        return cursor.fetchone() is not None
