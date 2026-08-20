---
title: AI Resume Screening & Candidate Clustering
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# AI Resume Screening & Candidate Clustering Platform

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/2006pritam/AI-Resume-Screening)

An explainable, high-throughput candidate screening and skill-archetype clustering platform built with **FastAPI**, **Python NLP**, and **React**. Designed for staffing agencies and talent acquisition teams to shortlist and analyze 300–800+ resumes within seconds.

---

## 🌟 Key Features

1. **High-Throughput Structured Extraction (NER & Regex)**:
   - Extracts canonical skills, years of experience, degree level/field, and previous companies.
   - Works with `spaCy` NLP and provides pure Python/Regex rule-based fallbacks.

2. **Explainable Scoring Engine (No Heavy LLM Dependency)**:
   - **Skill Fit (45%)**: Exact & semantic overlap of required skills + bonus points for preferred skills.
   - **Experience Alignment (25%)**: Linear calibration against minimum required years with seniority scaling.
   - **Education Fit (15%)**: Degree hierarchy (Doctorate > Master > Bachelor > Bootcamp) and major alignment.
   - **Project & Semantic Relevance (15%)**: Cosine similarity between candidate project achievements and JD responsibilities.
   - **Recruiter Explanations**: Generates transparent reasoning (e.g., matched vs missing skills, experience delta, prior companies).

3. **Candidate Skill Archetype Clustering**:
   - Clusters candidates into natural skill groups (e.g., *React & TypeScript Specialists*, *Fullstack MERN*, *QA Automation with Python*, *Data Analytics & BI*).
   - Uses K-Means vector clustering (compatible with FAISS and pure NumPy) and auto-generates descriptive archetype profiles and recruiter recommendations.

4. **Interactive Recruiter Dashboard**:
   - Modern React + Tailwind UI with real-time candidate search, score threshold sliders, experience filtering, cluster drill-downs, and detailed candidate scorecards.
   - Resume upload modal with immediate structured extraction and re-ranking.

---

## 🤗 Deploy to Hugging Face Spaces

1. Go to [Hugging Face Create Space](https://huggingface.co/new-space).
2. Set Space Name: `ai-resume-screening`
3. Select License: `MIT`
4. Select **Docker** as Space SDK (Blank).
5. Clone or sync this repository:
   ```bash
   git remote add space https://huggingface.co/spaces/pritam06/ai-resume-screening
   git push space main
   ```
   *Or duplicate/import repository directly from GitHub: `https://github.com/2006pritam/AI-Resume-Screening`.*

---

## ☁️ 1-Click Deployment on Render

Click the button below to deploy this repository directly to Render using the pre-configured `render.yaml` Blueprint:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/2006pritam/AI-Resume-Screening)

---

## 🏗️ Architecture & Project Structure

```
ai_resume_screening/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application & REST endpoints
│   ├── schemas.py       # Pydantic data schemas
│   ├── extractor.py     # Structured resume parser (Skills, Exp, Education, Companies)
│   ├── vectorizer.py    # SentenceTransformers / TF-IDF Vectorizer & FAISS Index
│   ├── matcher.py       # Explainable scoring engine
│   ├── clusterer.py     # K-Means clustering & cluster profiling
│   └── service.py       # Core screening & caching orchestrator
├── data/
│   ├── jobs.json        # Pre-configured job descriptions
│   └── resumes.json     # 180+ realistic synthetic resumes
├── frontend/
│   └── index.html       # Standalone interactive React dashboard
├── tests/
│   └── test_screening.py # Automated test suite
├── data_generator.py    # Synthetic dataset generator
├── requirements.txt     # Python dependencies
├── render.yaml          # Render Blueprint deployment config
├── Dockerfile           # Docker container specification (HF Space compatible)
├── start.py             # Server launcher script
└── README.md
```

---

## 🚀 Local Setup Guide

```bash
git clone https://github.com/2006pritam/AI-Resume-Screening.git
cd AI-Resume-Screening

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3 data_generator.py
python3 start.py
```
