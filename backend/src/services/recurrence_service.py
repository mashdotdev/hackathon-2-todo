"""Recurrence service for calculating next execution times.

Provides utility functions for recurring task scheduling.
"""

from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta

from src.models.recurring_task_schedule import RecurrencePatternEnum


def calculate_next_execution(
    current: datetime,
    pattern: str,
) -> datetime:
    """Calculate the next execution time based on recurrence pattern.

    Args:
        current: The current/base datetime
        pattern: Recurrence pattern (daily/weekly/monthly)

    Returns:
        The next execution datetime

    Raises:
        ValueError: If pattern is invalid or 'none'
    """
    if pattern == RecurrencePatternEnum.DAILY.value or pattern == "daily":
        return current + relativedelta(days=1)
    elif pattern == RecurrencePatternEnum.WEEKLY.value or pattern == "weekly":
        return current + relativedelta(weeks=1)
    elif pattern == RecurrencePatternEnum.MONTHLY.value or pattern == "monthly":
        return current + relativedelta(months=1)
    elif pattern == RecurrencePatternEnum.NONE.value or pattern == "none":
        raise ValueError("Cannot calculate next execution for non-recurring task")
    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")


def calculate_initial_execution(
    due_date: Optional[datetime],
    pattern: str,
) -> datetime:
    """Calculate the initial execution time for a new recurring task.

    If due_date is provided, use it as the starting point.
    Otherwise, calculate from current time.

    Args:
        due_date: Optional due date for the first instance
        pattern: Recurrence pattern

    Returns:
        The initial execution datetime
    """
    if due_date:
        return due_date
    return calculate_next_execution(datetime.utcnow(), pattern)


def is_valid_recurrence_pattern(pattern: str) -> bool:
    """Check if a pattern string is a valid recurrence pattern.

    Args:
        pattern: Pattern string to validate

    Returns:
        True if valid, False otherwise
    """
    valid_patterns = {"none", "daily", "weekly", "monthly"}
    return pattern.lower() in valid_patterns
