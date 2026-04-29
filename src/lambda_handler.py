"""AWS Lambda handler for Water Billing Tracker Bot"""

import json
import logging
import sys

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from bill_processor import BillProcessor

# Import application modules
from similpay_client import SimilpayClient
from state_manager import StateManager
from telegram_notifier import TelegramNotifier


def handler(event, context):
    """
    Main Lambda handler function - triggered daily by EventBridge

    Args:
        event: EventBridge scheduled event
        context: Lambda context object

    Returns:
        dict: Response with statusCode and execution results
    """
    logger.info("Water Billing Tracker Bot started")
    logger.info(f"Event: {json.dumps(event)}")

    try:
        # Initialize components
        similpay_client = SimilpayClient()
        state_manager = StateManager()
        telegram_notifier = TelegramNotifier()
        bill_processor = BillProcessor(similpay_client, state_manager, telegram_notifier)

        mock_data = None
        if event and "Code" in event:
            logger.info("Test event detected: Using mock data for processing")
            mock_data = event

        result = bill_processor.process_bills(mock_data=mock_data)

        # Log results
        logger.info(f"Processing complete: {json.dumps(result)}")

        return {"statusCode": 200 if result["success"] else 500, "body": json.dumps(result)}

    except Exception as e:
        logger.error(f"Fatal error in handler: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"success": False, "error": str(e)})}
