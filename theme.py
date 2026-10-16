"""
theme.py - Light and Dark theme styling definitions for SkillGraph.
"""

CSS = """
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
.hero { position: relative; overflow: hidden; border-radius: 24px; padding: 42px 32px 39px; text-align: center; color: #fff;
  background: linear-gradient(120deg, #0f172a, #1e3a8a, #1d4ed8, #0f172a); background-size: 300% 300%;
  animation: drift 16s ease infinite; margin-bottom: 28px; }
.hero::before, .hero::after { content: ""; position: absolute; border-radius: 50%; filter: blur(60px); opacity: .45; }
.hero::before { width: 260px; height: 260px; background: #3b82f6; top: -80px; left: -60px; animation: float 9s ease-in-out infinite; }
.hero::after  { width: 220px; height: 220px; background: #f59e0b; bottom: -100px; right: -40px; opacity: .28; animation: float 11s ease-in-out infinite reverse; }
.hero > * { position: relative; z-index: 1; }
.brand { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 20px; letter-spacing: .2px; margin-bottom: 26px; }
.brand b { color: var(--sky); }
.hero h1 { font-family: 'Sora', sans-serif; font-size: clamp(30px, 6vw, 48px); font-weight: 800; line-height: 1.15; margin: 0 0 14px; }
.rotator-line { display: flex; justify-content: center; align-items: center; gap: 0.35em; font-size: clamp(26px, 5.5vw, 42px); font-weight: 700; line-height: 1.2; color: #dbeafe; margin-bottom: 18px; }
.rotator { display: inline-grid; text-align: left; }
.rotator span { grid-area: 1/1; opacity: 0; color: var(--amber); font-weight: 700; white-space: nowrap;
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

@media (max-width:600px) { .hero { padding:30px 18px; } .when { display:none; } }
@media (prefers-reduced-motion: reduce) {
  .hero, .hero::before, .hero::after, .result-head { animation:none; }
  .rotator span { animation:none; } .rotator span:first-child { opacity:1; }
}
</style>
"""

DARK_CSS = """
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
.hero .rotator-line { color: #dbeafe !important; }
.hero .rotator span { color: var(--amber) !important; }
.hero p.sub { color: #c7d7f5 !important; }
.hero .brand b { color: var(--sky) !important; }
.badge { color: #ffffff !important; }
.goal h4 { color: #ffffff !important; }
.goal p { color: #dbeafe !important; }

/* Placeholder color --muted in all inputs */
::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder,
div[data-baseweb="base-input"] input::placeholder,
div[data-baseweb="base-input"] textarea::placeholder,
[data-baseweb="select"] input::placeholder,
[data-baseweb="select"] div[data-placeholder="true"],
[data-baseweb="select"] div[aria-hidden="true"] {
  color: var(--muted) !important;
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
div[data-baseweb="base-input"] textarea {
  background-color: transparent !important;
  color: var(--text) !important;
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
  color: var(--text) !important;
  border: none !important;
  outline: none !important;
}

[data-baseweb="select"] [role="combobox"] {
  background-color: transparent !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div {
  color: var(--text) !important;
}

[data-baseweb="select"] svg {
  fill: var(--text) !important;
  color: var(--text) !important;
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

/* File Uploader */
[data-testid="stFileUploader"] section {
  background-color: var(--surface) !important;
  border: 1px dashed var(--line) !important;
  color: var(--text) !important;
}

[data-testid="stFileUploader"] section:hover {
  border-color: var(--blue) !important;
}

[data-testid="stFileUploader"] section small, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] div {
  color: var(--muted) !important;
}

[data-testid="stFileUploader"] button {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
  border-color: var(--line) !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] {
  background-color: var(--surface-2) !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
  color: var(--text) !important;
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
</style>
"""
