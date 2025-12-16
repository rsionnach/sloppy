"""Tests for structural pattern detection."""



from sloppy.detector import Detector


def test_bare_except_detected(tmp_python_file):
    """Test that bare except clauses are detected."""
    code = """
try:
    risky_operation()
except:
    pass
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    bare_issues = [i for i in issues if i.pattern_id == "bare_except"]
    assert len(bare_issues) == 1
    assert bare_issues[0].severity.value == "critical"


def test_broad_except_detected(tmp_python_file):
    """Test that broad Exception handling is detected."""
    code = """
try:
    risky_operation()
except Exception:
    pass
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    broad_issues = [i for i in issues if i.pattern_id == "broad_except"]
    assert len(broad_issues) == 1


def test_specific_except_not_flagged(tmp_python_file):
    """Test that specific exception handling is not flagged."""
    code = """
try:
    risky_operation()
except ValueError as e:
    handle_error(e)
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    except_issues = [i for i in issues if i.pattern_id in ("bare_except", "broad_except")]
    assert len(except_issues) == 0


def test_empty_except_detected(tmp_python_file):
    """Test that empty except blocks (just pass) are detected."""
    code = """
try:
    risky_operation()
except ValueError:
    pass
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    empty_issues = [i for i in issues if i.pattern_id == "empty_except"]
    assert len(empty_issues) == 1


def test_star_import_detected(tmp_python_file):
    """Test that wildcard imports are detected."""
    code = """
from os import *
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    star_issues = [i for i in issues if i.pattern_id == "star_import"]
    assert len(star_issues) == 1


def test_specific_import_not_flagged(tmp_python_file):
    """Test that specific imports are not flagged."""
    code = """
from os import path, getcwd
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    star_issues = [i for i in issues if i.pattern_id == "star_import"]
    assert len(star_issues) == 0


def test_single_method_class_detected(tmp_python_file):
    """Test that single-method classes are detected."""
    code = """
class Processor:
    def __init__(self, data):
        self.data = data

    def process(self):
        return self.data.strip()
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    single_method_issues = [i for i in issues if i.pattern_id == "single_method_class"]
    assert len(single_method_issues) == 1


def test_multi_method_class_not_flagged(tmp_python_file):
    """Test that multi-method classes are not flagged."""
    code = """
class Processor:
    def __init__(self, data):
        self.data = data

    def process(self):
        return self.data.strip()

    def validate(self):
        return bool(self.data)
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    single_method_issues = [i for i in issues if i.pattern_id == "single_method_class"]
    assert len(single_method_issues) == 0
