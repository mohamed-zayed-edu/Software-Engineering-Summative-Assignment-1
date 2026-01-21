import plotly.graph_objects as go
from dash import dcc, html

from ui import build_home_page, build_placeholder_figure, build_dataset_page


def find_component_by_type(component, target_type):
    if isinstance(component, target_type):
        return component
    if hasattr(component, "children"):
        if isinstance(component.children, list):
            for child in component.children:
                found = find_component_by_type(child, target_type)
                if found:
                    return found
        else:
            return find_component_by_type(component.children, target_type)
    return None


def find_component_by_id(component, target_id):
    if hasattr(component, "id") and isinstance(component.id, dict):
        if component.id == target_id:
            return component
    if hasattr(component, "children"):
        if isinstance(component.children, list):
            for child in component.children:
                found = find_component_by_id(child, target_id)
                if found:
                    return found
        else:
            return find_component_by_id(component.children, target_id)
    return None


class TestBuildHomePage:
    """Tests for build_home_page function."""

    def test_build_home_page_returns_div(self):
        """Test that build_home_page returns a Div component."""
        result = build_home_page()
        assert isinstance(result, html.Div)


class TestBuildPlaceholderFigure:
    """Tests for build_placeholder_figure function."""

    def test_build_placeholder_figure_returns_figure(self):
        """Test that function returns a Plotly Figure."""
        result = build_placeholder_figure()
        assert isinstance(result, go.Figure)


class TestBuildDatasetPage:
    """Tests for build_dataset_page function."""

    def test_build_dataset_page_returns_div(self):
        """Test that function returns a Div component."""
        result = build_dataset_page("ks2-performance")
        assert isinstance(result, html.Div)

    def test_build_dataset_page_invalid_key(self):
        """Test handling of invalid dataset key."""
        result = build_dataset_page("invalid-dataset")
        assert isinstance(result, html.Div)
        assert "Dataset not found" in str(result.children)

    def test_build_dataset_page_contains_indicator_dropdown(self):
        """Test that page includes indicator dropdown."""
        page = build_dataset_page("ks2-performance")
        dropdown = find_component_by_id(
            page, {"type": "indicator-dropdown", "index": "ks2-performance"}
        )
        assert dropdown is not None
        assert isinstance(dropdown, dcc.Dropdown)

    def test_build_dataset_page_contains_time_dropdown(self):
        """Test that page includes time period dropdown."""
        page = build_dataset_page("ks2-performance")
        dropdown = find_component_by_id(
            page, {"type": "time-dropdown", "index": "ks2-performance"}
        )
        assert dropdown is not None
        assert isinstance(dropdown, dcc.Dropdown)

    def test_build_dataset_page_contains_filter_dimension_dropdown(self):
        """Test that page includes filter dimension dropdown."""
        page = build_dataset_page("ks2-performance")
        dropdown = find_component_by_id(
            page, {"type": "filter-dimension", "index": "ks2-performance"}
        )
        assert dropdown is not None
        assert isinstance(dropdown, dcc.Dropdown)

    def test_build_dataset_page_contains_filter_values_dropdown(self):
        """Test that page includes filter values dropdown."""
        page = build_dataset_page("ks2-performance")
        dropdown = find_component_by_id(
            page, {"type": "filter-values", "index": "ks2-performance"}
        )
        assert dropdown is not None
        assert isinstance(dropdown, dcc.Dropdown)

    def test_build_dataset_page_contains_graph(self):
        """Test that page includes graph component."""
        page = build_dataset_page("ks2-performance")
        graph = find_component_by_id(
            page, {"type": "graph", "index": "ks2-performance"}
        )
        assert graph is not None
        assert isinstance(graph, dcc.Graph)
        assert isinstance(graph.figure, go.Figure)

    def test_build_dataset_page_contains_update_button(self):
        """Test that page includes update button."""
        page = build_dataset_page("ks2-performance")
        button = find_component_by_id(
            page, {"type": "update-button", "index": "ks2-performance"}
        )
        assert button is not None
        assert isinstance(button, html.Button)
