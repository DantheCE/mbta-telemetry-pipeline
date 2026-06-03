import pytest
from unittest.mock import MagicMock
from consumer import init_db

def test_init_db():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    init_db(mock_conn)
    
    mock_cursor.execute.assert_called_once()
    assert "CREATE TABLE IF NOT EXISTS vehicle_positions" in mock_cursor.execute.call_args[0][0]
    mock_conn.commit.assert_called_once()
