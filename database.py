import sqlite3
import os
import shutil
from datetime import datetime
from typing import Optional, List, Tuple

DB_FILE = 'bot_database.db'

def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table - track who can use the bot
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            is_allowed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Files table - track all uploaded files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            file_url TEXT,
            file_type TEXT,
            file_size INTEGER,
            service_used TEXT DEFAULT 'file_upload',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Migration: Add service_used column if it doesn't exist
    try:
        cursor.execute("PRAGMA table_info(files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'service_used' not in columns:
            cursor.execute('ALTER TABLE files ADD COLUMN service_used TEXT DEFAULT "file_upload"')
            # Backfill existing records
            cursor.execute('UPDATE files SET service_used = "file_upload" WHERE service_used IS NULL')
            conn.commit()
            print("✅ Migration: Added service_used column to files table")
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
    
    conn.commit()
    conn.close()

def add_or_update_user(user_id: int, username: str, full_name: str):
    """Add or update user in database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            full_name = excluded.full_name
    ''', (user_id, username, full_name))
    
    conn.commit()
    conn.close()

def is_user_allowed(user_id: int) -> bool:
    """Check if user has permission to use the bot"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT is_allowed FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] == 1 if result else False

def set_user_permission(user_id: int, allowed: bool):
    """Grant or revoke user permission"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET is_allowed = ? WHERE user_id = ?
    ''', (1 if allowed else 0, user_id))
    
    conn.commit()
    conn.close()

def get_all_users() -> List[Tuple]:
    """Get all users from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, full_name, is_allowed, created_at 
        FROM users 
        ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return users

def add_file_record(user_id: int, file_name: str, file_path: str, file_url: str, 
                   file_type: str, file_size: int, service_used: str = 'file_upload'):
    """Add file upload record to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO files (user_id, file_name, file_path, file_url, file_type, file_size, service_used)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, file_name, file_path, file_url, file_type, file_size, service_used))
    
    conn.commit()
    conn.close()

def get_all_files() -> List[Tuple]:
    """Get all files with user info"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.id, f.file_name, f.file_url, f.file_type, f.file_size, 
               f.service_used, f.uploaded_at, u.username, u.full_name
        FROM files f
        JOIN users u ON f.user_id = u.user_id
        ORDER BY f.uploaded_at DESC
    ''')
    
    files = cursor.fetchall()
    conn.close()
    
    return files

def get_user_files(user_id: int) -> List[Tuple]:
    """Get all files uploaded by specific user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, file_name, file_url, file_type, file_size, uploaded_at
        FROM files
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
    ''', (user_id,))
    
    files = cursor.fetchall()
    conn.close()
    
    return files

def get_stats() -> dict:
    """Get database statistics"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_allowed = 1')
    allowed_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM files')
    total_files = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(file_size) FROM files')
    total_size = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_users': total_users,
        'allowed_users': allowed_users,
        'total_files': total_files,
        'total_size': total_size
    }

# Initialize database on import
init_database()
