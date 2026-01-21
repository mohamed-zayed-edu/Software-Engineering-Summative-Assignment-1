import dash
from dash import dcc, html
from ui import build_home_page, build_dataset_page


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
            build_home_page(),
            html.Hr(),
            html.H2("Dataset Page 1", style={"textAlign": "center"}),
            build_dataset_page(page_id="dataset-1"),
            html.Hr(),
            html.H2("Dataset Page 2", style={"textAlign": "center"}),
            build_dataset_page(page_id="dataset-2"),
        ],
    )

    return app


if __name__ == "__main__":
    app = init_app()
    app.run(debug=True, host="0.0.0.0", port=8080)
