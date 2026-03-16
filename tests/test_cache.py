import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from cache import init_cache_db, cache_key, get_cached, set_cache, clear_expired, cache_stats


def test_cache_miss_returns_none(tmp_path):
    """Test that get_cached returns None when key doesn't exist"""
    db_path = tmp_path / "test_cache.db"

    # Initialize cache database
    init_cache_db(db_path)

    # Try to get a non-existent key
    result = get_cached("nonexistent_key", db_path=db_path)

    assert result is None


def test_cache_hit_returns_value(tmp_path):
    """Test that get_cached returns the correct value when key exists and not expired"""
    db_path = tmp_path / "test_cache.db"

    # Initialize cache database
    init_cache_db(db_path)

    # Set a cache entry
    key = cache_key("test_tool", param1="value1")
    value = "test_value"
    set_cache(key, value, ttl_seconds=3600, db_path=db_path)

    # Retrieve the cached value
    result = get_cached(key, db_path=db_path)

    assert result == value


def test_expired_entry_returns_none(tmp_path):
    """Test that get_cached returns None when key exists but is expired"""
    db_path = tmp_path / "test_cache.db"

    # Initialize cache database
    init_cache_db(db_path)

    # Set a cache entry with a very short TTL
    key = cache_key("test_tool", param1="value1")
    value = "test_value"
    set_cache(key, value, ttl_seconds=0, db_path=db_path)  # Expired immediately

    # Try to retrieve the expired value
    result = get_cached(key, db_path=db_path)

    assert result is None


def test_clear_expired_removes_old_entries(tmp_path):
    """Test that clear_expired removes expired entries and returns count"""
    db_path = tmp_path / "test_cache.db"

    # Initialize cache database
    init_cache_db(db_path)

    # Set a few cache entries with expired TTL
    key1 = cache_key("test_tool1", param1="value1")
    key2 = cache_key("test_tool2", param2="value2")
    value = "test_value"

    set_cache(key1, value, ttl_seconds=0, db_path=db_path)  # Expired
    set_cache(key2, value, ttl_seconds=0, db_path=db_path)  # Expired

    # Set a non-expired entry
    key3 = cache_key("test_tool3", param3="value3")
    set_cache(key3, value, ttl_seconds=3600, db_path=db_path)  # Not expired

    # Clear expired entries
    deleted_count = clear_expired(db_path=db_path)

    # Should have deleted at least 2 expired entries
    assert deleted_count >= 2

    # Check that expired entries are gone
    result1 = get_cached(key1, db_path=db_path)
    result2 = get_cached(key2, db_path=db_path)

    assert result1 is None
    assert result2 is None

    # Verify clear_expired ran successfully (deleted something)
    assert deleted_count > 0