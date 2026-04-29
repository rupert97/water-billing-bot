"""Telegram notification sender"""

import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime
from typing import Optional, Any, cast

logger = logging.getLogger()


class TelegramNotifier:
    """Sends notifications via Telegram Bot API"""

    API_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
        """
        Initialize Telegram notifier

        Args:
            token: Telegram bot token (defaults to TELEGRAM_BOT_TOKEN env var)
            chat_id: Target chat ID (defaults to TELEGRAM_CHAT_ID env var)
        """
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.logger = logger

        if not self.token:
            self.logger.warning("TELEGRAM_BOT_TOKEN not configured")
        if not self.chat_id:
            self.logger.warning("TELEGRAM_CHAT_ID not configured")

    def format_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
            return date_obj.strftime("%b %d, %Y")
        except Exception:
            # Fallback if parsing fails
            return date_str.split("T")[0]

    def send_new_bill_alert(self, amount: float, due_date: str) -> bool:
        """
        Send new bill notification

        Args:
            amount: Bill amount
            due_date: Bill due date

        Returns:
            bool: True if sent successfully
        """

        message = (
            f"💧 <b>New Water Bill Alert</b>\n\n"
            f"Amount: ${amount:.2f}\n"
            f"Due Date: {self.format_date(due_date)}\n\n"
            f"<b>Payment Details:</b>\n"
            f"Codigo interno: {os.environ.get('SIMILPAY_USER_REFERENCE')}\n\n"
            f"<a href='https://similpay.com/#/biller_code/18590'>Pay your bill on Similpay</a>"
        )

        return self.send_message(message)

    def send_urgent_reminder(self, amount: float, due_date: str, days_left: int) -> bool:
        """
        Send urgent payment reminder

        Args:
            amount: Bill amount
            due_date: Bill due date
            days_left: Days until due date

        Returns:
            bool: True if sent successfully
        """
        message = (
            f"⚠️ <b>URGENT: Water Bill Due Soon</b>\n\n"
            f"Amount: ${amount:.2f}\n"
            f"Due Date: {self.format_date(due_date)}\n"
            f"Days Left: {days_left}\n\n"
            f"<b>Payment Details:</b>\n"
            f"Codigo interno: {os.environ.get('SIMILPAY_USER_REFERENCE')}\n\n"
            f"⏰ <a href='https://similpay.com/#/biller_code/18590'>PAY NOW to avoid late fees!</a>"
        )

        return self.send_message(message)

    def send_message(self, text: str) -> bool:
        """
        Send message via Telegram API

        Args:
            text: Message text (supports HTML formatting)

        Returns:
            bool: True if sent successfully
        """
        if not self.token or not self.chat_id:
            return False

        try:
            url = self.API_URL.format(token=self.token)

            # Bandit B310 Safety Check
            if not url.startswith("https://"):
                raise ValueError("Insecure URL scheme")

            payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
            json_data = json.dumps(payload).encode("utf-8")

            request = urllib.request.Request(
                url, data=json_data, headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(request, timeout=10) as response:  # nosec B310
                result = json.loads(response.read().decode("utf-8"))
                return cast(bool, result.get("ok"))

        except Exception as e:
            self.logger.error(f"Telegram error: {str(e)}")
            return False
