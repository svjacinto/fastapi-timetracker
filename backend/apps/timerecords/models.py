from datetime import date, datetime
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field

class TimeRecordModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    clock_in: datetime
    clock_out: Optional[datetime]
    employee: EmailStr
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "00010203-0405-0607-0809-0a0b0c0d0e0f",
                "clock_in": "2022-03-17T08:01:48.588Z",
                "clock_out": "2022-03-18T08:01:48.588Z",
                "employee": "user@example.com"
            }
        }
    
class UpdateTimeRecordModel(BaseModel):
    clock_in: Optional[datetime]
    clock_out: Optional[datetime]
    
    class Config:
        schema_extra = {
            "example": {
                "clock_in": "2022-03-17T08:01:48.588Z",
                "clock_out": "2022-03-18T08:01:48.588Z",
            }
        }
    
    
    
