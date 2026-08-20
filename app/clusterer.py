import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
from app.schemas import Candidate, ClusterSummary

class CandidateClusterer:
    def __init__(self, n_clusters: int = 4, max_iter: int = 50):
        self.n_clusters = n_clusters
        self.max_iter = max_iter

    def _kmeans_numpy(self, X: np.ndarray, k: int) -> np.ndarray:
        n_samples, n_features = X.shape
        if n_samples <= k:
            return np.arange(n_samples)

        rng = np.random.RandomState(42)
        centroids = [X[rng.choice(n_samples)]]
        
        for _ in range(1, k):
            dist_sq = np.array([min([np.inner(c - x, c - x) for c in centroids]) for x in X])
            probs = dist_sq / (dist_sq.sum() + 1e-9)
            next_idx = rng.choice(n_samples, p=probs)
            centroids.append(X[next_idx])
            
        centroids = np.array(centroids)

        labels = np.zeros(n_samples, dtype=int)
        for _ in range(self.max_iter):
            distances = np.linalg.norm(X[:, np.newaxis] - centroids, axis=2)
            new_labels = np.argmin(distances, axis=1)
            
            if np.array_equal(labels, new_labels):
                break
            labels = new_labels
            
            for i in range(k):
                members = X[labels == i]
                if len(members) > 0:
                    centroids[i] = members.mean(axis=0)

        return labels

    def _generate_cluster_name(self, top_skills: List[str], avg_exp: float) -> str:
        skills_lower = [s.lower() for s in top_skills]
        
        if any("selenium" in s or "cypress" in s or "test" in s or "qa" in s for s in skills_lower):
            if any("python" in s for s in skills_lower):
                return "QA Automation & Python Specialists"
            return "QA Automation & Modern Web Testers"
        elif any("tableau" in s or "data analysis" in s or "bi" in s for s in skills_lower):
            return "Data Analytics & BI Specialists"
        elif any("snowflake" in s or "dbt" in s or "airflow" in s for s in skills_lower):
            return "Data Engineering & Pipeline Specialists"
        elif any("react" in s for s in skills_lower) and any("node" in s or "express" in s or "mongo" in s for s in skills_lower):
            return "Fullstack MERN Engineers"
        elif any("react" in s or "typescript" in s or "next.js" in s for s in skills_lower):
            if any("typescript" in s for s in skills_lower):
                return "React & TypeScript Frontend Specialists"
            return "Modern Frontend & UI Engineers"
        elif any("node" in s or "nestjs" in s or "postgres" in s for s in skills_lower):
            return "Node.js & Backend Architecture"
        else:
            if top_skills:
                top_str = " + ".join(top_skills[:2])
                return f"{top_str} Talent Cohort"
            return "General Software Engineering Cohort"

    def _generate_recommendation(self, cluster_name: str, avg_score: float, top_skills: List[str]) -> str:
        if avg_score >= 75.0:
            return f"Primary candidate pool for immediate recruiter shortlisting. High density of {', '.join(top_skills[:3])}."
        elif avg_score >= 50.0:
            return f"Strong secondary pool with valuable adjacent capabilities in {', '.join(top_skills[:2])}."
        else:
            return f"Alternative skill profile cohort, suitable for cross-functional or hybrid staffing requirements."

    def cluster_candidates(
        self,
        candidates: List[Candidate],
        candidate_vectors: np.ndarray,
        candidate_scores: Dict[str, float]
    ) -> Tuple[List[int], List[ClusterSummary]]:
        
        n_candidates = len(candidates)
        if n_candidates == 0:
            return [], []

        k = min(self.n_clusters, n_candidates)
        if n_candidates >= 100:
            k = 5
        elif n_candidates >= 50:
            k = 4
        else:
            k = max(2, min(3, n_candidates))

        labels = self._kmeans_numpy(candidate_vectors, k)

        cluster_summaries = []
        for c_id in range(k):
            indices = np.where(labels == c_id)[0]
            cluster_cands = [candidates[i] for i in indices]
            count = len(cluster_cands)
            
            if count == 0:
                continue

            avg_exp = round(float(np.mean([c.years_exp for c in cluster_cands])), 1)
            scores = [candidate_scores.get(c.id, 0.0) for c in cluster_cands]
            avg_score = round(float(np.mean(scores)), 1)

            all_skills = []
            for c in cluster_cands:
                all_skills.extend(c.skills)
            skill_counts = Counter(all_skills)
            
            top_dominant = [
                {"skill": skill, "count": cnt, "percentage": round((cnt / count) * 100, 1)}
                for skill, cnt in skill_counts.most_common(6)
            ]
            top_skill_names = [item["skill"] for item in top_dominant]

            proj_words = []
            for c in cluster_cands:
                for p in c.projects:
                    proj_words.extend([w.strip(".,()") for w in p.split() if len(w) > 4])
            top_keywords = [w for w, _ in Counter(proj_words).most_common(5)]

            ranked_in_cluster = sorted(cluster_cands, key=lambda c: candidate_scores.get(c.id, 0.0), reverse=True)
            top_cand_ids = [c.id for c in ranked_in_cluster[:5]]

            cluster_name = self._generate_cluster_name(top_skill_names, avg_exp)
            recommendation = self._generate_recommendation(cluster_name, avg_score, top_skill_names)

            summary = ClusterSummary(
                cluster_id=c_id,
                cluster_name=cluster_name,
                candidate_count=count,
                avg_experience=avg_exp,
                avg_score=avg_score,
                top_dominant_skills=top_dominant,
                representative_keywords=top_keywords,
                top_candidate_ids=top_cand_ids,
                shortlist_recommendation=recommendation
            )
            cluster_summaries.append(summary)

        cluster_summaries.sort(key=lambda cs: cs.avg_score, reverse=True)
        id_map = {old_summary.cluster_id: new_idx for new_idx, old_summary in enumerate(cluster_summaries)}
        for new_idx, cs in enumerate(cluster_summaries):
            cs.cluster_id = new_idx
            
        final_labels = [id_map.get(l, 0) for l in labels]

        return final_labels, cluster_summaries
