"""Well-known constants that should NOT be flagged as magic numbers.

HTTP status codes, time units, and common computing values are
universally understood and don't need named constants.
"""


def check_response_status(status: int) -> str:
    """Check HTTP response status."""
    # HTTP status codes - universally understood
    if status == 200:
        return "OK"
    elif status == 201:
        return "Created"
    elif status == 204:
        return "No Content"
    elif status == 301:
        return "Moved Permanently"
    elif status == 302:
        return "Found"
    elif status == 400:
        return "Bad Request"
    elif status == 401:
        return "Unauthorized"
    elif status == 403:
        return "Forbidden"
    elif status == 404:
        return "Not Found"
    elif status == 500:
        return "Internal Server Error"
    elif status == 502:
        return "Bad Gateway"
    elif status == 503:
        return "Service Unavailable"
    else:
        return "Unknown"


def time_calculations() -> None:
    """Time unit calculations."""
    # Time units - universally understood
    seconds_per_minute = 60
    minutes_per_hour = 60
    hours_per_day = 24

    seconds_per_day = seconds_per_minute * minutes_per_hour * hours_per_day
    assert seconds_per_day == 86400


def computing_constants() -> None:
    """Common computing values."""
    # Powers of 2 - universally understood in computing

    # Common ports

    assert 1024 * 1024 == 1048576  # 1 MB
