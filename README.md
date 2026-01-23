# Education Data Insights Explorer

A dashboard for exploring education statistics from the Department for Education (DfE).

## Proposal

The Department for Education collects and shares a large amount of data on various branches it oversees including schools, colleges and higher education. Much of this data is publicly available on many platforms, including the Explore Education Statistics (EES) platform. The data available on EES is comprehensive with many breakdowns available including by year, geographic level (national, regional, local authority), disadvantage status, and many more. This data is however only available in tabular format. Although, the recent development of the EES API which allows datasets to be accessed programatically provides an opportunity to build tools that can visualise this data. This dashboard provides a proof of concept for how an interactive tool can be developed that makes the most of this large bank of data, providing simple visualisations that are customisable and allow users to explore the data more easily.

## Design and Prototyping

The design and prototyping was carried out using Figma and can be found [here](https://www.figma.com/proto/t339ZomN0RNiL4HRKKpYy7/Summative-1?node-id=28-289&t=2scAk19vIt2rYRdR-1). The design was kept simple as to be intuitive for users. The homepage provides a welcome message as well as links to the EES platform and API documentation. From the homepage, users are able to navigate to pages dedicated to individual datasets using buttons that are clearly labeled. The dataset pages were also kept simple with clear instructions on what each component is, and how to generate the visualisation. For accessibility purposes, text size is relatively large with the font being simple, and colours are kept simple.

## Project Planning

The project was carried out in an agile manner, using a [Kanban board](https://github.com/users/mohamed-zayed-edu/projects/2) on Github Projects for ticketing. The board is split into 5 sections, backklog where all future tasks are kept, ready where a ticket is ready to be actioned, in progress where a ticket is being actively worked on, review where the ticket implementation is being reviewed, and finally done when a ticket is closed. Tickets were labeled either as enhancements, bugs or documentation. Although sprints are customarily two weeks, they were kept to only one week due to the time constraints and the scope of the project. 

## MVP Development

Sprint 1 involved the project set up and research phase, as well creating some basic functions to interact with the API. Sprint 2 then focussed on starting to build the dashboard UI, specifically the homepage, as well as writing tests and setting up CI/CD via Github actions, the yaml file for which can be found [here](.github/workflows/ci.yml). Sprint 3 included building out the dashboard by creating dataset pages and adding navigation. Sprint 4 was when filter controls and visualisations were added. And finally, sprint 5 is when documentation was improved by adding docstrings.

## Documentation

### User documentation

#### Prerequisites
- Python 3.10+ installed
- Dependencies from `requirements.txt` installed with `pip install -r requirements.txt`

#### Run the app
1) In a terminal, from the project root run `python app.py`.
2) Open http://localhost:8080/ in your browser.

#### Navigate the dashboard
- Home: Read the overview and follow dataset buttons to open a dataset page.
- Dataset pages: Use the controls on the left to pick indicator, time periods, and optional filters and click update graph for the time series chart to update after selections.

#### Typical workflow
1) Choose a dataset from the home page.
2) Pick an indicator to plot.
3) Select one or more time periods (or click Select All).
4) Choose a filter dimension, then pick filter values to break down the series.
5) View the chart and note any warning text below it for excluded non-numeric periods.

#### Troubleshooting
- Blank chart: Ensure at least one time period is selected and the indicator has numeric data.
- API/network errors: Restart the app and retry; the app prints errors to the terminal for inspection.

### Technical documentation

#### Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

#### Run

Start the Dash server:
```bash
python app.py
```

Open http://localhost:8080/ in your browser.

#### Test

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

#### Structure

- `api.py`: Core API client.
- `app.py`: Dash app entry; renders home page and dataset pages.
- `ui.py`: UI components.
- `utils.py`: Helper utilities.
- `test_api.py`: Pytest suite covering API helper functions and query logic with mocks.


#### API

- Location: [api.py](api.py)
- Helpers: `get_json(endpoint, params=None)` and `post_query(endpoint, payload)` wrap the EES API with common headers, 30s timeout, and `raise_for_status()` to raise HTTP errors.
- Metadata: `get_metadata(dataset_id)` fetches dataset metadata. Uses @lru_cache(maxsize=10) for fast repeated lookups enabling addition of more datasets without affecting code.
- Query pipeline: `query_dataset(dataset_id, indicator_id, geo_level_codes, period_list, filters=None)` builds criteria, resolves time period codes from metadata, paginates through all result pages, flattens responses to a DataFrame, and converts academic year periods to datetimes. Results cached (max 50 queries) with hash-based key using tuples and automatic FIFO eviction.
- Cache implementation: Uses `OrderedDict` for clean FIFO eviction with `popitem(last=False)`. Helper `make_hashable()` recursively converts nested dicts/lists to tuples for cache keys.
- Client-side filtering: `filters` uses simple `in` or `eq` semantics; filter IDs are extracted from API labels so you can pass raw IDs.
- Non-numeric values: indicator values that cannot coerce to float are kept as strings (e.g., "suppressed"), so downstream code should handle both numeric and string types.
- Error handling: raises `ValueError` when API warns of `NoResults`, HTTP errors propagate from `requests` exceptions.

#### UI

- Location: [ui.py](ui.py)
- `build_home_page()`: Landing content with welcome and overview text.
- `build_placeholder_figure(message=...)`: Creates a centered instructional figure used as the default graph placeholder.
- `build_dataset_page(dataset_key)`: Dataset exploration layout with indicator dropdown, time-period multi-select, filter dimension and values selectors, graph, and error displays. Fetches metadata once at page load and stores it client-side (`dcc.Store`) for callback reuse.
- Pattern-matching IDs: All components use `{"type": "component-name", "index": dataset_key}` format for dynamic callback targeting.

#### Utils

`extract_label(value)`: Extracts label from `"id :: label"` format filter values (returns the label part).
`prepare_chart_data(df, indicator_id, selected_dim)`: Processes dataframe for plotting by converting to numeric, grouping by time period and filter value, filtering non-numeric data, and generating warnings for excluded periods.

#### App Callbacks

`update_filter_values`: Updates filter value dropdown options based on selected filter dimension. Uses stored metadata from `dcc.Store` to avoid redundant API calls. Handles multiple dataset pages via ALL pattern-matching.
`update_graph`: Main visualisation callback. Validates inputs, queries dataset, processes data using `prepare_chart_data()` helper, and renders Plotly line charts. Uses stored metadata to avoid re-fetching. Returns figures and error messages for each dataset page.
`display_page`: Routes URL pathname to appropriate dataset page or home page.

#### Optimisations:
- **Server-side caching**: 
  - `get_metadata()` uses LRU cache (maxsize=10) for instant repeated lookups
  - `query_dataset()` caches up to 50 query results with tuple-based keys for O(1) lookup speed
  - Automatic FIFO eviction using OrderedDict to prevent unbounded memory growth
- **Client-side caching**: Metadata stored in `dcc.Store` components (fetched once per dataset page load)
- **Callback optimisation**: All callbacks use stored metadata via State parameters instead of re-fetching

## Evaluation

### What went well
- Overall clean API integration: predictable schemas allowed for shared helpers that kept the data layer simple.
- Modular UI design: reusable header/nav/builders made it easy to add datasets without duplicating code.
- Reliable tests & CI/CD: pytest plus GitHub Actions caught issues early preventing breaks to main.

### Challenges
- API filtering: initial plan to apply filtering server-side was changed due to issues in API functionality.
- Handling API pagination and caching: needed tuple-based cache keys and FIFO eviction to balance speed and memory - important since datasets were large.
- Testing UI callbacks: Dash pattern-matching IDs required careful fixtures and state setup to validate callbacks reliably.

### Lessons learned
- TDD improves confidence in code: starting with API/query tests clarified edge cases and guided implementation.
- CI/CD enforces consistent quality: automated formatting and tests reduced manual checks and can speed up review.

### Future work
- Add export options sych as CSV so users can take underlying data offline.
- Enhance filtering with multi-select across dimensions and clearer default choices per dataset.
- Deploy to a cloud host to make dashboard more accessible and reduce compuational load on user device.