import pytest
from unittest.mock import patch, Mock
from src.Extract.eurostat_client import EurostatClient
import requests

# ===== Constructor tests ======

def test_init_valid():
    client = EurostatClient("demo_r_pjangrp3")
    assert client.dataset_name == "demo_r_pjangrp3"

def test_init_empty():
    with pytest.raises(ValueError):
        EurostatClient("")

def test_init_none():
    with pytest.raises(ValueError):
        EurostatClient(None)


# ===== Test validate_dataset =====

# Test if validate_dataset() returns true for a successful API calls
@patch("src.Extract.eurostat_client.requests.get")
def test_validate_dataset_true(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = EurostatClient("test")
    assert client.validate_dataset() is True

# Test if validate_dataset() returns False for a fail API calls
@patch("src.Extract.eurostat_client.requests.get")
def test_validate_dataset_false(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=Mock(status_code=404)
    )

    mock_get.return_value = mock_response

    client = EurostatClient("wrong")
    assert client.validate_dataset() is False



# ==== Test fetch data and date
@patch("src.Extract.eurostat_client.requests.get")
def test_fetch_last_update(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "extension": {
            "annotation": [
                {
                    "type": "UPDATE_DATA",
                    "date": "2026-04-17"
                }
            ]
        }
    }

    mock_get.return_value = mock_response

    client = EurostatClient("test")
    result = client.fetch_last_update_date()

    assert result == "2026-04-17"


@patch("src.Extract.eurostat_client.requests.get")
def test_download_stream(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    client = EurostatClient("test")
    result = client.download_stream()

    assert result == mock_response