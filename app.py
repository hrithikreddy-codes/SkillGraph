"""
AI Resume & Job-Readiness Analyzer
===================================
A beginner-friendly Streamlit app that uses Google's free Gemini API
to analyze your resume and give you actionable feedback.

How to run:
    streamlit run app.py
"""

import streamlit as st
from PyPDF2 import PdfReader
import io
import traceback
# Force Streamlit to reload the updated analyzer.py

# Import our AI logic from the new analyzer.py file
from analyzer import analyze_resume

# ---------------------------------------------------------------------------
# 1.  HELPER FUNCTION — Extract text from an uploaded PDF file
# ---------------------------------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Takes a PDF file uploaded through Streamlit and returns all the text
    inside it as one big string.
    """
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if not text.strip():
            return None
        return text
    except Exception as e:
        st.error(f"❌ Could not read this PDF: {e}")
        return None


# ---------------------------------------------------------------------------
# 2.  STREAMLIT UI — Everything the user sees and interacts with
# ---------------------------------------------------------------------------
def main():
    # --- Page configuration ---
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="centered",
    )
    
    if st.sidebar.button("Clear saved results"):
        st.cache_data.clear()

    st.title("📄 AI Resume & Job-Readiness Analyzer")
    st.markdown("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>", unsafe_allow_html=True)
    st.write(
        "Paste your resume and a job description to see how well you match."
    )

    # --- Text areas ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1️⃣  Your Resume", anchor=False)
        tab1, tab2 = st.tabs(["Paste text", "Upload file"])
        with tab1:
            resume_text_area = st.text_area(
                "Resume text",
                height=120,
                label_visibility="collapsed",
                placeholder="Paste your resume here..."
            )
        with tab2:
            uploaded_resume = st.file_uploader(
                "Upload resume file", 
                type=["pdf", "docx", "txt"], 
                label_visibility="collapsed"
            )
            extracted_text = ""
            if uploaded_resume:
                from file_reader import extract_text
                extracted_text = extract_text(uploaded_resume)
                if not extracted_text:
                    st.warning("Couldn't read text from this file (scanned PDF?). Please paste the text instead.")
                else:
                    with st.expander("Preview extracted text"):
                        st.text(extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""))

    with col2:
        st.subheader("2️⃣  Job Description", anchor=False)
        job_tab, = st.tabs(["Paste text"])
        with job_tab:
            job_description_area = st.text_area(
                "Job description text",
                height=120,
                label_visibility="collapsed",
                placeholder="Paste the job description here..."
            )

    # --- Analyze button ---
    st.subheader("3️⃣  Run the analysis", anchor=False)
    analyze_button = st.button("🚀 Analyze", use_container_width=True)

    if analyze_button:
        try:
            final_resume_text = resume_text_area.strip()
            if not final_resume_text and uploaded_resume:
                final_resume_text = extracted_text

            if not final_resume_text or not job_description_area.strip():
                st.warning("⚠️ Please provide both a resume and a job description.")
                return
                
            with st.spinner("Analyzing your resume against the job..."):
                from analyzer import extract_resume_skills, extract_job_skills, compare, build_graph, assess_other_requirements
                resume_data = extract_resume_skills(final_resume_text)
                job_data = extract_job_skills(job_description_area)
                match_results = compare(final_resume_text, resume_data, job_data)
                
                from analyzer import score_breakdown
                scores = score_breakdown(match_results)
                match_results["match_percent"] = scores["match_percent"]
                
                st.markdown("---")
                st.subheader("📋 Match Results", anchor=False)
                st.metric("Match Percentage", f"{scores['match_percent']}%")
                st.caption("Core skill match: matched + half of partial, out of required skills")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Required skills", scores["total_required"])
                m2.metric("Matched", scores["matched_count"])
                m3.metric("Partial", scores["partial_count"])
                m4.metric("Missing", scores["missing_count"])
                
                if not scores.get("consistent", True):
                    st.warning("⚠️ Warning: Score calculations were inconsistent. Some skills may be overlapping or percentages differ.")
                
                # Skill lists
                st.success(f"**Matched Skills:** {', '.join(match_results['matched']) if match_results['matched'] else 'None'}")
                
                st.markdown("**Required gaps (affect your score)**")
                col1, col2 = st.columns(2)
                with col1:
                    if match_results.get('partial'):
                        st.warning(f"**Partial Match:** {', '.join(match_results['partial'])}")
                with col2:
                    st.error(f"**Missing:** {', '.join(match_results['missing']) if match_results['missing'] else 'None'}")
                    
                if match_results.get('bonus_matched') or match_results.get('bonus_missing'):
                    with st.expander("Preferred by the job (does not affect your score)"):
                        if match_results.get('bonus_matched'):
                            st.info(f"**Bonus Matched:** {', '.join(match_results['bonus_matched'])}")
                        if match_results.get('bonus_missing'):
                            st.warning(f"**Bonus Missing:** {', '.join(match_results['bonus_missing'])}")
                        
                verified_skills = set(match_results.get("evidence", {}).keys()) | set(match_results.get("reasons", {}).keys())
                if verified_skills:
                    with st.expander("Why we classified skills this way"):
                        matched_list = [s for s in sorted(verified_skills) if s in match_results.get("matched", [])]
                        partial_list = [s for s in sorted(verified_skills) if s in match_results.get("partial", [])]
                        missing_list = [s for s in sorted(verified_skills) if s not in match_results.get("matched", []) and s not in match_results.get("partial", [])]
                        
                        if matched_list:
                            st.subheader("Matched", anchor=False)
                            for skill in matched_list:
                                ev_type = match_results.get("evidence_type", {}).get(skill, "")
                                conf_text = " (inferred)" if ev_type == "inferred" else ""
                                evidence = match_results.get("evidence", {}).get(skill, "")
                                reason = match_results.get("reasons", {}).get(skill, "")
                                
                                parts = []
                                if evidence:
                                    parts.append(f'Evidence: "{evidence}"')
                                if reason:
                                    parts.append(f"Reason: {reason}")
                                
                                desc = " | ".join(parts) if parts else "No additional details."
                                st.write(f"🟢 **{skill}**{conf_text}: {desc}")
                                
                        if partial_list:
                            st.subheader("Partial", anchor=False)
                            for skill in partial_list:
                                ev_type = match_results.get("evidence_type", {}).get(skill, "")
                                conf_text = " (inferred)" if ev_type == "inferred" else ""
                                evidence = match_results.get("evidence", {}).get(skill, "")
                                reason = match_results.get("reasons", {}).get(skill, "")
                                gap = match_results.get("gaps", {}).get(skill, "")
                                
                                parts = []
                                if evidence:
                                    parts.append(f'Evidence: "{evidence}"')
                                if reason:
                                    parts.append(f"Why partial: {reason}")
                                if gap:
                                    parts.append(f"What's missing: {gap}")
                                    
                                desc = " | ".join(parts) if parts else "No additional details."
                                st.write(f"🟡 **{skill}**{conf_text}: {desc}")
                                
                        if missing_list:
                            st.subheader("Not demonstrated yet", anchor=False)
                            for skill in missing_list:
                                ev_type = match_results.get("evidence_type", {}).get(skill, "")
                                conf_text = " (inferred)" if ev_type == "inferred" else ""
                                evidence = match_results.get("evidence", {}).get(skill, "")
                                reason = match_results.get("reasons", {}).get(skill, "")
                                
                                parts = []
                                if evidence:
                                    parts.append(f'Evidence: "{evidence}"')
                                if reason:
                                    parts.append(f"Reason: {reason}")
                                    
                                desc = " | ".join(parts) if parts else "No additional details."
                                st.write(f"🔴 **{skill}**{conf_text}: {desc}")
                soft = job_data.get("soft_skills", [])
                exp_req = job_data.get("experience_requirements", [])
                if soft or exp_req:
                    st.markdown("---")
                    st.subheader("Other requirements (not part of your score)", anchor=False)
                    other_res = assess_other_requirements(final_resume_text, soft, exp_req)
                    for item_res in other_res.get("results", []):
                        it = item_res.get("item", "")
                        st_stat = item_res.get("status", "")
                        ev = item_res.get("evidence", "")
                        
                        if st_stat == "supported":
                            st.markdown(f"- **{it}**: :green[supported] — *{ev}*")
                        else:
                            st.markdown(f"- **{it}**: :gray[not shown]")
                
                # Graph
                st.markdown("---")
                st.subheader("Your Skill Graph", anchor=False)
                job_role = job_data.get("role", "Job Role")
                dot_string = build_graph(job_role, match_results)
                
                @st.dialog("Full Screen Skill Graph", width="large")
                def show_full_graph():
                    st.graphviz_chart(dot_string, use_container_width=True)
                
                if st.button("🔍 View Full Screen Graph"):
                    show_full_graph()
                    
                st.graphviz_chart(dot_string)
                st.caption("🟢 Green ✓ = skills you have | 🟡 Amber ~ = partial | 🔴 Red ✗ = skills to learn")
                
                # Next Steps / Roadmap
                st.markdown("---")
                st.subheader("🚀 Your Next Steps", anchor=False)
                missing_skills = match_results.get("missing", [])
                partial_skills = match_results.get("partial", [])
                
                from analyzer import generate_roadmap, build_html_report
                roadmap = generate_roadmap(missing_skills, partial_skills, job_role, resume_data.get("projects", []), job_description_area, match_results.get("evidence", {}), match_results.get("gaps", {}))
                
                if not missing_skills and not partial_skills:
                    st.balloons()
                    st.success("🎉 Incredible! Your resume already covers every required skill for this role.")
                else:
                    groups = {"High": [], "Medium": [], "Low": []}
                    for step in roadmap.get("steps", []):
                        pri = step.get("priority", "Medium")
                        if pri not in groups:
                            pri = "Medium"
                        groups[pri].append(step)
                        
                    for pri_label, pri_key in [("High priority", "High"), ("Medium priority", "Medium"), ("Lower priority", "Low")]:
                        if groups[pri_key]:
                            sorted_steps = sorted(groups[pri_key], key=lambda x: x.get("order", 999))
                            st.markdown(f"**{pri_label}**")
                            for step in sorted_steps:
                                skill_name = step.get("skill", "")
                                order_val = step.get("order", "?")
                                eff = step.get("suggested_effort", "")
                                
                                exp_title = f"{order_val}. {skill_name} ({eff})" if eff else f"{order_val}. {skill_name}"
                                with st.expander(exp_title):
                                    if step.get("do_after"):
                                        st.markdown(f"**Do this after:** {step.get('do_after')}")
                                    st.markdown(f"**Why this is a gap:** {step.get('why_gap', '')}")
                                    st.markdown(f"**Learn:** {step.get('learn', '')}")
                                    st.markdown(f"**Apply:** {step.get('apply', '')}")
                                    st.markdown(f"**Prove it:** {step.get('prove', '')}")
                                    st.markdown(f"**Example resume bullet (write this only after you complete the step):** {step.get('example_bullet', '')}")
                                    
                    optional_items = roadmap.get("optional", [])
                    if optional_items:
                        st.markdown("---")
                        st.markdown("**Extra suggestions (not in the job description)**")
                        for item in optional_items:
                            st.markdown(f"- **{item.get('skill', '')}**: {item.get('reason', '')}")
                                    
                    st.caption("After you finish a step, add the resume bullet and run the analysis again to watch the gap close.")
                            
                # Export Report
                st.markdown("---")
                report = f"# Career Analysis: {job_role}\n\n"
                report += f"**Match Score:** {match_results['match_percent']}%\n\n"
                report += f"### ✅ Matched Skills\n{', '.join(match_results['matched']) if match_results['matched'] else 'None'}\n\n"
                if match_results.get('partial'):
                    report += f"### ⚠️ Partial Skills\n{', '.join(match_results['partial'])}\n\n"
                report += f"### ❌ Missing Skills\n{', '.join(match_results['missing']) if match_results['missing'] else 'None'}\n\n"
                report += "### 🚀 Your Roadmap\n"
                if not missing_skills and not partial_skills:
                    report += "You already have all required skills!\n"
                else:
                    for step in roadmap.get("steps", []):
                        report += f"\n#### {step.get('order', '?')}. {step.get('skill', '')} ({step.get('priority', 'Medium')} Priority)\n"
                        report += f"- **Why this is a gap:** {step.get('why_gap', '')}\n"
                        report += f"- **Learn:** {step.get('learn', '')}\n"
                        report += f"- **Apply:** {step.get('apply', '')}\n"
                        report += f"- **What proves it:** {step.get('prove', '')}\n"
                        report += f"- **Example resume bullet (write this only after you complete the step):** {step.get('example_bullet', '')}\n"
                        report += f"- **Estimated effort:** {step.get('suggested_effort', '')}\n"
                        
                    optional_items = roadmap.get("optional", [])
                    if optional_items:
                        report += "\n### ✨ Extra suggestions (not in the job description)\n"
                        for item in optional_items:
                            report += f"- **{item.get('skill', '')}**: {item.get('reason', '')}\n"
                            
                html_report = build_html_report(job_role, match_results, scores, roadmap)
                st.download_button("Download report (HTML)", data=html_report, file_name="skillgraph_report.html", mime="text/html")
                st.download_button("📥 Download Full Report", report, file_name="skill_report.md", mime="text/markdown")
        except Exception as e:
            traceback.print_exc()
            st.error("Something went wrong, please try again")
            with st.expander("Technical details"):
                st.exception(e)



def _legacy_ui_code_do_not_call():
    # Note: We removed the API key sidebar! The app now safely loads 
    # your keys directly from the .env file in the background.

    # --- File upload ---
    st.subheader("1️⃣  Upload your resume", anchor=False)
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"],
        help="Supported formats: .pdf, .txt",
    )

    # --- Optional job description ---
    st.subheader("2️⃣  Paste a job description (optional)", anchor=False)
    job_description = st.text_area(
        "Paste the full job posting here for a match analysis",
        height=150,
        placeholder="Copy-paste a job description from LinkedIn, Indeed, etc.",
    )

    # --- Analyze button ---
    st.subheader("3️⃣  Run the analysis", anchor=False)
    analyze_button = st.button("🚀 Analyze My Resume", use_container_width=True)

    # --- When the button is clicked ---
    if analyze_button:
        # Guard: a file must be uploaded
        if not uploaded_file:
            st.warning("⚠️ Please upload a resume file first.")
            return

        # --- Extract text depending on file type ---
        if uploaded_file.name.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            # For .txt files, just decode the bytes to a string
            resume_text = uploaded_file.read().decode("utf-8", errors="ignore")

        if not resume_text or not resume_text.strip():
            st.error(
                "❌ Could not extract any text from this file. "
                "If it's a scanned PDF, try a text-based version."
            )
            return

        # Show a preview so the user can verify the right file was uploaded
        with st.expander("👀 Preview extracted text", expanded=False):
            st.text(resume_text[:3000])

        # --- Call Gemini (now using analyzer.py) ---
        with st.spinner("🤖 Gemini is analyzing your resume… (15-30 seconds)"):
            # We no longer pass api_key here; analyzer.py handles it!
            result = analyze_resume(resume_text, job_description)

        # --- Display results ---
        st.markdown("---")
        st.subheader("📋 Analysis Results", anchor=False)
        st.markdown(result)

        # --- Download button for the report ---
        st.download_button(
            label="💾 Download Report as Text",
            data=result,
            file_name="resume_analysis_report.md",
            mime="text/markdown",
        )


# ---------------------------------------------------------------------------
# 3.  ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
