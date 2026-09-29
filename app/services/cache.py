import time
from typing import Any, Optional, Dict, Tuple

class SimpleTTLCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self._storage: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._storage:
            value, expiry = self._storage[key]
            if time.time() < expiry:
                return value
            del self._storage[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._storage[key] = (value, expiry)

    def clear(self) -> None:
        self._storage.clear()

audit_cache = SimpleTTLCache()
