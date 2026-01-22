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
- Metadata: `get_metadata(dataset_id)` fetches dataset metadata. **Uses @lru_cache(maxsize=10) for fast repeated lookups enabling addition of more datasets without affecting code.**
- Query pipeline: `query_dataset(dataset_id, indicator_id, geo_level_codes, period_list, filters=None)` builds criteria, resolves time period codes from metadata, paginates through all result pages, flattens responses to a DataFrame, and converts academic year periods to datetimes. **Results cached (max 50 queries) with hash-based key using tuples and automatic FIFO eviction.**
- Cache implementation: Uses `OrderedDict` for clean FIFO eviction with `popitem(last=False)`. Helper `make_hashable()` recursively converts nested dicts/lists to tuples for cache keys.
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

`extract_label(value)`: Extracts label from `"id :: label"` format filter values (returns the label part).
`prepare_chart_data(df, indicator_id, selected_dim)`: Processes dataframe for plotting by converting to numeric, grouping by time period and filter value, filtering non-numeric data, and generating warnings for excluded periods.

### App Callbacks

`update_filter_values`: Updates filter value dropdown options based on selected filter dimension. Uses stored metadata from `dcc.Store` to avoid redundant API calls. Handles multiple dataset pages via ALL pattern-matching.
`update_graph`: Main visualisation callback. Validates inputs, queries dataset, processes data using `prepare_chart_data()` helper, and renders Plotly line charts. Uses stored metadata to avoid re-fetching. Returns figures and error messages for each dataset page.
`display_page`: Routes URL pathname to appropriate dataset page or home page.

**Optimisations:**
- **Server-side caching**: 
  - `get_metadata()` uses LRU cache (maxsize=10) for instant repeated lookups
  - `query_dataset()` caches up to 50 query results with tuple-based keys for O(1) lookup speed
  - Automatic FIFO eviction using OrderedDict to prevent unbounded memory growth
- **Client-side caching**: Metadata stored in `dcc.Store` components (fetched once per dataset page load)
- **Callback optimisation**: All callbacks use stored metadata via State parameters instead of re-fetching
- **Code simplification**: 
  - Data processing logic extracted to testable `prepare_chart_data()` utility function

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

