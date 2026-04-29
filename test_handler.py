"""
Lambda Handler Test - Run this to test locally before deployment

Usage:
    python test_handler.py

This simulates an EventBridge event and tests the main handler.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock environment variables before importing
import os

os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
os.environ["TELEGRAM_CHAT_ID"] = "test_chat_id"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["SIMILPAY_USER_REFERENCE"] = "9999999"

# Create a mock event
mock_event = {
    "version": "0",
    "id": "6a7e8feb-b491-4cf7-a9f1-bf3703467718",
    "detail-type": "Scheduled Event",
    "source": "aws.events",
    "account": "123456789012",
    "time": "2026-04-27T08:00:00Z",
    "region": "us-east-1",
    "resources": [],
    "detail": {},
}

mock_context = type(
    "obj",
    (object,),
    {
        "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:water-billing-tracker",
        "aws_request_id": "test-request-id",
    },
)()

if __name__ == "__main__":
    print("=" * 60)
    print("Water Billing Tracker Bot - Handler Test")
    print("=" * 60)
    print()
    print("Testing Lambda handler with mock EventBridge event...")
    print()

    try:
        # Import handler
        from src.lambda_handler import handler

        # Call handler
        print("Invoking handler...")
        response = handler(mock_event, mock_context)

        print()
        print("Response:")
        print(json.dumps(response, indent=2))

        if response["statusCode"] == 200:
            print()
            print("[OK] Handler executed successfully!")
            print()
            print("Note: This is a test run with mocked DynamoDB and Telegram.")
            print("Actual deployment requires:")
            print("  1. DynamoDB table: WaterBillState")
            print("  2. Telegram Bot Token (environment variable)")
            print("  3. Telegram Chat ID (environment variable)")
        else:
            print()
            print("[ERROR] Handler returned error status")

    except Exception as e:
        print()
        print(f"[ERROR] Error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
