# Education Data Insights Explorer

A dashboard for exploring education statistics from the Department for Education.

## Structure

- `api.py`: Core API client.
- `app.py`: Dash app entry; renders home page and dataset pages.
- `ui.py`: UI components.
- `utils.py`: Helper utilities.
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

### UI

- Location: [ui.py](ui.py)
- `build_home_page()`: Landing content with welcome and overview text.
- `build_placeholder_figure(message=...)`: Creates a centered instructional figure used as the default graph placeholder.
- `build_dataset_page(dataset_key)`: Dataset exploration layout with indicator dropdown, time-period multi-select, filter dimension and values selectors, graph, and error displays. Fetches metadata once at page load and stores it client-side (`dcc.Store`) for callback reuse.
- Pattern-matching IDs: All components use `{"type": "component-name", "index": dataset_key}` format for dynamic callback targeting.

### Utils

- Location: [utils.py](utils.py)
- `extract_filter_id(value)`: Extracts ID from `"id :: label"` format filter values.
- `period_to_datetime(period_str)`: Converts academic year strings like `"2024/2025"` to pandas Timestamp (September 1st).
- `get_dataset_title(dataset_key)`: Maps dataset keys to human-readable titles from config.
- `build_dropdown_options(values, label_key, id_key)`: Transforms metadata lists into Dash dropdown option format.


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

Run all tests:
```bash
pytest -v
```

Automated pipeline runs on push/PR to `main` or `develop` branches:

**Test Job:**
- Matrix testing across Python 3.10, 3.11, 3.12
- Pytest

**Lint Job:**
- Black code formatting checks

View workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)

