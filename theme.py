"""
theme.py - Light and Dark theme styling definitions for SkillGraph.
"""

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --bg: #f4f6fb;
  --surface: #ffffff;
  --surface-2: #dfe6f3;
  --text: #0f172a;
  --ink: var(--text);
  --muted: #5b6475;
  --line: #e3e8f2;
  --tag-bg: #e0ecff;
  --tag-text: #1e40af;
  --note-bg: #eff6ff;
  --shadow: 0 12px 32px rgba(15, 23, 42, 0.06);

  /* Accents */
  --blue: #2563eb;
  --deep: #1e3a8a;
  --sky: #60a5fa;
  --amber: #fbbf24;
  --when-bg: #fef3c7;
  --when-text: #92400e;
}

.stApp { background: var(--bg); color: var(--text); }
.stApp, .stApp p, .stApp li, .stApp label, .stApp input { font-family: 'DM Sans', Arial, sans-serif; }
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] { visibility: hidden; height: 0; }
.block-container { max-width: 860px; padding-top: 1.5rem; padding-bottom: 3rem; }

/* ---------- Theme icon button top right ---------- */
.st-key-theme_btn {
  position: fixed;
  top: 14px;
  right: 18px;
  z-index: 1000;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  transition: all 0.2s ease;
}

.st-key-theme_btn:hover {
  background: var(--surface-2);
  border-color: var(--blue);
  transform: translateY(-1px);
}

.st-key-theme_btn button,
.stButton.st-key-theme_btn button {
  width: 40px !important;
  height: 40px !important;
  min-height: 40px !important;
  max-height: 40px !important;
  min-width: 40px !important;
  max-width: 40px !important;
  border-radius: 50% !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 18px !important;
  line-height: 1 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.st-key-theme_btn button:hover,
.st-key-theme_btn button:focus,
.st-key-theme_btn button:active,
.stButton.st-key-theme_btn button:hover,
.stButton.st-key-theme_btn button:focus,
.stButton.st-key-theme_btn button:active {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

.st-key-theme_btn button p,
.stButton.st-key-theme_btn button p {
  margin: 0 !important;
  padding: 0 !important;
  font-size: 18px !important;
  line-height: 1 !important;
  color: var(--text) !important;
}

/* ---------- Hero: the one big animated moment ---------- */
.hero { position: relative; overflow: hidden; border-radius: 24px; padding: 24px 28px 20px; text-align: center; color: #fff;
  background: linear-gradient(120deg, #0f172a, #1e3a8a, #1d4ed8, #0f172a); background-size: 300% 300%;
  animation: drift 16s ease infinite; margin-bottom: 20px; }
.hero-nodes {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.35;
  animation: nodeDrift 24s ease-in-out infinite alternate;
}
.hero-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  background: radial-gradient(ellipse 85% 75% at 50% 60%, rgba(30, 64, 175, 0.55) 0%, rgba(30, 64, 175, 0.28) 45%, rgba(30, 64, 175, 0.08) 75%, transparent 100%);
}
.hero-content {
  position: relative;
  z-index: 1;
  width: 100%;
}

.hero-slim {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  height: 64px;
  min-height: 64px;
  max-height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(120deg, #0f172a, #1e3a8a, #1d4ed8, #0f172a);
  background-size: 300% 300%;
  animation: drift 16s ease infinite;
  margin-bottom: 24px;
  color: #fff;
  box-sizing: border-box;
}
.hero-slim .hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.hero-slim .brand {
  margin-bottom: 0 !important;
  font-size: 18px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.hero-slim .tagline {
  font-size: 14px;
  color: #c7d7f5;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
}

@keyframes nodeDrift {
  0% { transform: scale(1) translate(0, 0); }
  50% { transform: scale(1.05) translate(-14px, 8px); }
  100% { transform: scale(1.02) translate(10px, -8px); }
}
.brand { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 20px; letter-spacing: .2px; margin-bottom: 14px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
.brand svg { display: inline-block; vertical-align: middle; flex-shrink: 0; }
.brand .wordmark { display: inline-flex; align-items: center; gap: 0; }
.brand .wordmark b, .brand b { color: var(--sky); }
.hero h1 { font-family: 'Sora', sans-serif; font-size: clamp(30px, 6vw, 48px); font-weight: 800; line-height: 1.15; margin: 0 0 10px; }
.hero .become { color: #ffffff; opacity: 0.7; font-size: clamp(16px, 2.6vw, 20px); letter-spacing: 0.5px; text-align: center; margin: 0 0 6px; }
.rotator { display: grid; justify-items: center; text-align: center; font-size: clamp(28px, 5.5vw, 44px); font-weight: 700; line-height: 1.2; margin: 0 auto 22px; }
.rotator span { grid-area: 1/1; opacity: 0; color: var(--amber); font-weight: 700; text-align: center;
  animation: cycle 12s infinite; animation-fill-mode: both; }
.hero p.sub { max-width: 560px; margin: 0 auto; color: #c7d7f5; font-size: 17px; line-height: 1.6; }
@keyframes drift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes float { 0%,100%{transform:translate(0,0)} 50%{transform:translate(30px,24px)} }
@keyframes cycle { 0%{opacity:0;transform:translateY(14px)} 3%{opacity:1;transform:none} 14%{opacity:1;transform:none} 17%,100%{opacity:0;transform:translateY(-14px)} }
@keyframes rise { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }

/* ---------- Form ---------- */
[data-testid="stForm"] { background: var(--surface); border: 1px solid var(--line); border-radius: 20px; padding: 28px; box-shadow: var(--shadow); }
.form-title { font-family: 'Sora', sans-serif; font-size: 22px; font-weight: 700; margin: 0 0 4px; }
.form-hint { color: var(--muted); margin: 0 0 18px; }
[data-baseweb="select"] > div, .stTextInput input { border-radius: 12px !important; }
.stApp label p { font-weight: 600; }

/* ---------- Buttons ---------- */
div[data-testid="stFormSubmitButton"] button, .stButton button, .stDownloadButton button {
  border-radius: 12px; font-weight: 700; padding: .7rem 1.2rem; border: 1px solid var(--line); transition: transform .15s, box-shadow .15s; }
div[data-testid="stFormSubmitButton"] button { width: 100%; background: linear-gradient(90deg, #2563eb, #1d4ed8); color: #fff; border: none; font-size: 17px; }
div[data-testid="stFormSubmitButton"] button:hover { transform: translateY(-2px); box-shadow: 0 10px 22px rgba(37, 99, 235, .35); color: #fff; }

/* ---------- Results ---------- */
.result-head { background: var(--surface); border: 1px solid var(--line); border-radius: 20px; padding: 28px; margin-bottom: 18px;
  box-shadow: var(--shadow); animation: rise .6s ease both; }
.career { font-family: 'Sora', sans-serif; font-size: clamp(26px, 5vw, 36px); font-weight: 800; color: var(--deep); margin: 0 0 8px; }
.summary { color: var(--muted); line-height: 1.65; margin: 0 0 14px; }
.tag { display: inline-block; padding: 6px 12px; background: var(--tag-bg); color: var(--tag-text); border-radius: 999px; margin: 4px 6px 4px 0; font-size: 13px; font-weight: 600; }
.tag.sg-chip-skill, .sg-chip-skill { background: #dbeafe; color: #1e40af; border: none; }
.tag.sg-chip-matched, .sg-chip-matched { background: #dcfce7; color: #15803d; border: none; }
.tag.sg-chip-partial, .sg-chip-partial { background: #fef3c7; color: #b45309; border: none; }
.tag.sg-chip-missing, .sg-chip-missing { background: #fee2e2; color: #b91c1c; border: none; }
.note { background: var(--note-bg); border-left: 4px solid var(--blue); padding: 14px 16px; border-radius: 0 12px 12px 0; margin-top: 14px; line-height: 1.6; }
.tips { margin: 12px 0 0 18px; color: var(--text); line-height: 1.7; }

.progress { height: 12px; background: var(--surface-2); border-radius: 999px; overflow: hidden; }
.bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #2563eb); border-radius: 999px; transition: width .8s cubic-bezier(.2, .8, .2, 1); }
.pcount { color: var(--muted); font-size: 14px; margin: 8px 0 20px; }

[data-testid="stVerticalBlockBorderWrapper"] { background: var(--surface); border-radius: 18px; border: 1px solid var(--line); }
.phase-top { display: flex; align-items: center; gap: 14px; }
.badge { flex: 0 0 40px; height: 40px; border-radius: 50%; background: var(--blue); color: #fff; display: flex; align-items: center; justify-content: center; font-family: 'Sora', sans-serif; font-weight: 700; }
.phase-title { font-family: 'Sora', sans-serif; font-size: 19px; font-weight: 700; margin: 0; }
.when { margin-left: auto; font-size: 13px; font-weight: 600; color: var(--when-text); background: var(--when-bg); padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
.phase-blurb { color: var(--muted); margin: 10px 0 6px; line-height: 1.6; }
.goal { background: linear-gradient(135deg, #0f172a, #1e3a8a); color: #fff; border-radius: 18px; padding: 26px; margin-top: 18px; }
.goal h4 { font-family: 'Sora', sans-serif; margin: 0 0 8px; }
.goal p { color: #dbeafe; line-height: 1.6; margin: 0; }
.foot { text-align: center; color: var(--muted); padding: 28px 0 0; font-size: 14px; }

/* Charts and Graphviz */
[data-testid="stGraphvizChart"], [data-testid="stGraphvizChart"] svg { background: transparent !important; }
[data-testid="stVegaLiteChart"], .vega-embed { background: transparent !important; }

@media (max-width:600px) {
  .hero { padding:20px 18px; }
  .hero-slim { padding: 0 16px; height: 64px; min-height: 64px; }
  .hero-slim .tagline { display: none; }
  .when { display:none; }
}
@media (prefers-reduced-motion: reduce) {
  .hero, .hero-nodes, .hero-slim, .result-head { animation:none !important; }
  .rotator span { animation:none; } .rotator span:first-child { opacity:1; }
}
</style>
"""

DARK_CSS = r"""
<style>
:root {
  --bg: #0b1220;
  --surface: #111a2e;
  --surface-2: #16213a;
  --text: #e5ecf8;
  --ink: #e5ecf8;
  --muted: #9aa8c2;
  --line: #24304d;
  --tag-bg: #1c2c52;
  --tag-text: #bcd2ff;
  --note-bg: #14223f;
  --shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  --when-bg: #2d2615;
  --when-text: #fde68a;
  --deep: #93c5fd;
}

/* Base App Dark Overrides */
.stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {
  color: var(--text);
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
  color: var(--text) !important;
}

.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown strong {
  color: var(--text) !important;
}

.stApp label p {
  color: var(--text) !important;
}

/* Preserve hero and banner contrast */
.hero h1 { color: #ffffff !important; }
.hero .become { color: #ffffff !important; opacity: 0.7; }
.hero .rotator span { color: var(--amber) !important; }
.hero p.sub { color: #c7d7f5 !important; }
.hero .brand b { color: var(--sky) !important; }
.hero-slim { color: #ffffff !important; }
.hero-slim .brand b { color: var(--sky) !important; }
.hero-slim .tagline { color: #c7d7f5 !important; }
.badge { color: #ffffff !important; }
.goal h4 { color: #ffffff !important; }
.goal p { color: #dbeafe !important; }

/* Placeholder color in all inputs */
::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder,
div[data-baseweb="base-input"] input::placeholder,
div[data-baseweb="base-input"] textarea::placeholder,
[data-baseweb="select"] input::placeholder,
[data-baseweb="select"] div[data-placeholder="true"],
[data-baseweb="select"] div[aria-hidden="true"],
textarea::placeholder,
input::placeholder {
  color: #5b6475 !important;
  -webkit-text-fill-color: #5b6475 !important;
  opacity: 1 !important;
}

/* Inputs & Textareas - 1px --line border, 1px #2563eb on focus with soft blue glow */
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="base-input"] {
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  outline: none !important;
  box-shadow: none !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
  border: 1px solid #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
  outline: none !important;
}

.stTextInput input,
.stTextArea textarea,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea,
.stApp textarea,
.stApp input[type="text"],
textarea,
input[type="text"] {
  background-color: transparent !important;
  color: #0f172a !important;
  caret-color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus,
div[data-baseweb="base-input"] input:focus,
div[data-baseweb="base-input"] textarea:focus {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* Selectboxes and Multiselects */
[data-baseweb="select"] > div {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  outline: none !important;
  box-shadow: none !important;
}

[data-baseweb="select"] > div:hover {
  background-color: var(--surface-2) !important;
  border-color: var(--blue) !important;
}

[data-baseweb="select"] > div:focus-within {
  background-color: var(--surface-2) !important;
  border: 1px solid #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
  outline: none !important;
}

[data-baseweb="select"] input {
  background-color: transparent !important;
  color: #0f172a !important;
  caret-color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  border: none !important;
  outline: none !important;
}

[data-baseweb="select"] [role="combobox"] {
  background-color: transparent !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
}

[data-baseweb="select"] svg {
  fill: #475569 !important;
  color: #475569 !important;
}

/* Open Dropdown Menus */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[role="listbox"] {
  background-color: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--shadow) !important;
}

li[role="option"] {
  background-color: var(--surface) !important;
  color: var(--text) !important;
}

li[role="option"]:hover,
li[role="option"]:focus,
li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]:hover {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
}

li[role="option"] * {
  color: var(--text) !important;
}

/* Multiselect Tags */
[data-baseweb="tag"],
.stMultiSelect [data-baseweb="tag"] {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 999px !important;
}

[data-baseweb="tag"] span,
.stMultiSelect [data-baseweb="tag"] span {
  color: var(--text) !important;
}

[data-baseweb="tag"] svg,
.stMultiSelect [data-baseweb="tag"] svg {
  fill: var(--text) !important;
  color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background-color: transparent !important;
  border-bottom: 1px solid var(--line) !important;
}

.stTabs [data-baseweb="tab"], button[role="tab"] {
  color: var(--muted) !important;
  background-color: transparent !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"], button[role="tab"][aria-selected="true"] {
  color: var(--text) !important;
}

.stTabs [data-baseweb="tab"] p, button[role="tab"] p {
  color: var(--muted) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] p, button[role="tab"][aria-selected="true"] p {
  color: var(--text) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
  background-color: var(--blue) !important;
}

/* Checkboxes */
.stCheckbox label p, .stCheckbox label span, [data-testid="stCheckbox"] label p, [data-testid="stCheckbox"] label span {
  color: var(--text) !important;
}

.stCheckbox input[type="checkbox"], [data-testid="stCheckbox"] input[type="checkbox"] {
  accent-color: var(--blue) !important;
}

/* Sliders */
.stSlider [data-baseweb="slider"] div[role="slider"] {
  background-color: var(--blue) !important;
  border-color: var(--surface) !important;
}

.stSlider div[data-testid="stSliderTickBar"] div {
  color: var(--muted) !important;
}

.stSlider [data-testid="stSliderTrack"] {
  background-color: var(--surface-2) !important;
}

.stSlider [data-testid="stSliderTrack"] > div {
  background-color: var(--blue) !important;
}

.stSlider label p {
  color: var(--text) !important;
}

/* File Uploader in Dark Mode — styled to match white input fields */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section {
  background-color: #ffffff !important;
  border: 1px dashed #cbd5e1 !important;
  border-radius: 12px !important;
  color: #475569 !important;
}

[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] section:hover {
  border-color: #94a3b8 !important;
}

[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] div,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section div,
[data-testid="stFileUploader"] section p {
  color: #475569 !important;
  -webkit-text-fill-color: #475569 !important;
}

[data-testid="stFileUploaderDropzone"] svg,
[data-testid="stFileUploader"] section svg {
  fill: #475569 !important;
  color: #475569 !important;
}

.stApp [data-testid="stFileUploaderDropzone"] button,
.stApp [data-testid="stFileUploader"] section button,
.stApp [data-testid="stFileUploader"] button[kind="secondary"],
.stApp [data-testid="stFileUploader"] button[data-testid="baseButton-secondary"],
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploader"] section button {
  background-color: #ffffff !important;
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: none !important;
}

.stApp [data-testid="stFileUploaderDropzone"] button:hover,
.stApp [data-testid="stFileUploader"] section button:hover,
.stApp [data-testid="stFileUploader"] button[kind="secondary"]:hover,
.stApp [data-testid="stFileUploader"] button[data-testid="baseButton-secondary"]:hover,
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploader"] section button:hover {
  background-color: #f1f5f9 !important;
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  border-color: #cbd5e1 !important;
}

.stApp [data-testid="stFileUploaderDropzone"] button p,
.stApp [data-testid="stFileUploaderDropzone"] button span,
.stApp [data-testid="stFileUploader"] section button p,
.stApp [data-testid="stFileUploader"] section button span,
[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploader"] section button p {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
}

/* File chip after upload */
[data-testid="stFileUploaderFileData"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] {
  background-color: #f1f5f9 !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 8px !important;
  color: #0f172a !important;
}

[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  font-weight: 600;
}

[data-testid="stFileUploaderFileData"] small,
[data-testid="stFileUploaderFileData"] span,
[data-testid="stFileUploaderFileData"] div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] small,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] span,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] div {
  color: #475569 !important;
  -webkit-text-fill-color: #475569 !important;
}

.stApp [data-testid="stFileUploaderFileData"] button,
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] button,
[data-testid="stFileUploaderFileData"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #475569 !important;
}

.stApp [data-testid="stFileUploaderFileData"] button:hover,
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] button:hover,
[data-testid="stFileUploaderFileData"] button:hover {
  background-color: #e2e8f0 !important;
  color: #0f172a !important;
}

[data-testid="stFileUploaderFileData"] svg,
[data-testid="stFileUploaderFileData"] button svg,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] svg {
  fill: #475569 !important;
  color: #475569 !important;
}

[data-testid="stFileUploaderFileData"] button:hover svg {
  fill: #0f172a !important;
  color: #0f172a !important;
}

/* Bordered Containers & Forms */
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"], .result-head {
  background: var(--surface) !important;
  border-color: var(--line) !important;
  box-shadow: var(--shadow) !important;
}

/* Alert Boxes (st.info, st.success, st.error, st.warning) */
[data-testid="stAlert"] {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border-color: var(--line) !important;
}

[data-testid="stAlert"] p, [data-testid="stAlert"] div, [data-testid="stAlert"] span {
  color: var(--text) !important;
}

/* Secondary Buttons (Start over, Download, Full Screen Graph) */
.stButton button,
.stDownloadButton button,
button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
  background-color: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--shadow) !important;
}

.stButton button:hover,
.stDownloadButton button:hover,
button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border-color: var(--blue) !important;
}

.stButton button p,
.stDownloadButton button p,
button[kind="secondary"] p,
button[data-testid="baseButton-secondary"] p {
  color: var(--text) !important;
}

/* Primary Buttons ("Generate my roadmap", "Analyze Resume & Match Skills") */
.stButton button[kind="primary"],
.stButton button[data-testid="baseButton-primary"],
button[kind="primary"],
button[data-testid="baseButton-primary"],
div[data-testid="stFormSubmitButton"] button {
  background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
  color: #ffffff !important;
  border: none !important;
  font-weight: 700 !important;
}

.stButton button[kind="primary"]:hover,
.stButton button[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] button:hover {
  background: linear-gradient(90deg, #1d4ed8, #1e40af) !important;
  color: #ffffff !important;
  border: none !important;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.45) !important;
  transform: translateY(-2px);
}

.stButton button[kind="primary"] p,
.stButton button[data-testid="baseButton-primary"] p,
button[kind="primary"] p,
button[data-testid="baseButton-primary"] p,
div[data-testid="stFormSubmitButton"] button p {
  color: #ffffff !important;
}

/* Theme Button in Dark Mode */
.st-key-theme_btn {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--shadow) !important;
}

.st-key-theme_btn:hover {
  background: var(--surface-2) !important;
  border-color: var(--blue) !important;
}

.st-key-theme_btn button,
.stButton.st-key-theme_btn button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--text) !important;
}

.st-key-theme_btn button:hover,
.st-key-theme_btn button:focus,
.st-key-theme_btn button:active,
.stButton.st-key-theme_btn button:hover,
.stButton.st-key-theme_btn button:focus,
.stButton.st-key-theme_btn button:active {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  color: var(--text) !important;
}

.st-key-theme_btn button p,
.stButton.st-key-theme_btn button p {
  color: var(--text) !important;
}

/* Graphviz and Altair transparent backgrounds */
[data-testid="stGraphvizChart"], [data-testid="stGraphvizChart"] svg {
  background: transparent !important;
}

[data-testid="stVegaLiteChart"], .vega-embed {
  background: transparent !important;
}

/* Fullscreen Dialogs / Modals */
[data-testid="stDialog"], [data-testid="stModal"], [role="dialog"], [role="dialog"] > div {
  background-color: var(--surface) !important;
  color: var(--text) !important;
}

[role="dialog"] h2, [role="dialog"] span, [role="dialog"] p {
  color: var(--text) !important;
}

/* ============================================================
   FINAL DARK-MODE OVERRIDE
   Text inputs, textareas, selects & file uploader stay WHITE.
   Only dropdown menus, sliders, expanders & alerts go dark.
   ============================================================ */

/* 5. Open dropdown menus (render in a portal, look fine dark) */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[role="listbox"],
.stApp [data-baseweb="popover"],
.stApp [data-baseweb="menu"],
.stApp ul[role="listbox"] {
  background-color: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--shadow) !important;
}

li[role="option"],
.stApp li[role="option"] {
  background-color: var(--surface) !important;
  color: var(--text) !important;
}

li[role="option"]:hover,
li[role="option"]:focus,
li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]:hover,
.stApp li[role="option"]:hover,
.stApp li[role="option"]:focus,
.stApp li[role="option"][aria-selected="true"],
.stApp li[role="option"][aria-selected="true"]:hover {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
}

li[role="option"] *,
.stApp li[role="option"] * {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

/* 7b. Sliders */
.stApp [data-testid="stSlider"] label,
.stApp [data-testid="stSlider"] label p {
  color: var(--text) !important;
}

.stApp [data-testid="stSlider"] [data-testid="stSliderTrack"] {
  background-color: var(--surface-2) !important;
}

.stApp [data-testid="stSlider"] [data-testid="stSliderTrack"] > div {
  background-color: var(--blue) !important;
}

.stApp [data-baseweb="slider"] div[role="slider"] {
  background-color: var(--blue) !important;
  border: 2px solid var(--surface) !important;
  outline: none !important;
  box-shadow: none !important;
}

.stApp [data-baseweb="slider"] div[role="slider"]:focus {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
}

.stApp [data-testid="stSliderTickBar"] div,
.stApp [data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
  color: var(--muted) !important;
}

/* 7d. Expanders */
.stApp [data-testid="stExpander"] {
  background-color: var(--surface-2) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
}

.stApp [data-testid="stExpander"] details,
.stApp [data-testid="stExpander"] summary {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
}

.stApp [data-testid="stExpander"] summary p,
.stApp [data-testid="stExpander"] summary span {
  color: var(--text) !important;
}

.stApp [data-testid="stExpander"] summary svg {
  fill: var(--muted) !important;
  color: var(--muted) !important;
}

.stApp [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  background-color: var(--surface) !important;
  color: var(--text) !important;
  border-top: 1px solid var(--line) !important;
}

/* 7e. Alert boxes (st.info, st.success, st.warning, st.error) */
.stApp [data-testid="stAlert"] {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
}

.stApp [data-testid="stAlert"] p,
.stApp [data-testid="stAlert"] span,
.stApp [data-testid="stAlert"] div {
  color: var(--text) !important;
}

.stApp div[data-baseweb="notification"] {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
}

/* Final text box text color override: crisp dark text on white inputs */
.stApp textarea,
.stApp input[type="text"],
.stApp input:not([type="checkbox"]):not([type="radio"]):not([type="button"]):not([type="submit"]):not([type="range"]),
.stApp div[data-baseweb="textarea"] textarea,
.stApp div[data-baseweb="input"] input,
.stApp div[data-baseweb="base-input"] textarea,
.stApp div[data-baseweb="base-input"] input,
.stApp div[data-baseweb="select"] input,
.stApp div[data-baseweb="select"] span,
.stApp div[data-baseweb="select"] div[aria-selected],
textarea,
input[type="text"] {
  color: #0f172a !important;
  caret-color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
}

.stApp textarea::placeholder,
.stApp input::placeholder,
.stApp div[data-baseweb="textarea"] textarea::placeholder,
.stApp div[data-baseweb="input"] input::placeholder,
.stApp div[data-baseweb="base-input"] textarea::placeholder,
.stApp div[data-baseweb="base-input"] input::placeholder,
.stApp div[data-baseweb="select"] input::placeholder,
.stApp div[data-baseweb="select"] div[data-placeholder="true"],
.stApp div[data-baseweb="select"] div[aria-hidden="true"],
textarea::placeholder,
input::placeholder {
  color: #5b6475 !important;
  -webkit-text-fill-color: #5b6475 !important;
  opacity: 1 !important;
}

/* ------------------------------------------------------------
   DARK MODE OVERRIDES: CHIPS & SPINNERS
   ------------------------------------------------------------ */

/* 1. Career Roadmap learner skill chips (⚡ ...) in dark mode */
.tag.sg-chip-skill,
span.tag.sg-chip-skill,
.sg-chip-skill,
span.sg-chip-skill,
.stApp .tag.sg-chip-skill,
.stApp span.sg-chip-skill,
.stMarkdown .tag.sg-chip-skill,
.stMarkdown span.sg-chip-skill,
.result-head span.tag.sg-chip-skill,
.result-head .tag.sg-chip-skill {
  background: #1e2a4a !important;
  color: #e2e8f0 !important;
  -webkit-text-fill-color: #e2e8f0 !important;
  border: 1px solid rgba(148, 163, 184, 0.25) !important;
  border-radius: 999px !important;
  padding: 6px 12px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  margin: 4px 6px 4px 0 !important;
  display: inline-block !important;
}

/* 2. Spinner and status text in dark mode */
.stSpinner,
[data-testid="stSpinner"],
[data-testid="stStatusWidget"] {
  color: var(--text) !important;
}

.stSpinner p,
.stSpinner span,
.stSpinner div,
.stSpinner [role="status"],
.stSpinner [role="status"] *,
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span,
[data-testid="stSpinner"] div,
[data-testid="stSpinner"] [role="status"],
[data-testid="stSpinner"] [role="status"] *,
[data-testid="stSpinner"] [data-testid="stMarkdownContainer"] *,
[data-testid="stStatusWidget"] * {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

.stSpinner [data-testid="stSpinnerIcon"],
[data-testid="stSpinner"] [data-testid="stSpinnerIcon"],
[data-testid="stSpinnerIcon"],
.stSpinner span[class*="eafbkhs"],
[data-testid="stSpinner"] span[class*="eafbkhs"],
.stSpinner [role="progressbar"],
[data-testid="stSpinner"] [role="progressbar"],
.stSpinner div > span > span,
[data-testid="stSpinner"] div > span > span,
div[data-testid="stSpinner"] > div > span:first-child,
.stSpinner > div > span:first-child {
  border-color: rgba(96, 165, 250, 0.25) !important;
  border-top-color: #60a5fa !important;
  border-right-color: rgba(96, 165, 250, 0.25) !important;
  border-bottom-color: rgba(96, 165, 250, 0.25) !important;
  border-left-color: rgba(96, 165, 250, 0.25) !important;
}

.stSpinner svg,
.stSpinner [data-testid="stSpinnerIcon"] svg,
[data-testid="stSpinner"] svg,
[data-testid="stSpinner"] [data-testid="stSpinnerIcon"] svg {
  color: #60a5fa !important;
  fill: #60a5fa !important;
  stroke: #60a5fa !important;
}

/* 3. Skills Breakdown chips in dark mode */
.tag.sg-chip-matched,
span.tag.sg-chip-matched,
.sg-chip-matched,
span.sg-chip-matched,
.stApp .tag.sg-chip-matched,
.stApp span.sg-chip-matched,
.stMarkdown .tag.sg-chip-matched,
.stMarkdown span.sg-chip-matched {
  background: rgba(34, 197, 94, 0.15) !important;
  color: #86efac !important;
  -webkit-text-fill-color: #86efac !important;
  border: 1px solid rgba(34, 197, 94, 0.4) !important;
  border-radius: 999px !important;
  padding: 6px 12px !important;
  margin: 4px 6px 4px 0 !important;
  display: inline-block !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}

.tag.sg-chip-partial,
span.tag.sg-chip-partial,
.sg-chip-partial,
span.sg-chip-partial,
.stApp .tag.sg-chip-partial,
.stApp span.sg-chip-partial,
.stMarkdown .tag.sg-chip-partial,
.stMarkdown span.sg-chip-partial {
  background: rgba(245, 158, 11, 0.15) !important;
  color: #fcd34d !important;
  -webkit-text-fill-color: #fcd34d !important;
  border: 1px solid rgba(245, 158, 11, 0.4) !important;
  border-radius: 999px !important;
  padding: 6px 12px !important;
  margin: 4px 6px 4px 0 !important;
  display: inline-block !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}

.tag.sg-chip-missing,
span.tag.sg-chip-missing,
.sg-chip-missing,
span.sg-chip-missing,
.stApp .tag.sg-chip-missing,
.stApp span.sg-chip-missing,
.stMarkdown .tag.sg-chip-missing,
.stMarkdown span.sg-chip-missing {
  background: rgba(239, 68, 68, 0.15) !important;
  color: #fca5a5 !important;
  -webkit-text-fill-color: #fca5a5 !important;
  border: 1px solid rgba(239, 68, 68, 0.4) !important;
  border-radius: 999px !important;
  padding: 6px 12px !important;
  margin: 4px 6px 4px 0 !important;
  display: inline-block !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}
</style>
"""
