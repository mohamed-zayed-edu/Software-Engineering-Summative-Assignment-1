import dash
from dash import dcc, html, Input, Output, callback, State
from ui import build_home_page, build_dataset_page


def init_app() -> dash.Dash:
    """Initialise the Dash app and build the layout.

    Returns:
        A Dash app instance ready to run.
    """
    app = dash.Dash("Education Data Insights Explorer")
    app.title = "Education Data Insights Explorer"

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.H1(
                "Education Data Insights Explorer",
                style={"textAlign": "center"},
            ),
            html.Div(id="page-content"),
            build_dataset_page("ks2-performance"),
        ],
    )

    return app


app = init_app()


@app.callback(
    Output({"type": "filter-values", "index": "ks2-performance"}, "options"),
    Input({"type": "filter-dimension", "index": "ks2-performance"}, "value"),
    State({"type": "metadata-store", "index": "ks2-performance"}, "data"),
)
def update_filter_values(selected_filter_dimension, meta):
    if not selected_filter_dimension or not meta:
        return []

    filters = meta.get("filters", [])
    for f in filters:
        if f.get("id") == selected_filter_dimension:
            return [
                {"label": opt.get("label"), "value": opt.get("id")}
                for opt in f.get("options", [])
            ]

    return []


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
