"""
roadmap_ai.py — AI-generated personalized career roadmaps via Groq.
"""

import json
from analyzer import _get_api_keys, _call_groq


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
            - total_months (int)
            - tasks (list of strings, max 4)
            - tags (list of strings for phase 1; empty list for phases 2-5)
        Returns None on any error or parsing failure.
    """
    try:
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

        prompt = f"""You are an expert career and learning mentor. Create a personalized career learning roadmap sized to the user's weekly study budget.

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
   - Fewer hours means fewer, smaller tasks per phase (never more than 4 tasks per phase), not just a longer timeline. Scope each task so it realistically fits within the study budget.

2. Use the exact 5 phase titles in this order:
   - Phase 1: "Build your foundation"
   - Phase 2: "Learn the core skills"
   - Phase 3: "Build real projects"
   - Phase 4: "Gain experience"
   - Phase 5: "Prepare for your career"

3. Task prefixes:
   - Every single task MUST start with "Learn:", "Practice:", or "Build:" (e.g., "Learn: core syntax and data structures", "Practice: solve 5 beginner algorithm problems", "Build: a CLI budget tracker"). Tasks must be short, concrete, and actionable.

4. Learner Tier & Difficulty:
   - For starter-tier learners (School, Intermediate / 12th, or beginners): provide exploratory, beginner-friendly steps with free tools. Do NOT ask for mastery of advanced topics (Docker, microservices, CI/CD, system design) in the first 12 months; mention them as awareness only (e.g., "Learn: awareness of containerization concepts and what Docker solves").
   - For college / B.Tech / Degree learners: focus on production-grade tools, deeper computer science fundamentals, and technical interview preparation.

5. Handling existing skills:
   - If the user's skills list is empty or "None", assume a beginner.
   - If the user has existing skills, build on them and say in the Phase 1 blurb which known skills the plan builds on.

6. Make tasks differ meaningfully by interest ({interest_label}) and target career ({career}). Do NOT reuse generic tasks across fields.

7. Task count and Goal:
   - Keep each phase to at most 4 tasks (between 2 to 4 tasks, never more than 4).
   - Add one short "goal" field per phase: a one-line outcome the learner can check (e.g., "You can build and deploy a small API", "You can conduct exploratory data analysis on a real-world dataset").

8. Controllable actions (no outcome promises):
   - Do NOT promise outcomes like getting an internship or job. Phrase career tasks strictly as actions the learner controls (e.g., "Practice: apply to 10 internships with tailored resumes", NOT "Get an internship" or "Land a job").

9. Tags:
   - Phase 1 must include a "tags" list with 3-5 key tools, languages, or foundational concepts (e.g., ["Python", "Git", "VS Code"]).
   - Phases 2, 3, 4, and 5 must have an empty "tags" list ([]).

10. Return JSON only with "total_months" integer and "phases" list. No markdown formatting, no code fences (```json ... ```), no introductory or concluding text.

Output format:
{{
  "total_months": {target_months},
  "phases": [
    {{
      "title": "Build your foundation",
      "when": "...",
      "blurb": "Short summary of what to achieve in this phase (if user had skills, explicitly state which known skills the plan builds on).",
      "goal": "You can write basic scripts and use Git for version control.",
      "tasks": [
        "Learn: core language syntax and variables",
        "Practice: solve 10 basic coding exercises",
        "Build: a small command-line tool"
      ],
      "tags": ["Tool 1", "Tool 2", "Tool 3"]
    }},
    {{
      "title": "Learn the core skills",
      "when": "...",
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You can build a functional CRUD application with a database.",
      "tasks": [
        "Learn: relational databases and SQL queries",
        "Practice: design a database schema for an application",
        "Build: a backend API connected to SQLite"
      ],
      "tags": []
    }},
    {{
      "title": "Build real projects",
      "when": "...",
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have 2 full projects documented and hosted online.",
      "tasks": [
        "Build: a full-stack project solving a real problem",
        "Practice: write comprehensive README documentation",
        "Build: deploy the application to a free hosting platform"
      ],
      "tags": []
    }},
    {{
      "title": "Gain experience",
      "when": "...",
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have collaborated with other developers on a shared codebase.",
      "tasks": [
        "Practice: contribute a bug fix or docs to an open-source repo",
        "Practice: participate in a hackathon or team build",
        "Build: collaborate on a feature using pull requests"
      ],
      "tags": []
    }},
    {{
      "title": "Prepare for your career",
      "when": "...",
      "blurb": "Short summary of what to achieve in this phase.",
      "goal": "You have an active portfolio and application pipeline ready.",
      "tasks": [
        "Build: a clean 1-page portfolio website showcasing top projects",
        "Practice: apply to 10 internships or junior roles with tailored resumes",
        "Practice: complete 20 technical interview practice questions"
      ],
      "tags": []
    }}
  ]
}}
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

        # Validate total_months: must be an integer > 0
        if total_months is None:
            return None
        if not isinstance(total_months, int):
            try:
                total_months = int(total_months)
            except (ValueError, TypeError):
                return None
        if total_months <= 0:
            return None

        if not isinstance(raw_phases, list) or len(raw_phases) != 5:
            return None

        validated_phases = []
        for i, phase in enumerate(raw_phases):
            if not isinstance(phase, dict):
                return None

            title = phase.get("title")
            when = phase.get("when")
            blurb = phase.get("blurb")
            goal = phase.get("goal")
            tasks = phase.get("tasks")
            tags = phase.get("tags")

            if not (isinstance(title, str) and title.strip()):
                return None
            if not (isinstance(when, str) and when.strip()):
                return None
            if not (isinstance(blurb, str) and blurb.strip()):
                return None
            if not (isinstance(tasks, list) and len(tasks) >= 1 and all(isinstance(t, str) and t.strip() for t in tasks)):
                return None

            clean_tasks = [t.strip() for t in tasks[:4]]
            if len(clean_tasks) < 1 or len(clean_tasks) > 4:
                return None

            clean_goal = goal.strip() if isinstance(goal, str) and goal.strip() else f"Achieve key milestone for {title.strip()}."

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
                "total_months": total_months,
                "tasks": clean_tasks,
                "tags": clean_tags
            })

        return validated_phases

    except Exception:
        return None
