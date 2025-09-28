from typing import Dict, Any, Optional

class QueryCache:
    """A simple in-memory cache for query results."""
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieves an item from the cache if it exists."""
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        """Adds an item to the cache."""
        self._cache[key] = value

    def clear(self):
        """Clears the entire cache."""
        self._cache.clear()