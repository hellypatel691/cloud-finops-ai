# Decision 001

## Title
Why we chose FastAPI over Node.js

## Decision
We chose FastAPI because the backend and machine learning models are both implemented in Python. This avoids maintaining separate Node.js and Python services, simplifies deployment, and allows tighter integration between APIs and ML pipelines.

## Consequences
- Easier ML integration
- Single backend language
- Faster development
- Smaller deployment complexity

Decision 002
Title

Why FastAPI instead of Flask

Decision

FastAPI provides automatic API documentation, type validation using Pydantic, asynchronous support, and better performance. Since our project integrates machine learning models written in Python, FastAPI offers a clean and efficient architecture.

Consequences

+ Faster APIs

+ Swagger UI

+ Better developer experience

+ Easier deployment

Decision 003

Title

Why Repository Pattern?

Decision

Repositories separate database operations from business logic, making the application easier to test, maintain, and extend.

Consequences

Database technology can change without affecting API logic.

Improved maintainability.

Better testing.

# Decision 004

Title

Why Alembic?

Decision

Database schema changes will be managed using Alembic migrations instead of SQLAlchemy create_all().

Reason

This enables version control of database schema, supports production deployments, and allows multiple developers to collaborate safely.

Consequences

- Reproducible database changes
- Rollback capability
- Production-ready workflow