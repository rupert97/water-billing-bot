"""Tests for bill processor"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bill_processor import BillProcessor


class TestBillProcessor(unittest.TestCase):
    """Test cases for BillProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.similpay_mock = MagicMock()
        self.state_mock = MagicMock()
        self.telegram_mock = MagicMock()
        
        self.processor = BillProcessor(
            self.similpay_mock,
            self.state_mock,
            self.telegram_mock
        )
    
    def test_processor_initialization(self):
        """Test processor is properly initialized"""
        self.assertIsNotNone(self.processor.similpay)
        self.assertIsNotNone(self.processor.state)
        self.assertIsNotNone(self.processor.telegram)
    
    def test_process_bills_no_bills(self):
        """Test processing with no unpaid bills"""
        self.state_mock.ensure_table_exists.return_value = True
        self.similpay_mock.query_bills.return_value = {'success': True, 'data': []}
        self.similpay_mock.extract_unpaid_bills.return_value = []
        
        result = self.processor.process_bills()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['bills_found'], 0)
        self.assertEqual(result['new_alerts_sent'], 0)
    
    def test_process_bills_new_bill_alert(self):
        """Test new bill alert is sent"""
        self.state_mock.ensure_table_exists.return_value = True
        self.state_mock.get_bill_state.return_value = None  # New bill
        self.state_mock.create_bill_state.return_value = True
        self.state_mock.mark_new_bill_notified.return_value = True
        
        self.similpay_mock.query_bills.return_value = {'success': True}
        self.similpay_mock.extract_unpaid_bills.return_value = [
            {'id': '123', 'amount': 45.50, 'dueDate': '2026-05-15', 'status': 'unpaid'}
        ]
        self.similpay_mock.generate_bill_id.return_value = 'water_bill_123'
        
        self.telegram_mock.send_new_bill_alert.return_value = True
        self.telegram_mock.send_urgent_reminder.return_value = False
        
        result = self.processor.process_bills()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['bills_found'], 1)
        self.assertEqual(result['new_alerts_sent'], 1)
        self.telegram_mock.send_new_bill_alert.assert_called_once()
    
    def test_process_bills_already_notified(self):
        """Test no alert if already notified"""
        self.state_mock.ensure_table_exists.return_value = True
        self.state_mock.get_bill_state.return_value = {
            'notified_new': True,
            'urgent_sent': False
        }
        
        self.similpay_mock.query_bills.return_value = {'success': True}
        self.similpay_mock.extract_unpaid_bills.return_value = [
            {'id': '123', 'amount': 45.50, 'dueDate': '2026-05-15', 'status': 'unpaid'}
        ]
        self.similpay_mock.generate_bill_id.return_value = 'water_bill_123'
        
        self.telegram_mock.send_new_bill_alert.return_value = False
        self.telegram_mock.send_urgent_reminder.return_value = False
        
        result = self.processor.process_bills()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['new_alerts_sent'], 0)
        self.telegram_mock.send_new_bill_alert.assert_not_called()
    
    def test_process_bills_urgent_reminder(self):
        """Test urgent reminder is sent when due"""
        # Due date is 1 day away
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        self.state_mock.ensure_table_exists.return_value = True
        self.state_mock.get_bill_state.return_value = {
            'notified_new': True,
            'urgent_sent': False
        }
        self.state_mock.mark_urgent_notified.return_value = True
        
        self.similpay_mock.query_bills.return_value = {'success': True}
        self.similpay_mock.extract_unpaid_bills.return_value = [
            {'id': '123', 'amount': 45.50, 'dueDate': tomorrow, 'status': 'unpaid'}
        ]
        self.similpay_mock.generate_bill_id.return_value = 'water_bill_123'
        
        self.telegram_mock.send_new_bill_alert.return_value = False
        self.telegram_mock.send_urgent_reminder.return_value = True
        
        result = self.processor.process_bills()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['urgent_alerts_sent'], 1)
        self.telegram_mock.send_urgent_reminder.assert_called_once()
    
    def test_process_bills_api_failure(self):
        """Test handling of API failure"""
        self.state_mock.ensure_table_exists.return_value = True
        self.similpay_mock.query_bills.return_value = None  # API failed
        
        result = self.processor.process_bills()
        
        self.assertFalse(result['success'])
        self.assertIn("Failed to query Similpay API", result['errors'])
    
    def test_process_bills_table_creation_failure(self):
        """Test handling of table creation failure"""
        self.state_mock.ensure_table_exists.return_value = False
        
        result = self.processor.process_bills()
        
        self.assertFalse(result['success'])
        self.assertIn("Failed to ensure DynamoDB table exists", result['errors'])


class TestBillProcessorHelpers(unittest.TestCase):
    """Test helper methods"""
    
    def test_days_until_due_future_date(self):
        """Test days calculation for future date"""
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        days = BillProcessor._days_until_due(future_date)
        self.assertEqual(days, 5)
    
    def test_days_until_due_past_date(self):
        """Test days calculation for past date"""
        past_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        days = BillProcessor._days_until_due(past_date)
        self.assertEqual(days, -2)
    
    def test_days_until_due_invalid_format(self):
        """Test days calculation with invalid date format"""
        days = BillProcessor._days_until_due("invalid-date")
        self.assertEqual(days, -1)


if __name__ == '__main__':
    unittest.main()
