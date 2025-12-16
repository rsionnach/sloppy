"""Cross-file duplicate code detection."""

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


@dataclass
class FunctionInfo:
    """Information about a function for duplicate detection."""

    name: str
    file: Path
    line: int
    source: str
    normalized: str


@dataclass
class DuplicatePair:
    """A pair of similar functions."""

    func_a: FunctionInfo
    func_b: FunctionInfo
    similarity: float


def extract_functions(file: Path, source: str) -> list[FunctionInfo]:
    """Extract function information from a file."""
    functions: list[FunctionInfo] = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return functions

    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "end_lineno") and node.end_lineno:
                func_lines = lines[node.lineno - 1 : node.end_lineno]
                func_source = "\n".join(func_lines)

                # Normalize: remove whitespace, comments, docstrings for comparison
                normalized = normalize_function(func_source)

                if len(normalized) > 50:  # Only consider non-trivial functions
                    functions.append(
                        FunctionInfo(
                            name=node.name,
                            file=file,
                            line=node.lineno,
                            source=func_source,
                            normalized=normalized,
                        )
                    )

    return functions


def normalize_function(source: str) -> str:
    """Normalize function source for comparison."""
    lines = []
    for line in source.splitlines():
        # Strip whitespace
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Skip comments
        if stripped.startswith("#"):
            continue

        # Skip docstrings (simple heuristic)
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue

        lines.append(stripped)

    return "\n".join(lines)


def find_duplicates(
    functions: list[FunctionInfo],
    threshold: float = 0.8,
) -> Iterator[DuplicatePair]:
    """Find duplicate/near-duplicate functions."""
    seen = set()

    for i, func_a in enumerate(functions):
        for func_b in functions[i + 1 :]:
            # Skip same file same function
            if func_a.file == func_b.file and func_a.name == func_b.name:
                continue

            # Skip if already compared
            pair_key = (
                min(str(func_a.file) + func_a.name, str(func_b.file) + func_b.name),
                max(str(func_a.file) + func_a.name, str(func_b.file) + func_b.name),
            )
            if pair_key in seen:
                continue
            seen.add(pair_key)

            # Compare normalized versions
            ratio = SequenceMatcher(
                None,
                func_a.normalized,
                func_b.normalized,
            ).ratio()

            if ratio >= threshold:
                yield DuplicatePair(
                    func_a=func_a,
                    func_b=func_b,
                    similarity=ratio,
                )
