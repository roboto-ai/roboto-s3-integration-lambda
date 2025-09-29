# Roboto S3 Integration Lambda

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](LICENSE)

An AWS Lambda function that automatically imports files from S3 into [Roboto](https://www.roboto.ai/) datasets. This integration enables seamless data ingestion workflows where files uploaded to S3 are automatically organized into Roboto datasets with rich metadata, tags, and device associations.

**💡 Key Benefit:** Roboto imports create references to your S3 files in their original location—**no data duplication, no additional storage costs**. Your files stay exactly where they are while gaining all the power of Roboto's metadata, search, and organization capabilities.

## ⚠️ Important Requirements

**This Lambda function requires a registered bring-your-own-bucket (BYOB) integration:**

- Your S3 bucket must be registered as an **external read-only bring-your-own-bucket integration** with Roboto
- This feature is **only available for Premium organizations**
- To set up this integration, please contact **support@roboto.ai**

Without this integration configured, the Lambda function will not be able to import files into Roboto.

## 📋 Prerequisites

- AWS Account with Lambda and S3 access
- [Roboto](https://www.roboto.ai/) account and API key
- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

## 🛠️ Installation

### Clone the Repository

```bash
git clone https://github.com/roboto-ai/roboto-s3-integration-lambda.git
cd roboto-s3-integration-lambda
```

### Build the Lambda Deployment Package

```bash
./build-support/build.sh
```

This creates `build/lambda.zip` ready for deployment to AWS Lambda.

## 📦 Deployment

### 1. Create the Lambda Function

```bash
aws lambda create-function \
  --function-name roboto-s3-integration \
  --runtime python3.13 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_LAMBDA_ROLE \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://build/lambda.zip \
  --timeout 300 \
  --memory-size 512
```

### 2. Configure Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name roboto-s3-integration \
  --environment Variables="{ROBOTO_API_KEY=your_api_key,ROBOTO_ORG_ID=your_org_id}"
```

**Required Environment Variables:**
- `ROBOTO_API_KEY`: Your Roboto API key (required)
- `ROBOTO_ORG_ID`: Your Roboto organization ID (optional, required if you're in multiple orgs)

### 3. Configure S3 Event Trigger

Add an S3 event notification to trigger the Lambda function:

```bash
aws s3api put-bucket-notification-configuration \
  --bucket your-bucket-name \
  --notification-configuration file://s3-notification.json
```

Example `s3-notification.json`:

```json
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT:function:roboto-s3-integration",
      "Events": ["s3:ObjectCreated:*"]
    }
  ]
}
```

### 4. Grant S3 Access to Lambda

Ensure your Lambda execution role has permissions to read from S3:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

## 🎯 Usage

Once deployed, the Lambda function automatically processes files uploaded to your S3 bucket:

1. **Upload a file to S3**
   ```bash
   aws s3 cp mydata.bag s3://your-bucket-name/data/mydata.bag
   ```

2. **Lambda automatically**:
   - Detects the ObjectCreated event
   - Creates or finds an appropriate Roboto dataset
   - Imports the file as a reference (no data duplication!)
   - Adds metadata and tags
   - Logs the operation

3. **View in Roboto**: Your file is now available in Roboto with full metadata and search capabilities—while remaining in your S3 bucket

## 🔍 How It Works

When a file is uploaded to your S3 bucket, this Lambda function creates a **reference-based import** in Roboto:

- **No data duplication**: Files remain in your S3 bucket at their original location
- **No additional storage costs**: Roboto doesn't copy or store your data
- **Full Roboto capabilities**: Despite being external references, you get complete access to Roboto's metadata management, search, tagging, and organization features
- **Cost-efficient scaling**: Import terabytes of data without worrying about duplicate storage costs

This approach gives you the best of both worlds: your data stays in your infrastructure while you leverage Roboto's powerful data management platform.

---

Made with ❤️ by the Roboto team
