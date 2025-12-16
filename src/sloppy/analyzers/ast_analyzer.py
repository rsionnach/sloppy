"""AST-based code analysis."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sloppy.patterns.base import BasePattern, Issue


class ASTAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST for pattern violations."""

    def __init__(
        self,
        file: Path,
        source: str,
        patterns: list[BasePattern],
    ):
        self.file = file
        self.source = source
        self.source_lines = source.splitlines()
        self.patterns = patterns
        self.issues: list[Issue] = []
        self.nesting_depth = 0

    def analyze(self, tree: ast.AST) -> list[Issue]:
        """Run analysis on the AST."""
        self.visit(tree)
        return self.issues

    def _check_patterns(self, node: ast.AST) -> None:
        """Run all applicable patterns on a node."""
        for pattern in self.patterns:
            if hasattr(pattern, "check_node"):
                node_types = getattr(pattern, "node_types", ())
                if not node_types or isinstance(node, node_types):
                    issues = pattern.check_node(node, self.file, self.source_lines)
                    self.issues.extend(issues)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit except handlers."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from ... import statements."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function/method calls."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute access."""
        self._check_patterns(node)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statements, tracking nesting depth."""
        self._visit_nested_block(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loops, tracking nesting depth."""
        self._visit_nested_block(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loops, tracking nesting depth."""
        self._visit_nested_block(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit with statements, tracking nesting depth."""
        self._visit_nested_block(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try blocks, tracking nesting depth."""
        self._visit_nested_block(node)

    def _visit_nested_block(self, node: ast.AST) -> None:
        """Handle nested blocks with depth tracking."""
        self.nesting_depth += 1

        # Check for deep nesting
        if self.nesting_depth > 4:
            from sloppy.patterns.base import Issue, Severity

            self.issues.append(
                Issue(
                    pattern_id="deep_nesting",
                    severity=Severity.MEDIUM,
                    axis="style",
                    file=self.file,
                    line=getattr(node, "lineno", 0),
                    column=getattr(node, "col_offset", 0),
                    message=f"Code nested {self.nesting_depth} levels deep - consider refactoring",
                    code=None,
                )
            )

        self._check_patterns(node)
        self.generic_visit(node)
        self.nesting_depth -= 1
