---
title: AI Resume Screening & Candidate Clustering
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.20.0
app_file: app.py
pinned: false
license: mit
---

# AI Resume Screening & Candidate Clustering Platform

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/2006pritam/AI-Resume-Screening)

An explainable, high-throughput candidate screening and skill-archetype clustering platform built with **FastAPI / Gradio**, **Python NLP**, and **React**. Designed for staffing agencies and talent acquisition teams to shortlist and analyze 300–800+ resumes within seconds.

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

4. **Dual Interface**:
   - **Gradio Dashboard (`app.py`)**: 100% Free 1-click Hugging Face Spaces integration.
   - **FastAPI + React Dashboard (`app/main.py`)**: Standalone REST API and custom UI for Render/Docker.

---

## 🤗 1-Click Free Deployment on Hugging Face Spaces

1. Go to [Hugging Face — New Space](https://huggingface.co/new-space).
2. Set Space Name: `ai-resume-screening`
3. Select License: `MIT`
4. Select **Gradio** as Space SDK (100% Free CPU default, no payment required!).
5. Clone or sync this repository:
   ```bash
   git clone https://github.com/2006pritam/AI-Resume-Screening.git
   cd AI-Resume-Screening
   git remote add space https://huggingface.co/spaces/pritam06/ai-resume-screening
   git push space main --force
   ```

---

## ☁️ 1-Click Deployment on Render

Click the button below to deploy this repository directly to Render using the pre-configured `render.yaml` Blueprint:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/2006pritam/AI-Resume-Screening)

---

## 🚀 Local Setup Guide

```bash
git clone https://github.com/2006pritam/AI-Resume-Screening.git
cd AI-Resume-Screening

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3 data_generator.py

# Launch Gradio UI
python3 app.py

# OR Launch FastAPI + React UI
python3 start.py
```
