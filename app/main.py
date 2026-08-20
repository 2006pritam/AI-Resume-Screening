import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List

from app.schemas import (
    Candidate, JobDescription, ScreeningResponse,
    ScreeningFilterRequest, ResumeUploadRequest
)
from app.service import ScreeningService

app = FastAPI(
    title="AI Resume Screening & Candidate Clustering API",
    description="High-throughput explainable candidate screening, structured NER extraction, and skill archetype clustering.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ScreeningService()

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "total_jobs": len(service.jobs),
        "total_candidates": len(service.candidates),
        "vectorizer_type": "SentenceTransformer" if service.vectorizer.use_st else "Normalized TF-IDF + Subword"
    }

@app.get("/api/jobs", response_model=List[JobDescription])
def list_jobs():
    return service.get_all_jobs()

@app.get("/api/jobs/{job_id}", response_model=JobDescription)
def get_job(job_id: str):
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job

@app.post("/api/jobs", response_model=JobDescription)
def create_job(job: JobDescription):
    return service.add_job(job)

@app.post("/api/screen", response_model=ScreeningResponse)
def screen_resumes(job_id: str = Query(..., description="The ID of the job to screen resumes against")):
    try:
        return service.run_screening(job_id=job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/filter", response_model=ScreeningResponse)
def filter_candidates(filter_req: ScreeningFilterRequest):
    try:
        return service.filter_results(filter_req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/candidates/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str):
    cand = service.candidates.get(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")
    return cand

@app.post("/api/resumes", response_model=Candidate)
def upload_resume(req: ResumeUploadRequest):
    return service.add_resume(
        raw_text=req.raw_text,
        candidate_name=req.candidate_name,
        email=req.email
    )

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>AI Resume Screening & Candidate Clustering Dashboard</h1>"
