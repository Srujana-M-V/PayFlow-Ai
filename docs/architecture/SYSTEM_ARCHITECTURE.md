# PayFlow AI — System Architecture

## 1. Architecture Style

PayFlow AI will use a modular microservice-oriented architecture.

The major components are:

- API Gateway
- Authentication Service
- Payment Service
- Fraud Detection Service
- Reconciliation Service
- Notification Service
- React Frontend
- PostgreSQL
- Redis
- Apache Kafka

---

## 2. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │    React Frontend    │
                         │ Dashboard / Analytics│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     API Gateway      │
                         │ Routing / Security   │
                         └──────────┬───────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
       ┌──────────────┐     ┌──────────────┐    ┌─────────────────┐
       │ Auth Service │     │Payment Service│    │Reconciliation  │
       │              │     │              │    │    Service      │
       └──────────────┘     └──────┬───────┘    └─────────────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │   Fraud Service  │
                          │ FastAPI + ML     │
                          └────────┬─────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  Gateway Router     │
                         │ Health / Routing    │
                         └─────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
               ┌─────────┐   ┌─────────┐   ┌────────────┐
               │Gateway A│   │Gateway B│   │Mock Gateway│
               └─────────┘   └─────────┘   └────────────┘


              ┌─────────────────────────────────────┐
              │          Apache Kafka               │
              │                                     │
              │ payment-events                      │
              │ fraud-alerts                        │
              │ notification-events                 │
              │ settlement-jobs                     │
              └─────────────────────────────────────┘
                         │       │       │
                         ▼       ▼       ▼
                  Notification Fraud  Settlement
                     Service   Flow     Flow
                         │               │
                         ▼               ▼
                    WebSocket      Reconciliation
                         │               │
                         └───────┬───────┘
                                 ▼
                         React Dashboard


              ┌─────────────────────────────────────┐
              │            Infrastructure           │
              │                                     │
              │ PostgreSQL     Redis     Kafka      │
              └─────────────────────────────────────┘