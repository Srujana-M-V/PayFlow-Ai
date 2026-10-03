# PayFlow AI — Data Flow

## 1. Purpose

This document defines the major data flows of the PayFlow AI platform.

The core flows are:

1. Payment Flow
2. Fraud Detection Flow
3. Gateway Routing and Failover Flow
4. Kafka Event Flow
5. Reconciliation Flow
6. Notification Flow
7. Analytics Flow

All flows must preserve:

- Multi-tenant context
- Authentication and authorization
- Payment reliability
- Idempotency
- Fraud protection
- Event-driven processing
- Reconciliation
- Real-time monitoring
- Operational analytics

---

## 2. Payment Flow

The payment flow is the primary business flow of PayFlow AI.

```text
React Frontend
      |
      v
API Gateway
      |
      v
Payment Service
      |
      v
Tenant Validation
      |
      v
Request Validation
      |
      v
Idempotency Check
      |
      v
Fraud Check
      |
      v
Gateway Health
      |
      v
Gateway Selection
      |
      v
Primary Gateway
      |
      v
Transaction Update
      |
      v
PostgreSQL
      |
      v
Kafka Event
```

### Payment Flow Steps

1. The merchant initiates a payment from the React frontend.
2. The request reaches the API Gateway.
3. Authentication information is validated.
4. The Payment Service identifies the authenticated organization.
5. Tenant authorization is performed.
6. The payment request is validated.
7. The idempotency key is checked.
8. A payment transaction is created and moves into the appropriate processing state.
9. The Payment Service requests a fraud evaluation.
10. The fraud result is received.
11. If the transaction is blocked, payment processing stops.
12. If processing is allowed to continue, gateway health is evaluated.
13. The Payment Service selects a suitable payment gateway.
14. The payment request is sent to the selected gateway.
15. The gateway response is received.
16. The transaction state is updated.
17. The transaction is persisted in PostgreSQL.
18. A payment event is published to Kafka.
19. Downstream services process the event where required.
20. The frontend can receive the updated status through the real-time notification flow.

---

## 3. Payment State Flow

The payment lifecycle follows controlled transaction states.

```text
CREATED
   |
   v
PROCESSING
   |
   +----------> SUCCESS
   |
   +----------> FAILED
```

The Payment Service owns the payment state machine.

Clients must not be allowed to arbitrarily change transaction states.

---

## 4. Idempotency Flow

Idempotency prevents duplicate payment processing when the same request is submitted more than once.

```text
Payment Request
      |
      v
Payment Service
      |
      v
Redis Idempotency Check
      |
      +----------------------+
      |                      |
   Existing                New Key
      |                      |
      v                      v
Return Existing         Continue Payment
Result
```

### Flow

1. The client sends a payment request containing an idempotency key.
2. Payment Service checks Redis.
3. If the key already exists, the request is treated as a duplicate.
4. The previously stored result can be returned.
5. If the key does not exist, payment processing continues.
6. The idempotency information is stored for subsequent duplicate requests.

---

## 5. Fraud Detection Flow

Fraud detection occurs before payment gateway processing.

```text
Payment Service
      |
      | Transaction Risk Data
      v
Fraud Service
      |
      v
Feature Processing
      |
      v
Rules + ML Model
      |
      v
Risk Score
      |
      v
ALLOW / FLAG / BLOCK
      |
      v
Payment Service
```

### Fraud Flow Steps

1. Payment Service sends the required transaction information to the Fraud Service.
2. Fraud Service prepares the required features.
3. Rule-based fraud checks are performed.
4. The ML model evaluates the transaction.
5. The signals are combined into a risk score.
6. The Fraud Service returns one of:
   - ALLOW
   - FLAG
   - BLOCK
7. Payment Service uses the result in the payment decision.
8. Fraud information is associated with the relevant transaction.

---

## 6. Gateway Routing Flow

Payment Service evaluates gateway availability before processing the payment.

```text
Payment Service
      |
      v
Gateway Health
      |
      v
Gateway Selection
      |
      +------------+-------------+
      |            |             |
      v            v             v
   Gateway A    Gateway B    Mock Gateway
```

Gateway selection may consider:

- Gateway availability
- Gateway health
- Gateway performance
- Routing configuration
- Payment requirements

Gateway-specific implementation remains behind a common gateway abstraction.

---

## 7. Gateway Failover Flow

PayFlow AI must handle gateway failures.

```text
Payment Service
      |
      v
Primary Gateway
      |
      X
   Failure
      |
      v
Update Gateway Health
      |
      v
Failover Decision
      |
      v
Fallback Gateway
      |
      v
Payment Result
      |
      v
Transaction Update
```

### Failover Flow Steps

1. Payment Service selects a primary gateway.
2. The payment request is sent to that gateway.
3. The gateway fails or becomes unavailable.
4. Gateway health information is updated.
5. Payment Service evaluates whether failover is appropriate.
6. A fallback gateway can be selected.
7. The payment request is processed through the fallback gateway.
8. The final result is recorded.
9. Relevant events are published to Kafka.

---

## 8. Kafka Event Flow

Kafka provides asynchronous communication between services.

The primary event categories are:

```text
payment-events
fraud-alerts
notification-events
settlement-jobs
```

### General Kafka Flow

```text
Payment / Fraud / Reconciliation Service
                  |
                  v
                Kafka
                  |
        +---------+---------+
        |         |         |
        v         v         v
 Notification   Fraud   Reconciliation
   Service      Alerts     Processing
```

---

## 9. Payment Event Flow

```text
Payment Service
      |
      v
payment-events
      |
      +-------------> Notification Service
      |
      +-------------> Other Consumers
```

A tenant-specific payment event should contain sufficient context such as:

- Event ID
- Transaction ID
- Organization ID
- Event type
- Payment status
- Timestamp
- Required metadata

---

## 10. Fraud Alert Event Flow

```text
Fraud Service
      |
      v
Fraud Decision
      |
      v
fraud-alerts
      |
      v
Notification / Monitoring Consumers
```

Fraud events allow downstream components to process fraud alerts asynchronously without tightly coupling them to the payment request.

---

## 11. Reconciliation Event Flow

```text
Reconciliation Service
      |
      v
Reconciliation Result
      |
      v
settlement-jobs
      |
      +-------------> Notification Service
      |
      +-------------> Other Consumers
```

Settlement and reconciliation events allow downstream services to react to reconciliation results.

---

## 12. Reconciliation Flow

Reconciliation compares internal payment information with external settlement information.

```text
External Settlement File
          |
          v
Reconciliation Service
          |
          v
Parse Settlement Records
          |
          v
Compare With Internal Records
          |
          v
Reconciliation Result
          |
     +----+---------+---------+
     |              |         |
     v              v         v
 MATCHED        MISMATCH    MISSING
                               
                          EXTRA
```

### Reconciliation Flow Steps

1. External settlement information is received.
2. The Reconciliation Service processes the settlement file.
3. Settlement records are compared with internal payment records.
4. Each record is classified as:
   - MATCHED
   - MISMATCH
   - MISSING
   - EXTRA
5. Reconciliation records are stored.
6. Investigation information can be created for relevant mismatches.
7. A settlement/reconciliation event is published to Kafka.
8. Notification and analytics components can consume the resulting information.

---

## 13. Scheduled Reconciliation Flow

The Python implementation will use Celery and Celery Beat for scheduled reconciliation processing.

```text
Celery Beat
     |
     | Scheduled Trigger
     v
Celery Worker
     |
     v
Reconciliation Service
     |
     v
Settlement Processing
     |
     v
PostgreSQL
     |
     v
Kafka
```

The scheduling configuration will be finalized during the Reconciliation implementation phase.

---

## 14. Notification Flow

The Notification Service consumes relevant events and handles notification delivery.

```text
Kafka
  |
  v
Notification Service
  |
  +-----------> WebSocket
  |
  +-----------> Merchant Webhook
  |
  +-----------> Email Foundation
```

Notifications may include:

- Payment success/failure
- Fraud alerts
- Reconciliation mismatches
- Investigation updates
- System events
- Gateway events

---

## 15. Real-Time Monitoring Flow

Real-time operational information is delivered to the dashboard.

```text
Backend Event
      |
      v
Kafka
      |
      v
Notification Service
      |
      v
Django Channels
      |
      v
WebSocket
      |
      v
React Dashboard
```

Examples include:

- Payment status changes
- Fraud alerts
- Gateway health changes
- Reconciliation updates
- Investigation updates

---

## 16. Analytics Flow

Analytics provides tenant-specific operational visibility into the payment platform.

```text
Payment Transactions
        |
        +-------------------+
        |                   |
        v                   v
Transaction Data       Kafka Events
        |                   |
        +---------+---------+
                  |
                  v
          Analytics Processing
                  |
                  v
           Aggregated Metrics
                  |
                  v
        React Analytics Dashboard
```

### Analytics Data Sources

Analytics can use information from:

- Payment transactions
- Payment success/failure states
- Gateway performance
- Fraud results
- Reconciliation results
- Investigation records
- Relevant Kafka events

### Tenant-Specific Analytics

Analytics must remain scoped to the authenticated organization.

Dashboard metrics include:

- Transaction volume
- Payment success rate
- Payment failure rate
- Gateway performance
- Fraud statistics
- Reconciliation statistics
- Investigation statistics
- Payment trends

The dashboard must never expose another organization's analytics.

---

## 17. Investigation Flow

Investigation information is accessed by authorized users.

```text
React Dashboard
      |
      v
API Gateway
      |
      v
Backend Service
      |
      v
Tenant Authorization
      |
      v
Tenant-Scoped Data
      |
      v
Investigation Result
      |
      v
React Dashboard
```

Investigation data may originate from:

- Payment failures
- Gateway mismatches
- Fraud alerts
- Reconciliation mismatches
- Other operational events

Access must respect both tenant isolation and role-based authorization.

---

## 18. Complete End-to-End Flow

The overall PayFlow AI flow is:

```text
React
  |
  v
API Gateway
  |
  v
Authentication / Tenant Validation
  |
  v
Payment Service
  |
  +----> Idempotency / Redis
  |
  +----> Fraud Service
  |          |
  |          v
  |      Risk Decision
  |
  +----> Gateway Health
  |
  +----> Gateway Selection
  |
  +----> Payment Gateway
  |
  v
PostgreSQL
  |
  v
Kafka
  |
  +----> Notification Service
  |
  +----> Fraud Alerts
  |
  +----> Reconciliation
  |
  +----> Analytics
              |
              v
        React Dashboard
```

---

## 19. Tenant Context Throughout Data Flow

Tenant context must remain associated with tenant-specific operations.

```text
Authenticated User
       |
       v
Organization Context
       |
       v
Payment Request
       |
       v
Payment Transaction
       |
       +----> Fraud Information
       |
       +----> Gateway Processing
       |
       +----> Kafka Event
       |
       +----> Notification
       |
       +----> Reconciliation
       |
       +----> Analytics
```

The organization ID must not be lost when tenant-specific information moves between services.

---

## 20. Error and Recovery Flow

Failures must be observable and recoverable.

```text
Service Operation
      |
      +---- Success
      |       |
      |       v
      |    Continue
      |
      +---- Failure
              |
              v
        Error Handling
              |
       +------+------+
       |      |      |
       v      v      v
     Retry   Log   State Update
              |
              v
        Event / Alert
              |
              v
       Investigation
```

Kafka-based processing will later include retry, deduplication, and dead-letter handling.

---

## 21. Data Flow Principles

The following principles apply:

1. Client requests enter through the API Gateway.
2. Authentication establishes user and tenant context.
3. Payment processing belongs to the Payment Service.
4. Idempotency is checked before duplicate payment processing.
5. Fraud evaluation occurs before gateway execution.
6. Gateway health is considered during routing.
7. Gateway failures can trigger failover where appropriate.
8. PostgreSQL stores persistent business data.
9. Redis handles appropriate high-speed operational state.
10. Kafka handles asynchronous event communication.
11. Reconciliation compares internal and external payment records.
12. Notification processing is asynchronous.
13. Real-time monitoring uses WebSockets.
14. Analytics are tenant-specific.
15. Investigation access requires appropriate authorization.
16. Tenant context must be preserved across services and events.
17. Backend services enforce tenant isolation.
18. Important failures must be observable and recoverable.

---

## 22. Architectural Goal

The data-flow architecture must allow PayFlow AI to process a payment from the initial merchant request through:

Payment
→ Idempotency
→ Fraud Detection
→ Gateway Routing
→ Gateway Processing
→ Transaction Persistence
→ Kafka Events
→ Notification
→ Reconciliation
→ Investigation
→ Analytics
→ Real-Time Dashboard

while maintaining:

- Multi-tenancy
- Security
- Reliability
- Event-driven processing
- Operational visibility
- Data consistency
- Fault recovery