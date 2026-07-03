import sqlite3
import os
from pathlib import Path
from datetime import datetime
from blog_agent import config

DB_PATH = config.OUTPUT_DIR / "blog_history.db"

def init_db():
    """
    Initializes the SQLite database and creates the blogs table if it doesn't exist.
    """
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            file_path TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_blog(title: str, topic: str, file_path: str, content: str):
    """
    Saves a generated blog post to the SQLite history database.
    """
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO blogs (title, topic, file_path, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (title, topic, file_path, content, created_at)
    )
    conn.commit()
    conn.close()

def get_all_blogs():
    """
    Fetches all historical blog metadata, ordered by newest first.
    """
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, topic, created_at, file_path FROM blogs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    blogs = []
    for row in rows:
        blogs.append({
            "id": row[0],
            "title": row[1],
            "topic": row[2],
            "created_at": row[3],
            "file_path": row[4]
        })
    return blogs

def get_blog_by_id(blog_id: int):
    """
    Fetches the full details of a specific blog post by its database ID.
    """
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT title, topic, file_path, content, created_at FROM blogs WHERE id = ?", (blog_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "title": row[0],
            "topic": row[1],
            "file_path": row[2],
            "content": row[3],
            "created_at": row[4]
        }
    return None
