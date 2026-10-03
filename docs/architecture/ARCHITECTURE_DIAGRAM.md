# PayFlow AI — Architecture Diagram

## High-Level System Architecture

                         +----------------------+
                         |    React Frontend    |
                         |  Dashboard / UI      |
                         +----------+-----------+
                                    |
                              HTTPS / REST
                                    |
                                    v
                         +----------------------+
                         |     API Gateway      |
                         +----------+-----------+
                                    |
                +-------------------+-------------------+
                |                   |                   |
                v                   v                   v
        +---------------+   +---------------+   +---------------+
        | Auth Service  |   | Payment       |   | Other Backend |
        |               |   | Service       |   | Services      |
        +---------------+   +-------+-------+   +---------------+
                                    |
                 +------------------+------------------+
                 |                  |                  |
                 v                  v                  v
        +---------------+    +-------------+    +---------------+
        | Fraud Service |    |    Redis    |    |  PostgreSQL   |
        |   FastAPI     |    |             |    |               |
        +---------------+    +-------------+    +---------------+
                                    |
                                    v
                         +----------------------+
                         | Payment Gateways     |
                         | Gateway A / B / Mock |
                         +----------+-----------+
                                    |
                                    v
                              +-----------+
                              |   Kafka   |
                              +-----+-----+
                                    |
                 +------------------+------------------+
                 |                  |                  |
                 v                  v                  v
        +---------------+   +---------------+   +---------------+
        | Notification  |   | Reconciliation|   |   Analytics   |
        | Service       |   | Service       |   |   Processing  |
        +-------+-------+   +---------------+   +---------------+
                |
                v
        +---------------+
        | Django        |
        | Channels      |
        | WebSocket     |
        +-------+-------+
                |
                v
        +---------------+
        | React         |
        | Dashboard     |
        +---------------+

Supporting Infrastructure

+-----------------------------------------------------------+
|                    PayFlow AI Platform                    |
|                                                           |
|  PostgreSQL  ---- Persistent Business Data                |
|                                                           |
|  Redis       ---- Idempotency / Cache / Gateway Health    |
|                                                           |
|  Kafka       ---- Asynchronous Event Communication        |
|                                                           |
|  Celery      ---- Background Processing                   |
|                                                           |
|  Celery Beat ---- Scheduled Reconciliation Jobs           |
|                                                           |
|  Service Discovery ---- Internal Service Location         |
+-----------------------------------------------------------+


Core Payment Flow
React
  |
  v
API Gateway
  |
  v
Payment Service
  |
  +--> Tenant Validation
  |
  +--> Idempotency / Redis
  |
  +--> Fraud Service
  |       |
  |       v
  |   ALLOW / FLAG / BLOCK
  |
  +--> Gateway Health
  |
  +--> Gateway Selection
  |
  +--> Primary Gateway
  |       |
  |       +--> Failure
  |              |
  |              v
  |        Fallback Gateway
  |
  v
PostgreSQL
  |
  v
Kafka
  |
  +--> Notification
  +--> Reconciliation
  +--> Analytics
Tenant Context
Authenticated User
       |
       v
Organization / Tenant
       |
       v
Payment Request
       |
       +--> Transaction
       +--> Fraud Information
       +--> Gateway Processing
       +--> Kafka Event
       +--> Notification
       +--> Reconciliation
       +--> Analytics