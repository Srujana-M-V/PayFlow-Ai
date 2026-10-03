# PayFlow AI — Microservice Boundaries

## 1. Purpose

This document defines the responsibility and boundaries of each major service in the PayFlow AI platform.

The objective is to keep services independently understandable, maintainable, testable, and deployable while preserving the complete PayFlow AI business flow.

---

## 2. Service Overview

PayFlow AI consists of the following major application services:

1. API Gateway
2. Auth Service
3. Payment Service
4. Fraud Detection Service
5. Reconciliation Service
6. Notification Service
7. React Frontend

The platform also depends on shared infrastructure:

- PostgreSQL
- Redis
- Kafka
- Payment Gateway Providers
- Object/File Storage
- Email/Webhook delivery infrastructure

---

## 3. API Gateway

### Responsibility

The API Gateway is the single entry point for client requests.

### Responsibilities

- Receive requests from the React frontend.
- Route requests to the appropriate backend service.
- Perform gateway-level authentication/token validation.
- Apply request-level security controls.
- Handle CORS configuration.
- Apply request logging and tracing.
- Provide a controlled external API boundary.

### Does Not Own

The API Gateway does not own:

- User accounts
- Payment transactions
- Fraud decisions
- Settlement records
- Business workflows
- Payment gateway credentials

---

## 4. Auth Service

### Responsibility

The Auth Service manages identity, authentication, authorization, users, roles, and organization membership.

### Responsibilities

- User registration.
- User login.
- Password hashing and verification.
- Access token generation.
- Refresh token management.
- Logout and token invalidation.
- Role-based access control.
- Organization membership.
- User management.
- Permission validation.
- Authentication-related audit events.

### Roles

The platform supports:

- SUPER_ADMIN
- MERCHANT_ADMIN
- ACCOUNTANT
- SUPPORT
- FRAUD_ANALYST

### Does Not Own

The Auth Service does not own:

- Payment transactions.
- Gateway routing.
- Fraud scoring.
- Settlement reconciliation.

---

## 5. Payment Service

### Responsibility

The Payment Service is responsible for the complete payment transaction lifecycle.

### Responsibilities

- Create payment transactions.
- Validate payment requests.
- Enforce idempotency.
- Initiate fraud evaluation before payment processing.
- Select an appropriate payment gateway.
- Route payments to gateway adapters.
- Handle gateway responses.
- Maintain transaction state.
- Handle gateway failures and failover.
- Track gateway health.
- Process payment webhooks.
- Handle refunds.
- Provide transaction history.
- Publish payment events to Kafka.
- Maintain payment-related audit information.

### Transaction States

The payment lifecycle includes:

- CREATED
- PROCESSING
- SUCCESS
- FAILED

Additional internal investigation or reconciliation states may be maintained where required.

### Gateway Abstraction

The Payment Service uses a gateway abstraction so that different providers can be integrated without changing the core payment orchestration logic.

Potential adapters include:

- Gateway A
- Gateway B
- Mock Gateway

Real providers may be integrated later without changing the overall architecture.

### Does Not Own

The Payment Service does not directly own:

- ML model training.
- Fraud model lifecycle.
- Settlement file processing.
- User authentication.

---

## 6. Fraud Detection Service

### Responsibility

The Fraud Detection Service evaluates payment risk using machine learning and rule-based detection.

### Technology Direction

- Python
- FastAPI
- scikit-learn
- XGBoost

### Responsibilities

- Receive payment risk-scoring requests.
- Perform feature processing.
- Apply machine-learning fraud prediction.
- Apply rule-based checks.
- Detect velocity-based suspicious activity.
- Detect unusually high transaction amounts.
- Combine ML and rule-based signals.
- Produce a fraud score.
- Produce a fraud decision.
- Expose health and scoring APIs.

### Fraud Decisions

The service can return:

- ALLOW
- FLAG
- BLOCK

### Does Not Own

The Fraud Detection Service does not own:

- Payment gateway routing.
- User authentication.
- Settlement processing.
- Frontend presentation.

The Payment Service remains responsible for deciding how the fraud result affects the payment workflow.

---

## 7. Reconciliation Service

### Responsibility

The Reconciliation Service compares internal payment records with external gateway settlement data.

### Responsibilities

- Receive settlement files.
- Store settlement file metadata.
- Parse settlement records.
- Compare gateway records with internal transactions.
- Detect reconciliation differences.
- Classify reconciliation results.
- Generate reconciliation records.
- Support investigation of mismatches.
- Run scheduled reconciliation jobs.
- Publish settlement/reconciliation events.

### Reconciliation States

The system supports:

- MATCHED
- MISMATCH
- MISSING
- EXTRA

### Scheduling

The Python implementation will use:

- Celery
- Celery Beat

for asynchronous and scheduled reconciliation processing.

### Does Not Own

The Reconciliation Service does not own:

- Payment execution.
- User authentication.
- ML fraud model decisions.

---

## 8. Notification Service

### Responsibility

The Notification Service handles asynchronous notification delivery and real-time platform updates.

### Responsibilities

- Consume relevant Kafka events.
- Process payment notifications.
- Process fraud notifications.
- Process gateway health notifications.
- Process reconciliation notifications.
- Send merchant webhook notifications.
- Provide notification events to the real-time communication layer.
- Provide the foundation for email notifications.

### Communication

The Notification Service consumes events from Kafka rather than tightly coupling notification processing to payment execution.

---

## 9. React Frontend

### Responsibility

The React frontend provides the merchant and operations dashboard.

### Responsibilities

- Authentication screens.
- Registration screens.
- Dashboard.
- Transaction listing.
- Transaction details.
- Fraud monitoring.
- Reconciliation monitoring.
- Gateway health monitoring.
- Investigation views.
- User management.
- Real-time updates.
- Analytics visualization.

### Technology Direction

- React
- Vite
- Redux
- React Router
- Axios
- Tailwind CSS
- Recharts

The frontend communicates with backend services through the API Gateway rather than directly accessing internal service databases.

---

## 10. Infrastructure Boundaries

### PostgreSQL

PostgreSQL is the primary persistent database infrastructure.

It stores business data such as:

- Organizations
- Users
- Gateway configurations
- Transactions
- Fraud scores
- Settlement information
- Reconciliation records
- Webhook configurations
- Audit logs

Database ownership will follow service boundaries as the architecture is implemented.

---

### Redis

Redis is used for high-speed and temporary operational data.

Primary uses include:

- Idempotency keys.
- Gateway health information.
- Caching.
- Short-lived state.
- Rate limiting where required.

Redis is not treated as the system of record for permanent business data.

---

### Kafka

Kafka provides asynchronous event communication between services.

Core event categories include:

- Payment events.
- Fraud alerts.
- Notification events.
- Settlement/reconciliation events.

Kafka allows downstream processing to occur independently of the original payment request.

---

## 11. Payment Gateway Providers

External payment gateways are treated as external systems.

The Payment Service communicates with them through gateway adapters.

The internal system must not depend directly on provider-specific implementation details.

The gateway abstraction allows:

- Multiple providers.
- Gateway health tracking.
- Routing.
- Failover.
- Provider-specific request/response handling.

---

## 12. Service Ownership Principle

Each service should own its business responsibility.

A service should not directly modify another service's internal business data.

Communication between services should happen through:

- REST APIs for synchronous operations.
- Kafka events for asynchronous operations.

---

## 13. Dependency Direction

The intended dependency direction is:

React Frontend
        |
        v
API Gateway
        |
        +------------------+
        |                  |
        v                  v
Auth Service        Payment Service
                         |
                         +----------> Fraud Service
                         |
                         +----------> Payment Gateways
                         |
                         +----------> Redis
                         |
                         +----------> PostgreSQL
                         |
                         +----------> Kafka
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
                Notification Service      Reconciliation Service

---

## 14. Boundary Rules

The following rules apply to the architecture:

1. Authentication logic belongs to Auth Service.
2. Payment lifecycle logic belongs to Payment Service.
3. Fraud scoring belongs to Fraud Detection Service.
4. Settlement comparison belongs to Reconciliation Service.
5. Notification delivery belongs to Notification Service.
6. Client presentation belongs to React.
7. API routing belongs to the API Gateway.
8. Permanent business data belongs in PostgreSQL.
9. Temporary/high-speed operational state may use Redis.
10. Asynchronous cross-service events use Kafka.
11. External gateway-specific logic is isolated behind gateway adapters.
12. Services should communicate through defined APIs/events rather than directly accessing another service's internal logic.

---

## 15. Architectural Goal

The service boundaries are designed to support:

- Independent development.
- Clear responsibility ownership.
- Testability.
- Fault isolation.
- Horizontal scaling.
- Event-driven processing.
- Future gateway expansion.
- Multi-tenant payment processing.
- Fraud detection.
- Settlement reconciliation.
- Real-time analytics and notifications.

These boundaries form the foundation for the implementation phases that follow.