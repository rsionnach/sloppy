"""Base pattern class and Issue dataclass."""

from __future__ import annotations

import ast
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from re import Pattern as RePattern


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Axis(Enum):
    """Slop detection axes."""

    NOISE = "noise"
    QUALITY = "quality"
    STYLE = "style"
    STRUCTURE = "structure"


@dataclass
class Issue:
    """A detected issue."""

    pattern_id: str
    severity: Severity
    axis: str
    file: Path
    line: int
    column: int
    message: str
    code: str | None = None


class BasePattern(ABC):
    """Base class for all detection patterns."""

    id: str = ""
    severity: Severity = Severity.MEDIUM
    axis: str = "noise"
    message: str = ""

    def create_issue(
        self,
        file: Path,
        line: int,
        column: int = 0,
        code: str | None = None,
        message: str | None = None,
    ) -> Issue:
        """Create an issue from this pattern."""
        return Issue(
            pattern_id=self.id,
            severity=self.severity,
            axis=self.axis,
            file=file,
            line=line,
            column=column,
            message=message or self.message,
            code=code,
        )

    def create_issue_from_node(
        self,
        node: ast.AST,
        file: Path,
        code: str | None = None,
        message: str | None = None,
    ) -> Issue:
        """Create an issue from an AST node."""
        return self.create_issue(
            file=file,
            line=getattr(node, "lineno", 0),
            column=getattr(node, "col_offset", 0),
            code=code,
            message=message,
        )


class RegexPattern(BasePattern):
    """Pattern that matches via regex on lines."""

    pattern: RePattern[str] | None = None

    def check_line(
        self,
        line: str,
        lineno: int,
        file: Path,
    ) -> list[Issue]:
        """Check a line for pattern matches."""
        if self.pattern is None:
            return []

        issues = []
        for match in self.pattern.finditer(line):
            issues.append(
                self.create_issue(
                    file=file,
                    line=lineno,
                    column=match.start(),
                    code=line.strip(),
                )
            )
        return issues


class ASTPattern(BasePattern):
    """Pattern that operates on AST nodes."""

    node_types: tuple[type, ...] = ()

    def check_node(
        self,
        node: ast.AST,
        file: Path,
        source_lines: list[str],
    ) -> list[Issue]:
        """Check an AST node for issues."""
        return []
