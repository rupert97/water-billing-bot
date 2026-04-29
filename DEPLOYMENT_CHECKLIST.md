# Deployment Checklist

Complete this checklist to deploy Water Billing Tracker Bot to AWS Lambda.

## Prerequisites

- [ ] AWS Account created
- [ ] Telegram Bot created (@BotFather)
- [ ] Bot Token obtained
- [ ] Chat ID obtained

## Step 1: Prepare Telegram Credentials

- [ ] Telegram Bot Token: `___________________________________`
- [ ] Telegram Chat ID: `___________________________________`

**How to get these:**
1. Start @BotFather on Telegram
2. Use `/newbot` command
3. Save the bot token
4. Send a message to your bot
5. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
6. Find `"chat":{"id":XXXXX}` - that's your chat ID

## Step 2: Create DynamoDB Table

**Via AWS Console:**
- [ ] Go to DynamoDB → Tables → Create Table
- [ ] Table Name: `WaterBillState`
- [ ] Partition Key: `bill_id` (String)
- [ ] Billing Mode: On-demand
- [ ] Create Table
- [ ] Wait for table to be Active

**Via AWS CLI:**
```bash
aws dynamodb create-table \
  --table-name WaterBillState \
  --attribute-definitions AttributeName=bill_id,AttributeType=S \
  --key-schema AttributeName=bill_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

- [ ] Table created successfully

## Step 3: Create IAM Role for Lambda

**Via AWS Console:**
- [ ] Go to IAM → Roles → Create Role
- [ ] Service: Lambda
- [ ] Next: Permissions
- [ ] Create inline policy:
  - Copy contents from `lambda-iam-policy.json`
  - Paste into JSON editor
  - Review and Create
- [ ] Role Name: `lambda-water-billing-role`
- [ ] Create Role
- [ ] Note the Role ARN: `arn:aws:iam::ACCOUNT_ID:role/lambda-water-billing-role`

**Via AWS CLI:**
```bash
# Create role
aws iam create-role \
  --role-name lambda-water-billing-role \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{
      "Effect":"Allow",
      "Principal":{"Service":"lambda.amazonaws.com"},
      "Action":"sts:AssumeRole"
    }]
  }'

# Attach inline policy
aws iam put-role-policy \
  --role-name lambda-water-billing-role \
  --policy-name water-billing-policy \
  --policy-document file://lambda-iam-policy.json
```

- [ ] Role created and policy attached

## Step 4: Package Lambda Code

```bash
# In project root directory
zip -r lambda-deployment.zip src/ -x "*.pyc" "__pycache__/*"

# Verify contents
unzip -l lambda-deployment.zip | head -20
```

- [ ] File `lambda-deployment.zip` created (~5-10 KB)
- [ ] Contains `src/` directory with all modules

## Step 5: Create Lambda Function

**Via AWS Console:**
- [ ] Go to Lambda → Create Function
- [ ] Name: `water-billing-tracker`
- [ ] Runtime: Python 3.12
- [ ] Architecture: x86_64
- [ ] Permissions: Use role `lambda-water-billing-role` (from Step 3)
- [ ] Create Function
- [ ] Upload Code:
  - [ ] Actions → Upload from → .zip file
  - [ ] Upload `lambda-deployment.zip`
- [ ] General Configuration:
  - [ ] Memory: 256 MB
  - [ ] Timeout: 30 seconds
  - [ ] Ephemeral Storage: 512 MB (default)
- [ ] Save

**Via AWS CLI:**
```bash
aws lambda create-function \
  --function-name water-billing-tracker \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-water-billing-role \
  --handler src.lambda_handler.handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 30 \
  --memory-size 256 \
  --region us-east-1
```

- [ ] Lambda function created
- [ ] Handler set to: `src.lambda_handler.handler`

## Step 6: Set Environment Variables

**Via AWS Console:**
- [ ] Lambda → water-billing-tracker → Configuration → Environment Variables
- [ ] Add Variable:
  - Key: `TELEGRAM_BOT_TOKEN`
  - Value: `<Your Bot Token>`
- [ ] Add Variable:
  - Key: `TELEGRAM_CHAT_ID`
  - Value: `<Your Chat ID>`
- [ ] Save

**Via AWS CLI:**
```bash
aws lambda update-function-configuration \
  --function-name water-billing-tracker \
  --environment Variables="{TELEGRAM_BOT_TOKEN=YOUR_TOKEN,TELEGRAM_CHAT_ID=YOUR_CHAT_ID}" \
  --region us-east-1
```

- [ ] Environment variables set
- [ ] Values are confidential and secured

## Step 7: Create EventBridge Rule

**Via AWS Console:**
- [ ] Go to EventBridge → Rules → Create Rule
- [ ] Name: `water-billing-daily-trigger`
- [ ] Description: Daily trigger for water billing check
- [ ] Rule Type: Schedule
- [ ] Schedule Pattern: `cron(0 8 * * ? *)` (8 AM UTC daily)
  - OR use Rate: `1 day`
- [ ] Next: Select Target
- [ ] AWS Service: Lambda Function
- [ ] Function: `water-billing-tracker`
- [ ] Next → Create Rule

**Via AWS CLI:**
```bash
# Create rule
aws events put-rule \
  --name water-billing-daily-trigger \
  --schedule-expression "cron(0 8 * * ? *)" \
  --state ENABLED \
  --region us-east-1

# Add Lambda as target
aws events put-targets \
  --rule water-billing-daily-trigger \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:water-billing-tracker","RoleArn"="arn:aws:iam::YOUR_ACCOUNT_ID:role/service-role/EventBridgeRole" \
  --region us-east-1

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
  --function-name water-billing-tracker \
  --statement-id AllowExecutionFromEventBridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/water-billing-daily-trigger \
  --region us-east-1
```

- [ ] EventBridge rule created
- [ ] Rule scheduled for `cron(0 8 * * ? *)` (8 AM UTC daily)
- [ ] Lambda permission granted

## Step 8: Test Deployment

**Manual Test:**
- [ ] Go to Lambda → water-billing-tracker
- [ ] Click "Test"
- [ ] Create test event (use default)
- [ ] Click "Test" button
- [ ] Check Result (should show Status 200)
- [ ] Check CloudWatch Logs (should show execution)

**Via AWS CLI:**
```bash
aws lambda invoke \
  --function-name water-billing-tracker \
  --region us-east-1 \
  /tmp/lambda-response.json

cat /tmp/lambda-response.json
```

- [ ] Lambda executed successfully
- [ ] Response contains: `"statusCode": 200`

**Check CloudWatch Logs:**
- [ ] Go to Lambda → water-billing-tracker → Monitor → Logs
- [ ] Click on latest log stream
- [ ] Should show:
  - Water Billing Tracker Bot started
  - Similpay API query result
  - DynamoDB operations
  - Telegram notifications sent (or skipped)

- [ ] No error messages in logs
- [ ] Execution completed successfully

## Step 9: Verify Telegram Notifications

**Test Configuration:**
- [ ] Check Telegram for test message from your bot
- [ ] Verify message format and content

**Expected Behavior:**
- Day 1: New Bill Alert sent
- Day 2: No duplicate alert (state remembered)
- 2 days before due: Urgent reminder sent

- [ ] Telegram notifications working correctly

## Step 10: Monitor Ongoing Operations

**CloudWatch Monitoring:**
- [ ] Set up Lambda Alarms
  - [ ] Monitor for errors
  - [ ] Monitor invocation count
  - [ ] Monitor duration

**DynamoDB Monitoring:**
- [ ] Check Table size in DynamoDB Console
- [ ] Verify items are being created/updated

**Telegram Monitoring:**
- [ ] Receive daily notifications
- [ ] No duplicate messages on subsequent days
- [ ] Urgent reminder 2 days before due date

- [ ] All monitoring in place

## Troubleshooting

If issues occur, check:

1. **Lambda Logs:** CloudWatch Logs → /aws/lambda/water-billing-tracker
2. **DynamoDB Table:** Exists and is Active
3. **Environment Variables:** Bot token and chat ID correct
4. **IAM Role:** Has proper DynamoDB and CloudWatch permissions
5. **EventBridge Rule:** Enabled and properly configured

**Common Issues:**
- ❌ "No DynamoDB table" → Create `WaterBillState` table
- ❌ "Telegram auth failed" → Verify token and chat ID
- ❌ "Permission denied" → Check Lambda IAM role permissions
- ❌ "Connection timeout" → Check Lambda timeout (30 seconds)

## Deployment Complete!

Once all steps are checked, your Water Billing Tracker Bot is live!

✅ **Active Features:**
- Daily automated bill check (8 AM UTC)
- New bill alerts via Telegram
- Urgent reminders (2 days before due)
- Automatic state management
- Error logging and monitoring

**Cost:** Free (within AWS Free Tier)
**Status:** Running and monitoring water bills 24/7
