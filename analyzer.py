"""
analyzer.py — AI-powered resume analysis functions (Gemini + Groq)
===================================================================
All AI logic lives here. The Streamlit UI (app.py) imports from this file.

Setup:
    Put your API keys in your .env file:
        GEMINI_API_KEYS=key1,key2
        GROQ_API_KEYS=groq_key1,groq_key2
    
    The system will try Groq first (because it is insanely fast). If Groq
    is rate-limited or unavailable, it falls back to Gemini.
"""

import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# SHARED HELPER — Load API keys & call LLMs with auto-rotation
# ---------------------------------------------------------------------------

def _get_api_keys(env_var_name):
    """Reads all API keys for a given service from the .env file."""
    raw = os.getenv(env_var_name, "")
    if raw:
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if keys:
            return keys
    # Fallback to singular just in case (e.g., GEMINI_API_KEY instead of KEYS)
    single = os.getenv(env_var_name.replace("_KEYS", "_KEY"), "")
    if single.strip():
        return [single.strip()]
    return []


# Gemini Models
_GEMINI_MODELS = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-3.8-flash"]

# Groq Models
_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "allam-2-7b",
]

def _call_groq(prompt):
    """Tries Groq models. Returns text if successful, or None if rate limited/failed."""
    keys = _get_api_keys("GROQ_API_KEYS")
    if not keys:
        return None  # No Groq keys provided, skip to Gemini
        
    for api_key in keys:
        client = Groq(api_key=api_key)
        for model_name in _GROQ_MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=2048,
                    timeout=60
                )
                return completion.choices[0].message.content
            except Exception as e:
                error_msg = str(e).lower()
                
                # If rate limited -> try next model/key
                if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                    continue
                    
                # If it's a 401 Unauthorized, the key is actually bad
                if "401" in error_msg:
                    return f"❌ Groq API error: Unauthorized (401). Please check GROQ_API_KEYS."
                    
                # For 404 (Model not found) or other errors, skip to next model
                if "404" in error_msg or "does not exist" in error_msg:
                    continue
                    
                # Return other unexpected errors so we can actually see what went wrong
                return f"❌ Groq API error: {e}"
                
    return None

def _call_gemini(prompt):
    """Tries Gemini models. Returns text if successful, or None if rate limited/failed."""
    keys = _get_api_keys("GEMINI_API_KEYS")
    if not keys:
        return None

    for api_key in keys:
        genai.configure(api_key=api_key)
        for model_name in _GEMINI_MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2048,
                        temperature=0.2,
                    ),
                )
                response = model.generate_content(
                    prompt,
                    request_options={"timeout": 60},
                )
                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                
                # If the key itself is invalid, stop and tell the user
                if "400" in error_msg or "invalid" in error_msg or "api_key_invalid" in error_msg:
                    return f"❌ Gemini API error: Invalid API Key. Please check GEMINI_API_KEYS in your .env file.\n\n(Error details: {e})"
                    
                if "429" in error_msg or "quota" in error_msg:
                    continue
                continue
                
    return None

def _call_llm(prompt):
    """
    Master function: 
    1. Tries Groq (fastest)
    2. Falls back to Gemini
    3. Returns an error message if all fail.
    """
    # 1. Try Groq
    groq_result = _call_groq(prompt)
    if groq_result:
        return groq_result
        
    # 2. Try Gemini
    gemini_result = _call_gemini(prompt)
    if gemini_result:
        return gemini_result
        
    # 3. Both failed
    return (
        "⏱️ **All API keys (Groq & Gemini) are rate-limited or missing.**\n\n"
        "Please check your `.env` file and make sure you have valid API keys for "
        "either `GROQ_API_KEYS` or `GEMINI_API_KEYS`."
    )


# ---------------------------------------------------------------------------
# FUNCTION — Normalize Skills
# ---------------------------------------------------------------------------

def normalize(skill):
    """
    Normalizes a skill name by trimming, lowercasing, and mapping common
    aliases to a standard professional name. If no alias is found, it
    returns the original string if it contains any uppercase letters,
    otherwise capitalizes the first letter of each word.
    """
    if not skill:
        return ""
        
    cleaned = skill.strip()
    key = cleaned.lower()
    
    aliases = {
        "rest api": "REST APIs",
        "rest apis": "REST APIs",
        "css": "CSS",
        "css3": "CSS",
        "html": "HTML",
        "html5": "HTML",
        "github": "GitHub",
        "github actions": "GitHub Actions",
        "mongodb": "MongoDB",
        "mongo": "MongoDB",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "express": "Express.js",
        "express.js": "Express.js",
        "expressjs": "Express.js",
        "node": "Node.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "tensorflow": "TensorFlow",
        "tf": "TensorFlow",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "aws": "AWS",
        "amazon web services": "AWS",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "docker": "Docker",
        "jest": "Jest",
        "git": "Git",
        "python": "Python",
        "python3": "Python",
        "sql": "SQL",
        "machine learning": "Machine Learning",
        "ml": "Machine Learning",
        "unit testing": "Unit Testing",
        "integration testing": "Integration Testing",
        "agile": "Agile/Scrum",
        "scrum": "Agile/Scrum",
        "agile/scrum": "Agile/Scrum",
        "state management": "State Management",
        "responsive web design": "Responsive Web Design",
        "vuejs": "Vue.js",
        "vue.js": "Vue.js",
        "gcp": "Google Cloud",
        "google cloud platform": "Google Cloud",
        "k8s": "Kubernetes",
        "c++": "C++",
        "cpp": "C++",
        "c#": "C#",
        "csharp": "C#",
        "dl": "Deep Learning",
        "cv": "Computer Vision",
        "nlp": "Natural Language Processing",
        "ai": "Artificial Intelligence"
    }
    
    if key in aliases:
        return aliases[key]
        
    has_upper = any(c.isupper() for c in cleaned)
    if has_upper:
        return cleaned
    
    return " ".join(word.capitalize() for word in cleaned.split())

# ---------------------------------------------------------------------------
# FUNCTION — Extract structured skills/data from resume text
# ---------------------------------------------------------------------------

import json
import streamlit as st

@st.cache_data
def extract_resume_skills(text):
    """
    Sends resume text to the LLM and asks for a JSON object with:
        - skills:           list of short skill names (e.g. "Python", "SQL")
        - experience_years: total years of experience (number)
        - education:        list of degrees/certifications
        - projects:         list of project names/titles

    Returns a Python dictionary parsed from the model's response.
    """
    prompt = f"""
You are a resume parser. Read the resume below and return ONLY valid JSON.
No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "skills": [],
    "experience_years": 0,
    "education": [],
    "projects": []
}}

Rules you MUST follow:
1. "skills" — short names only, like "Python", "SQL", "React", "AWS".
   Never use sentences. Never duplicate.
   - Include skills that are clearly demonstrated by projects or experience, even if the exact word isn't in a skills list. Example: a project that trains a prediction model means "Machine Learning" is a skill.
   - If a skills section has a category heading (like "AI / Machine Learning: Pandas, NumPy"), include the category as a skill too.
   - Still never invent skills with no evidence in the text.
2. "experience_years" — total years of professional experience.
   If not stated, estimate from job date ranges. If unknown, use 0.
3. "education" — each entry is a short string like
   "B.Sc. Computer Science, XYZ University (2022)".
4. "projects" — each entry is the project name/title only.
   If no projects section exists, return an empty list.

--- RESUME TEXT ---
{text}
--- END RESUME TEXT ---
"""
    raw_response = _call_llm(prompt)
    
    # Fallback default dictionary
    default_dict = {"skills": [], "experience_years": 0, "education": [], "projects": []}
    
    if not raw_response or "⏱️" in raw_response:
        return default_dict
        
    try:
        # Strip markdown fences (e.g., ```json ... ```)
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    except Exception:
        # Return fallback dictionary if JSON parsing crashes
        return default_dict


@st.cache_data
def extract_job_skills(text):
    """
    Sends job description text to the LLM and asks for a JSON object with:
        - role:                 the job title/role
        - required_skills:      list of mandatory skills
        - nice_to_have_skills:  list of bonus/preferred skills
        - alternatives:         list of lists of alternative skills

    Returns a Python dictionary parsed from the model's response.
    """
    prompt = f"""
You are a job description parser. Read the job description below and return ONLY valid JSON.
No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "role": "",
    "required_skills": [],
    "nice_to_have_skills": [],
    "alternatives": []
}}

Rules you MUST follow:
1. "role" — the core job title (e.g., "Software Engineer", "Data Scientist").
2. "required_skills" — short skill names only (e.g., "Python", "React", "AWS"). Never use sentences.
3. "nice_to_have_skills" — short skill names only. These are bonus, preferred, or "nice to have" skills.
4. "alternatives" — a list of lists, where each inner list holds skills of which any ONE satisfies the job (for example "AWS, Azure or GCP" gives [["AWS", "Azure", "GCP"]]).
5. Skills in an alternatives group must NOT also appear in required_skills.

--- JOB DESCRIPTION TEXT ---
{text}
--- END JOB DESCRIPTION TEXT ---
"""
    raw_response = _call_llm(prompt)
    
    # Fallback default dictionary
    default_dict = {"role": "", "required_skills": [], "nice_to_have_skills": [], "alternatives": []}
    
    if not raw_response or "⏱️" in raw_response:
        return default_dict
        
    try:
        # Strip markdown fences (e.g., ```json ... ```)
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    except Exception:
        # Return fallback dictionary if JSON parsing crashes
        return default_dict


def compare(resume_text, resume, job):
    """
    Compares resume skills and job requirements.
    Normalizes all skills and returns matched/missing lists and a match percentage.
    """
    # 1. Normalize all skill lists into sets for easy comparison
    res_skills = set(normalize(s) for s in resume.get("skills", []) if s)
    job_req = set(normalize(s) for s in job.get("required_skills", []) if s)
    job_nice = set(normalize(s) for s in job.get("nice_to_have_skills", []) if s)
    
    # 2. Calculate initial intersections and differences
    matched = list(job_req.intersection(res_skills))
    missing = list(job_req.difference(res_skills))
    
    bonus_matched = list(job_nice.intersection(res_skills))
    bonus_missing = list(job_nice.difference(res_skills))
    
    partial = []
    evidence = {}
    reasons = {}
    confidence = {}
    
    # 3. Verify missing skills via LLM
    if missing:
        verification = verify_missing_skills(resume_text, missing)
        for result in verification.get("results", []):
            skill = result.get("skill")
            status = result.get("status")
            ev = result.get("evidence", "")
            reason = result.get("reason", "")
            conf = result.get("confidence", "")
            
            if not skill or skill not in missing:
                continue
                
            if ev:
                evidence[skill] = ev
            if reason:
                reasons[skill] = reason
            if conf:
                confidence[skill] = conf
                
            if status == "matched":
                missing.remove(skill)
                matched.append(skill)
            elif status == "partial":
                missing.remove(skill)
                partial.append(skill)
                
    # 4. Calculate percentage
    match_percent = 0
    total_req = len(matched) + len(partial) + len(missing)
    if total_req > 0:
        match_percent = int((len(matched) + 0.5 * len(partial)) / total_req * 100)
        
    return {
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "bonus_matched": bonus_matched,
        "bonus_missing": bonus_missing,
        "evidence": evidence,
        "reasons": reasons,
        "confidence": confidence,
        "match_percent": match_percent
    }


# ---------------------------------------------------------------------------
# FUNCTION — Full resume analysis
# ---------------------------------------------------------------------------

def analyze_resume(resume_text, job_description=""):
    """
    Sends the resume (and optional job description) to the LLM
    and returns a detailed analysis report as markdown text.
    """
    prompt = f"""
You are a ruthlessly specific resume reviewer. You MUST reference and quote
actual words, phrases, bullet points, and section titles from the resume
provided below. Do NOT give generic advice — every single point you make
must cite something specific from this resume.

Analyze the resume below and return a STRUCTURED report with these exact
sections:

### 📊 Overall Score (out of 10)
Give a single number. Justify it by referencing 2–3 specific things
from the resume (quote them).

### ✅ Strengths (3–5 points)
For each strength, QUOTE the exact phrase or bullet from the resume that
is strong and explain WHY it works. Example format:
- ✅ **"Led a team of 5 to deliver X"** — Strong because it shows
  leadership and quantifies the impact.

### ⚠️ Weaknesses (3–5 points)
For each weakness, QUOTE the exact phrase or bullet that is weak and
explain what's wrong with it and how to fix it. Example format:
- ⚠️ **"Responsible for handling tasks"** — Too vague. Rewrite as:
  "Managed 15+ daily customer requests, reducing response time by 30%."

### 🛠️ Rewrite Suggestions
Pick the 3 weakest bullet points from the resume. For each one, show:
- **Original:** (quote the exact text)
- **Rewritten:** (your improved version with action verbs & metrics)

### 📝 Missing Sections
List any standard resume sections that are completely absent from this
resume. Only flag sections that are truly missing — check carefully
before listing. Common sections: Summary/Objective, Skills, Work
Experience, Projects, Education, Certifications, Awards.

### 🎯 ATS Compatibility (score out of 10)
- List 5 keywords that ARE present in the resume.
- List 5 important keywords that are MISSING and should be added.
- Flag any formatting issues that could break an ATS parser
  (e.g., tables, images, fancy characters).
"""

    if job_description.strip():
        prompt += f"""
### 🔗 Job-Match Analysis
Compare the resume against the job description below.
- List skills from the job description that APPEAR in the resume (quote them).
- List skills from the job description that are MISSING from the resume.
- Give a match percentage and explain what to add to increase it.

--- JOB DESCRIPTION ---
{job_description}
--- END JOB DESCRIPTION ---
"""

    prompt += f"""
--- RESUME TEXT ---
{resume_text}
--- END RESUME TEXT ---
"""
    return _call_llm(prompt)

# ---------------------------------------------------------------------------
# FUNCTION — Skill Categorization
# ---------------------------------------------------------------------------

CATEGORY_MAP = {
    # Frontend
    "React": "Frontend", "JavaScript": "Frontend", "TypeScript": "Frontend", 
    "HTML": "Frontend", "CSS": "Frontend", "State Management": "Frontend", 
    "Responsive Web Design": "Frontend", "Vue.js": "Frontend", "Angular": "Frontend", 
    "Next.js": "Frontend",
    
    # Backend
    "Node.js": "Backend", "REST APIs": "Backend", "FastAPI": "Backend", 
    "Django": "Backend", "Flask": "Backend", "Spring Boot": "Backend", 
    "Express.js": "Backend", "GraphQL": "Backend", "Microservices": "Backend",
    
    # Database
    "MongoDB": "Database", "MySQL": "Database", "PostgreSQL": "Database", 
    "Redis": "Database", "SQL": "Database", "NoSQL": "Database", 
    "Cassandra": "Database", "Elasticsearch": "Database", "SQLite": "Database",
    
    # DevOps & Cloud
    "Docker": "DevOps & Cloud", "AWS": "DevOps & Cloud", "CI/CD": "DevOps & Cloud", 
    "GitHub Actions": "DevOps & Cloud", "Kubernetes": "DevOps & Cloud", 
    "Google Cloud": "DevOps & Cloud", "Azure": "DevOps & Cloud", 
    "Terraform": "DevOps & Cloud", "Linux": "DevOps & Cloud",
    
    # Testing
    "Jest": "Testing", "Unit Testing": "Testing", "Integration Testing": "Testing", 
    "Cypress": "Testing", "Selenium": "Testing", "Mocha": "Testing", "PyTest": "Testing",
    
    # AI/ML
    "Machine Learning": "AI/ML", "NumPy": "AI/ML", "Pandas": "AI/ML", 
    "Scikit-learn": "AI/ML", "TensorFlow": "AI/ML", "Artificial Intelligence": "AI/ML", 
    "Deep Learning": "AI/ML", "Computer Vision": "AI/ML", 
    "Natural Language Processing": "AI/ML", "PyTorch": "AI/ML",
    
    # Tools
    "Git": "Tools", "GitHub": "Tools", "Jira": "Tools", "Webpack": "Tools", 
    "Babel": "Tools", "Figma": "Tools", "VS Code": "Tools", "Postman": "Tools",
    
    # Practices
    "Agile/Scrum": "Practices", "Object-Oriented Programming": "Practices",
    "Clean Code": "Practices", "System Design": "Practices", "Code Review": "Practices",
    
    # Languages
    "Python": "Languages", "Java": "Languages", "C++": "Languages", 
    "C#": "Languages", "Ruby": "Languages", "Go": "Languages", 
    "Rust": "Languages", "PHP": "Languages", "Swift": "Languages"
}

def categorize(skill):
    """
    Returns the broad category of a standard skill name.
    If the skill isn't found in the dictionary, returns 'Other'.
    """
    if not skill:
        return "Other"
    return CATEGORY_MAP.get(skill, "Other")

# ---------------------------------------------------------------------------
# FUNCTION — Graphviz DOT Builder
# ---------------------------------------------------------------------------

def build_graph(job_role, compare_result):
    """
    Builds a Graphviz DOT string drawn as a tree grouped by skill category.
    """
    safe_role = str(job_role).replace('"', '\\"') if job_role else "Job Role"
    
    categories = {}
    def add_skills(skill_list, color, text_color, mark):
        for skill in skill_list:
            cat = categorize(skill)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "name": str(skill).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
                "color": color,
                "text_color": text_color,
                "mark": mark
            })
            
    add_skills(compare_result.get("matched", []), "#2e7d32", "white", "✓ ")
    add_skills(compare_result.get("partial", []), "#f9a825", "black", "~ ")
    add_skills(compare_result.get("missing", []), "#c62828", "white", "✗ ")
    
    lines = ["digraph G {"]
    lines.append('    rankdir=TB;')
    lines.append('    graph [splines=ortho, nodesep=0.5, ranksep=0.8];')
    lines.append('    node [fontname="Helvetica", shape=plain];')
    lines.append('    edge [color="#94a3b8", style="solid", penwidth=1.5];')
    
    # Top node
    lines.append(f'    "{safe_role}" [shape=box, style="filled,rounded", fillcolor="#1e3a8a", fontcolor="white", fontsize=18, width=2, height=0.6];')
    
    # Build category tables
    for i, (cat, skills) in enumerate(categories.items()):
        if not skills:
            continue
            
        node_id = f"cat_{i}"
        
        # HTML Table for category
        html = '<TABLE BORDER="1" COLOR="#cbd5e1" STYLE="ROUNDED" CELLBORDER="0" CELLSPACING="2" CELLPADDING="6" BGCOLOR="white">'
        html += f'<TR><TD BGCOLOR="#475569"><FONT COLOR="white" POINT-SIZE="14"><B>{cat}</B></FONT></TD></TR>'
        
        for s in skills:
            html += f'<TR><TD BGCOLOR="{s["color"]}" STYLE="ROUNDED"><FONT COLOR="{s["text_color"]}" POINT-SIZE="13">{s["mark"]}{s["name"]}</FONT></TD></TR>'
            
        html += '</TABLE>'
        
        lines.append(f'    {node_id} [label=<{html}>];')
        lines.append(f'    "{safe_role}" -> {node_id};')
        
    lines.append("}")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# FUNCTION — Generate Learning Roadmap
# ---------------------------------------------------------------------------

@st.cache_data
def generate_roadmap(missing_skills, partial_skills, role):
    """
    Generates a personalized learning roadmap for missing and partial skills.
    Returns a Python dictionary parsed from the model's JSON response.
    """
    default_dict = {"steps": []}
    
    if not missing_skills and not partial_skills:
        return default_dict
        
    prompt = f"""
You are an expert career mentor. The user wants to become a "{role}".
They are completely missing these skills: {', '.join(missing_skills) if missing_skills else 'None'}.
They have partial exposure to these skills: {', '.join(partial_skills) if partial_skills else 'None'}.

Return ONLY valid JSON. No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "steps": [
        {{
            "skill": "",
            "priority": "",
            "why_it_matters": "",
            "how_to_learn": "",
            "time_estimate": ""
        }}
    ]
}}

Rules you MUST follow:
1. Provide one step for every missing and partial skill provided.
2. Order the steps from most important to least important for this role.
3. "priority" must be exactly "High", "Medium", or "Low".
   - High = skills the job description lists as required or mentions repeatedly.
   - Medium = useful but secondary.
   - Low = nice-to-have or already partly shown on the resume.
4. Every text field ("why_it_matters" and "how_to_learn") must be exactly ONE short sentence.
5. "time_estimate" should be a short string like "1-2 weeks" or "3 days".
6. NEVER use markdown.
"""
    raw_response = _call_llm(prompt)
    
    if not raw_response or "⏱️" in raw_response:
        return default_dict
        
    try:
        # Strip markdown fences (e.g., ```json ... ```)
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    except Exception:
        # Return fallback dictionary if JSON parsing crashes
        return default_dict

# ---------------------------------------------------------------------------
# FUNCTION — Verify Missing Skills
# ---------------------------------------------------------------------------

@st.cache_data
def verify_missing_skills(resume_text, missing_skills):
    """
    Double-checks if the "missing" skills are actually hidden somewhere in the resume.
    Returns a Python dictionary parsed from the model's JSON response.
    """
    default_dict = {"results": []}
    
    if not missing_skills:
        return default_dict
        
    prompt = f"""
You are an expert technical recruiter. Read the resume below and verify if it contains evidence for these skills: {', '.join(missing_skills)}.

Return ONLY valid JSON. No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "results": [
        {{
            "skill": "",
            "status": "matched" or "partial" or "missing",
            "evidence": "",
            "reason": "",
            "confidence": "high" or "medium" or "low"
        }}
    ]
}}

Rules you MUST follow:
1. Look for evidence anywhere in the resume: skills section, projects, experience, certifications.
2. If the resume shows a closely related technology (for example MySQL for PostgreSQL, or JavaScript for TypeScript), mark "partial" and name the related technology in "reason".
3. Statements like "interested in", "learning", "planning to", "no experience with" never count as matched. Mark those "missing".
4. For "missing", "reason" is one short sentence saying what is not demonstrated (use "not demonstrated", not "doesn't know").
5. If a skill name contains " / ", it means any ONE of those options satisfies the requirement.
6. Use "low" confidence when you are inferring rather than reading it directly.

--- RESUME TEXT ---
{resume_text}
--- END RESUME TEXT ---
"""
    raw_response = _call_llm(prompt)
    
    if not raw_response or "⏱️" in raw_response:
        return default_dict
        
    try:
        # Strip markdown fences (e.g., ```json ... ```)
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    except Exception:
        # Return fallback dictionary if JSON parsing crashes
        return default_dict

# ---------------------------------------------------------------------------
# FUNCTION — Score Breakdown
# ---------------------------------------------------------------------------

def score_breakdown(compare_result):
    """
    Calculates a detailed score breakdown including partial matches.
    Partial matches count as 0.5 towards the final match percentage.
    """
    matched_count = len(compare_result.get("matched", []))
    partial_count = len(compare_result.get("partial", []))
    missing_count = len(compare_result.get("missing", []))
    
    total_required = matched_count + partial_count + missing_count
    
    if total_required > 0:
        match_percent = round((matched_count + 0.5 * partial_count) / total_required * 100)
    else:
        match_percent = 0
        
    return {
        "total_required": total_required,
        "matched_count": matched_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "match_percent": match_percent
    }
