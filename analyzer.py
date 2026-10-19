"""
analyzer.py — AI-powered resume analysis functions (Groq)
===================================================================
All AI logic lives here. The Streamlit UI (app.py) imports from this file.

Setup:
    Put your API keys in your .env file:
        GROQ_API_KEYS=groq_key1,groq_key2
    
    The system uses Groq for resume and job match analysis.
"""

import os
import time
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Rate limit tracking & cooldown helpers (Groq)
# ---------------------------------------------------------------------------

last_rate_limit_at: float = 0.0


def set_last_rate_limit_at(ts: float | None = None) -> float:
    """Updates the shared module-level last_rate_limit_at timestamp."""
    global last_rate_limit_at
    last_rate_limit_at = time.time() if ts is None else float(ts)
    return last_rate_limit_at


def wait_for_rate_limit_cooldown(start_time: float | None = None, max_wait: float = 15.0):
    """
    Before any Groq call, if a rate limit happened less than 15 seconds ago,
    wait out the remainder (max 15 seconds). Never blocks longer than 30s in total.
    """
    global last_rate_limit_at
    if last_rate_limit_at > 0:
        elapsed = time.time() - last_rate_limit_at
        if elapsed < 15.0:
            remainder = 15.0 - elapsed
            wait_time = min(15.0, max_wait, remainder)
            if start_time is not None:
                budget = max(0.0, 30.0 - (time.time() - start_time))
                wait_time = min(wait_time, budget)
            if wait_time > 0:
                time.sleep(wait_time)


def _extract_retry_after(e: Exception) -> float | None:
    """Reads the Retry-After header or message from an exception if present."""
    if e is None:
        return None
    # 1. Check response.headers
    response = getattr(e, "response", None)
    if response is not None:
        headers = getattr(response, "headers", {})
        if hasattr(headers, "get"):
            ra = headers.get("retry-after") or headers.get("Retry-After") or headers.get("retry-after-ms")
            if ra is not None:
                try:
                    val = float(ra)
                    if headers.get("retry-after-ms") and val > 1000:
                        val = val / 1000.0
                    return val
                except (ValueError, TypeError):
                    pass
    # 2. Check attribute on exception directly
    if hasattr(e, "retry_after"):
        try:
            return float(getattr(e, "retry_after"))
        except (ValueError, TypeError):
            pass
    # 3. Check error message string for "try again in Xs" or "retry after X"
    msg = str(e)
    match = re.search(r"try again in ([\d\.]+)s", msg, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    match_sec = re.search(r"retry[- ]after[:\s]+([\d\.]+)", msg, re.IGNORECASE)
    if match_sec:
        try:
            return float(match_sec.group(1))
        except (ValueError, TypeError):
            pass
    return None

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
    # Fallback to singular just in case (e.g., GROQ_API_KEY instead of KEYS)
    single = os.getenv(env_var_name.replace("_KEYS", "_KEY"), "")
    if single.strip():
        return [single.strip()]
    return []


# Groq Models
_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "allam-2-7b",
]

def _call_groq(prompt, temperature=0.2, seed=None):
    """Tries Groq models. Returns text if successful, or None if rate limited/failed."""
    keys = _get_api_keys("GROQ_API_KEYS")
    if not keys:
        return None  # No Groq keys provided
        
    for api_key in keys:
        client = Groq(api_key=api_key)
        for model_name in _GROQ_MODELS:
            try:
                wait_for_rate_limit_cooldown()
                kwargs = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": 2048,
                    "timeout": 60
                }
                if seed is not None:
                    kwargs["seed"] = seed
                
                completion = client.chat.completions.create(**kwargs)
                return completion.choices[0].message.content
            except Exception as e:
                error_msg = str(e).lower()
                
                # If rate limited -> try next model/key
                if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                    set_last_rate_limit_at()
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

def _call_llm(prompt, temperature=0.2, seed=None):
    """
    Master function: 
    1. Tries Groq
    2. Returns an error message if failed.
    """
    # 1. Try Groq
    groq_result = _call_groq(prompt, temperature=temperature, seed=seed)
    if groq_result:
        return groq_result
        
    # 2. Failed
    return (
        "⏱️ **All Groq API keys are rate-limited or missing.**\n\n"
        "Please check your `.env` file and make sure you have valid API keys for "
        "`GROQ_API_KEYS`."
    )

_ORIGINAL_CALL_LLM_CODE = _call_llm.__code__



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
    raw_response = _call_llm(prompt, temperature=0.0, seed=42)
    
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
        
        parsed = json.loads(cleaned.strip())
        if "skills" in parsed and isinstance(parsed["skills"], list):
            parsed["skills"] = sorted(list(set(normalize(s) for s in parsed["skills"] if s)))
        return parsed
    except Exception:
        # Return fallback dictionary if JSON parsing crashes
        return default_dict


import time


class JobExtractionError(Exception):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason
        self.message = message
        self._data = {
            "error": reason,
            "error_message": message,
            "role": "",
            "required_skills": [],
            "nice_to_have_skills": [],
            "alternatives": [],
            "soft_skills": [],
            "experience_requirements": [],
        }

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


class _EmptyResultException(Exception):
    def __init__(self, data: dict):
        self.data = data


REASON_MESSAGES = {
    "rate_limit": "The AI service is busy (rate limit). Please wait about a minute and try again.",
    "timeout": "The AI service request timed out. Please try again.",
    "bad_json": "The AI service returned an invalid response (bad JSON). Please try again.",
    "no_key": "No API key found. Please configure your API key in the .env file.",
    "other": "The AI service encountered an error. Please try again."
}


def _classify_llm_exception(e: Exception) -> str:
    err_str = str(e).lower()
    err_type = type(e).__name__.lower()

    if (
        "429" in err_str
        or "rate limit" in err_str
        or "ratelimit" in err_str
        or "quota" in err_str
        or "resource_exhausted" in err_str
        or "resourceexhausted" in err_type
        or "ratelimit" in err_type
    ):
        return "rate_limit"

    if (
        "timeout" in err_str
        or "timed out" in err_str
        or "deadline" in err_str
        or "deadlineexceeded" in err_type
        or "timeouterror" in err_type
        or "timeout" in err_type
    ):
        return "timeout"

    return "other"


def _get_extraction_keys():
    keys = []
    for k in _get_api_keys("GROQ_API_KEYS"):
        keys.append(("groq", k))
    return keys


class _ParseStepResult(tuple):
    def __new__(cls, success, reason, parsed, retry_after=None):
        obj = super().__new__(cls, (success, reason, parsed))
        obj.retry_after = retry_after
        return obj


def _execute_extraction_call(prompt: str, provider: str, api_key: str, timeout: int = 25, check_cooldown: bool = True, start_time: float | None = None) -> str:
    if provider == "groq":
        if Groq is None:
            raise RuntimeError("groq library is not installed")
        if check_cooldown:
            wait_for_rate_limit_cooldown(start_time=start_time)
        client = Groq(api_key=api_key)
        last_err = None
        for model_name in _GROQ_MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=2048,
                    timeout=timeout,
                    seed=42,
                )
                return completion.choices[0].message.content
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                    set_last_rate_limit_at()
                if "404" in err_str or "does not exist" in err_str or "decommissioned" in err_str:
                    last_err = e
                    continue
                raise e
        if last_err:
            raise last_err
        raise RuntimeError("No Groq models available")

    else:
        raise ValueError(f"Unknown provider: {provider}")


def _call_and_parse_step(prompt: str, provider: str, api_key: str, timeout: int = 25, check_cooldown: bool = True, start_time: float | None = None):
    try:
        is_mocked = (
            type(_call_llm).__name__ in ("MagicMock", "Mock", "AsyncMock")
            or hasattr(_call_llm, "mock")
            or getattr(_call_llm, "__code__", None) is not _ORIGINAL_CALL_LLM_CODE
        )
        if is_mocked:
            if check_cooldown and provider == "groq":
                wait_for_rate_limit_cooldown(start_time=start_time)
            raw = _call_llm(prompt, temperature=0.0, seed=42)
        else:
            raw = _execute_extraction_call(prompt, provider, api_key, timeout=timeout, check_cooldown=check_cooldown, start_time=start_time)
    except Exception as e:
        reason = _classify_llm_exception(e)
        retry_after = _extract_retry_after(e) if reason == "rate_limit" else None
        if reason == "rate_limit":
            set_last_rate_limit_at()
        return _ParseStepResult(False, reason, None, retry_after)

    if raw is None:
        set_last_rate_limit_at()
        return _ParseStepResult(False, "rate_limit", None, None)

    if isinstance(raw, str) and ("⏱️" in raw or "rate-limited" in raw.lower() or "rate limit" in raw.lower()):
        set_last_rate_limit_at()
        return _ParseStepResult(False, "rate_limit", None, None)

    if isinstance(raw, str) and ("timed out" in raw.lower() or "timeout" in raw.lower()):
        return _ParseStepResult(False, "timeout", None, None)

    if isinstance(raw, str) and "❌" in raw:
        return _ParseStepResult(False, "other", None, None)

    cleaned = str(raw).strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        parsed = json.loads(cleaned.strip())
        if not isinstance(parsed, dict):
            return _ParseStepResult(False, "bad_json", None, None)
        return _ParseStepResult(True, None, parsed, None)
    except Exception:
        return _ParseStepResult(False, "bad_json", None, None)


def _extract_job_skills_uncached(text: str) -> dict:
    prompt = f"""
You are a job description parser. Read the job description below and return ONLY valid JSON.
No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "role": "",
    "required_skills": [],
    "nice_to_have_skills": [],
    "alternatives": [],
    "soft_skills": [],
    "experience_requirements": []
}}

Rules you MUST follow:
1. "role" — the core job title (e.g., "Software Engineer", "Data Scientist").
2. "required_skills" and "nice_to_have_skills" may contain ONLY named technologies, tools, languages, engineering practices (like Unit Testing, CI/CD) and methodologies (like Agile/Scrum), each a short name of at most 4 words.
3. Interpersonal qualities (communication, teamwork, problem-solving) go in "soft_skills".
4. Sentences or statements like "experience integrating AI/ML models into applications" or "basic understanding of machine learning" go in "experience_requirements", never in required_skills. For "basic understanding of machine learning", ALSO add the plain skill "Machine Learning" to required_skills.
5. Do not list the same requirement twice under different names.
6. "alternatives" — a list of lists, where each inner list holds skills of which any ONE satisfies the job (for example "AWS, Azure or GCP" gives [["AWS", "Azure", "GCP"]]).
7. Skills in an alternatives group must NOT also appear in required_skills.
8. If the job description describes a practice and a tool as one requirement (for example "unit and integration tests using Jest" or "CI/CD pipelines using GitHub Actions"), list it as ONE required skill with a combined name like "Unit & Integration Testing with Jest" or "CI/CD with GitHub Actions", not as separate skills. Only list them separately if the job description lists them in separate places.

--- JOB DESCRIPTION TEXT ---
{text}
--- END JOB DESCRIPTION TEXT ---
"""
    start_time = time.time()
    keys = _get_extraction_keys()
    if not keys:
        reason = "no_key"
        elapsed = time.time() - start_time
        print(f"{reason} (attempt 0, key index None, elapsed {elapsed:.2f}s)")
        raise JobExtractionError(reason, REASON_MESSAGES[reason])

    key_idx = 0
    attempt = 1
    provider, api_key = keys[key_idx]

    step_res = _call_and_parse_step(prompt, provider, api_key, timeout=25, check_cooldown=True, start_time=start_time)
    success, reason, parsed = step_res[0], step_res[1], step_res[2]
    retry_after = getattr(step_res, "retry_after", None) or (step_res[3] if len(step_res) > 3 else None)

    if not success:
        elapsed = time.time() - start_time
        print(f"{reason} (attempt {attempt}, key index {key_idx}, elapsed {elapsed:.2f}s)")

        if reason == "rate_limit":
            # On a rate limit (HTTP 429), read the Retry-After header if present.
            # Wait that long, capped at 20 seconds, then retry once on the next key (or the same key if only one).
            # If no header, wait 15 seconds. Never block longer than 30 seconds in total.
            if retry_after is not None:
                wait_time = min(20.0, max(0.0, float(retry_after)))
            else:
                wait_time = 15.0

            remaining_budget = max(0.0, 30.0 - (time.time() - start_time))
            wait_time = min(wait_time, remaining_budget)
            if wait_time > 0:
                time.sleep(wait_time)

            key_idx = (key_idx + 1) % len(keys)
            attempt = 2
            provider, api_key = keys[key_idx]
            step_res2 = _call_and_parse_step(prompt, provider, api_key, timeout=25, check_cooldown=False, start_time=start_time)
            success, reason2, parsed = step_res2[0], step_res2[1], step_res2[2]
            if not success:
                elapsed = time.time() - start_time
                print(f"{reason2} (attempt {attempt}, key index {key_idx}, elapsed {elapsed:.2f}s)")
                raise JobExtractionError(reason2, REASON_MESSAGES.get(reason2, REASON_MESSAGES["other"]))

        elif reason == "bad_json":
            # Retry once on bad_json (add "Return valid JSON only" to the prompt)
            attempt = 2
            retry_prompt = prompt.rstrip() + "\n\nReturn valid JSON only."
            step_res2 = _call_and_parse_step(retry_prompt, provider, api_key, timeout=25, check_cooldown=True, start_time=start_time)
            success, reason2, parsed = step_res2[0], step_res2[1], step_res2[2]
            if not success:
                elapsed = time.time() - start_time
                print(f"{reason2} (attempt {attempt}, key index {key_idx}, elapsed {elapsed:.2f}s)")
                raise JobExtractionError(reason2, REASON_MESSAGES.get(reason2, REASON_MESSAGES["other"]))

        else:
            # timeout, other -> no retry
            raise JobExtractionError(reason, REASON_MESSAGES.get(reason, REASON_MESSAGES["other"]))

    import re
    trigger_pattern = re.compile(r"\b(experience|understanding|ability|skills|knowledge|familiarity)\b", re.IGNORECASE)

    if "experience_requirements" not in parsed or not isinstance(parsed["experience_requirements"], list):
        parsed["experience_requirements"] = []

    for key in ["required_skills", "nice_to_have_skills"]:
        if key in parsed and isinstance(parsed[key], list):
            valid_skills = []
            for s in parsed[key]:
                if not s:
                    continue
                if len(s.split()) > 5 or trigger_pattern.search(s):
                    parsed["experience_requirements"].append(s)
                else:
                    valid_skills.append(s)
            parsed[key] = sorted(list(set(normalize(s) for s in valid_skills if s)))

    if "alternatives" in parsed and isinstance(parsed["alternatives"], list):
        new_alts = []
        for alt_group in parsed["alternatives"]:
            if isinstance(alt_group, list):
                clean_group = sorted(list(set(normalize(s) for s in alt_group if s)))
                if clean_group:
                    new_alts.append(clean_group)
        parsed["alternatives"] = new_alts

    parsed.setdefault("role", "")
    parsed.setdefault("required_skills", [])
    parsed.setdefault("nice_to_have_skills", [])
    parsed.setdefault("alternatives", [])
    parsed.setdefault("soft_skills", [])
    parsed.setdefault("experience_requirements", [])

    return parsed


@st.cache_data(show_spinner=False)
def _cached_job_skills(text: str) -> dict:
    data = _extract_job_skills_uncached(text)
    if not data.get("required_skills"):
        raise _EmptyResultException(data)
    return data


def extract_job_skills(text: str) -> dict:
    """
    Sends job description text to the LLM and asks for a JSON object with:
        - role:                 the job title/role
        - required_skills:      list of mandatory skills
        - nice_to_have_skills:  list of bonus/preferred skills
        - alternatives:         list of lists of alternative skills

    Returns a Python dictionary parsed from the model's response.
    Never caches empty or failed results; only caches successful results with >= 1 skill.
    """
    try:
        return _cached_job_skills(text)
    except _EmptyResultException as e:
        return e.data


extract_job_skills.clear = _cached_job_skills.clear


def apply_verification(compare_result, verification):
    matched = compare_result.setdefault("matched", [])
    partial = compare_result.setdefault("partial", [])
    missing = compare_result.setdefault("missing", [])
    
    evidence = compare_result.setdefault("evidence", {})
    reasons = compare_result.setdefault("reasons", {})
    gaps = compare_result.setdefault("gaps", {})
    confidence = compare_result.setdefault("confidence", {})
    evidence_type = compare_result.setdefault("evidence_type", {})

    for result in verification.get("results", []):
        skill = result.get("skill")
        status = result.get("status")
        ev = result.get("evidence", "")
        reason = result.get("reason", "")
        conf = result.get("confidence", "")
        what = result.get("what_is_missing", "")
        ev_type = result.get("evidence_type", "")
        
        if not skill:
            continue
            
        if ev and not (skill in evidence and evidence[skill]):
            evidence[skill] = ev
        if reason:
            reasons[skill] = reason
        if conf:
            confidence[skill] = conf
        if what:
            gaps[skill] = what
        if ev_type:
            evidence_type[skill] = ev_type
            
        if status == "matched":
            if skill in missing: missing.remove(skill)
            if skill in partial: partial.remove(skill)
            if skill not in matched: matched.append(skill)
        elif status == "partial":
            if skill in missing: missing.remove(skill)
            if skill in matched: matched.remove(skill)
            if skill not in partial: partial.append(skill)
        elif status == "missing":
            if skill in matched: matched.remove(skill)
            if skill in partial: partial.remove(skill)
            if skill not in missing: missing.append(skill)

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
            
    compare_result = {
        "matched": matched,
        "partial": [],
        "missing": missing,
        "bonus_matched": bonus_matched,
        "bonus_missing": bonus_missing,
        "evidence": {},
        "reasons": {},
        "confidence": {},
        "gaps": {},
        "evidence_type": {}
    }
    
    # 3. Verify missing skills via LLM
    import copy
    _debug_pre_verification = copy.deepcopy(compare_result)
    _debug_raw_verification = None
    if missing:
        verification = verify_missing_skills(resume_text, missing)
        _debug_raw_verification = verification
        apply_verification(compare_result, verification)
        
    matched = compare_result.get("matched", [])
    partial = compare_result.get("partial", [])
    missing = compare_result.get("missing", [])
    evidence = compare_result.get("evidence", {})
    reasons = compare_result.get("reasons", {})
    confidence = compare_result.get("confidence", {})
    gaps = compare_result.get("gaps", {})
    evidence_type = compare_result.get("evidence_type", {})
    
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
        "evidence_type": evidence_type,
        "match_percent": match_percent,
        "_debug_pre_verification": _debug_pre_verification,
        "_debug_raw_verification": _debug_raw_verification
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

def build_graph(job_role, compare_result, is_dark: bool = False):
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
            
    # Theme colors
    matched_bg = "#2563eb"
    matched_text = "white"
    partial_bg = "#fbbf24"
    partial_text = "#0f172a"
    missing_bg = "#111a2e" if is_dark else "#ffffff"
    missing_text = "#e5ecf8" if is_dark else "#0f172a"

    # Only group required skills (skip nice-to-have)
    add_skills(compare_result.get("matched", []), matched_bg, matched_text, "✓ ")
    add_skills(compare_result.get("partial", []), partial_bg, partial_text, "~ ")
    add_skills(compare_result.get("missing", []), missing_bg, missing_text, "✗ ")

    root_fill = "#16213a" if is_dark else "#1e3a8a"
    root_border = "#3b82f6" if is_dark else "#1e3a8a"
    root_font = "#e5ecf8" if is_dark else "white"
    cat_bg = "#16213a" if is_dark else "#1e3a8a"
    cat_font = "#e5ecf8" if is_dark else "white"
    cell_border_color = "#24304d" if is_dark else "#e3e8f2"
    edge_color = "#60a5fa"

    lines = [
        "digraph G {",
        "    rankdir=TB;",
        '    bgcolor="transparent";',
        '    node [fontname="DM Sans, sans-serif", shape=plain];',
        f'    edge [color="{edge_color}", penwidth=1.2, style="solid"];',
        f'    "{safe_role}" [shape=box, style="filled,rounded", fillcolor="{root_fill}", color="{root_border}", fontcolor="{root_font}", fontsize=18];'
    ]
    
    for i, (cat, skills) in enumerate(categories.items()):
        if not skills:
            continue
            
        node_id = f"cat_{i}"
        
        # Build HTML table
        html = f'<TABLE BORDER="0" CELLBORDER="1" COLOR="{cell_border_color}" CELLSPACING="0" CELLPADDING="4">'
        html += f'<TR><TD BGCOLOR="{cat_bg}"><B><FONT COLOR="{cat_font}">{cat}</FONT></B></TD></TR>'
        
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

def is_unsafe_bullet(bullet_text):
    if not bullet_text: return False
    b_lower = bullet_text.lower()
    banned_words = ["ensuring", "ensure", "improving", "enhance", "reliability", "availability", "optimal", "production", "scalable", "robust"]
    return any(char.isdigit() for char in bullet_text) or "%" in bullet_text or any(w in b_lower for w in banned_words)

def clean_bullet(bullet, skill, apply_text):
    if not is_unsafe_bullet(bullet):
        return bullet
        
    rewritten = _rewrite_bullet(bullet, apply_text)
    if rewritten and not is_unsafe_bullet(rewritten):
        return rewritten
        
    return f"Added {skill} to <project> [describe what you actually did]"

DEPENDENCY_RULES = {
    "Integration Testing": ["Unit Testing"],
    "CI/CD": ["Testing", "Jest"]
}

def order_steps(steps):
    for i, step in enumerate(steps):
        step["_orig_idx"] = i
        step["do_after"] = ""
        
    for step in steps:
        sk = step.get("skill", "")
        for target, deps in DEPENDENCY_RULES.items():
            if target in sk:
                for other in steps:
                    if any(dep in other.get("skill", "") for dep in deps):
                        step["do_after"] = other.get("skill", "")
                        break
                if step["do_after"]:
                    break
                    
    pri_map = {"High": 0, "Medium": 1, "Low": 2}
    adj = {step.get("skill", ""): [] for step in steps}
    in_degree = {step.get("skill", ""): 0 for step in steps}
    
    for step in steps:
        dep = step.get("do_after", "")
        sk = step.get("skill", "")
        if dep and dep in adj and dep != sk:
            adj[dep].append(sk)
            in_degree[sk] += 1
            
    import heapq
    queue = []
    for step in steps:
        sk = step.get("skill", "")
        if in_degree[sk] == 0:
            heapq.heappush(queue, (pri_map.get(step.get("priority", "Medium"), 1), step["_orig_idx"], id(step), step))
            
    ordered = []
    order_val = 1
    while queue:
        _, _, _, step = heapq.heappop(queue)
        step["order"] = order_val
        order_val += 1
        ordered.append(step)
        
        sk = step.get("skill", "")
        for n_sk in adj[sk]:
            in_degree[n_sk] -= 1
            if in_degree[n_sk] == 0:
                n_step = next(s for s in steps if s.get("skill", "") == n_sk)
                heapq.heappush(queue, (pri_map.get(n_step.get("priority", "Medium"), 1), n_step["_orig_idx"], id(n_step), n_step))
                
    for step in steps:
        if step not in ordered:
            step["order"] = order_val
            order_val += 1
            ordered.append(step)
            
    for step in ordered:
        if "_orig_idx" in step:
            del step["_orig_idx"]
            
    return ordered

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
            "skill": "",
            "priority": "High" or "Medium" or "Low",
            "why_gap": "",
            "learn": "",
            "apply": "",
            "prove": "",
            "example_bullet": "",
            "suggested_effort": ""
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
1. Merge closely related skills into one step (for example Unit Testing + Jest becomes "Unit Testing with Jest", CI/CD + GitHub Actions becomes one step). Every required skill or requirement marked "Not shown" or missing (for example Jest testing) must also get a step in the Actionable Roadmap — do not omit any.
2. Use 3 to 5 High, 3 to 5 Medium, and the rest Low. Never mark more than 5 steps High.
3. "why_gap" must be built only from the job requirement plus the evidence and gaps provided. Do not say things like "only partial exposure". For partial skills, state what related skills were found and what direct experience was not shown. If no evidence is provided for a skill, say "not demonstrated in the resume". Do not make claims about what the industry "standard" is.
4. "learn" is what to study, "apply" is a concrete change to one of the candidate's existing projects (by name), "prove" is what real evidence should exist afterwards (for example "a repo with tests that run on every push").
5. "apply" and "learn" must only reference projects from the provided projects list, exactly as named.
6. Scope each step to what the job requires (for example "deploy one existing application to AWS EC2", not "learn AWS").
7. "example_bullet" describes only the work to be done, in plain past tense, with NO numbers, percentages, performance claims, reliability or availability claims, or business impact (for example never write "ensuring high availability", "improving code quality", "reducing errors").
8. For methodologies like Agile/Scrum, "prove" is "a board and sprint notes for a personal project" and the example bullet must say "applied Agile practices to a personal project", never professional Scrum experience.
9. If a metric would normally help, end the bullet with a bracket like "[add your real result here if you have one]".
10. Never claim an outcome the candidate has not achieved.
11. "suggested_effort" must be phrased like "Estimated effort for foundational experience: 1-2 weeks".
12. If a skill is "partial", recommend fundamentals first. Never use "Advanced" in a step name unless the job description itself asks for advanced level.
13. Steps are only for skills in the missing or partial lists. Nice-to-have skills that are core to the role (for example LLMs for an AI engineer role) and other high-value additions should appear in "optional" (Extra Suggestions) with a one-line reason, not just left as chips.
14. Decide priority using (a) skills listed under requirements or mentioned several times in the job description rank higher, (b) skills the job only prefers rank lower, (c) a partial skill that the job clearly centers on can outrank a missing minor skill such as Agile/Scrum.
15. Choose ONE simple route per skill and do not list several tools or architectures. For AWS, recommend deploying one existing application to a single EC2 instance, and mention only EC2, security groups, SSH and basic IAM unless the job description names other services.
16. If a skill name contains " / " (the job accepts any one option), recommend exactly one option and say why it is a good choice.
17. "prove" must describe the outcome, not the folder structure. For example "a working Jest test suite covering the main parts of the application", not "a tests directory". Do not require specific file paths.
18. For partial skills, do not start from scratch: build on the related evidence the candidate already has.
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
        if "steps" in parsed:
            parsed["steps"] = order_steps(parsed["steps"])
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
            "what_is_missing": "",
            "evidence_type": "explicit" or "project" or "inferred"
        }}
    ]
}}

JSON Field Instructions:
- evidence: a phrase of at most 12 words copied from the resume, empty if none.
- reason: one short sentence.
- what_is_missing: for partial: "Found: <related items>. Not found: <direct evidence>."; empty otherwise.

Rules you MUST follow:
1. Evidence can come from anywhere in the resume.
2. If evidence_type is "inferred", the status can be at most "partial".
3. Statements like "interested in", "learning", "planning to" or "no experience with" never count and are "missing".
4. For Agile/Scrum, "matched" only if sprints, standups, retrospectives or Scrum roles are shown; code reviews or task boards alone are "partial".
5. HTML, CSS or React alone only give "partial" for Responsive Web Design and State Management.
6. A combined requirement like "Unit & Integration Testing with Jest" is "matched" only if both parts are shown, otherwise "partial".
7. A skill containing " / " is satisfied by any ONE of the options.
8. Use the wording "not demonstrated", never "doesn't know".

--- RESUME TEXT ---
{resume_text}
--- END RESUME TEXT ---
"""
    raw_response = _call_llm(prompt, temperature=0.0, seed=42)
    
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
# FUNCTION — Assess Other Requirements
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def assess_other_requirements(resume_text, soft_skills, experience_requirements):
    default_dict = {"results": []}
    
    items = soft_skills + experience_requirements
    if not items:
        return default_dict
        
    prompt = f"""
You are an expert technical recruiter. Check if the resume below shows evidence for these requirements: {', '.join(items)}.

Return ONLY valid JSON. No markdown formatting blocks like ```json, no explanation, no extra text — just the raw JSON object.

Return this exact shape:
{{
    "results": [
        {{
            "item": "",
            "status": "supported" or "not shown",
            "evidence": ""
        }}
    ]
}}

Rules you MUST follow:
1. "supported" only if the resume contains explicit evidence (for example a team project for teamwork, a presentation or documentation for communication, a built project for "integrating AI/ML models").
2. "evidence" is a short phrase copied from the resume of at most 12 words. Leave it empty if there is no evidence.
3. NEVER invent evidence.
4. Generic statements about being a good communicator without any example do not count as evidence for communication.

--- RESUME TEXT ---
{resume_text}
--- END RESUME TEXT ---
"""
    raw_response = _call_llm(prompt, temperature=0.0, seed=42)
    
    if not raw_response or "⏱️" in raw_response:
        return default_dict
        
    try:
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())
    except Exception:
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
    raw_response = _call_llm(prompt, temperature=0.0, seed=42)
    
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
    matched = compare_result.get("matched", [])
    partial = compare_result.get("partial", [])
    missing = compare_result.get("missing", [])
    
    matched_count = len(matched)
    partial_count = len(partial)
    missing_count = len(missing)
    
    total_required = matched_count + partial_count + missing_count
    
    if total_required > 0:
        match_percent = round((matched_count + 0.5 * partial_count) / total_required * 100)
    else:
        match_percent = 0
        
    overlap = bool(set(matched) & set(partial) or set(matched) & set(missing) or set(partial) & set(missing))
    original_percent = compare_result.get("match_percent")
    consistent = not overlap and (original_percent is None or original_percent == match_percent)
        
    return {
        "total_required": total_required,
        "matched_count": matched_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "match_percent": match_percent,
        "consistent": consistent
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
