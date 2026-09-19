import sqlite3
import os
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from typing import List, Dict, Optional, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "novel.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Bảng thông tin truyện
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS novel_info (
        id INTEGER PRIMARY KEY DEFAULT 1,
        book_id TEXT NOT NULL,
        title_zh TEXT,
        title_vi TEXT,
        author_zh TEXT,
        author_vi TEXT,
        description_zh TEXT,
        description_vi TEXT,
        source_url TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Bảng danh sách chương
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_num INTEGER NOT NULL,
        title_zh TEXT,
        title_vi TEXT,
        url TEXT UNIQUE,
        content_zh TEXT,
        content_vi TEXT,
        status TEXT DEFAULT 'pending', -- pending, crawled, translating, completed, error
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapter_num ON chapters(chapter_num)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapter_status ON chapters(status)")
    
    conn.commit()
    conn.close()

def save_novel_info(book_id: str, title_zh: str, title_vi: str = "", author_zh: str = "", author_vi: str = "", description_zh: str = "", description_vi: str = "", source_url: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO novel_info (id, book_id, title_zh, title_vi, author_zh, author_vi, description_zh, description_vi, source_url, updated_at)
    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
        title_zh = excluded.title_zh,
        title_vi = CASE WHEN excluded.title_vi != '' THEN excluded.title_vi ELSE novel_info.title_vi END,
        author_zh = excluded.author_zh,
        author_vi = CASE WHEN excluded.author_vi != '' THEN excluded.author_vi ELSE novel_info.author_vi END,
        description_zh = excluded.description_zh,
        description_vi = CASE WHEN excluded.description_vi != '' THEN excluded.description_vi ELSE novel_info.description_vi END,
        source_url = excluded.source_url,
        updated_at = CURRENT_TIMESTAMP
    """, (book_id, title_zh, title_vi, author_zh, author_vi, description_zh, description_vi, source_url))
    conn.commit()
    conn.close()

def get_novel_info() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM novel_info WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def upsert_chapter(chapter_num: int, title_zh: str, url: str, content_zh: str = "", title_vi: str = "", content_vi: str = "", status: str = "pending"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO chapters (chapter_num, title_zh, url, content_zh, title_vi, content_vi, status, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(url) DO UPDATE SET
        chapter_num = excluded.chapter_num,
        title_zh = excluded.title_zh,
        content_zh = CASE WHEN excluded.content_zh != '' THEN excluded.content_zh ELSE chapters.content_zh END,
        title_vi = CASE WHEN excluded.title_vi != '' THEN excluded.title_vi ELSE chapters.title_vi END,
        content_vi = CASE WHEN excluded.content_vi != '' THEN excluded.content_vi ELSE chapters.content_vi END,
        status = CASE WHEN excluded.status != 'pending' THEN excluded.status ELSE chapters.status END,
        updated_at = CURRENT_TIMESTAMP
    """, (chapter_num, title_zh, url, content_zh, title_vi, content_vi, status))
    conn.commit()
    conn.close()

def update_chapter_translation(chapter_num: int, title_vi: str, content_vi: str, status: str = "completed"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE chapters 
    SET title_vi = ?, content_vi = ?, status = ?, updated_at = CURRENT_TIMESTAMP
    WHERE chapter_num = ?
    """, (title_vi, content_vi, status, chapter_num))
    conn.commit()
    conn.close()

def get_chapter(chapter_num: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chapters WHERE chapter_num = ?", (chapter_num,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_chapters_list(limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, chapter_num, title_zh, title_vi, url, status, created_at, updated_at,
           length(content_zh) as len_zh, length(content_vi) as len_vi
    FROM chapters 
    ORDER BY chapter_num ASC
    LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_prev_next_chapter(chapter_num: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chapter_num, title_vi, title_zh FROM chapters WHERE chapter_num < ? ORDER BY chapter_num DESC LIMIT 1", (chapter_num,))
    prev_chap = cursor.fetchone()
    cursor.execute("SELECT chapter_num, title_vi, title_zh FROM chapters WHERE chapter_num > ? ORDER BY chapter_num ASC LIMIT 1", (chapter_num,))
    next_chap = cursor.fetchone()
    conn.close()
    return dict(prev_chap) if prev_chap else None, dict(next_chap) if next_chap else None

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM chapters")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as completed FROM chapters WHERE status = 'completed' AND content_vi IS NOT NULL AND content_vi != ''")
    completed = cursor.fetchone()["completed"]
    cursor.execute("SELECT MIN(chapter_num) as min_chap, MAX(chapter_num) as max_chap FROM chapters")
    min_max = cursor.fetchone()
    conn.close()
    return {
        "total": total,
        "completed": completed,
        "min_chapter": min_max["min_chap"] if min_max else None,
        "max_chapter": min_max["max_chap"] if min_max else None
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
