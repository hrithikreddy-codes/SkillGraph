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
import inspect
import math
from pathlib import Path
import re
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st
from analyzer import (
    JobExtractionError,
    _call_llm,
    assess_other_requirements,
    build_graph,
    build_html_report,
    categorize,
    compare,
    extract_job_skills,
    extract_resume_skills,
    generate_roadmap,
    score_breakdown,
)
from file_reader import extract_text
import roadmap_ai
from report_export import roadmap_to_html, analysis_to_html
from theme import CSS, DARK_CSS

FAVICON_PATH = str(Path(__file__).parent / "favicon.svg")
LOGO_SVG = (
    '<svg viewBox="0 0 32 32" width="28" height="28" style="vertical-align: middle; display: inline-block;">'
    '<rect width="32" height="32" rx="8" fill="#1e3a8a"/>'
    '<path d="M7 23 L14 12 L21 18 L26 8" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="7" cy="23" r="2.6" fill="#fff"/>'
    '<circle cx="14" cy="12" r="2.6" fill="#fff"/>'
    '<circle cx="21" cy="18" r="2.6" fill="#fff"/>'
    '<circle cx="26" cy="8" r="3" fill="#fbbf24"/>'
    '</svg>'
)
GRAPH_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'style="vertical-align: -3px; margin-right: 7px; display: inline-block;">'
    '<circle cx="12" cy="5" r="2.5" fill="#60a5fa" stroke="#3b82f6" stroke-width="1.5"/>'
    '<circle cx="5" cy="19" r="2.5" fill="#60a5fa" stroke="#3b82f6" stroke-width="1.5"/>'
    '<circle cx="12" cy="19" r="2.5" fill="#60a5fa" stroke="#3b82f6" stroke-width="1.5"/>'
    '<circle cx="19" cy="19" r="2.5" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>'
    '<path d="M12 7.5v4" stroke="#60a5fa" stroke-width="1.8"/>'
    '<path d="M5 16.5v-2a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v2" stroke="#60a5fa" stroke-width="1.8"/>'
    '<path d="M12 11.5v5" stroke="#60a5fa" stroke-width="1.8"/>'
    '</svg>'
)
SUN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="theme-toggle-svg sg-sun">'
    '<circle cx="12" cy="12" r="4"/>'
    '<path d="M12 2v2"/><path d="M12 20v2"/>'
    '<path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
    '<path d="M2 12h2"/><path d="M20 12h2"/>'
    '<path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>'
    '</svg>'
)
MOON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="theme-toggle-svg sg-moon">'
    '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'
    '</svg>'
)
NODES_SVG = (
    '<svg class="hero-nodes" viewBox="0 0 1000 450" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
    '<g stroke="#ffffff" stroke-width="1" fill="#ffffff">'
    '<line x1="50" y1="80" x2="80" y2="240"/>'
    '<line x1="80" y1="240" x2="60" y2="380"/>'
    '<line x1="50" y1="80" x2="190" y2="140"/>'
    '<line x1="80" y1="240" x2="190" y2="140"/>'
    '<line x1="80" y1="240" x2="220" y2="310"/>'
    '<line x1="60" y1="380" x2="220" y2="310"/>'
    '<line x1="190" y1="140" x2="280" y2="70"/>'
    '<line x1="190" y1="140" x2="380" y2="180"/>'
    '<line x1="220" y1="310" x2="380" y2="180"/>'
    '<line x1="220" y1="310" x2="420" y2="360"/>'
    '<line x1="280" y1="70" x2="500" y2="90"/>'
    '<line x1="380" y1="180" x2="500" y2="90"/>'
    '<line x1="380" y1="180" x2="540" y2="270"/>'
    '<line x1="420" y1="360" x2="540" y2="270"/>'
    '<line x1="420" y1="360" x2="680" y2="380"/>'
    '<line x1="500" y1="90" x2="640" y2="160"/>'
    '<line x1="500" y1="90" x2="720" y2="80"/>'
    '<line x1="540" y1="270" x2="640" y2="160"/>'
    '<line x1="540" y1="270" x2="680" y2="380"/>'
    '<line x1="640" y1="160" x2="720" y2="80"/>'
    '<line x1="640" y1="160" x2="820" y2="220"/>'
    '<line x1="680" y1="380" x2="860" y2="350"/>'
    '<line x1="720" y1="80" x2="920" y2="110"/>'
    '<line x1="820" y1="220" x2="860" y2="350"/>'
    '<line x1="820" y1="220" x2="920" y2="110"/>'
    '<line x1="820" y1="220" x2="950" y2="270"/>'
    '<line x1="860" y1="350" x2="950" y2="270"/>'
    '<line x1="920" y1="110" x2="950" y2="270"/>'
    '<circle cx="50" cy="80" r="3"/>'
    '<circle cx="80" cy="240" r="3"/>'
    '<circle cx="60" cy="380" r="3"/>'
    '<circle cx="190" cy="140" r="3.5"/>'
    '<circle cx="220" cy="310" r="3"/>'
    '<circle cx="280" cy="70" r="3"/>'
    '<circle cx="380" cy="180" r="3.5"/>'
    '<circle cx="420" cy="360" r="3"/>'
    '<circle cx="500" cy="90" r="3.5"/>'
    '<circle cx="540" cy="270" r="3"/>'
    '<circle cx="640" cy="160" r="3.5"/>'
    '<circle cx="680" cy="380" r="3"/>'
    '<circle cx="720" cy="80" r="3"/>'
    '<circle cx="820" cy="220" r="3.5"/>'
    '<circle cx="860" cy="350" r="3"/>'
    '<circle cx="920" cy="110" r="3"/>'
    '<circle cx="950" cy="270" r="3"/>'
    '</g>'
    '</svg>'
)

# ============================================================
# INTEREST SVG ICONS & KEYWORD MATCHING
# ============================================================
INTEREST_SVGS: dict[str, str] = {
    # software/web/programming (code brackets)
    "software": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M5 4.5L1.5 8l3.5 3.5M11 4.5L14.5 8 11 11.5M9.5 3l-3 10"/>'
        '</svg>'
    ),
    # data/analytics (bar chart)
    "data": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M2 13.5h12M4.5 13.5V9M8 13.5V6M11.5 13.5V2.5"/>'
        '</svg>'
    ),
    # AI/machine learning (brain or chip)
    "ai": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<rect x="4.5" y="4.5" width="7" height="7" rx="1.5"/>'
        '<path d="M6 1.5v3M10 1.5v3M6 11.5v3M10 11.5v3M1.5 6h3M1.5 10h3M11.5 6h3M11.5 10h3M7 7h2v2H7z"/>'
        '</svg>'
    ),
    # design/UI/UX (pen tool)
    "design": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M12 8.5l-1-4.5L2 2l2 9 4.5 1 3.5-3.5zM2 2l5 5M9.5 9.5l4.5 4.5"/>'
        '</svg>'
    ),
    # cybersecurity (shield)
    "cyber": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M8 1.5l5.5 2.2v4c0 3.6-2.5 6.3-5.5 7.3-3-1-5.5-3.7-5.5-7.3v-4L8 1.5zM8 5.5v5"/>'
        '</svg>'
    ),
    # cloud/DevOps (cloud)
    "cloud": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M4.5 13h7a3 3 0 0 0 1.2-5.7A4 4 0 0 0 5.2 5.5 3.2 3.2 0 0 0 4.5 13z"/>'
        '</svg>'
    ),
    # mobile (phone)
    "mobile": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<rect x="4" y="1.5" width="8" height="13" rx="2"/>'
        '<path d="M7 11.5h2M7 3.5h2"/>'
        '</svg>'
    ),
    # games (controller)
    "games": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M4 4.5h8a3 3 0 0 1 3 3v2.5a2 2 0 0 1-3.5 1.4L10 10H6l-1.5 1.4A2 2 0 0 1 1 10V7.5a3 3 0 0 1 3-3zM4 7.5h2.5M5.25 6.25v2.5M10.75 7.5h.01M12.5 8.5h.01"/>'
        '</svg>'
    ),
    # robotics/electronics/embedded (gear)
    "robotics": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<circle cx="8" cy="8" r="2.6"/>'
        '<path d="M8 1.5v2.2M8 12.3v2.2M1.5 8h2.2M12.3 8h2.2M3.4 3.4l1.6 1.6M11 11l1.6 1.6M3.4 12.6l1.6-1.6M11 5l1.6-1.6"/>'
        '</svg>'
    ),
    # business/finance/marketing (briefcase)
    "business": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<rect x="2" y="5" width="12" height="9" rx="1.5"/>'
        '<path d="M5.5 5V3.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1V5M2 8.5h12M7 8.5v2h2v-2"/>'
        '</svg>'
    ),
    # healthcare/medicine (heart-pulse or cross)
    "healthcare": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M1.5 8.5h2.5l1.5-4 2.5 7.5 2-5 1.5 1.5h3"/>'
        '</svg>'
    ),
    # education/teaching (book)
    "education": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M2 3.5a2 2 0 0 1 2-2h3.5v11H4a2 2 0 0 0-2 2V3.5zM14 3.5a2 2 0 0 0-2-2H8.5v11H12a2 2 0 0 1 2 2V3.5z"/>'
        '</svg>'
    ),
    # neutral fallback (a small node-graph icon in the style of the SkillGraph logo)
    "fallback": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="15" height="15" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="sg-interest-icon">'
        '<path d="M3 11.5L6.5 6l3.5 3 3-5.5"/>'
        '<circle cx="3" cy="11.5" r="1.4" fill="currentColor"/>'
        '<circle cx="6.5" cy="6" r="1.4" fill="currentColor"/>'
        '<circle cx="10" cy="9" r="1.4" fill="currentColor"/>'
        '<circle cx="13" cy="3.5" r="1.4" fill="currentColor"/>'
        '</svg>'
    ),
}

INTEREST_KEYWORD_GROUPS: list[tuple[str, list[str], Optional[re.Pattern]]] = [
    # 1. AI / Machine Learning (brain or chip)
    (
        "ai",
        [
            "machine learning", "deep learning", "artificial intelligence", "neural",
            "nlp", "natural language", "computer vision", "generative ai", "genai",
            "reinforcement learning", "data science with ai", "llm", "large language model"
        ],
        re.compile(r"\b(ai|ml|llm)\b", re.IGNORECASE),
    ),
    # 2. Cybersecurity (shield)
    (
        "cyber",
        [
            "cyber", "security", "infosec", "pentest", "pen test", "penetration",
            "ethical hack", "soc", "cryptograph", "crypto", "forensic",
            "vulnerability", "network security", "threat"
        ],
        None,
    ),
    # 3. Cloud / DevOps (cloud)
    (
        "cloud",
        [
            "cloud", "devops", "sre", "infrastructure", "kubernetes", "k8s",
            "docker", "aws", "azure", "gcp", "terraform", "ci/cd", "cicd",
            "sysadmin", "site reliability"
        ],
        None,
    ),
    # 4. Games (controller)
    (
        "games",
        [
            "game", "gaming", "gamedev", "unity", "unreal", "godot", "gameplay"
        ],
        None,
    ),
    # 5. Mobile (phone)
    (
        "mobile",
        [
            "mobile", "ios", "android", "flutter", "react native", "swift",
            "kotlin", "mobile app"
        ],
        None,
    ),
    # 6. Robotics / Electronics / Embedded (gear)
    (
        "robotics",
        [
            "robot", "embedded", "hardware", "electronic", "circuit", "arduino",
            "raspberry", "mechatronic", "microcontroller", "iot", "firmware"
        ],
        None,
    ),
    # 7. Healthcare / Medicine (heart-pulse or cross)
    (
        "healthcare",
        [
            "health", "medic", "clinical", "hospital", "pharma", "biotech",
            "biomed", "nurs", "doctor", "patient", "therap", "dental"
        ],
        None,
    ),
    # 8. Education / Teaching (book)
    (
        "education",
        [
            "educat", "teach", "tutor", "instruct", "academic", "school",
            "pedagog", "professor", "curriculum", "training"
        ],
        None,
    ),
    # 9. Design / UI / UX (pen tool)
    (
        "design",
        [
            "design", "ui/ux", "figma", "wireframe", "user experience",
            "user interface", "graphic", "creative", "prototyp", "typography"
        ],
        re.compile(r"\b(ui|ux)\b", re.IGNORECASE),
    ),
    # 10. Data / Analytics (bar chart)
    (
        "data",
        [
            "data", "analy", "business intelligence", "statistics", "statistic",
            "visualization", "tableau", "power bi", "big data", "databricks"
        ],
        re.compile(r"\bbi\b", re.IGNORECASE),
    ),
    # 11. Business / Finance / Marketing (briefcase)
    (
        "business",
        [
            "business", "entrepreneur", "startup", "finance", "financial",
            "market", "marketing", "sales", "accounting", "venture",
            "founder", "product manage", "product manager", "consult",
            "management", "commerce", "fintech", "strategy", "human resources"
        ],
        re.compile(r"\bhr\b", re.IGNORECASE),
    ),
    # 12. Software / Web / Programming (code brackets)
    (
        "software",
        [
            "software", "web", "program", "code", "coding", "developer",
            "development", "frontend", "front-end", "backend", "back-end",
            "fullstack", "full-stack", "full stack", "api", "dev", "engineer"
        ],
        None,
    ),
]


def get_interest_icon_svg(target) -> str:
    """Map user interest to a matching 16x16 line SVG icon with stroke="currentColor".
    Checks specific categories first, falling back to a neutral node-graph icon.
    """
    if isinstance(target, dict):
        raw_interest = target.get("interest", "")
        if raw_interest == "other":
            search_text = target.get("other_interest", "").strip() or target.get("career", "").strip() or ""
        else:
            topic_info = INTERESTS.get(raw_interest, {})
            label = topic_info.get("label", "")
            search_text = f"{raw_interest} {label}"
    else:
        search_text = str(target or "")

    cleaned = search_text.lower().strip()
    if cleaned:
        for cat, kws, regex in INTEREST_KEYWORD_GROUPS:
            for kw in kws:
                if kw in cleaned:
                    return INTEREST_SVGS[cat]
            if regex and regex.search(cleaned):
                return INTEREST_SVGS[cat]

    return INTEREST_SVGS["fallback"]


st.set_page_config(page_title="SkillGraph - Your Career Roadmap", page_icon=FAVICON_PATH, layout="centered")


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

PRESET_STRENGTHS = [
    "Problem Solving",
    "Creativity",
    "Communication",
    "Mathematics",
    "Teamwork",
    "Leadership",
    "Curiosity",
    "Writing",
    "Attention to detail",
    "Public speaking",
    "Patience",
    "Time management",
]

INTERESTS = {
    "software": {
        "label": "Software Development", "emoji": "💻",
        "tiers": {
            "starter": {
                "foundation": [
                    "Explore coding basics with Python: variables, loops, conditionals, and functions",
                    "Create your first web page using free tools: HTML & CSS on CodePen or Replit",
                    "Learn how software works by building simple interactive text games",
                ],
                "core": [
                    "Practice basic programming logic: lists, dictionaries, and simple problem-solving",
                    "Build a simple interactive browser app or visual game using free online editors",
                    "Create a free GitHub account and learn how to save and share your code",
                ],
                "projects": [
                    "Beginner: interactive quiz or text-adventure game in Python",
                    "Intermediate: personal hobby, profile, or club webpage styled with HTML & CSS",
                    "Creative: mini calculator or budget tracker app built with free tools",
                ],
                "tools": ["Python", "HTML/CSS", "Replit", "VS Code", "GitHub"],
            },
            "builder": {
                "foundation": [
                    "Master Python or JavaScript fundamentals: data types, functions, modules, and error handling",
                    "Understand how the web works: HTML5, responsive CSS, and HTTP client-server communication",
                    "Set up Git, GitHub, and a modern local development environment in VS Code",
                ],
                "core": [
                    "Build backend services and REST APIs with Node.js, Express, Flask, or FastAPI",
                    "Learn relational databases: SQL schema design, CRUD queries, and joins",
                    "Connect frontend user interfaces to backend REST APIs with database persistence",
                ],
                "projects": [
                    "Beginner: responsive personal portfolio website hosted on GitHub Pages",
                    "Intermediate: task manager or note-taking web app with user login and a database",
                    "Advanced: full-stack CRUD application deployed on a free cloud platform",
                ],
                "tools": ["Python", "JavaScript", "Git", "SQL", "VS Code", "REST APIs"],
            },
            "job_ready": {
                "foundation": [
                    "Master programming concepts in Python, TypeScript, or Java: OOP, async programming, and clean code",
                    "Configure professional development workflows: Git branching, Linux CLI, and VS Code debugging",
                    "Understand web architecture: RESTful standards, async I/O, authentication, and API security",
                ],
                "core": [
                    "Master Data Structures & Algorithms: arrays, trees, graphs, sorting, and Big-O complexity",
                    "Build scalable backend services or microservices using FastAPI, Spring Boot, or Node.js",
                    "Design production schemas with PostgreSQL or MongoDB, indexing, and transactions",
                ],
                "projects": [
                    "Full-Stack: web application with JWT authentication, relational database, and unit tests",
                    "Systems: high-performance REST API with Docker containerization and CI/CD pipelines",
                    "Capstone: internship-ready collaborative project or open-source contribution with live deployment",
                ],
                "tools": ["Python", "TypeScript", "Git", "PostgreSQL", "Docker", "REST APIs"],
            },
        },
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

HERO_WORDS = ["an AI Engineer", "a Data Scientist", "a UX Designer", "a Security Analyst", "a Software Developer", "a Founder"]


# ============================================================
# 2. STYLES - imported from theme.py
# ============================================================
# CSS and DARK_CSS are imported from theme.py


def clean(markup: str) -> str:
    """Streamlit treats indented / blank-line HTML as code. Strip it so HTML renders."""
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


def slugify_filename(text: str, fallback: str) -> str:
    """Lowercase, replace runs of non-alphanumeric chars with an underscore,
    strip leading/trailing underscores, truncate to 50 chars, and return fallback if empty.
    """
    s = str(text or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    s = s[:50].rstrip("_")
    return s if s else fallback


# ============================================================
# 3. LOGIC - turn the user's answers into a list of phases
# ============================================================
COMMON_SKILLS: list[str] = sorted(
    [
        # Programming Languages
        "Bash",
        "C",
        "C#",
        "C++",
        "Dart",
        "Go",
        "HTML/CSS",
        "Java",
        "JavaScript",
        "Kotlin",
        "PHP",
        "Python",
        "R",
        "Ruby",
        "Rust",
        "Scala",
        "Shell Scripting",
        "SQL",
        "Swift",
        "TypeScript",
        # Web & Backend Frameworks
        "Angular",
        "ASP.NET Core",
        "Django",
        "Express.js",
        "FastAPI",
        "Flask",
        "GraphQL",
        "Laravel",
        "Next.js",
        "Node.js",
        "React",
        "Redux",
        "REST APIs",
        "Ruby on Rails",
        "Spring Boot",
        "Svelte",
        "Vue.js",
        "WebSockets",
        # Styling & Design
        "Bootstrap",
        "Figma",
        "Prototyping",
        "Responsive Design",
        "Tailwind CSS",
        "UI/UX Design",
        "Wireframing",
        # Databases & Storage
        "Cassandra",
        "DynamoDB",
        "Elasticsearch",
        "Firebase",
        "Microsoft SQL Server",
        "MongoDB",
        "MySQL",
        "Neo4j",
        "Oracle Database",
        "PostgreSQL",
        "Redis",
        "SQLite",
        "Supabase",
        # Cloud, DevOps & Infrastructure
        "Ansible",
        "AWS",
        "CI/CD",
        "Cloudflare",
        "Docker",
        "Git",
        "GitHub Actions",
        "GitLab CI/CD",
        "Google Cloud Platform (GCP)",
        "Grafana",
        "Helm",
        "Kubernetes",
        "Linux",
        "Microsoft Azure",
        "Nginx",
        "Prometheus",
        "Serverless",
        "Terraform",
        # Data & Machine Learning
        "Apache Airflow",
        "Apache Kafka",
        "Apache Spark",
        "Computer Vision",
        "Deep Learning",
        "Hugging Face",
        "Keras",
        "LangChain",
        "LLMs",
        "Machine Learning",
        "Matplotlib",
        "Natural Language Processing (NLP)",
        "NumPy",
        "OpenCV",
        "Pandas",
        "Power BI",
        "PyTorch",
        "Scikit-learn",
        "Seaborn",
        "Snowflake",
        "Tableau",
        "TensorFlow",
        # Testing & Tools
        "Cypress",
        "Jest",
        "JUnit",
        "Mocha",
        "Playwright",
        "Postman",
        "Pytest",
        "Selenium",
        "Unit Testing",
        # Methodologies, Architecture & Soft Skills
        "Agile",
        "Code Review",
        "Communication",
        "Critical Thinking",
        "Debugging",
        "Leadership",
        "Microservices",
        "Problem Solving",
        "Project Management",
        "Scrum",
        "System Design",
        "Teamwork",
        "Time Management",
    ]
)


def render_skills_input(
    label: str,
    key: str,
    placeholder: str = "Pick from the list or type a skill and press Enter...",
    options: list[str] | None = None,
) -> list[str]:
    supports_new = "accept_new_options" in inspect.signature(st.multiselect).parameters
    opts = options if options is not None else COMMON_SKILLS
    if supports_new:
        return st.multiselect(
            label,
            options=opts,
            default=[],
            accept_new_options=True,
            key=key,
            placeholder=placeholder,
        )
    else:
        raw = st.text_input(
            f"{label} (comma-separated)",
            key=key,
            placeholder="e.g. Python, SQL, React",
        )
        if raw:
            seen = set()
            skills = []
            for item in raw.split(","):
                s = item.strip()
                if s and s.lower() not in seen:
                    seen.add(s.lower())
                    skills.append(s)
            return skills
        return []


def get_education_tier(education: str) -> str:
    if education in ("School", "Intermediate / 12th"):
        return "starter"
    elif education == "B.Tech / Engineering":
        return "job_ready"
    return "builder"


def task_mentions_skill(task: str, user_skills: list[str]) -> bool:
    if not user_skills:
        return False
    import re
    for skill in user_skills:
        s = skill.strip()
        if not s:
            continue
        if re.match(r'^[A-Za-z0-9_]+$', s):
            if re.search(r'\b' + re.escape(s) + r'\b', task, flags=re.IGNORECASE):
                return True
        else:
            if s.lower() in task.lower():
                return True
    return False


def filter_tasks_by_skills(tasks: list[str], user_skills: list[str]) -> list[str]:
    return [t for t in tasks if not task_mentions_skill(t, user_skills)]


def build_roadmap(profile: dict) -> list[dict]:
    level = LEVELS[profile["education"]]
    if profile.get("interest") == "other":
        field = profile.get("other_interest", "").strip() or profile.get("career", "").strip() or "your chosen field"
        user_skills = profile.get("skills", [])
        tags = user_skills if user_skills else ["Fundamentals", "Core Tools", "Best Practices"]
        phases = [
            {"title": "Build your foundation", "when": "Weeks 1-6",
             "blurb": f"Get comfortable with core principles and fundamental tools for {field}.",
             "tasks": [
                 f"Master the core terminology, principles, and foundational concepts of {field}",
                 f"Set up your development and practical working environment for {field}",
                 f"Complete a structured introductory curriculum or authoritative tutorials in {field}",
             ],
             "tags": tags},
            {"title": "Learn the core skills", "when": "Months 2-4",
             "blurb": f"These are the essential competencies professionals in {field} use daily.",
             "tasks": [
                 f"Study industry-standard workflows and intermediate methodologies in {field}",
                 f"Deep-dive into the primary frameworks, platforms, and toolkits used in {field}",
                 f"Analyze real-world case studies and production examples in {field}",
             ],
             "tags": []},
            {"title": "Build real projects", "when": "Months 4-6",
             "blurb": "Projects prove what you can do. Put every project in your portfolio or repository.",
             "tasks": [
                 f"Beginner: Build a starter project solving a specific problem in {field}",
                 f"Intermediate: Build a functional, full-featured project applying standards in {field}",
                 f"Advanced: Ship an end-to-end, polished project demonstrating competence in {field}",
             ],
             "tags": []},
            {"title": "Gain experience", "when": "Months 6-9",
             "blurb": "Work with other people and real deadlines.",
             "tasks": level["experience"] + [f"Enter a competition, hackathon, or collaborative project in {field}"],
             "tags": []},
            {"title": "Prepare for your career", "when": "Months 9-12",
             "blurb": f"Turn your skills into something a recruiter or team in {field} can see.",
             "tasks": level["prep"] + [f"Practice technical and scenario-based interview questions for {field} every week"],
             "tags": []},
        ]
    else:
        topic = INTERESTS[profile["interest"]]
        if profile.get("interest") == "software" and "tiers" in topic:
            tier = get_education_tier(profile.get("education", ""))
            tier_data = topic["tiers"].get(tier, topic["tiers"]["builder"])
            user_skills = profile.get("skills", [])

            foundation_tasks = filter_tasks_by_skills(tier_data["foundation"], user_skills)
            core_tasks = filter_tasks_by_skills(tier_data["core"], user_skills)
            projects_tasks = filter_tasks_by_skills(tier_data["projects"], user_skills)
            tools = tier_data.get("tools", topic["tools"])
            exp_tasks = filter_tasks_by_skills(level["experience"] + ["Enter one hackathon or online competition"], user_skills)
            prep_tasks = filter_tasks_by_skills(level["prep"] + [f"Practice {topic['interview']} questions every week"], user_skills)

            phases = [
                {"title": "Build your foundation", "when": "Weeks 1-6",
                 "blurb": "Get comfortable with the basics before anything advanced.",
                 "tasks": foundation_tasks, "tags": tools},
                {"title": "Learn the core skills", "when": "Months 2-4",
                 "blurb": "These are the skills people in this field use every day.",
                 "tasks": core_tasks, "tags": []},
                {"title": "Build real projects", "when": "Months 4-6",
                 "blurb": "Projects prove what you can do. Put every one on GitHub or in a portfolio.",
                 "tasks": projects_tasks, "tags": []},
                {"title": "Gain experience", "when": "Months 6-9",
                 "blurb": "Work with other people and real deadlines.",
                 "tasks": exp_tasks, "tags": []},
                {"title": "Prepare for your career", "when": "Months 9-12",
                 "blurb": "Turn your skills into something a recruiter or college can see.",
                 "tasks": prep_tasks, "tags": []},
            ]
        else:
            phases = [
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

    for ph in phases:
        ph["groups"] = [{"name": "", "tasks": list(ph.get("tasks", []))}]
    return phases


def roadmap_as_markdown(profile: dict, phases: list[dict]) -> str:
    """Plain-text version of the roadmap for the download button."""
    interest_label = (
        profile.get("other_interest") or "Other"
        if profile.get("interest") == "other"
        else INTERESTS[profile["interest"]]["label"]
    )
    lines = [f"# Roadmap: {profile['career']}", "", f"Level: {profile['education']}",
             f"Interest: {interest_label}", ""]
    if profile.get("skills"):
        lines += [f"Existing Skills: {', '.join(profile['skills'])}", ""]
    for i, p in enumerate(phases, 1):
        lines += [f"## {i}. {p['title']} ({p['when']})", p["blurb"], ""]
        lines += [f"- [ ] {t}" for t in p["tasks"]] + [""]
    return "\n".join(lines)


# ============================================================
# 4. UI
# ============================================================
def render_hero(slim: bool | None = None):
    if slim is None:
        slim = bool(st.session_state.get("profile") or st.session_state.get("ra_results"))

    if slim:
        st.markdown(clean(f"""
            <div class="hero hero-slim">
                {NODES_SVG}
                <div class="hero-content">
                    <div class="brand">{LOGO_SVG}<span class="wordmark">Skill<b>Graph</b></span></div>
                    <div class="tagline">Don't guess your career.</div>
                </div>
            </div>"""), unsafe_allow_html=True)
        return

    words = "".join(f'<span style="animation-delay:{i * 2}s">{w}</span>' for i, w in enumerate(HERO_WORDS))
    st.markdown(clean(f"""
        <div class="hero">
            {NODES_SVG}
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <div class="brand">{LOGO_SVG}<span class="wordmark">Skill<b>Graph</b></span></div>
                <h1>Don't guess your career.</h1>
                <div class="become">Become</div>
                <div class="rotator">{words}</div>
                <p class="sub">Get a step-by-step plan for your career, then check your resume against any job.</p>
            </div>
        </div>"""), unsafe_allow_html=True)


def render_form():
    with st.container(border=True, key="sg_card_roadmap_form"):
        st.markdown(clean("""
            <p class="form-title">🎯 Create your career roadmap</p>
            <p class="form-hint">It takes under a minute. You can start over any time.</p>"""),
            unsafe_allow_html=True)

        education = st.selectbox(
            "What are you currently studying?",
            list(LEVELS),
            index=None,
            placeholder="Select your level",
            key="rf_education",
        )

        interest_options = list(INTERESTS) + ["other"]
        interest = st.selectbox(
            "What area interests you?",
            interest_options,
            index=None,
            placeholder="Select an interest",
            format_func=lambda k: "✨  Other" if k == "other" else f"{INTERESTS[k]['emoji']}  {INTERESTS[k]['label']}",
            key="rf_interest",
        )

        other_field = ""
        if interest == "other":
            other_field = st.text_input(
                "Specify your field of interest",
                placeholder="Example: Game Development, Robotics, Cloud Architecture...",
                key="rf_other_field",
            )

        raw_skills = st.text_input(
            "Skills you already have (optional)",
            placeholder="Python, Excel, Figma (separate with commas)",
            key="rf_skills",
        )
        skills = []
        if raw_skills:
            seen_skills = set()
            for item in raw_skills.split(","):
                s = item.strip()
                if s and s.lower() not in seen_skills:
                    seen_skills.add(s.lower())
                    skills.append(s)

        strengths = st.multiselect(
            "What are your main strengths? (optional)",
            PRESET_STRENGTHS,
            placeholder="Pick as many as you like",
            accept_new_options=True,
            key="rf_strengths",
        )
        career = st.text_input(
            "Which career do you want to explore? (optional)",
            placeholder="Example: AI Engineer",
            key="rf_career",
        )
        hours = st.slider(
            "Hours per week you can study",
            min_value=2,
            max_value=40,
            value=8,
            step=1,
            help="Be realistic. We size your plan to this.",
            key="rf_hours",
        )
        submitted = st.button("Generate my roadmap", type="primary", width="stretch", key="rf_submit")

    if submitted:
        if education is None or interest is None:
            st.error("Please choose your education level and an area of interest.")
            return
        if interest == "other" and not other_field.strip():
            st.error("Please specify your field of interest.")
            return

        chosen_label = other_field.strip() if interest == "other" else INTERESTS[interest]["label"]
        career_val = career.strip() or chosen_label
        profile_data = {
            "education": education,
            "interest": interest,
            "other_interest": other_field.strip() if interest == "other" else "",
            "skills": skills,
            "strengths": strengths,
            "career": career_val,
            "hours": hours,
        }

        roadmap_loading_ph = st.empty()
        ai_phases = None
        fail_reason = None
        try:
            with roadmap_loading_ph.container():
                with st.spinner("Building your roadmap..."):
                    import roadmap_ai
                    ai_phases, fail_reason = roadmap_ai.generate_roadmap(
                        education=education,
                        interest_label=chosen_label,
                        career=career_val,
                        skills=skills,
                        strengths=strengths,
                        hours_per_week=hours,
                    )
        finally:
            roadmap_loading_ph.empty()

        if ai_phases:
            phases = ai_phases
            st.session_state.roadmap_is_ai = True
            st.session_state.roadmap_fail_reason = None
        else:
            phases = build_roadmap(profile_data)
            st.session_state.roadmap_is_ai = False
            st.session_state.roadmap_fail_reason = fail_reason

        st.session_state.profile = profile_data
        st.session_state.roadmap_phases = phases
        st.session_state.roadmap_id = st.session_state.get("roadmap_id", 0) + 1
        st.rerun()


def render_results(profile: dict):
    level = LEVELS[profile["education"]]
    if profile.get("interest") == "other":
        topic_label = profile.get("other_interest", "").strip() or profile.get("career", "").strip() or "Other"
        topic_resources = []
    else:
        topic_data = INTERESTS[profile["interest"]]
        topic_label = topic_data["label"]
        topic_resources = topic_data.get("resources", [])

    interest_icon = get_interest_icon_svg(profile)

    phases = st.session_state.get("roadmap_phases")
    if not phases:
        phases = build_roadmap(profile)
        st.session_state.roadmap_phases = phases
    rid = st.session_state.roadmap_id

    # Checkbox keys include the roadmap id, so a new roadmap starts with a clean slate.
    keys = [
        [
            [f"task_{rid}_{p}_{g}_{t}" for t in range(len(grp.get("tasks", [])))]
            for g, grp in enumerate(ph.get("groups") or [{"name": "", "tasks": ph.get("tasks", [])}])
        ]
        for p, ph in enumerate(phases)
    ]
    total = sum(len(grp_keys) for phase_keys in keys for grp_keys in phase_keys)
    done = sum(bool(st.session_state.get(k)) for phase_keys in keys for grp_keys in phase_keys for k in grp_keys)
    pct = round(done / total * 100) if total > 0 else 0

    chips = f'<span class="tag">{html.escape(profile["education"])}</span><span class="tag sg-chip-interest">{interest_icon}{html.escape(topic_label)}</span>'
    chips += "".join(f'<span class="tag">{html.escape(s)}</span>' for s in profile.get("strengths", []))
    user_skills = profile.get("skills", [])
    if user_skills:
        chips += "".join(f'<span class="tag sg-chip-skill">⚡ {html.escape(s)}</span>' for s in user_skills)
    tips_items = []
    for s in profile.get("strengths", []):
        if s in STRENGTH_TIPS:
            tip_text = STRENGTH_TIPS[s]
        else:
            ci_match = next((v for k, v in STRENGTH_TIPS.items() if k.lower() == s.lower()), None)
            tip_text = ci_match if ci_match else f"Use your {s} to stand out: show it in a project or a story on your resume."
        tips_items.append(f"<li>{html.escape(tip_text)}</li>")
    tips = "".join(tips_items)
    tips_html = f'<ul class="tips">{tips}</ul>' if tips else ""

    hours = profile.get("hours", 8)
    is_ai = st.session_state.get("roadmap_is_ai", False)
    total_months = None
    if is_ai and phases:
        for ph in phases:
            if isinstance(ph, dict) and ph.get("total_months"):
                total_months = ph["total_months"]
                break

    if is_ai and total_months:
        summary_line = f"A {total_months}-month starting plan built for your level and your interest in {html.escape(topic_label)}, about {hours} hours a week."
        note_content = f'{level["note"]}{tips_html}'
    else:
        summary_line = f"A 12-month starting plan built for your level and your interest in {html.escape(topic_label)}."
        note_content = f'Note: about {hours} hours a week.<br>{level["note"]}{tips_html}'

    st.markdown(clean(f"""
        <div class="result-head">
            <h2 class="career">{html.escape(profile["career"])}</h2>
            <p class="summary">{summary_line}</p>
            <div>{chips}</div>
            <div class="note">{note_content}</div>
        </div>
        <div class="progress"><div class="bar" style="width:{pct}%"></div></div>
        <div class="pcount">{done} of {total} steps done ({pct}%)</div>"""), unsafe_allow_html=True)
    if st.session_state.get("roadmap_is_ai"):
        st.caption("Personalized with AI")
    else:
        reason = st.session_state.get("roadmap_fail_reason")
        if reason:
            display_reason = reason.replace("_", " ") if not str(reason).startswith("validation:") else reason
            st.caption(f"Template roadmap (AI unavailable: {display_reason})")
        else:
            st.caption("Template roadmap (AI unavailable)")

    if done == total:
        st.success("You finished every step. Time to pick a harder goal and start a new roadmap!")

    for p, ph in enumerate(phases):
        with st.container(border=True, key=f"sg_card_phase_{p}"):
            when_label = f"{ph['when']} &bull; up to {ph['hours']} hours" if ph.get("hours") else ph["when"]
            goal_val = str(ph.get("goal") or "").strip()
            goal_html = f'<p class="phase-goal" style="font-size: 14px; color: var(--text); margin: 0 0 10px; line-height: 1.5;"><strong>Goal:</strong> {html.escape(goal_val)}</p>' if goal_val else ""
            st.markdown(clean(f"""
                <div class="phase-top"><div class="badge">{p + 1}</div>
                <p class="phase-title">{ph["title"]}</p><span class="when">{when_label}</span></div>
                <p class="phase-blurb">{ph["blurb"]}</p>
                {goal_html}"""), unsafe_allow_html=True)
            if ph["tags"]:
                st.markdown("".join(f'<span class="tag">{t}</span>' for t in ph["tags"]), unsafe_allow_html=True)
            groups = ph.get("groups") or [{"name": "", "tasks": ph.get("tasks", [])}]
            for g, grp in enumerate(groups):
                grp_name = grp.get("name", "").strip()
                if grp_name:
                    st.markdown(f"**{grp_name}**")
                for t, task in enumerate(grp.get("tasks", [])):
                    st.checkbox(task, key=keys[p][g][t])
            ph_resources = ph.get("resources")
            if isinstance(ph_resources, list):
                res_names = [str(r).strip() for r in ph_resources if str(r).strip()]
            elif isinstance(ph_resources, str) and ph_resources.strip():
                res_names = [str(r).strip() for r in ph_resources.split(",") if str(r).strip()]
            else:
                res_names = []

            if res_names:
                st.markdown(f"**Free places to learn:** {', '.join(res_names)}")
            elif p == 1 and topic_resources:
                links = " &nbsp;|&nbsp; ".join(f"[{name}]({url})" for name, url in topic_resources)
                st.markdown(f"**Free places to learn:** {links}")

    st.markdown(clean("""
        <div class="goal"><h4>🚀 Your long-term goal</h4>
        <p>Keep learning, pick a specialty, and refresh your skills as the industry changes.
        Come back to this plan every month and tick off what you have done.</p></div>"""), unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    checked_state = {
        (p, g, t): bool(st.session_state.get(keys[p][g][t]))
        for p, ph in enumerate(phases)
        for g, grp in enumerate(ph.get("groups") or [{"name": "", "tasks": ph.get("tasks", [])}])
        for t in range(len(grp.get("tasks", [])))
    }
    for p_keys in keys:
        for g_keys in p_keys:
            for k in g_keys:
                checked_state[k] = bool(st.session_state.get(k))
    roadmap_html = roadmap_to_html(profile, phases, checked_state=checked_state)
    career_title = profile.get("career", "")
    col1.download_button(
        "Download roadmap (HTML)",
        roadmap_html,
        file_name=f"{slugify_filename(career_title, 'career')}_roadmap.html",
        mime="text/html",
        width="stretch",
    )
    if col2.button("Start over", width="stretch"):
        st.session_state.profile = None
        st.session_state.roadmap_phases = None
        st.session_state.roadmap_is_ai = False
        st.session_state.roadmap_fail_reason = None
        st.rerun()


def build_skill_tree_html(job_role: str, match_results: dict, is_fullscreen: bool = False) -> str:
    """Builds an HTML/CSS tree for the skill breakdown grouped by category."""
    matched_skills = match_results.get("matched", []) or []
    partial_skills = match_results.get("partial", []) or []
    missing_skills = match_results.get("missing", []) or []

    categories: dict[str, list[dict]] = {}

    def add_skills(skill_list, status, symbol, css_cls):
        for s in skill_list:
            if not s:
                continue
            cat = categorize(s)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "name": str(s),
                "status": status,
                "symbol": symbol,
                "cls": css_cls,
            })

    add_skills(matched_skills, "matched", "✓", "sg-node-matched")
    add_skills(partial_skills, "partial", "~", "sg-node-partial")
    add_skills(missing_skills, "missing", "✗", "sg-node-missing")

    safe_role = html.escape(str(job_role) if job_role else "Target Role")
    fs_class = " sg-tree-fullscreen" if is_fullscreen else ""

    if not categories:
        return clean(f"""
            <div class="sg-tree-wrapper{fs_class}">
                <div class="sg-tree-root-container">
                    <div class="sg-tree-root-pill">{safe_role}</div>
                </div>
                <p style="text-align: center; color: var(--muted); margin: 16px 0;">No required skills found.</p>
            </div>
        """)

    preferred_order = [
        "Languages",
        "Frontend",
        "Backend",
        "Database",
        "DevOps & Cloud",
        "Testing",
        "AI / ML",
        "Tools & Process",
        "Other",
    ]

    sorted_cats = sorted(
        categories.keys(),
        key=lambda c: (preferred_order.index(c) if c in preferred_order else 999, c),
    )

    max_per_row = 4
    n = len(sorted_cats)
    if n > 0:
        num_rows = math.ceil(n / max_per_row)
        per_row = math.ceil(n / num_rows)
        category_rows = [
            sorted_cats[i : i + per_row]
            for i in range(0, n, per_row)
        ]
    else:
        num_rows = 0
        category_rows = []

    # Metrics in em matching CSS variables in theme.py
    card_width_em = 13.5
    col_pad_em = 0.35
    row_gap_em = 1.0
    root_height_em = 2.4
    stem_height_em = 0.8
    stub_height_em = 0.8
    header_height_em = 2.0
    skill_row_height_em = 1.62
    skill_gap_em = 0.25
    body_pad_em = 0.85

    if is_fullscreen and category_rows:
        max_cards = max((len(r) for r in category_rows), default=1)
        w_em = round(max_cards * (card_width_em + 2 * col_pad_em), 2)
        w_em = max(w_em, 18.0)

        row_heights = []
        for r in category_rows:
            tallest = max((len(categories[cat]) for cat in r), default=0)
            skills_h = (tallest * skill_row_height_em + (tallest - 1) * skill_gap_em) if tallest > 0 else 0
            row_heights.append(stub_height_em + header_height_em + body_pad_em + skills_h)

        gaps_h = (len(category_rows) - 1) * row_gap_em if len(category_rows) > 1 else 0
        h_em = round(root_height_em + stem_height_em + sum(row_heights) + gaps_h, 2)
        inner_style = f' style="--sg-w: {w_em}; --sg-h: {h_em}; font-size: clamp(8px, min(100cqw / {w_em}, 100cqh / {h_em}), 28px);"'
    else:
        inner_style = ""

    rows_html = []
    for row_cats in category_rows:
        cards_html = []
        for cat in row_cats:
            cat_skills = categories[cat]
            safe_cat = html.escape(cat)
            skill_rows = []
            for sk in cat_skills:
                safe_name = html.escape(sk["name"])
                symbol = sk["symbol"]
                cls = sk["cls"]
                skill_rows.append(
                    f'<div class="sg-tree-node {cls}" title="{safe_name}">'
                    f'{symbol} {safe_name}'
                    f'</div>'
                )
            rows_str = "".join(skill_rows)
            cards_html.append(
                f'<div class="sg-tree-card-col">'
                f'  <div class="sg-tree-card">'
                f'    <div class="sg-tree-card-header">{safe_cat}</div>'
                f'    <div class="sg-tree-card-body">{rows_str}</div>'
                f'  </div>'
                f'</div>'
            )
        row_content = "".join(cards_html)
        rows_html.append(f'<div class="sg-tree-row">{row_content}</div>')

    rows_str = "".join(rows_html)

    legend_html = (
        '<div class="sg-tree-legend">'
        '  <span class="sg-tree-node sg-node-matched">Matched ✓</span>'
        '  <span class="sg-tree-node sg-node-partial">Partial ~</span>'
        '  <span class="sg-tree-node sg-node-missing">Missing ✗</span>'
        '</div>'
    )

    return clean(f"""
        <div class="sg-tree-wrapper{fs_class}">
            <div class="sg-tree-graph-area">
                <div class="sg-tree-graph-inner"{inner_style}>
                    <div class="sg-tree-root-container">
                        <div class="sg-tree-root-pill">{safe_role}</div>
                        <div class="sg-tree-root-stem"></div>
                    </div>
                    <div class="sg-tree-rows">
                        {rows_str}
                    </div>
                </div>
            </div>
            {legend_html}
        </div>
    """)


def restyle_dot_graph(dot_string: str, is_dark: bool = False) -> str:
    """Restyles the Graphviz DOT graph to the SkillGraph design palette based on theme."""
    if not dot_string:
        return dot_string
    styled = dot_string

    text_color = "#e5ecf8" if is_dark else "#0f172a"
    grid_color = "#24304d" if is_dark else "#e3e8f2"
    edge_color = "#60a5fa"
    root_fill = "#16213a" if is_dark else "#1e3a8a"
    root_border = "#3b82f6" if is_dark else "#1e3a8a"
    root_font = "#e5ecf8" if is_dark else "white"
    cat_bg = "#16213a" if is_dark else "#1e3a8a"
    cat_font = "#e5ecf8" if is_dark else "white"
    missing_bg = "#111a2e" if is_dark else "#ffffff"
    missing_font = text_color

    # Ensure bgcolor is transparent and font is DM Sans
    if 'bgcolor="transparent"' not in styled:
        styled = styled.replace(
            'node [fontname="Helvetica", shape=plain];',
            'bgcolor="transparent";\n    node [fontname="DM Sans, sans-serif", shape=plain];',
        )
    styled = styled.replace('fontname="Helvetica"', 'fontname="DM Sans, sans-serif"')

    # Edge styling
    styled = styled.replace(
        'edge [color="grey", style="solid"];',
        f'edge [color="{edge_color}", penwidth=1.2, style="solid"];',
    )
    styled = styled.replace(
        'edge [color="#60a5fa", penwidth=1.2, style="solid"];',
        f'edge [color="{edge_color}", penwidth=1.2, style="solid"];',
    )

    # Root node fill & font
    styled = styled.replace('fillcolor="darkblue", fontcolor="white"', f'fillcolor="{root_fill}", color="{root_border}", fontcolor="{root_font}"')
    styled = styled.replace('fillcolor="darkblue"', f'fillcolor="{root_fill}", color="{root_border}", fontcolor="{root_font}"')
    styled = styled.replace('fillcolor="#1e3a8a", color="#1e3a8a"', f'fillcolor="{root_fill}", color="{root_border}", fontcolor="{root_font}"')
    styled = styled.replace('fillcolor="#16213a", color="#3b82f6", fontcolor="#e5ecf8"', f'fillcolor="{root_fill}", color="{root_border}", fontcolor="{root_font}"')

    # Category header
    styled = styled.replace('BGCOLOR="darkgrey"><B><FONT COLOR="white"', f'BGCOLOR="{cat_bg}"><B><FONT COLOR="{cat_font}"')
    styled = styled.replace('BGCOLOR="darkgrey"', f'BGCOLOR="{cat_bg}"')
    styled = styled.replace('BGCOLOR="#1e3a8a"><B><FONT COLOR="white"', f'BGCOLOR="{cat_bg}"><B><FONT COLOR="{cat_font}"')
    styled = styled.replace('BGCOLOR="#16213a"><B><FONT COLOR="#e5ecf8"', f'BGCOLOR="{cat_bg}"><B><FONT COLOR="{cat_font}"')

    # Matched skills (blue)
    styled = styled.replace('BGCOLOR="#2e7d32"', 'BGCOLOR="#2563eb"')

    # Partial skills (amber)
    styled = styled.replace('BGCOLOR="#f9a825"', 'BGCOLOR="#fbbf24"')
    styled = styled.replace('<FONT COLOR="black"', '<FONT COLOR="#0f172a"')

    # Missing skills (surface + contrast text)
    styled = styled.replace(
        'BGCOLOR="#c62828"><FONT COLOR="white"',
        f'BGCOLOR="{missing_bg}"><FONT COLOR="{missing_font}"',
    )
    styled = styled.replace(
        'BGCOLOR="#ffffff"><FONT COLOR="#0f172a"',
        f'BGCOLOR="{missing_bg}"><FONT COLOR="{missing_font}"',
    )
    styled = styled.replace(
        'BGCOLOR="#111a2e"><FONT COLOR="#e5ecf8"',
        f'BGCOLOR="{missing_bg}"><FONT COLOR="{missing_font}"',
    )

    # Table cell borders / grid lines
    if f'COLOR="{grid_color}"' not in styled:
        if 'COLOR="#e3e8f2"' in styled:
            styled = styled.replace('COLOR="#e3e8f2"', f'COLOR="{grid_color}"')
        elif 'COLOR="#24304d"' in styled:
            styled = styled.replace('COLOR="#24304d"', f'COLOR="{grid_color}"')
        else:
            styled = styled.replace('CELLBORDER="1"', f'CELLBORDER="1" COLOR="{grid_color}"')

    return styled


def render_resume_analyzer(is_dark: bool = False):
    if not is_dark and (st.session_state.get("theme") == "dark" or st.session_state.get("theme_toggle")):
        is_dark = True
    st.session_state.setdefault("ra_results", None)
    st.session_state.setdefault("ra_extracted_text", "")

    has_valid_results = (
        st.session_state.ra_results is not None
        and isinstance(st.session_state.ra_results, dict)
        and st.session_state.ra_results.get("scores", {}).get("total_required", 0) > 0
    )

    if not has_valid_results:
        with st.container(border=True, key="sg_card_analyzer_input"):
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
                st.markdown(
                    '<p style="color: var(--muted) !important; font-size: 13px; margin: 6px 0 0; line-height: 1.4;">'
                    '🔒 Your resume is sent to an AI service (Groq) for analysis. SkillGraph doesn\'t save it to disk, and it\'s cleared when your session ends.'
                    '</p>',
                    unsafe_allow_html=True,
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
            extra_skills = render_skills_input(
                "Extra skills you have (optional)",
                key="ra_extra_skills",
                placeholder="Pick from the list or type a skill and press Enter...",
            )

            st.write("")
            analyze_button = st.button("🚀 Analyze Resume & Match Skills", type="primary", width="stretch", key="ra_analyze_btn")

            if analyze_button:
                final_resume_text = resume_pasted.strip()
                if not final_resume_text:
                    if uploaded_resume:
                        final_resume_text = extract_text(uploaded_resume).strip()
                    elif st.session_state.ra_extracted_text:
                        final_resume_text = st.session_state.ra_extracted_text.strip()

                final_job_text = job_desc.strip()

                if not final_resume_text or not final_job_text:
                    st.warning("⚠️ Please provide both a resume (uploaded or pasted) and a job description/role.")
                    return

                if extra_skills:
                    final_resume_text += "\n\nAdditional Skills: " + ", ".join(extra_skills)

                loading_placeholder = st.empty()
                error_msg = None
                should_stop = False
                try:
                    with loading_placeholder.container():
                        with st.spinner(
                            "Analyzing your resume against the target role...\n\n"
                            "This usually takes under a minute, but can take up to two or a little longer if the AI service is busy. Please keep this tab open."
                        ):
                            resume_data = extract_resume_skills(final_resume_text)
                            if extra_skills:
                                curr_skills = resume_data.get("skills", [])
                                seen_skills = {s.lower() for s in curr_skills}
                                for es in extra_skills:
                                    if es and es.lower() not in seen_skills:
                                        curr_skills.append(es)
                                        seen_skills.add(es.lower())
                                resume_data["skills"] = curr_skills

                            try:
                                job_data = extract_job_skills(final_job_text)
                            except JobExtractionError as e:
                                error_msg = str(e)
                                should_stop = True
                            else:
                                if not job_data.get("required_skills"):
                                    error_msg = (
                                        "Could not extract any required skills from the job description or role. "
                                        "Please provide a more detailed job posting or role description."
                                    )
                                    should_stop = True
                                else:
                                    match_results = compare(final_resume_text, resume_data, job_data)
                                    scores = score_breakdown(match_results)
                                    if scores.get("total_required", 0) <= 0:
                                        error_msg = (
                                            "Analysis found 0 required skills for this role. "
                                            "Please provide a more detailed job description."
                                        )
                                        should_stop = True
                                    else:
                                        match_results["match_percent"] = scores["match_percent"]

                                        job_role = job_data.get("role", "Target Role") or "Target Role"

                                        soft = job_data.get("soft_skills", [])
                                        exp_req = job_data.get("experience_requirements", [])
                                        other_res = assess_other_requirements(final_resume_text, soft, exp_req) if (soft or exp_req) else None

                                        dot_string = build_graph(job_role, match_results, is_dark=is_dark)

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

                                        html_report = analysis_to_html({
                                            "job_role": job_role,
                                            "match_results": match_results,
                                            "scores": scores,
                                            "other_res": other_res,
                                            "roadmap": roadmap,
                                            "report_md": report_md,
                                        })

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
                    error_msg = str(e)
                finally:
                    loading_placeholder.empty()

                if error_msg:
                    st.session_state.ra_results = None
                    st.error(error_msg)
                    if should_stop:
                        st.stop()
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

        with st.container(border=True, key="sg_card_metrics"):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Required skills", scores["total_required"])
            m2.metric("Matched", scores["matched_count"])
            m3.metric("Partial", scores["partial_count"])
            m4.metric("Missing", scores["missing_count"])
            if not scores.get("consistent", True):
                st.warning("⚠️ Warning: Score calculations had slight inconsistencies due to alternative skills.")

        with st.container(border=True, key="sg_card_skills"):
            st.markdown("#### 📋 Skills Breakdown")
            if match_results.get("matched"):
                tags_html = "".join(f'<span class="tag sg-chip-matched">✓ {html.escape(s)}</span>' for s in match_results["matched"])
                st.markdown(f"**Matched Skills:**<br>{tags_html}", unsafe_allow_html=True)
            else:
                st.info("No direct skill matches found.")

            st.write("")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("**Partial Matches (needs strengthening):**")
                if match_results.get("partial"):
                    p_html = "".join(f'<span class="tag sg-chip-partial">~ {html.escape(s)}</span>' for s in match_results["partial"])
                    st.markdown(p_html, unsafe_allow_html=True)
                else:
                    st.caption("None")
            with col_g2:
                st.markdown("**Missing Required Skills:**")
                if match_results.get("missing"):
                    m_html = "".join(f'<span class="tag sg-chip-missing">✗ {html.escape(s)}</span>' for s in match_results["missing"])
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
            with st.container(border=True, key="sg_card_other_reqs"):
                st.markdown("#### 📌 Other Requirements (Soft Skills & Experience)")
                for item_res in other_res["results"]:
                    it = item_res.get("item", "")
                    st_stat = item_res.get("status", "")
                    ev = item_res.get("evidence", "")
                    if st_stat == "supported":
                        st.markdown(f"- **{it}**: :green[Supported] — *{ev}*")
                    else:
                        st.markdown(f"- **{it}**: :gray[Not shown]")

        with st.container(border=True, key="sg_card_match_overview"):
            bar_icon = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
                'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" '
                'style="vertical-align: -2px; margin-right: 6px; display: inline-block;">'
                '<line x1="3" y1="6" x2="21" y2="6"/>'
                '<line x1="3" y1="12" x2="15" y2="12"/>'
                '<line x1="3" y1="18" x2="9" y2="18"/>'
                '</svg>'
            )
            st.markdown(f"#### {bar_icon}Match Overview", unsafe_allow_html=True)
            matched_count = int(scores.get("matched_count", 0))
            partial_count = int(scores.get("partial_count", 0))
            missing_count = int(scores.get("missing_count", 0))
            max_c = max(matched_count, partial_count, missing_count, 1)

            if max_c <= 10:
                step = 1
            elif max_c <= 20:
                step = 2
            elif max_c <= 50:
                step = 5
            else:
                step = max(1, round(max_c / 10))
            ticks = list(range(0, max_c + 1, step))
            if ticks[-1] != max_c:
                ticks.append(max_c)

            gridlines_html = "".join(
                f'<div class="sg-chart-gridline" style="left: {(t / max_c) * 100:.2f}%;"></div>'
                for t in ticks
            )

            row_items = [
                ("Matched", matched_count, "#22c55e"),
                ("Partial", partial_count, "#f59e0b"),
                ("Missing", missing_count, "#ef4444"),
            ]
            rows_html = "".join(
                f'''<div class="sg-chart-bar-row">
                  <div class="sg-chart-bar" style="width: {(cnt / max_c) * 100:.2f}%; background-color: {clr};"></div>
                  <span class="sg-chart-count" style="left: calc({(cnt / max_c) * 100:.2f}% + 8px);">{cnt}</span>
                </div>'''
                for lbl, cnt, clr in row_items
            )

            ticks_html = "".join(
                f'''<div class="sg-chart-tick-wrap" style="left: {(t / max_c) * 100:.2f}%;">
                  <div class="sg-chart-tick-mark"></div>
                  <span class="sg-chart-tick-label">{t}</span>
                </div>'''
                for t in ticks
            )

            overview_chart_html = f"""
            <style>
              :root {{
                --sg-chart-text: #334155;
                --sg-chart-grid: rgba(100, 116, 139, 0.25);
              }}
              :root[data-sg-theme="dark"] {{
                --sg-chart-text: #e5ecf8;
                --sg-chart-grid: rgba(148, 163, 184, 0.25);
              }}
              .sg-chart-wrap {{
                font-family: 'DM Sans', Arial, sans-serif;
                padding: 10px 0 4px;
                user-select: none;
              }}
              .sg-chart-body {{
                display: flex;
                align-items: stretch;
                gap: 12px;
              }}
              .sg-chart-labels {{
                width: 65px;
                flex-shrink: 0;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                gap: 14px;
              }}
              .sg-chart-label {{
                height: 22px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                font-size: 13px;
                font-weight: 600;
                color: var(--sg-chart-text, #334155);
                line-height: 1;
              }}
              .sg-chart-track-area {{
                flex: 1;
                position: relative;
                margin-right: 36px;
              }}
              .sg-chart-grid-layer {{
                position: absolute;
                inset: 0;
                pointer-events: none;
              }}
              .sg-chart-gridline {{
                position: absolute;
                top: 0;
                bottom: 0;
                width: 1px;
                background-color: var(--sg-chart-grid, rgba(100, 116, 139, 0.25));
              }}
              .sg-chart-bars-layer {{
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                gap: 14px;
              }}
              .sg-chart-bar-row {{
                height: 22px;
                position: relative;
                display: flex;
                align-items: center;
              }}
              .sg-chart-bar {{
                height: 22px;
                border-radius: 6px;
                transition: width 0.3s ease;
              }}
              .sg-chart-count {{
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                font-size: 13px;
                font-weight: 600;
                color: var(--sg-chart-text, #334155);
                line-height: 1;
                white-space: nowrap;
              }}
              .sg-chart-axis-row {{
                display: flex;
                gap: 12px;
                margin-top: 6px;
              }}
              .sg-chart-axis-spacer {{
                width: 65px;
                flex-shrink: 0;
              }}
              .sg-chart-axis-track {{
                flex: 1;
                position: relative;
                margin-right: 36px;
                height: 22px;
                border-top: 1px solid var(--sg-chart-grid, rgba(100, 116, 139, 0.25));
              }}
              .sg-chart-tick-wrap {{
                position: absolute;
                top: 0;
                transform: translateX(-50%);
                display: flex;
                flex-direction: column;
                align-items: center;
              }}
              .sg-chart-tick-mark {{
                width: 1px;
                height: 4px;
                background-color: var(--sg-chart-grid, rgba(100, 116, 139, 0.25));
              }}
              .sg-chart-tick-label {{
                font-size: 12px;
                font-weight: 500;
                color: var(--sg-chart-text, #334155);
                margin-top: 2px;
                line-height: 1;
              }}
              .sg-chart-title-row {{
                display: flex;
                gap: 12px;
                margin-top: 4px;
              }}
              .sg-chart-title {{
                flex: 1;
                margin-right: 36px;
                text-align: center;
                font-size: 12px;
                font-weight: 500;
                color: var(--sg-chart-text, #334155);
              }}
            </style>
            <div class="sg-chart-wrap">
              <div class="sg-chart-body">
                <div class="sg-chart-labels">
                  <div class="sg-chart-label">Matched</div>
                  <div class="sg-chart-label">Partial</div>
                  <div class="sg-chart-label">Missing</div>
                </div>
                <div class="sg-chart-track-area">
                  <div class="sg-chart-grid-layer">
                    {gridlines_html}
                  </div>
                  <div class="sg-chart-bars-layer">
                    {rows_html}
                  </div>
                </div>
              </div>
              <div class="sg-chart-axis-row">
                <div class="sg-chart-axis-spacer"></div>
                <div class="sg-chart-axis-track">
                  {ticks_html}
                </div>
              </div>
              <div class="sg-chart-title-row">
                <div class="sg-chart-axis-spacer"></div>
                <div class="sg-chart-title">Number of skills</div>
              </div>
            </div>
            """
            st.markdown(overview_chart_html, unsafe_allow_html=True)

        with st.container(border=True, key="sg_card_skill_graph"):
            st.markdown(f"#### {GRAPH_ICON_SVG}Skill Graph", unsafe_allow_html=True)
            if hasattr(st, "dialog"):
                @st.dialog("Full Screen Skill Graph", width="large")
                def show_full_graph():
                    st.markdown(build_skill_tree_html(job_role, match_results, is_fullscreen=True), unsafe_allow_html=True)

                if st.button("🔍 View Full Screen Graph", key="ra_full_graph_btn"):
                    show_full_graph()
            st.markdown(build_skill_tree_html(job_role, match_results, is_fullscreen=False), unsafe_allow_html=True)

        with st.container(border=True, key="sg_card_roadmap"):
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
        html_report_data = res.get("html_report") or analysis_to_html(res)
        col_d1.download_button(
            "Download report (HTML)",
            data=html_report_data,
            file_name=f"{slugify_filename(job_role, 'role')}_report.html",
            mime="text/html",
            width="stretch",
            key="ra_dl_html",
        )
        if col_d2.button("🔄 Analyze another resume or job", width="stretch", key="ra_start_over"):
            st.session_state.ra_results = None
            st.session_state.ra_extracted_text = ""
            st.rerun()


def main():
    initial_theme = "dark" if st.query_params.get("theme") == "dark" else "light"
    is_dark = (initial_theme == "dark")
    st.session_state["theme"] = initial_theme

    btn_help = "Switch to light mode" if is_dark else "Switch to dark mode"
    toggle_html = f"""
    <style>
      #sg-theme-toggle {{
        position: fixed;
        top: 14px;
        right: 18px;
        z-index: 1000;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--surface);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        margin: 0;
        cursor: pointer !important;
        transition: all 0.2s ease;
        color: var(--text);
        box-sizing: border-box;
      }}
      #sg-theme-toggle * {{
        cursor: pointer !important;
      }}
      #sg-theme-toggle:hover {{
        background: var(--surface-2);
        border-color: var(--blue);
        transform: translateY(-1px);
      }}
      #sg-theme-toggle .theme-toggle-svg {{
        width: 20px;
        height: 20px;
        stroke: currentColor;
        pointer-events: none;
      }}
      :root[data-sg-theme="dark"] .sg-moon {{ display: none !important; }}
      :root:not([data-sg-theme="dark"]) .sg-sun {{ display: none !important; }}
    </style>
    <button id="sg-theme-toggle" type="button" aria-label="Toggle theme" title="{btn_help}">
      {SUN_SVG}
      {MOON_SVG}
    </button>
    """
    st.markdown(toggle_html, unsafe_allow_html=True)

    st.markdown(CSS, unsafe_allow_html=True)
    if is_dark:
        st.markdown(DARK_CSS, unsafe_allow_html=True)

    st.components.v1.html(
        f"""
        <style>
          html, body {{
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
          }}
        </style>
        <script>
          try {{
            var pWin = window.parent;
            var pDoc = pWin && pWin.document;
            if (!pDoc || !pDoc.documentElement) {{
              console.warn("sg-theme: parent not accessible");
            }} else {{
              // 1. On load: pick theme from ?theme= if present, else localStorage, else prefers-color-scheme
              var theme = null;
              try {{
                var urlParams = new URLSearchParams(pWin.location.search);
                var qTheme = urlParams.get("theme");
                if (qTheme === "dark" || qTheme === "light") {{
                  theme = qTheme;
                }}
              }} catch (e) {{}}

              if (!theme) {{
                try {{
                  if (pWin.localStorage) {{
                    var stored = pWin.localStorage.getItem("sg-theme");
                    if (stored === "dark" || stored === "light") {{
                      theme = stored;
                    }}
                  }}
                }} catch (e) {{}}
              }}

              if (!theme) {{
                try {{
                  if (pWin.matchMedia && pWin.matchMedia("(prefers-color-scheme: dark)").matches) {{
                    theme = "dark";
                  }} else {{
                    theme = "light";
                  }}
                }} catch (e) {{
                  theme = "light";
                }}
              }}

              // Set attribute as early as the script allows
              pDoc.documentElement.dataset.sgTheme = theme;

              // Update initial toggle title if toggle exists in DOM
              var initialToggle = pDoc.getElementById("sg-theme-toggle");
              if (initialToggle) {{
                initialToggle.setAttribute("title", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
              }}

              // 2. Bind ONE click listener on window.parent.document that delegates to #sg-theme-toggle
              if (!pWin.__sgThemeToggleBound) {{
                pWin.__sgThemeToggleBound = true;
                pDoc.addEventListener("click", function(e) {{
                  try {{
                    var btn = e.target && e.target.closest && e.target.closest("#sg-theme-toggle");
                    if (!btn) return;
                    e.preventDefault();
                    e.stopPropagation();

                    var current = pDoc.documentElement.dataset.sgTheme === "dark" ? "dark" : "light";
                    var next = current === "dark" ? "light" : "dark";

                    // Flip document.documentElement.dataset.sgTheme
                    pDoc.documentElement.dataset.sgTheme = next;

                    // Save to window.parent.localStorage under "sg-theme"
                    try {{
                      if (pWin.localStorage) {{
                        pWin.localStorage.setItem("sg-theme", next);
                      }}
                    }} catch (err) {{}}

                    // Update ?theme= value in URL with history.replaceState (no navigation)
                    try {{
                      var url = new URL(pWin.location.href);
                      url.searchParams.set("theme", next);
                      pWin.history.replaceState(null, "", url.toString());
                    }} catch (err) {{}}

                    // Update toggle's title tooltip
                    var nextTitle = next === "dark" ? "Switch to light mode" : "Switch to dark mode";
                    btn.setAttribute("title", nextTitle);
                  }} catch (clickErr) {{
                    console.warn("sg-theme: click error", clickErr);
                  }}
                }}, true);
              }}

              // 3. Bind drag-and-drop highlight listeners on window.parent.document
              if (!pWin.__sgDragoverBound) {{
                pWin.__sgDragoverBound = true;
                try {{
                  pDoc.addEventListener("dragenter", function(e) {{
                    try {{
                      var dz = e.target && e.target.closest && e.target.closest('[data-testid="stFileUploaderDropzone"]');
                      if (dz) {{
                        dz.classList.add("sg-dragover");
                      }}
                    }} catch (err) {{}}
                  }}, true);

                  pDoc.addEventListener("dragover", function(e) {{
                    try {{
                      var dz = e.target && e.target.closest && e.target.closest('[data-testid="stFileUploaderDropzone"]');
                      if (dz) {{
                        dz.classList.add("sg-dragover");
                      }}
                    }} catch (err) {{}}
                  }}, true);

                  pDoc.addEventListener("dragleave", function(e) {{
                    try {{
                      var dz = e.target && e.target.closest && e.target.closest('[data-testid="stFileUploaderDropzone"]');
                      if (dz) {{
                        if (!e.relatedTarget || !dz.contains(e.relatedTarget)) {{
                          dz.classList.remove("sg-dragover");
                        }}
                      }}
                    }} catch (err) {{}}
                  }}, true);

                  pDoc.addEventListener("drop", function(e) {{
                    try {{
                      var dz = e.target && e.target.closest && e.target.closest('[data-testid="stFileUploaderDropzone"]');
                      if (dz) {{
                        dz.classList.remove("sg-dragover");
                      }}
                      var activeList = pDoc.querySelectorAll('[data-testid="stFileUploaderDropzone"].sg-dragover');
                      for (var i = 0; i < activeList.length; i++) {{
                        activeList[i].classList.remove("sg-dragover");
                      }}
                    }} catch (err) {{}}
                  }}, true);
                }} catch (dragErr) {{
                  console.warn("sg-dragover: bind error", dragErr);
                }}
              }}

              // Hide component iframe and container
              if (window.frameElement) {{
                window.frameElement.style.display = "none";
                window.frameElement.style.height = "0";
                window.frameElement.style.margin = "0";
                window.frameElement.style.padding = "0";
                var el = window.frameElement;
                while (el && el !== pDoc.body) {{
                  if (el.getAttribute("data-testid") === "stElementContainer" || el.classList.contains("element-container")) {{
                    el.style.display = "none";
                    break;
                  }}
                  el.style.display = "none";
                  el = el.parentElement;
                }}
              }}
            }}
          }} catch (e) {{
            console.warn("sg-theme: parent not accessible");
          }}
        </script>
        """,
        height=0,
    )

    st.session_state.setdefault("profile", None)
    has_results = bool(st.session_state.get("profile") or st.session_state.get("ra_results"))
    render_hero(slim=has_results)
    tab1, tab2 = st.tabs(["Career Roadmap", "Resume Analyzer"])
    with tab1:
        if st.session_state.profile is None:
            render_form()
        else:
            render_results(st.session_state.profile)
    with tab2:
        render_resume_analyzer(is_dark=is_dark)
    st.markdown('<div class="foot">SkillGraph © 2026 - Helping students find their direction.</div>',
                unsafe_allow_html=True)

if __name__ == "__main__":
    main()
