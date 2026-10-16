"""
roadmap_ai.py — AI-generated personalized career roadmaps via Groq.
"""

import json
from analyzer import _get_api_keys, _call_groq


def generate_roadmap(education, interest_label, career, skills, strengths):
    """
    Generates a personalized 5-phase career roadmap using Groq.

    Args:
        education: Current education level (e.g., "School (under 18)", "B.Tech / Engineering").
        interest_label: Field of interest (e.g., "Software Development", "Artificial Intelligence").
        career: Target career/role (e.g., "Full Stack Developer", "AI Engineer").
        skills: List or collection of skills the user already knows.
        strengths: List of the user's main personal/professional strengths.

    Returns:
        A list of 5 dictionaries with keys:
            - title (str)
            - when (str)
            - blurb (str)
            - tasks (list of 3-4 strings)
            - tags (list of strings for phase 1; empty list for phases 2-5)
        Returns None on any error or parsing failure.
    """
    try:
        skills_str = ", ".join(skills) if isinstance(skills, list) and skills else (str(skills) if skills else "None")
        strengths_str = ", ".join(strengths) if isinstance(strengths, list) and strengths else (str(strengths) if strengths else "None")

        prompt = f"""You are an expert career and learning mentor. Create a personalized 12-month career learning roadmap.

Candidate Profile:
- Education level: {education}
- Area of interest: {interest_label}
- Target career: {career}
- Skills they already have: {skills_str}
- Key strengths: {strengths_str}

Rules:
1. Use the exact 5 phases of the standard career roadmap in this order:
   - Phase 1: "Build your foundation" (Weeks 1-6)
   - Phase 2: "Learn the core skills" (Months 2-4)
   - Phase 3: "Build real projects" (Months 4-6)
   - Phase 4: "Gain experience" (Months 6-9)
   - Phase 5: "Prepare for your career" (Months 9-12)
2. Match the education level:
   - A school student gets exploratory, beginner-friendly steps and simple experiments.
   - A college/B.Tech/degree student gets internship-ready, production tools, and interview-focused steps.
3. Skip skills the user already has and build directly on them.
4. Tasks must be short, concrete and actionable (e.g., "Build a REST API with FastAPI and SQLite", not "Learn backend").
5. Each phase must contain exactly 3 to 4 tasks in a list of strings.
6. Phase 1 must include a "tags" list with 3-5 key tools, languages, or foundational concepts (e.g., ["Python", "Git", "VS Code"]).
7. Phases 2, 3, 4, and 5 must have an empty "tags" list ([]).
8. Return JSON only. No markdown formatting, no code fences (```json ... ```), no introductory or concluding text.

Output format:
[
  {{
    "title": "Build your foundation",
    "when": "Weeks 1-6",
    "blurb": "Short summary of what to achieve in this phase.",
    "tasks": ["Task 1", "Task 2", "Task 3"],
    "tags": ["Tool 1", "Tool 2", "Tool 3"]
  }},
  {{
    "title": "Learn the core skills",
    "when": "Months 2-4",
    "blurb": "Short summary of what to achieve in this phase.",
    "tasks": ["Task 1", "Task 2", "Task 3"],
    "tags": []
  }},
  {{
    "title": "Build real projects",
    "when": "Months 4-6",
    "blurb": "Short summary of what to achieve in this phase.",
    "tasks": ["Task 1", "Task 2", "Task 3"],
    "tags": []
  }},
  {{
    "title": "Gain experience",
    "when": "Months 6-9",
    "blurb": "Short summary of what to achieve in this phase.",
    "tasks": ["Task 1", "Task 2", "Task 3"],
    "tags": []
  }},
  {{
    "title": "Prepare for your career",
    "when": "Months 9-12",
    "blurb": "Short summary of what to achieve in this phase.",
    "tasks": ["Task 1", "Task 2", "Task 3"],
    "tags": []
  }}
]
"""

        raw_response = _call_groq(prompt, temperature=0.2)
        if not raw_response or raw_response.startswith("❌") or "⏱️" in raw_response:
            return None

        # Strip markdown fences
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        # Unwrap if wrapped in an object like {"phases": [...]}
        if isinstance(data, dict):
            for key in ("phases", "roadmap", "steps", "data"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break

        if not isinstance(data, list) or len(data) != 5:
            return None

        validated_phases = []
        for i, phase in enumerate(data):
            if not isinstance(phase, dict):
                return None

            title = phase.get("title")
            when = phase.get("when")
            blurb = phase.get("blurb")
            tasks = phase.get("tasks")
            tags = phase.get("tags")

            if not (isinstance(title, str) and title.strip()):
                return None
            if not (isinstance(when, str) and when.strip()):
                return None
            if not (isinstance(blurb, str) and blurb.strip()):
                return None
            if not (isinstance(tasks, list) and len(tasks) >= 3 and all(isinstance(t, str) and t.strip() for t in tasks)):
                return None

            clean_tasks = [t.strip() for t in tasks[:4]]
            if len(clean_tasks) < 3 or len(clean_tasks) > 4:
                return None

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
                "tasks": clean_tasks,
                "tags": clean_tags
            })

        return validated_phases

    except Exception:
        return None
