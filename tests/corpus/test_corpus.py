"""Test suite for false positive and true positive corpus.

This test suite validates that:
1. False positive files do NOT trigger unexpected warnings
2. True positive files DO trigger expected warnings
"""
from pathlib import Path

from sloppy.detector import Detector

CORPUS_DIR = Path(__file__).parent


class TestFalsePositives:
    """Tests that validate we don't flag valid code."""

    def test_cli_with_print_no_debug_print_warning(self) -> None:
        """CLI files with print() should not trigger debug_print."""
        file = CORPUS_DIR / "false_positives" / "cli_with_print.py"
        detector = Detector()
        issues = detector.scan([file])

        debug_prints = [i for i in issues if i.pattern_id == "debug_print"]
        assert len(debug_prints) == 0, f"Unexpected debug_print warnings: {debug_prints}"

    def test_abstract_methods_no_placeholder_warning(self) -> None:
        """Abstract methods should not trigger placeholder warnings."""
        file = CORPUS_DIR / "false_positives" / "abstract_methods.py"
        detector = Detector()
        issues = detector.scan([file])

        placeholders = [
            i
            for i in issues
            if i.pattern_id
            in ("pass_placeholder", "ellipsis_placeholder", "notimplemented_placeholder")
        ]
        assert len(placeholders) == 0, f"Unexpected placeholder warnings: {placeholders}"

    def test_valid_python_methods_no_hallucination_warning(self) -> None:
        """Valid Python methods should not trigger hallucinated_method."""
        file = CORPUS_DIR / "false_positives" / "valid_python_methods.py"
        detector = Detector()
        issues = detector.scan([file])

        hallucinated = [i for i in issues if i.pattern_id == "hallucinated_method"]
        assert len(hallucinated) == 0, f"Unexpected hallucinated_method warnings: {hallucinated}"

    def test_main_block_print_no_debug_print_warning(self) -> None:
        """Print in __main__ block should not trigger debug_print."""
        file = CORPUS_DIR / "false_positives" / "main_block_print.py"
        detector = Detector()
        issues = detector.scan([file])

        debug_prints = [i for i in issues if i.pattern_id == "debug_print"]
        assert len(debug_prints) == 0, f"Unexpected debug_print warnings: {debug_prints}"

    def test_well_known_constants_no_magic_number_warning(self) -> None:
        """Well-known constants should not trigger magic_number."""
        file = CORPUS_DIR / "false_positives" / "well_known_constants.py"
        detector = Detector()
        issues = detector.scan([file])

        # Filter for magic numbers that are NOT in the well-known list
        magic_numbers = [i for i in issues if i.pattern_id == "magic_number"]
        # Allow some magic numbers (like 86400) but not HTTP codes, time units, etc.
        unexpected = [
            i
            for i in magic_numbers
            if any(
                code in str(i.line)
                for code in ["200", "201", "204", "301", "400", "401", "403", "404", "500"]
            )
        ]
        assert len(unexpected) == 0, f"HTTP status codes flagged as magic numbers: {unexpected}"


class TestTruePositives:
    """Tests that validate we DO flag problematic code."""

    def test_js_patterns_flagged(self) -> None:
        """JavaScript patterns should be flagged."""
        file = CORPUS_DIR / "true_positives" / "js_patterns.py"
        detector = Detector()
        issues = detector.scan([file])

        # Should flag forEach, unshift, length, toUpperCase, etc.
        hallucinated = [
            i for i in issues if i.pattern_id in ("hallucinated_method", "hallucinated_attribute")
        ]
        assert len(hallucinated) >= 3, f"Expected JS patterns to be flagged, got: {hallucinated}"

    def test_hallucinated_imports_flagged(self) -> None:
        """Hallucinated imports should be flagged."""
        file = CORPUS_DIR / "true_positives" / "hallucinated_imports.py"
        detector = Detector()
        issues = detector.scan([file])

        hallucinated = [i for i in issues if i.pattern_id == "hallucinated_import"]
        assert len(hallucinated) >= 2, f"Expected hallucinated imports, got: {hallucinated}"

    def test_placeholder_functions_flagged(self) -> None:
        """Placeholder functions should be flagged."""
        file = CORPUS_DIR / "true_positives" / "placeholder_functions.py"
        detector = Detector()
        issues = detector.scan([file])

        placeholders = [
            i
            for i in issues
            if i.pattern_id
            in ("pass_placeholder", "ellipsis_placeholder", "notimplemented_placeholder")
        ]
        assert len(placeholders) >= 3, f"Expected placeholder warnings, got: {placeholders}"

    def test_mutable_defaults_flagged(self) -> None:
        """Mutable default arguments should be flagged."""
        file = CORPUS_DIR / "true_positives" / "mutable_defaults.py"
        detector = Detector()
        issues = detector.scan([file])

        mutable = [i for i in issues if i.pattern_id == "mutable_default_arg"]
        assert len(mutable) >= 3, f"Expected mutable default warnings, got: {mutable}"

    def test_java_patterns_flagged(self) -> None:
        """Java patterns should be flagged."""
        file = CORPUS_DIR / "true_positives" / "java_patterns.py"
        detector = Detector()
        issues = detector.scan([file])

        hallucinated = [i for i in issues if i.pattern_id == "hallucinated_method"]
        assert len(hallucinated) >= 2, f"Expected Java patterns to be flagged, got: {hallucinated}"
