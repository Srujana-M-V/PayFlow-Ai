# PayFlow AI — Microservice Boundaries

## 1. Purpose

This document defines the service boundaries of the PayFlow AI platform.

PayFlow AI follows a microservice-oriented architecture where each major business capability is isolated into a dedicated service.

The service boundaries are designed to provide:

- Clear ownership of business responsibilities
- Independent service development
- Controlled service-to-service communication
- Loose coupling
- Independent scalability
- Fault isolation
- Multi-tenant processing
- Event-driven integration

---

## 2. Target Microservices

The PayFlow AI platform contains six primary backend services:

1. API Gateway
2. Auth Service
3. Payment Service
4. Fraud Detection Service
5. Reconciliation Service
6. Notification Service

The platform also contains:

- React Frontend
- PostgreSQL
- Redis
- Apache Kafka
- External Payment Gateways

---

## 3. API Gateway

### Responsibility

The API Gateway is the external entry point for backend API requests.

It is responsible for:

- Request routing
- Authentication/token validation at the gateway boundary
- Request-level security
- CORS handling
- Routing requests to internal services
- Protecting internal services from direct public access

### Does Not Own

The API Gateway does not own:

- Payment business logic
- Fraud decisions
- Reconciliation logic
- Notification business logic
- Tenant business data

### Communication

The API Gateway communicates with:

- Auth Service
- Payment Service
- Other required backend services

The React frontend communicates with the system through the API Gateway.

---

## 4. Auth Service

### Responsibility

The Auth Service owns authentication and authorization-related identity information.

It is responsible for:

- User registration
- User login
- Password management
- JWT access tokens
- Refresh tokens
- Logout
- User roles
- Organization membership
- Permissions

### Tenant Responsibility

The Auth Service establishes the authenticated user's organization context.

The organization identity must be available to downstream services where tenant-specific processing is required.

### Does Not Own

The Auth Service does not own:

- Payment transactions
- Fraud scores
- Settlement records
- Gateway processing
- Notification delivery

---

## 5. Payment Service

### Responsibility

The Payment Service is the core business service of PayFlow AI.

It owns:

- Payment requests
- Payment transaction lifecycle
- Idempotency
- Gateway selection
- Gateway health evaluation
- Gateway failover
- Payment state management
- Refund processing
- Payment webhooks
- Payment events

### Payment Processing

The Payment Service coordinates the following flow:

```text
Payment Request
      |
      v
Validation
      |
      v
Idempotency
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
Fallback Gateway if required
      |
      v
Transaction Update
      |
      v
Kafka Event