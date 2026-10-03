# PayFlow AI — Multi-Tenant Architecture

## 1. Purpose

PayFlow AI is designed as a multi-tenant platform.

Multiple organizations can use the same application while their users, payment transactions, gateway configurations, fraud information, reconciliation records, and other business data remain logically isolated.

The multi-tenant architecture must prevent one organization from accessing another organization's data.

---

## 2. Tenant Definition

A tenant represents an organization or merchant using PayFlow AI.

Each organization has its own:

- Users
- Payment transactions
- Gateway configurations
- Gateway health information
- Fraud records
- Settlement records
- Reconciliation records
- Webhook configurations
- Audit records

The organization is the primary tenant boundary.

---

## 3. Tenant Identification

Every authenticated user belongs to an organization.

After authentication, the user's organization identity is associated with the authenticated request.

The backend uses this organization identity to determine which tenant's data can be accessed.

The organization identifier must be available throughout the request lifecycle wherever tenant-specific data is required.

---

## 4. Tenant Isolation Strategy

PayFlow AI will initially use logical tenant isolation within PostgreSQL.

The main business tables will contain an organization/tenant reference where tenant ownership is required.

Conceptually:

    Organization
         |
         +--------------------+
         |                    |
         v                    v
      Users              Transactions
         |                    |
         |                    +------> Fraud Scores
         |                    |
         |                    +------> Reconciliation
         |
         +------> Gateway Configurations
         |
         +------> Webhook Configurations
         |
         +------> Audit Logs

This allows multiple organizations to share the same database infrastructure while keeping their business records logically separated.

---

## 5. Organization Entity

The organization is the root tenant entity.

An organization should contain information such as:

- Organization ID
- Organization name
- Organization status
- Created timestamp
- Updated timestamp

The organization ID is referenced by tenant-owned entities.

---

## 6. User and Organization Relationship

Each user belongs to an organization.

Conceptually:

    Organization 1
         |
         +---- User 1
         +---- User 2
         +---- User 3

A user must only be able to access resources belonging to their authorized organization.

User roles determine what operations the user can perform inside that organization.

---

## 7. Tenant-Owned Data

The following data is tenant-specific:

### Users

Users belong to an organization.

### Gateway Configurations

Payment gateway configurations belong to the organization using them.

### Transactions

Every payment transaction belongs to the organization that initiated it.

### Fraud Records

Fraud scores and fraud decisions are associated with the relevant payment transaction and therefore with the corresponding organization.

### Settlement Records

Settlement and reconciliation information belongs to the organization whose payments are being reconciled.

### Webhook Configurations

Webhook configuration belongs to the organization receiving the events.

### Audit Logs

Audit records must preserve the organization context whenever the event is tenant-specific.

---

## 8. Tenant Context

The backend should establish tenant context from the authenticated user's identity.

The expected request flow is:

    Client Request
          |
          v
    API Gateway
          |
          v
    Authentication Validation
          |
          v
    User Identity + Organization ID
          |
          v
    Backend Service
          |
          v
    Tenant-Aware Business Logic
          |
          v
    Tenant-Scoped Database Query

The service must never blindly trust a tenant identifier supplied by the client when determining authorization.

---

## 9. Tenant Authorization Rule

A user must satisfy both:

1. Authentication
2. Authorization for the requested organization's resource

For tenant-owned resources, the backend must verify that the authenticated user's organization matches the organization associated with the resource.

Example:

    Authenticated User
           |
           | organization_id = ORG-001
           v
    Request Transaction
           |
           | transaction.organization_id
           v
         ORG-001

Access is permitted when the authenticated organization is authorized to access the transaction.

If the resource belongs to another organization, access must be denied.

---

## 10. Cross-Tenant Data Protection

The system must prevent:

- Reading another organization's transactions.
- Modifying another organization's transactions.
- Accessing another organization's gateway credentials.
- Viewing another organization's fraud records.
- Viewing another organization's reconciliation records.
- Accessing another organization's webhook configuration.
- Accessing tenant-restricted audit information.

Tenant filtering must be applied at the backend/service layer.

The frontend must not be responsible for enforcing tenant isolation.

---

## 11. Role-Based Access Within a Tenant

Tenant isolation and role-based access control are separate concerns.

First:

    Is the user part of the organization?

Then:

    Does the user's role have permission for the requested operation?

Example:

    Organization
         |
         +-- MERCHANT_ADMIN
         +-- ACCOUNTANT
         +-- SUPPORT
         +-- FRAUD_ANALYST

Different roles may have different permissions while remaining inside the same tenant.

---

## 12. Service-Level Tenant Awareness

Each service handling tenant-specific data must preserve organization context.

### Auth Service

Responsible for:

- User identity
- Organization membership
- Roles
- Permissions

### Payment Service

Responsible for:

- Tenant-scoped transactions
- Tenant-scoped gateway configurations
- Tenant-scoped payment operations

### Fraud Service

Receives the required transaction/risk information for fraud evaluation.

Fraud scoring must remain associated with the originating payment and organization.

### Reconciliation Service

Processes settlement information belonging to the appropriate organization.

### Notification Service

Ensures tenant-specific notifications are delivered to the correct organization.

---

## 13. Tenant Isolation in Database Queries

Tenant-specific queries should conceptually follow:

    SELECT ...
    FROM transactions
    WHERE organization_id = authenticated_organization_id;

The organization filter must be applied consistently to tenant-owned resources.

The application should avoid unrestricted queries against tenant-owned tables.

---

## 14. Tenant Isolation and APIs

API endpoints that return tenant-specific information must automatically operate within the authenticated tenant context.

For example:

    GET /api/transactions

should return transactions belonging only to the authenticated user's authorized organization.

It should not return transactions from every organization.

Similarly:

    GET /api/transactions/{id}

must verify that the requested transaction belongs to the user's authorized organization.

---

## 15. Tenant Isolation and Events

Kafka events involving tenant-specific business operations should carry sufficient organization context for downstream processing.

Conceptually:

    Payment Event
        |
        +-- event_id
        +-- transaction_id
        +-- organization_id
        +-- event_type
        +-- timestamp
        +-- payload

Consumers must use the organization context when processing tenant-specific events.

---

## 16. Tenant Isolation and Redis

Redis keys containing tenant-specific information should use a tenant-aware naming strategy where appropriate.

Example:

    tenant:{organization_id}:idempotency:{key}

    tenant:{organization_id}:gateway-health:{gateway_id}

This reduces the risk of collisions and makes tenant ownership explicit.

---

## 17. Tenant Isolation and Webhooks

Merchant webhook configurations are tenant-specific.

When an event is generated:

    Payment Event
         |
         v
    Notification Service
         |
         v
    Identify Organization
         |
         v
    Load Organization Webhook Configuration
         |
         v
    Send Webhook

The system must never use another organization's webhook configuration.

---

## 18. Tenant Isolation and Auditability

Tenant-specific actions should preserve organization context in audit records.

An audit record should conceptually contain:

- Audit ID
- Organization ID
- User ID
- Action
- Resource
- Resource ID
- Timestamp
- Relevant metadata

This makes it possible to investigate actions within the correct tenant boundary.

---

## 19. Multi-Tenant Security Principles

The following principles apply:

1. Every tenant-owned resource must have an identifiable organization owner.
2. Tenant identity comes from authenticated context.
3. Client-provided organization identifiers must not be trusted for authorization.
4. Backend services must enforce tenant isolation.
5. Frontend filtering is not a security boundary.
6. Database queries must be tenant-scoped.
7. Kafka events must preserve tenant context where required.
8. Redis keys should avoid cross-tenant collisions.
9. Webhooks must remain tenant-specific.
10. Audit records must preserve organization context.

---

## 20. Future Scalability

The initial architecture uses logical tenant isolation within shared PostgreSQL infrastructure.

The design should allow future evolution toward stronger isolation models if required.

Possible future approaches include:

- Separate database schemas per tenant.
- Separate databases for selected tenants.
- Dedicated infrastructure for high-volume tenants.

These are future scalability options and are not required for the initial implementation.

---

## 21. Multi-Tenant Architectural Goal

The multi-tenant architecture must provide:

- Logical data isolation.
- Secure tenant authorization.
- Role-based access within each tenant.
- Tenant-aware API processing.
- Tenant-aware event processing.
- Tenant-aware caching.
- Tenant-aware notifications.
- Tenant-aware auditing.
- A foundation for future tenant scaling.

The organization is the primary security and data-isolation boundary throughout the PayFlow AI platform.