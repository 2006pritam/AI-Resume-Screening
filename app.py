import os
import pandas as pd
from app.service import ScreeningService
from app.schemas import JobDescription, ResumeUploadRequest

service = ScreeningService()

def get_job_choices():
    jobs = service.get_all_jobs()
    return [f"{j.id} - {j.title}" for j in jobs]

def screen_candidates(job_selection, min_score, min_exp, filter_cluster):
    if not job_selection:
        return "Select a job description.", pd.DataFrame(), pd.DataFrame(), []
    job_id = job_selection.split(" - ")[0]
    res = service.run_screening(job_id)
    
    kpi_text = f"### 📊 Total Screened: **{res.total_candidates_screened}** | ⭐ Shortlisted (≥70%): **{res.shortlisted_count}** | 🧩 Skill Clusters: **{len(res.clusters)}**"
    
    cluster_rows = []
    for c in res.clusters:
        skills_str = ", ".join([s["skill"] for s in c.top_dominant_skills[:3]])
        cluster_rows.append({
            "Cluster ID": c.cluster_id,
            "Archetype Name": c.cluster_name,
            "Candidate Count": c.candidate_count,
            "Avg Exp (Yrs)": c.avg_experience,
            "Avg Score (%)": c.avg_score,
            "Dominant Skills": skills_str
        })
    df_clusters = pd.DataFrame(cluster_rows)
    
    results = res.results
    if filter_cluster != "All":
        try:
            c_id = int(filter_cluster.split(":")[0])
            results = [r for r in results if r.cluster_id == c_id]
        except Exception:
            pass

    results = [r for r in results if r.score_breakdown.overall_score >= min_score and r.candidate.years_exp >= min_exp]
    
    cand_rows = []
    cand_choices = []
    for r in results:
        cand_choices.append(f"{r.candidate.id} - {r.candidate.name} ({r.score_breakdown.overall_score}%)")
        cand_rows.append({
            "Rank": r.rank,
            "Name": r.candidate.name,
            "Exp (Yrs)": r.candidate.years_exp,
            "Score (%)": r.score_breakdown.overall_score,
            "Cluster": r.cluster_name,
            "Matched Skills": ", ".join(r.score_breakdown.matched_required_skills[:3]),
            "Missing Skills": ", ".join(r.score_breakdown.missing_required_skills[:2]) if r.score_breakdown.missing_required_skills else "None"
        })
    df_cands = pd.DataFrame(cand_rows)
    
    return kpi_text, df_clusters, df_cands, cand_choices

def explain_candidate(cand_selection, job_selection):
    if not cand_selection or not job_selection:
        return "Select a candidate to view explainable breakdown."
    cand_id = cand_selection.split(" - ")[0]
    job_id = job_selection.split(" - ")[0]
    
    res = service.run_screening(job_id)
    cand_res = next((r for r in res.results if r.candidate.id == cand_id), None)
    if not cand_res:
        return "Candidate not found."
        
    c = cand_res.candidate
    b = cand_res.score_breakdown
    
    highlights = "\n".join([f"- ✅ {h}" for h in b.explanation_highlights])
    projects = "\n".join([f"- 📌 {p}" for p in c.projects])
    
    return f"""
### 🧑‍💼 Candidate Scorecard: **{c.name}** (Rank #{cand_res.rank})
- **Email**: `{c.email}` | **Total Experience**: `{c.years_exp} Years`
- **Archetype Cluster**: `{cand_res.cluster_name}`
- **Education**: `{c.education.degree}`

---
#### 🎯 Calibrated Match Score Breakdown
| Metric | Score | Weight | Contribution |
| :--- | :--- | :--- | :--- |
| **Skill Match** | `{b.skill_score}%` | 45% | `{round(b.skill_score * 0.45, 1)} pts` |
| **Experience Fit** | `{b.experience_score}%` | 25% | `{round(b.experience_score * 0.25, 1)} pts` |
| **Education Fit** | `{b.education_score}%` | 15% | `{round(b.education_score * 0.15, 1)} pts` |
| **Project Relevance** | `{b.project_score}%` | 15% | `{round(b.project_score * 0.15, 1)} pts` |
| **Final Overall Score** | **`{b.overall_score}%`** | 100% | **`{b.overall_score} / 100`** |

---
#### 💡 Why this candidate ranked here:
{highlights}

---
#### 🔍 Skill Overlap Analysis
- **Matched Required Skills**: `{", ".join(b.matched_required_skills) if b.matched_required_skills else "None"}`
- **Missing Required Skills**: `{", ".join(b.missing_required_skills) if b.missing_required_skills else "None (100% Core Match)"}`
- **Bonus Preferred Skills**: `{", ".join(b.matched_preferred_skills) if b.matched_preferred_skills else "None"}`

---
#### 💼 Key Project Highlights:
{projects}
"""

def upload_and_screen(resume_text, job_selection):
    if not resume_text.strip() or not job_selection:
        return "Please paste resume text and select a target job."
    job_id = job_selection.split(" - ")[0]
    cand = service.add_resume(resume_text)
    res = service.run_screening(job_id, force_refresh=True)
    cand_res = next((r for r in res.results if r.candidate.id == cand.id), None)
    if not cand_res:
        return f"Candidate {cand.name} added."
    
    return f"""
### ✅ Candidate Successfully Extracted & Screened!
- **Assigned ID**: `{cand.id}`
- **Name**: `{cand.name}` | **Extracted Experience**: `{cand.years_exp} Years`
- **Extracted Skills**: `{", ".join(cand.skills)}`
- **Extracted Education**: `{cand.education.degree}`
- **Overall Match Score**: **`{cand_res.score_breakdown.overall_score}%`** (Rank #{cand_res.rank} out of {res.total_candidates_screened})
- **Assigned Cluster**: `{cand_res.cluster_name}`
"""

def build_gradio_app():
    import gradio as gr
    
    job_choices = get_job_choices()
    default_job = job_choices[0] if job_choices else ""
    
    with gr.Blocks(title="AI Resume Screening & Candidate Clustering") as demo:
        gr.Markdown("# 🧠 AI Resume Screening & Candidate Clustering Platform\n*Explainable candidate ranking, structured extraction & skill archetype clustering.*")
        
        with gr.Row():
            job_dropdown = gr.Dropdown(choices=job_choices, value=default_job, label="Select Target Job Description", scale=3)
            screen_btn = gr.Button("🔍 Run Screening", variant="primary", scale=1)
            
        kpi_output = gr.Markdown("### Click 'Run Screening' to analyze candidates.")
        
        with gr.Tab("📋 Candidate Ranking & Clusters"):
            with gr.Row():
                min_score_slider = gr.Slider(0, 90, value=0, step=5, label="Min Score (%)")
                min_exp_slider = gr.Slider(0, 10, value=0, step=1, label="Min Experience (Years)")
                cluster_filter = gr.Dropdown(choices=["All", "0: Cluster 0", "1: Cluster 1", "2: Cluster 2", "3: Cluster 3", "4: Cluster 4"], value="All", label="Filter by Cluster")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🧩 Discovered Skill Clusters")
                    clusters_table = gr.Dataframe(interactive=False)
                with gr.Column(scale=2):
                    gr.Markdown("### 🏆 Ranked Candidates Shortlist")
                    cands_table = gr.Dataframe(interactive=False)
            
            gr.Markdown("---")
            with gr.Row():
                cand_selector = gr.Dropdown(choices=[], label="Select Candidate for Deep Explainability Scorecard", scale=3)
                explain_btn = gr.Button("🔎 Inspect Candidate", scale=1)
                
            explain_output = gr.Markdown("Select a candidate above to view their explainable scorecard.")
            
        with gr.Tab("📄 Upload & Screen Custom Resume"):
            gr.Markdown("### Paste raw resume text to test automatic entity extraction and instant scoring against the active job.")
            resume_input = gr.TextArea(lines=8, placeholder="Paste resume text (e.g. skills, years of experience, companies, education)...", label="Raw Resume Text")
            upload_btn = gr.Button("⚡ Parse & Screen Resume", variant="primary")
            upload_output = gr.Markdown()
            
        def on_screen(job, score, exp, cluster):
            kpi, df_cl, df_cd, choices = screen_candidates(job, score, exp, cluster)
            init_explain = explain_candidate(choices[0] if choices else None, job) if choices else "No candidates found."
            return kpi, df_cl, df_cd, gr.Dropdown(choices=choices, value=choices[0] if choices else None), init_explain
            
        screen_btn.click(
            fn=on_screen,
            inputs=[job_dropdown, min_score_slider, min_exp_slider, cluster_filter],
            outputs=[kpi_output, clusters_table, cands_table, cand_selector, explain_output]
        )
        
        explain_btn.click(
            fn=explain_candidate,
            inputs=[cand_selector, job_dropdown],
            outputs=[explain_output]
        )
        
        upload_btn.click(
            fn=upload_and_screen,
            inputs=[resume_input, job_dropdown],
            outputs=[upload_output]
        )
        
    return demo

app = build_gradio_app()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
