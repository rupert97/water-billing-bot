import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add src to sys.path so lambda_handler can import its dependencies
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


class TestLambdaHandler(unittest.TestCase):
    @patch("src.lambda_handler.BillProcessor")
    @patch("src.lambda_handler.TelegramNotifier")
    @patch("src.lambda_handler.StateManager")
    @patch("src.lambda_handler.SimilpayClient")
    def test_handler_success(self, MockSimilpay, MockState, MockTelegram, MockProcessor):
        from src.lambda_handler import handler

        # Setup mock processor
        mock_processor_instance = MockProcessor.return_value
        mock_processor_instance.process_bills.return_value = {
            "success": True,
            "bills_found": 1,
            "new_alerts_sent": 1,
            "urgent_alerts_sent": 0,
            "errors": [],
        }

        # Call handler
        event = {"source": "aws.events"}
        context = MagicMock()
        response = handler(event, context)

        # Assertions
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertTrue(body["success"])
        mock_processor_instance.process_bills.assert_called_once_with(mock_data=None)

    @patch("src.lambda_handler.BillProcessor")
    @patch("src.lambda_handler.TelegramNotifier")
    @patch("src.lambda_handler.StateManager")
    @patch("src.lambda_handler.SimilpayClient")
    def test_handler_mock_data(self, MockSimilpay, MockState, MockTelegram, MockProcessor):
        from src.lambda_handler import handler

        # Setup mock processor
        mock_processor_instance = MockProcessor.return_value
        mock_processor_instance.process_bills.return_value = {
            "success": True,
            "bills_found": 0,
            "new_alerts_sent": 0,
            "urgent_alerts_sent": 0,
            "errors": [],
        }

        # Call handler with test data containing "Code"
        event = {"Code": "1", "Data": {}}
        context = MagicMock()
        response = handler(event, context)

        # Assertions
        self.assertEqual(response["statusCode"], 200)
        mock_processor_instance.process_bills.assert_called_once_with(mock_data=event)

    @patch("src.lambda_handler.BillProcessor")
    @patch("src.lambda_handler.TelegramNotifier")
    @patch("src.lambda_handler.StateManager")
    @patch("src.lambda_handler.SimilpayClient")
    def test_handler_failure(self, MockSimilpay, MockState, MockTelegram, MockProcessor):
        from src.lambda_handler import handler

        # Setup mock processor
        mock_processor_instance = MockProcessor.return_value
        mock_processor_instance.process_bills.return_value = {
            "success": False,
            "bills_found": 0,
            "errors": ["API Error"],
        }

        # Call handler
        event = {"source": "aws.events"}
        context = MagicMock()
        response = handler(event, context)

        # Assertions
        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertFalse(body["success"])

    @patch("src.lambda_handler.SimilpayClient")
    def test_handler_exception(self, MockSimilpay):
        from src.lambda_handler import handler

        MockSimilpay.side_effect = Exception("Initialization failed")

        # Call handler
        event: dict = {}
        context = MagicMock()
        response = handler(event, context)

        # Assertions
        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertFalse(body["success"])
        self.assertIn("Initialization failed", body["error"])


if __name__ == "__main__":
    unittest.main()
