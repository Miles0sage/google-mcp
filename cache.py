import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


CACHE_DB = Path(__file__).parent / 'data' / 'cache.db'


def init_cache_db(db_path: Optional[Path] = None) -> None:
    """Initialize the cache database with the response_cache table."""
    if db_path is None:
        db_path = CACHE_DB

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at TEXT,
            ttl_seconds INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def cache_key(tool_name: str, **kwargs) -> str:
    """Generate a SHA256 hash key from tool name and sorted kwargs."""
    # Convert kwargs to a sorted JSON string to ensure consistent hashing
    sorted_kwargs = json.dumps(kwargs, sort_keys=True, separators=(',', ':'))
    key_string = f"{tool_name}:{sorted_kwargs}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def get_cached(key: str, db_path: Optional[Path] = None) -> Optional[str]:
    """Retrieve cached value if it exists and is not expired."""
    if db_path is None:
        db_path = CACHE_DB

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT value, created_at, ttl_seconds FROM response_cache WHERE key = ?',
        (key,)
    )
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    value, created_at_str, ttl_seconds = row
    created_at = datetime.fromisoformat(created_at_str)
    expiration_time = created_at + timedelta(seconds=ttl_seconds)

    if datetime.now() >= expiration_time:
        return None

    return value


def set_cache(key: str, value: str, ttl_seconds: int = 3600, db_path: Optional[Path] = None) -> None:
    """Insert or replace a cache entry."""
    if db_path is None:
        db_path = CACHE_DB

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute('''
        INSERT OR REPLACE INTO response_cache (key, value, created_at, ttl_seconds)
        VALUES (?, ?, ?, ?)
    ''', (key, value, created_at, ttl_seconds))

    conn.commit()
    conn.close()


def clear_expired(db_path: Optional[Path] = None) -> int:
    """Delete expired cache entries and return the count of deleted entries."""
    if db_path is None:
        db_path = CACHE_DB

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now_iso = datetime.now().isoformat()

    cursor.execute('''
        DELETE FROM response_cache
        WHERE datetime(created_at, '+' || ttl_seconds || ' seconds') < ?
    ''', (now_iso,))

    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count


def cache_stats(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Return cache statistics: total entries, expired count, total size in bytes."""
    if db_path is None:
        db_path = CACHE_DB

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total entries
    cursor.execute('SELECT COUNT(*) FROM response_cache')
    total_entries = cursor.fetchone()[0]

    # Count of expired entries
    now_iso = datetime.now().isoformat()
    cursor.execute('''
        SELECT COUNT(*)
        FROM response_cache
        WHERE datetime(created_at, '+' || ttl_seconds || ' seconds') < ?
    ''', (now_iso,))
    expired_count = cursor.fetchone()[0]

    # Total size in bytes
    cursor.execute('SELECT SUM(LENGTH(value)) FROM response_cache')
    size_result = cursor.fetchone()[0]
    total_size_bytes = size_result if size_result is not None else 0

    conn.close()

    return {
        'total_entries': total_entries,
        'expired_count': expired_count,
        'total_size_bytes': total_size_bytes
    }