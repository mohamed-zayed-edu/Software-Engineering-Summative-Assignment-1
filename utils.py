import pandas as pd

def extract_filter_id(value):
    """Extract ID from a filter value in the format "id :: label".

    Args:
        value: Filter value that may be in format "id :: label" or plain ID.

    Returns:
        The ID part (before '::') or the full value if no '::' present.
    """
    if pd.isna(value):
        return value
    value_str = str(value)
    if " :: " in value_str:
        return value_str.split(" :: ")[0]
    return value_str


def period_to_datetime(period_str):
    """Convert time period string to datetime.

    Args:
        period_str: Period string like "2024/2025" or "2024".

    Returns:
        Pandas Timestamp at September 1st of academic year, or pd.NaT on failure.
    """
    if "/" in str(period_str):
        year_str = str(period_str).split("/")[0]
    else:
        year_str = str(period_str)

    try:
        year = int(year_str)
        # Use September 1st as the academic year start
        return pd.Timestamp(year=year, month=9, day=1)
    except (ValueError, TypeError):
        return pd.NaT
