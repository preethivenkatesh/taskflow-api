"""
Date Utilities - Helper functions for date operations
BUG: Date handling issues!
"""
from datetime import datetime, timedelta

def parse_date_string(date_str: str):
    """Parse date string to datetime"""
    # BUG 1: Hardcoded format, won't work for other formats
    return datetime.strptime(date_str, '%Y-%m-%d')

def calculate_business_days(start_date: datetime, end_date: datetime):
    """Calculate business days between dates"""
    # BUG 2: Doesn't account for weekends
    # BUG 3: Doesn't validate start < end
    delta = end_date - start_date
    return delta.days

def add_working_days(start_date: datetime, days: int):
    """Add working days to a date"""
    # BUG 4: Just adds days without considering weekends
    return start_date + timedelta(days=days)

def is_valid_date(date_str: str):
    """Check if date string is valid"""
    # BUG 5: Try-except missing, will crash on invalid date
    datetime.strptime(date_str, '%Y-%m-%d')
    return True

def get_month_boundaries(year: int, month: int):
    """Get first and last day of month"""
    # BUG 6: Doesn't handle December (month+1 = 13)
    # BUG 7: Doesn't validate month range
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    return first_day, last_day

def format_timestamp(timestamp: int):
    """Format unix timestamp to readable string"""
    # BUG 8: No validation for negative or future timestamps
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')
