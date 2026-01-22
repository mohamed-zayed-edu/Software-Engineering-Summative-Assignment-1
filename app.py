"""Dash app initialisation and callbacks for the education dashboard."""
import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH
import plotly.express as px
from ui import (
    build_home_page,
    build_dataset_page,
    build_placeholder_figure,
)
from config import DATASETS
from api import query_dataset
from utils import prepare_chart_data


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
            html.Div(id="page-content"),
        ],
    )

    return app


app = init_app()


@app.callback(
    Output({"type": "filter-values", "index": ALL}, "options"),
    Input({"type": "filter-dimension", "index": ALL}, "value"),
    State({"type": "metadata-store", "index": ALL}, "data"),
)
def update_filter_values(selected_dims, metas):
    """Update filter value options based on selected filter dimension.

    Handles multiple dataset pages via ALL pattern-matching IDs.
    """
    if not selected_dims or not metas:
        return [[]] * len(selected_dims) if selected_dims else []

    results = []
    for selected_dim, meta in zip(selected_dims, metas):
        if not selected_dim or not meta:
            results.append([])
            continue

        filters = meta.get("filters", [])
        options = []
        for f in filters:
            if f.get("id") == selected_dim:
                options = [
                    {"label": opt.get("label"), "value": opt.get("id")}
                    for opt in f.get("options", [])
                ]
                break
        results.append(options)

    return results


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def display_page(pathname: str):
    dataset_key = pathname.strip("/") if pathname else ""

    if dataset_key in DATASETS:
        return build_dataset_page(dataset_key)
    else:
        return build_home_page()


@app.callback(
    [
        Output({"type": "graph", "index": ALL}, "figure"),
        Output({"type": "error-message", "index": ALL}, "children"),
    ],
    [Input({"type": "update-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "indicator-dropdown", "index": ALL}, "value"),
        State({"type": "time-dropdown", "index": ALL}, "value"),
        State({"type": "filter-dimension", "index": ALL}, "value"),
        State({"type": "filter-values", "index": ALL}, "value"),
        State({"type": "update-button", "index": ALL}, "id"),
        State({"type": "metadata-store", "index": ALL}, "data"),
    ],
    prevent_initial_call=True,
)
def update_graph(
    _,
    indicator_ids: list,
    periods_list: list,
    selected_dims: list,
    selected_values_list: list,
    button_ids: list,
    metas: list,
):
    figures = []
    errors = []

    # only process components on current page
    for i, button_id in enumerate(button_ids):
        dataset_key = button_id["index"]

        if i < len(indicator_ids) and i < len(periods_list):
            indicator_id = indicator_ids[i]
            periods = periods_list[i]
            filters_dict = {}
            selected_dim = selected_dims[i] if i < len(selected_dims) else None
            selected_vals = (
                selected_values_list[i] if i < len(selected_values_list) else []
            )
            if selected_dim and selected_vals:
                filters_dict[selected_dim] = {
                    "in": (
                        selected_vals
                        if isinstance(selected_vals, list)
                        else [selected_vals]
                    )
                }

            if not indicator_id or not periods:
                figures.append(
                    build_placeholder_figure(
                        "Select an indicator, choose time periods, then click Update Graph."
                    )
                )
                errors.append(
                    "Please select an indicator and at least one time period."
                )
            else:
                try:
                    # Validate required inputs
                    if not selected_dim or not selected_vals:
                        raise ValueError(
                            "Please select a filter dimension and at least one value."
                        )

                    # Get metadata and labels
                    dataset_id = DATASETS[dataset_key]
                    meta = metas[i]
                    indicator_label = next(
                        (
                            ind["label"]
                            for ind in meta.get("indicators", [])
                            if ind["id"] == indicator_id
                        ),
                        indicator_id,
                    )
                    selected_dim_label = next(
                        (
                            f["label"]
                            for f in meta.get("filters", [])
                            if f["id"] == selected_dim
                        ),
                        selected_dim,
                    )

                    # Query dataset
                    df = query_dataset(
                        dataset_id, indicator_id, ["NAT"], periods, filters=filters_dict
                    )
                    if df.empty:
                        raise ValueError("No data found for this combination.")

                    # Process data for plotting
                    df_numeric, warning_message = prepare_chart_data(
                        df, indicator_id, selected_dim
                    )

                    # Create line chart
                    fig = px.line(
                        df_numeric,
                        x="time_period",
                        y=indicator_id,
                        color="filter_value_label",
                        markers=True,
                        labels={
                            "time_period": "Time Period",
                            indicator_id: indicator_label,
                            "filter_value_label": "Filter value",
                        },
                        title=f"{indicator_label} by {selected_dim_label}",
                    )
                    figures.append(fig)
                    errors.append(warning_message)
                except Exception as exc:
                    figures.append(px.scatter())
                    errors.append(f"Error: {exc}")
        else:
            figures.append(px.scatter())
            errors.append("")

    return figures, errors


# Select All button callbacks
@app.callback(
    Output({"type": "time-dropdown", "index": MATCH}, "value"),
    Input({"type": "time-select-all", "index": MATCH}, "n_clicks"),
    State({"type": "time-dropdown", "index": MATCH}, "options"),
    prevent_initial_call=True,
)
def select_all_time_periods(n_clicks, options):
    if not n_clicks or not options:
        raise dash.exceptions.PreventUpdate
    return [opt["value"] for opt in options]


@app.callback(
    Output({"type": "filter-values", "index": MATCH}, "value"),
    Input({"type": "filter-values-select-all", "index": MATCH}, "n_clicks"),
    State({"type": "filter-values", "index": MATCH}, "options"),
    prevent_initial_call=True,
)
def select_all_filter_values(n_clicks, options):
    if not n_clicks or not options:
        raise dash.exceptions.PreventUpdate
    return [opt["value"] for opt in options]


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
