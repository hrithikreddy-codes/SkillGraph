"""
report_export.py — Standalone HTML report generator for SkillGraph.
Provides self-contained, offline-compatible HTML templates with print-ready styling.
"""

import html


def base_html_template(title: str, content: str) -> str:
    """
    Returns a self-contained HTML document string with inline CSS (no external assets).
    Styled using the SkillGraph theme and optimized for screen display and clean PDF printing.
    """
    safe_title = html.escape(title)
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
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }}

    .header-card {{
      border-top: 6px solid var(--primary);
    }}

    .brand {{
      display: inline-block;
      font-size: 13px;
      font-weight: 700;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 1.2px;
      margin-bottom: 10px;
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
      background: #f1f5f9;
      color: var(--text);
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 500;
      border: 1px solid var(--border);
    }}

    .tag-blue {{
      background: #dbeafe;
      color: #1e40af;
      border-color: #bfdbfe;
    }}

    .tag-amber {{
      background: #fef3c7;
      color: #92400e;
      border-color: #fde68a;
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
      background: #eff6ff;
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

    .task-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
      font-size: 15px;
      color: var(--text);
    }}

    .task-checkbox {{
      display: inline-block;
      width: 18px;
      height: 18px;
      border: 2px solid var(--primary);
      border-radius: 4px;
      flex-shrink: 0;
      margin-top: 3px;
      background: #ffffff;
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
      body {{
        background: #ffffff !important;
        padding: 0 !important;
        color: #000000 !important;
      }}
      .container {{
        max-width: 100% !important;
      }}
      .card {{
        border: 1px solid #cbd5e1 !important;
        box-shadow: none !important;
        margin-bottom: 16px !important;
        padding: 20px !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }}
      .task-checkbox {{
        border: 2px solid #000000 !important;
      }}
      .tag {{
        border: 1px solid #94a3b8 !important;
        background: #f8fafc !important;
        color: #000000 !important;
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
    <div class="footer">SkillGraph &copy; 2026 &bull; Personalized Career Roadmap</div>
  </div>
</body>
</html>"""


def roadmap_to_html(profile: dict, phases: list[dict]) -> str:
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

    # Header section
    header_html = f"""
    <div class="card header-card">
      <div class="brand">🧭 SkillGraph &bull; Career Roadmap</div>
      <h1 class="career-title">{html.escape(career)}</h1>
      <p class="subtitle">A 12-month step-by-step career roadmap for your interest in {html.escape(topic_label)}.</p>
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
        when = html.escape(ph.get("when", ""))
        blurb = html.escape(ph.get("blurb", ""))

        tags_html = ""
        phase_tags = ph.get("tags", [])
        if phase_tags:
            tag_spans = "".join(f'<span class="tag tag-blue">{html.escape(str(t))}</span>' for t in phase_tags if str(t).strip())
            if tag_spans:
                tags_html = f'<div class="phase-tags">{tag_spans}</div>'

        tasks_html = []
        for task in ph.get("tasks", []):
            safe_task = html.escape(str(task))
            tasks_html.append(f"""
            <div class="task-item">
              <span class="task-checkbox"></span>
              <span class="task-text">{safe_task}</span>
            </div>
            """)

        tasks_rendered = "".join(tasks_html)

        phases_html.append(f"""
        <div class="card">
          <div class="phase-top">
            <span class="phase-badge">{p_num}</span>
            <h2 class="phase-title">{title}</h2>
            <span class="phase-when">{when}</span>
          </div>
          <p class="phase-blurb">{blurb}</p>
          {tags_html}
          <div class="tasks-list">
            {tasks_rendered}
          </div>
        </div>
        """)

    body_content = header_html + "\n".join(phases_html)
    doc_title = f"{career} - Career Roadmap"
    return base_html_template(doc_title, body_content)
