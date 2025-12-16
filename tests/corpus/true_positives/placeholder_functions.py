"""Placeholder functions that SHOULD be flagged.

Functions with just pass, ..., or raise NotImplementedError
that are NOT abstract methods should be flagged.
"""


def unimplemented_feature():
    """This function has no implementation."""
    pass


def another_placeholder():
    """Another unimplemented function."""
    ...


def todo_function():
    """Function that raises NotImplementedError."""
    raise NotImplementedError


def with_todo_comment():
    # TODO: implement this function
    pass


class RegularClass:
    """Regular class (not ABC/Protocol)."""

    def incomplete_method(self):
        """Method that should be implemented."""
        pass

    def stub_method(self):
        """Another stub."""
        ...
