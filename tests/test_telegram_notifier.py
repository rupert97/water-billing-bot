"""Tests for Telegram notifier"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.telegram_notifier import TelegramNotifier


class TestTelegramNotifier(unittest.TestCase):
    """Test cases for TelegramNotifier"""

    def setUp(self):
        """Set up test fixtures"""
        self.token = "test_token_12345"
        self.chat_id = "12345678"
        self.notifier = TelegramNotifier(self.token, self.chat_id)

    def test_notifier_initialization(self):
        """Test notifier is properly initialized"""
        self.assertEqual(self.notifier.token, self.token)
        self.assertEqual(self.notifier.chat_id, self.chat_id)

    def test_notifier_from_env_vars(self):
        """Test notifier initialization from environment variables"""
        with patch.dict(
            os.environ, {"TELEGRAM_BOT_TOKEN": "env_token", "TELEGRAM_CHAT_ID": "env_chat"}
        ):
            notifier = TelegramNotifier()
            self.assertEqual(notifier.token, "env_token")
            self.assertEqual(notifier.chat_id, "env_chat")

    @patch("urllib.request.urlopen")
    def test_send_new_bill_alert(self, mock_urlopen):
        """Test sending new bill alert"""
        mock_response = {"ok": True, "result": {"message_id": 123}}
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            mock_response
        ).encode("utf-8")

        result = self.notifier.send_new_bill_alert(45.50, "2026-05-15")
        self.assertTrue(result)
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_send_urgent_reminder(self, mock_urlopen):
        """Test sending urgent reminder"""
        mock_response = {"ok": True, "result": {"message_id": 124}}
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            mock_response
        ).encode("utf-8")

        result = self.notifier.send_urgent_reminder(45.50, "2026-05-15", 2)
        self.assertTrue(result)
        mock_urlopen.assert_called_once()

    def test_send_message_missing_credentials(self):
        """Test send_message with missing credentials"""
        notifier = TelegramNotifier()  # No token or chat_id
        result = notifier.send_message("Test message")
        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_send_message_api_error(self, mock_urlopen):
        """Test send_message with API error response"""
        mock_response = {"ok": False, "description": "Bot was blocked by the user"}
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            mock_response
        ).encode("utf-8")

        result = self.notifier.send_message("Test message")
        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_send_message_connection_error(self, mock_urlopen):
        """Test send_message with connection error"""
        mock_urlopen.side_effect = Exception("Connection failed")

        result = self.notifier.send_message("Test message")
        self.assertFalse(result)

    def test_send_message_insecure_url(self):
        """Test send_message rejects non-https URLs"""
        with patch.object(
            self.notifier, "API_URL", "http://api.telegram.org/bot{token}/sendMessage"
        ):
            result = self.notifier.send_message("Test message")
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
