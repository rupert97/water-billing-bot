# Water Billing Tracker Bot

A serverless automation tool that bridges the gap between utility payment portals and personal financial management. This AWS Lambda application eliminates manual portal checks by notifying you via Telegram when a water bill is generated and sending urgent reminders before the deadline.

## Features

✅ **Automated Monitoring** - Queries Similpay API daily without user intervention
✅ **Proactive Notifications** - Push alerts via Telegram when bills are generated
✅ **Smart State Management** - Tracks notification history to prevent spam
✅ **Urgent Reminders** - Sends high-priority alerts 2 days before due date
✅ **Cost Efficient** - Runs on AWS Free Tier ($0/month)
✅ **Zero External Dependencies** - Uses only Python standard library + AWS Lambda pre-installed boto3

## Architecture

```
EventBridge (Daily Schedule)
        ↓
AWS Lambda (Python 3.12)
        ↓
┌───────────────────────────────────────────┐
│ 1. Query Similpay API                      │
│ 2. Extract unpaid bills                    │
│ 3. Check DynamoDB state                    │
│ 4. Send Telegram notifications             │
│ 5. Update state (prevent duplicates)       │
└───────────────────────────────────────────┘
        ↓
DynamoDB (State Tracking)  +  Telegram (Notifications)
```

## Project Structure

```
.
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── lambda_handler.py           # Main Lambda entry point
│   ├── similpay_client.py          # Similpay API client
│   ├── state_manager.py            # DynamoDB state management
│   ├── telegram_notifier.py        # Telegram Bot API integration
│   ├── bill_processor.py           # Core business logic
│   └── utils.py                    # Utility functions
├── tests/
│   ├── test_similpay_client.py
│   ├── test_state_manager.py
│   ├── test_telegram_notifier.py
│   ├── test_bill_processor.py
│   └── __init__.py
├── water_billing_bot_prd.md        # Product Requirements Document
├── requirements.txt                 # Dependencies documentation
└── README.md                        # This file
```

## Setup Instructions

### Prerequisites

- Python 3.12
- AWS Account (Free Tier eligible)
- Telegram Bot Token
- Similpay Account

### 1. Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Save your **Bot Token** (example: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. Get your **Chat ID**:
   - Send a message to your bot
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

### 2. Deploy to AWS Lambda

#### Option A: AWS Console (Manual)

1. **Create DynamoDB Table**
   - Go to DynamoDB → Create Table
   - Table name: `WaterBillState`
   - Partition key: `bill_id` (String)
   - Billing mode: On-demand
   - Create table

2. **Create Lambda Function**
   - Go to Lambda → Create Function
   - Name: `water-billing-tracker`
   - Runtime: Python 3.12
   - Create function

3. **Package Code**
   ```bash
   # From project root
   zip -r lambda-deployment.zip src/ -x "*.pyc" "__pycache__/*"
   ```

4. **Upload Code**
   - Upload `lambda-deployment.zip` to Lambda
   - Set handler: `src.lambda_handler.handler`
   - Set timeout: 30 seconds
   - Set memory: 256 MB

5. **Configure Environment Variables**
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `TELEGRAM_CHAT_ID`: Your chat ID

6. **Create EventBridge Rule**
   - Go to EventBridge → Create Rule
   - Name: `water-billing-daily-trigger`
   - Schedule: `cron(0 8 * * ? *)` (8 AM daily, UTC)
   - Target: Lambda function `water-billing-tracker`
   - Create rule

#### Option B: AWS CLI (Automated)

```bash
# 1. Create DynamoDB table
aws dynamodb create-table \
  --table-name WaterBillState \
  --attribute-definitions AttributeName=bill_id,AttributeType=S \
  --key-schema AttributeName=bill_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# 2. Package code
zip -r lambda-deployment.zip src/ -x "*.pyc" "__pycache__/*"

# 3. Create Lambda function
aws lambda create-function \
  --function-name water-billing-tracker \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-dynamodb-role \
  --handler src.lambda_handler.handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{TELEGRAM_BOT_TOKEN=YOUR_TOKEN,TELEGRAM_CHAT_ID=YOUR_CHAT_ID}" \
  --region us-east-1

# 4. Create EventBridge rule
aws events put-rule \
  --name water-billing-daily-trigger \
  --schedule-expression "cron(0 8 * * ? *)" \
  --state ENABLED \
  --region us-east-1

# 5. Add Lambda as target
aws events put-targets \
  --rule water-billing-daily-trigger \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:water-billing-tracker" \
  --region us-east-1
```

### 3. Grant Lambda Permissions

**DynamoDB Access:**
Create an IAM role with this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:CreateTable"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/WaterBillState"
    }
  ]
}
```

## Testing

### Run All Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run Specific Test File

```bash
python -m unittest tests.test_bill_processor -v
```

### Run Specific Test

```bash
python -m unittest tests.test_similpay_client.TestSimilpayClient.test_query_bills_success -v
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | `123456789` |

## Data Flow

1. **EventBridge** triggers Lambda daily at 8 AM (UTC)
2. **SimilpayClient** queries Similpay API for bills
3. **BillProcessor** extracts unpaid bills
4. **StateManager** checks DynamoDB for notification history
5. **TelegramNotifier** sends alerts if needed
6. **StateManager** updates DynamoDB to mark notifications sent

## Notification Types

### New Bill Alert
Sent when an unpaid bill is first discovered.

```
💧 New Water Bill Alert

Amount: $45.50
Due Date: May 15, 2026

Please log in to Similpay to pay your bill.
```

### Urgent Reminder
Sent when a bill is still unpaid and 2 days remain until due date.

```
⚠️ URGENT: Water Bill Due Soon

Amount: $45.50
Due Date: May 15, 2026
Days Left: 2

⏰ Please pay your bill immediately to avoid late fees!
```

## Troubleshooting

### Lambda Execution Fails
- Check CloudWatch Logs: Lambda → Functions → water-billing-tracker → Logs
- Verify Telegram token and chat ID are correctly set
- Ensure DynamoDB table exists and Lambda has permissions

### No Notifications Received
- Check Telegram token validity in environment variables
- Verify chat ID is correct
- Check Similpay API response in CloudWatch Logs
- Test with manual Lambda invocation: `aws lambda invoke --function-name water-billing-tracker /tmp/output.txt`

### Bill State Not Updating
- Verify DynamoDB table exists: `WaterBillState`
- Check Lambda IAM role has DynamoDB permissions
- Verify table has no encryption issues

## Cost Estimation

**Monthly Operating Cost: $0-1** (AWS Free Tier)

- **Lambda**: 1 invocation/day × 30 days = 30 invocations (always free)
- **DynamoDB**: ~1KB per bill × 1 month = negligible (25GB free)
- **Data Transfer**: < 1MB/month (1GB free)

## Security Considerations

✅ **No Public Endpoints** - Purely event-driven, no API Gateway
✅ **Credentials in Environment Variables** - Secured by AWS
✅ **No Hardcoded Secrets** - All sensitive data in environment
✅ **Read-Only to Similpay** - Only queries API, doesn't modify
✅ **Limited DynamoDB Access** - Function can only access WaterBillState table

## Future Enhancements

- [ ] Multiple Telegram groups/chats support
- [ ] SMS notifications as fallback
- [ ] Email summaries
- [ ] Web dashboard for bill history
- [ ] Historical bill tracking and analytics
- [ ] Support for multiple utilities
- [ ] Scheduled payment integration

## Support

For issues or feature requests, please check the CloudWatch Logs or verify:

1. Telegram bot token validity
2. DynamoDB table exists
3. Lambda execution role permissions
4. Similpay API connectivity

## License

This is a sample project for educational purposes.
