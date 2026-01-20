# Education Data Insights Explorer

A dashboard for exploring education statistics from the Department for Education.

## Structure

- `api.py`: Core API client.
- `app.py`: main app.
- `test_api.py`: Pytest suite covering API helper functions and query logic with mocks.

## Technical documentation

### API

- Location: [api.py](api.py)
- Helpers: `get_json(endpoint, params=None)` and `post_query(endpoint, payload)` wrap the EES API with common headers, 30s timeout, and `raise_for_status()` to raise HTTP errors.
- Metadata: `get_metadata(dataset_id)` fetches dataset meta for querying.
- Query pipeline: `query_dataset(dataset_id, indicator_id, geo_level_codes, period_list, filters=None)` builds criteria, resolves time period codes from metadata, paginates through all result pages, flattens responses to a DataFrame, and converts academic year periods to datetimes when possible.
- Client-side filtering: `filters` uses simple `in` or `eq` semantics; filter IDs are extracted from API labels so you can pass raw IDs.
- Non-numeric values: indicator values that cannot coerce to float are kept as strings (e.g., "suppressed"), so downstream code should handle both numeric and string types.
- Error handling: raises `ValueError` when API warns of `NoResults`; HTTP errors propagate from `requests` exceptions.


## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## Run

Start the Dash server:
```bash
python app.py
```

Open http://localhost:8080/ in your browser.

## Test

```bash
pytest -v
```

