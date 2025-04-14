"""
Utility functions for Taipan.
"""

from typing import Optional, Generator
from textual import events

def get_one(event: events.Key) -> Optional[str]:
    """
    Get a single character input, handling backspace and escape.
    Similar to the C code's get_one() function.
    
    Args:
        event: The key event to process
        
    Returns:
        The character if valid, None if escape or invalid
    """
    if event.key == "escape":
        return None
    
    if event.key == "backspace":
        return "\b"
    
    if event.character and len(event.character) == 1:
        return event.character.upper()
    
    return None

def get_num(maxlen: int) -> Generator[None, events.Key, int]:
    """
    Get a numeric input, handling backspace and escape.
    Similar to the C code's get_num() function.
    
    Args:
        maxlen: Maximum length of the number
        
    Returns:
        The number if valid, -1 if escape or invalid
    """
    result = ""
    
    while True:
        event = yield
        if event.key == "escape":
            return -1
        
        if event.key == "backspace":
            if result:
                result = result[:-1]
            continue
        
        if event.key == "enter":
            if not result:
                return 0
            try:
                return int(result)
            except ValueError:
                return -1
        
        if event.character and len(event.character) == 1 and event.character.isdigit():
            if len(result) < maxlen:
                result += event.character
    
    return -1 