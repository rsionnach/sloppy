"""Tests for unused imports detection."""



from sloppy.detector import Detector


def test_unused_import_detected(tmp_python_file):
    """Test that unused imports are detected."""
    code = """
import os
import sys

print("hello")
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 2
    names = {i.message.split("'")[1] for i in unused}
    assert names == {"os", "sys"}


def test_used_import_not_flagged(tmp_python_file):
    """Test that used imports are not flagged."""
    code = """
import os

path = os.getcwd()
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 0


def test_from_import_unused(tmp_python_file):
    """Test that unused 'from x import y' is detected."""
    code = """
from os import path, getcwd

print(getcwd())
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 1
    assert "path" in unused[0].message


def test_aliased_import_unused(tmp_python_file):
    """Test that unused aliased imports are detected."""
    code = """
import numpy as np
import pandas as pd

print(np.array([1, 2, 3]))
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 1
    assert "pd" in unused[0].message


def test_type_annotation_counts_as_usage(tmp_python_file):
    """Test that imports used in type annotations are not flagged."""
    code = """
from typing import List, Optional

def process(items: List[str]) -> Optional[str]:
    return items[0] if items else None
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 0


def test_decorator_counts_as_usage(tmp_python_file):
    """Test that imports used as decorators are not flagged."""
    code = """
from functools import lru_cache

@lru_cache
def expensive_func(x):
    return x * 2
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 0


def test_base_class_counts_as_usage(tmp_python_file):
    """Test that imports used as base classes are not flagged."""
    code = """
from abc import ABC, abstractmethod

class MyClass(ABC):
    @abstractmethod
    def method(self):
        pass
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 0


def test_attribute_access_counts_as_usage(tmp_python_file):
    """Test that module.attr usage counts."""
    code = """
import os.path

exists = os.path.exists("/tmp")
"""
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 0


def test_disabled_pattern(tmp_python_file):
    """Test that unused_import can be disabled."""
    code = """
import os
import sys
"""
    file = tmp_python_file(code)
    detector = Detector(disabled_patterns=["unused_import"])
    issues = detector.scan([file])

    unused = [i for i in issues if i.pattern_id == "unused_import"]
    assert len(unused) == 0
