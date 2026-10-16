"""
roadmap_ai.py — AI-generated personalized career roadmaps via Groq.
"""

import json
import time
from groq import Groq
from analyzer import _get_api_keys, _GROQ_MODELS


def _call_single_key(api_key, prompt, temperature=0.2):
    """
    Attempts to call Groq with a single API key across _GROQ_MODELS.
    Returns (content, error_type) where error_type can be 'rate_limit', 'other', or None.
    """
    try:
        client = Groq(api_key=api_key)
    except Exception:
        return None, "other"

    hit_rate_limit = False
    for model_name in _GROQ_MODELS:
        try:
            kwargs = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 2048,
                "timeout": 60,
            }
            completion = client.chat.completions.create(**kwargs)
            return completion.choices[0].message.content, None
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "rate limit" in err_msg or "quota" in err_msg:
                hit_rate_limit = True
                continue
            if "404" in err_msg or "does not exist" in err_msg:
                continue
            return None, "other"

    if hit_rate_limit:
        return None, "rate_limit"
    return None, "other"


def _execute_groq_call(prompt, keys, start_key_idx=0):
    """
    Executes Groq API call with single rate_limit retry:
    - On rate limit, waits 2 seconds and retries once with the next key (or retries same key if only 1).
    - Returns (raw_text, error_reason)
    """
    current_idx = start_key_idx % len(keys)
    content, err = _call_single_key(keys[current_idx], prompt)
    if err == "rate_limit":
        time.sleep(2)
        next_idx = (current_idx + 1) % len(keys)
        content_retry, err_retry = _call_single_key(keys[next_idx], prompt)
        if content_retry is not None:
            return content_retry, None
        return None, err_retry or "rate_limit"
    elif err is not None:
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

    validated_phases = []
    for i, phase in enumerate(raw_phases):
        if not isinstance(phase, dict):
            return None, f"validation: phase {i+1} must be an object"

        title = phase.get("title")
        when = phase.get("when")
        blurb = phase.get("blurb")
        goal = phase.get("goal")
        tags = phase.get("tags")

        if not (isinstance(title, str) and title.strip()):
            return None, f"validation: phase {i+1} missing title"
        if not (isinstance(when, str) and when.strip()):
            return None, f"validation: phase {i+1} missing when"
        if not (isinstance(blurb, str) and blurb.strip()):
            return None, f"validation: phase {i+1} missing blurb"

        clean_goal = goal.strip() if isinstance(goal, str) and goal.strip() else f"Achieve key milestone for {title.strip()}."

        hours_val = phase.get("hours")
        clean_hours = None
        if isinstance(hours_val, (int, float)):
            clean_hours = int(hours_val)
        elif isinstance(hours_val, str) and hours_val.strip().isdigit():
            clean_hours = int(hours_val.strip())
        if clean_hours is None or clean_hours <= 0:
            clean_hours = int(hpw * 8)

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
            - hours (int)
            - total_months (int)
            - groups (list of dicts with 'name' and 'tasks')
            - tasks (list of strings)
            - tags (list of strings for phase 1; empty list for phases 2-5)
        Returns None on any error or parsing failure.
    """
    try:
        keys = _get_api_keys("GROQ_API_KEYS")
        if not keys:
            reason = "no_key"
            print(reason)
            return None, reason

        try:
            hpw = float(hours_per_week)
        except (ValueError, TypeError):
            hpw = 8.0

        if hpw >= 25:
            target_months = 6
            when_guide = 'Phase 1: "Weeks 1-4" (or "Month 1"), Phase 2: "Month 2", Phase 3: "Months 3-4", Phase 4: "Month 5", Phase 5: "Month 6"'
        elif hpw >= 10:
            target_months = 9
            when_guide = 'Phase 1: "Weeks 1-6" (or "Months 1-2"), Phase 2: "Months 2-4", Phase 3: "Months 4-6", Phase 4: "Months 6-7", Phase 5: "Months 8-9"'
        elif hpw >= 5:
            target_months = 12
            when_guide = 'Phase 1: "Weeks 1-6", Phase 2: "Months 2-4", Phase 3: "Months 4-6", Phase 4: "Months 6-9", Phase 5: "Months 9-12"'
        else:
            target_months = 18
            when_guide = 'Phase 1: "Months 1-3", Phase 2: "Months 3-6", Phase 3: "Months 6-10", Phase 4: "Months 10-14", Phase 5: "Months 14-18"'

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
   - Total study budget = hours_per_week x weeks in each phase. Size each phase's tasks to fit that budget.
   - Choose total plan length strictly from weekly study hours:
     * 25+ hrs/week -> 6 months
     * 10-24 hrs/week -> 9 months
     * 5-9 hrs/week -> 12 months
     * under 5 hrs/week -> 18 months
     For this candidate ({hpw:g} hrs/week), set "total_months" to {target_months}.
   - Split the total plan length across the same 5 phases and write the "when" labels to match (e.g. {when_guide}).
   - Add a phase-level "hours" integer: a rough total effort that must not exceed hours_per_week x weeks in that phase.

2. Phase Groups and Structure:
   - Change each phase from a flat "tasks" list to "groups": include 2 to 3 groups per phase.
   - Each group must be formatted as: {{"name": "<Specific Skill Area>", "tasks": ["<task 1>", "<task 2>"]}}.
   - Each group must contain 2 to 3 tasks.
   - Group names must be specific skill areas of the field (for example "Databases", "Networking", "Testing", "API Design", "Frontend State", "Security Hardening").
   - NEVER use generic group names like "Other", "Skills", "Tasks", "General", or "Misc".

3. Task Prefixes & Build Limits:
   - Every single task MUST start with "Learn:", "Practice:", or "Build:" (e.g., "Learn: relational schema design", "Practice: write integration tests", "Build: a REST API with FastAPI"). Tasks must be short, concrete, and actionable.
   - At most ONE "Build:" task per phase unless the phase is longer than 2 months (phases longer than 2 months may contain up to 2 Build tasks).

4. Use the exact 5 phase titles in this order:
   - Phase 1: "Build your foundation"
   - Phase 2: "Learn the core skills"
   - Phase 3: "Build real projects"
   - Phase 4: "Gain experience"
   - Phase 5: "Prepare for your career"

5. Learner Tier & Difficulty:
   - For starter-tier learners (School, Intermediate / 12th, or beginners): provide exploratory, beginner-friendly steps with free tools. Do NOT ask for mastery of advanced topics (Docker, microservices, CI/CD, system design) in the first 12 months; mention them as awareness only (e.g., "Learn: awareness of containerization concepts and what Docker solves").
   - For college / B.Tech / Degree learners: focus on production-grade tools, deeper computer science fundamentals, and technical interview preparation.

6. Handling existing skills:
   - If the user's skills list is empty or "None", assume a beginner.
   - If the user has existing skills, build on them and say in the Phase 1 blurb which known skills the plan builds on.

7. Make tasks differ meaningfully by interest ({interest_label}) and target career ({career}). Do NOT reuse generic tasks across fields.

8. Goal field:
   - Add one short "goal" field per phase: a one-line outcome the learner can check (e.g., "You can build and deploy a small API", "You can conduct exploratory data analysis on a real-world dataset").

9. Controllable actions (no outcome promises):
   - Do NOT promise outcomes like getting an internship or job. Phrase career tasks strictly as actions the learner controls (e.g., "Practice: apply to 10 internships with tailored resumes", NOT "Get an internship" or "Land a job").

10. Tags:
   - Phase 1 must include a "tags" list with 3-5 key tools, languages, or foundational concepts (e.g., ["Python", "Git", "VS Code"]).
   - Phases 2, 3, 4, and 5 must have an empty "tags" list ([]).

11. Return JSON only with "total_months" integer and "phases" list. No markdown formatting, no code fences (```json ... ```), no introductory or concluding text.

Output format:
{{
  "total_months": {target_months},
  "phases": [
    {{
      "title": "Build your foundation",
      "when": "...",
      "hours": {int(hpw * 6)},
      "blurb": "Short summary of what to achieve in this phase (if user had skills, explicitly state which known skills the plan builds on).",
      "goal": "You can write basic scripts and use Git for version control.",
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
      "when": "...",
      "hours": {int(hpw * 10)},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You can build a functional CRUD application with a database.",
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
      "when": "...",
      "hours": {int(hpw * 8)},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have 2 full projects documented and hosted online.",
      "groups": [
        {{
          "name": "Project Architecture",
          "tasks": [
            "Learn: clean code organization and modular design",
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
      "when": "...",
      "hours": {int(hpw * 12)},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have collaborated with other developers on a shared codebase.",
      "groups": [
        {{
          "name": "Testing & Code Quality",
          "tasks": [
            "Learn: automated testing patterns and CI workflows",
            "Practice: write unit and integration test suites"
          ]
        }},
        {{
          "name": "Open Source Collaboration",
          "tasks": [
            "Practice: contribute a bug fix or docs to an open repo",
            "Build: collaborate on a feature using pull requests"
          ]
        }}
      ],
      "tags": []
    }},
    {{
      "title": "Prepare for your career",
      "when": "...",
      "hours": {int(hpw * 12)},
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have an active portfolio and application pipeline ready.",
      "groups": [
        {{
          "name": "Portfolio & Branding",
          "tasks": [
            "Practice: write concise project case studies",
            "Build: a clean 1-page portfolio website"
          ]
        }},
        {{
          "name": "Interview Preparation",
          "tasks": [
            "Practice: solve 20 technical interview practice questions",
            "Practice: apply to 10 internships or junior roles with tailored resumes"
          ]
        }}
      ],
      "tags": []
    }}
  ]
}}
"""

        # Attempt 1
        raw_text, err = _execute_groq_call(prompt, keys)
        if err:
            reason = err
            print(reason)
            return None, reason

        phases, parse_err = _parse_and_validate(raw_text, hpw)
        if phases:
            return phases, None

        # Retry once: on bad_json or validation failure, retry once with the same keys and an added line "Return valid JSON matching the schema exactly"
        retry_prompt = prompt + "\nReturn valid JSON matching the schema exactly"
        retry_raw_text, retry_err = _execute_groq_call(retry_prompt, keys)
        if retry_err:
            reason = retry_err
            print(reason)
            return None, reason

        retry_phases, retry_parse_err = _parse_and_validate(retry_raw_text, hpw)
        if retry_phases:
            return retry_phases, None

        reason = retry_parse_err or parse_err or "other"
        print(reason)
        return None, reason

    except Exception:
        reason = "other"
        print(reason)
        return None, reason
