import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from app.schemas import (
    Candidate, JobDescription, ScreeningResponse,
    CandidateScreeningResult, ClusterSummary, ScoreBreakdown,
    ScreeningFilterRequest
)
from app.extractor import ResumeExtractor
from app.vectorizer import TextVectorizer, VectorIndex
from app.matcher import ExplainableMatcher
from app.clusterer import CandidateClusterer
from app.file_parser import extract_text_from_file

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class ScreeningService:
    def __init__(self):
        self.extractor = ResumeExtractor()
        self.vectorizer = TextVectorizer()
        self.matcher = ExplainableMatcher(self.vectorizer)
        self.clusterer = CandidateClusterer(n_clusters=5)
        
        self.jobs: Dict[str, JobDescription] = {}
        self.candidates: Dict[str, Candidate] = {}
        self.cached_screenings: Dict[str, ScreeningResponse] = {}
        
        self._load_initial_data()
        self._fit_vectorizer()

    def _load_initial_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        jobs_file = os.path.join(DATA_DIR, "jobs.json")
        resumes_file = os.path.join(DATA_DIR, "resumes.json")
        
        if not os.path.exists(jobs_file) or not os.path.exists(resumes_file) or (os.path.exists(resumes_file) and os.path.getsize(resumes_file) < 50):
            try:
                from data_generator import generate_synthetic_dataset
                dataset = generate_synthetic_dataset(160)
                with open(jobs_file, "w") as f:
                    json.dump(dataset["jobs"], f, indent=2)
                with open(resumes_file, "w") as f:
                    json.dump(dataset["resumes"], f, indent=2)
            except Exception as e:
                print(f"Warning: Auto-generation fallback: {e}")
                
        if os.path.exists(jobs_file):
            with open(jobs_file, "r") as f:
                jobs_data = json.load(f)
                for j_id, j_val in jobs_data.items():
                    self.jobs[j_id] = JobDescription(**j_val)
                    
        if os.path.exists(resumes_file):
            with open(resumes_file, "r") as f:
                resumes_data = json.load(f)
                for r in resumes_data:
                    self.candidates[r["id"]] = Candidate(**r)

    def _fit_vectorizer(self):
        docs = []
        for c in self.candidates.values():
            docs.append(f"{' '.join(c.skills)} {' '.join(c.projects)} {c.education.degree}")
        for j in self.jobs.values():
            docs.append(f"{j.title} {j.description} {' '.join(j.required_skills)} {' '.join(j.responsibilities)}")
            
        if docs:
            self.vectorizer.fit(docs)

    def get_all_jobs(self) -> List[JobDescription]:
        return list(self.jobs.values())

    def get_job(self, job_id: str) -> Optional[JobDescription]:
        return self.jobs.get(job_id)

    def add_job(self, job: JobDescription) -> JobDescription:
        self.jobs[job.id] = job
        self.cached_screenings.clear()
        self._fit_vectorizer()
        return job

    def clear_all_candidates(self):
        self.candidates.clear()
        self.cached_screenings.clear()
        resumes_file = os.path.join(DATA_DIR, "resumes.json")
        if os.path.exists(resumes_file):
            with open(resumes_file, "w") as f:
                json.dump([], f)
        self._fit_vectorizer()

    def regenerate_fresh_dataset(self, num_candidates: int = 160):
        from data_generator import generate_synthetic_dataset
        dataset = generate_synthetic_dataset(num_candidates)
        
        jobs_file = os.path.join(DATA_DIR, "jobs.json")
        resumes_file = os.path.join(DATA_DIR, "resumes.json")
        
        with open(jobs_file, "w") as f:
            json.dump(dataset["jobs"], f, indent=2)
        with open(resumes_file, "w") as f:
            json.dump(dataset["resumes"], f, indent=2)
            
        self.jobs.clear()
        self.candidates.clear()
        self.cached_screenings.clear()
        
        for j_id, j_val in dataset["jobs"].items():
            self.jobs[j_id] = JobDescription(**j_val)
        for r in dataset["resumes"]:
            self.candidates[r["id"]] = Candidate(**r)
            
        self._fit_vectorizer()

    def add_resume(self, raw_text: str, candidate_name: Optional[str] = None, email: Optional[str] = None) -> Candidate:
        cand_id = f"cand_{len(self.candidates) + 1:03d}"
        extracted = self.extractor.extract_structured_candidate(
            raw_text=raw_text,
            candidate_id=cand_id,
            name=candidate_name,
            email=email
        )
        cand = Candidate(**extracted)
        self.candidates[cand.id] = cand
        self.cached_screenings.clear()
        self._fit_vectorizer()
        return cand

    def add_resume_file(self, file_bytes: bytes, filename: str) -> Candidate:
        raw_text = extract_text_from_file(file_bytes, filename)
        if not raw_text.strip():
            raw_text = f"Resume file: {filename}\nSkills: Software Engineering, Git, Problem Solving"
        base_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        return self.add_resume(raw_text=raw_text, candidate_name=base_name)

    def run_screening(
        self,
        job_id: str,
        skill_weight: float = 0.45,
        exp_weight: float = 0.25,
        edu_weight: float = 0.15,
        project_weight: float = 0.15,
        n_clusters: int = 5,
        strict_core_skills: bool = False,
        force_refresh: bool = False
    ) -> ScreeningResponse:
        
        cache_key = f"{job_id}_{skill_weight}_{exp_weight}_{edu_weight}_{project_weight}_{n_clusters}_{strict_core_skills}"
        if not force_refresh and cache_key in self.cached_screenings:
            return self.cached_screenings[cache_key]

        job = self.jobs.get(job_id)
        if not job:
            if self.jobs:
                job = list(self.jobs.values())[0]
            else:
                raise ValueError(f"Job ID '{job_id}' not found.")

        candidate_list = list(self.candidates.values())
        if not candidate_list:
            return ScreeningResponse(
                job_id=job.id,
                job_title=job.title,
                total_candidates_screened=0,
                shortlisted_count=0,
                clusters=[],
                results=[]
            )

        candidate_scores: Dict[str, float] = {}
        score_breakdowns: Dict[str, ScoreBreakdown] = {}

        for cand in candidate_list:
            breakdown = self.matcher.calculate_match(
                candidate=cand,
                job=job,
                skill_weight=skill_weight,
                exp_weight=exp_weight,
                edu_weight=edu_weight,
                project_weight=project_weight,
                strict_core_skills=strict_core_skills
            )
            candidate_scores[cand.id] = breakdown.overall_score
            score_breakdowns[cand.id] = breakdown

        cand_profile_texts = [
            f"{' '.join(c.skills)} {' '.join(c.projects)} {c.education.degree} {c.education.field}"
            for c in candidate_list
        ]
        cand_vectors = self.vectorizer.encode(cand_profile_texts)

        vec_index = VectorIndex(cand_vectors.shape[1])
        vec_index.add([c.id for c in candidate_list], cand_vectors)

        self.clusterer.n_clusters = max(2, min(8, n_clusters))
        labels, cluster_summaries = self.clusterer.cluster_candidates(
            candidates=candidate_list,
            candidate_vectors=cand_vectors,
            candidate_scores=candidate_scores
        )

        cluster_map = {cluster_list_idx: cluster_summaries[cluster_list_idx].cluster_name for cluster_list_idx in range(len(cluster_summaries))}

        unsorted_results = []
        for idx, cand in enumerate(candidate_list):
            cluster_id = labels[idx] if idx < len(labels) else 0
            cluster_name = cluster_map.get(cluster_id, "General Talent Cohort")
            
            unsorted_results.append({
                "candidate": cand,
                "score_breakdown": score_breakdowns[cand.id],
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "overall_score": score_breakdowns[cand.id].overall_score
            })

        unsorted_results.sort(key=lambda x: x["overall_score"], reverse=True)

        final_results: List[CandidateScreeningResult] = []
        for rank_idx, item in enumerate(unsorted_results, start=1):
            final_results.append(
                CandidateScreeningResult(
                    candidate=item["candidate"],
                    score_breakdown=item["score_breakdown"],
                    cluster_id=item["cluster_id"],
                    cluster_name=item["cluster_name"],
                    rank=rank_idx
                )
            )

        shortlisted = [r for r in final_results if r.score_breakdown.overall_score >= 70.0]

        response = ScreeningResponse(
            job_id=job.id,
            job_title=job.title,
            total_candidates_screened=len(final_results),
            shortlisted_count=len(shortlisted),
            clusters=cluster_summaries,
            results=final_results
        )

        self.cached_screenings[cache_key] = response
        return response
