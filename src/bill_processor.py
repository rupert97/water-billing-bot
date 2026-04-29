"""Core bill processing and notification logic"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger()


class BillProcessor:
    """Processes bills and determines notification requirements"""

    URGENT_THRESHOLD_DAYS = 2  # Send urgent reminder 2 days before due date

    def __init__(self, similpay_client, state_manager, telegram_notifier):
        """
        Initialize bill processor

        Args:
            similpay_client: SimilpayClient instance
            state_manager: StateManager instance
            telegram_notifier: TelegramNotifier instance
        """
        self.similpay = similpay_client
        self.state = state_manager
        self.telegram = telegram_notifier
        self.logger = logger

    def process_bills(self, mock_data=None) -> Dict:
        """
        Main processing workflow

        Returns:
            dict: Processing results with statistics
        """
        result = {
            "success": False,
            "bills_found": 0,
            "new_alerts_sent": 0,
            "urgent_alerts_sent": 0,
            "errors": [],
        }

        try:
            # If mock_data is provided, use it. Otherwise, call the API.
            if mock_data:
                self.logger.info("Skipping Similpay API call, using mock data")
                api_response = mock_data
            else:
                self.logger.info(f"Querying Similpay for reference {self.similpay.USER_REFERENCE}")
                api_response = self.similpay.query_bills()

            if not api_response:
                result["errors"].append("Failed to get API response")
                return result

            # Ensure DynamoDB table exists
            if not self.state.ensure_table_exists():
                result["errors"].append("Failed to ensure DynamoDB table exists")
                return result

            # Extract unpaid bills
            unpaid_bills = self.similpay.extract_unpaid_bills(api_response)
            result["bills_found"] = len(unpaid_bills)

            if not unpaid_bills:
                self.logger.info("No unpaid bills found")
                result["success"] = True
                return result

            # Process each bill
            for bill in unpaid_bills:
                self.logger.info(f"Processing bill: {bill}")

                try:
                    # Generate bill ID for state tracking
                    bill_id = self.similpay.generate_bill_id(bill)
                    amount = float(bill.get("amount", 0))
                    due_date = bill.get("dueDate", "")

                    # Get or create state
                    state = self.state.get_bill_state(bill_id)
                    if state is None:
                        # New bill, create state
                        if not self.state.create_bill_state(bill_id):
                            self.logger.error(f"Failed to create state for bill {bill_id}")
                            continue
                        state = {"notified_new": False, "urgent_sent": False}

                    # Check if new bill notification needed
                    if not state.get("notified_new", False):
                        if self.telegram.send_new_bill_alert(amount, due_date):
                            self.state.mark_new_bill_notified(bill_id)
                            result["new_alerts_sent"] += 1

                    # Check if urgent reminder needed
                    if not state.get("urgent_sent", False):
                        days_until_due = self._days_until_due(due_date)

                        if 0 <= days_until_due <= self.URGENT_THRESHOLD_DAYS:
                            if self.telegram.send_urgent_reminder(amount, due_date, days_until_due):
                                self.state.mark_urgent_notified(bill_id)
                                result["urgent_alerts_sent"] += 1

                except Exception as e:
                    self.logger.error(f"Error processing bill {bill}: {str(e)}")
                    result["errors"].append(f"Error processing bill: {str(e)}")

            result["success"] = True
            return result

        except Exception as e:
            self.logger.error(f"Fatal error in bill processing: {str(e)}", exc_info=True)
            result["errors"].append(f"Fatal error: {str(e)}")
            return result

    @staticmethod
    def _days_until_due(due_date: str) -> int:
        try:
            # Split by 'T' to ignore the time part and only parse the date
            date_only = due_date.split("T")[0]
            due_datetime = datetime.strptime(date_only, "%Y-%m-%d")

            today = datetime.now()
            # Ensure we are comparing dates only to avoid negative rounding
            delta = due_datetime.date() - today.date()
            return delta.days
        except (ValueError, TypeError, IndexError):
            logger.warning(f"Could not parse due date: {due_date}")
            return -1
