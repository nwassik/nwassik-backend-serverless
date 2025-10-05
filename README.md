# Nwassik Store

## Product Overview

**Nwassik Store** is a reverse marketplace platform designed to help users request products or services, which others (providers) can fulfill. It focuses especially on enabling people (example: in Tunisia) to request goods or services, including deliveries from abroad (example: from France), with, initially, offline cash payments. It empowers individuals to get better deals, avoid high local tariffs, and enables providers to earn money by fulfilling these requests.

## What Nwassik Store Allows

### Core Actions

- **Post a Request:**

  - A user posts a request for an item or service they want.
  - They specify where they want it delivered (drop-off location), and optionally, from where it should be picked up (pickup location).
  - A due date can also be specified by when the request should be completed.

- **Providers Respond:**

  - Other users see public requests.
  - They can offer to fulfill a posted request.

- **Private Chat Communication:**

  - Providers and Requesters can communicate privately through a messaging system to negotiate details.

- **Offline Payment:**

  - Payments happen offline, usually cash on delivery or during a physical handover of the item/service.

### Two Workflows Supported

- **Simple Delivery:**
  - Requester asks for something to be delivered to a place (drop-off only).
- **Pickup and Delivery:**
  - Requester asks for something to be picked up from a place and delivered to another.

## How It Works (Non-Technical Flow)

1. **User Registration/Login**
2. **Posting Requests:**
   - User writes what they need.
   - Optionally sets pickup and dropoff locations (with map based location search).
   - Sets due date if necessary.
3. **Viewing Requests:**
   - Providers browse public listings based on filters.
4. **Contact and Negotiation:**
   - Provider sends a chat message about the request.
   - Requester and Provider discuss details privately.
5. **Agreement and Delivery:**
   - They agree offline.
   - Provider fulfills the request.
6. **Cash Payment on Delivery:**
   - No online payments at this stage.
   - Subscription based model will be used on the providers side.

## Technical Architecture (Serverless Version)

### Technologies Used

| Layer                     | Technology / Service                           |
|---------------------------|------------------------------------------------|
| Backend API               | AWS Lambda (Python 3.13)                       |
| API Gateway               | AWS API Gateway (REST/WebSocket endpoints)     |
| Database                  | AWS DynamoDB (NoSQL, serverless)               |
| Storage                   | AWS S3 (file uploads, static assets)           |
| Messaging / Notifications | AWS SNS / SQS (event-driven notifications)     |
| Authentication            | AWS Cognito (user pools & JWT tokens)          |
| Deployment / IaC          | Serverless Framework / CloudFormation / Github |
| Monitoring / Logging      | AWS CloudWatch Logs & Metrics                  |
| Tracing                   | AWS X-Ray                                      |
| Secrets Management        | AWS Secrets Manager / Parameter Store          |

---

### Production (Serverless)

- Backend functions deployed as **AWS Lambda** functions.  
- REST and WebSocket APIs exposed via **AWS API Gateway**.  
- File storage handled by **AWS S3** for uploads and static assets.  
- Database is **AWS DynamoDB**, fully managed and serverless.  
- Event-driven workflows (notifications, chat updates) handled by **SNS/SQS**.  
- Authentication and user management via **AWS Cognito**.  
- Automatic scaling is handled by AWS; Lambdas scale per request, DynamoDB scales automatically.  
- HTTPS endpoints provided natively by API Gateway.  
- Monitoring, logging, and tracing through **CloudWatch Logs, Metrics, and AWS X-Ray**.  
- Secrets and environment variables managed via **AWS Secrets Manager / Parameter Store**.  
- CI/CD Pipelines (GitHub Actions):  
  - Install dependencies and Serverless Framework CLI  
  - Run tests for functions locally or in CI  
  - Deploy functions, resources, and stages to AWS  
  - Manage Lambda versions and aliases for safe production updates  
- Optional traffic shifting (blue/green or canary) handled via **Lambda aliases and deployment preferences**.
