"""Script with print in __main__ block.

Print statements in if __name__ == "__main__" blocks should NOT
be flagged as debug prints - they are legitimate CLI output.
"""


def calculate(x: int, y: int) -> int:
    """Calculate something."""
    return x + y


def process_data(data: list) -> list:
    """Process some data."""
    return [x * 2 for x in data]


if __name__ == "__main__":
    # These prints are legitimate - this is a script entry point
    print("Starting script...")

    result = calculate(5, 3)
    print(f"Result: {result}")

    data = [1, 2, 3, 4, 5]
    processed = process_data(data)
    print(f"Processed data: {processed}")

    print("Done!")
