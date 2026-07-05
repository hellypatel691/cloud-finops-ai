from pydantic import BaseModel


class OrganizationCreate(BaseModel):

    name: str

    description: str


class OrganizationResponse(BaseModel):

    id: int

    name: str

    description: str

    class Config:
        from_attributes = True