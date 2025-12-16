"""Hallucinated imports that SHOULD be flagged.

These are imports from wrong modules - a common AI mistake.
"""
# These SHOULD be flagged as hallucinated imports
from typing import dataclass  # noqa: F401 - Should be: from dataclasses import dataclass
from collections import dataclass  # noqa: F401 - Should be: from dataclasses import dataclass
from json import parse  # noqa: F401 - Should be: json.loads()
from json import stringify  # noqa: F401 - Should be: json.dumps()


def use_imports() -> None:
    """Use the imports to avoid unused import warnings."""
    pass
