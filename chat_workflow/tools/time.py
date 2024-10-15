from datetime import datetime


async def get_datetime_now() -> str:
    """
    Get current datetime.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
