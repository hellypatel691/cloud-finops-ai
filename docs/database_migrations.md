# Database Migrations

We use Alembic to version-control the PostgreSQL schema.

Workflow:

1. Modify SQLAlchemy models.
2. Generate migration:

alembic revision --autogenerate -m "message"

3. Apply migration:

alembic upgrade head

Benefits

- Version controlled schema
- Safe production updates
- Team collaboration