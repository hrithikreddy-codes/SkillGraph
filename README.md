# SkillGraph

A personalized career roadmap generator and resume skill-gap analyzer built with Streamlit and Groq.

## Features

- **Career Roadmap Generator**: Generates a 5-phase career learning roadmap sized to your weekly study hours, automatically calibrating overall plan duration (6, 9, 12, or 18 months).
- **Resume Analyzer with Skill-Gap Breakdown**: Compares an uploaded resume against a target job role or job description, breaking requirements down into matched, partial, and missing skills with an overall match score.
- **Skill Tree**: An HTML/CSS skill tree (matched, partial and missing skills by category) with a full-screen view.
- **Downloadable HTML Exports**: The roadmap export has task checkboxes saved in the browser's localStorage, and both exports have print styles and a light/dark toggle.
- **Light and Dark Theme**: Built-in theme switcher with matching light and dark modes across the Streamlit application and exported HTML documents.

## How It Works

- **Streamlit**: Serves the user interface with dual tabs for roadmap planning and resume analysis.
- **Resume Parsing**: Extracts plain text from `.pdf`, `.docx`, and `.txt` files using `pypdf` and `python-docx`.
- **Groq LLMs**: Uses Groq-hosted LLMs; model names are set in roadmap_ai.py and analyzer.py.
- **Retry and Rate-Limit Handling**: Automatically rotates across comma-separated API keys, tracks cooldown windows, and reads `Retry-After` response headers to safely handle free-tier API throttling.

## Setup

Developed with Python 3.14.

1. Clone the repository and enter the directory:
   ```bash
   git clone <repository-url> && cd SkillGraph
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` (`cp` works in Git Bash, macOS and Linux; use `copy` in PowerShell):
   ```bash
   cp .env.example .env
   ```
4. Get a free API key from the Groq console and paste it after `GROQ_API_KEYS=` in `.env` before running.
5. Launch the application:
   ```bash
   streamlit run app.py
   ```

## Known Limits

- **Groq Free-Tier Rate Limits**: Free-tier API keys have strict rate limits; key rotation helps, but high-frequency requests can trigger cooldown waits.
- **Analysis Duration**: A complete resume analysis and verification pipeline takes about 2 minutes to run.
- **Privacy**: Uploaded resume and job description text is sent to Groq for analysis.

## Development Note

This project was built with AI assistance for code generation, interface styling, and troubleshooting.

## What I'd Do Next

- Run independent AI calls in parallel to shorten the roughly 2-minute analysis.
- Add support for local LLM inference (e.g., Ollama) so resumes can be parsed entirely offline without third-party API transmission.
- Add database persistence (SQLite or PostgreSQL) to track roadmap task completion across devices and revisit past analysis reports.
- Support multi-job comparison to find common skill gaps across multiple target job listings at once.
- Add direct export of tailored resume bullet points to downloadable DOCX and PDF formats.
