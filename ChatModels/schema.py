from typing import List
from pydantic import BaseModel, Field

class BookingAnswer(BaseModel):
    steps: List[str] = Field(description="Steps to book a tour")
