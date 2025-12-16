"""Axis 1: Information Utility (Noise) patterns."""

import ast
import re
from pathlib import Path

from sloppy.patterns.base import ASTPattern, Issue, RegexPattern, Severity


class DebugPrint(ASTPattern):
    """Detect debug print statements, excluding CLI contexts."""

    id = "debug_print"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Debug print statement - remove before production"
    node_types = (ast.Call,)

    # Files where print() is expected (CLI tools)
    CLI_FILE_PATTERNS = {"cli.py", "__main__.py", "main.py", "console.py", "commands.py"}

    # Directories where print() is expected (scripts, CLI tools)
    CLI_DIR_PATTERNS = {"scripts", "bin", "cli", "commands"}

    # CLI-related imports that indicate this is a CLI application
    CLI_IMPORTS = {"click", "typer", "argparse", "fire", "rich"}

    def check_node(
        self,
        node: ast.AST,
        file: Path,
        source_lines: list[str],
    ) -> list[Issue]:
        if not isinstance(node, ast.Call):
            return []

        # Check if this is a print() call
        if not (isinstance(node.func, ast.Name) and node.func.id == "print"):
            return []

        # Skip CLI-related files where print() is expected
        if file.name in self.CLI_FILE_PATTERNS:
            return []

        # Skip files in CLI-related directories
        for parent in file.parents:
            if parent.name in self.CLI_DIR_PATTERNS:
                return []

        # Check if the file has CLI-related imports (scan source lines)
        source_text = "\n".join(source_lines)
        for cli_import in self.CLI_IMPORTS:
            if f"import {cli_import}" in source_text or f"from {cli_import}" in source_text:
                return []

        # Check if print is inside if __name__ == "__main__" block
        if self._is_in_main_block(node, source_lines):
            return []

        lineno = getattr(node, "lineno", 0)
        code = source_lines[lineno - 1].strip() if 0 < lineno <= len(source_lines) else "print(...)"

        return [
            self.create_issue_from_node(
                node,
                file,
                code=code,
            )
        ]

    def _is_in_main_block(self, node: ast.AST, source_lines: list[str]) -> bool:
        """Check if the node is inside an if __name__ == '__main__' block."""
        lineno = getattr(node, "lineno", 0)
        if lineno <= 0:
            return False

        # Look backwards from the print statement to find if __name__ == "__main__"
        for i in range(lineno - 1, max(lineno - 100, -1), -1):
            if i < 0 or i >= len(source_lines):
                continue
            line = source_lines[i].strip()
            # Check for if __name__ == "__main__": pattern
            if line.startswith("if __name__") and "__main__" in line:
                return True
            # If we hit a function or class def at column 0, we're not in __main__ block
            if (line.startswith("def ") or line.startswith("class ")) and not source_lines[i].startswith(" "):
                return False

        return False


class DebugBreakpoint(RegexPattern):
    """Detect breakpoint() and pdb calls."""

    id = "debug_breakpoint"
    severity = Severity.HIGH
    axis = "noise"
    message = "Debug breakpoint - remove before production"
    pattern = re.compile(r"\b(breakpoint\s*\(|pdb\.set_trace\s*\(|import\s+pdb)")


class RedundantComment(RegexPattern):
    """Detect comments that just restate the code."""

    id = "redundant_comment"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Redundant comment restating obvious code"
    pattern = re.compile(
        r"#\s*(increment|decrement|set|assign|return|get|initialize|init|create)\s+\w+\s*$",
        re.IGNORECASE,
    )


class EmptyDocstring(RegexPattern):
    """Detect empty or placeholder docstrings."""

    id = "empty_docstring"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Empty or placeholder docstring"
    pattern = re.compile(r'"""(\s*|\s*TODO.*|\s*FIXME.*|\s*pass\s*|\s*\.\.\.\s*)"""', re.IGNORECASE)


class GenericDocstring(RegexPattern):
    """Detect non-informative generic docstrings."""

    id = "generic_docstring"
    severity = Severity.LOW
    axis = "noise"
    message = "Generic docstring provides no useful information"
    pattern = re.compile(
        r'"""(This (function|method|class) (does|is|handles?|returns?|takes?) (stuff|things|something|it|the)\.?)"""',
        re.IGNORECASE,
    )


class CommentedCodeBlock(RegexPattern):
    """Detect large blocks of commented-out code."""

    id = "commented_code_block"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Commented-out code block - remove or uncomment"
    pattern = re.compile(
        r"^#\s*(def |class |import |from |if |for |while |return |yield )",
    )


class ChangelogComment(RegexPattern):
    """Detect version history in comments."""

    id = "changelog_in_code"
    severity = Severity.LOW
    axis = "noise"
    message = "Version history belongs in git commits, not code comments"
    pattern = re.compile(
        r"#\s*v?\d+\.\d+.*[-:].*\b(added|fixed|changed|removed|updated)\b", re.IGNORECASE
    )


NOISE_PATTERNS = [
    DebugPrint(),
    DebugBreakpoint(),
    RedundantComment(),
    EmptyDocstring(),
    GenericDocstring(),
    CommentedCodeBlock(),
    ChangelogComment(),
]
