"""Utility functions"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, cast

logger = logging.getLogger()


def safe_json_loads(data: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely parse JSON with default fallback

    Args:
        data: JSON string to parse
        default: Default value if parsing fails

    Returns:
        dict: Parsed JSON or default value
    """
    try:
        return cast(Dict[str, Any], json.loads(data))
    except (json.JSONDecodeError, TypeError):
        return default or {}


def format_currency(amount: float) -> str:
    """
    Format amount as currency string

    Args:
        amount: Dollar amount

    Returns:
        str: Formatted currency string
    """
    return f"${amount:.2f}"


def format_date(date_str: str) -> str:
    """
    Format date string to readable format

    Args:
        date_str: Date in "YYYY-MM-DD" format

    Returns:
        str: Formatted date (e.g., "May 15, 2026")
    """
    try:
        # Split by 'T' to ignore the time part
        date_only = date_str.split("T")[0]
        date_obj = datetime.strptime(date_only, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return date_str


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value

    Args:
        data: Dictionary to search
        *keys: Nested keys to access
        default: Default value if key not found

    Returns:
        Value at nested key or default
    """
    current: Any = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    return current if current is not None else default
