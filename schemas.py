# schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum

class EvaluationParameter(str, Enum):
    CLARITY = 'clarity'
    COHERENCE = 'coherence'
    CONCISENESS = 'conciseness'
    GRAMMAR = 'grammar'

class EvaluationRequest(BaseModel):
    lecture_transcript: str = Field(
        ..., 
        min_length=100, 
        description="The full text of the lecture transcript."
    )
    student_summary: str = Field(
        ..., 
        min_length=20, 
        description="The summary written by the student."
    )
    evaluation_parameters: List[EvaluationParameter] = Field(
        ...,
        description="A list of qualitative parameters to evaluate."
    )

class IndividualScore(BaseModel):
    score: float = Field(..., ge=0, le=10, description="The score for this specific parameter (out of 10).")
    explanation: str = Field("", description="A brief explanation for the score, if applicable.")

class EvaluationResponse(BaseModel):
    final_score: float = Field(
        ..., 
        ge=0, 
        le=10, 
        description="The final aggregated score for the summary, normalized to 10."
    )
    feedback: str = Field(
        ...,
        description="Detailed, human-readable feedback on the summary's strengths and areas for improvement."
    )
    individual_scores: Dict[str, IndividualScore] = Field(
        ...,
        description="A breakdown of scores for each evaluated parameter."
    )
