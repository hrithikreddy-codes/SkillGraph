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

    st.title("📄 AI Resume & Job-Readiness Analyzer")
    st.write(
        "Paste your resume and a job description to see how well you match."
    )

    # --- Text areas ---
    st.subheader("1️⃣  Paste your resume")
    resume_text_area = st.text_area(
        "Paste your resume",
        height=200,
    )

    st.subheader("2️⃣  Paste the job description")
    job_description_area = st.text_area(
        "Paste the job description",
        height=200,
    )

    # --- Analyze button ---
    st.subheader("3️⃣  Run the analysis")
    analyze_button = st.button("🚀 Analyze", use_container_width=True)

    if analyze_button:
        try:
            if not resume_text_area.strip() or not job_description_area.strip():
                st.warning("⚠️ Please provide both a resume and a job description.")
                return
                
            with st.spinner("🤖 Analyzing skills..."):
                from analyzer import extract_resume_skills, extract_job_skills, compare, build_graph
                resume_data = extract_resume_skills(resume_text_area)
                job_data = extract_job_skills(job_description_area)
                match_results = compare(resume_data, job_data)
                
                st.markdown("---")
                st.subheader("📋 Match Results")
                st.metric("Match Percentage", f"{match_results['match_percent']}%")
                
                # Skill lists
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**Matched Skills:** {', '.join(match_results['matched']) if match_results['matched'] else 'None'}")
                    if match_results['bonus_matched']:
                        st.info(f"**Bonus Matched:** {', '.join(match_results['bonus_matched'])}")
                with col2:
                    st.error(f"**Missing Skills:** {', '.join(match_results['missing']) if match_results['missing'] else 'None'}")
                    if match_results['bonus_missing']:
                        st.warning(f"**Bonus Missing:** {', '.join(match_results['bonus_missing'])}")
                
                # Graph
                st.markdown("---")
                st.subheader("Your Skill Graph")
                job_role = job_data.get("role", "Job Role")
                dot_string = build_graph(job_role, match_results)
                st.graphviz_chart(dot_string)
                st.caption("🟢 Green = skills you have | 🔴 Red dashed = skills to learn")
                
                # Next Steps / Roadmap
                st.markdown("---")
                st.subheader("🚀 Your Next Steps")
                missing_skills = match_results.get("missing", [])
                
                if not missing_skills:
                    st.balloons()
                    st.success("🎉 Incredible! Your resume already covers every required skill for this role.")
                else:
                    from analyzer import generate_roadmap
                    roadmap = generate_roadmap(missing_skills, job_role)
                    for step in roadmap.get("steps", []):
                        skill_name = step.get("skill", "")
                        with st.expander(f"📘 {skill_name}"):
                            st.markdown(f"**Why it matters:** {step.get('why_it_matters', '')}")
                            st.markdown(f"**How to learn:** {step.get('how_to_learn', '')}")
                            st.markdown(f"**Time estimate:** {step.get('time_estimate', '')}")
        except Exception:
            st.error("Something went wrong, please try again")



def _legacy_ui_code_do_not_call():
    # Note: We removed the API key sidebar! The app now safely loads 
    # your keys directly from the .env file in the background.

    # --- File upload ---
    st.subheader("1️⃣  Upload your resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"],
        help="Supported formats: .pdf, .txt",
    )

    # --- Optional job description ---
    st.subheader("2️⃣  Paste a job description (optional)")
    job_description = st.text_area(
        "Paste the full job posting here for a match analysis",
        height=150,
        placeholder="Copy-paste a job description from LinkedIn, Indeed, etc.",
    )

    # --- Analyze button ---
    st.subheader("3️⃣  Run the analysis")
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
        st.subheader("📋 Analysis Results")
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
