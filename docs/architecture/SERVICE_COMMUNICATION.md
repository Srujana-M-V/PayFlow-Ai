# PayFlow AI — Service Communication

## 1. Purpose

This document defines how the services in the PayFlow AI platform communicate with each other.

The communication architecture uses two primary mechanisms:

1. Synchronous REST/HTTP communication
2. Asynchronous Kafka event communication

The communication design must preserve:

- Multi-tenant context
- Authentication and authorization
- Reliable service interaction
- Loose coupling
- Event-driven processing
- Error handling
- Retry capability
- Observability

---

## 2. Communication Overview

The major services are:

- API Gateway
- Auth Service
- Payment Service
- Fraud Detection Service
- Reconciliation Service
- Notification Service
- React Frontend

The main communication mechanisms are:

```text
React
  |
  | HTTPS / REST
  v
API Gateway
  |
  +---- REST ----> Auth Service
  |
  +---- REST ----> Payment Service
  |
  +---- REST ----> Other Required Services


Payment Service
  |
  +---- REST ----> Fraud Service
  |
  +---- REST ----> Payment Gateway
  |
  +---- Kafka ---> Kafka Topics


Kafka
  |
  +----> Notification Service
  |
  +----> Reconciliation Processing
  |
  +----> Fraud / Alert Consumers
  |
  +----> Analytics Consumers
```

---

## 3. Synchronous Communication

Synchronous communication is used when the requesting service needs an immediate response.

The primary synchronous protocol is:

```text
HTTP / REST
```

Examples include:

- Frontend to API Gateway
- API Gateway to Auth Service
- API Gateway to Payment Service
- Payment Service to Fraud Service
- Payment Service to external payment gateways

The calling service waits for the response before continuing the relevant part of its workflow.

---

## 4. Asynchronous Communication

Asynchronous communication is used when work can happen independently of the original request.

The primary asynchronous technology is:

```text
Apache Kafka
```

Kafka is used for:

- Payment events
- Fraud alerts
- Notification events
- Settlement/reconciliation jobs
- Other operational events

The producer does not need to wait for every downstream consumer to finish processing the event.

---

## 5. React to API Gateway

The React frontend communicates with the backend through the API Gateway.

```text
React Frontend
      |
      | HTTPS / REST
      v
API Gateway
```

The frontend should not directly communicate with internal backend services.

### Responsibilities

The API Gateway provides:

- Request routing
- Authentication/token validation at the gateway boundary
- CORS handling
- Request-level security controls
- External API boundary

---

## 6. API Gateway to Auth Service

Authentication-related requests are routed from the API Gateway to the Auth Service.

```text
React
  |
  v
API Gateway
  |
  | REST / HTTP
  v
Auth Service
```

Examples:

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

The exact API paths will be finalized during implementation.

The Auth Service returns the authentication result to the API Gateway, which returns the response to the frontend.

---

## 7. API Gateway to Payment Service

Payment-related requests are routed through the API Gateway.

```text
React
  |
  v
API Gateway
  |
  | REST / HTTP
  v
Payment Service
```

Examples include:

- Create payment
- Get transaction
- Get transaction history
- Refund payment
- Payment-related operations

The Payment Service remains responsible for payment business logic.

---

## 8. Payment Service to Fraud Service

Fraud evaluation requires synchronous communication because the payment workflow needs the fraud decision before continuing to gateway processing.

```text
Payment Service
      |
      | REST / HTTP
      v
Fraud Service
      |
      v
Fraud Decision
      |
      v
Payment Service
```

### Flow

1. Payment Service prepares the required transaction risk information.
2. Payment Service sends the information to Fraud Service.
3. Fraud Service evaluates rules and ML predictions.
4. Fraud Service returns:
   - ALLOW
   - FLAG
   - BLOCK
5. Payment Service uses the result to continue or stop payment processing.

The Fraud Service does not directly execute the payment.

---

## 9. Payment Service to Payment Gateway

Payment Service communicates with external payment gateways through gateway adapters.

```text
Payment Service
      |
      v
Gateway Abstraction
      |
      +----> Gateway A
      |
      +----> Gateway B
      |
      +----> Mock Gateway
```

The Payment Service should not depend directly on provider-specific implementation details.

A common gateway interface allows different gateway implementations to be substituted.

---

## 10. Payment Service to Kafka

After important payment state changes, Payment Service publishes events to Kafka.

```text
Payment Service
      |
      | Publish Event
      v
Kafka
      |
      v
payment-events
```

A payment event should contain sufficient information for downstream processing.

Conceptually:

```text
Payment Event
    |
    +-- event_id
    +-- transaction_id
    +-- organization_id
    +-- event_type
    +-- payment_status
    +-- timestamp
    +-- metadata
```

The organization ID is included where the event represents tenant-specific business data.

---

## 11. Fraud Service to Kafka

Fraud-related events can be published for downstream processing.

```text
Fraud Service
      |
      | Publish Fraud Event
      v
Kafka
      |
      v
fraud-alerts
```

These events can be consumed by notification and monitoring components.

Fraud event processing should remain separate from the synchronous fraud decision required by the Payment Service.

---

## 12. Reconciliation Service to Kafka

The Reconciliation Service publishes settlement/reconciliation events.

```text
Reconciliation Service
      |
      | Publish Event
      v
Kafka
      |
      v
settlement-jobs
```

These events can be consumed by:

- Notification Service
- Analytics processing
- Other required consumers

---

## 13. Kafka to Notification Service

The Notification Service consumes relevant Kafka events.

```text
Kafka
  |
  +---- payment-events
  |
  +---- fraud-alerts
  |
  +---- settlement-jobs
  |
  v
Notification Service
```

The Notification Service processes the event and determines the required notification action.

Possible outputs include:

- WebSocket updates
- Merchant webhooks
- Email notifications

---

## 14. Notification Service to WebSocket

The Notification Service provides real-time updates to the frontend through WebSockets.

The Python implementation uses Django Channels.

```text
Kafka
  |
  v
Notification Service
  |
  v
Django Channels
  |
  | WebSocket
  v
React Dashboard
```

Possible real-time updates include:

- Payment status changes
- Fraud alerts
- Gateway health changes
- Reconciliation updates
- Investigation updates

---

## 15. Notification Service to Merchant Webhooks

Merchant webhook delivery is asynchronous.

```text
Kafka
  |
  v
Notification Service
  |
  v
Merchant Webhook Endpoint
```

The Notification Service uses the webhook configuration belonging to the appropriate organization.

Webhook failures should be logged and handled through the notification retry strategy.

---

## 16. Kafka and Reconciliation Communication

Reconciliation-related processing can use Kafka for asynchronous event handling.

```text
Settlement Processing
        |
        v
Reconciliation Service
        |
        v
settlement-jobs
        |
        +----> Notification Service
        |
        +----> Analytics / Other Consumers
```

The exact consumer responsibilities will be finalized during the Kafka implementation phase.

---

## 17. Kafka and Analytics Communication

Analytics can consume relevant business events.

```text
Payment Events
Fraud Events
Reconciliation Events
       |
       v
      Kafka
       |
       v
Analytics Processing
       |
       v
Aggregated Metrics
       |
       v
React Dashboard
```

Analytics processing must preserve organization context so that metrics remain tenant-specific.

---

## 18. Service-to-Service Authentication

Internal service communication must be protected.

For protected service-to-service requests:

```text
Service A
   |
   | Authenticated Request
   v
Service B
```

The implementation will define the exact service authentication mechanism during the security phase.

Services must not blindly trust arbitrary internal requests.

---

## 19. Tenant Context Propagation

Tenant context must be preserved when communicating between services.

For synchronous communication:

```text
Authenticated Request
        |
        v
Organization Context
        |
        v
Service Request
```

For asynchronous communication:

```text
Business Event
     |
     +-- organization_id
     |
     +-- transaction_id
     |
     +-- event_id
     |
     v
Kafka
```

Downstream services must use the organization context when processing tenant-specific data.

---

## 20. Request vs Event Communication

The system uses REST and Kafka for different purposes.

| Requirement | Communication |
|---|---|
| User login | REST |
| User registration | REST |
| Create payment | REST |
| Get transaction | REST |
| Fraud decision before payment | REST |
| External gateway request | REST/HTTPS |
| Payment state event | Kafka |
| Fraud alert | Kafka |
| Notification processing | Kafka |
| Settlement/reconciliation event | Kafka |
| Analytics event processing | Kafka |
| Real-time dashboard update | WebSocket |

---

## 21. Communication Failure Handling

Service communication failures must be handled explicitly.

### REST Failure

```text
Service A
    |
    v
Service B
    |
    X
 Failure
    |
    v
Timeout / Error Handling
```

Possible handling includes:

- Timeout
- Controlled retry where appropriate
- Error logging
- State update
- Failure response
- Fallback where supported

Retries must be designed carefully for payment operations to avoid duplicate processing.

---

## 22. Kafka Failure Handling

Kafka consumers must support reliable event processing.

The architecture will support:

- Consumer groups
- Retry handling
- Dead Letter Topics
- Event deduplication
- Idempotent event processing
- Error logging
- Failed-event investigation

These mechanisms will be implemented in the Kafka phase.

---

## 23. Communication Boundaries

Each service communicates only through defined interfaces.

```text
React
  |
  v
API Gateway
  |
  +----> Auth Service
  |
  +----> Payment Service
              |
              +----> Fraud Service
              |
              +----> Payment Gateways
              |
              +----> Kafka
                         |
                         +----> Notification
                         |
                         +----> Reconciliation
                         |
                         +----> Analytics
```

Services must not directly access another service's internal application logic.

---

## 24. Database Communication Boundary

Services should not directly modify another service's internal business data.

Conceptually:

```text
Service A
   |
   X
Service B Database
```

Instead:

```text
Service A
   |
   | REST / Kafka
   v
Service B
   |
   v
Service B Data
```

This preserves service ownership and reduces tight coupling.

---

## 25. Communication Principles

The following principles apply:

1. REST is used for synchronous operations.
2. Kafka is used for asynchronous event processing.
3. React communicates through the API Gateway.
4. Internal services should not be directly exposed to the public internet.
5. Payment Service communicates synchronously with Fraud Service when a fraud decision is required before payment processing.
6. Payment Service communicates with external gateways through gateway abstractions.
7. Payment events are published to Kafka.
8. Fraud alerts are published to Kafka where downstream processing is required.
9. Reconciliation events are published to Kafka.
10. Notification Service consumes relevant Kafka events.
11. WebSocket communication is used for real-time dashboard updates.
12. Merchant webhooks are handled asynchronously.
13. Tenant context must be preserved across service communication.
14. Service-to-service requests must be protected.
15. Payment operations must be designed carefully to prevent duplicate processing.
16. Kafka consumers must support retry and dead-letter handling.
17. Services must communicate through defined APIs and events rather than direct internal database access.

---

## 26. Architectural Goal

The service communication architecture provides clear and controlled communication between PayFlow AI components.

The design combines:

- REST/HTTP
- Kafka
- WebSockets
- External HTTPS APIs

to support:

- Payment orchestration
- Fraud detection
- Gateway routing
- Event-driven processing
- Reconciliation
- Notifications
- Analytics
- Real-time monitoring
- Multi-tenant processing