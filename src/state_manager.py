"""DynamoDB state management for bill tracking"""

import json
import logging
from typing import Dict, Optional, Any, cast

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()


class StateManager:
    """Manages bill notification state in DynamoDB"""

    TABLE_NAME = "WaterBillState"

    def __init__(self):
        """Initialize DynamoDB client"""
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.TABLE_NAME)
        self.logger = logger

    def get_bill_state(self, bill_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve bill notification state from DynamoDB

        Args:
            bill_id: Unique bill identifier

        Returns:
            dict: Bill state with notified_new and urgent_sent flags, or None if not found
        """
        try:
            response = self.table.get_item(Key={"bill_id": bill_id})
            item = response.get("Item")
            return cast(Optional[Dict[str, Any]], item)
        except ClientError as e:
            self.logger.error(f"DynamoDB error: {str(e)}")
            return None

    def create_bill_state(self, bill_id: str) -> bool:
        """
        Create initial bill state in DynamoDB

        Args:
            bill_id: Unique bill identifier

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.table.put_item(
                Item={"bill_id": bill_id, "notified_new": False, "urgent_sent": False}
            )
            self.logger.info(f"Created new state for bill {bill_id}")
            return True

        except ClientError as e:
            self.logger.error(f"DynamoDB put_item error: {str(e)}")
            return False

    def mark_new_bill_notified(self, bill_id: str) -> bool:
        """
        Mark that new bill notification has been sent

        Args:
            bill_id: Unique bill identifier

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.table.update_item(
                Key={"bill_id": bill_id},
                UpdateExpression="SET notified_new = :val",
                ExpressionAttributeValues={":val": True},
            )
            self.logger.info(f"Marked bill {bill_id} as notified (new)")
            return True

        except ClientError as e:
            self.logger.error(f"DynamoDB update_item error: {str(e)}")
            return False

    def mark_urgent_notified(self, bill_id: str) -> bool:
        """
        Mark that urgent notification has been sent

        Args:
            bill_id: Unique bill identifier

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.table.update_item(
                Key={"bill_id": bill_id},
                UpdateExpression="SET urgent_sent = :val",
                ExpressionAttributeValues={":val": True},
            )
            self.logger.info(f"Marked bill {bill_id} as notified (urgent)")
            return True

        except ClientError as e:
            self.logger.error(f"DynamoDB update_item error: {str(e)}")
            return False

    def ensure_table_exists(self) -> bool:
        """
        Ensure DynamoDB table exists, create if needed

        Returns:
            bool: True if table exists or was created successfully
        """
        try:
            # Check if table exists
            self.table.table_status
            self.logger.info(f"DynamoDB table '{self.TABLE_NAME}' exists")
            return True

        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            self.logger.info(f"DynamoDB table '{self.TABLE_NAME}' does not exist, creating...")

            try:
                self.dynamodb.create_table(
                    TableName=self.TABLE_NAME,
                    KeySchema=[{"AttributeName": "bill_id", "KeyType": "HASH"}],
                    AttributeDefinitions=[{"AttributeName": "bill_id", "AttributeType": "S"}],
                    BillingMode="PAY_PER_REQUEST",
                )
                self.logger.info(f"Created DynamoDB table '{self.TABLE_NAME}'")
                return True

            except ClientError as e:
                self.logger.error(f"Failed to create DynamoDB table: {str(e)}")
                return False

        except Exception as e:
            self.logger.error(f"Unexpected error checking DynamoDB table: {str(e)}")
            return False
