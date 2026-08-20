import json
import random
from typing import List, Dict, Any

ROLES = {
    "job_react_dev": {
        "id": "job_react_dev",
        "title": "Senior React / Frontend Developer",
        "department": "Engineering",
        "min_experience_years": 4,
        "required_skills": ["React", "TypeScript", "JavaScript", "HTML/CSS", "Redux", "REST APIs"],
        "preferred_skills": ["Next.js", "Tailwind CSS", "GraphQL", "Jest", "CI/CD", "Webpack"],
        "min_education": "Bachelor",
        "description": "Looking for an experienced React developer to build high-performance web applications using modern React, TypeScript, and state management tools.",
        "responsibilities": [
            "Architect and build reusable frontend components in React and TypeScript",
            "Optimize web applications for maximum speed and scalability",
            "Collaborate with backend engineers to integrate REST and GraphQL APIs",
            "Write comprehensive unit and integration tests using Jest and React Testing Library"
        ]
    },
    "job_qa_automation": {
        "id": "job_qa_automation",
        "title": "QA Automation Engineer",
        "department": "Quality Assurance",
        "min_experience_years": 3,
        "required_skills": ["Selenium", "Python", "Test Automation", "API Testing", "Postman", "Git"],
        "preferred_skills": ["Cypress", "Playwright", "Jenkins", "Docker", "SQL", "Jira"],
        "min_education": "Bachelor",
        "description": "Seeking a dedicated QA Automation Engineer to design, develop, and maintain robust automated test suites for web and backend services.",
        "responsibilities": [
            "Develop automated test scripts using Selenium and Python/Playwright",
            "Execute end-to-end integration and regression test suites",
            "Perform API testing with Postman and automated pipelines in Jenkins",
            "Identify, log, and track software defects in Jira"
        ]
    },
    "job_data_analyst": {
        "id": "job_data_analyst",
        "title": "Data Analyst / BI Specialist",
        "department": "Analytics",
        "min_experience_years": 2,
        "required_skills": ["SQL", "Python", "Data Analysis", "Tableau", "Excel", "Data Visualization"],
        "preferred_skills": ["Power BI", "Pandas", "R", "Statistics", "Snowflake", "dbt"],
        "min_education": "Bachelor",
        "description": "Looking for a Data Analyst to extract business insights, build interactive dashboards, and drive data-informed decisions across product teams.",
        "responsibilities": [
            "Query complex relational databases using advanced SQL",
            "Build automated reporting dashboards in Tableau and Power BI",
            "Conduct exploratory data analysis using Python and Pandas",
            "Present key performance metrics and actionable insights to executive leadership"
        ]
    },
    "job_node_backend": {
        "id": "job_node_backend",
        "title": "Backend Node.js Engineer",
        "department": "Backend",
        "min_experience_years": 4,
        "required_skills": ["Node.js", "Express", "PostgreSQL", "REST APIs", "TypeScript", "Docker"],
        "preferred_skills": ["NestJS", "Redis", "MongoDB", "AWS", "Kafka", "Microservices"],
        "min_education": "Bachelor",
        "description": "Join our platform team to design, scale, and maintain high-throughput backend microservices using Node.js, Express, and distributed caching.",
        "responsibilities": [
            "Design secure and scalable RESTful APIs in Node.js and TypeScript",
            "Optimize PostgreSQL queries and database schemas for high concurrency",
            "Implement caching mechanisms with Redis and asynchronous queues",
            "Containerize microservices with Docker and deploy to cloud environments"
        ]
    }
}

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Neha", "Aditya", "Pooja",
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Casey", "Riley", "Cameron",
    "David", "Elena", "Marcus", "Sophie", "Lucas", "Maya", "Carlos", "Fatima", "Chen", "Yuki"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Sen", "Chatterjee", "Gupta", "Nair", "Iyer", "Mukherjee", "Das",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Taylor", "Anderson",
    "Müller", "Dubois", "Santos", "Kim", "Tanaka", "Ivanov", "Al-Mansoor", "Zhang", "Nguyen", "Gomez"
]

COMPANIES = [
    "Infosys", "TCS", "Wipro", "Cognizant", "Accenture", "Deloitte", "Amazon", "Microsoft", 
    "Google", "Meta", "Swiggy", "Zomato", "Flipkart", "Razorpay", "Zoho", "Freshworks",
    "Thoughtworks", "EPAM Systems", "Capgemini", "Oracle", "IBM", "Stripe", "Uber"
]

UNIVERSITIES = [
    "Indian Institute of Technology (IIT)", "National Institute of Technology (NIT)",
    "Jadavpur University", "University of California, Berkeley", "Georgia Tech",
    "University of Waterloo", "Birla Institute of Technology (BITS)", "Delhi University",
    "PES University", "Vellore Institute of Technology (VIT)", "State University"
]

DEGREES = [
    {"level": "Master", "title": "M.Tech in Computer Science", "field": "Computer Science"},
    {"level": "Master", "title": "M.S. in Data Science", "field": "Data Science"},
    {"level": "Master", "title": "MCA - Master of Computer Applications", "field": "Computer Science"},
    {"level": "Bachelor", "title": "B.Tech in Information Technology", "field": "Computer Science"},
    {"level": "Bachelor", "title": "BCA - Bachelor of Computer Applications", "field": "Computer Science"},
    {"level": "Bachelor", "title": "B.S. in Statistics and Economics", "field": "Data Science"},
    {"level": "Bachelor", "title": "B.E. in Electronics & Communication", "field": "Engineering"},
    {"level": "Bootcamp", "title": "Full Stack Software Engineering Certificate", "field": "Software Engineering"}
]

ARCHETYPES = {
    "react_ts_expert": {
        "role_category": "React Frontend",
        "primary_skills": ["React", "TypeScript", "Redux", "Next.js", "Tailwind CSS", "JavaScript", "HTML/CSS"],
        "secondary_skills": ["Jest", "GraphQL", "REST APIs", "Webpack", "Vite", "Git", "Figma"],
        "project_templates": [
            "Built a high-traffic SaaS analytics dashboard using React 18, TypeScript, and Tailwind CSS with sub-second page loads.",
            "Migrated legacy SPA from JavaScript to TypeScript, increasing code coverage to 92% with Jest and RTL.",
            "Engineered server-side rendered storefront using Next.js and GraphQL, boosting SEO scores by 35%."
        ]
    },
    "mern_fullstack": {
        "role_category": "Fullstack MERN",
        "primary_skills": ["React", "Node.js", "Express", "MongoDB", "JavaScript", "REST APIs"],
        "secondary_skills": ["Redux", "Bootstrap", "HTML/CSS", "Git", "Postman", "JWT Authentication"],
        "project_templates": [
            "Developed full-stack e-commerce portal with React, Redux, Express, and MongoDB.",
            "Created real-time collaborative workspace with WebSockets, Node.js, and React frontend.",
            "Designed secure REST APIs with Express, integrating Stripe payments and JWT auth."
        ]
    },
    "node_backend_cloud": {
        "role_category": "Backend Node & Cloud",
        "primary_skills": ["Node.js", "Express", "PostgreSQL", "TypeScript", "Docker", "REST APIs"],
        "secondary_skills": ["NestJS", "Redis", "AWS", "Microservices", "Kafka", "Kubernetes", "Git"],
        "project_templates": [
            "Architected high-throughput microservices using NestJS, PostgreSQL, and Redis caching handling 10k RPS.",
            "Containerized core transaction pipelines with Docker and automated deployment on AWS ECS via GitHub Actions.",
            "Designed event-driven message bus using Apache Kafka for real-time order processing."
        ]
    },
    "qa_automation_python": {
        "role_category": "QA Automation (Python)",
        "primary_skills": ["Selenium", "Python", "Test Automation", "API Testing", "Postman", "Git"],
        "secondary_skills": ["PyTest", "Jenkins", "Docker", "Jira", "SQL", "Linux", "CI/CD"],
        "project_templates": [
            "Created automated end-to-end regression testing framework with Selenium WebDriver and PyTest.",
            "Integrated continuous API automated validation in Jenkins CI/CD pipeline reducing release bugs by 40%.",
            "Designed synthetic test data generation scripts in Python to stress test REST microservices."
        ]
    },
    "qa_modern_cypress_playwright": {
        "role_category": "QA Automation (Cypress/Playwright)",
        "primary_skills": ["Cypress", "Playwright", "JavaScript", "Test Automation", "API Testing", "Git"],
        "secondary_skills": ["TypeScript", "Postman", "Jira", "GitHub Actions", "Docker", "Mocha"],
        "project_templates": [
            "Implemented cross-browser end-to-end test suites using Playwright and TypeScript for a fintech web app.",
            "Constructed fast CI test workflows with Cypress and GitHub Actions, cutting test runtimes by 50%.",
            "Conducted accessibility and load performance audits with Lighthouse and k6."
        ]
    },
    "data_analyst_bi": {
        "role_category": "Data Analyst / BI",
        "primary_skills": ["SQL", "Python", "Data Analysis", "Tableau", "Excel", "Data Visualization"],
        "secondary_skills": ["Pandas", "Power BI", "Statistics", "Snowflake", "NumPy", "Matplotlib"],
        "project_templates": [
            "Designed executive BI dashboards in Tableau connecting to Snowflake data warehouse for sales insights.",
            "Conducted customer churn analysis and cohort retention studies using Python (Pandas/NumPy) and SQL.",
            "Automated monthly KPI reconciliation reports in Excel VBA and Python, saving 20 hours/month."
        ]
    },
    "data_engineer_analytics": {
        "role_category": "Data Engineer / Analytics",
        "primary_skills": ["SQL", "Python", "PostgreSQL", "Data Analysis", "dbt", "Snowflake"],
        "secondary_skills": ["Airflow", "Spark", "AWS", "Docker", "Pandas", "Data Modeling"],
        "project_templates": [
            "Built automated ETL data pipelines using Apache Airflow, dbt, and Snowflake for multi-source analytics.",
            "Optimized complex SQL aggregation queries across 50M+ rows in PostgreSQL for real-time reporting.",
            "Modeled dimensional star schemas for enterprise customer transaction tracking."
        ]
    }
}

def generate_synthetic_dataset(num_resumes: int = 150) -> Dict[str, Any]:
    random.seed(42)
    candidates = []
    archetype_keys = list(ARCHETYPES.keys())
    
    for i in range(1, num_resumes + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}@example.com"
        
        arch_key = random.choice(archetype_keys)
        arch = ARCHETYPES[arch_key]
        years_exp = round(random.triangular(1.0, 12.0, 4.5), 1)
        
        num_primary = random.randint(len(arch["primary_skills"]) - 2, len(arch["primary_skills"]))
        selected_skills = random.sample(arch["primary_skills"], k=min(num_primary, len(arch["primary_skills"])))
        
        num_secondary = random.randint(2, min(4, len(arch["secondary_skills"])))
        selected_skills += random.sample(arch["secondary_skills"], k=num_secondary)
        
        if random.random() < 0.25:
            crossover = random.choice(["Docker", "SQL", "Python", "AWS", "GraphQL", "Linux", "Figma", "Tailwind CSS"])
            if crossover not in selected_skills:
                selected_skills.append(crossover)
        
        education = random.choice(DEGREES)
        university = random.choice(UNIVERSITIES)
        
        num_companies = min(max(1, int(years_exp // 2)), 4)
        past_companies = random.sample(COMPANIES, k=num_companies)
        projects = random.sample(arch["project_templates"], k=min(2, len(arch["project_templates"])))
        
        raw_text = f"""
{full_name}
Email: {email} | Experience: {years_exp} Years | Education: {education['title']} - {university}
Target Profile: {arch['role_category']}
Past Companies: {', '.join(past_companies)}

SKILLS:
{', '.join(selected_skills)}

EXPERIENCE & PROJECTS:
- {projects[0]}
- {projects[1] if len(projects) > 1 else 'Collaborated with agile cross-functional teams to deliver key features.'}

EDUCATION:
- {education['title']} ({education['level']}), {university}
"""
        
        candidate = {
            "id": f"cand_{i:03d}",
            "name": full_name,
            "email": email,
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "years_exp": years_exp,
            "skills": selected_skills,
            "education": {
                "degree": education["title"],
                "level": education["level"],
                "field": education["field"],
                "institution": university
            },
            "companies": past_companies,
            "projects": projects,
            "archetype": arch_key,
            "raw_text": raw_text.strip()
        }
        candidates.append(candidate)
        
    return {
        "jobs": ROLES,
        "resumes": candidates
    }

if __name__ == "__main__":
    dataset = generate_synthetic_dataset(180)
    with open("data/jobs.json", "w") as f:
        json.dump(dataset["jobs"], f, indent=2)
    with open("data/resumes.json", "w") as f:
        json.dump(dataset["resumes"], f, indent=2)
    print(f"Generated {len(dataset['jobs'])} jobs and {len(dataset['resumes'])} resumes.")
