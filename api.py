"""API interaction functions for EES API."""

import requests

# Base URL for the EES API
BASE_URL = "https://api.education.gov.uk/statistics/v1"


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


def get_metadata(dataset_id: str) -> dict:
    """Retrieve metadata for a dataset.

    Fetches available indicators, filters, geographic levels,
    locations, and time periods.

    Args:
        dataset_id: Unique identifier for the dataset.

    Returns:
        Metadata dictionary with keys: 'filters', 'indicators', 'geographicLevels',
        'locations', 'timePeriods'. Each contains list of metadata objects.

    Raises:
        requests.HTTPError: If API request fails.
    """
    return get_json(f"data-sets/{dataset_id}/meta")
