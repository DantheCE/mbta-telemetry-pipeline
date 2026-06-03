import pytest
from unittest.mock import patch, MagicMock
from producer import fetch_transit_data

def test_fetch_transit_data():
    with patch("producer.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock_data"
        mock_get.return_value = mock_response
        
        result = fetch_transit_data("http://fake", "fake_key")
        
        assert result == b"mock_data"
        mock_get.assert_called_once()
        assert mock_get.call_args[1]["headers"]["x-api-key"] == "fake_key"
