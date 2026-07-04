from app.database.database import engine
from app.models.base import Base

# Import all models
from app.models.organization import Organization

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully!")