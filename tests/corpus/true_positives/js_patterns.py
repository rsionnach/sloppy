"""JavaScript patterns that SHOULD be flagged as hallucinations.

These are common mistakes made by AI when generating Python code,
using JavaScript syntax instead of Python.
"""


def js_array_methods() -> None:
    """JavaScript array methods that don't exist in Python."""
    items = [1, 2, 3]

    # These SHOULD be flagged
    items.forEach(lambda x: print(x))  # Should use: for x in items
    items.unshift(0)  # Should use: items.insert(0, 0)

    # This accesses .length which doesn't exist


def js_string_methods() -> None:
    """JavaScript string methods."""
    text = "hello"

    # These SHOULD be flagged
    text.toUpperCase()  # Should use: text.upper()
    text.toLowerCase()  # Should use: text.lower()
    text.trimStart()  # Should use: text.lstrip()
    text.charAt(0)  # Should use: text[0]
    text.indexOf("l")  # Should use: text.find("l")
