---
title: AI Resume Screening & Candidate Clustering
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: 1.32.0
app_file: streamlit_app.py
pinned: false
license: mit
---

# AI Resume Screening & Candidate Clustering Platform (Streamlit)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/2006pritam/AI-Resume-Screening)

An explainable, high-throughput candidate screening and skill-archetype clustering platform built with **Streamlit**, **FastAPI**, and **Python NLP**. Designed for staffing agencies and recruiters to shortlist, cluster, and evaluate 300–800+ resumes in seconds.

---

## 🌟 Key Features

1. **Interactive Streamlit Dashboard (`streamlit_app.py`)**:
   - **Target Role Switcher**: React Developer, QA Automation, Data Analyst, Node.js Backend.
   - **Shortlist Table**: Sortable candidate ranking with interactive score progress bars, search, and CSV export.
   - **Skill Archetype Clusters**: Visual cards displaying cluster distribution, dominant skills, and recruiter recommendations.
   - **Explainability Inspector**: Deep candidate scorecards decomposing scores across Skills (45%), Experience (25%), Education (15%), and Projects (15%).
   - **Resume Text Extractor**: Paste raw resume text for instantaneous structured entity parsing and real-time re-ranking.

2. **High-Throughput Extraction (NER & Taxonomy Matching)**:
   - Normalizes skills, extracts years of experience, classifies degrees, and tracks previous companies.

3. **Multi-Factor Explainable Scoring (No Heavy LLM Dependency)**:
   $$\text{Score} = 0.45 \cdot S_{\text{skills}} + 0.25 \cdot S_{\text{experience}} + 0.15 \cdot S_{\text{education}} + 0.15 \cdot S_{\text{projects}}$$

4. **Candidate Skill Clustering**:
   - Groups candidates into skill cohorts using K-Means and latent profile embeddings.

---

## 🚀 Running Locally with Streamlit

```bash
git clone https://github.com/2006pritam/AI-Resume-Screening.git
cd AI-Resume-Screening

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit Dashboard
streamlit run streamlit_app.py
```

---

## 🤗 Deploying to Hugging Face Spaces (Streamlit SDK)

1. Go to [Hugging Face — New Space](https://huggingface.co/new-space).
2. Set Space Name: `ai-resume-screening`
3. Select **Streamlit** as the Space SDK (100% Free CPU default).
4. Push your repository:
   ```bash
   git remote add space https://huggingface.co/spaces/pritam06/ai-resume-screening
   git push space main --force
   ```
