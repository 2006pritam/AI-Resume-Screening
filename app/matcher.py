from typing import Dict, Any, List, Tuple
from app.schemas import Candidate, JobDescription, ScoreBreakdown
from app.vectorizer import TextVectorizer
import numpy as np

DEGREE_SCORES = {
    "Doctorate": 100.0,
    "Master": 95.0,
    "Bachelor": 90.0,
    "Associate": 75.0,
    "Bootcamp": 70.0
}

FIELD_WEIGHTS = {
    "Computer Science": 1.0,
    "Information Technology": 1.0,
    "Data Science": 1.0,
    "Software Engineering": 1.0,
    "Engineering": 0.9,
    "Mathematics": 0.85,
    "Other": 0.75
}

class ExplainableMatcher:
    def __init__(self, vectorizer: TextVectorizer):
        self.vectorizer = vectorizer

    def _normalize_skill(self, s: str) -> str:
        return s.strip().lower()

    def evaluate_skills(self, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> Tuple[float, List[str], List[str], List[str]]:
        cand_set = {self._normalize_skill(s): s for s in candidate_skills}
        
        matched_req = []
        missing_req = []
        for req in required_skills:
            req_norm = self._normalize_skill(req)
            if req_norm in cand_set:
                matched_req.append(req)
            else:
                matched = False
                for c_norm, original in cand_set.items():
                    if req_norm in c_norm or c_norm in req_norm:
                        matched_req.append(req)
                        matched = True
                        break
                if not matched:
                    missing_req.append(req)

        matched_pref = []
        for pref in preferred_skills:
            pref_norm = self._normalize_skill(pref)
            if pref_norm in cand_set:
                matched_pref.append(pref)
            else:
                for c_norm, original in cand_set.items():
                    if pref_norm in c_norm or c_norm in pref_norm:
                        matched_pref.append(pref)
                        break

        req_ratio = len(matched_req) / max(len(required_skills), 1)
        req_score = req_ratio * 100.0

        pref_ratio = len(matched_pref) / max(len(preferred_skills), 1) if preferred_skills else 0.0
        pref_bonus = pref_ratio * 20.0

        skill_score = min(100.0, req_score * 0.85 + pref_bonus)
        return skill_score, matched_req, missing_req, matched_pref

    def evaluate_experience(self, cand_years: float, req_years: float) -> Tuple[float, float]:
        delta = cand_years - req_years
        if delta >= 0:
            score = 90.0 + min(10.0, delta * 2.5)
        else:
            ratio = cand_years / max(req_years, 0.5)
            score = max(10.0, ratio * 85.0)
            
        return round(min(100.0, score), 1), round(delta, 1)

    def evaluate_education(self, cand_edu: Dict[str, Any], min_level: str) -> Tuple[float, str]:
        level = cand_edu.get("level", "Bachelor")
        field = cand_edu.get("field", "Computer Science")
        
        base_score = DEGREE_SCORES.get(level, 80.0)
        field_mult = FIELD_WEIGHTS.get(field, 0.8)
        final_edu_score = round(base_score * field_mult, 1)
        
        fit_desc = f"{cand_edu.get('degree', level)} ({level})"
        return final_edu_score, fit_desc

    def evaluate_project_relevance(self, cand_projects: List[str], job_text: str) -> float:
        if not cand_projects:
            return 50.0
        
        cand_text = " ".join(cand_projects)
        vecs = self.vectorizer.encode([cand_text, job_text])
        sim = float(np.dot(vecs[0], vecs[1]))
        
        project_score = max(20.0, min(100.0, (sim + 0.2) * 80.0))
        return round(project_score, 1)

    def calculate_match(self, candidate: Candidate, job: JobDescription) -> ScoreBreakdown:
        skill_score, matched_req, missing_req, matched_pref = self.evaluate_skills(
            candidate.skills, job.required_skills, job.preferred_skills
        )
        
        exp_score, exp_delta = self.evaluate_experience(
            candidate.years_exp, job.min_experience_years
        )
        
        edu_dict = candidate.education.model_dump() if hasattr(candidate.education, "model_dump") else candidate.education.dict()
        edu_score, edu_fit = self.evaluate_education(edu_dict, job.min_education)
        
        job_full_text = f"{job.title} {job.description} {' '.join(job.responsibilities)} {' '.join(job.required_skills)}"
        project_score = self.evaluate_project_relevance(candidate.projects, job_full_text)
        
        overall = (
            (skill_score * 0.45) +
            (exp_score * 0.25) +
            (edu_score * 0.15) +
            (project_score * 0.15)
        )
        overall_score = round(min(100.0, max(0.0, overall)), 1)
        
        highlights = []
        strengths = []
        gaps = []
        
        req_pct = int((len(matched_req) / max(len(job.required_skills), 1)) * 100)
        highlights.append(f"Matched {len(matched_req)}/{len(job.required_skills)} required skills ({req_pct}% coverage).")
        
        if exp_delta >= 0:
            highlights.append(f"Exceeds experience target by +{exp_delta} yrs ({candidate.years_exp} yrs total vs {job.min_experience_years} yrs required).")
            strengths.append(f"Solid experience seniority ({candidate.years_exp} yrs)")
        else:
            highlights.append(f"Experience is {abs(exp_delta)} yrs below requirement ({candidate.years_exp} yrs vs {job.min_experience_years} yrs).")
            gaps.append(f"Years of experience below target ({candidate.years_exp} vs {job.min_experience_years} yrs)")
            
        if matched_req:
            strengths.append(f"Core skills: {', '.join(matched_req[:4])}")
        if matched_pref:
            strengths.append(f"Bonus preferred skills: {', '.join(matched_pref)}")
        if missing_req:
            gaps.append(f"Missing required skills: {', '.join(missing_req)}")
            
        if candidate.companies:
            strengths.append(f"Prior experience at reputable companies: {', '.join(candidate.companies[:3])}")
            
        return ScoreBreakdown(
            overall_score=overall_score,
            skill_score=round(skill_score, 1),
            experience_score=exp_score,
            education_score=edu_score,
            project_score=project_score,
            matched_required_skills=matched_req,
            missing_required_skills=missing_req,
            matched_preferred_skills=matched_pref,
            experience_delta=exp_delta,
            education_fit=edu_fit,
            explanation_highlights=highlights,
            strengths=strengths,
            gap_analysis=gaps
        )
