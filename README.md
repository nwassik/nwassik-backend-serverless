# Nwassik Store

## Product Overview

**Nwassik Store** is a reverse marketplace platform designed to help users request products or services, which others (providers) can fulfill. It focuses especially on enabling people (example: in Tunisia) to request goods or services, including deliveries from abroad (example: from France), with, initially, offline cash payments between both parties (or free if accepted). It empowers individuals to get better deals, avoid high local tariffs, and enables providers to earn/save money when traveling by fulfilling these requests.

## What Nwassik Store Allows

### Core Actions

- **Login & Register**
  - Users can login & register via email/password and via 2 social media platforms: facebook + google

- **Post a Request:**

  - A user posts a request for an item or service
  - Three request options are available:
    - Buy & Deliver service
      - Users specify what items they want bought and to where should be delivered
    - Pickup & Deliver service
      - Users specify from where items should be picked, and to where should be delivered
    - Online Service
      - Users specify what online service they need (Netflix, plane ticket,..) and meetup location for transaction
  - A due date can also be specified informing when the request should be completed.

- **Viewing Requests:**
  - Providers browse public listings based on filters (request type, location, due date, ..)

- **Providers Respond:**

  - Other users (providers) see public requests.
  - They can offer to fulfill a posted request by sending a chat message
  - Requester and Provider discuss details privately

- **Private Chat Communication:**

  - Providers and Requesters can communicate privately through a messaging system to negotiate details
  - They agree offline

- **Offline Payment:**

  - Payments happen offline, usually cash on delivery or during a physical handover of the item/service.
  - No online payments at this stage
  - Subscription based model in the future will be used on the providers side

## Features To Add

- **Trust, Safety & Reputation:** Users can report inappropriate or fraudulent requests/offers.  
- **Ratings & Completion Feedback:** Allow requesters and providers to rate each other, even if payment occurs offline.  
- **Verification Levels (Optional Future):** Users can verify their phone, email, or ID to increase trust, with a blue mark for verified users.  
- **Notification System:** Notify users when a new request is posted and allow subscription to filters (service type, location, date, etc.).  
- **Chat:** Built-in messaging between requesters and providers.  
- **Feedback:** Users can provide feedback with text and image for me  
- **Current Offers Page:** Separate page displaying all current offers.  
- **Request Images:** Allow users to upload a maximum of two images per request.  
- **Money Exchange Officer:** Add a trusted fund handler for secure money exchange and transactions.  

## Technical Architecture

### Technologies Used

| Layer                            | Technology / Service                           | Other notes                                                              |
|----------------------------------|------------------------------------------------|--------------------------------------------------------------------------|
| Backend API                      | AWS Lambda (Python 3.13)                       | -                                                                        |
| API Gateway                      | AWS API Gateway (REST endpoints)               | Initially, chat part will poll messages but later will be websocket      |
| App Database                     | AWS RDS/ Aurora DSQL                           | -                                                                        |
| Chat Database                    | AWS DynamoDB                                   | -                                                                        |
| Storage                          | AWS S3 (file uploads, static assets)           | Mainly to upload user profile images and Requests files upload           |
| Chat Messaging / Notifications   | AWS SNS / SQS (event-driven notifications)     | -                                                                        |
| Authentication & User management | Authgear/AWS Cognito (user pools & JWT tokens) | -                                                                        |
| App Deployment                   | Serverless Framework (CloudFormation)          | -                                                                        |
| Infra Deployment / IaC           | Terraform                                      | Mainly to setup persistance layer (RDS + DynamoDB) along with S3 buckets |
| Monitoring / Logging             | AWS CloudWatch Logs & Metrics                  | -                                                                        |
| Tracing                          | AWS X-Ray                                      | -                                                                        |
| Secrets Management               | AWS Secrets Manager / Parameter Store          | To store Secrets and environment variables                               |
