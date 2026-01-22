"""API interaction functions for EES API."""

from collections import OrderedDict
from functools import lru_cache

import requests
import pandas as pd

from utils import extract_filter_id, period_to_datetime
from config import BASE_URL


def get_json(endpoint: str, params: dict | None = None) -> dict:
    """Call an EES API GET endpoint and return parsed JSON.

    Args:
        endpoint: Relative API path.
        params (optional): Query parameters for the request.

    Returns:
        dict: Parsed JSON response as dictionary.

    Raises:
        requests.HTTPError: If API returns an error status code.
    """
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Accept": "application/json",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


@lru_cache(maxsize=10)
def get_metadata(dataset_id: str) -> dict:
    """Retrieve metadata for a dataset.

    Fetches available indicators, filters, geographic levels,
    locations, and time periods. Results are cached for performance.

    Args:
        dataset_id: Unique identifier for the dataset.

    Returns:
        Metadata dictionary with keys: 'filters', 'indicators', 'geographicLevels',
        'locations', 'timePeriods'. Each contains list of metadata objects.

    Raises:
        requests.HTTPError: If API request fails.
    """
    return get_json(f"data-sets/{dataset_id}/meta")


def post_query(endpoint: str, payload: dict) -> dict:
    """POST a data query to the EES API.

    Args:
        endpoint: Relative API path to POST to.
        payload: JSON payload containing query criteria, indicators, and filters.

    Returns:
        dict: Parsed JSON response as dictionary, including 'results' (paginated data)
        and 'paging' info (totalPages, page, pageSize).

    Raises:
        requests.HTTPError: If the API returns an error status code.
    """
    url = f"{BASE_URL}/{endpoint}"

    headers = {
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


# Cache for query results
query_cache = OrderedDict()


def make_hashable(obj):
    """Convert nested dicts/lists to hashable tuples."""
    if isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return tuple(make_hashable(item) for item in obj)
    return obj


def query_dataset(
    dataset_id: str,
    indicator_id: str,
    geo_level_codes: list[str],
    period_list: list[str],
    filters: dict | None = None,
) -> pd.DataFrame:
    """Query a dataset to retrieve indicator values with client-side filtering.

    Fetches data from the EES API with pagination, applies client-side filtering,
    and converts time periods to datetime for time series plotting.
    Results are cached to improve performance on repeated queries.

    Args:
        dataset_id: Unique identifier for the dataset.
        indicator_id: ID of the indicator to retrieve values for.
        geo_level_codes: List of geographic level codes.
        period_list: List of time periods as strings.
        filters (optional): Optional dict with filter criteria.

    Returns:
        DataFrame: with columns time_period (datetime), geographic_level, location_name,
        indicator_id (numeric values), and filter_* columns for each dimension.

    Raises:
        ValueError: If API returns no results or pagination fails.
        requests.HTTPError: If API request fails.
    """
    # Check cache first
    cache_key = (
        dataset_id,
        indicator_id,
        tuple(sorted(geo_level_codes)),
        tuple(sorted(period_list)),
        make_hashable(filters) if filters else None,
    )
    if cache_key in query_cache:
        return query_cache[cache_key].copy()

    # Get metadata to find available time period codes
    meta = get_metadata(dataset_id)
    time_periods_meta = meta.get("timePeriods", [])

    # Build time period criteria using codes from metadata
    time_period_criteria = []
    for p in period_list:
        matching = next((tp for tp in time_periods_meta if tp.get("period") == p), None)
        if matching:
            time_period_criteria.append(
                {"code": matching.get("code"), "period": matching.get("period")}
            )
        else:
            time_period_criteria.append({"code": "AY", "period": p})

    payload = {
        "criteria": {
            "geographicLevels": {"in": geo_level_codes},
            "timePeriods": {"in": time_period_criteria},
        },
        "indicators": [indicator_id],
        "debug": True,  # Enable debug mode to get human-readable labels
    }

    # Fetch all pages of results
    all_results = []
    page = 1
    total_pages = 1

    while page <= total_pages:
        paginated_payload = payload.copy()
        paginated_payload["page"] = page

        data = post_query(f"data-sets/{dataset_id}/query", paginated_payload)

        # Check for warnings
        warnings = data.get("warnings", [])
        if warnings:
            for warning in warnings:
                if warning.get("code") == "NoResults":
                    raise ValueError(
                        f"The query returned no data. Dataset may not have this combination of criteria. Warnings: {warnings}"
                    )

        # Get pagination info
        paging = data.get("paging", {})
        total_pages = paging.get("totalPages", 1)

        results = data.get("results", [])
        all_results.extend(results)

        page += 1

    # Convert results into a DF
    records = []
    for res in all_results:
        time_period = res.get("timePeriod", {}).get("period", "Unknown")
        geo_level = res.get("geographicLevel", "Unknown")
        locations = res.get("locations", {})
        location_name = next(iter(locations.values())) if locations else "Unknown"
        values = res.get("values", {})
        indicator_value = None

        # Look for the indicator_id in the values dict
        for key, val in values.items():
            if indicator_id in key:
                try:
                    indicator_value = float(val)
                except (ValueError, TypeError):
                    # Keep non-numerical values as strings ("suppressed", "N/A", etc.)
                    indicator_value = str(val) if val is not None else None
                break

        # Extract filter values from response
        filter_values = res.get("filters", {})

        # Include all records, even with non-numerical values
        if indicator_value is not None:
            record = {
                "time_period": time_period,
                "geographic_level": geo_level,
                "location_name": location_name,
                indicator_id: indicator_value,
            }
            # Add filter columns
            for filter_key, filter_val in filter_values.items():
                record[f"filter_{filter_key}"] = filter_val
            records.append(record)

    df = pd.DataFrame(records)

    # Apply client-side filtering if filters are provided - API filtering not functional
    if filters and not df.empty:
        for filter_name, filter_criteria in filters.items():
            filter_col_prefix = f"filter_{filter_name}"
            matching_col = None
            for col in df.columns:
                if col.startswith(filter_col_prefix):
                    matching_col = col
                    break

            if matching_col:
                if "in" in filter_criteria:
                    allowed_values = filter_criteria["in"]
                    filter_ids = df[matching_col].apply(extract_filter_id)
                    df = df[filter_ids.isin(allowed_values)]
                elif "eq" in filter_criteria:
                    filter_ids = df[matching_col].apply(extract_filter_id)
                    df = df[filter_ids == filter_criteria["eq"]]

    # Convert time_period to datetime for time series plotting
    if not df.empty and "time_period" in df.columns:
        try:
            df["time_period"] = df["time_period"].apply(period_to_datetime)
            df = df.sort_values("time_period")
        except Exception:
            # If conversion fails, just leave as-is
            pass

    # Cache result with FIFO eviction
    if len(query_cache) >= 50:
        query_cache.popitem(last=False)  # Remove oldest entry
    query_cache[cache_key] = df.copy()

    return df
