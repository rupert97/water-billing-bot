"""Similpay API client for querying water bills"""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

logger = logging.getLogger()


class SimilpayClient:
    """Client for interacting with Similpay API"""

    HOST = "www.similpay.com"
    AUTH_PATH = "/back_commerce/getAuthorizationToken"
    QUERY_PATH = "/back_commerce/api/transaction/query"
    # These should ideally be passed in or loaded from env vars
    PROJECT_ID = "18590"
    USER_REFERENCE = "2128388"

    def __init__(self):
        """Initialize Similpay client"""
        self.auth_url = f"https://{self.HOST}{self.AUTH_PATH}"
        self.query_url = f"https://{self.HOST}{self.QUERY_PATH}"
        self.logger = logger

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        try:
            req = urllib.request.Request(self.auth_url, data=encoded_payload, headers=headers)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                return result.get("access_token")

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            logger.error(f"Auth failed with {e.code}. Response: {error_body}")
            return None

        except Exception as e:
            logger.error(f"Failed to get auth token: {e}")
            return None

    def query_bills(self) -> Optional[Dict]:
        """
        Query Similpay API for water bills.
        Matches the Similpay specific payload and structure.
        """
        try:
            token = self._get_token()
            if not token:
                return None

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.similpay.com/",
                "Origin": "https://www.similpay.com",
            }
            # Payload keys must match the API's expected 'reference' and 'project'
            payload = {"reference": self.USER_REFERENCE, "project": self.PROJECT_ID}

            json_data = json.dumps(payload).encode("utf-8")

            request = urllib.request.Request(self.query_url, data=json_data, headers=headers)

            self.logger.info(f"Querying Similpay for reference {self.USER_REFERENCE}")

            with urllib.request.urlopen(request, timeout=10) as response:
                response_data = response.read().decode("utf-8")
                result = json.loads(response_data)
                logger.info(f"Query successful. Code: {result.get('Code')}")
                return result

        except Exception as e:
            self.logger.error(f"Error querying Similpay API: {str(e)}")
            return None

    def extract_unpaid_bills(self, api_response: Dict) -> List[Dict]:
        """
        Extracts bill info only if Code is NOT "3" (Paid)
        and Data contains a valid amount.
        """
        if not api_response:
            return []

        # Check for the "Already Paid" code
        code = str(api_response.get("Code"))
        if code == "3":
            self.logger.info("Bill already paid (Code 3).")
            return []

        data = api_response.get("Data", {})

        # In this API, 'amount' is usually only populated if a bill is pending
        amount = data.get("amount")
        if amount and amount > 0:
            # We wrap it in a list to keep your existing downstream logic consistent
            bill_info = {
                "amount": amount,
                "dueDate": data.get("expirationDate"),
                "reference": data.get("reference") or self.USER_REFERENCE,
            }
            self.logger.info(f"Unpaid bill found: {amount}")
            return [bill_info]

        return []

    def generate_bill_id(self, bill: Dict) -> str:
        """
        Generates a unique ID based on the expiration date
        to prevent duplicate notifications in the same month.
        """
        due_date = bill.get("dueDate", "")
        if due_date and "0001-01-01" not in due_date:
            # "2026-05-15T00:00:00" -> "water_bill_2026_05"
            date_part = due_date.split("T")[0]
            parts = date_part.split("-")
            if len(parts) >= 2:
                return f"water_bill_{parts[0]}_{parts[1]}"

        return f"water_bill_{bill.get('amount', 'unknown')}"
