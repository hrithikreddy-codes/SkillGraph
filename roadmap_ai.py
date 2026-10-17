"""
roadmap_ai.py — AI-generated personalized career roadmaps via Groq.
"""

import json
import time
import sys
import types
import groq
import httpx
from groq import Groq
import analyzer
from analyzer import _get_api_keys, _GROQ_MODELS, REASON_MESSAGES


class _RoadmapAiModule(types.ModuleType):
    @property
    def last_rate_limit_at(self):
        return analyzer.last_rate_limit_at

    @last_rate_limit_at.setter
    def last_rate_limit_at(self, val):
        analyzer.last_rate_limit_at = float(val)


sys.modules[__name__].__class__ = _RoadmapAiModule


def __getattr__(name):
    if name == "last_rate_limit_at":
        return analyzer.last_rate_limit_at
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


_last_call_meta = {"attempts": 1, "key_idx": 0, "retry_after": None}


class _CallResult(tuple):
    def __new__(cls, content, err, retry_after=None):
        obj = super().__new__(cls, (content, err))
        obj.retry_after = retry_after
        return obj


def _call_single_key(api_key, prompt, temperature=0.2, check_cooldown=True, start_time=None):
    """
    Attempts to call Groq with a single API key across _GROQ_MODELS with a 25-second timeout.
    Returns (content, error_type) where error_type can be 'timeout', 'rate_limit', 'other', or None.
    Also provides .retry_after on the return value if rate-limited.
    """
    if check_cooldown:
        analyzer.wait_for_rate_limit_cooldown(start_time=start_time)

    try:
        client = Groq(api_key=api_key, timeout=25.0)
    except Exception as e:
        err_msg = str(e).lower()
        if isinstance(e, (groq.APITimeoutError, httpx.TimeoutException, TimeoutError)) or "timeout" in err_msg or "timed out" in err_msg:
            return _CallResult(None, "timeout", None)
        return _CallResult(None, "other", None)

    hit_rate_limit = False
    rate_limit_err = None
    for model_name in _GROQ_MODELS:
        try:
            kwargs = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 2048,
                "timeout": 25,
            }
            completion = client.chat.completions.create(**kwargs)
            return _CallResult(completion.choices[0].message.content, None, None)
        except Exception as e:
            err_msg = str(e).lower()
            if isinstance(e, (groq.APITimeoutError, httpx.TimeoutException, TimeoutError)) or "timeout" in err_msg or "timed out" in err_msg:
                return _CallResult(None, "timeout", None)
            if isinstance(e, groq.RateLimitError) or "429" in err_msg or "rate limit" in err_msg or "quota" in err_msg:
                hit_rate_limit = True
                rate_limit_err = e
                continue
            if "404" in err_msg or "does not exist" in err_msg:
                continue
            return _CallResult(None, "other", None)

    if hit_rate_limit:
        analyzer.last_rate_limit_at = time.time()
        retry_after = analyzer._extract_retry_after(rate_limit_err) if rate_limit_err else None
        return _CallResult(None, "rate_limit", retry_after)
    return _CallResult(None, "other", None)


def _execute_groq_call(prompt, keys, start_key_idx=0, max_attempts=2, start_time=None):
    """
    Executes Groq API call with single rate_limit or timeout retry:
    - On rate limit, reads Retry-After header if present. Waits that long, capped at 20s.
      If no header, waits 15 seconds. Never blocks longer than 30 seconds in total.
      Retries once on the next key (or the same key if only one).
    - On timeout, retries once with the next key (or same key if only 1).
    - Respects max_attempts (at most 2 attempts in total).
    - Returns (raw_text, error_reason)
    """
    if start_time is None:
        start_time = time.time()

    if not keys:
        return None, "no_key"

    current_idx = start_key_idx % len(keys)
    res = _call_single_key(keys[current_idx], prompt, check_cooldown=True, start_time=start_time)
    content, err = res[0], res[1]
    retry_after = getattr(res, "retry_after", None) or (res[2] if len(res) > 2 else None)
    _last_call_meta["attempts"] = 1
    _last_call_meta["key_idx"] = current_idx
    _last_call_meta["retry_after"] = retry_after

    if max_attempts >= 2:
        if err == "rate_limit":
            if retry_after is not None:
                wait_time = min(20.0, max(0.0, float(retry_after)))
            else:
                wait_time = 15.0

            remaining_budget = max(0.0, 30.0 - (time.time() - start_time))
            wait_time = min(wait_time, remaining_budget)
            if wait_time > 0:
                time.sleep(wait_time)

            next_idx = (current_idx + 1) % len(keys)
            res_retry = _call_single_key(keys[next_idx], prompt, check_cooldown=False, start_time=start_time)
            content_retry, err_retry = res_retry[0], res_retry[1]
            _last_call_meta["attempts"] = 2
            _last_call_meta["key_idx"] = next_idx
            _last_call_meta["retry_after"] = getattr(res_retry, "retry_after", None)
            if content_retry is not None:
                return content_retry, None
            return None, err_retry or "rate_limit"

        elif err == "timeout":
            next_idx = (current_idx + 1) % len(keys)
            res_retry = _call_single_key(keys[next_idx], prompt, check_cooldown=True, start_time=start_time)
            content_retry, err_retry = res_retry[0], res_retry[1]
            _last_call_meta["attempts"] = 2
            _last_call_meta["key_idx"] = next_idx
            _last_call_meta["retry_after"] = getattr(res_retry, "retry_after", None)
            if content_retry is not None:
                return content_retry, None
            return None, err_retry or "timeout"

    if err is not None:
        return None, err
    return content, None


def _parse_and_validate(raw_response, hpw):
    """
    Parses and validates Groq raw response.
    Returns (validated_phases, error_reason)
    """
    if not raw_response or not isinstance(raw_response, str):
        return None, "bad_json"

    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except Exception:
        return None, "bad_json"

    total_months = None
    raw_phases = None

    if isinstance(data, dict):
        total_months = data.get("total_months")
        for key in ("phases", "roadmap", "steps", "data"):
            if key in data and isinstance(data[key], list):
                raw_phases = data[key]
                break
    elif isinstance(data, list):
        raw_phases = data
        for item in data:
            if isinstance(item, dict) and "total_months" in item:
                total_months = item["total_months"]
                break

    if total_months is None:
        return None, "validation: missing total_months"
    if not isinstance(total_months, int):
        try:
            total_months = int(total_months)
        except (ValueError, TypeError):
            return None, "validation: total_months must be an integer"
    if total_months <= 0:
        return None, "validation: total_months must be positive"

    if not isinstance(raw_phases, list):
        return None, "validation: phases must be a list"
    if len(raw_phases) != 5:
        return None, f"validation: expected 5 phases, got {len(raw_phases)}"

    if total_months == 6:
        default_weeks = [4, 4, 8, 4, 4]
    elif total_months == 9:
        default_weeks = [8, 8, 8, 4, 8]
    elif total_months == 18:
        default_weeks = [12, 12, 16, 16, 16]
    else:
        default_weeks = [8, 8, 8, 12, 12]

    validated_phases = []
    for i, phase in enumerate(raw_phases):
        if not isinstance(phase, dict):
            return None, f"validation: phase {i+1} must be an object"

        title = phase.get("title")
        when = phase.get("when")
        blurb = phase.get("blurb")
        goal = phase.get("goal")
        resources = phase.get("resources")
        tags = phase.get("tags")

        if not (isinstance(title, str) and title.strip()):
            return None, f"validation: phase {i+1} missing title"
        if not (isinstance(when, str) and when.strip()):
            return None, f"validation: phase {i+1} missing when"
        if not (isinstance(blurb, str) and blurb.strip()):
            return None, f"validation: phase {i+1} missing blurb"

        clean_goal = goal.strip() if isinstance(goal, str) and goal.strip() else ""

        clean_resources = []
        if isinstance(resources, list):
            clean_resources = [str(r).strip() for r in resources if str(r).strip()]
        elif isinstance(resources, str) and resources.strip():
            clean_resources = [str(r).strip() for r in resources.split(",") if str(r).strip()]

        hours_val = phase.get("hours")
        clean_hours = None
        if isinstance(hours_val, (int, float)):
            clean_hours = int(hours_val)
        elif isinstance(hours_val, str) and hours_val.strip().isdigit():
            clean_hours = int(hours_val.strip())
        if clean_hours is None or clean_hours <= 0:
            clean_hours = int(round(hpw * default_weeks[i]))

        raw_groups = phase.get("groups")
        clean_groups = []

        if isinstance(raw_groups, list) and len(raw_groups) > 0:
            for grp in raw_groups:
                if not isinstance(grp, dict):
                    continue
                grp_name = str(grp.get("name", "")).strip()
                grp_tasks = grp.get("tasks", [])
                if isinstance(grp_tasks, list):
                    valid_tasks = [str(t).strip() for t in grp_tasks if str(t).strip()]
                    if valid_tasks:
                        clean_groups.append({
                            "name": grp_name,
                            "tasks": valid_tasks
                        })

        if not clean_groups and "tasks" in phase and isinstance(phase["tasks"], list):
            old_tasks = [str(t).strip() for t in phase["tasks"] if str(t).strip()]
            if old_tasks:
                clean_groups = [{
                    "name": "",
                    "tasks": old_tasks
                }]

        if not clean_groups:
            return None, f"validation: phase {i+1} missing valid groups or tasks"

        flattened_tasks = [t for g in clean_groups for t in g["tasks"]]
        if not flattened_tasks:
            return None, f"validation: phase {i+1} has no tasks"

        if i == 0:
            if not isinstance(tags, list):
                clean_tags = []
            else:
                clean_tags = [str(t).strip() for t in tags if str(t).strip()]
        else:
            clean_tags = []

        validated_phases.append({
            "title": title.strip(),
            "when": when.strip(),
            "blurb": blurb.strip(),
            "goal": clean_goal,
            "resources": clean_resources,
            "hours": clean_hours,
            "total_months": total_months,
            "groups": clean_groups,
            "tasks": flattened_tasks,
            "tags": clean_tags
        })

    return validated_phases, None


def generate_roadmap(education, interest_label, career, skills, strengths, hours_per_week=8):
    """
    Generates a personalized 5-phase career roadmap using Groq sized by study hours.

    Args:
        education: Current education level (e.g., "School (under 18)", "B.Tech / Engineering").
        interest_label: Field of interest (e.g., "Software Development", "Artificial Intelligence").
        career: Target career/role (e.g., "Full Stack Developer", "AI Engineer").
        skills: List or collection of skills the user already knows.
        strengths: List of the user's main personal/professional strengths.
        hours_per_week: Number of hours per week the user can study (int or float).

    Returns:
        A list of 5 dictionaries with keys:
            - title (str)
            - when (str)
            - blurb (str)
            - goal (str)
            - resources (list of strings)
            - hours (int)
            - total_months (int)
            - groups (list of dicts with 'name' and 'tasks')
            - tasks (list of strings)
            - tags (list of strings for phase 1; empty list for phases 2-5)
        Returns None on any error or parsing failure.
    """
    start_time = time.time()
    _last_call_meta["attempts"] = 0
    _last_call_meta["key_idx"] = None
    try:
        keys = _get_api_keys("GROQ_API_KEYS")
        if not keys:
            reason = "no_key"
            elapsed = time.time() - start_time
            print(f"{reason} (attempt 0, key index None, elapsed {elapsed:.2f}s)")
            return None, reason

        try:
            hpw = float(hours_per_week)
        except (ValueError, TypeError):
            hpw = 8.0

        if hpw >= 25:
            target_months = 6
            phase_weeks = [4, 4, 8, 4, 4]
            phase_whens = ["Month 1", "Month 2", "Months 3-4", "Month 5", "Month 6"]
        elif hpw >= 10:
            target_months = 9
            phase_weeks = [8, 8, 8, 4, 8]
            phase_whens = ["Months 1-2", "Months 3-4", "Months 5-6", "Month 7", "Months 8-9"]
        elif hpw >= 5:
            target_months = 12
            phase_weeks = [8, 8, 8, 12, 12]
            phase_whens = ["Months 1-2", "Months 3-4", "Months 5-6", "Months 7-9", "Months 10-12"]
        else:
            target_months = 18
            phase_weeks = [12, 12, 16, 16, 16]
            phase_whens = ["Months 1-3", "Months 4-6", "Months 7-10", "Months 11-14", "Months 15-18"]

        phase_hours = [int(round(hpw * w)) for w in phase_weeks]

        if isinstance(skills, list):
            clean_skills = [str(s).strip() for s in skills if str(s).strip()]
        elif isinstance(skills, str) and skills.strip() and skills.strip().lower() != "none":
            clean_skills = [str(s).strip() for s in skills.split(",") if str(s).strip()]
        else:
            clean_skills = []

        skills_str = ", ".join(clean_skills) if clean_skills else "None"
        strengths_str = ", ".join(strengths) if isinstance(strengths, list) and strengths else (str(strengths) if strengths else "None")

        prompt = f"""You are an expert career and learning mentor. Create a personalized career learning roadmap structured into skill groups and sized to the user's weekly study budget.

Candidate Profile:
- Education level: {education}
- Area of interest: {interest_label}
- Target career: {career}
- Weekly study time: {hpw:g} hours/week
- Skills they already have: {skills_str}
- Key strengths: {strengths_str}

Rules:
1. Timeline & Study Budget:
   - Choose total plan length strictly from weekly study hours:
     * 25+ hrs/week -> 6 months
     * 10-24 hrs/week -> 9 months
     * 5-9 hrs/week -> 12 months
     * under 5 hrs/week -> 18 months
     For this candidate ({hpw:g} hrs/week), set "total_months" to {target_months}.
   - Phase "when" labels must start where the previous one ended, never overlap, and add up to total_months ({target_months}).
     Use these exact non-overlapping "when" labels for the 5 phases:
     * Phase 1: "{phase_whens[0]}" ({phase_weeks[0]} weeks)
     * Phase 2: "{phase_whens[1]}" ({phase_weeks[1]} weeks)
     * Phase 3: "{phase_whens[2]}" ({phase_weeks[2]} weeks)
     * Phase 4: "{phase_whens[3]}" ({phase_weeks[3]} weeks)
     * Phase 5: "{phase_whens[4]}" ({phase_weeks[4]} weeks)
   - Phase-level "hours" integer: each phase's hours = hours_per_week x weeks in that phase:
     * Phase 1: {phase_hours[0]} hours ({hpw:g} hrs/wk x {phase_weeks[0]} weeks)
     * Phase 2: {phase_hours[1]} hours ({hpw:g} hrs/wk x {phase_weeks[1]} weeks)
     * Phase 3: {phase_hours[2]} hours ({hpw:g} hrs/wk x {phase_weeks[2]} weeks)
     * Phase 4: {phase_hours[3]} hours ({hpw:g} hrs/wk x {phase_weeks[3]} weeks)
     * Phase 5: {phase_hours[4]} hours ({hpw:g} hrs/wk x {phase_weeks[4]} weeks)

2. Sizing & Task Counts:
   - Sizing effort: assume about 8-10 hours of effort per task for beginners (no listed skills) and 4-8 hours for experienced learners.
   - Number of tasks per phase = phase hours divided by that effort, strictly between 4 and 8 tasks total across 2-3 groups.
   - Low hours -> fewer tasks (towards 4 tasks per phase).
   - High hours -> more or deeper tasks (up to 8 tasks per phase), never padding.

3. Ordering & Field Basics:
   - Field basics (for example typography and color for design; core syntax and dev setup for software) belong in the foundation phase (Phase 1: "Build your foundation"), never later.
   - Later phases must build on the basics established in Phase 1.

4. Phase Groups and Structure:
   - Structure each phase into 2 to 3 groups.
   - Each group must be formatted as: {{"name": "<Specific Skill Area>", "tasks": ["<task 1>", "<task 2>"]}}.
   - Group names must be specific skill areas of the field (for example "Databases", "Networking", "Testing", "API Design", "Typography & Color", "Visual Layout").
   - NEVER use generic group names like "Other", "Skills", "Tasks", "General", or "Misc".
   - Total tasks across the groups in a phase must sum to between 4 and 8 tasks.

5. Task Prefixes, Awareness & Build Limits:
   - Every single task MUST start with "Learn:", "Practice:", "Build:", or "Awareness:" (e.g., "Learn: relational schema design", "Practice: write integration tests", "Build: a REST API with FastAPI", "Awareness: database sharding concepts"). Tasks must be short, concrete, and actionable.
   - At most ONE "Build:" task per phase across all phases.
   - Prefix topics beyond the core of the stated career with "Awareness:" and keep them small. Never make them Build tasks.
   - Heavy items (fixing a bug in a popular library, ML system design questions, sharding) are Awareness-only unless the phase is 100+ hours.

6. Use the exact 5 phase titles in this order:
   - Phase 1: "Build your foundation"
   - Phase 2: "Learn the core skills"
   - Phase 3: "Build real projects"
   - Phase 4: "Gain experience"
   - Phase 5: "Prepare for your career"

7. Education Level & Experience Tasks:
   - For School and Intermediate / 12th learners:
     * Treat the plan as exploration plus college preparation.
     * The last phase ("Prepare for your career") MUST cover choosing a degree and entrance exams, a beginner portfolio, and student-friendly steps (clubs, online contests, internships later).
     * Never ask them to apply for jobs or to prepare professional certifications.
     * Do NOT ask for mastery of advanced enterprise topics (Docker, microservices, CI/CD, system design); mention as awareness only if at all.
   - For Diploma, Degree and B.Tech / Engineering learners:
     * Job applications, internships, technical interview preparation, and production-grade tools are fine.
   - The "Gain experience" phase (Phase 4) needs at least one external, real-world task suited to the learner's level (volunteering, a freelance or class project, a team project, a contest, or an internship), not only work on the learner's own projects:
     * For School and Intermediate learners, use student-friendly external steps such as school tech/science clubs, student hackathons/contests, volunteer websites, or collaborative projects.
     * For Diploma, Degree and B.Tech learners, use an internship, freelance project, open-source team contribution, or collaborative community project.

8. Last Phase Job Market Research & Skill Gap Closing:
   - In Phase 5 ("Prepare for your career"), you MUST include:
     1. One task that researches 3-5 real job postings for the stated career ({career}) and lists the skills they require (e.g., "Practice: research 3-5 real job postings for {career} and list the required skills").
     2. One task that closes the gap with the learner's current skills (e.g., "Practice: identify skill gaps between target job requirements and current skills, and complete targeted projects to close them").

9. Hosting and Tools:
   - Only name hosting platforms and tools with a current free tier (Render, Vercel, Netlify).
   - NEVER mention Heroku.

10. Goal Field:
    - Add one short "goal" field per phase: a one-line outcome saying what the learner can do at the end (e.g., "You can build and deploy a small API", "You can conduct exploratory data analysis on a real-world dataset"). If omitted, it will default to empty.
    - Each phase's "goal" must be achievable by that phase's own tasks. Don't claim more than the tasks produce (for example "two case studies" with only one Build task).

11. Resources Field:
    - Add a "resources" list per phase containing 1-2 real, widely known names (for example "freeCodeCamp", "MDN Web Docs", "Nielsen Norman Group").
    - Names only, no URLs. No parentheses, no notes, no generic phrases like "guides" or "free trials".

12. Handling Existing Skills & Strengths:
    - If the user's skills list is empty or "None", assume a beginner.
    - If the user has existing skills, build on them and say in the Phase 1 blurb which known skills the plan builds on.
    - If the learner listed strengths ({strengths_str}), mention at least one in a phase blurb where it helps.

13. Meaningful Differentiation:
    - Make tasks differ meaningfully by interest ({interest_label}) and target career ({career}). Do NOT reuse generic tasks across fields.

14. Controllable Actions (No Outcome Promises):
    - Do NOT promise outcomes like getting an internship or job. Phrase career tasks strictly as actions the learner controls (e.g., "Practice: apply to 10 internships with tailored resumes", NOT "Get an internship" or "Land a job").

15. Tags:
    - Phase 1 must include a "tags" list with 3-5 key tools, languages, or foundational concepts (e.g., ["Python", "Git", "VS Code"]).
    - Phases 2, 3, 4, and 5 must have an empty "tags" list ([]).

16. Return JSON only with "total_months" integer and "phases" list. No markdown formatting, no code fences (```json ... ```), no introductory or concluding text.

Output format:
{{
  "total_months": {target_months},
  "phases": [
    {{
      "title": "Build your foundation",
      "when": "{phase_whens[0]}",
      "hours": {phase_hours[0]},
      "blurb": "Short summary of what to achieve in this phase (mentioning how a relevant strength helps, and if user had skills, stating which known skills the plan builds on).",
      "goal": "You can write basic scripts and use Git for version control.",
      "resources": ["freeCodeCamp", "MDN Web Docs"],
      "groups": [
        {{
          "name": "Core Programming",
          "tasks": [
            "Learn: language syntax, variables, and control flow",
            "Practice: solve 10 basic algorithm exercises"
          ]
        }},
        {{
          "name": "Developer Environment",
          "tasks": [
            "Learn: terminal commands and VS Code setup",
            "Build: a small command-line utility"
          ]
        }}
      ],
      "tags": ["Tool 1", "Tool 2", "Tool 3"]
    }},
    {{
      "title": "Learn the core skills",
      "when": "{phase_whens[1]}",
      "hours": {phase_hours[1]},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You can build a functional CRUD application with a database.",
      "resources": ["W3Schools", "Harvard CS50"],
      "groups": [
        {{
          "name": "Databases",
          "tasks": [
            "Learn: relational databases and SQL queries",
            "Practice: design a schema with foreign keys"
          ]
        }},
        {{
          "name": "Backend APIs",
          "tasks": [
            "Practice: implement REST endpoints with input validation",
            "Build: a backend API connected to SQLite"
          ]
        }}
      ],
      "tags": []
    }},
    {{
      "title": "Build real projects",
      "when": "{phase_whens[2]}",
      "hours": {phase_hours[2]},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have a full project documented and hosted online.",
      "resources": ["The Odin Project", "Full Stack Open"],
      "groups": [
        {{
          "name": "Project Architecture & Deployment",
          "tasks": [
            "Learn: clean code organization and modular design",
            "Practice: deploy a full-stack project to Render or Vercel",
            "Practice: write comprehensive README documentation"
          ]
        }},
        {{
          "name": "Full-Stack Implementation",
          "tasks": [
            "Practice: implement authentication and user flows",
            "Build: a full-stack project solving a real problem"
          ]
        }}
      ],
      "tags": []
    }},
    {{
      "title": "Gain experience",
      "when": "{phase_whens[3]}",
      "hours": {phase_hours[3]},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have collaborated with other developers on an external codebase.",
      "resources": ["GitHub Skills", "Linux Foundation Mentorship"],
      "groups": [
        {{
          "name": "Testing & Code Quality",
          "tasks": [
            "Learn: automated testing patterns and CI workflows",
            "Practice: write unit and integration test suites"
          ]
        }},
        {{
          "name": "Real-World Collaboration",
          "tasks": [
            "Awareness: large codebase navigation and open source triage",
            "Practice: contribute to an external open-source team project or volunteer organization",
            "Build: collaborate on a feature using pull requests"
          ]
        }}
      ],
      "tags": []
    }},
    {{
      "title": "Prepare for your career",
      "when": "{phase_whens[4]}",
      "hours": {phase_hours[4]},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have an active portfolio and readiness pipeline prepared.",
      "resources": ["Tech Interview Handbook", "LeetCode"],
      "groups": [
        {{
          "name": "Job Market Research & Gap Closing",
          "tasks": [
            "Practice: research 3-5 real job postings for {career} and list the skills they require",
            "Practice: identify skill gaps against target job requirements and complete targeted projects to close them"
          ]
        }},
        {{
          "name": "Portfolio & Career Readiness",
          "tasks": [
            "Practice: write concise project case studies",
            "Build: a clean 1-page portfolio website",
            "Practice: entrance exam prep or technical interview questions suited to your level"
          ]
        }}
      ],
      "tags": []
    }}
  ]
}}
"""

        # Attempt 1
        _last_call_meta["attempts"] = 1
        _last_call_meta["key_idx"] = 0
        raw_text, err = _execute_groq_call(prompt, keys, start_key_idx=0, max_attempts=2, start_time=start_time)
        if err:
            reason = err
            elapsed = time.time() - start_time
            attempt_num = _last_call_meta.get("attempts", 1)
            key_num = _last_call_meta.get("key_idx", 0)
            print(f"{reason} (attempt {attempt_num}, key index {key_num}, elapsed {elapsed:.2f}s)")
            return None, reason

        phases, parse_err = _parse_and_validate(raw_text, hpw)
        if phases:
            return phases, None

        # Check remaining attempts allowed (at most 2 attempts in total)
        attempts_used = _last_call_meta.get("attempts", 1)
        remaining_attempts = 2 - attempts_used

        if remaining_attempts <= 0:
            reason = parse_err or "bad_json"
            elapsed = time.time() - start_time
            key_num = _last_call_meta.get("key_idx", 0)
            print(f"{reason} (attempt {attempts_used}, key index {key_num}, elapsed {elapsed:.2f}s)")
            return None, reason

        # Retry once: on bad_json or validation failure, retry once with an added line "Return valid JSON matching the schema exactly"
        retry_prompt = prompt + "\nReturn valid JSON matching the schema exactly"
        current_key_idx = _last_call_meta.get("key_idx", 0)
        _last_call_meta["attempts"] = 1
        retry_raw_text, retry_err = _execute_groq_call(
            retry_prompt, keys, start_key_idx=current_key_idx, max_attempts=remaining_attempts, start_time=start_time
        )
        total_attempts = attempts_used + _last_call_meta.get("attempts", 1)
        final_key_num = _last_call_meta.get("key_idx", current_key_idx)

        if retry_err:
            reason = retry_err
            elapsed = time.time() - start_time
            print(f"{reason} (attempt {total_attempts}, key index {final_key_num}, elapsed {elapsed:.2f}s)")
            return None, reason

        retry_phases, retry_parse_err = _parse_and_validate(retry_raw_text, hpw)
        if retry_phases:
            return retry_phases, None

        reason = retry_parse_err or parse_err or "bad_json"
        elapsed = time.time() - start_time
        print(f"{reason} (attempt {total_attempts}, key index {final_key_num}, elapsed {elapsed:.2f}s)")
        return None, reason

    except Exception:
        reason = "other"
        elapsed = time.time() - start_time
        attempt_num = _last_call_meta.get("attempts", 0)
        key_num = _last_call_meta.get("key_idx", None)
        print(f"{reason} (attempt {attempt_num}, key index {key_num}, elapsed {elapsed:.2f}s)")
        return None, reason
