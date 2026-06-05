import sys
import os
import unittest
from unittest.mock import patch

# Add services directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from jobs.daily_transit_aggregation import get_db_connection

class TestDSNParser(unittest.TestCase):
    @patch('jobs.daily_transit_aggregation.psycopg2.connect')
    def test_parsing_standard(self, mock_connect):
        get_db_connection("postgresql://usr:pass@localhost:5432/db")
        mock_connect.assert_called_with(dbname='db', user='usr', password='pass', host='localhost', port='5432')

    @patch('jobs.daily_transit_aggregation.psycopg2.connect')
    def test_parsing_with_special_chars(self, mock_connect):
        get_db_connection("postgresql://usr:p@ssw@rd@localhost:5432/db")
        mock_connect.assert_called_with(dbname='db', user='usr', password='p@ssw@rd', host='localhost', port='5432')

    @patch('jobs.daily_transit_aggregation.psycopg2.connect')
    def test_parsing_fallback(self, mock_connect):
        get_db_connection("host=localhost user=usr password=pass dbname=db")
        mock_connect.assert_called_with("host=localhost user=usr password=pass dbname=db")

if __name__ == '__main__':
    unittest.main()
