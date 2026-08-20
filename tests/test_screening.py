import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.extractor import ResumeExtractor
from app.vectorizer import TextVectorizer
from app.matcher import ExplainableMatcher
from app.clusterer import CandidateClusterer
from app.schemas import Candidate, Education, JobDescription, ScreeningFilterRequest
from app.service import ScreeningService

class TestResumeScreening(unittest.TestCase):
    def setUp(self):
        self.extractor = ResumeExtractor()
        self.vectorizer = TextVectorizer()
        self.matcher = ExplainableMatcher(self.vectorizer)
        self.clusterer = CandidateClusterer(n_clusters=3)
        self.service = ScreeningService()

    def test_structured_extraction(self):
        raw_text = """
        John Doe
        Email: john.doe@example.com
        Experience: 6.5 Years of experience in fullstack development
        Skills: React, TypeScript, Redux, Node.js, Express, PostgreSQL, Docker
        Education: B.Tech in Information Technology from IIT
        Companies: TCS, Amazon
        Projects:
        - Built high-traffic React dashboard with TypeScript and Redux.
        - Designed PostgreSQL backend services in Node.js.
        """
        cand_dict = self.extractor.extract_structured_candidate(raw_text, "cand_test_01")
        self.assertEqual(cand_dict["name"], "John Doe")
        self.assertEqual(cand_dict["email"], "john.doe@example.com")
        self.assertAlmostEqual(cand_dict["years_exp"], 6.5)
        self.assertIn("React", cand_dict["skills"])
        self.assertIn("TypeScript", cand_dict["skills"])
        self.assertIn("PostgreSQL", cand_dict["skills"])
        self.assertEqual(cand_dict["education"]["level"], "Bachelor")

    def test_explainable_scoring(self):
        cand = Candidate(
            id="c_test",
            name="Alice Smith",
            years_exp=5.0,
            skills=["React", "TypeScript", "Redux", "Next.js", "Jest"],
            education=Education(degree="B.Tech Computer Science", level="Bachelor", field="Computer Science"),
            projects=["Architected React application with TypeScript and state management."]
        )
        job = JobDescription(
            id="job_test",
            title="Senior React Developer",
            min_experience_years=4.0,
            required_skills=["React", "TypeScript", "Redux"],
            preferred_skills=["Next.js", "Jest"],
            min_education="Bachelor",
            description="Need React developer",
            responsibilities=["Develop UI components"]
        )
        breakdown = self.matcher.calculate_match(cand, job)
        self.assertGreaterEqual(breakdown.overall_score, 80.0)
        self.assertEqual(len(breakdown.missing_required_skills), 0)
        self.assertEqual(len(breakdown.matched_required_skills), 3)
        self.assertGreaterEqual(len(breakdown.explanation_highlights), 2)

    def test_end_to_end_screening_service(self):
        res = self.service.run_screening("job_react_dev")
        self.assertGreater(res.total_candidates_screened, 50)
        self.assertGreater(res.shortlisted_count, 0)
        self.assertGreaterEqual(len(res.clusters), 2)
        
        scores = [r.score_breakdown.overall_score for r in res.results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_filtering(self):
        filter_req = ScreeningFilterRequest(
            job_id="job_react_dev",
            min_score=75.0,
            min_exp=4.0
        )
        res = self.service.filter_results(filter_req)
        for r in res.results:
            self.assertGreaterEqual(r.score_breakdown.overall_score, 75.0)
            self.assertGreaterEqual(r.candidate.years_exp, 4.0)

if __name__ == "__main__":
    unittest.main()
