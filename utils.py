import pandas as pd

from config import DATASET_TITLES

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


def get_dataset_title(dataset_key: str) -> str:
    """Get human-readable title for a dataset key.

    Args:
        dataset_key: Short key for the dataset (e.g., 'ks2-performance').

    Returns:
        Formatted display title (e.g., 'KS2 Performance').
    """
    return DATASET_TITLES.get(dataset_key, dataset_key)


def build_dropdown_options(
    values: list[dict], label_key: str = "label", id_key: str = "id"
) -> list[dict]:
    """Convert a list of dicts into Dash dropdown options.

    Args:
        values: List of dictionaries, each containing keys for label and id.
        label_key: Key in each dict that contains the display label.
        id_key: Key in each dict that contains the value ID.

    Returns:
        list: List of dictionaries with 'label' and 'value' keys.
    """
    return [{"label": v[label_key], "value": v[id_key]} for v in values]
