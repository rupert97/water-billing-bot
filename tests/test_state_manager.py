"""Tests for state manager"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.state_manager import StateManager


class TestStateManager(unittest.TestCase):
    """Test cases for StateManager"""

    @patch("boto3.resource")
    def setUp(self, mock_boto3):
        """Set up test fixtures"""
        self.mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = self.mock_table
        mock_boto3.return_value = mock_dynamodb

        self.manager = StateManager()

    @patch("boto3.resource")
    def test_manager_initialization(self, mock_boto3):
        """Test manager is properly initialized"""
        mock_dynamodb = MagicMock()
        mock_boto3.return_value = mock_dynamodb

        manager = StateManager()
        self.assertEqual(manager.TABLE_NAME, "WaterBillState")

    @patch("boto3.resource")
    def test_get_bill_state_found(self, mock_boto3):
        """Test retrieving existing bill state"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        mock_table.get_item.return_value = {
            "Item": {"bill_id": "water_bill_2026_05", "notified_new": True, "urgent_sent": False}
        }

        manager = StateManager()
        state = manager.get_bill_state("water_bill_2026_05")

        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(state["bill_id"], "water_bill_2026_05")
        self.assertTrue(state["notified_new"])

    @patch("boto3.resource")
    def test_get_bill_state_not_found(self, mock_boto3):
        """Test retrieving non-existent bill state"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        mock_table.get_item.return_value = {}  # No 'Item' key

        manager = StateManager()
        state = manager.get_bill_state("nonexistent")

        self.assertIsNone(state)

    @patch("boto3.resource")
    def test_create_bill_state(self, mock_boto3):
        """Test creating new bill state"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        manager = StateManager()
        result = manager.create_bill_state("water_bill_2026_05")

        self.assertTrue(result)
        mock_table.put_item.assert_called_once()

    @patch("boto3.resource")
    def test_mark_new_bill_notified(self, mock_boto3):
        """Test marking bill as notified"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        manager = StateManager()
        result = manager.mark_new_bill_notified("water_bill_2026_05")

        self.assertTrue(result)
        mock_table.update_item.assert_called_once()

    @patch("boto3.resource")
    def test_mark_urgent_notified(self, mock_boto3):
        """Test marking urgent notification"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        manager = StateManager()
        result = manager.mark_urgent_notified("water_bill_2026_05")

        self.assertTrue(result)
        mock_table.update_item.assert_called_once()

    @patch("boto3.resource")
    def test_get_bill_state_error_handling(self, mock_boto3):
        """Test error handling in get_bill_state"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        mock_table.get_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationException"}}, "GetItem"
        )

        manager = StateManager()
        state = manager.get_bill_state("water_bill_2026_05")

        self.assertIsNone(state)

    @patch("boto3.resource")
    def test_create_bill_state_error_handling(self, mock_boto3):
        """Test error handling in create_bill_state"""
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationException"}}, "PutItem"
        )

        manager = StateManager()
        result = manager.create_bill_state("water_bill_2026_05")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
