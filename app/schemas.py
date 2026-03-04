from pydantic import BaseModel, Field
from typing import List

class PlannerOut(BaseModel):
    search_queries: List[str] = Field(..., min_length=1, max_length=4)
    must_answer: List[str] = Field(default_factory=list)
    excluded: List[str] = Field(default_factory=list)

class Source(BaseModel):
    url: str
    title: str
    publisher: str
    published_date: str  # required ("" allowed)

class Claim(BaseModel):
    claim: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    citations: List[Source] = Field(default_factory=list)

class ResearchReport(BaseModel):
    # changed from one big string to short bullet strings
    answer_bullets: List[str] = Field(..., min_length=3, max_length=12)
    claims: List[Claim] = Field(..., min_length=1, max_length=8)
    sources: List[Source] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)