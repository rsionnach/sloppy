"""Java patterns that SHOULD be flagged as hallucinations.

These are common mistakes when AI uses Java idioms in Python.
"""


def java_methods() -> None:
    """Java methods that don't exist in Python."""
    text = "hello"
    items = [1, 2, 3]

    # These SHOULD be flagged
    text.equals("hello")  # Should use: text == "hello"
    text.hashCode()  # Should use: hash(text)
    text.getClass()  # Should use: type(text)
    items.isEmpty()  # Should use: not items or len(items) == 0

    # Wrong case for Python methods
    text.startsWith("h")  # Should use: text.startswith("h")
    text.endsWith("o")  # Should use: text.endswith("o")


def java_print() -> None:
    """Java print statements."""
    # SHOULD be flagged
    System.out.println("Hello")  # Should use: print("Hello")
