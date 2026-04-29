"""Core bill processing and notification logic"""

import logging
from datetime import datetime
from typing import Any, Dict, List, cast

logger = logging.getLogger()


class BillProcessor:
    URGENT_THRESHOLD_DAYS = 2

    def __init__(self, similpay_client: Any, state_manager: Any, telegram_notifier: Any) -> None:
        self.similpay = similpay_client
        self.state = state_manager
        self.telegram = telegram_notifier
        self.logger = logger

    def process_bills(self, mock_data: Any = None) -> Dict[str, Any]:
        # Explicitly typing as Any prevents Mypy from assuming 'object'
        result: Dict[str, Any] = {
            "success": False,
            "bills_found": 0,
            "new_alerts_sent": 0,
            "urgent_alerts_sent": 0,
            "errors": [],
        }

        try:
            api_response = mock_data if mock_data else self.similpay.query_bills()

            if not api_response:
                result["errors"].append("Failed to get API response")
                return result

            if not self.state.ensure_table_exists():
                result["errors"].append("Failed to ensure DynamoDB table exists")
                return result

            unpaid_bills = self.similpay.extract_unpaid_bills(api_response)
            result["bills_found"] = len(unpaid_bills)

            if not unpaid_bills:
                result["success"] = True
                return result

            for bill in unpaid_bills:
                try:
                    bill_id = self.similpay.generate_bill_id(bill)
                    amount = float(bill.get("amount", 0))
                    due_date = str(bill.get("dueDate", ""))

                    state = self.state.get_bill_state(bill_id)
                    if state is None:
                        if not self.state.create_bill_state(bill_id):
                            continue
                        state = {"notified_new": False, "urgent_sent": False}

                    if not state.get("notified_new", False):
                        if self.telegram.send_new_bill_alert(amount, due_date):
                            self.state.mark_new_bill_notified(bill_id)
                            result["new_alerts_sent"] += 1

                    if not state.get("urgent_sent", False):
                        days_until_due = self._days_until_due(due_date)
                        if 0 <= days_until_due <= self.URGENT_THRESHOLD_DAYS:
                            if self.telegram.send_urgent_reminder(amount, due_date, days_until_due):
                                self.state.mark_urgent_notified(bill_id)
                                result["urgent_alerts_sent"] += 1

                except Exception as e:
                    result["errors"].append(f"Error processing bill: {str(e)}")

            result["success"] = True
            return result

        except Exception as e:
            result["errors"].append(f"Fatal error: {str(e)}")
            return result

    @staticmethod
    def _days_until_due(due_date: str) -> int:
        try:
            date_only = due_date.split("T")[0]
            due_datetime = datetime.strptime(date_only, "%Y-%m-%d")
            today = datetime.now()
            delta = due_datetime.date() - today.date()
            return int(delta.days)
        except (ValueError, TypeError, IndexError):
            return -1
