## ✅ Current Implementation Status

### What's Working Now

#### Backend Infrastructure

- ✅ Serverless Framework configuration (AWS Lambda + API Gateway)
- ✅ SQLAlchemy ORM with support for PostgreSQL (RDS: production) and SQLite (local dev)
- ✅ AWS Secrets Manager integration for database credentials
- ✅ Environment-aware configuration (cloud vs local)
- ✅ Pydantic validation for all inputs

#### Database Schema

- ✅ Polymorphic request model (3 types with separate tables)
- ✅ Favorites/bookmarks system
- ✅ UUID primary keys throughout
- ✅ Cascade deletion handling

#### API Endpoints (10 total)

- ✅ Health check endpoint
- ✅ Request CRUD operations (create, read, update, delete, list)
- ✅ User-specific request listing
- ✅ Favorites CRUD operations (create, delete, list)
- ✅ JWT authentication via AWS Cognito
- ✅ Authorization checks (users can only modify their own resources)

#### Business Logic

- ✅ Request quota enforcement (max 20 requests per user)
- ✅ Request type validation (Buy & Deliver, Pickup & Deliver, Online Service)
- ✅ Geolocation coordinate validation
- ✅ Due date validation (timezone-aware, must be in future)
- ✅ Idempotent operations (favorites, deletes)

#### Code Quality

- ✅ Ruff linter configuration (strict rules)
- ✅ Repository pattern for data access
- ✅ Separation of concerns (handlers, repositories, models, schemas)
- ✅ Context managers for database sessions

### What's Not Yet Implemented

- ⏳ User profile management
- ⏳ Image uploads (profile pictures, request images)
- ⏳ Chat/messaging system
- ⏳ Notification system (email, SMS, push)
- ⏳ Content moderation (text and images)
- ⏳ API rate limiting and throttling
- ⏳ Ratings and reviews
- ⏳ Trust and safety features
- ⏳ Comprehensive testing (unit, integration, E2E)
- ⏳ CI/CD pipeline
- ⏳ Monitoring and alerting
- ⏳ Distributed tracing (X-Ray integration)

---






## 🚀 Core Features

### 1. User Authentication

- Registration and login using:
  - Email/password
  - Social login: Facebook + Google  
- JWT token-based authentication
- AWS Cognito user pool management

### 2. Request Management

#### Request Types

##### Buy & Deliver Service

- User specifies: item description, delivery location (lat/lng)
- Provider purchases item abroad and delivers to requester
- Use case: "Buy iPhone 15 in France, deliver to Tunis"

##### Pickup & Deliver Service

- User specifies: pickup location (lat/long), delivery location (lat/long)
- Provider picks up package from one location and delivers to another
- Use case: "Pickup package from Paris post office, deliver to Tunis"

##### Online Service

- User specifies: service needed, meetup location for transaction (lat/long)
- Provider purchases digital service (Netflix, flight tickets, etc.)
- Use case: "Subscribe to Spotify Premium, meet at café for cash exchange"

### 3. Favorites/Bookmarks

- Users can save requests they're interested in
- Unique constraint per user-request pair (no duplicates)
- Cascade deletion when request is deleted
- Quota: max 100 favorites per user

### 4. Public Request Browsing

- All requests are publicly viewable
- Filtering by request type (planned)
- Geolocation-based filtering (planned)
- Due date filtering (planned)

---

## 🔮 Planned Features

### Phase 1: Content Safety & Moderation

#### Automated Content Moderation Pipeline

##### Text Moderation

- Scan request titles and descriptions for profanity, hate speech, inappropriate content
- Use AWS Comprehend for sentiment analysis and entity detection
- Auto-flag suspicious content for manual review

##### Image Moderation

- Scan uploaded images for inappropriate content (nudity, violence, explicit material)
- Use AWS Rekognition for image analysis
- Detect faces, objects, text in images
- Auto-reject unethical images before storage

##### Workflow (using Step Functions)

1. User submits request with text + images
2. Lambda triggers Step Functions workflow
3. Parallel execution:
   - Comprehend analyzes text
   - Rekognition analyzes images
4. Decision logic:
   - Auto-approve if all checks pass
   - Auto-reject if high confidence violation
   - Queue for human review if uncertain
5. SNS notifies user of decision
6. SQS queue for manual moderation (with DLQ)

---

### Phase 2: Image Processing & Storage

#### Serverless Image Pipeline

##### Use Cases

- User profile pictures (1 image per user)
- Request images (max 2 images per request)

##### Processing Steps (using Step Functions)

1. **Pre-signed URL generation**:
   - Lambda generates S3 pre-signed URL
   - Client uploads directly to S3 (no server involvement)
   - EventBridge detects S3 PutObject event

2. **Validation**:
   - Lambda validates file type, size, dimensions
   - Virus scanning (optional: ClamAV in Lambda layer)
   - Move to quarantine bucket if suspicious

3. **Parallel Processing**:
   - **Thumbnail generation**: 150x150px
   - **Small variant**: 400x400px
   - **Medium variant**: 800x800px
   - **Large variant**: 1200x1200px (requests only)
   - **WebP conversion**: Modern format for faster loading
   - **Compression**: Reduce file size with quality=85

4. **Metadata Extraction**:
   - EXIF data removal (privacy: strip GPS coordinates)
   - Dimensions, format, size storage in RDS

6. **Completion**:
   - SNS notification to user
   - CloudWatch metrics for processing time
   - SQS DLQ for failed processing (with retry logic)

##### S3 Bucket Structure

```text
nwassik-uploads/
├── raw/              # Original uploads (temporary, deleted after processing)
├── quarantine/       # Failed validation
├── profiles/
│   ├── original/
│   ├── thumbnail/
│   └── webp/
└── requests/
    ├── original/
    ├── thumbnails/
    ├── small/
    ├── medium/
    ├── large/
    └── webp/
```

##### Benefits

- Learn S3 event-driven triggers
- Practice Step Functions parallel execution
- Master Lambda image processing
- Implement retry logic and DLQs

---

### Phase 3: API Rate Limiting & Protection

#### Intelligent Rate Limiter

##### Protection Strategies

###### 1. API Gateway Native Throttling

- Usage plans with API keys (for providers)
- Rate limits: 10,000 requests/day per user
- Burst capacity: 100 requests/second

###### 2. Custom Token Bucket Algorithm

- Lambda@Edge for edge-level throttling
- Redis/ElastiCache for distributed rate tracking
- DynamoDB for quota storage

###### 3. User Tier System

```text
Free Tier (Requesters):
- 5 requests/minute
- 100 requests/day
- Max 20 active requests

Premium Tier (Providers - future subscription):
- 20 requests/minute
- 1,000 requests/day
- Unlimited active offers
```

###### 4. Intelligent Throttling

- EventBridge scheduled rules reset quotas daily at midnight UTC
- Step Functions handle burst allowances:
  - Allow burst for verified users
  - Enforce cooldown periods after quota violations
- SQS queue for rate-limited requests:
  - Store excess requests with 15-minute TTL
  - Process when quota resets
  - DLQ for expired requests

###### 5. Monitoring & Alerts

- CloudWatch dashboards:
  - Real-time throttle rates
  - Per-user quota consumption
  - Burst usage patterns
- SNS alerts:
  - User approaching limit (80% quota)
  - Quota violation attempts
  - Suspicious activity patterns

###### 6. Analytics

- AWS Batch nightly jobs:
  - Generate usage reports
  - Identify abuse patterns
  - Recommend tier upgrades
- S3 storage for historical data
- QuickSight dashboards (future)

##### Benefits

- Protect backend from DDoS and abuse
- Learn API Gateway usage plans
- Master EventBridge scheduling
- Practice Step Functions conditional logic
- Build SQS/DLQ patterns

---

### Phase 4: Notification System

#### Multi-Channel Notifications

##### Triggers

- New request posted matching provider's filters
- Provider sends message to requester
- Request status changes (fulfilled, cancelled)
- Due date approaching (24 hours before)
- Moderation decision (approved/rejected)
- Rate limit warnings

##### Channels (via SNS)

- Email notifications
- SMS (optional, costly)
- Push notifications (future: mobile app via SNS → FCM/APNS)

##### Implementation

###### Option A: Database Triggers (preferred for learning)

```text
1. RDS PostgreSQL trigger on INSERT into requests table
2. Lambda function invoked by RDS event
3. Query users' notification preferences from RDS
4. Filter users based on:
   - Request type preference
   - Geolocation radius
   - Due date range
5. Publish to SNS topic per user
6. SNS delivers via subscribed channels
```

###### Option B: EventBridge Polling

```text
1. EventBridge scheduled rule (every 5 minutes)
2. Lambda polls RDS for new requests since last check
3. Store last_check_timestamp in DynamoDB
4. Same filtering logic as Option A
5. Publish to SNS
```

##### Notification Preferences Storage

```sql
notification_settings (
  user_id UUID PRIMARY KEY,
  email_enabled BOOLEAN DEFAULT true,
  sms_enabled BOOLEAN DEFAULT false,
  request_types TEXT[], -- ['buy_and_deliver', 'pickup_and_deliver']
  max_distance_km INTEGER, -- geofence radius
  min_due_date_days INTEGER,
  created_at TIMESTAMP
)
```

##### Benefits

- Learn RDS → Lambda integration
- Master SNS topic/subscription model
- Practice EventBridge scheduling
- Build user preference systems

---

### Phase 5: Real-Time Chat Messaging

#### WebSocket-Based Chat

##### Architecture

- API Gateway WebSocket API
- DynamoDB for message storage (fast, scalable)
- Lambda for message handling
- DynamoDB Streams → Lambda for real-time delivery
- SNS for offline notifications

##### Schema

```text
conversations (
  pk: "CONV#{request_id}",
  sk: "META",
  requester_id UUID,
  provider_id UUID,
  status: 'active' | 'archived',
  created_at TIMESTAMP
)

messages (
  pk: "CONV#{request_id}",
  sk: "MSG#{timestamp}#{message_id}",
  sender_id UUID,
  content TEXT,
  attachments JSON, -- future: image URLs
  read_by JSON, -- [user_id: timestamp]
  created_at TIMESTAMP
)

connections (
  pk: "USER#{user_id}",
  sk: "CONN#{connection_id}",
  connection_id TEXT, -- API Gateway connection ID
  connected_at TIMESTAMP,
  ttl NUMBER -- auto-expire after 2 hours idle
)
```

##### Message Flow

1. User connects to WebSocket endpoint
2. Lambda stores connection_id in DynamoDB
3. User sends message via WebSocket
4. Lambda writes to DynamoDB messages table
5. DynamoDB Stream triggers Lambda
6. Lambda looks up recipient's connection_id
7. Lambda posts message via API Gateway Management API
8. If recipient offline, trigger SNS email notification

##### Benefits

- Learn API Gateway WebSocket APIs
- Master DynamoDB Streams
- Practice real-time architectures
- Build connection management

---

### Phase 6: Trust, Safety & Reputation

#### Ratings & Reviews

- Users rate each other after transaction (1-5 stars)
- Text reviews (optional, moderated via Comprehend)
- Aggregate ratings displayed on profiles
- Verified completion badges

#### Reporting System

- Report inappropriate requests/offers/messages
- Categories: scam, inappropriate content, harassment, fake account
- Step Functions workflow:
  - Auto-review with Comprehend/Rekognition
  - Queue for moderator review
  - Suspend account if multiple violations
  - SNS notify both parties of decision

#### Verification Levels

- Email verification (required)
- Phone verification (optional, adds "Phone Verified" badge)
- ID verification (future, adds "ID Verified" badge)
- Trust score calculation:
  - Completion rate
  - Average rating
  - Account age
  - Verification level

---

### Phase 7: Advanced Features (Future)

#### Offers System

- Providers can post standing offers: "Traveling Paris → Tunis on Dec 15, can bring 10kg"
- Requesters browse offers instead of posting requests
- Two-sided marketplace

#### Payment Integration

- E-dinar integration (Tunisia)
- Stripe/PayPal (international)
- Escrow service (money held until delivery confirmed)
- Platform fee: 5% of transaction

#### Money Exchange Officer

- Trusted intermediaries for high-value transactions
- Hold funds until both parties confirm
- Dispute resolution

#### Subscription Model

- Free for requesters (unlimited requests)
- Providers:
  - Free tier: 5 responses/month
  - Premium: $9.99/month, unlimited responses, priority listing
  - Pro: $29.99/month, premium + analytics + verification badge

---
