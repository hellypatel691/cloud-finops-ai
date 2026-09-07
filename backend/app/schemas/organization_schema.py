from pydantic import BaseModel, Field, ConfigDict


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
