"""
Miscellaneous functions for the PSTB. 

Functions:
    is_primitive
        Check if a value is a primitive type (int, float, str, bool, NoneType).
"""

from typing import Any


def is_primitive(value: Any) -> bool:
    """
    Check if a value is a primitive type (int, float, str, bool, NoneType).

    Args:
        value (Any): Value to check.

    Returns:
        bool: True if value is a primitive type, False otherwise.

    """
    return isinstance(value, (int, float, str, bool, type(None)))
