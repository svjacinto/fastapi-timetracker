import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class EmployeeModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    lastname: str
    firstname: str
    email: EmailStr

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "00010203-0405-0607-0809-0a0b0c0d0e0f",
                "lastname": "Jackson",
                "firstname": "Percy",
                "email": "percyjackson@example.com"
            }
        }


class UpdateEmployeeModel(BaseModel):
    lastname: Optional[str]
    firstname: Optional[str]
    email: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "lastname": "Jackson",
                "firstname": "Percy",
                "email": "percyjackson@example.com"
            }
        }