"""
report_export.py — Standalone HTML report generator for SkillGraph.
Provides self-contained, offline-compatible HTML templates with print-ready styling.
"""

import html
import re
from typing import Any, Dict, List, Union


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


def base_html_template(title: str, content: str, footer_text: str = "Personalized Career Roadmap & Skills Intelligence") -> str:
    """
    Returns a self-contained HTML document string with inline CSS (no external assets).
    Styled using the SkillGraph theme and optimized for screen display and clean PDF printing.
    """
    safe_title = html.escape(title)
    safe_footer = html.escape(footer_text)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe_title}</title>
  <style>
    :root {{
      --primary: #2563eb;
      --deep: #1e3a8a;
      --amber: #fbbf24;
      --bg: #f4f6fb;
      --card-bg: #ffffff;
      --text: #0f172a;
      --muted: #5b6475;
      --border: #e3e8f2;
      --item-bg: #f8fafc;
      --code-bg: #ffffff;
      --code-text: #0f172a;
      --tag-bg: #f1f5f9;
      --when-bg: #eff6ff;
      --progress-bg: #e2e8f0;
      --shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
      --checked-text: #94a3b8;

      /* Badges */
      --matched-bg: #dbeafe;
      --matched-text: #1e40af;
      --matched-border: #bfdbfe;

      --partial-bg: #fef3c7;
      --partial-text: #92400e;
      --partial-border: #fde68a;

      --missing-bg: #fee2e2;
      --missing-text: #991b1b;
      --missing-border: #fecaca;

      --low-bg: #e0f2fe;
      --low-text: #075985;
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --primary: #3b82f6;
        --deep: #93c5fd;
        --amber: #fbbf24;
        --bg: #0b1220;
        --card-bg: #111a2e;
        --text: #e5ecf8;
        --muted: #9aa8c2;
        --border: #24304d;
        --item-bg: #16213a;
        --code-bg: #16213a;
        --code-text: #e5ecf8;
        --tag-bg: #1c2c52;
        --when-bg: #1e293b;
        --progress-bg: #1e293b;
        --shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        --checked-text: #64748b;

        /* Badges */
        --matched-bg: #1e3a8a;
        --matched-text: #bfdbfe;
        --matched-border: #2563eb;

        --partial-bg: #451a03;
        --partial-text: #fde68a;
        --partial-border: #92400e;

        --missing-bg: #450a0a;
        --missing-text: #fecaca;
        --missing-border: #991b1b;

        --low-bg: #082f49;
        --low-text: #bae6fd;
      }}
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'DM Sans', Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 40px 20px;
    }}

    .container {{
      max-width: 840px;
      margin: 0 auto;
    }}

    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: var(--shadow);
    }}

    .header-card {{
      border-top: 6px solid var(--primary);
    }}

    .brand {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 700;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 1.2px;
      margin-bottom: 10px;
    }}

    .brand svg {{
      display: inline-block;
      vertical-align: middle;
      flex-shrink: 0;
    }}

    .career-title {{
      font-size: 32px;
      font-weight: 800;
      color: var(--deep);
      margin-bottom: 8px;
      line-height: 1.2;
    }}

    .subtitle {{
      font-size: 16px;
      color: var(--muted);
      margin-bottom: 16px;
    }}

    .tags-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}

    .tag {{
      display: inline-block;
      background: var(--tag-bg);
      color: var(--text);
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 500;
      border: 1px solid var(--border);
    }}

    .tag-blue {{
      background: var(--matched-bg);
      color: var(--matched-text);
      border-color: var(--matched-border);
    }}

    .tag-amber {{
      background: var(--partial-bg);
      color: var(--partial-text);
      border-color: var(--partial-border);
    }}

    /* Progress bar */
    .progress-wrap {{
      background: var(--progress-bg);
      border-radius: 999px;
      height: 14px;
      overflow: hidden;
      margin: 14px 0 8px;
    }}

    .progress-bar {{
      height: 100%;
      background: linear-gradient(90deg, var(--primary), #3b82f6);
      border-radius: 999px;
    }}

    .score-number {{
      font-size: 38px;
      font-weight: 800;
      color: var(--deep);
      line-height: 1;
    }}

    /* Status Badges */
    .badge-status {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .badge-matched {{
      background: var(--matched-bg);
      color: var(--matched-text);
      border: 1px solid var(--matched-border);
    }}

    .badge-partial {{
      background: var(--partial-bg);
      color: var(--partial-text);
      border: 1px solid var(--partial-border);
    }}

    .badge-missing {{
      background: var(--missing-bg);
      color: var(--missing-text);
      border: 1px solid var(--missing-border);
    }}

    .badge-subtle {{
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--tag-bg);
      color: var(--muted);
      border: 1px solid var(--border);
    }}

    /* Skill items */
    .skill-item {{
      background: var(--item-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 10px;
    }}

    .skill-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
    }}

    .skill-name {{
      font-weight: 700;
      font-size: 16px;
      color: var(--deep);
    }}

    .skill-detail {{
      font-size: 14px;
      color: var(--text);
      margin-top: 5px;
      line-height: 1.5;
    }}

    .skill-detail strong {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-right: 4px;
    }}

    /* Roadmap step card */
    .roadmap-step {{
      background: var(--item-bg);
      border-left: 4px solid var(--primary);
      border-radius: 0 12px 12px 0;
      padding: 16px;
      margin-bottom: 14px;
      border-top: 1px solid var(--border);
      border-right: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }}

    .priority-badge {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }}

    .priority-high {{
      background: var(--missing-bg);
      color: var(--missing-text);
    }}

    .priority-medium {{
      background: var(--partial-bg);
      color: var(--partial-text);
    }}

    .priority-low {{
      background: var(--low-bg);
      color: var(--low-text);
    }}

    .code-bullet {{
      display: block;
      background: var(--code-bg);
      border: 1px solid var(--border);
      padding: 8px 12px;
      border-radius: 6px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
      margin-top: 6px;
      color: var(--code-text);
      line-height: 1.4;
    }}

    .phase-top {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }}

    .phase-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      background: var(--primary);
      color: #ffffff;
      font-weight: 700;
      font-size: 15px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    .phase-title {{
      font-size: 20px;
      font-weight: 700;
      color: var(--deep);
      flex-grow: 1;
    }}

    .phase-when {{
      font-size: 13px;
      font-weight: 600;
      color: var(--primary);
      background: var(--when-bg);
      padding: 4px 10px;
      border-radius: 6px;
      white-space: nowrap;
    }}

    .phase-blurb {{
      color: var(--muted);
      font-size: 15px;
      margin-bottom: 16px;
      padding-left: 44px;
    }}

    .phase-goal {{
      margin-left: 44px;
      margin-top: -6px;
      margin-bottom: 16px;
      font-size: 14px;
      line-height: 1.5;
      color: var(--text);
      background: var(--item-bg);
      border-left: 3px solid var(--primary);
      padding: 8px 12px;
      border-radius: 0 8px 8px 0;
    }}

    .phase-goal strong {{
      color: var(--deep);
      margin-right: 4px;
    }}

    .phase-tags {{
      padding-left: 44px;
      margin-bottom: 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .tasks-list {{
      padding-left: 44px;
    }}

    .phase-resources {{
      padding-left: 44px;
      margin-top: 14px;
      font-size: 14px;
      color: var(--muted);
      line-height: 1.5;
    }}

    .phase-resources strong {{
      color: var(--deep);
      margin-right: 4px;
    }}

    .group-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--deep);
      margin-top: 16px;
      margin-bottom: 10px;
    }}

    .group-title:first-child {{
      margin-top: 0;
    }}

    .task-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
      font-size: 15px;
      color: var(--text);
      cursor: pointer;
    }}

    .task-checkbox {{
      width: 18px;
      height: 18px;
      accent-color: #2563eb;
      flex-shrink: 0;
      margin-top: 3px;
      cursor: pointer;
    }}

    .task-checkbox:checked + .task-text,
    .task-item:has(:checked) .task-text {{
      color: var(--checked-text);
      text-decoration: line-through;
    }}

    .task-text {{
      flex: 1;
      line-height: 1.5;
    }}

    .footer {{
      text-align: center;
      font-size: 13px;
      color: var(--muted);
      margin-top: 24px;
    }}

    @media print {{
      :root {{
        --primary: #2563eb !important;
        --deep: #1e3a8a !important;
        --amber: #fbbf24 !important;
        --bg: #ffffff !important;
        --card-bg: #ffffff !important;
        --text: #0f172a !important;
        --muted: #5b6475 !important;
        --border: #e3e8f2 !important;
        --item-bg: #ffffff !important;
        --code-bg: #ffffff !important;
        --code-text: #0f172a !important;
        --tag-bg: #f8fafc !important;
        --when-bg: #eff6ff !important;
        --progress-bg: #e2e8f0 !important;
        --shadow: none !important;
        --checked-text: #64748b !important;
        --matched-bg: #dbeafe !important;
        --matched-text: #1e40af !important;
        --matched-border: #bfdbfe !important;
        --partial-bg: #fef3c7 !important;
        --partial-text: #92400e !important;
        --partial-border: #fde68a !important;
        --missing-bg: #fee2e2 !important;
        --missing-text: #991b1b !important;
        --missing-border: #fecaca !important;
        --low-bg: #e0f2fe !important;
        --low-text: #075985 !important;
      }}
      body {{
        background: #ffffff !important;
        padding: 0 !important;
        color: #000000 !important;
      }}
      .container {{
        max-width: 100% !important;
      }}
      .card {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: none !important;
        margin-bottom: 16px !important;
        padding: 20px !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }}
      .group-title {{
        color: #000000 !important;
        page-break-after: avoid !important;
        break-after: avoid !important;
      }}
      .career-title, .phase-title, .skill-name {{
        color: #000000 !important;
      }}
      .subtitle, .phase-blurb, .skill-detail strong {{
        color: #475569 !important;
      }}
      .skill-detail, .task-item {{
        color: #000000 !important;
      }}
      .code-bullet {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #000000 !important;
      }}
      .phase-when {{
        background: #eff6ff !important;
        color: #1e40af !important;
        border: 1px solid #bfdbfe !important;
      }}
      .task-checkbox {{
        border: 2px solid #000000 !important;
      }}
      .tag {{
        border: 1px solid #94a3b8 !important;
        background: #f8fafc !important;
        color: #000000 !important;
      }}
      .progress-wrap {{
        border: 1px solid #94a3b8 !important;
        background: #e2e8f0 !important;
      }}
      .progress-bar {{
        background: #2563eb !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }}
      .skill-item, .roadmap-step {{
        border: 1px solid #cbd5e1 !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        background: #ffffff !important;
      }}
      .badge-status, .priority-badge {{
        border: 1px solid #94a3b8 !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }}
      .footer {{
        display: none !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    {content}
    <div class="footer">SkillGraph &copy; 2026 &bull; {safe_footer}</div>
  </div>
</body>
</html>"""


def _is_task_checked(checked_state, p: int, g: int, t: int, task: str) -> bool:
    """Checks whether a given task is ticked in the checked_state."""
    if not checked_state:
        return False

    task_str = str(task).strip()

    if isinstance(checked_state, (set, list)):
        return task_str in checked_state or task in checked_state or (p, g, t) in checked_state or (p, t) in checked_state

    if isinstance(checked_state, dict) or hasattr(checked_state, "get"):
        if checked_state.get(task_str) or checked_state.get(task):
            return True
        if checked_state.get((p, g, t)) or checked_state.get((p, t)):
            return True
        suffix = f"_{p}_{g}_{t}"
        for k in checked_state:
            if isinstance(k, str) and (k.endswith(suffix) or k == f"task_{p}_{g}_{t}"):
                if checked_state.get(k):
                    return True

    return False


def roadmap_to_html(profile: dict, phases: list[dict], checked_state=None) -> str:
    """
    Renders a complete, standalone HTML roadmap document from user profile and phase data.
    All user text is escaped to protect against injection.
    """
    interest_map = {
        "software": ("Software Development", "💻"),
        "ai": ("Artificial Intelligence", "🤖"),
        "data": ("Data Science", "📊"),
        "cyber": ("Cybersecurity", "🛡️"),
        "design": ("UI/UX Design", "🎨"),
        "business": ("Business / Entrepreneurship", "🚀"),
    }

    raw_interest = profile.get("interest", "")
    if raw_interest == "other":
        topic_label = profile.get("other_interest", "").strip() or profile.get("career", "").strip() or "Other"
        topic_emoji = "✨"
    elif raw_interest in interest_map:
        topic_label, topic_emoji = interest_map[raw_interest]
    else:
        topic_label = raw_interest or "Career"
        topic_emoji = "🎯"

    career = profile.get("career", "").strip() or topic_label
    education = profile.get("education", "")
    hours = profile.get("hours", 8)

    total_months = None
    if phases and isinstance(phases, list):
        for ph in phases:
            if isinstance(ph, dict) and ph.get("total_months"):
                total_months = ph["total_months"]
                break

    if total_months:
        subtitle_html = f'<p class="subtitle">A {total_months}-month step-by-step career roadmap for your interest in {html.escape(topic_label)}, about {hours} hours a week.</p>'
    else:
        subtitle_html = (
            f'<p class="subtitle">A 12-month step-by-step career roadmap for your interest in {html.escape(topic_label)}.</p>\n'
            f'      <p class="subtitle" style="font-size: 13px; color: var(--muted); margin-top: -10px;">Note: Template roadmap &bull; about {hours} hours a week.</p>'
        )

    # Header section
    header_html = f"""
    <div class="card header-card">
      <div class="brand">{LOGO_SVG} SkillGraph &bull; Career Roadmap</div>
      <h1 class="career-title">{html.escape(career)}</h1>
      {subtitle_html}
      <div class="tags-wrap">
        <span class="tag">{html.escape(education)}</span>
        <span class="tag">{html.escape(topic_emoji)} {html.escape(topic_label)}</span>
    """

    for s in profile.get("strengths", []):
        if s:
            header_html += f'<span class="tag tag-amber">{html.escape(s)}</span>\n'

    for sk in profile.get("skills", []):
        if sk:
            header_html += f'<span class="tag tag-blue">&#9889; {html.escape(sk)}</span>\n'

    header_html += """
      </div>
    </div>
    """

    # Phases section
    phases_html = []
    for idx, ph in enumerate(phases):
        p_num = idx + 1
        title = html.escape(ph.get("title", f"Phase {p_num}"))
        when = html.escape(str(ph.get("when", "")))
        hours_val = ph.get("hours")
        if hours_val:
            safe_hours = html.escape(str(hours_val))
            when_display = f"{when} &bull; up to {safe_hours} hours" if when else f"up to {safe_hours} hours"
        else:
            when_display = when
        blurb = html.escape(ph.get("blurb", ""))

        goal_val = str(ph.get("goal") or "").strip()
        goal_html = f'<div class="phase-goal"><strong>Goal:</strong> {html.escape(goal_val)}</div>' if goal_val else ""

        tags_html = ""
        phase_tags = ph.get("tags", [])
        if phase_tags:
            tag_spans = "".join(f'<span class="tag tag-blue">{html.escape(str(t))}</span>' for t in phase_tags if str(t).strip())
            if tag_spans:
                tags_html = f'<div class="phase-tags">{tag_spans}</div>'

        tasks_html = []
        raw_groups = ph.get("groups")
        if isinstance(raw_groups, list) and len(raw_groups) > 0:
            groups = raw_groups
        else:
            groups = [{"name": "", "tasks": ph.get("tasks", [])}]

        for g_idx, grp in enumerate(groups):
            if not isinstance(grp, dict):
                continue
            grp_name = str(grp.get("name", "")).strip()
            if grp_name:
                tasks_html.append(f'<h3 class="group-title">{html.escape(grp_name)}</h3>')
            grp_tasks = grp.get("tasks", [])
            if isinstance(grp_tasks, list):
                for t_idx, task in enumerate(grp_tasks):
                    safe_task = html.escape(str(task))
                    is_checked = _is_task_checked(checked_state, idx, g_idx, t_idx, str(task))
                    checked_attr = " checked" if is_checked else ""
                    task_id = f"task_{idx}_{g_idx}_{t_idx}"
                    tasks_html.append(f"""
                    <label class="task-item">
                      <input type="checkbox" class="task-checkbox" data-task-id="{task_id}"{checked_attr}>
                      <span class="task-text">{safe_task}</span>
                    </label>
                    """)

        tasks_rendered = "".join(tasks_html)

        ph_resources = ph.get("resources")
        if isinstance(ph_resources, list):
            res_names = [str(r).strip() for r in ph_resources if str(r).strip()]
        elif isinstance(ph_resources, str) and ph_resources.strip():
            res_names = [str(r).strip() for r in ph_resources.split(",") if str(r).strip()]
        else:
            res_names = []

        if res_names:
            safe_resources = html.escape(", ".join(res_names))
            resources_html = f'<div class="phase-resources"><strong>Free places to learn:</strong> {safe_resources}</div>'
        else:
            resources_html = ""

        phases_html.append(f"""
        <div class="card">
          <div class="phase-top">
            <span class="phase-badge">{p_num}</span>
            <h2 class="phase-title">{title}</h2>
            <span class="phase-when">{when_display}</span>
          </div>
          <p class="phase-blurb">{blurb}</p>
          {goal_html}
          {tags_html}
          <div class="tasks-list">
            {tasks_rendered}
          </div>
          {resources_html}
        </div>
        """)

    storage_script = """
    <script>
    (function() {
      try {
        var key = "skillgraph_roadmap_" + (document.title || "roadmap").replace(/[^a-zA-Z0-9_-]/g, "_");
        var checkboxes = document.querySelectorAll(".task-checkbox");
        if (!checkboxes || checkboxes.length === 0) return;

        try {
          var saved = localStorage.getItem(key);
          if (saved) {
            var state = JSON.parse(saved);
            checkboxes.forEach(function(cb, idx) {
              var taskId = cb.getAttribute("data-task-id");
              if (taskId && state[taskId] !== undefined) {
                cb.checked = Boolean(state[taskId]);
              } else if (state[idx] !== undefined) {
                cb.checked = Boolean(state[idx]);
              }
            });
          }
        } catch (e) {}

        function saveState() {
          try {
            var state = {};
            checkboxes.forEach(function(cb, idx) {
              var taskId = cb.getAttribute("data-task-id") || String(idx);
              state[taskId] = cb.checked;
              state[idx] = cb.checked;
            });
            localStorage.setItem(key, JSON.stringify(state));
          } catch (e) {}
        }

        checkboxes.forEach(function(cb) {
          cb.addEventListener("change", saveState);
        });
      } catch (e) {}
    })();
    </script>
    """

    body_content = header_html + "\n".join(phases_html) + storage_script
    doc_title = f"{career} - Career Roadmap"
    return base_html_template(doc_title, body_content, "Personalized Career Roadmap")


def _inline_md_to_html(text: str) -> str:
    """Escapes text and converts inline bold (**text**) and code (`text`) to safe HTML."""
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code class='code-bullet'>\1</code>", escaped)
    return escaped


def _markdown_report_to_html(md_text: str) -> str:
    """
    Converts a markdown analysis report into a styled HTML document.
    Escapes all dynamic text to prevent XSS.
    """
    lines = md_text.splitlines()
    doc_title = "Resume Analysis Report"
    content_cards = []
    current_card_lines = []
    current_card_title = ""

    def flush_card():
        nonlocal current_card_lines, current_card_title
        if not current_card_lines and not current_card_title:
            return
        body = []
        in_list = False
        for l in current_card_lines:
            stripped = l.strip()
            if not stripped:
                if in_list:
                    body.append("</ul>")
                    in_list = False
                continue
            if stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    body.append('<ul style="padding-left: 20px; line-height: 1.8; margin-bottom: 12px;">')
                    in_list = True
                item_content = stripped[2:].strip()
                item_html = _inline_md_to_html(item_content)
                body.append(f"<li>{item_html}</li>")
            else:
                if in_list:
                    body.append("</ul>")
                    in_list = False
                body.append(f"<p style='margin-bottom: 10px;'>{_inline_md_to_html(stripped)}</p>")
        if in_list:
            body.append("</ul>")

        header_html = f"<h2 class='phase-title' style='margin-bottom: 14px;'>{html.escape(current_card_title)}</h2>" if current_card_title else ""
        content_cards.append(f"<div class='card'>{header_html}{''.join(body)}</div>")
        current_card_lines = []
        current_card_title = ""

    header_card_rendered = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not header_card_rendered:
            doc_title = stripped[2:].strip()
            content_cards.append(f"""
            <div class="card header-card">
              <div class="brand">{LOGO_SVG} SkillGraph &bull; Resume Analysis Report</div>
              <h1 class="career-title">{html.escape(doc_title)}</h1>
            </div>
            """)
            header_card_rendered = True
        elif stripped.startswith("### ") or stripped.startswith("## "):
            flush_card()
            current_card_title = stripped.lstrip("#").strip()
        else:
            current_card_lines.append(line)

    flush_card()
    if not header_card_rendered:
        content_cards.insert(0, f"""
        <div class="card header-card">
          <div class="brand">{LOGO_SVG} SkillGraph &bull; Resume Analysis Report</div>
          <h1 class="career-title">{html.escape(doc_title)}</h1>
        </div>
        """)


# ---------------------------------------------------------------------------
# Core Role & Roadmap Step Generation Helpers
# ---------------------------------------------------------------------------

ROLE_DOMAIN_SKILLS = [
    # AI / ML / NLP / Computer Vision / Data Science
    (
        {"ai", "artificial intelligence", "ml", "machine learning", "deep learning", "nlp", "computer vision", "data scientist", "data science", "llm", "generative ai", "prompt engineer"},
        {
            "llm", "llms", "large language model", "large language models", "langchain", "llamaindex", "transformer", "transformers",
            "pytorch", "tensorflow", "keras", "vector database", "vector databases", "vector db", "pinecone", "chroma", "weaviate", "qdrant",
            "hugging face", "huggingface", "rag", "retrieval augmented generation", "fine-tuning", "fine tuning", "prompt engineering",
            "openai", "gemini", "claude", "deep learning", "neural networks", "nlp", "natural language processing", "computer vision", "opencv",
            "scikit-learn", "sklearn", "generative ai", "genai", "diffusion", "reinforcement learning", "mlops", "data science", "machine learning"
        }
    ),
    # Frontend / Web / UI / UX
    (
        {"frontend", "front-end", "web developer", "web development", "ui", "ux", "react developer", "javascript developer"},
        {
            "react", "react.js", "next.js", "nextjs", "vue", "vue.js", "angular", "typescript", "tailwind", "tailwind css",
            "css", "html", "javascript", "redux", "graphql", "web performance", "responsive design", "webpack", "vite", "frontend"
        }
    ),
    # Backend / Software Engineering / Systems
    (
        {"backend", "back-end", "software engineer", "software engineering", "software developer", "fullstack", "full stack", "full-stack", "api developer", "systems engineer"},
        {
            "docker", "kubernetes", "microservices", "redis", "postgresql", "sql", "graphql", "kafka", "rabbitmq", "aws", "gcp", "azure",
            "ci/cd", "rest", "rest api", "grpc", "system design", "django", "fastapi", "spring boot", "node.js", "express", "go", "golang", "backend"
        }
    ),
    # Cloud / DevOps / SRE / Platform
    (
        {"devops", "cloud", "sre", "site reliability", "infrastructure", "platform engineer"},
        {
            "kubernetes", "docker", "terraform", "ci/cd", "aws", "gcp", "azure", "ansible", "linux", "prometheus", "grafana",
            "helm", "cloudformation", "jenkins", "argocd", "iac"
        }
    ),
    # Data Engineering / Big Data
    (
        {"data engineer", "data engineering", "etl", "big data", "analytics engineer"},
        {
            "spark", "pyspark", "kafka", "airflow", "sql", "dbt", "snowflake", "databricks", "hadoop", "etl", "data pipeline",
            "data warehouse", "bigquery"
        }
    ),
    # Cybersecurity / InfoSec
    (
        {"security", "cyber", "infosec", "soc", "penetration tester", "security engineer"},
        {
            "penetration testing", "siem", "owasp", "cryptography", "firewalls", "incident response", "network security",
            "vulnerability management", "wireshark", "burp suite"
        }
    ),
    # Mobile
    (
        {"mobile", "ios", "android", "flutter", "react native"},
        {
            "swift", "swiftui", "kotlin", "flutter", "react native", "ios", "android", "jetpack compose"
        }
    )
]


def _normalize_tokens(text: str) -> set[str]:
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    stop = {
        "with", "using", "and", "for", "the", "years", "year", "plus",
        "experience", "required", "knowledge", "skills", "skill",
        "demonstrated", "strong", "proficient", "proficiency", "in", "of", "to"
    }
    return {w for w in words if w not in stop and len(w) >= 2}


def _is_covered(target: str, steps: list) -> bool:
    t_clean = target.strip().lower()
    t_tokens = _normalize_tokens(t_clean)

    for st in steps:
        sk_clean = str(st.get("skill", "")).strip().lower()
        if not sk_clean:
            continue

        if t_clean == sk_clean or t_clean in sk_clean or sk_clean in t_clean:
            return True

        sk_tokens = _normalize_tokens(sk_clean)
        if t_tokens and t_tokens.issubset(sk_tokens):
            return True
        if sk_tokens and sk_tokens.issubset(t_tokens):
            return True

        step_text = f"{sk_clean} {str(st.get('learn', '')).lower()} {str(st.get('apply', '')).lower()} {str(st.get('why_gap', '')).lower()} {str(st.get('prove', '')).lower()}"
        if t_clean in step_text:
            return True
        step_tokens = _normalize_tokens(step_text)
        if t_tokens and t_tokens.issubset(step_tokens):
            return True

    return False


def _short_tool_name(clean_name: str) -> str:
    """
    Derives a short tool name from clean_name:
    if it contains " with " or " using ", takes the part after it (e.g. "Jest");
    otherwise returns clean_name unchanged.
    """
    s = clean_name.strip()
    s_lower = s.lower()
    if " with " in s_lower:
        idx = s_lower.find(" with ")
        return s[idx + 6:].strip()
    if " using " in s_lower:
        idx = s_lower.find(" using ")
        return s[idx + 7:].strip()
    return s


def _generate_step_for_item(item: str, job_role: str, is_missing_skill: bool, gaps: dict, reasons: dict, project_name: str = None) -> dict:
    it_lower = item.lower()

    why_gap = ""
    if item in gaps and gaps[item]:
        why_gap = str(gaps[item]).strip()
    elif item in reasons and reasons[item]:
        why_gap = str(reasons[item]).strip()
    else:
        for k, v in gaps.items():
            if k.lower() == it_lower and v:
                why_gap = str(v).strip()
                break
        if not why_gap:
            for k, v in reasons.items():
                if k.lower() == it_lower and v:
                    why_gap = str(v).strip()
                    break
    if not why_gap:
        why_gap = f"Required for {job_role} but not demonstrated in the resume."

    clean_name = re.sub(r'^(experience with|knowledge of|proven track record in)\s+', '', item, flags=re.IGNORECASE).strip()
    tool = _short_tool_name(clean_name)
    proj_name = project_name.strip() if (project_name and str(project_name).strip()) else "a personal project"

    if "jest" in it_lower or "testing" in it_lower:
        learn = f"Study test-driven development, unit testing patterns, and mocking with {tool}."
        apply = f"Write unit and integration test suites using {tool} for {proj_name}."
        prove = f"A working {tool} test suite covering core application logic with automated runs."
        example_bullet = f"Wrote unit and integration test suites using {tool} for {proj_name} [add your real result here if you have one]"
    elif "docker" in it_lower or "container" in it_lower:
        learn = f"Study containerization fundamentals and image builds with {tool}."
        apply = f"Containerize {proj_name} using {tool}."
        prove = f"A working Dockerfile and container configuration successfully building and running the application."
        example_bullet = f"Containerized {proj_name} using {tool}"
    elif "ci/cd" in it_lower or "github action" in it_lower or "pipeline" in it_lower:
        learn = f"Study automated integration and deployment workflows using {tool}."
        apply = f"Set up an automated pipeline using {tool} to test and build {proj_name} on code commits."
        prove = f"An active {tool} workflow passing automated test and build steps on code updates."
        example_bullet = f"Configured an automated CI/CD pipeline using {tool} for {proj_name} [add your real result here if you have one]"
    elif any(k in it_lower for k in ["aws", "cloud", "azure", "gcp", "ec2"]):
        learn = f"Learn cloud deployment fundamentals and hosting basics with {tool}."
        apply = f"Deploy {proj_name} using {tool}."
        prove = f"A live deployment accessible via public URL hosted on {tool}."
        example_bullet = f"Deployed {proj_name} to {tool} [add your real result here if you have one]"
    elif any(k in it_lower for k in ["agile", "scrum", "kanban"]):
        learn = f"Study Agile sprint cycles, backlog management, and task estimation practices."
        apply = f"Organize development of {proj_name} using an Agile board and sprint milestones."
        prove = f"A board and sprint notes for {proj_name}."
        example_bullet = f"Applied Agile practices to plan and execute milestones for {proj_name}"
    elif any(k in it_lower for k in ["git", "version control"]):
        learn = f"Learn branch management, pull request workflows, and merge conflict resolution with {tool}."
        apply = f"Use feature branches, semantic commits, and pull requests while developing {proj_name}."
        prove = f"A repository displaying structured branch merges and pull request histories for {proj_name}."
        example_bullet = f"Managed version control and development workflows for {proj_name} using {tool}"
    elif any(k in it_lower for k in ["communication", "teamwork", "collaboration", "stakeholder"]):
        learn = f"Study technical documentation standards and clear architecture communication."
        apply = f"Author technical documentation and architecture notes for {proj_name}."
        prove = f"Technical documentation and architecture decisions recorded for {proj_name}."
        example_bullet = f"Authored technical specifications and architecture documentation for {proj_name}"
    elif any(k in it_lower for k in ["years", "experience"]):
        learn = f"Deepen practical implementation patterns and best practices related to {tool}."
        apply = f"Build and document features in {proj_name} demonstrating practical experience with {tool}."
        prove = f"Working code and documentation demonstrating hands-on experience with {tool} in {proj_name}."
        example_bullet = f"Designed and delivered features in {proj_name} using {tool}"
    else:
        learn = f"Study core fundamentals, best practices, and practical implementation patterns for {tool}."
        apply = f"Implement {tool} into a functional feature within {proj_name}."
        prove = f"A working codebase and documentation demonstrating hands-on use of {tool}."
        example_bullet = f"Implemented {tool} in {proj_name}"

    priority = "High" if is_missing_skill else "Medium"

    return {
        "skill": item,
        "priority": priority,
        "why_gap": why_gap,
        "learn": learn,
        "apply": apply,
        "prove": prove,
        "example_bullet": example_bullet,
        "suggested_effort": "Estimated effort for foundational experience: 1-2 weeks"
    }


def _is_core_to_role(skill: str, role: str) -> bool:
    if not skill or not role:
        return False
    s_lower = skill.strip().lower()
    r_lower = role.strip().lower()

    for role_keywords, core_skills in ROLE_DOMAIN_SKILLS:
        role_matches = any(rk in r_lower for rk in role_keywords)
        if role_matches:
            if any(cs == s_lower or cs in s_lower or s_lower in cs for cs in core_skills):
                return True

    r_words = set(re.findall(r'[a-zA-Z]{3,}', r_lower)) - {"engineer", "developer", "senior", "junior", "lead", "specialist", "staff", "associate"}
    s_words = set(re.findall(r'[a-zA-Z]{3,}', s_lower))
    if r_words.intersection(s_words):
        return True

    return False


def _generate_core_reason(skill: str, role: str) -> str:
    sk_lower = skill.lower()

    if any(k in sk_lower for k in ["llm", "large language model", "langchain", "llamaindex", "rag", "transformer", "prompt engineering"]):
        return f"Core modern capability for {role} to build and evaluate production generative AI and LLM applications."
    elif any(k in sk_lower for k in ["pytorch", "tensorflow", "keras", "deep learning"]):
        return f"Fundamental framework for {role} to train, fine-tune, and deploy deep learning models."
    elif any(k in sk_lower for k in ["docker", "container", "kubernetes"]):
        return f"Essential industry standard for {role} to containerize, orchestrate, and scale services reliably."
    elif any(k in sk_lower for k in ["aws", "cloud", "azure", "gcp"]):
        return f"High-demand cloud infrastructure competency for {role} to host, scale, and secure production systems."
    elif any(k in sk_lower for k in ["ci/cd", "github action", "pipeline"]):
        return f"Crucial engineering practice for {role} to automate testing, build verification, and deployment pipelines."
    elif any(k in sk_lower for k in ["redis", "kafka", "rabbitmq"]):
        return f"Key messaging and caching technology for {role} to handle high-throughput, distributed workflows."
    elif any(k in sk_lower for k in ["graphql", "rest", "grpc", "api"]):
        return f"Modern communication protocol for {role} to architect flexible, resilient service interfaces."
    elif any(k in sk_lower for k in ["react", "typescript", "next"]):
        return f"Premier frontend standard for {role} to build responsive, type-safe web applications."
    else:
        return f"High-impact core competency for {role} that strengthens competitive positioning and demonstrates practical expertise."


def analysis_to_html(result: Union[Dict[str, Any], str]) -> str:
    """
    Renders a complete, standalone HTML resume/job match analysis report.
    Reuses the base HTML template and includes:
      - Target role in header card
      - Match score as a progress bar with percentage and skill counts
      - Matched, partial, and missing skills with evidence, reasons, and gaps
      - Additional requirements (soft skills & experience) if present
      - Actionable roadmap steps with priorities, efforts, and example resume bullets
      - Extra suggestions and analyzer recommendations
    All dynamic strings are escaped via html.escape.
    """
    if isinstance(result, str):
        return _markdown_report_to_html(result)

    if not isinstance(result, dict):
        safe_str = html.escape(str(result))
        return base_html_template("Career Analysis", f'<div class="card"><p>{safe_str}</p></div>')

    # Target role
    job_role = (
        result.get("job_role")
        or result.get("role")
        or result.get("target_role")
        or "Target Role"
    ).strip() or "Target Role"

    # Scores
    scores = result.get("scores") or result.get("score") or {}
    if not isinstance(scores, dict):
        scores = {}

    # Match results
    match_res = result.get("match_results") or result.get("compare_result") or result
    if not isinstance(match_res, dict):
        match_res = {}

    matched = [str(s) for s in (match_res.get("matched", []) or []) if str(s).strip()]
    partial = [str(s) for s in (match_res.get("partial", []) or []) if str(s).strip()]
    missing = [str(s) for s in (match_res.get("missing", []) or []) if str(s).strip()]

    evidence = match_res.get("evidence", {}) or {}
    reasons = match_res.get("reasons", {}) or {}
    gaps = match_res.get("gaps", {}) or {}
    evidence_type = match_res.get("evidence_type", {}) or {}

    bonus_matched = [str(s) for s in (match_res.get("bonus_matched", []) or []) if str(s).strip()]
    bonus_missing = [str(s) for s in (match_res.get("bonus_missing", []) or []) if str(s).strip()]

    matched_count = scores.get("matched_count", len(matched))
    partial_count = scores.get("partial_count", len(partial))
    missing_count = scores.get("missing_count", len(missing))
    total_required = scores.get("total_required", matched_count + partial_count + missing_count)

    raw_pct = scores.get("match_percent")
    if raw_pct is None:
        raw_pct = match_res.get("match_percent")
    if raw_pct is None:
        raw_pct = result.get("match_percent")
    if raw_pct is None:
        if total_required > 0:
            raw_pct = round((matched_count + 0.5 * partial_count) / total_required * 100)
        else:
            raw_pct = 0

    try:
        match_percent = int(round(float(raw_pct)))
    except (ValueError, TypeError):
        match_percent = 0

    match_percent = max(0, min(100, match_percent))

    # Roadmap
    roadmap = result.get("roadmap") or {}
    if not isinstance(roadmap, dict):
        roadmap = {}
    steps = [dict(s) for s in (roadmap.get("steps", []) or [])]
    optional_items = [dict(it) for it in (roadmap.get("optional", []) or [])]

    # Other requirements
    other_res = result.get("other_res") or {}
    if not isinstance(other_res, dict):
        other_res = {}
    other_items = other_res.get("results", []) or []

    # Derive project name if available in the resume
    project_name = None
    raw_projects = (
        result.get("projects")
        or result.get("resume_projects")
        or result.get("project_name")
        or result.get("project")
        or (result.get("resume_data") if isinstance(result.get("resume_data"), dict) else {}).get("projects")
        or (match_res if isinstance(match_res, dict) else {}).get("projects")
        or (roadmap if isinstance(roadmap, dict) else {}).get("projects")
    )
    if isinstance(raw_projects, list) and raw_projects:
        for p in raw_projects:
            if p and str(p).strip():
                project_name = str(p).strip()
                break
    elif isinstance(raw_projects, str) and raw_projects.strip():
        project_name = raw_projects.strip()

    # Ensure every required skill marked missing gets a step in the Actionable Roadmap
    for sk in missing:
        if not _is_covered(sk, steps):
            steps.append(_generate_step_for_item(sk, job_role, is_missing_skill=True, gaps=gaps, reasons=reasons, project_name=project_name))

    # Ensure every requirement marked "Not shown" gets a step in the Actionable Roadmap
    for it in other_items:
        it_name = str(it.get("item", "")).strip()
        st_stat = str(it.get("status", "")).strip().lower()
        if st_stat != "supported" and it_name:
            if not _is_covered(it_name, steps):
                steps.append(_generate_step_for_item(it_name, job_role, is_missing_skill=False, gaps=gaps, reasons=reasons, project_name=project_name))

    # Cleanly sort and assign sequential orders
    if steps:
        pri_rank = {"High": 0, "Medium": 1, "Low": 2}
        steps.sort(key=lambda s: (pri_rank.get(s.get("priority", "Medium"), 1), s.get("order", 999)))
        for idx, s in enumerate(steps, start=1):
            s["order"] = idx

    # Ensure nice-to-have skills core to the role appear in Extra Suggestions, not just as chips
    existing_opt_skills = {str(it.get("skill", "")).strip().lower() for it in optional_items}
    for b_sk in bonus_missing:
        if _is_core_to_role(b_sk, job_role):
            if not any(b_sk.lower() in esk or esk in b_sk.lower() for esk in existing_opt_skills):
                optional_items.append({
                    "skill": b_sk,
                    "reason": _generate_core_reason(b_sk, job_role)
                })
                existing_opt_skills.add(b_sk.lower())

    # Suggestions
    suggestions = result.get("suggestions") or result.get("recommendations") or result.get("notes") or []
    if isinstance(suggestions, str):
        suggestions = [suggestions]

    cards = []

    # 1. Header Card
    safe_role = html.escape(job_role)
    tags_html = [
        f'<span class="tag">🎯 Target Role: {safe_role}</span>',
        f'<span class="tag tag-blue">⚡ {total_required} Required Skills</span>',
        f'<span class="tag">✓ {matched_count} Matched</span>',
    ]
    if partial_count > 0:
        tags_html.append(f'<span class="tag tag-amber">~ {partial_count} Partial</span>')
    if missing_count > 0:
        tags_html.append(f'<span class="tag">✗ {missing_count} Missing</span>')

    cards.append(f"""
    <div class="card header-card">
      <div class="brand">{LOGO_SVG} SkillGraph &bull; Resume &amp; Job Match Analysis</div>
      <h1 class="career-title">{safe_role}</h1>
      <p class="subtitle">Comprehensive match breakdown, skill gap analysis, and personalized action roadmap.</p>
      <div class="tags-wrap">
        {''.join(tags_html)}
      </div>
    </div>
    """)

    # 2. Match Score Card with Progress Bar
    cards.append(f"""
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
        <h2 class="phase-title" style="margin: 0;">Core Skill Match</h2>
        <span class="score-number">{match_percent}%</span>
      </div>
      <div class="progress-wrap">
        <div class="progress-bar" style="width: {match_percent}%;"></div>
      </div>
      <p class="subtitle" style="margin-bottom: 0; margin-top: 10px;">
        <strong>{matched_count}</strong> fully matched + <strong>{partial_count}</strong> partial out of <strong>{total_required}</strong> required skills
      </p>
    </div>
    """)

    # 3. Matched Skills Card
    matched_items_html = []
    if matched:
        for sk in matched:
            safe_sk = html.escape(sk)
            ev = evidence.get(sk, "")
            ev_type = evidence_type.get(sk, "")
            type_pill = f'<span class="badge-subtle">{html.escape(str(ev_type).capitalize())}</span>' if ev_type else ''
            ev_html = f'<div class="skill-detail"><strong>Evidence:</strong> &ldquo;{html.escape(str(ev))}&rdquo;</div>' if ev else ''
            matched_items_html.append(f"""
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">{safe_sk}</span>
                <div style="display: flex; gap: 6px; align-items: center;">
                  {type_pill}
                  <span class="badge-status badge-matched">✓ Matched</span>
                </div>
              </div>
              {ev_html}
            </div>
            """)
    else:
        matched_items_html.append('<p class="subtitle" style="padding-left: 44px;">No matching skills identified.</p>')

    cards.append(f"""
    <div class="card">
      <div class="phase-top">
        <span class="phase-badge" style="background: #16a34a;">✓</span>
        <h2 class="phase-title">Matched Skills ({len(matched)})</h2>
      </div>
      <p class="phase-blurb">These skills from the job requirements are demonstrated on your resume.</p>
      <div style="padding-left: 44px;">
        {''.join(matched_items_html)}
      </div>
    </div>
    """)

    # 4. Partial Skills Card (only if partial skills exist)
    if partial:
        partial_items_html = []
        for sk in partial:
            safe_sk = html.escape(sk)
            ev = evidence.get(sk, "")
            rs = reasons.get(sk, "")
            gp = gaps.get(sk, "")
            ev_html = f'<div class="skill-detail"><strong>Evidence:</strong> &ldquo;{html.escape(str(ev))}&rdquo;</div>' if ev else ''
            rs_html = f'<div class="skill-detail"><strong>Why partial:</strong> {html.escape(str(rs))}</div>' if rs else ''
            gp_html = f'<div class="skill-detail"><strong>What&rsquo;s missing:</strong> {html.escape(str(gp))}</div>' if gp else ''
            partial_items_html.append(f"""
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">{safe_sk}</span>
                <span class="badge-status badge-partial">~ Partial</span>
              </div>
              {ev_html}
              {rs_html}
              {gp_html}
            </div>
            """)

        cards.append(f"""
        <div class="card">
          <div class="phase-top">
            <span class="phase-badge" style="background: var(--amber); color: #78350f;">~</span>
            <h2 class="phase-title">Partial Skills ({len(partial)})</h2>
          </div>
          <p class="phase-blurb">You have related experience, but some aspects of the required skill are missing.</p>
          <div style="padding-left: 44px;">
            {''.join(partial_items_html)}
          </div>
        </div>
        """)

    # 5. Missing Skills Card
    missing_items_html = []
    if missing:
        for sk in missing:
            safe_sk = html.escape(sk)
            rs = reasons.get(sk, "")
            gp = gaps.get(sk, "")
            rs_html = f'<div class="skill-detail"><strong>Reason:</strong> {html.escape(str(rs))}</div>' if rs else ''
            gp_html = f'<div class="skill-detail"><strong>Gap:</strong> {html.escape(str(gp))}</div>' if gp else ''
            missing_items_html.append(f"""
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">{safe_sk}</span>
                <span class="badge-status badge-missing">✗ Missing</span>
              </div>
              {rs_html}
              {gp_html}
            </div>
            """)
    else:
        missing_items_html.append('<p class="subtitle" style="padding-left: 44px;">🎉 Outstanding! No required skills are missing.</p>')

    cards.append(f"""
    <div class="card">
      <div class="phase-top">
        <span class="phase-badge" style="background: #dc2626;">✗</span>
        <h2 class="phase-title">Missing / Gap Skills ({len(missing)})</h2>
      </div>
      <p class="phase-blurb">These required skills were not demonstrated on your resume.</p>
      <div style="padding-left: 44px;">
        {''.join(missing_items_html)}
      </div>
    </div>
    """)

    # 6. Bonus / Nice-to-Have Skills
    if bonus_matched or bonus_missing:
        bonus_tags = []
        for s in bonus_matched:
            bonus_tags.append(f'<span class="tag tag-blue">🌟 {html.escape(str(s))} (Matched)</span>')
        for s in bonus_missing:
            bonus_tags.append(f'<span class="tag">💡 {html.escape(str(s))} (Recommended)</span>')
        cards.append(f"""
        <div class="card">
          <h2 class="phase-title" style="margin-bottom: 12px;">🌟 Nice-to-Have Skills</h2>
          <div class="tags-wrap" style="margin-top: 0;">
            {''.join(bonus_tags)}
          </div>
        </div>
        """)

    # 7. Other Requirements (Soft Skills & Experience)
    if other_items:
        other_items_html = []
        for it in other_items:
            it_name = html.escape(str(it.get("item", "")))
            st_stat = it.get("status", "")
            ev = it.get("evidence", "")
            if st_stat == "supported":
                stat_badge = '<span class="badge-status badge-matched">Supported</span>'
            else:
                stat_badge = '<span class="tag" style="font-size: 11px; padding: 2px 8px;">Not shown</span>'
            ev_html = f'<div class="skill-detail"><strong>Evidence:</strong> &ldquo;{html.escape(str(ev))}&rdquo;</div>' if ev else ''
            other_items_html.append(f"""
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">{it_name}</span>
                {stat_badge}
              </div>
              {ev_html}
            </div>
            """)

        cards.append(f"""
        <div class="card">
          <h2 class="phase-title" style="margin-bottom: 12px;">💬 Soft Skills &amp; Experience Requirements</h2>
          {''.join(other_items_html)}
        </div>
        """)

    # 8. Actionable Roadmap
    if steps:
        groups = {"High": [], "Medium": [], "Low": []}
        for st in steps:
            pri = st.get("priority", "Medium")
            if pri not in groups:
                pri = "Medium"
            groups[pri].append(st)

        roadmap_steps_html = []
        pri_configs = [
            ("🔥 High Priority", "High", "high"),
            ("⚡ Medium Priority", "Medium", "medium"),
            ("🌱 Lower Priority", "Low", "low"),
        ]

        for pri_label, pri_key, pri_class in pri_configs:
            group_steps = groups[pri_key]
            if not group_steps:
                continue
            sorted_steps = sorted(group_steps, key=lambda x: x.get("order", 999))
            roadmap_steps_html.append(f'<h3 style="font-size: 16px; font-weight: 700; color: var(--deep); margin: 18px 0 10px;">{html.escape(pri_label)}</h3>')

            for st in sorted_steps:
                order_val = html.escape(str(st.get("order", "?")))
                sk_name = html.escape(str(st.get("skill", "")))
                eff = html.escape(str(st.get("suggested_effort", "")))
                title_eff = f" ({eff})" if eff else ""
                pri_name = html.escape(str(st.get("priority", pri_key)))

                do_after = st.get("do_after", "")
                why_gap = st.get("why_gap", "")
                learn = st.get("learn", "")
                apply = st.get("apply", "")
                prove = st.get("prove", "")
                bullet = st.get("example_bullet", "")

                details = []
                if do_after:
                    details.append(f'<div class="skill-detail"><strong>Do this after:</strong> {html.escape(str(do_after))}</div>')
                if why_gap:
                    details.append(f'<div class="skill-detail"><strong>Why this is a gap:</strong> {html.escape(str(why_gap))}</div>')
                if learn:
                    details.append(f'<div class="skill-detail"><strong>Learn:</strong> {html.escape(str(learn))}</div>')
                if apply:
                    details.append(f'<div class="skill-detail"><strong>Apply:</strong> {html.escape(str(apply))}</div>')
                if prove:
                    details.append(f'<div class="skill-detail"><strong>Prove it:</strong> {html.escape(str(prove))}</div>')
                if bullet:
                    details.append(f'<div class="skill-detail"><strong>Example resume bullet:</strong> <code class="code-bullet">{html.escape(str(bullet))}</code></div>')

                roadmap_steps_html.append(f"""
                <div class="roadmap-step">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="font-size: 16px; font-weight: 700; color: var(--deep); margin: 0;">{order_val}. {sk_name}{title_eff}</h4>
                    <span class="priority-badge priority-{pri_class}">{pri_name} Priority</span>
                  </div>
                  {''.join(details)}
                </div>
                """)

        cards.append(f"""
        <div class="card">
          <div class="phase-top">
            <span class="phase-badge">🚀</span>
            <h2 class="phase-title">Your Actionable Roadmap</h2>
          </div>
          <p class="phase-blurb">Step-by-step guidance to close your skill gaps and strengthen your resume.</p>
          <div style="padding-left: 44px;">
            {''.join(roadmap_steps_html)}
          </div>
        </div>
        """)
    elif not missing and not partial and not any(it.get("status") != "supported" for it in other_items):
        cards.append("""
        <div class="card">
          <div class="phase-top">
            <span class="phase-badge">🎉</span>
            <h2 class="phase-title">Your Roadmap</h2>
          </div>
          <p class="subtitle" style="padding-left: 44px;">Incredible! Your resume already covers every required skill for this role.</p>
        </div>
        """)

    # 9. Extra Suggestions
    if optional_items:
        opt_html = []
        for it in optional_items:
            sk = html.escape(str(it.get("skill", "")))
            rs = html.escape(str(it.get("reason", "")))
            opt_html.append(f'<li><strong>{sk}</strong>: {rs}</li>')
        cards.append(f"""
        <div class="card">
          <h2 class="phase-title" style="margin-bottom: 12px;">✨ Extra Suggestions (Beyond Direct Requirements)</h2>
          <ul style="padding-left: 20px; line-height: 1.8;">
            {''.join(opt_html)}
          </ul>
        </div>
        """)

    # 10. Direct Analyzer Suggestions or Notes
    if suggestions:
        sug_html = []
        for s in suggestions:
            sug_html.append(f'<li>{html.escape(str(s))}</li>')
        cards.append(f"""
        <div class="card">
          <h2 class="phase-title" style="margin-bottom: 12px;">💡 Analyzer Suggestions</h2>
          <ul style="padding-left: 20px; line-height: 1.8;">
            {''.join(sug_html)}
          </ul>
        </div>
        """)

    # 11. Extra Report Markdown / Notes (if steps was empty and report_md is present)
    report_md = result.get("report_md") or result.get("text")
    if not steps and report_md and isinstance(report_md, str) and not matched and not missing:
        cards.append(f"""
        <div class="card">
          <h2 class="phase-title" style="margin-bottom: 12px;">📝 Analysis Summary</h2>
          <p style="white-space: pre-wrap;">{html.escape(report_md)}</p>
        </div>
        """)

    doc_title = f"{job_role} - SkillGraph Analysis Report"
    return base_html_template(doc_title, "\n".join(cards), "Resume & Job Match Analysis")
