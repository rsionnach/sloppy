"""Helper functions for pattern matching."""


def is_in_string_or_comment(line: str, position: int) -> bool:
    """
    Check if a position in a line is inside a string or after a comment.
    
    Args:
        line: The source line
        position: Character position to check
        
    Returns:
        True if the position is inside a string or after a # comment
    """
    prefix = line[:position]
    
    # Track string state and look for comments
    in_string = False
    string_char = None
    
    i = 0
    while i < len(prefix):
        char = prefix[i]
        
        # Handle escape sequences
        if char == '\\' and i + 1 < len(prefix):
            i += 2
            continue
        
        # Handle string boundaries
        if char in ('"', "'"):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
        
        # Handle comments (only outside strings)
        elif char == '#' and not in_string:
            return True  # Everything after # is a comment
        
        i += 1
    
    return in_string
