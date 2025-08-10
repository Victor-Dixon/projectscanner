# AUTO-GENERATED __init__.py
# DO NOT EDIT MANUALLY - changes may be overwritten

"""Top level package for projectscanner.

The package exposes certain submodules on import. Historically this file
assumed that a ``scanner`` module was always available, which caused import
errors in minimal environments such as unit tests.  To improve resilience we
now attempt the import defensively and continue even if the module is missing.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:  # pragma: no cover - exercised indirectly during imports
    from . import scanner  # type: ignore
except Exception as exc:  # pragma: no cover - logging branch
    logger.debug("Optional scanner module not available: %s", exc)
    scanner = None  # type: ignore

__all__ = ["scanner"]
