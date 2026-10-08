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
    returns the skill in Title Case.
    """
    if not skill:
        return ""
        
    cleaned = skill.strip().lower()
    
    # Map of ~30 common aliases to their standard names
    aliases = {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "reactjs": "React",
        "react.js": "React",
        "node": "Node.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "py": "Python",
        "python3": "Python",
        "ml": "Machine Learning",
        "machinelearning": "Machine Learning",
        "ai": "Artificial Intelligence",
        "html5": "HTML",
        "css3": "CSS",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "ts": "TypeScript",
        "vuejs": "Vue.js",
        "vue.js": "Vue.js",
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "Google Cloud",
        "google cloud platform": "Google Cloud",
        "k8s": "Kubernetes",
        "mongo": "MongoDB",
        "c++": "C++",
        "cpp": "C++",
        "c#": "C#",
        "csharp": "C#",
        "dl": "Deep Learning",
        "cv": "Computer Vision",
        "nlp": "Natural Language Processing",
    }
    
    # Return the mapped skill, or fallback to Title Casing the cleaned string
    return aliases.get(cleaned, cleaned.title())

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
   Never use sentences. Never duplicate. Only include skills that are
   explicitly written in the resume text. NEVER invent or guess skills.
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

    Returns a Python dictionary parsed from the model's response.
    """
    prompt = f"""
You are a job description parser. Read the job description below and return ONLY valid JSON.
No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "role": "",
    "required_skills": [],
    "nice_to_have_skills": []
}}

Rules you MUST follow:
1. "role" — the core job title (e.g., "Software Engineer", "Data Scientist").
2. "required_skills" — short skill names only (e.g., "Python", "React", "AWS"). Never use sentences.
3. "nice_to_have_skills" — short skill names only. These are bonus, preferred, or "nice to have" skills.

--- JOB DESCRIPTION TEXT ---
{text}
--- END JOB DESCRIPTION TEXT ---
"""
    raw_response = _call_llm(prompt)
    
    # Fallback default dictionary
    default_dict = {"role": "", "required_skills": [], "nice_to_have_skills": []}
    
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


def compare(resume, job):
    """
    Compares resume skills and job requirements.
    Normalizes all skills and returns matched/missing lists and a match percentage.
    """
    # 1. Normalize all skill lists into sets for easy comparison
    res_skills = set(normalize(s) for s in resume.get("skills", []) if s)
    job_req = set(normalize(s) for s in job.get("required_skills", []) if s)
    job_nice = set(normalize(s) for s in job.get("nice_to_have_skills", []) if s)
    
    # 2. Calculate intersections and differences
    matched = list(job_req.intersection(res_skills))
    missing = list(job_req.difference(res_skills))
    
    bonus_matched = list(job_nice.intersection(res_skills))
    bonus_missing = list(job_nice.difference(res_skills))
    
    # 3. Calculate percentage (matched / total required)
    match_percent = 0
    if len(job_req) > 0:
        match_percent = int((len(matched) / len(job_req)) * 100)
        
    return {
        "matched": matched,
        "missing": missing,
        "bonus_matched": bonus_matched,
        "bonus_missing": bonus_missing,
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
# FUNCTION — Graphviz DOT Builder
# ---------------------------------------------------------------------------

def build_graph(job_role, compare_result):
    """
    Builds a Graphviz DOT string visualizing matched and missing skills.
    Matched skills are green, missing are red with dashed edges.
    """
    safe_role = str(job_role).replace('"', '\\"') if job_role else "Job Role"
    
    lines = ["digraph G {"]
    lines.append(f'    "{safe_role}" [shape=ellipse, style=bold];')
    
    for skill in compare_result.get("matched", []):
        safe_skill = str(skill).replace('"', '\\"')
        lines.append(f'    "{safe_skill}" [style=filled, fillcolor=green];')
        lines.append(f'    "{safe_role}" -> "{safe_skill}";')
        
    for skill in compare_result.get("missing", []):
        safe_skill = str(skill).replace('"', '\\"')
        lines.append(f'    "{safe_skill}" [style=filled, fillcolor=red];')
        lines.append(f'    "{safe_role}" -> "{safe_skill}" [style=dashed];')
        
    lines.append("}")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# FUNCTION — Generate Learning Roadmap
# ---------------------------------------------------------------------------

@st.cache_data
def generate_roadmap(missing_skills, role):
    """
    Generates a personalized learning roadmap for missing skills.
    Returns a Python dictionary parsed from the model's JSON response.
    """
    default_dict = {"steps": []}
    
    if not missing_skills:
        return default_dict
        
    prompt = f"""
You are an expert career mentor. The user wants to become a "{role}" but is missing these skills: {', '.join(missing_skills)}.
Return ONLY valid JSON. No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "steps": [
        {{
            "skill": "",
            "why_it_matters": "",
            "how_to_learn": "",
            "time_estimate": ""
        }}
    ]
}}

Rules you MUST follow:
1. One step per missing skill provided.
2. Order the steps from most important to least important for this role.
3. Every text field ("why_it_matters" and "how_to_learn") must be exactly ONE short sentence.
4. "time_estimate" should be a short string like "1-2 weeks" or "3 days".
5. NEVER use markdown.
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
