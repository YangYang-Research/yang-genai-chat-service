from langchain.tools import tool
from datetime import datetime
import pytz

@tool("DateTimeTool", return_direct=True)
def datetime_tool(timezone: str = "UTC", fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get the current date and time.

    Args:
        timezone (str, optional): The timezone name (e.g. "UTC", "Asia/Ho_Chi_Minh").
        fmt (str, optional): The datetime format string using Python strftime format codes.

    Returns:
        str: The current date and time in the requested timezone and format.

    Example:
        - "What time is it now in Tokyo?"
        - "Give me today’s date in ISO format."
        - "What is the current UTC time?"
    """
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        return f"❌ Unknown timezone: {timezone}. Try a valid one like 'UTC' or 'Asia/Ho_Chi_Minh'."

    now = datetime.now(tz)
    return f"🕒 Current time in {timezone}: {now.strftime(fmt)}"
