import math
from datetime import datetime

def format_size(size_bytes: int) -> str:
    """Format bytes to a human readable string."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    try:
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    except Exception:
        return f"{size_bytes} B"

def format_date(timestamp: float) -> str:
    """Format a timestamp into a readable date string."""
    if not timestamp:
        return "Unknown"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Unknown"

def get_days_since(timestamp: float) -> int:
    """Calculate the number of days since the given timestamp."""
    if not timestamp:
        return 0
    try:
        dt = datetime.fromtimestamp(timestamp)
        delta = datetime.now() - dt
        return delta.days
    except Exception:
        return 0
