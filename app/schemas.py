from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Education(BaseModel):
    degree: str
    level: str = "Bachelor"  # Doctorate, Master, Bachelor, Associate, Bootcamp
    field: Optional[str] = "Computer Science"
    institution: Optional[str] = None

class Candidate(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    years_exp: float
    skills: List[str]
    education: Education
    companies: List[str] = []
    projects: List[str] = []
    archetype: Optional[str] = None
    raw_text: Optional[str] = None

class JobDescription(BaseModel):
    id: str
    title: str
    department: Optional[str] = "Engineering"
    min_experience_years: float = 3.0
    required_skills: List[str]
    preferred_skills: List[str] = []
    min_education: str = "Bachelor"
    description: Optional[str] = ""
    responsibilities: List[str] = []

class ScoreBreakdown(BaseModel):
    overall_score: float = Field(..., description="Final calibrated score from 0 to 100")
    skill_score: float = Field(..., description="Score based on required and preferred skill overlap (0-100)")
    experience_score: float = Field(..., description="Score based on years of experience vs job requirements (0-100)")
    education_score: float = Field(..., description="Score based on degree level and field alignment (0-100)")
    project_score: float = Field(..., description="Score based on semantic relevance of projects/work history (0-100)")
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_preferred_skills: List[str]
    experience_delta: float
    education_fit: str
    explanation_highlights: List[str]
    strengths: List[str]
    gap_analysis: List[str]

class CandidateScreeningResult(BaseModel):
    candidate: Candidate
    score_breakdown: ScoreBreakdown
    cluster_id: int
    cluster_name: str
    rank: int

class ClusterSummary(BaseModel):
    cluster_id: int
    cluster_name: str
    candidate_count: int
    avg_experience: float
    avg_score: float
    top_dominant_skills: List[Dict[str, Any]]
    representative_keywords: List[str]
    top_candidate_ids: List[str]
    shortlist_recommendation: str

class ScreeningResponse(BaseModel):
    job_id: str
    job_title: str
    total_candidates_screened: int
    shortlisted_count: int
    clusters: List[ClusterSummary]
    results: List[CandidateScreeningResult]

class ScreeningFilterRequest(BaseModel):
    job_id: str
    cluster_id: Optional[int] = None
    min_score: Optional[float] = None
    min_exp: Optional[float] = None
    required_skills: Optional[List[str]] = None
    search_query: Optional[str] = None
    limit: int = 100

class ResumeUploadRequest(BaseModel):
    raw_text: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
