# PayFlow AI — Technology Decisions

## Backend

| Requirement | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django |
| REST APIs | Django REST Framework |
| Authentication | DRF SimpleJWT |
| Authorization | Django Permissions |
| ORM | Django ORM |

## Microservices

| Service | Technology |
|---|---|
| API Gateway | Python |
| Auth Service | Django + DRF |
| Payment Service | Django + DRF |
| Fraud Service | FastAPI |
| Reconciliation Service | Django + Celery |
| Notification Service | Django + Django Channels |

## Database

| Requirement | Technology |
|---|---|
| Database | PostgreSQL |
| ORM | Django ORM |
| Tenant Isolation | Logical Tenant Isolation |

## Caching

| Requirement | Technology |
|---|---|
| Cache | Redis |
| Idempotency | Redis |
| Gateway Health | Redis |

## Event Architecture

| Requirement | Technology |
|---|---|
| Message Broker | Apache Kafka |
| Python Client | kafka-python |

Kafka Topics:

payment-events  
fraud-alerts  
notification-events  
settlement-jobs

## Background Processing

| Requirement | Technology |
|---|---|
| Background Jobs | Celery |
| Scheduled Jobs | Celery Beat |
| Reconciliation | Celery + Celery Beat |

## AI Fraud Detection

| Requirement | Technology |
|---|---|
| Service | FastAPI |
| ML | XGBoost / scikit-learn |
| Decision | ALLOW / FLAG / BLOCK |

## Real-Time Communication

| Requirement | Technology |
|---|---|
| Framework | Django Channels |
| Protocol | WebSocket |

## Frontend

| Requirement | Technology |
|---|---|
| Framework | React |
| State Management | Redux |
| Styling | Tailwind CSS |
| API | REST |
| Real-Time | WebSocket |

## Testing

| Requirement | Technology |
|---|---|
| Testing | pytest |
| Django Testing | pytest-django |
| Mocking | unittest.mock |
| Integration Testing | testcontainers-python |

## Containerization

| Requirement | Technology |
|---|---|
| Containerization | Docker |
| Local Environment | Docker Compose |

## CI/CD

| Requirement | Technology |
|---|---|
| Platform | GitHub Actions |
| Build | Docker |
| Testing | pytest |

## Cloud

| Requirement | Technology |
|---|---|
| Cloud Platform | AWS |
| Containers | Docker |
| Database | PostgreSQL |
| Cache | Redis |
| Messaging | Kafka |

## Java to Python Mapping

| Java | Python |
|---|---|
| Java 21 | Python 3.12 |
| Spring Boot | Django |
| Spring Web | Django REST Framework |
| Spring Security | DRF SimpleJWT + Django Permissions |
| JPA / Hibernate | Django ORM |
| Spring Kafka | kafka-python |
| Spring Batch | Celery + Celery Beat |
| Spring WebSocket / STOMP | Django Channels + WebSocket |
| JUnit | pytest |
| Mockito | unittest.mock |
| TestContainers | testcontainers-python |

## Technology Decision

PayFlow AI will retain the original project's architecture and functionality while using Python-based technologies instead of Java and Spring Boot.