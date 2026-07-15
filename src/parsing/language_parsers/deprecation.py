from __future__ import annotations

import functools
import warnings


def deprecated(message: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            warnings.warn(f"Deprecated: {func.__name__} - {message}", DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapped
    return decorator
