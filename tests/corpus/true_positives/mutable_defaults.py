"""Mutable default arguments that SHOULD be flagged.

Using mutable objects (list, dict, set) as default arguments
is a common Python gotcha that should be flagged.
"""


def bad_list_default(items=[]):  # noqa: B006
    """Mutable list default - SHOULD be flagged."""
    items.append(1)
    return items


def bad_dict_default(config={}):  # noqa: B006
    """Mutable dict default - SHOULD be flagged."""
    config["key"] = "value"
    return config


def bad_set_default(seen=set()):  # noqa: B006
    """Mutable set default - SHOULD be flagged."""
    seen.add(1)
    return seen


class BadDefaults:
    """Class with mutable default arguments."""

    def method_with_list(self, items=[]):  # noqa: B006
        """SHOULD be flagged."""
        return items

    def method_with_dict(self, data={}):  # noqa: B006
        """SHOULD be flagged."""
        return data
