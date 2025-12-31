# Nwassik Backend - Deployment Guide

## Prerequisites

- **AWS CLI** configured with appropriate credentials
- **Serverless Framework v4** installed globally (`npm install -g serverless`)
- **Docker** running (required for building Python dependencies on macOS)
- **Node.js** v18+ (for Serverless Framework)
- **Python 3.11** (for local development and testing)

## Environment Setup

### 1. Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd nwassik-backend-serverless

# Create and activate Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Node.js dependencies for Serverless plugins
npm install

# Copy environment file
cp .env.example .env

# Initialize local SQLite database (for testing)
python .local/init_db.py
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI (if not already done)
aws configure

# Verify your credentials
aws sts get-caller-identity
```

## Database Setup (Per Environment)

### Create RDS PostgreSQL Database

For each environment (dev, staging, prod), you need:

1. **RDS PostgreSQL Instance** (PostgreSQL 15.x)
   - Instance class: db.t3.micro (dev), db.t3.small (staging), db.t3.medium+ (prod)
   - Storage: 20GB minimum
   - Public accessibility: No
   - VPC: Same VPC as Lambda functions

2. **Database Credentials in Secrets Manager**
   - Secret name format: `rds!nwassik-{stage}-app-db-secret`
   - Secret value must include:
     ```json
     {
       "DATABASE_URL": "postgresql://user:password@host:5432/dbname"
     }
     ```

### Quick RDS Setup Script (Example for dev)

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier nwassik-dev-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username nwassik_admin \
  --master-user-password <SECURE_PASSWORD> \
  --allocated-storage 20 \
  --vpc-security-group-ids <YOUR_SECURITY_GROUP> \
  --db-subnet-group-name <YOUR_SUBNET_GROUP> \
  --backup-retention-period 7 \
  --no-publicly-accessible

# Create Secrets Manager secret
aws secretsmanager create-secret \
  --name "rds!nwassik-dev-app-db-secret" \
  --description "Database credentials for Nwassik dev environment" \
  --secret-string '{"DATABASE_URL":"postgresql://nwassik_admin:<PASSWORD>@<RDS_ENDPOINT>:5432/nwassik_dev"}'
```

## Deployment Steps

### Deploy to Dev Environment

```bash
# Ensure you're in the project root
cd nwassik-backend-serverless

# Deploy to dev
serverless deploy --stage dev

# Expected output:
# Service Information
# service: nwassik-store
# stage: dev
# region: eu-west-3
# stack: nwassik-store-dev
# endpoints:
#   GET - https://api-dev.nwassik.com/health
#   GET - https://api-dev.nwassik.com/requests
#   ...
```

### Deploy to Staging

```bash
serverless deploy --stage staging
```

### Deploy to Production

```bash
# Production deployment requires extra caution
serverless deploy --stage prod

# Always test critical endpoints after prod deployment
curl https://api.nwassik.com/health
```

## Database Migrations

After first deployment, initialize the database schema:

```bash
# SSH into a bastion host or use Lambda to run migrations
# For now, manual approach:

# 1. Connect to RDS from local machine (requires port forwarding or VPN)
psql postgresql://nwassik_admin:<PASSWORD>@<RDS_ENDPOINT>:5432/nwassik_dev

# 2. Run SQLAlchemy migrations
# (To be implemented: Use Alembic for migrations)
```

### Create Tables Manually (Temporary)

```python
# In Python shell with database access
from src.db.session import engine
from src.models.base import Base
from src.models.request import Request, BuyAndDeliverRequest, PickupAndDeliverRequest, OnlineServiceRequest
from src.models.favorite import Favorite

# Create all tables
Base.metadata.create_all(bind=engine)
```

## Testing Deployed Endpoints

### Health Check

```bash
curl https://api-dev.nwassik.com/health

# Expected response:
# {"status": "ok"}
```

### List Requests (Public)

```bash
curl https://api-dev.nwassik.com/requests

# Expected response:
# {
#   "requests": [],
#   "pagination": {
#     "next_cursor": null,
#     "has_more": false,
#     "limit": 20
#   }
# }
```

### Create Request (Requires Auth)

```bash
# First, get JWT token from Cognito (see Authentication section)
export JWT_TOKEN="<your-jwt-token>"

curl -X POST https://api-dev.nwassik.com/requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "type": "buy_and_deliver",
    "title": "iPhone 15 Pro from Paris",
    "description": "Need iPhone 15 Pro 256GB",
    "dropoff_latitude": 36.8065,
    "dropoff_longitude": 10.1815,
    "due_date": "2026-01-15T10:00:00Z"
  }'
```

## Rollback Deployment

```bash
# List recent deployments
serverless deploy list --stage dev

# Rollback to previous deployment
serverless rollback --stage dev --timestamp <timestamp>
```

## Monitoring

### View Logs

```bash
# Tail logs for all functions
serverless logs --stage dev --tail

# View logs for specific function
serverless logs --function createRequest --stage dev --tail

# View logs in CloudWatch (AWS Console)
# https://console.aws.amazon.com/cloudwatch/home?region=eu-west-3#logsV2:log-groups
```

### CloudWatch Metrics

Key metrics to monitor:
- **Lambda Invocations**: Number of requests per endpoint
- **Lambda Duration**: Response times
- **Lambda Errors**: Failed invocations
- **RDS CPU Utilization**: Database load
- **RDS Connections**: Active database connections

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```
Error: Could not connect to database
```

**Solution:**
- Verify RDS instance is running
- Check security group allows Lambda access
- Verify Secrets Manager secret exists and is accessible
- Ensure Lambda IAM role has `secretsmanager:GetSecretValue` permission

#### 2. Docker Build Errors (macOS)

```
Error: Unable to build Python dependencies
```

**Solution:**
- Ensure Docker is running
- Clear Serverless cache: `rm -rf .serverless node_modules/.cache`
- Rebuild: `serverless deploy --stage dev`

#### 3. CORS Errors

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution:**
- Verify origin is in `corsConfig` (serverless.yaml)
- Check API Gateway CORS settings in AWS Console

## Cost Estimation

### Dev Environment (Light Usage)
- **Lambda**: ~$1-5/month (1M requests)
- **RDS db.t3.micro**: ~$15/month
- **API Gateway**: ~$3.50/month (1M requests)
- **Secrets Manager**: ~$0.40/month
- **Total**: ~$20-25/month

### Production Environment (Moderate Usage)
- **Lambda**: ~$10-20/month
- **RDS db.t3.medium**: ~$60/month
- **API Gateway**: ~$10-15/month
- **CloudWatch Logs**: ~$5/month
- **Total**: ~$85-100/month

## Security Checklist

- [ ] RDS is not publicly accessible
- [ ] Database credentials stored in Secrets Manager
- [ ] IAM roles follow least privilege principle
- [ ] API Gateway has CORS properly configured
- [ ] Cognito user pool configured for authentication
- [ ] CloudTrail enabled for audit logging
- [ ] Encryption at rest enabled for RDS
- [ ] VPC endpoints configured for AWS services

## Next Steps

1. **Set up Cognito User Pool** for authentication
2. **Configure custom domain** (api.nwassik.com)
3. **Implement Alembic migrations** for schema versioning
4. **Set up CI/CD pipeline** (GitHub Actions)
5. **Add CloudWatch alarms** for critical metrics
6. **Enable X-Ray tracing** for debugging
7. **Implement automated testing** in CI/CD

## Support

For issues or questions:
- Check CloudWatch Logs first
- Review [README.md](README.md) for project overview
- Contact: [Your contact information]