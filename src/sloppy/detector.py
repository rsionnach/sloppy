"""Main detection orchestration."""

from __future__ import annotations

import ast
from pathlib import Path

from sloppy.analyzers.ast_analyzer import ASTAnalyzer
from sloppy.analyzers.dead_code import find_dead_code
from sloppy.analyzers.duplicates import find_cross_file_duplicates
from sloppy.analyzers.unused_imports import find_unused_imports
from sloppy.patterns import get_all_patterns
from sloppy.patterns.base import Issue

SEVERITY_ORDER = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


class Detector:
    """Main detector that orchestrates all pattern checks."""

    def __init__(
        self,
        ignore_patterns: list[str] | None = None,
        include_patterns: list[str] | None = None,
        disabled_patterns: list[str] | None = None,
        min_severity: str = "low",
    ):
        self.ignore_patterns = ignore_patterns or []
        self.include_patterns = include_patterns or []
        self.disabled_patterns: set[str] = set(disabled_patterns or [])
        self.min_severity = min_severity
        self.min_severity_level = SEVERITY_ORDER.get(min_severity, 0)

        # Load patterns
        self.patterns = [p for p in get_all_patterns() if p.id not in self.disabled_patterns]

    def scan(self, paths: list[Path]) -> list[Issue]:
        """Scan all paths and return issues."""
        issues: list[Issue] = []
        file_contents: list[tuple[Path, str]] = []  # For cross-file analysis

        for path in paths:
            if path.is_file():
                if self._should_scan(path):
                    file_issues, content = self._scan_file_with_content(path)
                    issues.extend(file_issues)
                    if content:
                        file_contents.append((path, content))
            elif path.is_dir():
                for file_path in path.rglob("*.py"):
                    if self._should_scan(file_path):
                        file_issues, content = self._scan_file_with_content(file_path)
                        issues.extend(file_issues)
                        if content:
                            file_contents.append((file_path, content))

        # Run cross-file analysis
        if "duplicate_code" not in self.disabled_patterns and len(file_contents) > 1:
            issues.extend(find_cross_file_duplicates(file_contents))

        # Filter by severity
        issues = [
            i for i in issues if SEVERITY_ORDER.get(i.severity.value, 0) >= self.min_severity_level
        ]

        # Sort by severity (critical first), then by file, then by line
        issues.sort(
            key=lambda i: (
                -SEVERITY_ORDER.get(i.severity.value, 0),
                i.file,
                i.line,
            )
        )

        return issues

    def _should_scan(self, path: Path) -> bool:
        """Check if a file should be scanned."""
        if path.suffix != ".py":
            return False

        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if path.match(pattern):
                return False

        # Check include patterns (if specified, file must match at least one)
        if self.include_patterns:
            matched = False
            for pattern in self.include_patterns:
                if path.match(pattern) or self._match_glob(path, pattern):
                    matched = True
                    break
            if not matched:
                return False

        return True

    def _match_glob(self, path: Path, pattern: str) -> bool:
        """Match path against a glob pattern with ** support."""
        import fnmatch

        path_str = str(path)
        # Handle ** patterns by checking if pattern matches any part of path
        if "**" in pattern:
            # Convert ** glob to regex-like matching
            # e.g., "scripts/**/*.py" should match "scripts/foo/bar.py"
            pattern.replace("**", "*").split("/")
            return fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                path_str, pattern.replace("**", "*")
            )
        return fnmatch.fnmatch(path_str, pattern)

    def _scan_file(self, path: Path) -> list[Issue]:
        """Scan a single file."""
        issues, _ = self._scan_file_with_content(path)
        return issues

    def _scan_file_with_content(self, path: Path) -> tuple[list[Issue], str | None]:
        """Scan a single file and return issues with content."""
        issues: list[Issue] = []

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return issues, None

        # Parse AST
        try:
            tree = ast.parse(content, filename=str(path))
        except SyntaxError:
            return issues, None

        # Run AST analyzer
        analyzer = ASTAnalyzer(path, content, self.patterns)
        issues.extend(analyzer.analyze(tree))

        # Run line-based patterns
        lines = content.splitlines()
        for pattern in self.patterns:
            if hasattr(pattern, "check_line"):
                for lineno, line in enumerate(lines, start=1):
                    pattern_issues = pattern.check_line(line, lineno, path)
                    issues.extend(pattern_issues)

        # Run file-level analyzers
        if "unused_import" not in self.disabled_patterns:
            issues.extend(find_unused_imports(path, content))

        if "dead_code" not in self.disabled_patterns:
            issues.extend(find_dead_code(path, content))

        return issues, content
