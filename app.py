"""
PathFinder - Career Roadmap Generator (Streamlit)
Run with:  streamlit run app.py
Needs:     pip install streamlit   (version 1.32 or newer)

File layout (top to bottom):
  1. DATA      - all the career content lives in plain dictionaries (easy to edit)
  2. STYLES    - one CSS block that gives the app its look and animations
  3. LOGIC     - build_roadmap() turns the user's answers into phases
  4. UI        - render_hero(), render_form(), render_results()
"""

import html

import streamlit as st

st.set_page_config(page_title="PathFinder - Your Career Roadmap", page_icon="🧭", layout="centered")


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
            <div class="brand">🧭 Path<b>Finder</b></div>
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


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.session_state.setdefault("profile", None)
    render_hero()
    if st.session_state.profile is None:
        render_form()
    else:
        render_results(st.session_state.profile)
    st.markdown('<div class="foot">PathFinder © 2026 - Helping students find their direction.</div>',
                unsafe_allow_html=True)


main()
