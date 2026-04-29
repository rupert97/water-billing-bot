"""Tests for Similpay client"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

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
        self.assertEqual(self.client.USER_REFERENCE, "2128388")
        self.assertEqual(self.client.HOST, "www.similpay.com")
    
    @patch('urllib.request.urlopen')
    def test_query_bills_success(self, mock_urlopen):
        """Test successful bill query"""
        mock_response = {
            'success': True,
            'data': [
                {
                    'id': '123',
                    'amount': 45.50,
                    'dueDate': '2026-05-15',
                    'status': 'unpaid'
                }
            ]
        }
        
        mock_urlopen.return_value.__enter__.return_value.read.return_value = \
            json.dumps(mock_response).encode('utf-8')
        
        result = self.client.query_bills()
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
    
    def test_extract_unpaid_bills(self):
        """Test extraction of unpaid bills"""
        api_response = {
            'success': True,
            'data': [
                {'id': '1', 'amount': 45.50, 'status': 'unpaid'},
                {'id': '2', 'amount': 30.00, 'status': 'paid'},
                {'id': '3', 'amount': 55.75, 'status': 'unpaid'}
            ]
        }
        
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 2)
        self.assertEqual(unpaid[0]['id'], '1')
        self.assertEqual(unpaid[1]['id'], '3')
    
    def test_extract_unpaid_bills_empty_response(self):
        """Test extraction with empty response"""
        api_response = {'success': True, 'data': []}
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 0)
    
    def test_extract_unpaid_bills_failed_response(self):
        """Test extraction with failed API response"""
        api_response = {'success': False, 'error': 'API error'}
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 0)
    
    def test_generate_bill_id_from_api_id(self):
        """Test bill ID generation with API ID"""
        bill = {'id': '123', 'amount': 45.50, 'dueDate': '2026-05-15'}
        bill_id = self.client.generate_bill_id(bill)
        self.assertEqual(bill_id, 'water_bill_123')
    
    def test_generate_bill_id_from_date(self):
        """Test bill ID generation from due date"""
        bill = {'amount': 45.50, 'dueDate': '2026-05-15'}
        bill_id = self.client.generate_bill_id(bill)
        self.assertEqual(bill_id, 'water_bill_2026_05')
    
    def test_generate_bill_id_fallback(self):
        """Test bill ID generation fallback"""
        bill = {'amount': 45.50}
        bill_id = self.client.generate_bill_id(bill)
        self.assertTrue(bill_id.startswith('water_bill_'))


class TestSimilpayClientErrorHandling(unittest.TestCase):
    """Test error handling in SimilpayClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SimilpayClient()
    
    @patch('urllib.request.urlopen')
    def test_query_bills_connection_error(self, mock_urlopen):
        """Test handling of connection errors"""
        mock_urlopen.side_effect = Exception("Connection failed")
        
        result = self.client.query_bills()
        self.assertIsNone(result)
    
    def test_extract_unpaid_bills_malformed_response(self):
        """Test extraction with malformed response"""
        api_response = {'invalid': 'structure'}
        unpaid = self.client.extract_unpaid_bills(api_response)
        self.assertEqual(len(unpaid), 0)


if __name__ == '__main__':
    unittest.main()
