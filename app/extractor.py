import re
from typing import List, Dict, Any, Optional

SKILL_TAXONOMY = {
    "react": "React", "react.js": "React", "reactjs": "React",
    "typescript": "TypeScript", "ts": "TypeScript",
    "javascript": "JavaScript", "js": "JavaScript", "es6": "JavaScript",
    "html": "HTML/CSS", "css": "HTML/CSS", "html/css": "HTML/CSS", "html5": "HTML/CSS", "css3": "HTML/CSS",
    "redux": "Redux", "redux toolkit": "Redux",
    "next.js": "Next.js", "nextjs": "Next.js", "next": "Next.js",
    "tailwind": "Tailwind CSS", "tailwind css": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "graphql": "GraphQL",
    "rest": "REST APIs", "rest apis": "REST APIs", "restful api": "REST APIs", "rest api": "REST APIs",
    "jest": "Jest", "react testing library": "Jest", "unit testing": "Jest",
    "node": "Node.js", "node.js": "Node.js", "nodejs": "Node.js",
    "express": "Express", "express.js": "Express", "expressjs": "Express",
    "nestjs": "NestJS", "nest.js": "NestJS",
    "mongodb": "MongoDB", "mongo": "MongoDB",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "redis": "Redis",
    "docker": "Docker", "containerization": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "aws": "AWS", "amazon web services": "AWS",
    "kafka": "Kafka", "apache kafka": "Kafka",
    "microservices": "Microservices",
    "selenium": "Selenium", "selenium webdriver": "Selenium",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "pytest": "PyTest",
    "postman": "Postman",
    "jenkins": "Jenkins",
    "jira": "Jira",
    "git": "Git", "github": "Git", "gitlab": "Git",
    "ci/cd": "CI/CD", "cicd": "CI/CD", "continuous integration": "CI/CD",
    "python": "Python", "python 3": "Python",
    "sql": "SQL", "t-sql": "SQL", "pl/sql": "SQL",
    "tableau": "Tableau",
    "power bi": "Power BI", "powerbi": "Power BI",
    "excel": "Excel", "ms excel": "Excel", "vba": "Excel",
    "data analysis": "Data Analysis", "exploratory data analysis": "Data Analysis", "eda": "Data Analysis",
    "data visualization": "Data Visualization",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
    "statistics": "Statistics",
    "snowflake": "Snowflake",
    "dbt": "dbt",
    "airflow": "Airflow", "apache airflow": "Airflow",
    "spark": "Spark", "apache spark": "Spark", "pyspark": "Spark",
    "webpack": "Webpack",
    "vite": "Vite",
    "figma": "Figma",
    "jwt": "JWT Authentication", "jwt authentication": "JWT Authentication"
}

DEGREE_LEVELS = {
    "phd": "Doctorate", "doctorate": "Doctorate", "ph.d": "Doctorate",
    "master": "Master", "m.tech": "Master", "msc": "Master", "ms": "Master", "mca": "Master", "m.e.": "Master",
    "bachelor": "Bachelor", "b.tech": "Bachelor", "bsc": "Bachelor", "bs": "Bachelor", "bca": "Bachelor", "b.e.": "Bachelor",
    "bootcamp": "Bootcamp", "diploma": "Associate", "associate": "Associate"
}

KNOWN_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Uber", "Stripe", "Airbnb",
    "Infosys", "TCS", "Wipro", "Cognizant", "Accenture", "Deloitte", "Swiggy", "Zomato",
    "Flipkart", "Razorpay", "Zoho", "Freshworks", "Thoughtworks", "EPAM Systems", "Capgemini",
    "Oracle", "IBM", "Salesforce", "Cisco", "Intel", "Adobe"
]

class ResumeExtractor:
    def __init__(self):
        self.nlp = None
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                pass
        except ImportError:
            pass

    def extract_skills(self, text: str) -> List[str]:
        text_lower = text.lower()
        found_skills = set()
        sorted_keys = sorted(SKILL_TAXONOMY.keys(), key=len, reverse=True)
        
        for k in sorted_keys:
            pattern = r'(?:\b|[^a-zA-Z0-9])' + re.escape(k) + r'(?:\b|[^a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                canonical = SKILL_TAXONOMY[k]
                found_skills.add(canonical)
                
        return sorted(list(found_skills))

    def extract_years_experience(self, text: str) -> float:
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s*of\s*experience|\s*exp)?',
            r'(?:experience|exp)\s*:\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)?',
            r'over\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)'
        ]
        
        candidates = []
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                try:
                    val = float(m)
                    if 0.5 <= val <= 35:
                        candidates.append(val)
                except ValueError:
                    pass
                    
        if candidates:
            return max(candidates)
        return 2.0

    def extract_education(self, text: str) -> Dict[str, str]:
        text_lower = text.lower()
        level = "Bachelor"
        field = "Computer Science"
        
        for kw, deg_level in DEGREE_LEVELS.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                level = deg_level
                break
                
        if "data science" in text_lower or "statistics" in text_lower:
            field = "Data Science"
            degree_title = f"{level} in Data Science"
        elif "information technology" in text_lower or "it" in text_lower:
            field = "Information Technology"
            degree_title = f"{level} in Information Technology"
        elif "computer applications" in text_lower or "bca" in text_lower or "mca" in text_lower:
            field = "Computer Applications"
            degree_title = f"{level} in Computer Applications"
        elif "bootcamp" in text_lower or "certificate" in text_lower:
            level = "Bootcamp"
            field = "Software Engineering"
            degree_title = "Software Engineering Certificate"
        else:
            degree_title = f"{level} in Computer Science"
            
        return {
            "degree": degree_title,
            "level": level,
            "field": field
        }

    def extract_companies(self, text: str) -> List[str]:
        found_companies = set()
        text_lower = text.lower()
        
        for comp in KNOWN_COMPANIES:
            if re.search(r'\b' + re.escape(comp.lower()) + r'\b', text_lower):
                found_companies.add(comp)
                
        if self.nlp:
            try:
                doc = self.nlp(text[:2000])
                for ent in doc.ents:
                    if ent.label_ == "ORG" and len(ent.text.strip()) > 2:
                        found_companies.add(ent.text.strip())
            except Exception:
                pass
                
        return sorted(list(found_companies))

    def extract_structured_candidate(self, raw_text: str, candidate_id: str = "cand_custom", name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        if not email:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
            email = email_match.group(0) if email_match else "candidate@example.com"
            
        if not name:
            lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
            if lines and len(lines[0].split()) <= 4:
                name = lines[0]
            else:
                name = email.split('@')[0].replace('.', ' ').title()
                
        skills = self.extract_skills(raw_text)
        years_exp = self.extract_years_experience(raw_text)
        edu = self.extract_education(raw_text)
        companies = self.extract_companies(raw_text)
        
        project_lines = []
        for line in raw_text.split('\n'):
            line_str = line.strip()
            if line_str.startswith(('-', '•', '*')) and len(line_str) > 20:
                project_lines.append(line_str.lstrip('-•* ').strip())
                
        if not project_lines:
            project_lines = ["Delivered production features with modern agile workflows."]

        return {
            "id": candidate_id,
            "name": name,
            "email": email,
            "years_exp": years_exp,
            "skills": skills,
            "education": edu,
            "companies": companies,
            "projects": project_lines,
            "raw_text": raw_text
        }
