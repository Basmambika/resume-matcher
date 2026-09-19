from typing import List, Optional
from pydantic import BaseModel


class ParsedDocumentResponse(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    degrees: List[str] = []
    years_experience: Optional[int] = None


class SuggestionResponse(BaseModel):
    category: str
    priority: str
    message: str


class MatchResponse(BaseModel):
    overall_score: float
    text_similarity: float
    skill_overlap_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[SuggestionResponse] = []


class JobDescriptionRequest(BaseModel):
    job_text: str