import dash
from dash import dcc, html, Input, Output, callback, State
from ui import build_home_page, build_dataset_page, build_nav_bar
from config import DATASETS


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
        ],
    )

    return app


app = init_app()


@app.callback(
    Output({"type": "filter-values", "index": dash.ALL}, "options"),
    Input({"type": "filter-dimension", "index": dash.ALL}, "value"),
    State({"type": "metadata-store", "index": dash.ALL}, "data"),
)
def update_filter_values(selected_filter_dimensions, metas):
    if not isinstance(selected_filter_dimensions, list):
        selected_filter_dimensions = [selected_filter_dimensions]
    if not isinstance(metas, list):
        metas = [metas]

    results = []
    for selected_filter_dimension, meta in zip(selected_filter_dimensions, metas):
        if not selected_filter_dimension or not meta:
            results.append([])
            continue

        filters = meta.get("filters", [])
        found = False
        for f in filters:
            if f.get("id") == selected_filter_dimension:
                results.append(
                    [
                        {"label": opt.get("label"), "value": opt.get("id")}
                        for opt in f.get("options", [])
                    ]
                )
                found = True
                break

        if not found:
            results.append([])

    return results


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def display_page(pathname: str):
    dataset_key = pathname.strip("/") if pathname else ""

    if dataset_key in DATASETS:
        return html.Div(
            [
                build_nav_bar(),
                build_dataset_page(dataset_key),
            ]
        )
    else:
        return build_home_page()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
