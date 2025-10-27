from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class CacheService:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl_seconds: int = 300):
        """
        Initialize cache service.
        
        Args:
            default_ttl_seconds: Default time-to-live in seconds (default: 5 minutes)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if entry has expired
        if datetime.now() > entry["expires_at"]:
            # Remove expired entry
            del self.cache[key]
            return None
        
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now()
        }
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            pattern: If provided, only clear keys containing this pattern.
                    If None, clears entire cache.
        
        Returns:
            Number of entries cleared
        """
        if pattern is None:
            count = len(self.cache)
            self.cache.clear()
            return count
        
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.cache[key]
        
        return len(keys_to_delete)
    
    def clear_expired(self) -> int:
        """
        Remove all expired entries from cache.
        
        Returns:
            Number of expired entries removed
        """
        now = datetime.now()
        expired_keys = [
            k for k, v in self.cache.items()
            if now > v["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for v in self.cache.values()
            if now > v["expires_at"]
        )
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "keys": list(self.cache.keys())
        }

