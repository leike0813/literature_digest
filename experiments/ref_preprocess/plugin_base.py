"""Plugin interface for reference preprocessing algorithms.

Any algorithm plugin must implement ReferencePreprocessor to be
compatible with the evaluation framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ReferencePreprocessor(ABC):
    """Abstract base for reference preprocessing algorithms.

    The ``process()`` method receives raw reference text and returns
    a structured dict with the same schema as the preprocessed JSON
    files in ``experiments/preprocessed/``::

        {
            "meta": {"entry_count": int, "entry_style": str, ...},
            "entries": [
                {
                    "raw": str,
                    "patterns": [{"pattern": str, "title_candidate": str,
                                  "author_candidates": list[str],
                                  "year_candidate": int | None, ...}],
                },
                ...
            ],
            "warnings": [str, ...],
            "suspect_blocks": [dict, ...],
        }
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for this algorithm, e.g. ``"line-first"``."""
        ...

    @abstractmethod
    def process(self, raw_text: str) -> dict[str, Any]:
        """Run preprocessing and return structured result."""
        ...


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_registry: dict[str, type[ReferencePreprocessor]] = {}


def register(cls: type[ReferencePreprocessor]) -> type[ReferencePreprocessor]:
    """Decorator: register a plugin class by its ``name`` property."""
    name = getattr(cls, "name", None)
    if callable(name):
        name = name.fget(cls) if isinstance(name, property) else name(cls)
    _registry[name] = cls
    return cls


def get_plugin(name: str) -> ReferencePreprocessor:
    """Instantiate a registered plugin by name."""
    if name not in _registry:
        available = ", ".join(sorted(_registry))
        raise KeyError(f"Unknown plugin {name!r}. Available: {available}")
    return _registry[name]()


def list_plugins() -> list[str]:
    """Return names of all registered plugins."""
    return sorted(_registry)
