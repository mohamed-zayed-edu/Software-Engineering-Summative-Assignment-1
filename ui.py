from dash import html, dcc
import plotly.graph_objects as go
from api import get_metadata
from config import DATASETS
from utils import get_dataset_title, build_dropdown_options

def build_home_page() -> html.Div:
    """Build the home page with dataset selection cards.

    Returns:
        Dash html.Div containing the home page layout.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(
                                "Welcome to Education Data Insights",
                                style={"color": "#333", "marginBottom": "1rem"},
                            ),
                            html.P(
                                "Explore comprehensive education statistics from the Department for Education's"
                                " Explore Education Statistics (EES) platform (https://explore-education-statistics.service.gov.uk/)"
                                " through their API (https://api.education.gov.uk/statistics/docs/)."
                                " Analyse trends through interactive visualisations.",
                                style={
                                    "fontSize": "16px",
                                    "color": "#555",
                                    "lineHeight": "1.6",
                                    "marginBottom": "1.5rem",
                                },
                            ),
                        ],
                        style={
                            "backgroundColor": "#f8f9fa",
                            "padding": "2rem",
                            "borderRadius": "8px",
                            "marginBottom": "2rem",
                            "border": "1px solid #e0e0e0",
                        },
                    ),
                ],
                style={"maxWidth": "800px", "margin": "auto", "marginTop": "0.5rem"},
            ),
        ],
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


def build_dataset_page(dataset_key: str) -> html.Div:
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

        indicator_options = build_dropdown_options(indicators) if indicators else []
        time_period_options = (
            build_dropdown_options(time_periods, label_key="period", id_key="period")
            if time_periods
            else []
        )

        # Build options for a single filter selector
        filter_dimension_options = []
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
            # Store metadata client-side to avoid re-fetching in callbacks
            dcc.Store(
                id={"type": "metadata-store", "index": dataset_key},
                data=meta,
            ),
            html.Div(
                [
                    html.H2(dataset_title, style={"textAlign": "center"}),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Select indicator:"),
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
                                    html.Label("Select time periods (at least one):"),
                                    dcc.Dropdown(
                                        id={
                                            "type": "time-dropdown",
                                            "index": dataset_key,
                                        },
                                        options=time_period_options,
                                        value=(
                                            [
                                                opt["value"]
                                                for opt in time_period_options
                                            ]
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
                                        style={"marginTop": "0.25rem"},
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            # Single filter selector (required)
                            html.Div(
                                [
                                    html.Label("Select filter dimension:"),
                                    dcc.Dropdown(
                                        id={
                                            "type": "filter-dimension",
                                            "index": dataset_key,
                                        },
                                        options=filter_dimension_options,
                                        value=(
                                            filter_dimension_options[0]["value"]
                                            if filter_dimension_options
                                            else None
                                        ),
                                        clearable=False,
                                        placeholder="Choose one filter dimension",
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Div(
                                [
                                    html.Label("Select values (for chosen dimension):"),
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
                                        style={"marginTop": "0.25rem"},
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Button(
                                "Update Graph",
                                id={"type": "update-button", "index": dataset_key},
                                n_clicks=0,
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
        style={"maxWidth": "800px", "margin": "auto"},
    )
