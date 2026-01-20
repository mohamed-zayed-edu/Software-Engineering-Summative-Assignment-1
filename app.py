import dash
from dash import dcc, html


def init_app() -> dash.Dash:
    """Initialise the Dash app and build the layout.

    Returns:
        A Dash app instance ready to run.
    """
    app = dash.Dash(__name__)
    app.title = "Education Data Insights Explorer"

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.H1(
                "Education Data Insights Explorer",
                style={"textAlign": "center"},
            ),
            html.Div(id="page-content"),
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

    return app


if __name__ == "__main__":
    app = init_app()
    app.run(debug=True, host="0.0.0.0", port=8080)
