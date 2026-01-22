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


def extract_label(value):
    """Extract label from a filter value in format "id :: label".

    Args:
        value: Filter value that may be in format "id :: label" or plain value.

    Returns:
        The label part (after '::') or the full value if no '::' present.
    """
    if pd.isna(value):
        return value
    value_str = str(value)
    if " :: " in value_str:
        return value_str.split(" :: ", 1)[1]
    return value_str


def prepare_chart_data(df, indicator_id, selected_dim):
    """Process dataframe for plotting: convert to numeric, group, and filter.

    Args:
        df: Raw dataframe from query_dataset.
        indicator_id: Column name for the indicator values.
        selected_dim: The filter dimension ID used for grouping.

    Returns:
        Tuple of (df_numeric, warning_message).
        df_numeric has columns: time_period, filter_value_label, indicator_id.
        warning_message is empty string or note about excluded periods.

    Raises:
        ValueError: If selected filter dimension not found or no numeric data.
    """
    # Convert indicator to numeric
    df[indicator_id] = pd.to_numeric(df[indicator_id], errors="coerce")

    # Find the target filter column
    target_col = next(
        (col for col in df.columns if col.startswith(f"filter_{selected_dim}")),
        None,
    )
    if not target_col:
        raise ValueError("Selected filter dimension not found in returned data.")

    # Extract display labels
    df["filter_value_label"] = df[target_col].apply(extract_label)

    # Group by time period and filter value
    df = df.groupby(["time_period", "filter_value_label"], as_index=False).agg(
        {indicator_id: "mean"}
    )

    # Split numeric and non-numeric data
    df_numeric = df[df[indicator_id].notna() & (df[indicator_id].apply(lambda x: isinstance(x, (int, float))))].copy()
    df_non_numeric = df[~df.index.isin(df_numeric.index)].copy()

    if df_numeric.empty:
        raise ValueError(
            "No numerical data available for plotting. All values are non-numeric."
        )

    # Build warning for excluded periods
    warning_message = ""
    if not df_non_numeric.empty:
        excluded_years = df_non_numeric["time_period"].dt.year.unique()
        period_str = ", ".join(str(y) for y in sorted(excluded_years))
        warning_message = f"Note: Data for time period(s) {period_str} could not be plotted as values are non-numerical."

    return df_numeric, warning_message
