import streamlit as st
import pandas as pd
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.service import ScreeningService
from app.schemas import JobDescription, ResumeUploadRequest

st.set_page_config(
    page_title="AI Resume Screening & Candidate Clustering",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .cluster-card {
        background-color: #0f172a;
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .highlight-badge {
        background-color: #064e3b;
        color: #6ee7b7;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }
    .missing-badge {
        background-color: #881337;
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }
    .pref-badge {
        background-color: #1e3a8a;
        color: #93c5fd;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_screening_service():
    return ScreeningService()

service = get_screening_service()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8649/8649607.png", width=55)
    st.title("TalentRadar AI")
    st.caption("Explainable Resume Screening & Skill Clustering")
    st.markdown("---")
    
    jobs = service.get_all_jobs()
    if not jobs:
        st.error("No jobs loaded. Initializing dataset...")
        service.regenerate_fresh_dataset()
        jobs = service.get_all_jobs()
        
    job_options = {f"{j.title} (Min {j.min_experience_years}+ yrs)": j.id for j in jobs}
    selected_label = st.selectbox("🎯 Target Role / Job Opening", list(job_options.keys()))
    active_job_id = job_options[selected_label]
    active_job = service.get_job(active_job_id)
    
    st.markdown("---")
    st.subheader("⚙️ Candidate Filters")
    min_score = st.slider("Minimum Match Score (%)", 0, 95, 0, step=5)
    min_exp = st.slider("Minimum Experience (Years)", 0, 12, 0, step=1)
    search_keyword = st.text_input("🔍 Search by Name, Skill, Company", placeholder="e.g. React, Docker, TCS...")
    
    st.markdown("---")
    with st.expander("🛠️ Advanced Scoring & Weights", expanded=False):
        st.caption("Customize the relative importance of evaluation components:")
        skill_weight = st.slider("Skill Match Weight", 0, 100, 45, step=5)
        exp_weight = st.slider("Experience Weight", 0, 100, 25, step=5)
        edu_weight = st.slider("Education Fit Weight", 0, 100, 15, step=5)
        proj_weight = st.slider("Project Relevance Weight", 0, 100, 15, step=5)
        
        st.markdown("---")
        cluster_k = st.slider("Number of Skill Clusters (k)", 2, 8, 5, step=1)
        strict_core = st.checkbox("Strict Core Skills Mode", value=False, help="Penalizes candidates if any required mandatory skill is missing.")

    st.markdown("---")
    with st.expander("🗑️ Dataset Management / Reset", expanded=False):
        st.caption("Manage or reset the candidate pool:")
        if st.button("🗑️ Delete All Resumes (Start Fresh)", use_container_width=True):
            service.clear_all_candidates()
            st.success("All existing resumes deleted! Upload fresh CVs in the Upload tab.")
            st.rerun()
            
        if st.button("🔄 Generate Fresh Synthetic Pool", use_container_width=True):
            service.regenerate_fresh_dataset(160)
            st.success("Generated 160 brand-new candidate profiles!")
            st.rerun()

screening_res = service.run_screening(
    job_id=active_job_id,
    skill_weight=float(skill_weight),
    exp_weight=float(exp_weight),
    edu_weight=float(edu_weight),
    project_weight=float(proj_weight),
    n_clusters=cluster_k,
    strict_core_skills=strict_core
)

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

st.title("🧠 AI Resume Screening & Skill Clustering Dashboard")
st.markdown(f"**Active Opening**: `{active_job.title}` ({active_job.department}) | **Target Experience**: `{active_job.min_experience_years} Years`")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Resumes in Pool", screening_res.total_candidates_screened)
with col2:
    st.metric("Shortlisted (Score ≥ 70%)", screening_res.shortlisted_count)
with col3:
    st.metric("Skill Clusters Discovered", len(screening_res.clusters))
with col4:
    top_score = screening_res.results[0].score_breakdown.overall_score if screening_res.results else 0
    st.metric("Top Candidate Score", f"{top_score}%")

with st.expander("📋 View Active Job Requirements & Responsibilities", expanded=False):
    st.write(f"**Description**: {active_job.description}")
    req_col, pref_col = st.columns(2)
    with req_col:
        st.markdown("**Required Core Skills:**")
        st.write(", ".join([f"`{s}`" for s in active_job.required_skills]))
    with pref_col:
        st.markdown("**Preferred / Bonus Skills:**")
        st.write(", ".join([f"`+{s}`" for s in active_job.preferred_skills]) if active_job.preferred_skills else "None specified")
    st.markdown("**Key Responsibilities:**")
    for resp in active_job.responsibilities:
        st.write(f"- {resp}")

tab_upload, tab_shortlist, tab_clusters, tab_explain, tab_new_job = st.tabs([
    "📥 Dynamic CV Upload Box",
    "🏆 Candidate Shortlist",
    "🧩 Skill Archetype Clusters",
    "🔎 Explainability Inspector",
    "➕ Create Custom Job"
])

with tab_upload:
    st.subheader("📥 Dynamic & Automatic Resume / CV Upload Box")
    st.markdown("Upload candidate resumes in **PDF, DOCX, or TXT** format (or drag-and-drop multiple CV files). The AI extractor will automatically parse structured entities, evaluate candidates against the active opening, and cluster them into skill archetypes.")
    
    upload_mode = st.radio("Choose Input Method:", ["📁 Drag & Drop File Upload (PDF, DOCX, TXT)", "✍️ Paste Resume Text"], horizontal=True)
    
    if upload_mode == "📁 Drag & Drop File Upload (PDF, DOCX, TXT)":
        uploaded_files = st.file_uploader(
            "Drop Single or Batch Resume Files Here",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            help="Supports PDF, DOCX, TXT. You can upload multiple resumes at once."
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected for processing.")
            if st.button(f"⚡ Automatically Process & Screen {len(uploaded_files)} Resume(s)", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                newly_added = []
                
                for idx, file in enumerate(uploaded_files):
                    status_text.text(f"Processing ({idx+1}/{len(uploaded_files)}): {file.name}...")
                    file_bytes = file.read()
                    cand = service.add_resume_file(file_bytes, file.name)
                    newly_added.append(cand)
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                status_text.success(f"🎉 Successfully extracted and screened {len(newly_added)} candidate resume(s)!")
                
                refresh_res = service.run_screening(active_job_id, force_refresh=True)
                
                st.markdown("#### 📋 Extraction & Screening Summary for Uploaded Batch:")
                batch_summary = []
                for c in newly_added:
                    c_res = next((r for r in refresh_res.results if r.candidate.id == c.id), None)
                    batch_summary.append({
                        "Candidate Name": c.name,
                        "Experience": f"{c.years_exp} yrs",
                        "Extracted Skills": ", ".join(c.skills[:5]),
                        "Education": c.education.degree,
                        "Match Score": f"{c_res.score_breakdown.overall_score}%" if c_res else "N/A",
                        "Assigned Cluster": c_res.cluster_name if c_res else "N/A",
                        "Rank": f"#{c_res.rank}" if c_res else "N/A"
                    })
                st.dataframe(pd.DataFrame(batch_summary), use_container_width=True)
                st.info("💡 Switch to the **'Candidate Shortlist'** or **'Explainability Inspector'** tab to explore full scorecards.")
                
    else:
        custom_resume_text = st.text_area(
            "Paste Raw Resume Content:",
            height=200,
            placeholder="""Pritam Kumar Modak
Email: pritam.modak@example.com | Experience: 5.5 Years in Fullstack & Cloud
Skills: React, TypeScript, Next.js, Node.js, Express, PostgreSQL, Docker, AWS, Git
Education: B.Tech in Information Technology
Companies: TCS, Cognizant
Projects:
- Built scalable web platforms in React 18, TypeScript, and Node.js microservices handling high traffic.
- Deployed containerized applications with Docker on AWS."""
        )
        
        if st.button("⚡ Extract Structured Fields & Screen Resume", type="primary"):
            if not custom_resume_text.strip():
                st.error("Please enter resume text.")
            else:
                with st.spinner("Extracting structured fields and scoring..."):
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
                    st.markdown(f"**Extracted Education**: `{new_cand.education.degree}` ({new_cand.education.level})")
                    st.markdown(f"**Assigned Skill Cluster**: `{new_cand_res.cluster_name}`")

with tab_shortlist:
    st.subheader(f"Ranked Candidate Shortlist ({len(filtered_results)} candidates showing)")
    
    if not filtered_results:
        if screening_res.total_candidates_screened == 0:
            st.info("ℹ️ The candidate pool is currently empty. Go to the **'Dynamic CV Upload Box'** tab to upload resumes, or click **'Generate Fresh Synthetic Pool'** in the sidebar!")
        else:
            st.warning("No candidates match the specified filters. Try lowering the minimum score or experience sliders.")
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

with tab_clusters:
    st.subheader("🧩 Candidate Skill Archetypes (K-Means Clustering)")
    st.caption("Candidates grouped by latent skill vectors and project keywords to uncover distinct talent pools.")
    
    if not screening_res.clusters:
        st.info("No skill clusters available. Upload resumes to generate clusters.")
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
        total_w = skill_weight + exp_weight + edu_weight + proj_weight or 1
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric(f"1. Skills Overlap ({int(skill_weight/total_w*100)}%)", f"{b.skill_score}%", f"{round(b.skill_score * (skill_weight/total_w), 1)} pts")
        with mcol2:
            st.metric(f"2. Experience Fit ({int(exp_weight/total_w*100)}%)", f"{b.experience_score}%", f"{round(b.experience_score * (exp_weight/total_w), 1)} pts")
        with mcol3:
            st.metric(f"3. Education Fit ({int(edu_weight/total_w*100)}%)", f"{b.education_score}%", f"{round(b.education_score * (edu_weight/total_w), 1)} pts")
        with mcol4:
            st.metric(f"4. Project Match ({int(proj_weight/total_w*100)}%)", f"{b.project_score}%", f"{round(b.project_score * (proj_weight/total_w), 1)} pts")
            
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
                st.markdown("<br>**Bonus Preferred Skills Matched:**", unsafe_allow_html=True)
                for s in b.matched_preferred_skills:
                    st.markdown(f"<span class='pref-badge'>★ {s}</span> ", unsafe_allow_html=True)
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

with tab_new_job:
    st.subheader("➕ Create / Define a New Job Description")
    st.caption("Add a custom job opening to screen all candidates against.")
    
    with st.form("new_job_form"):
        nj_title = st.text_input("Job Title", placeholder="e.g. Lead Machine Learning Engineer")
        nj_dept = st.selectbox("Department", ["Engineering", "AI & Research", "Infrastructure", "Quality Assurance", "Analytics", "Backend", "Frontend", "Product"])
        nj_exp = st.number_input("Minimum Experience (Years)", min_value=0.0, max_value=15.0, value=3.0, step=0.5)
        nj_req_skills = st.text_input("Required Skills (Comma separated)", placeholder="e.g. PyTorch, Python, Docker, FastAPI, Computer Vision")
        nj_pref_skills = st.text_input("Preferred / Bonus Skills (Comma separated)", placeholder="e.g. Kubernetes, MLflow, AWS, OpenCV")
        nj_edu = st.selectbox("Minimum Education Level", ["Bachelor", "Master", "Doctorate", "Associate", "Bootcamp"])
        nj_desc = st.text_area("Job Summary / Description", placeholder="Brief description of the role...")
        nj_resp = st.text_area("Key Responsibilities (One per line)", placeholder="Design and train neural networks\nDeploy models to cloud infrastructure\nCollaborate with product teams")
        
        submitted = st.form_submit_button("🚀 Create Job & Run Initial Screening", type="primary")
        if submitted:
            if not nj_title.strip() or not nj_req_skills.strip():
                st.error("Please fill in Job Title and Required Skills.")
            else:
                new_j_id = f"job_{nj_title.lower().replace(' ', '_').replace('/', '_')[:25]}"
                req_list = [s.strip() for s in nj_req_skills.split(',') if s.strip()]
                pref_list = [s.strip() for s in nj_pref_skills.split(',') if s.strip()]
                resp_list = [r.strip() for r in nj_resp.split('\n') if r.strip()]
                
                new_job_obj = JobDescription(
                    id=new_j_id,
                    title=nj_title.strip(),
                    department=nj_dept,
                    min_experience_years=nj_exp,
                    required_skills=req_list,
                    preferred_skills=pref_list,
                    min_education=nj_edu,
                    description=nj_desc.strip(),
                    responsibilities=resp_list
                )
                service.add_job(new_job_obj)
                st.success(f"Job **{nj_title}** created successfully! Select it from the sidebar to view candidate rankings.")
                st.rerun()
