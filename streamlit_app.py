import streamlit as st
import pandas as pd
import json
import os
import sys

# Ensure local modules can be imported
sys.path.insert(0, os.path.dirname(__file__))

from app.service import ScreeningService
from app.schemas import JobDescription, ResumeUploadRequest

st.set_page_config(
    page_title="AI Resume Screening & Candidate Clustering",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished recruiter dashboard
st.markdown("""
<style>
    .cluster-card {
        background-color: #0f172a;
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .highlight-badge {
        background-color: #064e3b;
        color: #6ee7b7;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    .missing-badge {
        background-color: #881337;
        color: #fca5a5;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_screening_service():
    return ScreeningService()

service = get_screening_service()

# --- SIDEBAR: Role Selection & Global Filters ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8649/8649607.png", width=60)
    st.title("TalentRadar AI")
    st.caption("Explainable Resume Screening & Skill Clustering")
    st.markdown("---")
    
    # Target Job Selector
    jobs = service.get_all_jobs()
    if not jobs:
        st.error("No jobs loaded. Initializing dataset...")
        st.stop()
        
    job_options = {f"{j.title} (Min {j.min_experience_years}+ yrs)": j.id for j in jobs}
    selected_label = st.selectbox("🎯 Target Role / Job Description", list(job_options.keys()))
    active_job_id = job_options[selected_label]
    active_job = service.get_job(active_job_id)
    
    st.markdown("---")
    st.subheader("⚙️ Candidate Filters")
    min_score = st.slider("Minimum Match Score (%)", 0, 95, 0, step=5)
    min_exp = st.slider("Minimum Experience (Years)", 0, 12, 0, step=1)
    search_keyword = st.text_input("🔍 Keyword / Skill Search", placeholder="e.g. React, Docker, TCS...")
    
    st.markdown("---")
    st.info("💡 **Explainable AI**: Matches candidates across skills (45%), experience (25%), education (15%), and projects (15%) with transparent reasoning.")

# --- RUN SCREENING ---
screening_res = service.run_screening(active_job_id)

# Filter results
filtered_results = screening_res.results
if min_score > 0:
    filtered_results = [r for r in filtered_results if r.score_breakdown.overall_score >= min_score]
if min_exp > 0:
    filtered_results = [r for r in filtered_results if r.candidate.years_exp >= min_exp]
if search_keyword.strip():
    q = search_keyword.lower()
    filtered_results = [
        r for r in filtered_results
        if q in r.candidate.name.lower()
        or q in (r.candidate.email or "").lower()
        or any(q in s.lower() for s in r.candidate.skills)
        or any(q in c.lower() for c in r.candidate.companies)
        or any(q in p.lower() for p in r.candidate.projects)
    ]

# --- MAIN DASHBOARD HEADER & KPIS ---
st.title("🧠 AI Resume Screening & Skill Clustering Dashboard")
st.markdown(f"**Target Role**: `{active_job.title}` ({active_job.department}) | **Required Experience**: `{active_job.min_experience_years} Years`")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Resumes Screened", screening_res.total_candidates_screened)
with col2:
    st.metric("Shortlisted (Score ≥ 70%)", screening_res.shortlisted_count)
with col3:
    st.metric("Skill Clusters Discovered", len(screening_res.clusters))
with col4:
    top_score = screening_res.results[0].score_breakdown.overall_score if screening_res.results else 0
    st.metric("Top Candidate Match", f"{top_score}%")

# Active Job Requirements Expander
with st.expander("📋 View Full Job Description & Skill Requirements", expanded=False):
    st.write(f"**Description**: {active_job.description}")
    req_col, pref_col = st.columns(2)
    with req_col:
        st.markdown("**Required Skills:**")
        st.write(", ".join([f"`{s}`" for s in active_job.required_skills]))
    with pref_col:
        st.markdown("**Preferred / Bonus Skills:**")
        st.write(", ".join([f"`+{s}`" for s in active_job.preferred_skills]) if active_job.preferred_skills else "None specified")
    st.markdown("**Key Responsibilities:**")
    for resp in active_job.responsibilities:
        st.write(f"- {resp}")

# --- TABS: Shortlist, Clusters, Deep Explainability, Upload ---
tab_shortlist, tab_clusters, tab_explain, tab_upload = st.tabs([
    "🏆 Candidate Shortlist",
    "🧩 Skill Archetype Clusters",
    "🔎 Explainability Inspector",
    "📄 Upload & Parse Resume"
])

# --- TAB 1: Shortlist Table ---
with tab_shortlist:
    st.subheader(f"Ranked Candidate Shortlist ({len(filtered_results)} candidates showing)")
    
    if not filtered_results:
        st.warning("No candidates match the specified filters. Try lowering the minimum score or experience.")
    else:
        table_data = []
        for r in filtered_results:
            table_data.append({
                "Rank": r.rank,
                "Candidate Name": r.candidate.name,
                "Match Score (%)": r.score_breakdown.overall_score,
                "Experience": f"{r.candidate.years_exp} yrs",
                "Skill Cluster": r.cluster_name,
                "Top Matched Skills": ", ".join(r.score_breakdown.matched_required_skills[:4]),
                "Missing Required Skills": ", ".join(r.score_breakdown.missing_required_skills[:3]) if r.score_breakdown.missing_required_skills else "None (100% Core Match)",
                "Degree": r.candidate.education.degree,
                "Email": r.candidate.email,
                "Candidate ID": r.candidate.id
            })
        
        df_display = pd.DataFrame(table_data)
        
        st.dataframe(
            df_display,
            column_config={
                "Rank": st.column_config.NumberColumn(width="small"),
                "Match Score (%)": st.column_config.ProgressColumn(
                    "Match Score",
                    help="Calibrated explainable score (0-100%)",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            use_container_width=True,
            hide_index=True
        )
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Candidate Shortlist (CSV)",
            data=csv,
            file_name=f"shortlist_{active_job_id}.csv",
            mime="text/csv"
        )

# --- TAB 2: Clusters View ---
with tab_clusters:
    st.subheader("🧩 Candidate Skill Archetypes (K-Means Clustering)")
    st.caption("Candidates grouped by latent skill vectors and project keywords to uncover distinct talent pools.")
    
    if not screening_res.clusters:
        st.info("No skill clusters found.")
    else:
        num_cols = min(3, len(screening_res.clusters))
        for row_start in range(0, len(screening_res.clusters), num_cols):
            row_clusters = screening_res.clusters[row_start : row_start + num_cols]
            cols = st.columns(len(row_clusters))
            for idx, c in enumerate(row_clusters):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="cluster-card">
                        <h4>{c.cluster_name}</h4>
                        <p><b>Candidates:</b> {c.candidate_count} ({round((c.candidate_count/max(screening_res.total_candidates_screened, 1))*100, 1)}%)</p>
                        <p><b>Avg Score:</b> {c.avg_score}% | <b>Avg Exp:</b> {c.avg_experience} yrs</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Dominant Skills:**")
                    for sk in c.top_dominant_skills[:4]:
                        st.caption(f"• {sk['skill']} ({sk['percentage']}%)")
                    
                    st.markdown(f"**Recruiter Note**: *{c.shortlist_recommendation}*")

# --- TAB 3: Explainability Inspector ---
with tab_explain:
    st.subheader("🔎 Deep Candidate Scorecard & Explainable Reasoning")
    
    cand_options = {
        f"#{r.rank} - {r.candidate.name} ({r.score_breakdown.overall_score}% | {r.candidate.years_exp} yrs)": r.candidate.id
        for r in filtered_results
    }
    
    if not cand_options:
        st.warning("No candidates available to inspect.")
    else:
        selected_cand_label = st.selectbox("Select Candidate to Inspect:", list(cand_options.keys()))
        selected_cand_id = cand_options[selected_cand_label]
        target_res = next(r for r in filtered_results if r.candidate.id == selected_cand_id)
        
        c = target_res.candidate
        b = target_res.score_breakdown
        
        st.markdown("---")
        hcol1, hcol2, hcol3 = st.columns([2, 1, 1])
        with hcol1:
            st.markdown(f"### {c.name} (Rank #{target_res.rank})")
            st.markdown(f"📧 `{c.email}` | 🎓 `{c.education.degree}` | 🏢 Past Companies: `{', '.join(c.companies) if c.companies else 'None listed'}`")
        with hcol2:
            st.metric("Overall Match Score", f"{b.overall_score}%")
        with hcol3:
            st.metric("Cluster Cohort", target_res.cluster_name)
            
        st.markdown("#### 🎯 Score Component Decomposition")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric("1. Skills Overlap (45%)", f"{b.skill_score}%", f"{round(b.skill_score * 0.45, 1)} pts")
        with mcol2:
            st.metric("2. Experience Fit (25%)", f"{b.experience_score}%", f"{round(b.experience_score * 0.25, 1)} pts")
        with mcol3:
            st.metric("3. Education Fit (15%)", f"{b.education_score}%", f"{round(b.education_score * 0.15, 1)} pts")
        with mcol4:
            st.metric("4. Project Match (15%)", f"{b.project_score}%", f"{round(b.project_score * 0.15, 1)} pts")
            
        st.markdown("#### 💡 Why did this candidate rank here?")
        for h in b.explanation_highlights:
            st.success(f"✓ {h}")
            
        scol1, scol2 = st.columns(2)
        with scol1:
            st.markdown("**Matched Required Skills:**")
            if b.matched_required_skills:
                for s in b.matched_required_skills:
                    st.markdown(f"<span class='highlight-badge'>✓ {s}</span> ", unsafe_allow_html=True)
            else:
                st.caption("No direct required skills matched.")
                
            if b.matched_preferred_skills:
                st.markdown("**Bonus Preferred Skills Matched:**")
                for s in b.matched_preferred_skills:
                    st.markdown(f"<span class='highlight-badge'>★ {s}</span> ", unsafe_allow_html=True)
        with scol2:
            st.markdown("**Missing Required Skills (Gaps):**")
            if b.missing_required_skills:
                for s in b.missing_required_skills:
                    st.markdown(f"<span class='missing-badge'>✗ {s}</span> ", unsafe_allow_html=True)
            else:
                st.info("🎉 Zero skill gaps! All core required skills are present.")
                
        st.markdown("#### 💼 Demonstrated Project Achievements (Semantic Relevance Analyzed)")
        for proj in c.projects:
            st.info(f"📌 {proj}")

# --- TAB 4: Upload & Parse Resume ---
with tab_upload:
    st.subheader("📄 Upload or Paste Custom Resume")
    st.caption("Test the automated entity extractor (skills, experience, education, companies) and evaluate in real-time.")
    
    custom_resume_text = st.text_area(
        "Paste Raw Resume Text:",
        height=220,
        placeholder="""Pritam Kumar Modak
Email: pritam.modak@example.com | Experience: 5.5 Years in Web Development
Skills: React, TypeScript, Next.js, Redux, Tailwind CSS, Jest, GraphQL, REST APIs, Git
Education: B.Tech in Information Technology from Supreme Knowledge Foundation
Companies: TCS, Cognizant
Projects:
- Built high-performance SaaS analytics dashboard using React 18, Next.js, and TypeScript.
- Architected reusable component library and automated unit test suites in Jest."""
    )
    
    if st.button("⚡ Extract Structured Fields & Screen Candidate", type="primary"):
        if not custom_resume_text.strip():
            st.error("Please enter resume text.")
        else:
            with st.spinner("Extracting entities and evaluating candidate..."):
                new_cand = service.add_resume(custom_resume_text)
                refresh_res = service.run_screening(active_job_id, force_refresh=True)
                new_cand_res = next(r for r in refresh_res.results if r.candidate.id == new_cand.id)
                
                st.success(f"Candidate **{new_cand.name}** successfully parsed and screened!")
                
                ecol1, ecol2, ecol3 = st.columns(3)
                with ecol1:
                    st.metric("Extracted Experience", f"{new_cand.years_exp} Years")
                with ecol2:
                    st.metric("Overall Match Score", f"{new_cand_res.score_breakdown.overall_score}%")
                with ecol3:
                    st.metric("Rank in Pool", f"#{new_cand_res.rank} of {refresh_res.total_candidates_screened}")
                
                st.markdown("**Extracted Skills:**")
                st.write(", ".join([f"`{s}`" for s in new_cand.skills]))
                
                st.markdown("**Extracted Education:**")
                st.write(f"`{new_cand.education.degree}` ({new_cand.education.level})")
                
                st.markdown(f"**Assigned Skill Cluster**: `{new_cand_res.cluster_name}`")
                
                st.info("💡 Switch to the **'Candidate Shortlist'** or **'Explainability Inspector'** tab to view the complete scorecard.")
