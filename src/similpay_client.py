"""Similpay API client for querying water bills"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, cast

logger = logging.getLogger()


class SimilpayClient:
    """Client for interacting with Similpay API"""

    HOST = "www.similpay.com"
    AUTH_PATH = "/back_commerce/getAuthorizationToken"
    QUERY_PATH = "/back_commerce/api/transaction/query"
    PROJECT_ID = "18590"

    def __init__(self) -> None:
        """Initialize Similpay client"""
        self.auth_url = f"https://{self.HOST}{self.AUTH_PATH}"
        self.query_url = f"https://{self.HOST}{self.QUERY_PATH}"
        self.logger = logger
        user_ref = os.environ.get("SIMILPAY_USER_REFERENCE")
        if not user_ref:
            raise ValueError("SIMILPAY_USER_REFERENCE environment variable is not set")
        self.USER_REFERENCE = user_ref

    def _safe_urlopen(
        self,
        url: str,
        data: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
    ) -> Any:
        """Helper to satisfy Bandit B310 by verifying https scheme"""
        if not url.startswith("https://"):
            raise ValueError(f"Forbidden URL scheme: {url}")

        req = urllib.request.Request(url, data=data, headers=headers or {})
        return urllib.request.urlopen(req, timeout=timeout)  # nosec B310

    def _get_token(self) -> Optional[str]:
        """Authenticates and returns a fresh Bearer token"""
        payload_dict = {
            "username": "siteFront",
            "password": "cHJ1ZWJhc3NpdGVwYXNhcmVsYQ==",
            "grant_type": "password",
        }

        encoded_payload = urllib.parse.urlencode(payload_dict).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0",
        }

        try:
            with self._safe_urlopen(
                self.auth_url, data=encoded_payload, headers=headers
            ) as response:
                result = json.loads(response.read().decode())
                return cast(Optional[str], result.get("access_token"))

        except Exception as e:
            logger.error(f"Failed to get auth token: {e}")
            return None

    def query_bills(self) -> Optional[Dict[str, Any]]:
        """Query Similpay API for water bills."""
        try:
            token = self._get_token()
            if not token:
                return None

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.similpay.com/",
            }
            payload = {"reference": self.USER_REFERENCE, "project": self.PROJECT_ID}
            json_data = json.dumps(payload).encode("utf-8")

            with self._safe_urlopen(self.query_url, data=json_data, headers=headers) as response:
                response_data = response.read().decode("utf-8")
                result = json.loads(response_data)
                return cast(Dict[str, Any], result)

        except Exception as e:
            self.logger.error(f"Error querying Similpay API: {str(e)}")
            return None

    def extract_unpaid_bills(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not api_response:
            return []

        code = str(api_response.get("Code"))
        if code == "3":
            return []

        data = cast(Dict[str, Any], api_response.get("Data", {}))
        amount = data.get("amount")

        if amount and float(amount) > 0:
            return [
                {
                    "amount": amount,
                    "dueDate": data.get("expirationDate"),
                    "reference": data.get("reference") or self.USER_REFERENCE,
                }
            ]
        return []

    def generate_bill_id(self, bill: Dict[str, Any]) -> str:
        due_date = str(bill.get("dueDate", ""))
        if due_date and "0001-01-01" not in due_date:
            date_part = due_date.split("T")[0]
            parts = date_part.split("-")
            if len(parts) >= 2:
                return f"water_bill_{parts[0]}_{parts[1]}"
        return f"water_bill_{bill.get('amount', 'unknown')}"
