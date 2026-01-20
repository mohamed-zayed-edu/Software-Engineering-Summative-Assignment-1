from unittest.mock import Mock, patch
import pytest
import requests
import pandas as pd
from api import get_json, get_metadata, post_query, query_dataset, BASE_URL


class TestGetJson:
    """Tests for _get_json function."""

    @patch("api.requests.get")
    def test_get_json_success(self, mock_get):
        """Test successful API GET request."""
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = get_json("publications")

        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            f"{BASE_URL}/publications",
            params=None,
            headers={"Accept": "application/json"},
            timeout=30,
        )

    @patch("api.requests.get")
    def test_get_json_with_params(self, mock_get):
        """Test GET request with query parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        params = {"filter": "value", "limit": 10}
        result = get_json("data", params=params)

        assert result == {"results": []}
        mock_get.assert_called_once_with(
            f"{BASE_URL}/data",
            params=params,
            headers={"Accept": "application/json"},
            timeout=30,
        )

    @patch("api.requests.get")
    def testget_json_http_error(self, mock_get):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            get_json("invalid-endpoint")

    @patch("api.requests.get")
    def test_get_json_timeout(self, mock_get):
        """Test timeout handling."""
        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(requests.Timeout):
            get_json("slow-endpoint")


class TestGetMetadata:
    """Tests for get_metadata function."""

    @patch("api.get_json")
    def test_get_metadata_success(self, mock_get_json):
        """Test successful metadata retrieval."""
        mock_metadata = {
            "filters": [{"id": "gender", "label": "Gender"}],
            "indicators": [{"id": "ind1", "label": "Indicator 1"}],
            "geographicLevels": [{"code": "NAT", "label": "National"}],
            "locations": [{"code": "E92000001", "label": "England"}],
            "timePeriods": [{"code": "AY", "period": "2024/2025"}],
        }
        mock_get_json.return_value = mock_metadata

        result = get_metadata("dataset123")

        assert result == mock_metadata
        mock_get_json.assert_called_once_with("data-sets/dataset123/meta")


class TestPostQuery:
    """Tests for post_query function."""

    @patch("api.requests.post")
    def test_post_query_success(self, mock_post):
        """Test successful API POST request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"value": 123}],
            "paging": {"page": 1, "totalPages": 1},
        }
        mock_post.return_value = mock_response

        payload = {"criteria": {"geographicLevels": {"in": ["NAT"]}}}
        result = post_query("data-sets/ds1/query", payload)

        assert result["results"] == [{"value": 123}]
        mock_post.assert_called_once_with(
            f"{BASE_URL}/data-sets/ds1/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

    @patch("api.requests.post")
    def test_post_query_http_error(self, mock_post):
        """Test HTTP error handling in POST."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Bad Request"
        )
        mock_post.return_value = mock_response

        payload = {"criteria": {}}
        with pytest.raises(requests.HTTPError):
            post_query("data-sets/ds1/query", payload)


class TestQueryDataset:
    """Tests for query_dataset function."""

    @patch("api.get_metadata")
    @patch("api.post_query")
    def test_query_dataset_single_page(self, mock_post_query, mock_get_metadata):
        """Test querying a dataset with single page of results."""
        # Mock metadata
        mock_get_metadata.return_value = {
            "timePeriods": [
                {"code": "AY", "period": "2024/2025"},
                {"code": "AY", "period": "2023/2024"},
            ]
        }

        # Mock API response
        mock_post_query.return_value = {
            "results": [
                {
                    "timePeriod": {"period": "2024/2025"},
                    "geographicLevel": "NAT",
                    "locations": {"E92000001": "England"},
                    "values": {"QL4wb :: elg_combination_children_count": "100"},
                    "filters": {"gender": "M"},
                }
            ],
            "paging": {"page": 1, "totalPages": 1},
        }

        df = query_dataset(
            dataset_id="ds1",
            indicator_id="QL4wb",
            geo_level_codes=["NAT"],
            period_list=["2024/2025"],
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.loc[0, "geographic_level"] == "NAT"
        assert df.loc[0, "location_name"] == "England"

    @patch("api.get_metadata")
    @patch("api.post_query")
    def test_query_dataset_multiple_pages(self, mock_post_query, mock_get_metadata):
        """Test querying a dataset with pagination."""
        mock_get_metadata.return_value = {
            "timePeriods": [{"code": "AY", "period": "2024/2025"}]
        }

        # Mock paginated responses
        page1_response = {
            "results": [
                {
                    "timePeriod": {"period": "2024/2025"},
                    "geographicLevel": "NAT",
                    "locations": {"E92000001": "England"},
                    "values": {"QL4wb :: indicator": "100"},
                    "filters": {},
                }
            ],
            "paging": {"page": 1, "totalPages": 2},
        }

        page2_response = {
            "results": [
                {
                    "timePeriod": {"period": "2024/2025"},
                    "geographicLevel": "NAT",
                    "locations": {"E92000001": "England"},
                    "values": {"QL4wb :: indicator": "200"},
                    "filters": {},
                }
            ],
            "paging": {"page": 2, "totalPages": 2},
        }

        mock_post_query.side_effect = [page1_response, page2_response]

        df = query_dataset(
            dataset_id="ds1",
            indicator_id="QL4wb",
            geo_level_codes=["NAT"],
            period_list=["2024/2025"],
        )

        assert len(df) == 2
        assert mock_post_query.call_count == 2

    @patch("api.get_metadata")
    @patch("api.post_query")
    def test_query_dataset_no_results_error(self, mock_post_query, mock_get_metadata):
        """Test error handling when API returns no results."""
        mock_get_metadata.return_value = {"timePeriods": []}

        mock_post_query.return_value = {
            "results": [],
            "warnings": [{"code": "NoResults", "message": "No data found"}],
            "paging": {"page": 1, "totalPages": 1},
        }

        with pytest.raises(ValueError, match="The query returned no data"):
            query_dataset(
                dataset_id="ds1",
                indicator_id="QL4wb",
                geo_level_codes=["NAT"],
                period_list=["2024/2025"],
            )

    @patch("api.get_metadata")
    @patch("api.post_query")
    def test_query_dataset_with_filters(self, mock_post_query, mock_get_metadata):
        """Test querying with client-side filtering."""
        mock_get_metadata.return_value = {
            "timePeriods": [{"code": "AY", "period": "2024/2025"}]
        }

        mock_post_query.return_value = {
            "results": [
                {
                    "timePeriod": {"period": "2024/2025"},
                    "geographicLevel": "NAT",
                    "locations": {"E92000001": "England"},
                    "values": {"QL4wb :: indicator": "100"},
                    "filters": {"gender": "M :: Male"},
                },
                {
                    "timePeriod": {"period": "2024/2025"},
                    "geographicLevel": "NAT",
                    "locations": {"E92000001": "England"},
                    "values": {"QL4wb :: indicator": "200"},
                    "filters": {"gender": "F :: Female"},
                },
            ],
            "paging": {"page": 1, "totalPages": 1},
        }

        df = query_dataset(
            dataset_id="ds1",
            indicator_id="QL4wb",
            geo_level_codes=["NAT"],
            period_list=["2024/2025"],
            filters={"gender": {"in": ["M"]}},
        )

        # Should only have male records
        assert len(df) == 1
