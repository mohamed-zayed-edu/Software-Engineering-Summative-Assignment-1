import pandas as pd
import pytest

from utils import (
    extract_filter_id,
    period_to_datetime,
    get_dataset_title,
    build_dropdown_options,
    extract_label,
    prepare_chart_data,
)


class TestExtractFilterId:
    """Tests for extract_filter_id function."""

    def test_extract_filter_id_with_label(self):
        """Test extraction when value contains '::' separator."""
        assert extract_filter_id("ABC123 :: Male") == "ABC123"
        assert extract_filter_id("XYZ99 :: Female") == "XYZ99"

    def test_extract_filter_id_without_label(self):
        """Test extraction when value is just an ID."""
        assert extract_filter_id("ABC123") == "ABC123"
        assert extract_filter_id("simple_id") == "simple_id"

    def test_extract_filter_id_with_na(self):
        """Test handling of pandas NA values."""
        result = extract_filter_id(pd.NA)
        assert pd.isna(result)

    def test_extract_filter_id_with_none(self):
        """Test handling of None values."""
        result = extract_filter_id(None)
        assert result is None


class TestPeriodToDatetime:
    """Tests for period_to_datetime function."""

    def test_period_to_datetime_academic_year(self):
        """Test conversion of academic year format."""
        result = period_to_datetime("2024/2025")
        expected = pd.Timestamp(year=2024, month=9, day=1)
        assert result == expected

    def test_period_to_datetime_single_year(self):
        """Test conversion of single year format."""
        result = period_to_datetime("2024")
        expected = pd.Timestamp(year=2024, month=9, day=1)
        assert result == expected

    def test_period_to_datetime_invalid_format(self):
        """Test handling of invalid formats."""
        result = period_to_datetime("qwerty")
        assert pd.isna(result)

    def test_period_to_datetime_none(self):
        """Test handling of None input."""
        result = period_to_datetime(None)
        assert pd.isna(result)

    def test_period_to_datetime_empty_string(self):
        """Test handling of empty string."""
        result = period_to_datetime("")
        assert pd.isna(result)

    def test_period_to_datetime_with_whitespace(self):
        """Test handling of whitespace in year."""
        result = period_to_datetime("2023 / 2024")
        expected = pd.Timestamp(year=2023, month=9, day=1)
        assert result == expected


class TestGetDatasetTitle:
    """Tests for get_dataset_title function."""

    def test_get_dataset_title_known_key(self):
        """Test retrieval of known dataset titles."""
        result = get_dataset_title("ks2-performance")
        assert result == "KS2 Performance"

    def test_get_dataset_title_unknown_key(self):
        """Test fallback for unknown dataset key."""
        result = get_dataset_title("unknown-dataset")
        assert result == "unknown-dataset"


class TestBuildDropdownOptions:
    """Tests for build_dropdown_options function."""

    def test_build_dropdown_options_default_keys(self):
        """Test with default label and id keys."""
        values = [
            {"id": "1", "label": "Option One"},
            {"id": "2", "label": "Option Two"},
        ]
        result = build_dropdown_options(values)
        expected = [
            {"label": "Option One", "value": "1"},
            {"label": "Option Two", "value": "2"},
        ]
        assert result == expected

    def test_build_dropdown_options_custom_keys(self):
        """Test with custom label and id keys."""
        values = [
            {"code": "A", "name": "Alpha"},
            {"code": "B", "name": "Beta"},
        ]
        result = build_dropdown_options(values, label_key="name", id_key="code")
        expected = [
            {"label": "Alpha", "value": "A"},
            {"label": "Beta", "value": "B"},
        ]
        assert result == expected

    def test_build_dropdown_options_empty_list(self):
        """Test with empty input list."""
        result = build_dropdown_options([])
        assert result == []


class TestExtractLabel:
    """Tests for extract_label function."""

    def test_extract_label_with_separator(self):
        """Test extracting label from 'id :: label' format."""
        result = extract_label("ENG :: England")
        assert result == "England"

    def test_extract_label_without_separator(self):
        """Test with plain value without separator."""
        result = extract_label("England")
        assert result == "England"

    def test_extract_label_with_none(self):
        """Test with None value."""
        result = extract_label(None)
        assert pd.isna(result)

class TestPrepareChartData:
    """Tests for prepare_chart_data function."""

    def test_prepare_chart_data_basic(self):
        """Test basic data preparation with numeric values."""
        df = pd.DataFrame(
            {
                "time_period": pd.to_datetime(
                    ["2023-09-01", "2023-09-01", "2024-09-01"]
                ),
                "indicator_123": [10, 20, 30],
                "filter_ethnicity": ["ETH1 :: Asian", "ETH2 :: White", "ETH1 :: Asian"],
            }
        )

        result_df, warning = prepare_chart_data(df, "indicator_123", "ethnicity")

        assert "filter_value_label" in result_df.columns
        assert warning == ""
        assert len(result_df) == 3

    def test_prepare_chart_data_with_non_numeric(self):
        """Test with mixed numeric and non-numeric values."""
        df = pd.DataFrame(
            {
                "time_period": pd.to_datetime(["2023-09-01", "2024-09-01"]),
                "indicator_123": [10, "N/A"],
                "filter_ethnicity": ["ETH1 :: Asian", "ETH1 :: Asian"],
            }
        )

        result_df, warning = prepare_chart_data(df, "indicator_123", "ethnicity")

        assert len(result_df) == 1
        assert "2024" in warning  # Warning mentions excluded year

    def test_prepare_chart_data_missing_filter_dimension(self):
        """Test with missing filter dimension column."""
        df = pd.DataFrame(
            {
                "time_period": pd.to_datetime(["2023-09-01"]),
                "indicator_123": [10],
                "filter_wrong": ["value"],
            }
        )

        with pytest.raises(ValueError, match="Selected filter dimension not found"):
            prepare_chart_data(df, "indicator_123", "ethnicity")

    def test_prepare_chart_data_all_non_numeric(self):
        """Test with all non-numeric values."""
        df = pd.DataFrame(
            {
                "time_period": pd.to_datetime(["2023-09-01", "2024-09-01"]),
                "indicator_123": ["N/A", "x"],
                "filter_ethnicity": ["ETH1", "ETH2"],
            }
        )

        with pytest.raises(ValueError, match="No numerical data available"):
            prepare_chart_data(df, "indicator_123", "ethnicity")
