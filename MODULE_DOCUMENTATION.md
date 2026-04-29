# Module Documentation

Quick reference guide for understanding the codebase structure.

## Core Modules

### `src/lambda_handler.py`
**Main entry point for AWS Lambda execution**

- `handler(event, context)` - Triggered by EventBridge daily
  - Initializes all components
  - Orchestrates the bill processing workflow
  - Returns execution result

**Returns:**
```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "bills_found": 1,
    "new_alerts_sent": 1,
    "urgent_alerts_sent": 0,
    "errors": []
  }
}
```

---

### `src/similpay_client.py`
**Queries the Similpay water utility API**

**Class:** `SimilpayClient`

**Methods:**
- `query_bills()` - Sends POST request to Similpay API
  - Returns raw API response or None on failure
  - Handles connection errors and JSON parsing

- `extract_unpaid_bills(api_response)` - Filters unpaid bills
  - Returns list of bills with status="unpaid"
  - Handles malformed responses gracefully

- `generate_bill_id(bill)` - Creates unique bill identifier
  - Prefers bill ID from API: `water_bill_123`
  - Falls back to date-based: `water_bill_2026_05`

**API Endpoint:**
```
POST https://www.similpay.com/back_commerce/api/transaction/query
Content-Type: application/json

{
  "projectId": "18590",
  "userReference": "2128388"
}
```

---

### `src/state_manager.py`
**Manages bill notification state in DynamoDB**

**Class:** `StateManager`

**Methods:**
- `ensure_table_exists()` - Creates table if needed
- `get_bill_state(bill_id)` - Retrieves state or None
- `create_bill_state(bill_id)` - Creates new state record
- `mark_new_bill_notified(bill_id)` - Sets notified_new=True
- `mark_urgent_notified(bill_id)` - Sets urgent_sent=True

**DynamoDB Table Schema:**
```
Table: WaterBillState
Partition Key: bill_id (String)

Item Example:
{
  "bill_id": "water_bill_2026_05",
  "notified_new": true,
  "urgent_sent": false
}
```

**State Tracking Logic:**
- New bill discovered → `notified_new=False`
- Alert sent → `notified_new=True` (prevent duplicate alerts)
- 2 days before due → Send urgent reminder
- Urgent sent → `urgent_sent=True` (prevent duplicate urgent)

---

### `src/telegram_notifier.py`
**Sends notifications via Telegram Bot API**

**Class:** `TelegramNotifier`

**Methods:**
- `send_new_bill_alert(amount, due_date)` - New bill notification
  - Format: `💧 New Water Bill Alert`
  - Includes amount and due date

- `send_urgent_reminder(amount, due_date, days_left)` - Urgent payment reminder
  - Format: `⚠️ URGENT: Water Bill Due Soon`
  - Includes urgency countdown

- `send_message(text)` - Generic message sender
  - Supports HTML formatting
  - Returns True on success, False on failure

**Configuration (Environment Variables):**
```
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF..."
TELEGRAM_CHAT_ID = "987654321"
```

**Telegram Bot API:**
```
POST https://api.telegram.org/bot{token}/sendMessage
Content-Type: application/json

{
  "chat_id": "987654321",
  "text": "Message text (supports HTML)",
  "parse_mode": "HTML"
}
```

---

### `src/bill_processor.py`
**Core business logic - orchestrates notifications**

**Class:** `BillProcessor`

**Methods:**
- `process_bills()` - Main workflow
  1. Ensure DynamoDB table exists
  2. Query Similpay API
  3. Extract unpaid bills
  4. For each bill:
     - Check state
     - Send new bill alert (if not yet notified)
     - Check urgency (2 days before due)
     - Send urgent reminder (if needed)
     - Update state
  5. Return execution results

**Returns:**
```json
{
  "success": true/false,
  "bills_found": 1,
  "new_alerts_sent": 1,
  "urgent_alerts_sent": 0,
  "errors": []
}
```

**Configuration:**
- `URGENT_THRESHOLD_DAYS = 2` - Days before due to send urgent

---

### `src/utils.py`
**Utility functions**

**Functions:**
- `safe_json_loads(data, default)` - Safe JSON parsing
- `format_currency(amount)` - Format as `$XX.XX`
- `format_date(date_str)` - Convert to readable format
- `safe_get(data, *keys, default)` - Nested dict access

---

## Data Flow

```
EventBridge (Daily 8 AM UTC)
        ↓
Lambda Handler
        ↓
SimilpayClient.query_bills()
        ↓
Extract unpaid bills
        ↓
For each bill:
  ├─ StateManager.get_bill_state()
  │
  ├─ If new: TelegramNotifier.send_new_bill_alert()
  │       └─ StateManager.mark_new_bill_notified()
  │
  └─ If 2 days before due: TelegramNotifier.send_urgent_reminder()
          └─ StateManager.mark_urgent_notified()
        ↓
Return execution results
        ↓
CloudWatch Logs
```

---

## Testing

**Test Coverage:**
- `test_similpay_client.py` - API client tests
- `test_state_manager.py` - DynamoDB state management
- `test_telegram_notifier.py` - Notification sending
- `test_bill_processor.py` - Business logic and workflows

**Run Tests:**
```bash
# All tests
python -m unittest discover -s tests -p "test_*.py" -v

# Specific module
python -m unittest tests.test_bill_processor -v

# Specific test
python -m unittest tests.test_bill_processor.TestBillProcessor.test_process_bills_new_bill_alert -v
```

---

## Error Handling

### API Failures
- Similpay API connection errors → Logged, graceful exit
- Invalid JSON response → Logged, return empty list
- Missing fields in response → Logged, continue

### DynamoDB Failures
- Table not found → Create table automatically
- Connection errors → Logged, return False
- Update failures → Logged, skip state update

### Telegram Failures
- Invalid token/chat ID → Logged, return False
- Bot blocked → Logged, return False
- Network errors → Logged, return False

### Graceful Degradation
- If Telegram fails, DynamoDB state still updates
- If DynamoDB fails, notifications still attempted
- All errors logged to CloudWatch

---

## Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Yes | `123456:ABC-DEF1234...` |
| `TELEGRAM_CHAT_ID` | Yes | `987654321` |
| `AWS_REGION` | No (default) | `us-east-1` |

---

## Deployment Artifacts

- `lambda-deployment.zip` - Deployable package
- `lambda-iam-policy.json` - Required IAM permissions
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step setup guide

---

## Configuration Files

- `water_billing_bot_prd.md` - Product requirements
- `README.md` - Full documentation
- `requirements.txt` - Dependencies reference
- `DEPLOYMENT_CHECKLIST.md` - AWS setup steps

---

## Performance Characteristics

**Execution Time:** ~2-5 seconds
- Similpay API query: ~1-2 seconds
- DynamoDB operations: ~500ms
- Telegram API: ~500ms (per message)

**Memory Usage:** ~50-100 MB (Lambda allocated: 256 MB)
**Cold Start:** ~1-2 seconds (first invocation)
**Network:** ~100KB outbound (1-2 API calls)

**Cost:** Free (AWS Free Tier)
- Lambda: 30 invocations/month free
- DynamoDB: 25GB storage, 25 read/write units free
- Data transfer: 1GB/month free

---

## Known Limitations

1. Uses in-memory state for DynamoDB (production should use persistent DB)
2. Similpay API endpoint not documented - assumes JSON format
3. Single Telegram chat target (no group notifications)
4. UTC only for cron scheduling (8 AM UTC)

---

For detailed API documentation, see `water_billing_bot_prd.md`.
