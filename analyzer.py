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

def _call_groq(prompt, temperature=0.2):
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
                    temperature=temperature,
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

def _call_gemini(prompt, temperature=0.2):
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
                        temperature=temperature,
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

def _call_llm(prompt, temperature=0.2):
    """
    Master function: 
    1. Tries Groq (fastest)
    2. Falls back to Gemini
    3. Returns an error message if all fail.
    """
    # 1. Try Groq
    groq_result = _call_groq(prompt, temperature=temperature)
    if groq_result:
        return groq_result
        
    # 2. Try Gemini
    gemini_result = _call_gemini(prompt, temperature=temperature)
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
        "restful api": "REST APIs",
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
        "aws ec2": "AWS",
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

@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
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
6. If the job description describes a practice and a tool as one requirement (for example "unit and integration tests using Jest" or "CI/CD pipelines using GitHub Actions"), list it as ONE required skill with a combined name like "Unit & Integration Testing with Jest" or "CI/CD with GitHub Actions", not as separate skills. Only list them separately if the job description lists them in separate places.

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
    
    # Process alternatives
    for group in job.get("alternatives", []):
        if not group:
            continue
        norm_group = []
        for s in group:
            if s:
                ns = normalize(s)
                if ns not in norm_group:
                    norm_group.append(ns)
                    
        if not norm_group:
            continue
            
        matching_skills = [s for s in norm_group if s in res_skills]
        if matching_skills:
            matched.append(matching_skills[0])
        else:
            missing.append(" / ".join(norm_group))
            
    partial = []
    evidence = {}
    reasons = {}
    confidence = {}
    gaps = {}
    
    # 3. Verify missing skills via LLM
    if missing:
        verification = verify_missing_skills(resume_text, missing)
        for result in verification.get("results", []):
            skill = result.get("skill")
            status = result.get("status")
            ev = result.get("evidence", "")
            reason = result.get("reason", "")
            conf = result.get("confidence", "")
            what = result.get("what_is_missing", "")
            
            if not skill or skill not in missing:
                continue
                
            if ev:
                evidence[skill] = ev
            if reason:
                reasons[skill] = reason
            if conf:
                confidence[skill] = conf
            if what:
                gaps[skill] = what
                
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
        
    # 5. Find evidence for matched skills
    if matched:
        found = find_evidence(resume_text, matched)
        for res in found.get("results", []):
            sk = res.get("skill")
            ev = res.get("evidence", "")
            if sk and ev and sk not in evidence:
                evidence[sk] = ev
                
    return {
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "bonus_matched": bonus_matched,
        "bonus_missing": bonus_missing,
        "evidence": evidence,
        "reasons": reasons,
        "confidence": confidence,
        "gaps": gaps,
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

SKILL_CATEGORIES = {
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
    
    # AI / ML
    "Machine Learning": "AI / ML", "NumPy": "AI / ML", "Pandas": "AI / ML", 
    "scikit-learn": "AI / ML", "TensorFlow": "AI / ML", "Artificial Intelligence": "AI / ML", 
    "Deep Learning": "AI / ML", "Computer Vision": "AI / ML", 
    "Natural Language Processing": "AI / ML", "PyTorch": "AI / ML",
    
    # Tools & Process
    "Git": "Tools & Process", "GitHub": "Tools & Process", "Agile/Scrum": "Tools & Process",
    "Jira": "Tools & Process", "Webpack": "Tools & Process", "Babel": "Tools & Process", 
    "Figma": "Tools & Process", "VS Code": "Tools & Process", "Postman": "Tools & Process",
    "Object-Oriented Programming": "Tools & Process", "Clean Code": "Tools & Process", 
    "System Design": "Tools & Process", "Code Review": "Tools & Process",
    
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
        
    skill_lower = skill.lower()
    if "testing" in skill_lower or "jest" in skill_lower:
        return "Testing"
    if "ci/cd" in skill_lower or "docker" in skill_lower or "aws" in skill_lower:
        return "DevOps & Cloud"
    if "agile" in skill_lower or "scrum" in skill_lower:
        return "Tools & Process"
        
    if " / " in skill:
        first_skill = skill.split(" / ")[0].strip()
        return SKILL_CATEGORIES.get(first_skill, "Other")
        
    return SKILL_CATEGORIES.get(skill, "Other")

# ---------------------------------------------------------------------------
# FUNCTION — Graphviz DOT Builder
# ---------------------------------------------------------------------------

def build_graph(job_role, compare_result):
    """
    Builds a Graphviz DOT string drawn as a tree grouped by skill category.
    """
    safe_role = str(job_role).replace('"', '\\"') if job_role else "Job Role"
    
    categories = {}
    
    def add_skills(skill_list, bg_color, text_color, mark):
        for skill in skill_list:
            cat = categorize(skill)
            if cat not in categories:
                categories[cat] = []
            
            safe_skill = str(skill).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            categories[cat].append({
                "name": safe_skill,
                "bg_color": bg_color,
                "text_color": text_color,
                "mark": mark
            })
            
    # Only group required skills (skip nice-to-have)
    add_skills(compare_result.get("matched", []), "#2e7d32", "white", "✓ ")
    add_skills(compare_result.get("partial", []), "#f9a825", "black", "~ ")
    add_skills(compare_result.get("missing", []), "#c62828", "white", "✗ ")
    
    lines = [
        "digraph G {",
        "    rankdir=TB;",
        '    node [fontname="Helvetica", shape=plain];',
        '    edge [color="grey", style="solid"];',
        f'    "{safe_role}" [shape=box, style="filled,rounded", fillcolor="darkblue", fontcolor="white", fontsize=18];'
    ]
    
    for i, (cat, skills) in enumerate(categories.items()):
        if not skills:
            continue
            
        node_id = f"cat_{i}"
        
        # Build HTML table
        html = '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'
        html += f'<TR><TD BGCOLOR="darkgrey"><B><FONT COLOR="white">{cat}</FONT></B></TD></TR>'
        
        for s in skills:
            html += f'<TR><TD BGCOLOR="{s["bg_color"]}"><FONT COLOR="{s["text_color"]}" POINT-SIZE="13">{s["mark"]}{s["name"]}</FONT></TD></TR>'
            
        html += '</TABLE>'
        
        lines.append(f'    {node_id} [label=<{html}>];')
        lines.append(f'    "{safe_role}" -> {node_id};')
        
    lines.append("}")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# FUNCTION — Generate Learning Roadmap
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _rewrite_bullet(bullet, apply_text):
    prompt = f"Rewrite this resume bullet so it only describes the work done on <project>, using the planned steps below. Do not include any numbers, percentages, outcomes, performance, reliability, scalability or business-impact claims. Planned steps: {apply_text}. Bullet: {bullet}"
    response = _call_llm(prompt)
    if response and "⏱️" not in response:
        return response.strip()
    return ""

def clean_bullet(bullet, skill, apply_text):
    def fails_check(b):
        if not b: return False
        b_lower = b.lower()
        banned_words = ["ensuring", "ensure", "improving", "enhance", "reliability", "availability", "optimal", "production", "scalable", "robust"]
        return any(char.isdigit() for char in b) or "%" in b or any(w in b_lower for w in banned_words)

    if not fails_check(bullet):
        return bullet
        
    rewritten = _rewrite_bullet(bullet, apply_text)
    if rewritten and not fails_check(rewritten):
        return rewritten
        
    return f"Added {skill} to <project> [describe what you actually did]"

@st.cache_data(show_spinner=False)
def generate_roadmap(missing_skills, partial_skills, role, projects, job_text, evidence, gaps):
    """
    Generates a personalized learning roadmap for missing and partial skills.
    Returns a Python dictionary parsed from the model's JSON response.
    """
    default_dict = {"steps": [], "optional": []}
    
    if not missing_skills and not partial_skills:
        return default_dict
        
    prompt = f"""
You are an expert career mentor. The user wants to become a "{role}".
The job description is:
{job_text}

They are completely missing these skills: {', '.join(missing_skills) if missing_skills else 'None'}.
They have partial exposure to these skills: {', '.join(partial_skills) if partial_skills else 'None'}.
Their current projects are: {', '.join(projects) if projects else 'None'}.
Evidence found: {json.dumps(evidence) if evidence else 'None'}
Gaps identified: {json.dumps(gaps) if gaps else 'None'}.

Return ONLY valid JSON. No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "steps": [
        {{
            "order": 1,
            "skill": "",
            "priority": "High" or "Medium" or "Low",
            "why_gap": "",
            "learn": "",
            "apply": "",
            "prove": "",
            "example_bullet": "",
            "suggested_effort": "",
            "do_after": ""
        }}
    ],
    "optional": [
        {{
            "skill": "",
            "reason": ""
        }}
    ]
}}

Rules you MUST follow:
1. Merge closely related skills into one step (for example Unit Testing + Jest becomes "Unit Testing with Jest", CI/CD + GitHub Actions becomes one step).
2. Use 3 to 5 High, 3 to 5 Medium, and the rest Low. Never mark more than 5 steps High.
3. "order" is the suggested learning order, starting at 1 (fundamentals first).
4. "why_gap" must be built only from the job requirement plus the evidence and gaps provided. Do not say things like "only partial exposure". For partial skills, state what related skills were found and what direct experience was not shown. If no evidence is provided for a skill, say "not demonstrated in the resume". Do not make claims about what the industry "standard" is.
5. "learn" is what to study, "apply" is a concrete change to one of the candidate's existing projects (by name), "prove" is what real evidence should exist afterwards (for example "a repo with tests that run on every push").
6. "apply" and "learn" must only reference projects from the provided projects list, exactly as named.
7. Scope each step to what the job requires (for example "deploy one existing application to AWS EC2", not "learn AWS").
8. "example_bullet" describes only the work to be done, in plain past tense, with NO numbers, percentages, performance claims, reliability or availability claims, or business impact (for example never write "ensuring high availability", "improving code quality", "reducing errors").
9. For methodologies like Agile/Scrum, "prove" is "a board and sprint notes for a personal project" and the example bullet must say "applied Agile practices to a personal project", never professional Scrum experience.
10. If a metric would normally help, end the bullet with a bracket like "[add your real result here if you have one]".
11. Never claim an outcome the candidate has not achieved.
12. "suggested_effort" must be phrased like "Estimated effort for foundational experience: 1-2 weeks".
13. If a skill is "partial", recommend fundamentals first. Never use "Advanced" in a step name unless the job description itself asks for advanced level.
14. Steps are only for skills in the missing or partial lists. Anything else useful (for example performance monitoring) goes in "optional" with a one-line reason, maximum 2 items.
15. Decide priority using (a) skills listed under requirements or mentioned several times in the job description rank higher, (b) skills the job only prefers rank lower, (c) a partial skill that the job clearly centers on can outrank a missing minor skill such as Agile/Scrum, (d) foundational skills that others depend on (for example unit testing before CI/CD) get an earlier "order".
16. Choose ONE simple route per skill and do not list several tools or architectures. For AWS, recommend deploying one existing application to a single EC2 instance, and mention only EC2, security groups, SSH and basic IAM unless the job description names other services.
17. If a skill name contains " / " (the job accepts any one option), recommend exactly one option and say why it is a good choice.
18. "prove" must describe the outcome, not the folder structure. For example "a working Jest test suite covering the main parts of the application", not "a tests directory". Do not require specific file paths.
19. For partial skills, do not start from scratch: build on the related evidence the candidate already has.
"""
    raw_response = _call_llm(prompt, temperature=0.2)
    
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
        
        parsed = json.loads(cleaned.strip())
        for step in parsed.get("steps", []):
            step["example_bullet"] = clean_bullet(step.get("example_bullet", ""), step.get("skill", ""), step.get("apply", ""))
        return parsed
    except Exception:
        # Return fallback dictionary if JSON parsing crashes
        return default_dict

# ---------------------------------------------------------------------------
# FUNCTION — Verify Missing Skills
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
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
            "confidence": "high" or "medium" or "low",
            "what_is_missing": ""
        }}
    ]
}}

Rules you MUST follow:
1. Look for evidence anywhere in the resume: skills section, projects, experience, certifications.
2. If the resume shows a closely related technology (for example MySQL for PostgreSQL, or JavaScript for TypeScript), mark "partial". For partial skills, the reason must name exactly which related evidence was found and which direct evidence was not found, using the pattern: "Found: <related items>. Not found: <direct evidence>." For "partial", "evidence" should list the related skills found.
3. Statements like "interested in", "learning", "planning to", "no experience with" never count as matched. Mark those "missing".
4. For "missing", "reason" is one short sentence saying what is not demonstrated (use "not demonstrated", not "doesn't know").
5. If a skill name contains " / ", it means any ONE of those options satisfies the requirement.
6. Use "low" confidence when you are inferring rather than reading it directly.
7. "what_is_missing": for "partial" it is one short sentence naming what the resume lacks (for example "No direct TypeScript typing, interfaces or generics shown"). For "matched" and "missing" it is an empty string.
8. For methodologies (Agile/Scrum): mark "matched" only if the resume shows real ceremonies or roles (sprint planning, standups, retrospectives, Scrum master, sprints). Code reviews, task boards or iterative work alone are "partial", and the reason must say "related engineering practice found, but Scrum practices were not shown".
9. Generic frontend skills (HTML, CSS, React) alone do not prove Responsive Web Design or State Management; they give "partial" only, with the pattern above.
10. If a skill name combines a practice and a tool (for example "Unit & Integration Testing with Jest"), mark it "matched" only if both parts are shown and "partial" if only one is shown.

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
# FUNCTION — Find Evidence
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def find_evidence(resume_text, matched_skills):
    """
    Finds exact phrase evidence in the resume for matched skills.
    Returns a Python dictionary parsed from the model's JSON response.
    """
    default_dict = {"results": []}
    
    if not matched_skills:
        return default_dict
        
    prompt = f"""
You are an expert technical recruiter. Read the resume below and find evidence for these matched skills: {', '.join(matched_skills)}.

Return ONLY valid JSON. No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "results": [
        {{
            "skill": "",
            "evidence": "",
            "where": "Skills section" or "Project" or "Experience" or "Other"
        }}
    ]
}}

Rules you MUST follow:
1. "evidence" is a short phrase of at most 12 words copied from the resume that shows the skill.
2. If there is no evidence, use an empty string.
3. NEVER invent evidence.

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

def build_html_report(job_role, compare_result, score, roadmap):
    """
    Builds a standalone HTML report.
    """
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append('<meta charset="UTF-8">')
    html.append(f"<title>Career Analysis: {job_role}</title>")
    html.append("""
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.6; }
        h1, h2, h3, h4 { color: #2c3e50; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.9em; margin-bottom: 8px; }
        .badge.matched { background-color: #2e7d32; }
        .badge.partial { background-color: #f9a825; color: black; }
        .badge.missing { background-color: #c62828; }
        .skill-card { border: 1px solid #eee; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .roadmap-step { background: #f8f9fa; border-left: 4px solid #2196f3; padding: 15px; margin-bottom: 20px; }
        .roadmap-optional { background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .detail-label { font-weight: bold; color: #555; }
    </style>
    """)
    html.append("</head>")
    html.append("<body>")
    
    html.append(f"<h1>Career Analysis: {job_role}</h1>")
    
    match_percent = score.get('match_percent', 0)
    matched_count = score.get('matched_count', 0)
    partial_count = score.get('partial_count', 0)
    total_req = score.get('total_required', 0)
    
    html.append(f"<h2>Core skill match: {match_percent}%</h2>")
    html.append(f"<p>{matched_count} fully matched + {partial_count} partial out of {total_req} required skills</p>")
    html.append("<hr>")
    
    evidence = compare_result.get("evidence", {})
    reasons = compare_result.get("reasons", {})
    gaps = compare_result.get("gaps", {})
    matched_skills = compare_result.get("matched", [])
    partial_skills = compare_result.get("partial", [])
    missing_skills = compare_result.get("missing", [])
    
    # Matched Skills
    html.append("<h3>✅ Matched Skills</h3>")
    if matched_skills:
        for skill in matched_skills:
            html.append('<div class="skill-card">')
            html.append(f'<div class="badge matched">{skill}</div>')
            ev = evidence.get(skill, "")
            if ev:
                html.append(f'<div><span class="detail-label">Evidence:</span> "{ev}"</div>')
            html.append('</div>')
    else:
        html.append("<p>None</p>")
        
    # Partial Skills
    html.append("<h3>⚠️ Partial Skills</h3>")
    if partial_skills:
        for skill in partial_skills:
            html.append('<div class="skill-card">')
            html.append(f'<div class="badge partial">{skill}</div>')
            ev = evidence.get(skill, "")
            if ev:
                html.append(f'<div><span class="detail-label">Evidence:</span> "{ev}"</div>')
            rs = reasons.get(skill, "")
            if rs:
                html.append(f'<div><span class="detail-label">Why partial:</span> {rs}</div>')
            gp = gaps.get(skill, "")
            if gp:
                html.append(f'<div><span class="detail-label">What\'s missing:</span> {gp}</div>')
            html.append('</div>')
    else:
        html.append("<p>None</p>")
        
    # Missing Skills
    html.append("<h3>❌ Not Demonstrated Skills</h3>")
    if missing_skills:
        for skill in missing_skills:
            html.append('<div class="skill-card">')
            html.append(f'<div class="badge missing">{skill}</div>')
            rs = reasons.get(skill, "")
            if rs:
                html.append(f'<div><span class="detail-label">Reason:</span> {rs}</div>')
            html.append('</div>')
    else:
        html.append("<p>None</p>")
        
    # Roadmap
    html.append("<hr>")
    html.append("<h2>🚀 Your Roadmap</h2>")
    
    if not missing_skills and not partial_skills:
        html.append("<p>You already have all required skills!</p>")
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
                html.append(f"<h3>{pri_label}</h3>")
                for step in sorted_steps:
                    html.append('<div class="roadmap-step">')
                    eff = step.get("suggested_effort", "")
                    title_eff = f" ({eff})" if eff else ""
                    html.append(f"<h4>{step.get('order', '?')}. {step.get('skill', '')}{title_eff}</h4>")
                    
                    do_after = step.get("do_after", "")
                    if do_after:
                        html.append(f'<div><span class="detail-label">Do this after:</span> {do_after}</div>')
                    
                    html.append(f'<div><span class="detail-label">Why this is a gap:</span> {step.get("why_gap", "")}</div>')
                    html.append(f'<div><span class="detail-label">Learn:</span> {step.get("learn", "")}</div>')
                    html.append(f'<div><span class="detail-label">Apply:</span> {step.get("apply", "")}</div>')
                    html.append(f'<div><span class="detail-label">What proves it:</span> {step.get("prove", "")}</div>')
                    html.append(f'<div><span class="detail-label">Example resume bullet:</span> {step.get("example_bullet", "")}</div>')
                    html.append('</div>')
                    
        optional_items = roadmap.get("optional", [])
        if optional_items:
            html.append("<h3>✨ Optional improvements</h3>")
            html.append('<div class="roadmap-optional"><ul>')
            for item in optional_items:
                html.append(f"<li><strong>{item.get('skill', '')}</strong>: {item.get('reason', '')}</li>")
            html.append('</ul></div>')
            
    html.append("</body>")
    html.append("</html>")
    return "\n".join(html)
