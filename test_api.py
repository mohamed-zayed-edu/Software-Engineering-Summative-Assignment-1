from unittest.mock import Mock, patch
import pytest
import requests

from api import get_json, get_metadata, BASE_URL


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
