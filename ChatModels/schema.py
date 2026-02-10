from typing import List, Optional
from pydantic import BaseModel, Field

class ChatbotAnswer(BaseModel):
    """
    Structured response from travel chatbot
    """

    answer: str = Field(description="Main chatbot answer in bullet points")
    source: Optional[str] = Field(default=None, description="Source of information (PDF / Knowledge Base)")
    confidence: Optional[float] = Field(default=None, description="Confidence score of answer (0 to 1)")
