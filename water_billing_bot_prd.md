# PRD: Automated Water Utility Billing Tracker (AWS Edition)

## 1. Product Overview
The **Water Billing Tracker Bot** is a serverless automation tool designed to bridge the gap between utility payment portals and personal financial management. It eliminates the need for manual portal checks by notifying the user via Telegram when a bill is generated and providing urgent reminders before the deadline.

## 2. Problem Statement
The water utility (Similpay/EMSERCHIA) lacks direct bank integration for scheduled payments. Users must manually visit a query-based portal to check for balance and deadlines. This leads to:
* High risk of late fees due to forgotten manual checks.
* Friction in managing household expenses.
* Inconvenience of repetitive manual data entry.

## 3. Goals & Objectives
* **Automated Monitoring:** Query the Similpay API daily without user intervention.
* **Proactive Notification:** Push alerts via Telegram when a bill is ready or pending.
* **Zero-Spam Logic:** Use state management to ensure only unique alerts are sent.
* **Cost Efficiency:** Leverage AWS Free Tier (Lambda, EventBridge, DynamoDB) for $0/month operation.

## 4. Technical Architecture

### 4.1. System Components
* **Scheduler:** AWS EventBridge (Cron) triggers the workflow daily.
* **Compute:** AWS Lambda running Python 3.12 (standard libraries only).
* **State Store:** Amazon DynamoDB to track notification history per billing cycle.
* **Messaging:** Telegram Bot API for real-time delivery.

### 4.2. API Integration Specifications
* **Host:** `www.similpay.com`
* **Path:** `/back_commerce/api/transaction/query`
* **Method:** POST
* **Static Project ID:** `18590`
* **User Reference:** `2128388`

## 5. User Stories
| ID | Requirement | Success Criteria |
|:---|:---|:---|
| US1 | **Bill Discovery** | If a bill is unpaid, user receives a Telegram message with the amount and due date. |
| US2 | **State Tracking** | The system remembers that a "New Bill" alert was sent and does not repeat it the next day. |
| US3 | **Urgency Logic** | If a bill is still unpaid 2 days before the due date, a high-priority "Urgent" message is sent. |

## 6. Data Schema (DynamoDB)
* **Table Name:** `WaterBillState`
* **Partition Key:** `bill_id` (String) - e.g., `water_bill_2026_04`
* **Attributes:**
    * `notified_new` (Boolean)
    * `urgent_sent` (Boolean)

## 7. Security & Privacy
* **Secret Management:** Telegram Tokens and Account References are stored in Lambda Environment Variables.
* **Encapsulation:** No public endpoints; the system is purely event-driven and internal.

---

## Implementation Status

✅ **Completed**
- Core Lambda handler with event processing
- Similpay API client (HTTP POST integration)
- State management (DynamoDB operations)
- Telegram notification service (Bot API integration)
- Bill processing logic (state tracking + notification logic)
- Comprehensive test suite (50+ test cases)
- AWS deployment documentation and CLI scripts

**See README.md for complete deployment instructions.**
