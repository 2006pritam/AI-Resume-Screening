import json
import random
import os
from typing import List, Dict, Any

ROLES = {
    "job_fullstack_react_node": {
        "id": "job_fullstack_react_node",
        "title": "Senior Full Stack Engineer (React / Node.js)",
        "department": "Engineering",
        "min_experience_years": 4.0,
        "required_skills": ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "REST APIs"],
        "preferred_skills": ["Next.js", "Docker", "Tailwind CSS", "Redux", "GraphQL", "AWS"],
        "min_education": "Bachelor",
        "description": "Looking for a versatile Senior Full Stack Engineer to build high-scale web platforms using React 18, TypeScript, Node.js microservices, and PostgreSQL.",
        "responsibilities": [
            "Design and build performant, responsive web applications in React and TypeScript",
            "Develop high-throughput REST APIs and backend microservices using Node.js and Express",
            "Architect relational database schemas and optimize queries in PostgreSQL",
            "Containerize services with Docker and set up automated CI/CD pipelines"
        ]
    },
    "job_ai_ml_engineer": {
        "id": "job_ai_ml_engineer",
        "title": "AI / Machine Learning Engineer",
        "department": "AI & Research",
        "min_experience_years": 3.0,
        "required_skills": ["Python", "PyTorch", "Machine Learning", "Data Analysis", "FastAPI", "Docker"],
        "preferred_skills": ["TensorFlow", "Computer Vision", "NLP", "Scikit-Learn", "MLflow", "AWS"],
        "min_education": "Bachelor",
        "description": "Seeking an AI/ML Engineer to train, evaluate, and deploy deep learning models and computer vision pipelines into production environments.",
        "responsibilities": [
            "Train and fine-tune deep neural networks using PyTorch and TensorFlow",
            "Develop computer vision and NLP model inference services using FastAPI",
            "Optimize model quantization, caching, and inference latencies for real-time APIs",
            "Collaborate with data engineers to build robust data preprocessing pipelines"
        ]
    },
    "job_devops_cloud": {
        "id": "job_devops_cloud",
        "title": "Cloud DevOps & Site Reliability Engineer",
        "department": "Infrastructure",
        "min_experience_years": 4.0,
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Linux"],
        "preferred_skills": ["Terraform", "Jenkins", "Python", "Redis", "Kafka", "PostgreSQL"],
        "min_education": "Bachelor",
        "description": "Join our platform team to architect scalable multi-region AWS cloud infrastructure, automate CI/CD deployments, and maintain 99.99% uptime.",
        "responsibilities": [
            "Manage and scale multi-tenant Kubernetes (EKS) clusters and containerized services",
            "Build automated CI/CD pipelines with GitHub Actions, Jenkins, and Docker",
            "Implement infrastructure-as-code using Terraform and AWS CloudFormation",
            "Monitor system performance, logging, and security observability"
        ]
    },
    "job_data_analyst_bi": {
        "id": "job_data_analyst_bi",
        "title": "Data Analyst & Business Intelligence Specialist",
        "department": "Analytics",
        "min_experience_years": 2.0,
        "required_skills": ["SQL", "Python", "Data Analysis", "Tableau", "Excel", "Data Visualization"],
        "preferred_skills": ["Power BI", "Pandas", "Snowflake", "dbt", "Statistics", "NumPy"],
        "min_education": "Bachelor",
        "description": "Looking for a Data Analyst to transform complex datasets into interactive BI dashboards and actionable commercial insights for leadership.",
        "responsibilities": [
            "Write advanced analytical SQL queries across Snowflake and relational databases",
            "Design and maintain interactive executive dashboards in Tableau and Power BI",
            "Perform statistical analysis and cohort retention modeling in Python (Pandas/NumPy)",
            "Automate recurring business metrics reporting to streamline operations"
        ]
    },
    "job_qa_automation_eng": {
        "id": "job_qa_automation_eng",
        "title": "QA Automation & SDET Engineer",
        "department": "Quality Assurance",
        "min_experience_years": 3.0,
        "required_skills": ["Selenium", "Python", "Test Automation", "API Testing", "Postman", "Git"],
        "preferred_skills": ["Cypress", "Playwright", "PyTest", "Jenkins", "Docker", "Jira"],
        "min_education": "Bachelor",
        "description": "Seeking an SDET / QA Automation Engineer to design, implement, and maintain automated end-to-end regression test suites and API validation pipelines.",
        "responsibilities": [
            "Build scalable automated test frameworks using Selenium WebDriver, Playwright, and PyTest",
            "Perform automated API integration tests using Postman and Python requests",
            "Integrate automated smoke and regression tests into Jenkins CI/CD pipelines",
            "Log, track, and verify software defects in Jira"
        ]
    }
}

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Neha", "Aditya", "Pooja",
    "Siddharth", "Ishaan", "Riya", "Kavya", "Tanvi", "Arjun", "Dev", "Meera", "Varun", "Simran",
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Casey", "Riley", "Cameron",
    "David", "Elena", "Marcus", "Sophie", "Lucas", "Maya", "Carlos", "Fatima", "Chen", "Yuki"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Sen", "Chatterjee", "Gupta", "Nair", "Iyer", "Mukherjee", "Das",
    "Banerjee", "Ghosh", "Dey", "Roy", "Chakraborty", "Bose", "Dutta", "Mishra", "Paul", "Saha",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Taylor", "Anderson",
    "Müller", "Dubois", "Santos", "Kim", "Tanaka", "Ivanov", "Al-Mansoor", "Zhang", "Nguyen", "Gomez"
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Uber", "Stripe", "Airbnb",
    "TCS", "Infosys", "Wipro", "Cognizant", "Accenture", "Deloitte", "Swiggy", "Zomato",
    "Flipkart", "Razorpay", "Zoho", "Freshworks", "Thoughtworks", "EPAM Systems", "Capgemini",
    "Oracle", "IBM", "Salesforce", "Cisco", "Intel", "Adobe", "Paytm", "Jio"
]

UNIVERSITIES = [
    "Indian Institute of Technology (IIT)", "National Institute of Technology (NIT)",
    "Jadavpur University", "Supreme Knowledge Foundation", "Delhi University",
    "Birla Institute of Technology (BITS)", "Vellore Institute of Technology (VIT)",
    "University of California, Berkeley", "Georgia Tech", "University of Waterloo"
]

DEGREES = [
    {"level": "Master", "title": "M.Tech in Computer Science", "field": "Computer Science"},
    {"level": "Master", "title": "M.S. in Data Science & AI", "field": "Data Science"},
    {"level": "Master", "title": "MCA - Master of Computer Applications", "field": "Computer Science"},
    {"level": "Bachelor", "title": "B.Tech in Information Technology", "field": "Information Technology"},
    {"level": "Bachelor", "title": "B.Tech in Computer Science & Engineering", "field": "Computer Science"},
    {"level": "Bachelor", "title": "BCA - Bachelor of Computer Applications", "field": "Computer Applications"},
    {"level": "Bachelor", "title": "B.S. in Statistics and Data Science", "field": "Data Science"},
    {"level": "Bootcamp", "title": "Full Stack Software Engineering Certificate", "field": "Software Engineering"}
]

ARCHETYPES = {
    "fullstack_modern": {
        "role_category": "Fullstack React & Node",
        "primary_skills": ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "JavaScript", "HTML/CSS"],
        "secondary_skills": ["Next.js", "Redux", "Tailwind CSS", "Docker", "REST APIs", "Git", "Jest"],
        "projects": [
            "Architected high-concurrency SaaS dashboard using React 18, TypeScript, and Node.js microservices handling 25k daily active users.",
            "Designed and optimized relational PostgreSQL schemas, implementing Redis caching layer to cut query latency by 45%.",
            "Migrated frontend from CRA to Next.js with Tailwind CSS, improving Core Web Vitals and Lighthouse performance to 98."
        ]
    },
    "ai_ml_specialist": {
        "role_category": "AI & Deep Learning",
        "primary_skills": ["Python", "PyTorch", "Machine Learning", "Data Analysis", "FastAPI", "Docker"],
        "secondary_skills": ["TensorFlow", "Computer Vision", "Scikit-Learn", "Pandas", "NumPy", "MLflow", "Git"],
        "projects": [
            "Trained and evaluated hybrid CNN-transformer vision models in PyTorch for medical image segmentation achieving 94.2% IoU.",
            "Engineered low-latency real-time model inference API using FastAPI, Docker, and ONNX Runtime with sub-40ms response times.",
            "Automated training evaluation pipelines using MLflow tracking experiments across multi-GPU clusters."
        ]
    },
    "devops_cloud_platform": {
        "role_category": "Cloud Infrastructure & DevOps",
        "primary_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"],
        "secondary_skills": ["Terraform", "Jenkins", "Python", "Redis", "Kafka", "PostgreSQL"],
        "projects": [
            "Managed production Kubernetes clusters on AWS EKS, deploying 40+ microservices with Helm and automated canary rollouts.",
            "Constructed continuous integration & automated deployment pipelines in GitHub Actions and Jenkins, cutting build times by 60%.",
            "Provisioned resilient multi-AZ cloud infrastructure via Terraform with automated disaster recovery."
        ]
    },
    "qa_automation_sdet": {
        "role_category": "QA Automation & Testing",
        "primary_skills": ["Selenium", "Python", "Test Automation", "API Testing", "Postman", "Git"],
        "secondary_skills": ["Playwright", "Cypress", "PyTest", "Jenkins", "Docker", "Jira", "SQL"],
        "projects": [
            "Designed and built automated regression test suites using Playwright and PyTest covering 500+ end-to-end user journeys.",
            "Integrated continuous API automated validation in Jenkins CI/CD pipeline reducing production defect escape rate by 40%.",
            "Constructed synthetic test data generation scripts in Python to stress test REST microservices."
        ]
    },
    "data_analyst_analytics": {
        "role_category": "Data Analytics & BI",
        "primary_skills": ["SQL", "Python", "Data Analysis", "Tableau", "Excel", "Data Visualization"],
        "secondary_skills": ["Power BI", "Pandas", "Snowflake", "dbt", "Statistics", "NumPy"],
        "projects": [
            "Designed executive BI dashboards in Tableau and Power BI connecting to Snowflake data warehouse for sales insights.",
            "Conducted customer churn analysis and cohort retention studies using Python (Pandas/NumPy) and complex analytical SQL.",
            "Automated weekly KPI reconciliation reports in Python and dbt, eliminating 15 hours of manual reporting per week."
        ]
    }
}

def generate_synthetic_dataset(num_resumes: int = 160) -> Dict[str, Any]:
    random.seed(101)
    candidates = []
    archetype_keys = list(ARCHETYPES.keys())
    
    for i in range(1, num_resumes + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}@example.com"
        
        arch_key = random.choice(archetype_keys)
        arch = ARCHETYPES[arch_key]
        years_exp = round(random.triangular(1.0, 12.0, 4.2), 1)
        
        num_primary = random.randint(len(arch["primary_skills"]) - 2, len(arch["primary_skills"]))
        selected_skills = random.sample(arch["primary_skills"], k=min(num_primary, len(arch["primary_skills"])))
        
        num_secondary = random.randint(2, min(4, len(arch["secondary_skills"])))
        selected_skills += random.sample(arch["secondary_skills"], k=num_secondary)
        
        if random.random() < 0.3:
            crossover = random.choice(["Docker", "SQL", "Python", "AWS", "GraphQL", "Linux", "FastAPI", "Tailwind CSS"])
            if crossover not in selected_skills:
                selected_skills.append(crossover)
        
        education = random.choice(DEGREES)
        university = random.choice(UNIVERSITIES)
        
        num_companies = min(max(1, int(years_exp // 2)), 4)
        past_companies = random.sample(COMPANIES, k=num_companies)
        projects = random.sample(arch["projects"], k=min(2, len(arch["projects"])))
        
        raw_text = f"""
{full_name}
Email: {email} | Experience: {years_exp} Years | Education: {education['title']} - {university}
Target Profile: {arch['role_category']}
Past Companies: {', '.join(past_companies)}

SKILLS:
{', '.join(selected_skills)}

EXPERIENCE & PROJECTS:
- {projects[0]}
- {projects[1] if len(projects) > 1 else 'Collaborated with agile cross-functional engineering teams to ship production features.'}

EDUCATION:
- {education['title']} ({education['level']}), {university}
"""
        
        candidate = {
            "id": f"cand_{i:03d}",
            "name": full_name,
            "email": email,
            "phone": f"+91-{random.randint(700, 999)}-{random.randint(1000, 9999)}-{random.randint(10, 99)}",
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
    dataset = generate_synthetic_dataset(160)
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "jobs.json"), "w") as f:
        json.dump(dataset["jobs"], f, indent=2)
    with open(os.path.join(data_dir, "resumes.json"), "w") as f:
        json.dump(dataset["resumes"], f, indent=2)
    print(f"Generated fresh dataset with {len(dataset['jobs'])} jobs and {len(dataset['resumes'])} candidates.")
