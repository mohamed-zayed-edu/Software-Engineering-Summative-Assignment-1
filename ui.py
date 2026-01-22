"""UI components for dashboard pages."""
from typing import Any
from dash import html, dcc
import plotly.graph_objects as go
from api import get_metadata
from config import DATASETS
from utils import get_dataset_title, build_dropdown_options


def build_header() -> html.Div:
    """Build the header with title.

    Returns:
        html.Div: Header component with dark blue background and title.
    """
    return html.Div(
        [
            html.H1(
                "Education Data Insights Dashboard",
                style={
                    "color": "white",
                    "margin": 0,
                    "fontSize": "32px",
                    "fontWeight": "400",
                    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                    "letterSpacing": "0.5px",
                },
            ),
        ],
        style={
            "backgroundColor": "#001d3d",
            "padding": "1rem 2rem",
            "marginBottom": "0",
            "textAlign": "center",
        },
    )


def build_navigation(active_path: str = "/") -> html.Div:
    """Build navigation bar with links to all pages.

    Args:
        active_path: The current path (e.g., "/", "/attendance") used to highlight the active tab.

    Returns:
        html.Div: Navigation bar with tabs for Homepage and datasets.
    """

    normalised_path = active_path or "/"

    def make_link(label: str, href: str) -> dcc.Link:
        is_active = href == normalised_path
        link_style = {
            "padding": "1rem 2rem",
            "color": "white",
            "textDecoration": "none",
            "fontSize": "16px",
            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
            "display": "inline-block",
            "backgroundColor": "#6c757d",
            "border": "1px solid #6c757d",
        }
        if is_active:
            link_style.update(
                {
                    "backgroundColor": "#4e555b",
                    "fontWeight": "600",
                    "borderBottom": "3px solid #001d3d",
                }
            )
        return dcc.Link(label, href=href, style=link_style)

    nav_items = [make_link("Homepage", "/")]
    for key in DATASETS.keys():
        nav_items.append(make_link(get_dataset_title(key), f"/{key}"))

    return html.Div(
        nav_items,
        style={
            "backgroundColor": "#6c757d",
            "display": "flex",
            "justifyContent": "center",
            "gap": "0.5rem",
            "marginBottom": "0",
        },
    )


def build_home_page() -> html.Div:
    """Build the homepage layout with welcome message and dataset links.
    Returns:
        html.Div: Homepage layout component.
    """
    return html.Div(
        [
            build_header(),
            # Welcome section
            html.Div(
                [
                    html.H2(
                        "Welcome to Education Data Insights",
                        style={
                            "color": "#333",
                            "marginBottom": "1rem",
                            "marginTop": "0",
                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                            "fontSize": "24px",
                            "fontWeight": "500",
                        },
                    ),
                    html.P(
                        [
                            "Explore comprehensive education statistics from the"
                            " Department for Education's ",
                            html.A(
                                "Explore Education Statistics (EES)",
                                href="https://explore-education-statistics.service.gov.uk/",
                                target="_blank",
                                style={
                                    "color": "#0b7285",
                                    "textDecoration": "none",
                                    "fontWeight": "500",
                                },
                            ),
                            " platform (",
                            html.A(
                                "API docs",
                                href="https://api.education.gov.uk/statistics/docs/",
                                target="_blank",
                                style={
                                    "color": "#0b7285",
                                    "textDecoration": "none",
                                    "fontWeight": "500",
                                },
                            ),
                            "). Analyse attendance, school performance, and apprenticeship trends"
                            " through interactive visualisations.",
                        ],
                        style={
                            "fontSize": "17px",
                            "color": "#555",
                            "lineHeight": "1.6",
                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                            "marginBottom": "1rem",
                        },
                    ),
                    html.P(
                        "Select an option from below to get started:",
                        style={
                            "fontSize": "17px",
                            "color": "#333",
                            "marginBottom": "1.5rem",
                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                        },
                    ),
                ],
                style={
                    "backgroundColor": "#e8e8e8",
                    "padding": "2rem",
                    "marginBottom": "2rem",
                },
            ),
            # Dataset selection buttons
            html.Div(
                [
                    dcc.Link(
                        html.Button(
                            get_dataset_title(key),
                            style={
                                "padding": "1rem 2rem",
                                "margin": "0.5rem",
                                "backgroundColor": "#888",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "4px",
                                "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                "fontWeight": "500",
                                "cursor": "pointer",
                                "transition": "background-color 0.2s",
                                "fontSize": "18px",
                                "minWidth": "150px",
                            },
                        ),
                        href=f"/{key}",
                        style={"textDecoration": "none"},
                    )
                    for key in DATASETS.keys()
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "justifyContent": "center",
                    "gap": "1rem",
                    "marginBottom": "3rem",
                },
            ),
        ],
        style={"minHeight": "100vh", "backgroundColor": "#f5f5f5"},
    )


def build_placeholder_figure(
    message: str = "Select options and click Update Graph to generate the chart.",
) -> go.Figure:
    """Create a placeholder figure with a centered instructional message.
    Args:
        message: Instructional message to display in the figure.
    Returns:
        Plotly Figure with the message centered."""
    fig = go.Figure()
    fig.update_layout(
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 14},
            }
        ],
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
    )
    return fig


def build_dataset_page(dataset_key: str, active_path: str = "") -> html.Div:
    """Build the interactive UI for a specific dataset.

    Constructs the page layout with:
    - Indicator selector (required dropdown)
    - Time period multi-select (defaults to all available periods)
    - Filter dimension selector (required dropdown)
    - Filter values multi-select (populated from metadata for chosen dimension)
    - Update Graph button (triggers callback with prevent_initial_call=True)
    - Graph placeholder and error message display

    Args:
        dataset_key: Short key for the dataset.

    Returns:
        html.Div: Dash html.Div containing the complete dataset page layout.

    Raises:
        Returns error message div if metadata cannot be fetched.
    """
    if dataset_key not in DATASETS:
        return html.Div("Dataset not found", style={"color": "red"})

    dataset_id = DATASETS[dataset_key]
    dataset_title = get_dataset_title(dataset_key)

    try:
        meta = get_metadata(dataset_id)
        indicators = meta.get("indicators", [])
        time_periods = meta.get("timePeriods", [])
        filters = meta.get("filters", [])

        indicator_dicts: list[dict[str, Any]] = (
            build_dropdown_options(indicators) if indicators else []
        )
        indicator_options: list[dict[str, Any]] = indicator_dicts
        time_period_dicts: list[dict[str, Any]] = (
            build_dropdown_options(time_periods, label_key="period", id_key="period")
            if time_periods
            else []
        )
        time_period_options: list[dict[str, Any]] = time_period_dicts

        # Build options for a single filter selector
        filter_dimension_options: list[dict[str, Any]] = []
        for filter_item in filters:
            filter_id = filter_item.get("id") or filter_item.get("key")
            filter_name = (
                filter_item.get("name")
                or filter_item.get("label")
                or filter_id
                or "Unknown Filter"
            )
            if filter_id and filter_name:
                filter_dimension_options.append(
                    {"label": filter_name, "value": filter_id}
                )
    except Exception as e:
        print(f"Error loading dataset page for {dataset_key}: {e}")
        import traceback

        traceback.print_exc()
        meta = {}
        indicator_options = []
        time_period_options = []
        filter_dimension_options = []

    return html.Div(
        [
            build_header(),
            build_navigation(active_path or f"/{dataset_key}"),
            # Store metadata client-side to avoid re-fetching in callbacks
            dcc.Store(
                id={"type": "metadata-store", "index": dataset_key},
                data=meta,
            ),
            html.Div(
                [
                    # Dataset title
                    html.H2(
                        dataset_title,
                        style={
                            "textAlign": "center",
                            "color": "#333",
                            "fontSize": "28px",
                            "fontWeight": "500",
                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                            "marginTop": "2rem",
                            "marginBottom": "1.5rem",
                        },
                    ),
                    # Controls section
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "Select indicator:",
                                        style={
                                            "fontSize": "16px",
                                            "fontWeight": "500",
                                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                            "marginBottom": "0.5rem",
                                            "display": "block",
                                        },
                                    ),
                                    # Indicator selector
                                    dcc.Dropdown(
                                        id={
                                            "type": "indicator-dropdown",
                                            "index": dataset_key,
                                        },
                                        options=indicator_options,
                                        value=(
                                            indicator_options[0]["value"]
                                            if indicator_options
                                            else None
                                        ),
                                        clearable=False,
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Select time periods (at least one):",
                                        style={
                                            "fontSize": "16px",
                                            "fontWeight": "500",
                                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                            "marginBottom": "0.5rem",
                                            "display": "block",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id={
                                            "type": "time-dropdown",
                                            "index": dataset_key,
                                        },
                                        options=time_period_options,
                                        value=(
                                            [opt["value"] for opt in time_period_options]
                                            if time_period_options
                                            else []
                                        ),
                                        multi=True,
                                    ),
                                    html.Button(
                                        "Select All",
                                        id={
                                            "type": "time-select-all",
                                            "index": dataset_key,
                                        },
                                        n_clicks=0,
                                        style={
                                            "marginTop": "0.5rem",
                                            "padding": "0.5rem 1rem",
                                            "backgroundColor": "#888",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "4px",
                                            "fontSize": "14px",
                                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                            "cursor": "pointer",
                                        },
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            # Single filter selector (required)
                            html.Div(
                                [
                                    html.Label(
                                        "Select filter dimension:",
                                        style={
                                            "fontSize": "16px",
                                            "fontWeight": "500",
                                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                            "marginBottom": "0.5rem",
                                            "display": "block",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id={
                                            "type": "filter-dimension",
                                            "index": dataset_key,
                                        },
                                        options=filter_dimension_options or [],
                                        value=(
                                            filter_dimension_options[0]["value"] if len(filter_dimension_options) > 0 else None
                                        ),
                                        clearable=False,
                                        placeholder="Choose one filter dimension",
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Select values (for chosen dimension):",
                                        style={
                                            "fontSize": "16px",
                                            "fontWeight": "500",
                                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                            "marginBottom": "0.5rem",
                                            "display": "block",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id={
                                            "type": "filter-values",
                                            "index": dataset_key,
                                        },
                                        options=[],
                                        value=[],
                                        multi=True,
                                        placeholder="Select values...",
                                    ),
                                    html.Button(
                                        "Select All",
                                        id={
                                            "type": "filter-values-select-all",
                                            "index": dataset_key,
                                        },
                                        n_clicks=0,
                                        style={
                                            "marginTop": "0.5rem",
                                            "padding": "0.5rem 1rem",
                                            "backgroundColor": "#888",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "4px",
                                            "fontSize": "14px",
                                            "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                            "cursor": "pointer",
                                        },
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Button(
                                "Update Graph",
                                id={"type": "update-button", "index": dataset_key},
                                n_clicks=0,
                                style={
                                    "padding": "0.75rem 2rem",
                                    "backgroundColor": "#007bff",
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "4px",
                                    "fontSize": "16px",
                                    "fontWeight": "500",
                                    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                                    "cursor": "pointer",
                                    "marginTop": "1rem",
                                },
                            ),
                            html.Div(
                                id={"type": "metadata-error", "index": dataset_key},
                                style={"color": "red", "marginBottom": "0.5rem"},
                            ),
                        ],
                        style={"marginBottom": "1rem"},
                    ),
                ],
                style={"marginBottom": "2rem"},
            ),
            dcc.Graph(
                id={"type": "graph", "index": dataset_key},
                figure=build_placeholder_figure(),
            ),
            html.Div(
                id={"type": "error-message", "index": dataset_key},
                style={"color": "red"},
            ),
        ],
        style={
            "maxWidth": "900px",
            "margin": "auto",
            "padding": "0 2rem 2rem 2rem",
            "backgroundColor": "#f5f5f5",
            "minHeight": "100vh",
        },
    )
