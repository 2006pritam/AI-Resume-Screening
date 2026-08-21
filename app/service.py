import json
import os
import sys
from typing import Dict, List, Any, Optional
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
        
        # If files are missing, automatically generate synthetic dataset
        if not os.path.exists(jobs_file) or not os.path.exists(resumes_file) or (os.path.exists(resumes_file) and os.path.getsize(resumes_file) < 50):
            try:
                from data_generator import generate_synthetic_dataset
                dataset = generate_synthetic_dataset(150)
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
        if job.id in self.cached_screenings:
            del self.cached_screenings[job.id]
        self._fit_vectorizer()
        return job

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

    def run_screening(self, job_id: str, force_refresh: bool = False) -> ScreeningResponse:
        if not force_refresh and job_id in self.cached_screenings:
            return self.cached_screenings[job_id]

        job = self.jobs.get(job_id)
        if not job:
            if self.jobs:
                job = list(self.jobs.values())[0]
            else:
                raise ValueError(f"Job ID '{job_id}' not found and no jobs available.")

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
            breakdown = self.matcher.calculate_match(cand, job)
            candidate_scores[cand.id] = breakdown.overall_score
            score_breakdowns[cand.id] = breakdown

        cand_profile_texts = [
            f"{' '.join(c.skills)} {' '.join(c.projects)} {c.education.degree} {c.education.field}"
            for c in candidate_list
        ]
        cand_vectors = self.vectorizer.encode(cand_profile_texts)

        vec_index = VectorIndex(cand_vectors.shape[1])
        vec_index.add([c.id for c in candidate_list], cand_vectors)

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

        self.cached_screenings[job_id] = response
        return response

    def filter_results(self, filter_req: ScreeningFilterRequest) -> ScreeningResponse:
        screening = self.run_screening(filter_req.job_id)
        filtered = list(screening.results)

        if filter_req.cluster_id is not None:
            filtered = [r for r in filtered if r.cluster_id == filter_req.cluster_id]

        if filter_req.min_score is not None:
            filtered = [r for r in filtered if r.score_breakdown.overall_score >= filter_req.min_score]

        if filter_req.min_exp is not None:
            filtered = [r for r in filtered if r.candidate.years_exp >= filter_req.min_exp]

        if filter_req.required_skills:
            req_set = {s.lower() for s in filter_req.required_skills}
            filtered = [
                r for r in filtered
                if req_set.issubset({s.lower() for s in r.candidate.skills})
            ]

        if filter_req.search_query:
            q = filter_req.search_query.lower()
            filtered = [
                r for r in filtered
                if q in r.candidate.name.lower() or
                   q in (r.candidate.email or "").lower() or
                   any(q in s.lower() for s in r.candidate.skills) or
                   any(q in c.lower() for c in r.candidate.companies)
            ]

        filtered = filtered[:filter_req.limit]

        return ScreeningResponse(
            job_id=screening.job_id,
            job_title=screening.job_title,
            total_candidates_screened=screening.total_candidates_screened,
            shortlisted_count=len([r for r in filtered if r.score_breakdown.overall_score >= 70.0]),
            clusters=screening.clusters,
            results=filtered
        )
