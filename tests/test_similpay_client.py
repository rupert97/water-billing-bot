"""Tests for Similpay client"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.similpay_client import SimilpayClient


class TestSimilpayClient(unittest.TestCase):
    """Test cases for SimilpayClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = SimilpayClient()

    def test_client_configuration(self):
        """Test client is properly configured"""
        self.assertEqual(self.client.PROJECT_ID, "18590")
        self.assertEqual(self.client.USER_REFERENCE, "9999999")
        self.assertEqual(self.client.HOST, "www.similpay.com")

    @patch("src.similpay_client.SimilpayClient._get_token")
    @patch("urllib.request.urlopen")
    def test_query_bills_success(self, mock_urlopen, mock_get_token):
        """Test successful bill query"""
        mock_get_token.return_value = "test_token_123"

        mock_response = {
            "Code": "1",
            "Message": "DEUDA PENDIENTE",
            "Data": {
                "amount": 45.50,
                "expirationDate": "2026-05-15T00:00:00",
                "reference": "9999999",
            },
        }

        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            mock_response
        ).encode("utf-8")

        result = self.client.query_bills()
        self.assertIsNotNone(result)
        self.assertEqual(result["Code"], "1")
        self.assertEqual(result["Data"]["amount"], 45.50)

    def test_extract_unpaid_bills(self):
        """Test extraction of unpaid bills"""
        api_response = {
            "Code": "1",
            "Data": {
                "amount": 45.50,
                "expirationDate": "2026-05-15T00:00:00",
                "reference": "9999999",
            },
        }

        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 1)
        self.assertEqual(unpaid[0]["amount"], 45.50)
        self.assertEqual(unpaid[0]["dueDate"], "2026-05-15T00:00:00")

    def test_extract_unpaid_bills_empty_response(self):
        """Test extraction with empty response"""
        api_response = {"Code": "2", "Data": {}}
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 0)

    def test_extract_unpaid_bills_paid_response(self):
        """Test extraction with paid bill (Code 3)"""
        api_response = {"Code": "3", "Message": "REFERENCIA YA PAGADA", "Data": {"amount": None}}
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 0)

    def test_generate_bill_id_from_date(self):
        """Test bill ID generation from due date"""
        bill = {"amount": 45.50, "dueDate": "2026-05-15T00:00:00"}
        bill_id = self.client.generate_bill_id(bill)
        self.assertEqual(bill_id, "water_bill_2026_05")

    def test_generate_bill_id_null_date_fallback(self):
        """Test bill ID generation with null/zero date"""
        bill = {"amount": 45.50, "dueDate": "0001-01-01T00:00:00"}
        bill_id = self.client.generate_bill_id(bill)
        self.assertEqual(bill_id, "water_bill_45.5")

    def test_generate_bill_id_missing_amount(self):
        """Test bill ID generation with missing amount"""
        bill = {"dueDate": ""}
        bill_id = self.client.generate_bill_id(bill)
        self.assertEqual(bill_id, "water_bill_unknown")


class TestSimilpayClientErrorHandling(unittest.TestCase):
    """Test error handling in SimilpayClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = SimilpayClient()

    @patch("urllib.request.urlopen")
    def test_query_bills_connection_error(self, mock_urlopen):
        """Test handling of connection errors"""
        mock_urlopen.side_effect = Exception("Connection failed")

        result = self.client.query_bills()
        self.assertIsNone(result)

    def test_extract_unpaid_bills_malformed_response(self):
        """Test extraction with malformed response"""
        api_response = {"invalid": "structure"}
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 0)

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_env_var(self):
        """Test initialization fails if env var is missing"""
        with self.assertRaises(ValueError) as context:
            SimilpayClient()
        self.assertIn(
            "SIMILPAY_USER_REFERENCE environment variable is not set", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
