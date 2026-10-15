"""
SkillGraph - Career Roadmap Generator (Streamlit)
Run with:  streamlit run app.py
Needs:     pip install streamlit   (version 1.32 or newer)

File layout (top to bottom):
  1. DATA      - all the career content lives in plain dictionaries (easy to edit)
  2. STYLES    - one CSS block that gives the app its look and animations
  3. LOGIC     - build_roadmap() turns the user's answers into phases
  4. UI        - render_hero(), render_form(), render_results()
"""

import html

import altair as alt
import pandas as pd
import streamlit as st
from analyzer import (
    assess_other_requirements,
    build_graph,
    build_html_report,
    compare,
    extract_job_skills,
    extract_resume_skills,
    generate_roadmap,
    score_breakdown,
)
from file_reader import extract_text

st.set_page_config(page_title="SkillGraph - Your Career Roadmap", page_icon="🧭", layout="centered")


# ============================================================
# 1. DATA - edit these to change the content, no UI code needed
# ============================================================
LEVELS = {
    "School": {
        "note": "You have time on your side. Explore widely and keep the stakes low.",
        "experience": ["Join or start a school coding, science or design club",
                       "Try one online contest or challenge made for students"],
        "prep": ["Talk to 2-3 people who do this job and ask what a normal day looks like",
                 "Shortlist the courses and entrance exams that lead to this career"],
    },
    "Intermediate / 12th": {
        "note": "Your next big decision is your degree. Pick one that keeps this path open.",
        "experience": ["Join a first-year community or hackathon in your target college",
                       "Do one small volunteer or freelance project"],
        "prep": ["Shortlist degree programs and the entrance exams they need",
                 "Keep 30 minutes a day for skills next to exam preparation"],
    },
    "B.Tech / Engineering": {
        "note": "You are well placed to move fast. Use your college labs, clubs and placement season.",
        "experience": ["Apply for internships (start looking 6 months before you need one)",
                       "Join a college tech club and a hackathon team"],
        "prep": ["Build a one-page resume and a LinkedIn profile",
                 "Do mock interviews with friends or seniors"],
    },
    "Degree": {
        "note": "Any stream works if you can show real skills. Proof of work matters most.",
        "experience": ["Earn one certification that is relevant to this career",
                       "Contribute to a beginner-friendly open-source or volunteer project"],
        "prep": ["Write a resume that leads with projects, not marks",
                 "Message 5 people working in this role on LinkedIn"],
    },
    "Diploma": {
        "note": "A diploma gives you a practical base. Use skill proof or lateral entry to go further.",
        "experience": ["Look for apprenticeships and internships",
                       "Check lateral-entry options if you want a degree later"],
        "prep": ["Build a portfolio that shows what you can do",
                 "Message 5 people working in this role on LinkedIn"],
    },
    "Other": {
        "note": "Everyone starts somewhere. A steady weekly routine beats any background.",
        "experience": ["Join an online community for this field",
                       "Do one small freelance or volunteer project"],
        "prep": ["Build a portfolio that shows what you can do",
                 "Message 5 people working in this role on LinkedIn"],
    },
}

STRENGTH_TIPS = {
    "Problem Solving": "Problem solving is your head start. Solve one or two small logic or coding problems every day.",
    "Creativity": "Creativity sets you apart. Make each project look and feel like yours, not a tutorial copy.",
    "Communication": "Communication is rare in tech. Write about what you build and practice demoing it out loud.",
    "Mathematics": "Maths is a strength. Start the statistics and algorithm topics earlier than most beginners.",
}

INTERESTS = {
    "software": {
        "label": "Software Development", "emoji": "💻",
        "foundation": ["Learn Python or JavaScript basics: variables, loops, functions",
                       "Understand how the web works: HTML, CSS and HTTP",
                       "Set up Git and a GitHub account"],
        "core": ["Study data structures and algorithms basics",
                 "Build a backend with Flask, FastAPI or Node",
                 "Learn SQL and one database"],
        "tools": ["Python", "Git", "SQL", "VS Code", "REST APIs"],
        "projects": ["Beginner: personal portfolio website",
                     "Intermediate: to-do app with login and a database",
                     "Advanced: full-stack app deployed online"],
        "interview": "data structures and algorithms",
        "resources": [("CS50 by Harvard", "https://cs50.harvard.edu"),
                      ("freeCodeCamp", "https://www.freecodecamp.org")],
    },
    "ai": {
        "label": "Artificial Intelligence", "emoji": "🤖",
        "foundation": ["Learn Python with NumPy and pandas",
                       "Refresh linear algebra, probability and statistics",
                       "Run your first notebook in Jupyter or Google Colab"],
        "core": ["Learn supervised and unsupervised learning with scikit-learn",
                 "Build neural networks with PyTorch or TensorFlow",
                 "Learn how to measure and improve a model"],
        "tools": ["Python", "NumPy", "scikit-learn", "PyTorch", "Jupyter"],
        "projects": ["Beginner: house price predictor",
                     "Intermediate: image classifier",
                     "Advanced: chatbot app using an LLM API"],
        "interview": "machine learning concepts",
        "resources": [("Kaggle Learn", "https://www.kaggle.com/learn"),
                      ("fast.ai course", "https://course.fast.ai")],
    },
    "data": {
        "label": "Data Science", "emoji": "📊",
        "foundation": ["Get comfortable with Excel or Google Sheets",
                       "Learn Python with pandas",
                       "Learn basic statistics: mean, spread, probability"],
        "core": ["Learn SQL for real queries",
                 "Make charts with Matplotlib or Power BI",
                 "Do exploratory data analysis, then basic machine learning"],
        "tools": ["Python", "SQL", "pandas", "Power BI", "Excel"],
        "projects": ["Beginner: IPL match stats dashboard",
                     "Intermediate: analyse a public government dataset",
                     "Advanced: end-to-end prediction project with a short report"],
        "interview": "SQL and statistics",
        "resources": [("Kaggle Learn", "https://www.kaggle.com/learn"),
                      ("freeCodeCamp", "https://www.freecodecamp.org")],
    },
    "cyber": {
        "label": "Cybersecurity", "emoji": "🛡️",
        "foundation": ["Learn networking: TCP/IP, DNS and HTTP",
                       "Get comfortable with the Linux command line",
                       "Learn basic Python scripting"],
        "core": ["Study the OWASP Top 10 web vulnerabilities",
                 "Learn the basics of cryptography",
                 "Practice on legal, hands-on labs only"],
        "tools": ["Linux", "Wireshark", "Nmap", "Burp Suite", "Python"],
        "projects": ["Beginner: home lab with virtual machines",
                     "Intermediate: password-strength checker in Python",
                     "Advanced: written walkthroughs of solved CTF challenges"],
        "interview": "networking and web security",
        "resources": [("TryHackMe", "https://tryhackme.com"),
                      ("picoCTF", "https://picoctf.org")],
    },
    "design": {
        "label": "UI/UX Design", "emoji": "🎨",
        "foundation": ["Learn design basics: hierarchy, contrast, spacing",
                       "Study typography and colour",
                       "Create a free Figma account and follow a starter tutorial"],
        "core": ["Learn user research and how to run short interviews",
                 "Make wireframes, then clickable prototypes",
                 "Learn accessibility basics"],
        "tools": ["Figma", "FigJam", "Miro", "Notion"],
        "projects": ["Beginner: redesign one screen of an app you use",
                     "Intermediate: full mobile app case study",
                     "Advanced: design system plus a usability test with 5 people"],
        "interview": "design critique and case studies",
        "resources": [("Figma resource library", "https://www.figma.com/resource-library/"),
                      ("Google UX Design (Coursera)", "https://www.coursera.org/professional-certificates/google-ux-design")],
    },
    "business": {
        "label": "Business / Entrepreneurship", "emoji": "🚀",
        "foundation": ["Learn how companies make money: pricing, costs, margins",
                       "Practice talking to customers and listening",
                       "Learn basic finance in Excel or Google Sheets"],
        "core": ["Learn market research and competitor analysis",
                 "Learn marketing and sales basics",
                 "Build a simple MVP with no-code tools"],
        "tools": ["Google Sheets", "Canva", "Notion", "No-code builders"],
        "projects": ["Beginner: sell a small product or service to 10 people",
                     "Intermediate: test a startup idea with 20 customer interviews",
                     "Advanced: launch an MVP and track its numbers"],
        "interview": "business cases and market sizing",
        "resources": [("NPTEL courses", "https://nptel.ac.in"),
                      ("Startup School", "https://www.startupschool.org")],
    },
}

HERO_WORDS = ["AI Engineer", "Data Scientist", "UX Designer", "Security Analyst", "Software Developer", "Founder"]


# ============================================================
# 2. STYLES - one CSS block; Streamlit renders it via st.markdown
# ============================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root { --ink:#0f172a; --muted:#5b6475; --blue:#2563eb; --deep:#1e3a8a; --sky:#60a5fa; --amber:#fbbf24; --line:#e3e8f2; }

.stApp { background:#f4f6fb; color:var(--ink); }
.stApp, .stApp p, .stApp li, .stApp label, .stApp input { font-family:'DM Sans', Arial, sans-serif; }
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] { visibility:hidden; height:0; }
.block-container { max-width:860px; padding-top:1.5rem; padding-bottom:3rem; }

/* ---------- Hero: the one big animated moment ---------- */
.hero { position:relative; overflow:hidden; border-radius:24px; padding:56px 32px 52px; text-align:center; color:#fff;
  background:linear-gradient(120deg,#0f172a,#1e3a8a,#1d4ed8,#0f172a); background-size:300% 300%;
  animation:drift 16s ease infinite; margin-bottom:28px; }
.hero::before, .hero::after { content:""; position:absolute; border-radius:50%; filter:blur(60px); opacity:.45; }
.hero::before { width:260px; height:260px; background:#3b82f6; top:-80px; left:-60px; animation:float 9s ease-in-out infinite; }
.hero::after  { width:220px; height:220px; background:#f59e0b; bottom:-100px; right:-40px; opacity:.28; animation:float 11s ease-in-out infinite reverse; }
.hero > * { position:relative; z-index:1; }
.brand { font-family:'Sora',sans-serif; font-weight:700; font-size:20px; letter-spacing:.2px; margin-bottom:26px; }
.brand b { color:var(--sky); }
.hero h1 { font-family:'Sora',sans-serif; font-size:clamp(30px,6vw,48px); font-weight:800; line-height:1.15; margin:0 0 14px; }
.rotator-line { display:flex; justify-content:center; align-items:center; gap:10px; font-size:clamp(18px,3.4vw,24px); color:#dbeafe; margin-bottom:18px; }
.rotator { position:relative; height:1.5em; width:11em; text-align:left; }
.rotator span { position:absolute; left:0; top:0; opacity:0; color:var(--amber); font-weight:600; white-space:nowrap;
  animation:cycle 12s infinite; animation-fill-mode:both; }
.hero p.sub { max-width:560px; margin:0 auto; color:#c7d7f5; font-size:17px; line-height:1.6; }

@keyframes drift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes float { 0%,100%{transform:translate(0,0)} 50%{transform:translate(30px,24px)} }
@keyframes cycle { 0%{opacity:0;transform:translateY(14px)} 3%{opacity:1;transform:none} 14%{opacity:1;transform:none} 17%,100%{opacity:0;transform:translateY(-14px)} }
@keyframes rise { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }

/* ---------- Form ---------- */
[data-testid="stForm"] { background:#fff; border:1px solid var(--line); border-radius:20px; padding:28px; box-shadow:0 12px 32px rgba(15,23,42,.06); }
.form-title { font-family:'Sora',sans-serif; font-size:22px; font-weight:700; margin:0 0 4px; }
.form-hint { color:var(--muted); margin:0 0 18px; }
[data-baseweb="select"] > div, .stTextInput input { border-radius:12px !important; }
.stApp label p { font-weight:600; }

/* ---------- Buttons ---------- */
div[data-testid="stFormSubmitButton"] button, .stButton button, .stDownloadButton button {
  border-radius:12px; font-weight:700; padding:.7rem 1.2rem; border:1px solid var(--line); transition:transform .15s, box-shadow .15s; }
div[data-testid="stFormSubmitButton"] button { width:100%; background:linear-gradient(90deg,#2563eb,#1d4ed8); color:#fff; border:none; font-size:17px; }
div[data-testid="stFormSubmitButton"] button:hover { transform:translateY(-2px); box-shadow:0 10px 22px rgba(37,99,235,.35); color:#fff; }

/* ---------- Results ---------- */
.result-head { background:#fff; border:1px solid var(--line); border-radius:20px; padding:28px; margin-bottom:18px;
  box-shadow:0 12px 32px rgba(15,23,42,.06); animation:rise .6s ease both; }
.career { font-family:'Sora',sans-serif; font-size:clamp(26px,5vw,36px); font-weight:800; color:var(--deep); margin:0 0 8px; }
.summary { color:var(--muted); line-height:1.65; margin:0 0 14px; }
.tag { display:inline-block; padding:6px 12px; background:#e0ecff; color:#1e40af; border-radius:999px; margin:4px 6px 4px 0; font-size:13px; font-weight:600; }
.note { background:#eff6ff; border-left:4px solid var(--blue); padding:14px 16px; border-radius:0 12px 12px 0; margin-top:14px; line-height:1.6; }
.tips { margin:12px 0 0 18px; color:var(--ink); line-height:1.7; }

.progress { height:12px; background:#dfe6f3; border-radius:999px; overflow:hidden; }
.bar { height:100%; background:linear-gradient(90deg,#3b82f6,#2563eb); border-radius:999px; transition:width .8s cubic-bezier(.2,.8,.2,1); }
.pcount { color:var(--muted); font-size:14px; margin:8px 0 20px; }

[data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border-radius:18px; border:1px solid var(--line); }
.phase-top { display:flex; align-items:center; gap:14px; }
.badge { flex:0 0 40px; height:40px; border-radius:50%; background:var(--blue); color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Sora',sans-serif; font-weight:700; }
.phase-title { font-family:'Sora',sans-serif; font-size:19px; font-weight:700; margin:0; }
.when { margin-left:auto; font-size:13px; font-weight:600; color:#92400e; background:#fef3c7; padding:4px 10px; border-radius:999px; white-space:nowrap; }
.phase-blurb { color:var(--muted); margin:10px 0 6px; line-height:1.6; }
.goal { background:linear-gradient(135deg,#0f172a,#1e3a8a); color:#fff; border-radius:18px; padding:26px; margin-top:18px; }
.goal h4 { font-family:'Sora',sans-serif; margin:0 0 8px; }
.goal p { color:#dbeafe; line-height:1.6; margin:0; }
.foot { text-align:center; color:#6b7280; padding:28px 0 0; font-size:14px; }

@media (max-width:600px) { .hero { padding:40px 18px; } .rotator { width:9em; } .when { display:none; } }
@media (prefers-reduced-motion: reduce) {
  .hero, .hero::before, .hero::after, .result-head { animation:none; }
  .rotator span { animation:none; } .rotator span:first-child { opacity:1; }
}
</style>
"""


def clean(markup: str) -> str:
    """Streamlit treats indented / blank-line HTML as code. Strip it so HTML renders."""
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


# ============================================================
# 3. LOGIC - turn the user's answers into a list of phases
# ============================================================
def build_roadmap(profile: dict) -> list[dict]:
    topic = INTERESTS[profile["interest"]]
    level = LEVELS[profile["education"]]
    return [
        {"title": "Build your foundation", "when": "Weeks 1-6",
         "blurb": "Get comfortable with the basics before anything advanced.",
         "tasks": topic["foundation"], "tags": topic["tools"]},
        {"title": "Learn the core skills", "when": "Months 2-4",
         "blurb": "These are the skills people in this field use every day.",
         "tasks": topic["core"], "tags": []},
        {"title": "Build real projects", "when": "Months 4-6",
         "blurb": "Projects prove what you can do. Put every one on GitHub or in a portfolio.",
         "tasks": topic["projects"], "tags": []},
        {"title": "Gain experience", "when": "Months 6-9",
         "blurb": "Work with other people and real deadlines.",
         "tasks": level["experience"] + ["Enter one hackathon or online competition"], "tags": []},
        {"title": "Prepare for your career", "when": "Months 9-12",
         "blurb": "Turn your skills into something a recruiter or college can see.",
         "tasks": level["prep"] + [f"Practice {topic['interview']} questions every week"], "tags": []},
    ]


def roadmap_as_markdown(profile: dict, phases: list[dict]) -> str:
    """Plain-text version of the roadmap for the download button."""
    lines = [f"# Roadmap: {profile['career']}", "", f"Level: {profile['education']}",
             f"Interest: {INTERESTS[profile['interest']]['label']}", ""]
    for i, p in enumerate(phases, 1):
        lines += [f"## {i}. {p['title']} ({p['when']})", p["blurb"], ""]
        lines += [f"- [ ] {t}" for t in p["tasks"]] + [""]
    return "\n".join(lines)


# ============================================================
# 4. UI
# ============================================================
def render_hero():
    words = "".join(f'<span style="animation-delay:{i * 2}s">{w}</span>' for i, w in enumerate(HERO_WORDS))
    st.markdown(clean(f"""
        <div class="hero">
            <div class="brand">🧭 Skill<b>Graph</b></div>
            <h1>Don't guess your career.</h1>
            <div class="rotator-line"><span>Become a</span><div class="rotator">{words}</div></div>
            <p class="sub">Answer four quick questions and get a step-by-step plan for what to learn, build and do next.</p>
        </div>"""), unsafe_allow_html=True)


def render_form():
    with st.form("profile_form"):
        st.markdown(clean("""
            <p class="form-title">🎯 Create your career roadmap</p>
            <p class="form-hint">It takes under a minute. You can start over any time.</p>"""),
            unsafe_allow_html=True)

        education = st.selectbox("What are you currently studying?", list(LEVELS), index=None,
                                 placeholder="Select your level")
        interest = st.selectbox("What area interests you?", list(INTERESTS), index=None,
                                placeholder="Select an interest",
                                format_func=lambda k: f"{INTERESTS[k]['emoji']}  {INTERESTS[k]['label']}")
        strengths = st.multiselect("What are your main strengths? (optional)", list(STRENGTH_TIPS),
                                   placeholder="Pick as many as you like")
        career = st.text_input("Which career do you want to explore? (optional)",
                               placeholder="Example: AI Engineer")
        submitted = st.form_submit_button("Generate my roadmap")

    if submitted:
        if education is None or interest is None:
            st.error("Please choose your education level and an area of interest.")
            return
        st.session_state.profile = {
            "education": education, "interest": interest, "strengths": strengths,
            "career": career.strip() or INTERESTS[interest]["label"],
        }
        st.session_state.roadmap_id = st.session_state.get("roadmap_id", 0) + 1
        st.rerun()


def render_results(profile: dict):
    topic, level = INTERESTS[profile["interest"]], LEVELS[profile["education"]]
    phases = build_roadmap(profile)
    rid = st.session_state.roadmap_id

    # Checkbox keys include the roadmap id, so a new roadmap starts with a clean slate.
    keys = [[f"task_{rid}_{p}_{t}" for t in range(len(ph["tasks"]))] for p, ph in enumerate(phases)]
    total = sum(len(k) for k in keys)
    done = sum(bool(st.session_state.get(k)) for group in keys for k in group)
    pct = round(done / total * 100)

    chips = f'<span class="tag">{html.escape(profile["education"])}</span><span class="tag">{topic["emoji"]} {topic["label"]}</span>'
    chips += "".join(f'<span class="tag">{html.escape(s)}</span>' for s in profile["strengths"])
    tips = "".join(f"<li>{html.escape(STRENGTH_TIPS[s])}</li>" for s in profile["strengths"])
    tips_html = f'<ul class="tips">{tips}</ul>' if tips else ""

    st.markdown(clean(f"""
        <div class="result-head">
            <h2 class="career">{html.escape(profile["career"])}</h2>
            <p class="summary">A 12-month starting plan built for your level and your interest in {topic["label"]}.</p>
            <div>{chips}</div>
            <div class="note">{level["note"]}{tips_html}</div>
        </div>
        <div class="progress"><div class="bar" style="width:{pct}%"></div></div>
        <div class="pcount">{done} of {total} steps done ({pct}%)</div>"""), unsafe_allow_html=True)

    if done == total:
        st.success("You finished every step. Time to pick a harder goal and start a new roadmap!")

    for p, ph in enumerate(phases):
        with st.container(border=True):
            st.markdown(clean(f"""
                <div class="phase-top"><div class="badge">{p + 1}</div>
                <p class="phase-title">{ph["title"]}</p><span class="when">{ph["when"]}</span></div>
                <p class="phase-blurb">{ph["blurb"]}</p>"""), unsafe_allow_html=True)
            if ph["tags"]:
                st.markdown("".join(f'<span class="tag">{t}</span>' for t in ph["tags"]), unsafe_allow_html=True)
            for t, task in enumerate(ph["tasks"]):
                st.checkbox(task, key=keys[p][t])
            if p == 1:  # free resources fit best next to the core skills
                links = " &nbsp;|&nbsp; ".join(f"[{name}]({url})" for name, url in topic["resources"])
                st.markdown(f"**Free places to learn:** {links}")

    st.markdown(clean("""
        <div class="goal"><h4>🚀 Your long-term goal</h4>
        <p>Keep learning, pick a specialty, and refresh your skills as the industry changes.
        Come back to this plan every month and tick off what you have done.</p></div>"""), unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    col1.download_button("Download roadmap", roadmap_as_markdown(profile, phases),
                         file_name="my_roadmap.md", mime="text/markdown", use_container_width=True)
    if col2.button("Start over", use_container_width=True):
        st.session_state.profile = None
        st.rerun()


def restyle_dot_graph(dot_string: str) -> str:
    """Restyles the Graphviz DOT graph to the SkillGraph design palette."""
    if not dot_string:
        return dot_string
    styled = dot_string
    styled = styled.replace(
        'edge [color="grey", style="solid"];',
        'edge [color="#60a5fa", penwidth=1.2, style="solid"];',
    )
    styled = styled.replace(
        'node [fontname="Helvetica", shape=plain];',
        'bgcolor="transparent";\n    node [fontname="DM Sans, sans-serif", shape=plain];',
    )
    styled = styled.replace(
        'fillcolor="darkblue"',
        'fillcolor="#1e3a8a", color="#1e3a8a"',
    )
    styled = styled.replace('BGCOLOR="darkgrey"', 'BGCOLOR="#1e3a8a"')
    styled = styled.replace('BGCOLOR="#2e7d32"', 'BGCOLOR="#2563eb"')
    styled = styled.replace('BGCOLOR="#f9a825"', 'BGCOLOR="#fbbf24"')
    styled = styled.replace('<FONT COLOR="black"', '<FONT COLOR="#0f172a"')
    styled = styled.replace(
        'BGCOLOR="#c62828"><FONT COLOR="white"',
        'BGCOLOR="#ffffff"><FONT COLOR="#0f172a"',
    )
    styled = styled.replace(
        'CELLBORDER="1"',
        'CELLBORDER="1" COLOR="#e3e8f2"',
    )
    return styled


def render_resume_analyzer():
    st.session_state.setdefault("ra_results", None)
    st.session_state.setdefault("ra_extracted_text", "")

    if st.session_state.ra_results is None:
        with st.container(border=True):
            st.markdown(clean("""
                <p class="form-title">📄 Analyze Your Resume Against a Job</p>
                <p class="form-hint">Upload or paste your resume and target role to get an in-depth gap analysis, skill graph, and roadmap.</p>"""),
                unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**1️⃣ Your Resume**")
                tab_upload, tab_paste = st.tabs(["Upload file", "Paste text"])
                with tab_upload:
                    uploaded_resume = st.file_uploader(
                        "Upload resume file (.pdf, .docx, .txt)",
                        type=["pdf", "docx", "txt"],
                        key="ra_file_uploader",
                        label_visibility="collapsed",
                    )
                    if uploaded_resume:
                        extracted = extract_text(uploaded_resume)
                        if extracted:
                            st.session_state.ra_extracted_text = extracted
                            with st.expander("👀 Preview extracted text", expanded=False):
                                st.text(extracted[:500] + ("..." if len(extracted) > 500 else ""))
                        else:
                            st.warning("Couldn't read text from this file (scanned PDF?). Please paste your resume text instead.")
                with tab_paste:
                    resume_pasted = st.text_area(
                        "Resume text",
                        height=160,
                        placeholder="Paste your resume content here...",
                        key="ra_resume_pasted",
                        label_visibility="collapsed",
                    )

            with col2:
                st.markdown("**2️⃣ Job Description or Target Role**")
                job_tab, = st.tabs(["Job Requirements"])
                with job_tab:
                    job_desc = st.text_area(
                        "Job description text",
                        height=160,
                        placeholder="Paste the job posting, role description, or target requirements here...",
                        key="ra_job_desc",
                        label_visibility="collapsed",
                    )

            st.write("")
            analyze_button = st.button("🚀 Analyze Resume & Match Skills", type="primary", use_container_width=True, key="ra_analyze_btn")

            if analyze_button:
                final_resume_text = resume_pasted.strip()
                if not final_resume_text and st.session_state.ra_extracted_text:
                    final_resume_text = st.session_state.ra_extracted_text.strip()

                final_job_text = job_desc.strip()

                if not final_resume_text or not final_job_text:
                    st.warning("⚠️ Please provide both a resume (uploaded or pasted) and a job description/role.")
                    return

                with st.spinner("Analyzing your resume against the target role..."):
                    try:
                        resume_data = extract_resume_skills(final_resume_text)
                        job_data = extract_job_skills(final_job_text)
                        match_results = compare(final_resume_text, resume_data, job_data)
                        scores = score_breakdown(match_results)
                        match_results["match_percent"] = scores["match_percent"]

                        job_role = job_data.get("role", "Target Role") or "Target Role"

                        soft = job_data.get("soft_skills", [])
                        exp_req = job_data.get("experience_requirements", [])
                        other_res = assess_other_requirements(final_resume_text, soft, exp_req) if (soft or exp_req) else None

                        dot_string = build_graph(job_role, match_results)

                        missing_skills = match_results.get("missing", [])
                        partial_skills = match_results.get("partial", [])
                        roadmap = generate_roadmap(
                            missing_skills,
                            partial_skills,
                            job_role,
                            resume_data.get("projects", []),
                            final_job_text,
                            match_results.get("evidence", {}),
                            match_results.get("gaps", {}),
                        )

                        html_report = build_html_report(job_role, match_results, scores, roadmap)

                        # Generate Markdown Report
                        report_md = f"# Career Analysis: {job_role}\n\n"
                        report_md += f"**Match Score:** {scores['match_percent']}%\n\n"
                        report_md += f"### ✅ Matched Skills\n{', '.join(match_results['matched']) if match_results['matched'] else 'None'}\n\n"
                        if match_results.get("partial"):
                            report_md += f"### ⚠️ Partial Skills\n{', '.join(match_results['partial'])}\n\n"
                        report_md += f"### ❌ Missing Skills\n{', '.join(match_results['missing']) if match_results['missing'] else 'None'}\n\n"
                        report_md += "### 🚀 Your Roadmap\n"
                        if not missing_skills and not partial_skills:
                            report_md += "You already have all required skills!\n"
                        else:
                            for step in roadmap.get("steps", []):
                                report_md += f"\n#### {step.get('order', '?')}. {step.get('skill', '')} ({step.get('priority', 'Medium')} Priority)\n"
                                report_md += f"- **Why this is a gap:** {step.get('why_gap', '')}\n"
                                report_md += f"- **Learn:** {step.get('learn', '')}\n"
                                report_md += f"- **Apply:** {step.get('apply', '')}\n"
                                report_md += f"- **What proves it:** {step.get('prove', '')}\n"
                                report_md += f"- **Example resume bullet:** {step.get('example_bullet', '')}\n"
                                report_md += f"- **Estimated effort:** {step.get('suggested_effort', '')}\n"

                            for item in roadmap.get("optional", []):
                                report_md += f"- **{item.get('skill', '')}**: {item.get('reason', '')}\n"

                        st.session_state.ra_results = {
                            "job_role": job_role,
                            "match_results": match_results,
                            "scores": scores,
                            "other_res": other_res,
                            "dot_string": dot_string,
                            "roadmap": roadmap,
                            "html_report": html_report,
                            "report_md": report_md,
                        }
                        st.rerun()
                    except Exception as e:
                        st.error("Something went wrong during analysis. Please check your inputs and try again.")
                        with st.expander("Technical details"):
                            st.exception(e)
    else:
        res = st.session_state.ra_results
        job_role = res["job_role"]
        scores = res["scores"]
        match_results = res["match_results"]
        pct = scores["match_percent"]

        chips = f'<span class="tag">🎯 {html.escape(job_role)}</span>'
        chips += f'<span class="tag">⚡ {scores["total_required"]} Required Skills</span>'
        st.markdown(clean(f"""
            <div class="result-head">
                <h2 class="career">{html.escape(job_role)}</h2>
                <p class="summary">Resume match analysis & personalized skill gap breakdown.</p>
                <div>{chips}</div>
            </div>
            <div class="progress"><div class="bar" style="width:{pct}%"></div></div>
            <div class="pcount">{pct}% Match Score ({scores["matched_count"]} matched, {scores["partial_count"]} partial, {scores["missing_count"]} missing)</div>"""),
            unsafe_allow_html=True)

        with st.container(border=True):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Required skills", scores["total_required"])
            m2.metric("Matched", scores["matched_count"])
            m3.metric("Partial", scores["partial_count"])
            m4.metric("Missing", scores["missing_count"])
            if not scores.get("consistent", True):
                st.warning("⚠️ Warning: Score calculations had slight inconsistencies due to alternative skills.")

        with st.container(border=True):
            st.markdown("#### 📋 Skills Breakdown")
            if match_results.get("matched"):
                tags_html = "".join(f'<span class="tag" style="background:#dcfce7; color:#15803d;">✓ {html.escape(s)}</span>' for s in match_results["matched"])
                st.markdown(f"**Matched Skills:**<br>{tags_html}", unsafe_allow_html=True)
            else:
                st.info("No direct skill matches found.")

            st.write("")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("**Partial Matches (needs strengthening):**")
                if match_results.get("partial"):
                    p_html = "".join(f'<span class="tag" style="background:#fef3c7; color:#b45309;">~ {html.escape(s)}</span>' for s in match_results["partial"])
                    st.markdown(p_html, unsafe_allow_html=True)
                else:
                    st.caption("None")
            with col_g2:
                st.markdown("**Missing Required Skills:**")
                if match_results.get("missing"):
                    m_html = "".join(f'<span class="tag" style="background:#fee2e2; color:#b91c1c;">✗ {html.escape(s)}</span>' for s in match_results["missing"])
                    st.markdown(m_html, unsafe_allow_html=True)
                else:
                    st.caption("None")

            if match_results.get("bonus_matched") or match_results.get("bonus_missing"):
                with st.expander("Preferred / Nice-to-have Skills (not counted in score)"):
                    if match_results.get("bonus_matched"):
                        st.markdown(f"**Bonus Matched:** {', '.join(match_results['bonus_matched'])}")
                    if match_results.get("bonus_missing"):
                        st.markdown(f"**Bonus Missing:** {', '.join(match_results['bonus_missing'])}")

        verified_skills = set(match_results.get("evidence", {}).keys()) | set(match_results.get("reasons", {}).keys())
        if verified_skills:
            with st.expander("🔍 Why we classified skills this way (AI Evidence & Gaps)"):
                matched_list = [s for s in sorted(verified_skills) if s in match_results.get("matched", [])]
                partial_list = [s for s in sorted(verified_skills) if s in match_results.get("partial", [])]
                missing_list = [s for s in sorted(verified_skills) if s not in match_results.get("matched", []) and s not in match_results.get("partial", [])]

                if matched_list:
                    st.markdown("**🟢 Matched Skills Evidence**")
                    for skill in matched_list:
                        ev = match_results.get("evidence", {}).get(skill, "")
                        reason = match_results.get("reasons", {}).get(skill, "")
                        parts = [p for p in [f'Evidence: "{ev}"' if ev else "", f'Reason: {reason}' if reason else ""] if p]
                        st.write(f"- **{skill}**: {' | '.join(parts) or 'Direct match found in resume.'}")

                if partial_list:
                    st.markdown("**🟡 Partial Skills Context**")
                    for skill in partial_list:
                        ev = match_results.get("evidence", {}).get(skill, "")
                        reason = match_results.get("reasons", {}).get(skill, "")
                        gap = match_results.get("gaps", {}).get(skill, "")
                        parts = [p for p in [f'Evidence: "{ev}"' if ev else "", f'Why partial: {reason}' if reason else "", f"What's missing: {gap}" if gap else ""] if p]
                        st.write(f"- **{skill}**: {' | '.join(parts) or 'Partially demonstrated.'}")

                if missing_list:
                    st.markdown("**🔴 Missing Skills Gaps**")
                    for skill in missing_list:
                        reason = match_results.get("reasons", {}).get(skill, "")
                        gap = match_results.get("gaps", {}).get(skill, "")
                        parts = [p for p in [f'Reason: {reason}' if reason else "", f"Gap: {gap}" if gap else ""] if p]
                        st.write(f"- **{skill}**: {' | '.join(parts) or 'Not demonstrated in resume.'}")

        other_res = res.get("other_res")
        if other_res and other_res.get("results"):
            with st.container(border=True):
                st.markdown("#### 📌 Other Requirements (Soft Skills & Experience)")
                for item_res in other_res["results"]:
                    it = item_res.get("item", "")
                    st_stat = item_res.get("status", "")
                    ev = item_res.get("evidence", "")
                    if st_stat == "supported":
                        st.markdown(f"- **{it}**: :green[Supported] — *{ev}*")
                    else:
                        st.markdown(f"- **{it}**: :gray[Not shown]")

        with st.container(border=True):
            st.markdown("#### 📊 Skills Breakdown")
            chart_df = pd.DataFrame([
                {"Status": "Matched", "Count": scores["matched_count"]},
                {"Status": "Partial", "Count": scores["partial_count"]},
                {"Status": "Missing", "Count": scores["missing_count"]},
            ])
            dist_chart = (
                alt.Chart(chart_df)
                .mark_bar(cornerRadius=6, height=26)
                .encode(
                    y=alt.Y(
                        "Status:N",
                        sort=None,
                        title=None,
                        axis=alt.Axis(
                            labelColor="#0f172a",
                            labelFontSize=13,
                            labelFont="DM Sans, sans-serif",
                            domainColor="#e3e8f2",
                            tickColor="#e3e8f2",
                        ),
                    ),
                    x=alt.X(
                        "Count:Q",
                        title="Number of Skills",
                        axis=alt.Axis(
                            grid=True,
                            gridColor="#e3e8f2",
                            domainColor="#e3e8f2",
                            tickColor="#e3e8f2",
                            labelColor="#0f172a",
                            titleColor="#0f172a",
                            labelFont="DM Sans, sans-serif",
                            titleFont="DM Sans, sans-serif",
                            tickMinStep=1,
                        ),
                    ),
                    color=alt.Color(
                        "Status:N",
                        scale=alt.Scale(
                            domain=["Matched", "Partial", "Missing"],
                            range=["#2563eb", "#fbbf24", "#60a5fa"],
                        ),
                        legend=None,
                    ),
                    tooltip=[
                        alt.Tooltip("Status:N", title="Status"),
                        alt.Tooltip("Count:Q", title="Skills Count"),
                    ],
                )
                .properties(height=140)
                .configure_view(strokeWidth=0)
                .configure(background="transparent")
            )
            st.altair_chart(dist_chart, use_container_width=True)

        with st.container(border=True):
            st.markdown("#### 🕸️ Skill Graph")
            dot_string = res["dot_string"]
            styled_dot = restyle_dot_graph(dot_string)
            if hasattr(st, "dialog"):
                @st.dialog("Full Screen Skill Graph", width="large")
                def show_full_graph():
                    st.graphviz_chart(styled_dot, use_container_width=True)

                if st.button("🔍 View Full Screen Graph", key="ra_full_graph_btn"):
                    show_full_graph()
            st.graphviz_chart(styled_dot, use_container_width=True)
            st.caption("🔵 Blue ✓ = Matched | 🟡 Amber ~ = Partial | ⚪ White/Bordered ✗ = Missing")

        with st.container(border=True):
            st.markdown("#### 🚀 Your Actionable Roadmap")
            missing_skills = match_results.get("missing", [])
            partial_skills = match_results.get("partial", [])
            roadmap = res["roadmap"]

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

                for pri_label, pri_key in [("🔥 High Priority", "High"), ("⚡ Medium Priority", "Medium"), ("🌱 Lower Priority", "Low")]:
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
                                if step.get("why_gap"):
                                    st.markdown(f"**Why this is a gap:** {step.get('why_gap')}")
                                if step.get("learn"):
                                    st.markdown(f"**Learn:** {step.get('learn')}")
                                if step.get("apply"):
                                    st.markdown(f"**Apply:** {step.get('apply')}")
                                if step.get("prove"):
                                    st.markdown(f"**Prove it:** {step.get('prove')}")
                                if step.get("example_bullet"):
                                    st.markdown(f"**Example resume bullet (write after completing):** `{step.get('example_bullet')}`")

                optional_items = roadmap.get("optional", [])
                if optional_items:
                    st.markdown("---")
                    st.markdown("**Extra suggestions (beyond direct job requirements):**")
                    for item in optional_items:
                        st.markdown(f"- **{item.get('skill', '')}**: {item.get('reason', '')}")

                st.caption("After you finish a step, add the project / bullet to your resume and rerun the analysis to close the gap.")

        st.write("")
        col_d1, col_d2 = st.columns(2)
        safe_name = job_role.lower().replace(" ", "_")
        col_d1.download_button(
            "Download report (HTML)",
            data=res["html_report"],
            file_name=f"{safe_name}_skillgraph_report.html",
            mime="text/html",
            use_container_width=True,
            key="ra_dl_html",
        )
        col_d2.download_button(
            "Download report (Markdown)",
            data=res["report_md"],
            file_name=f"{safe_name}_analysis.md",
            mime="text/markdown",
            use_container_width=True,
            key="ra_dl_md",
        )

        if st.button("🔄 Analyze another resume or job", use_container_width=True, key="ra_start_over"):
            st.session_state.ra_results = None
            st.session_state.ra_extracted_text = ""
            st.rerun()


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.session_state.setdefault("profile", None)
    render_hero()
    tab1, tab2 = st.tabs(["Career Roadmap", "Resume Analyzer"])
    with tab1:
        if st.session_state.profile is None:
            render_form()
        else:
            render_results(st.session_state.profile)
    with tab2:
        render_resume_analyzer()
    st.markdown('<div class="foot">SkillGraph © 2026 - Helping students find their direction.</div>',
                unsafe_allow_html=True)


main()
