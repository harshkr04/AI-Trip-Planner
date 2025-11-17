# backend/utils/cache.py
import time
import json
from functools import wraps

def _safe_serialize(obj):
    """Try to JSON-serialize; fall back to repr if that fails."""
    try:
        return json.dumps(obj, default=str, sort_keys=True)
    except Exception:
        return repr(obj)

def ttl_cache(ttl_seconds: int = 60):
    """
    Simple in-memory TTL cache.
    Uses stable, hashable keys by serializing args/kwargs.
    """
    def decorator(fn):
        cache = {}

        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Build a safe key using function name + serialized args/kwargs
            key = (fn.__name__, _safe_serialize(args), _safe_serialize(kwargs))

            item = cache.get(key)
            if item:
                value, ts = item
                if time.time() - ts < ttl_seconds:
                    return value

            result = fn(*args, **kwargs)
            try:
                cache[key] = (result, time.time())
            except Exception:
                # If result itself is not serializable or another issue occurs,
                # still return result (do not crash).
                pass
            return result

        return wrapper
    return decorator
