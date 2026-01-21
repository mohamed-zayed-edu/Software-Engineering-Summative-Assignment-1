from dash import html, dcc
import plotly.graph_objects as go


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


def build_dataset_page(page_id: str = "default") -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Dataset Explorer", style={"textAlign": "center"}),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Select indicator:"),
                                    dcc.Dropdown(
                                        id={
                                            "type": "indicator-dropdown",
                                            "index": page_id,
                                        },
                                        options=[1, 2, 3],
                                        value=None,
                                        clearable=False,
                                        placeholder="Choose an indicator...",
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
                                            "index": page_id,
                                        },
                                        options=[1, 2, 3],
                                        value=[],
                                        multi=True,
                                        placeholder="Choose time periods...",
                                    ),
                                    html.Button(
                                        "Select All",
                                        id={
                                            "type": "time-select-all",
                                            "index": page_id,
                                        },
                                        n_clicks=0,
                                        style={"marginTop": "0.25rem"},
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Div(
                                [
                                    html.Label("Select filter:"),
                                    dcc.Dropdown(
                                        id={
                                            "type": "filter-dimension",
                                            "index": page_id,
                                        },
                                        options=[1, 2, 3],
                                        value=None,
                                        clearable=False,
                                        placeholder="Choose a filter dimension...",
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Div(
                                [
                                    html.Label("Select values (for chosen filter):"),
                                    dcc.Dropdown(
                                        id={
                                            "type": "filter-values",
                                            "index": page_id,
                                        },
                                        options=[1, 2, 3],
                                        value=[],
                                        multi=True,
                                        placeholder="Select filter values...",
                                    ),
                                    html.Button(
                                        "Select All",
                                        id={
                                            "type": "filter-values-select-all",
                                            "index": page_id,
                                        },
                                        n_clicks=0,
                                        style={"marginTop": "0.25rem"},
                                    ),
                                ],
                                style={"marginBottom": "1rem"},
                            ),
                            html.Button(
                                "Update Graph",
                                id={"type": "update-button", "index": page_id},
                                n_clicks=0,
                            ),
                            html.Div(
                                id={"type": "metadata-error", "index": page_id},
                                style={"color": "red", "marginBottom": "0.5rem"},
                            ),
                        ],
                        style={"marginBottom": "1rem"},
                    ),
                ],
                style={"marginBottom": "2rem"},
            ),
            dcc.Graph(
                id={"type": "graph", "index": page_id},
                figure=build_placeholder_figure(),
            ),
            html.Div(
                id={"type": "error-message", "index": page_id},
                style={"color": "red"},
            ),
        ],
        style={"maxWidth": "800px", "margin": "auto"},
    )
