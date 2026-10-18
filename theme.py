"""
theme.py - Light and Dark theme styling definitions for SkillGraph.
"""

LIGHT_RULES = r"""
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

  /* Card and Expander Shapes & Shadow */
  --sg-card-radius: 18px;
  --sg-card-border-width: 1px;
  --sg-card-shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 4px 12px rgba(15, 23, 42, 0.06);
  --sg-expander-radius: 18px;
  --sg-card-inner-radius: 10px;
}

.stApp { background: var(--bg); color: var(--text); }
.stApp, .stApp p, .stApp li, .stApp label, .stApp input { font-family: 'DM Sans', Arial, sans-serif; }
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stElementToolbar"], .stElementToolbar { visibility: hidden; height: 0; }
[data-testid="stElementToolbar"], .stElementToolbar, [data-testid="stElementToolbarButtonContainer"] {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
  height: 0 !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Hide Streamlit heading anchor link icons and action containers */
[data-testid="stHeaderActionElements"],
[data-testid="stHeadingWithActionElements"] [data-testid="stHeaderActionElements"],
[data-testid="stHeadingWithActionElements"] a,
a[data-testid="stHeaderActionElements"],
a[aria-label="Link to heading"],
.stHeadingActionElements,
h1 a[href^="#"],
h2 a[href^="#"],
h3 a[href^="#"],
h4 a[href^="#"],
h5 a[href^="#"],
h6 a[href^="#"] {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
  width: 0 !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}
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

.theme-toggle-icon {
  position: fixed;
  top: 14px;
  right: 18px;
  z-index: 1001;
  width: 40px;
  height: 40px;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

body:has(.st-key-theme_btn:hover) .theme-toggle-icon,
.st-key-theme_btn:hover ~ * .theme-toggle-icon {
  transform: translateY(-1px);
}

.theme-toggle-svg {
  width: 20px;
  height: 20px;
  display: block;
  color: var(--text);
  stroke: var(--text);
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
  display: none !important;
  margin: 0 !important;
  padding: 0 !important;
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
/* ---------- Form Controls in Light Mode ---------- */
/* 1. Base styles for controls: selectboxes, multiselects, inputs, textareas, file uploader dropzone */
[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[role="group"],
[data-testid="stSelectbox"] .react-aria-ComboBox > div,
[data-testid="stMultiSelect"] div[role="group"],
[data-testid="stMultiSelect"] .react-aria-ComboBox > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"],
[data-testid="stTextInputRootElement"],
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"],
[data-testid="stTextInput"] .react-aria-TextField > div {
  background-color: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: var(--sg-card-inner-radius, 10px) !important;
  min-height: 40px !important;
  box-sizing: border-box !important;
  outline: none !important;
  box-shadow: none !important;
}

div[data-baseweb="textarea"],
[data-testid="stTextAreaRootElement"],
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"] {
  background-color: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: var(--sg-card-inner-radius, 10px) !important;
  min-height: 80px !important;
  box-sizing: border-box !important;
  outline: none !important;
  box-shadow: none !important;
}

[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section {
  background-color: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: var(--sg-card-inner-radius, 10px) !important;
  min-height: 68px !important;
  padding: 12px 16px !important;
  box-sizing: border-box !important;
  outline: none !important;
  box-shadow: none !important;
}

/* BaseWeb container padding if present */
[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
  padding: 0 8px !important;
}
div[data-baseweb="textarea"] {
  padding: 8px 10px !important;
}

/* 2. Hover state */
[data-baseweb="select"] > div:hover,
[data-testid="stSelectbox"] div[role="group"]:hover,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:hover,
[data-testid="stMultiSelect"] div[role="group"]:hover,
[data-testid="stMultiSelect"] .react-aria-ComboBox > div:hover,
div[data-baseweb="input"]:hover,
div[data-baseweb="base-input"]:hover,
[data-testid="stTextInputRootElement"]:hover,
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:hover,
[data-testid="stTextInput"] .react-aria-TextField > div:hover,
div[data-baseweb="textarea"]:hover,
[data-testid="stTextAreaRootElement"]:hover,
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"]:hover,
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] section:hover {
  border: 1px solid #94a3b8 !important;
  border-color: #94a3b8 !important;
}

/* 2b. Focus and focus-within states */
[data-baseweb="select"] > div:focus,
[data-baseweb="select"] > div:focus-within,
[data-testid="stSelectbox"] div[role="group"]:focus,
[data-testid="stSelectbox"] div[role="group"]:focus-within,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:focus,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:focus-within,
[data-testid="stMultiSelect"] div[role="group"]:focus,
[data-testid="stMultiSelect"] div[role="group"]:focus-within,
[data-testid="stMultiSelect"] .react-aria-ComboBox > div:focus,
[data-testid="stMultiSelect"] .react-aria-ComboBox > div:focus-within,
div[data-baseweb="input"]:focus,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus,
div[data-baseweb="base-input"]:focus-within,
[data-testid="stTextInputRootElement"]:focus,
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus,
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextInput"] .react-aria-TextField > div:focus,
[data-testid="stTextInput"] .react-aria-TextField > div:focus-within,
div[data-baseweb="textarea"]:focus,
div[data-baseweb="textarea"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"]:focus,
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stFileUploaderDropzone"]:focus,
[data-testid="stFileUploaderDropzone"]:focus-within,
[data-testid="stFileUploader"] section:focus,
[data-testid="stFileUploader"] section:focus-within {
  border: 1px solid #2563eb !important;
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
  outline: none !important;
}

/* Dragover highlight on file uploader dropzone */
[data-testid="stFileUploaderDropzone"].sg-dragover,
[data-testid="stFileUploader"] section.sg-dragover {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
  background-color: #eff6ff !important;
  transition: border-color 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease !important;
}

/* 3. Placeholder text */
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
[data-testid="stSelectbox"] input::placeholder,
[data-testid="stMultiSelect"] input::placeholder,
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
textarea::placeholder,
input::placeholder {
  color: #64748b !important;
  -webkit-text-fill-color: #64748b !important;
  opacity: 1 !important;
}

/* 3b. Dropdown arrow remains visible */
[data-baseweb="select"] svg,
[data-testid="stSelectbox"] svg,
[data-testid="stMultiSelect"] svg {
  color: #64748b !important;
  fill: #64748b !important;
  visibility: visible !important;
  opacity: 1 !important;
}

[data-testid="stSelectbox"] button:hover svg,
[data-testid="stMultiSelect"] button:hover svg {
  color: #0f172a !important;
  fill: #0f172a !important;
}

/* 4. Inner wrapper elements remain transparent with no border/shadow */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea,
[data-testid="stTextInputField"],
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stSelectbox"] input,
[data-testid="stMultiSelect"] input,
[data-testid="stSelectbox"] button,
[data-testid="stMultiSelect"] button,
[data-testid="stMultiSelectTagsContainer"],
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] span,
[data-baseweb="select"] div {
  background-color: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
}

div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus,
div[data-baseweb="base-input"] input:focus,
div[data-baseweb="base-input"] textarea:focus,
[data-testid="stTextInputField"]:focus,
[data-testid="stTextAreaRootElement"] textarea:focus,
[data-testid="stSelectbox"] input:focus,
[data-testid="stMultiSelect"] input:focus {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}
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
.tag { display: inline-block; padding: 6px 12px; background: var(--tag-bg); color: var(--tag-text); border-radius: 999px; margin: 4px 6px 4px 0; font-size: 13px; font-weight: 600; vertical-align: middle; }
.tag.sg-chip-interest, .sg-chip-interest { display: inline-flex; align-items: center; gap: 6px; vertical-align: middle; }
.tag.sg-chip-interest svg, .sg-chip-interest svg, svg.sg-interest-icon { width: 15px; height: 15px; flex-shrink: 0; display: inline-block; vertical-align: middle; stroke: currentColor; }
.tag.sg-chip-skill, .sg-chip-skill { background: #dbeafe; color: #1e40af; border: none; vertical-align: middle; }
.tag.sg-chip-matched, .sg-chip-matched { background: #dcfce7; color: #15803d; border: none; vertical-align: middle; }
.tag.sg-chip-partial, .sg-chip-partial { background: #fef3c7; color: #b45309; border: none; vertical-align: middle; }
.tag.sg-chip-missing, .sg-chip-missing { background: #fee2e2; color: #b91c1c; border: none; vertical-align: middle; }
.note { background: var(--note-bg); border-left: 4px solid var(--blue); padding: 14px 16px; border-radius: 0 12px 12px 0; margin-top: 14px; line-height: 1.6; }
.tips { margin: 12px 0 0 18px; color: var(--text); line-height: 1.7; }

.progress { height: 12px; background: var(--surface-2); border-radius: 999px; overflow: hidden; }
.bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #2563eb); border-radius: 999px; transition: width .8s cubic-bezier(.2, .8, .2, 1); }
.pcount { color: var(--muted); font-size: 14px; margin: 8px 0 20px; }

/* Page-level wrappers must NEVER look like cards */
.stMainBlockContainer,
[data-testid="stMainBlockContainer"],
.block-container,
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > .main > .block-container,
[data-testid="stAppViewContainer"] > .main > .block-container > div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hero),
div[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .foot),
div[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] [data-testid="stTabs"]),
div[data-testid="stElementContainer"]:has(> .hero),
div[data-testid="stElementContainer"]:has(> .foot),
[data-testid="stTabs"],
[data-baseweb="tab-list"] {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

/* Real Cards in Light Mode */
[class*="st-key-sg_card_"],
[data-baseweb="tab-panel"] [class*="st-key-sg_card_"],
[data-baseweb="tab-panel"] [data-testid="stVerticalBlockBorderWrapper"],
[data-baseweb="tab-panel"] [data-testid="stForm"] {
  background: var(--surface) !important;
  border: var(--sg-card-border-width) solid var(--line) !important;
  border-radius: var(--sg-card-radius) !important;
  box-shadow: var(--sg-card-shadow) !important;
}

/* A card nested inside another card must not get its own shadow or a second border */
[class*="st-key-sg_card_"] [class*="st-key-sg_card_"],
[data-baseweb="tab-panel"] [data-testid="stForm"] [class*="st-key-sg_card_"] {
  border: none !important;
  box-shadow: none !important;
}

/* Expanders in Light Mode */
[data-testid="stExpander"],
.stApp [data-testid="stExpander"],
[data-testid="stExpander"] details {
  border-radius: var(--sg-expander-radius) !important;
  overflow: hidden !important;
}
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

/* ---------- Skill Graph HTML Tree (Light Mode) ---------- */
:root {
  --sg-fs-chrome: 108px;
  --tree-line: #3b82f6;
  --tree-card-width: 13.5em;
  --tree-col-pad: 0.35em;
  --tree-row-gap: 1.0em;
  --tree-root-height: 2.4em;
  --tree-stem-height: 0.8em;
  --tree-stub-height: 0.8em;
  --tree-header-height: 2.0em;
  --tree-skill-height: 1.62em;
  --tree-skill-gap: 0.25em;
  --tree-body-pad: 0.85em;
}

.sg-tree-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin: 14px 0 8px 0;
  box-sizing: border-box;
  font-size: 13px;
  position: relative;
}

.sg-tree-wrapper:not(.sg-tree-fullscreen) {
  --tree-row-gap: 20px;
  --tree-stub-height: 14px;
  --tree-stem-height: 14px;
  --tree-col-pad: 6px;
  --tree-card-max-width: 220px;
  --tree-card-width: 220px;
}

.sg-tree-graph-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  box-sizing: border-box;
}

.sg-tree-graph-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.sg-tree-root-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  z-index: 2;
  margin: 0;
  padding: 0;
}

.sg-tree-root-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: 'DM Sans', Arial, sans-serif;
  font-weight: 700;
  font-size: 1.05em;
  padding: 0.35em 1.2em;
  border-radius: 999em;
  text-align: center;
  background: #1e3a8a;
  color: #ffffff;
  border: 0.1em solid #1e3a8a;
  box-shadow: 0 0.15em 0.5em rgba(15, 23, 42, 0.12);
  z-index: 3;
  line-height: 1.3;
  box-sizing: border-box;
}

.sg-tree-root-stem {
  width: 0.15em;
  height: var(--tree-stem-height, 0.8em);
  background: var(--tree-line, #3b82f6);
  margin: 0 auto;
  z-index: 1;
}

.sg-tree-rows {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  margin: 0;
  padding: 0;
}

.sg-tree-row {
  display: flex;
  justify-content: center;
  align-items: stretch;
  width: 100%;
  position: relative;
  margin-bottom: var(--tree-row-gap, 1.0em);
  box-sizing: border-box;
}

.sg-tree-row:last-child {
  margin-bottom: 0;
}

/* Vertical trunk running down the horizontal center to the next row's bar */
.sg-tree-row:not(:last-child)::before {
  content: "";
  position: absolute;
  top: 0;
  bottom: calc(-1 * var(--tree-row-gap, 1.0em));
  left: 50%;
  transform: translateX(-50%);
  width: 0.15em;
  background: var(--tree-line, #3b82f6);
  z-index: 1;
  pointer-events: none;
}

/* Card columns: no fixed widths */
.sg-tree-card-col {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding-top: var(--tree-stub-height, 0.8em);
  padding-left: var(--tree-col-pad, 0.35em);
  padding-right: var(--tree-col-pad, 0.35em);
  box-sizing: border-box;
  flex: 1 1 0;
  max-width: var(--tree-card-width, 13.5em);
  min-width: 0;
}

/* Left half of horizontal bar */
.sg-tree-card-col::before {
  content: "";
  position: absolute;
  top: 0;
  right: 50%;
  width: 50%;
  height: 0.15em;
  background: var(--tree-line, #3b82f6);
  z-index: 2;
}

/* Right half of horizontal bar AND vertical stub dropping into the card */
.sg-tree-card-col::after {
  content: "";
  position: absolute;
  top: 0;
  left: 50%;
  width: 50%;
  height: var(--tree-stub-height, 0.8em);
  border-top: 0.15em solid var(--tree-line, #3b82f6);
  border-left: 0.15em solid var(--tree-line, #3b82f6);
  box-sizing: border-box;
  z-index: 2;
  background: transparent;
}

.sg-tree-wrapper:not(.sg-tree-fullscreen) .sg-tree-root-stem,
.sg-tree-wrapper:not(.sg-tree-fullscreen) .sg-tree-row:not(:last-child)::before {
  width: 2px;
}
.sg-tree-wrapper:not(.sg-tree-fullscreen) .sg-tree-card-col::before {
  height: 2px;
}
.sg-tree-wrapper:not(.sg-tree-fullscreen) .sg-tree-card-col::after {
  border-top-width: 2px;
  border-left-width: 2px;
}

/* First card in row: omit left half of horizontal bar */
.sg-tree-card-col:first-child::before {
  display: none !important;
}

/* Last card in row: omit right half of horizontal bar, retain vertical stub */
.sg-tree-card-col:last-child::after {
  border-top: none !important;
}

/* Single card in row: omit both left and right halves, retain vertical stub */
.sg-tree-card-col:only-child::before {
  display: none !important;
}
.sg-tree-card-col:only-child::after {
  border-top: none !important;
}

/* Card container: opaque background & z-index above trunk */
.sg-tree-card {
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 3;
  width: 100%;
  border-radius: 0.5em;
  overflow: hidden;
  box-shadow: 0 0.15em 0.5em rgba(15, 23, 42, 0.05);
  background: #ffffff;
  border: 0.08em solid #e2e8f0;
  box-sizing: border-box;
}

.sg-tree-card-header {
  font-family: 'DM Sans', Arial, sans-serif;
  font-size: 0.9em;
  font-weight: 700;
  padding: 0.35em 0.5em;
  text-align: center;
  background: #1e3a8a;
  color: #ffffff;
  border-bottom: 0.08em solid #1e3a8a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
  box-sizing: border-box;
}

.sg-tree-card-body {
  display: flex;
  flex-direction: column;
  padding: 0.35em;
  gap: 0.25em;
  background: #ffffff;
  box-sizing: border-box;
}

.sg-tree-node {
  display: flex;
  align-items: center;
  font-family: 'DM Sans', Arial, sans-serif;
  font-size: 0.82em;
  font-weight: 500;
  padding: 0.25em 0.5em;
  border-radius: 0.25em;
  line-height: 1.3;
  text-align: left;
  box-sizing: border-box;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sg-node-matched {
  background: #2563eb !important;
  color: #ffffff !important;
  border: 0.08em solid #1d4ed8 !important;
}

.sg-node-partial {
  background: #fbbf24 !important;
  color: #0f172a !important;
  border: 0.08em solid #f59e0b !important;
}

.sg-node-missing {
  background: transparent !important;
  color: #1e293b !important;
  border: 0.1em solid #94a3b8 !important;
}

.sg-tree-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  width: 100%;
  flex-shrink: 0;
}

.sg-tree-legend .sg-tree-node {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
}

/* Fullscreen Dialog styling & resize handle cleanup */
[data-testid="stDialogResizeHandle"],
div[data-testid="stDialog"] [data-testid="stDialogResizeHandle"],
div.stDialog [data-testid="stDialogResizeHandle"],
div[role="dialog"] [data-testid="stDialogResizeHandle"],
.stDialogResizeHandle,
[class*="stDialogResizeHandle"],
[class*="resizeHandle"] {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
  width: 0 !important;
  height: 0 !important;
}

/* Stop background page from scrolling when dialog is open */
body:has([data-testid="stDialog"]) [data-testid="stMain"],
body:has([data-testid="stDialog"]) {
  overflow: hidden !important;
}

[data-testid="stDialog"] {
  overflow: hidden !important;
  display: flex !important;
  justify-content: center !important;
  align-items: flex-start !important;
  padding: 24px 0 !important;
  box-sizing: border-box !important;
}

div[data-testid="stDialog"] > div,
div[role="dialog"] {
  width: 95vw !important;
  max-width: 95vw !important;
  height: calc(100dvh - 48px) !important;
  max-height: calc(100dvh - 48px) !important;
  margin: 0 auto !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  box-sizing: border-box !important;
  padding: 16px 24px !important;
}

div[data-testid="stDialog"] *,
div[role="dialog"] * {
  scrollbar-width: none !important;
}

div[data-testid="stDialog"] *::-webkit-scrollbar,
div[role="dialog"] *::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

div[data-testid="stDialog"] [data-testid="stDialogBody"],
div[role="dialog"] [data-testid="stDialogBody"],
div[data-testid="stDialog"] [data-testid="stVerticalBlock"],
div[role="dialog"] [data-testid="stVerticalBlock"],
div[data-testid="stDialog"] [data-testid="stVerticalBlock"] > div,
div[role="dialog"] [data-testid="stVerticalBlock"] > div,
div[data-testid="stDialog"] .stElementContainer,
div[role="dialog"] .stElementContainer,
div[data-testid="stDialog"] .stMarkdown,
div[role="dialog"] .stMarkdown,
div[data-testid="stDialog"] [data-testid="stMarkdownContainer"],
div[role="dialog"] [data-testid="stMarkdownContainer"] {
  overflow: hidden !important;
  box-sizing: border-box !important;
  padding: 0 !important;
  margin: 0 !important;
}

div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] [data-testid="stDialogHeader"] h2,
div[role="dialog"] h2 {
  text-align: left !important;
  margin: 0 0 8px 0 !important;
  padding: 0 !important;
  font-size: clamp(16px, 2vh, 20px) !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  flex-shrink: 0 !important;
  line-height: 1.3 !important;
}

div[data-testid="stDialog"] button[aria-label="Close"],
div[role="dialog"] button[aria-label="Close"] {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 32px !important;
  height: 32px !important;
  border-radius: 50% !important;
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  color: #0f172a !important;
  transition: background-color 0.15s ease !important;
}

div[data-testid="stDialog"] button[aria-label="Close"]:hover,
div[role="dialog"] button[aria-label="Close"]:hover {
  background-color: rgba(15, 23, 42, 0.08) !important;
  border-radius: 50% !important;
}

/* Fullscreen Tree rules: explicit 100dvh - chrome height, size container, legend pinned below */
.sg-tree-fullscreen {
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  align-items: center !important;
  width: 100% !important;
  height: calc(100dvh - var(--sg-fs-chrome, 108px)) !important;
  max-height: calc(100dvh - var(--sg-fs-chrome, 108px)) !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
}

.sg-tree-fullscreen .sg-tree-graph-area {
  container-type: size;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-items: center !important;
  width: 100% !important;
  flex: 1 1 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  padding: 0 !important;
  margin: 0 auto !important;
}

.sg-tree-fullscreen .sg-tree-graph-inner {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  font-size: clamp(8px, min(100cqw / var(--sg-w, 50), 100cqh / var(--sg-h, 30)), 28px);
}

.sg-tree-fullscreen .sg-tree-root-container {
  flex-shrink: 0 !important;
}

.sg-tree-fullscreen .sg-tree-rows {
  width: 100% !important;
}

.sg-tree-fullscreen .sg-tree-legend {
  flex: none !important;
  flex-shrink: 0 !important;
  margin-top: auto !important;
  padding-top: 8px !important;
  padding-bottom: 2px !important;
  font-size: 12px !important;
  z-index: 10 !important;
  width: 100% !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}


@media (max-width:600px) {
  .hero { padding:20px 18px; }
  .hero-slim { padding: 0 16px; height: 64px; min-height: 64px; }
  .hero-slim .tagline { display: none; }
  .when { display:none; }
  .sg-tree-wrapper:not(.sg-tree-fullscreen) {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
    padding-bottom: 8px;
  }
  .sg-tree-wrapper:not(.sg-tree-fullscreen) .sg-tree-row {
    min-width: 440px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .hero, .hero-nodes, .hero-slim, .result-head { animation:none !important; }
  .rotator span { animation:none; } .rotator span:first-child { opacity:1; }
}

/* ============================================================
   CURSOR STYLES: Default cursor for non-editable text & content
   ============================================================ */
html,
body,
.stApp,
h1, h2, h3, h4, h5, h6,
p, span, div, li, ul, ol,
table, th, td, caption,
[data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"],
.tag, .tag *, .badge, .badge *,
.career, .summary, .note, .note *, .tips, .tips *, .goal, .goal *, .result-head, .pcount,
.sg-tree-wrapper, .sg-tree-wrapper *,
.sg-tree-card, .sg-tree-card *,
.sg-tree-card-header, .sg-tree-card-body,
.sg-tree-node, .sg-tree-node *,
.sg-tree-legend, .sg-tree-legend *,
.sg-tree-root-pill, .sg-tree-root-pill *,
[data-testid="stVegaLiteChart"], [data-testid="stVegaLiteChart"] * {
  cursor: default;
}

/* ============================================================
   CURSOR STYLES: Clickable interactive elements
   ============================================================ */
/* Tabs and all their inner elements */
[role="tab"],
[role="tab"] *,
[role="tab"] p,
[role="tab"] div,
[role="tab"] span,
button[role="tab"],
button[role="tab"] *,
button[role="tab"] p,
button[role="tab"] div,
div[role="tab"],
div[role="tab"] *,
div[role="tab"] p,
div[role="tab"] div,
[data-baseweb="tab"],
[data-baseweb="tab"] *,
[data-baseweb="tab"] p,
[data-baseweb="tab"] div,
[data-testid="stTab"],
[data-testid="stTab"] *,
[data-testid="stTab"] p,
[data-testid="stTab"] div,
[data-testid="stTabs"] [role="tab"],
[data-testid="stTabs"] [role="tab"] *,
[data-testid="stTabs"] [role="tab"] p,
[data-testid="stTabs"] [role="tab"] div,
[data-testid="stTabs"] button,
[data-testid="stTabs"] button *,
div[data-baseweb="tab-list"] button,
div[data-baseweb="tab-list"] button *,
div[data-baseweb="tab-list"] [role="tab"],
div[data-baseweb="tab-list"] [role="tab"] *,

/* Expander summaries */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
details summary,
details summary *,
summary,
summary *,

/* All buttons and their inner text */
button,
button *,
div[data-testid="stButton"] button,
div[data-testid="stButton"] button *,
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stFormSubmitButton"] button *,
div[data-testid="stDownloadButton"] button,
div[data-testid="stDownloadButton"] button *,
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondary"] *,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] *,

/* Theme toggle */
.st-key-theme_btn,
.st-key-theme_btn *,
.stButton.st-key-theme_btn,
.stButton.st-key-theme_btn *,
.theme-toggle-icon,
.theme-toggle-icon *,
.theme-toggle-svg,

/* Dialog close button */
div[data-testid="stDialog"] button[aria-label="Close"],
div[data-testid="stDialog"] button[aria-label="Close"] *,
div[role="dialog"] button[aria-label="Close"],
div[role="dialog"] button[aria-label="Close"] *,
[data-testid="stDialogCloseButton"],
[data-testid="stDialogCloseButton"] *,

/* Checkboxes and labels */
[data-testid="stCheckbox"],
[data-testid="stCheckbox"] *,
label[data-baseweb="checkbox"],
label[data-baseweb="checkbox"] *,

/* Selectbox and multiselect containers and options */
div[data-baseweb="select"],
div[data-baseweb="select"] *:not(input),
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] *:not(input),
[data-testid="stMultiSelect"] div[data-baseweb="select"],
[data-testid="stMultiSelect"] div[data-baseweb="select"] *:not(input),
[data-testid="stSelectbox"] .react-aria-ComboBox,
[data-testid="stSelectbox"] .react-aria-ComboBox *:not(input),
[data-testid="stMultiSelect"] .react-aria-ComboBox,
[data-testid="stMultiSelect"] .react-aria-ComboBox *:not(input),
[data-testid="stSelectbox"] [role="group"],
[data-testid="stSelectbox"] [role="group"] *:not(input),
[data-testid="stMultiSelect"] [role="group"],
[data-testid="stMultiSelect"] [role="group"] *:not(input),
[data-testid="stSelectbox"] button,
[data-testid="stSelectbox"] button *,
[data-testid="stMultiSelect"] button,
[data-testid="stMultiSelect"] button *,
[role="listbox"],
[role="listbox"] *,
[role="option"],
[role="option"] *,
li[role="option"],
li[role="option"] *,
.react-aria-ListBoxItem,
.react-aria-ListBoxItem *,
[data-baseweb="menu"],
[data-baseweb="menu"] *,
[data-baseweb="popover"] li,
[data-baseweb="popover"] li *,
[data-baseweb="tag"],
[data-baseweb="tag"] *,

/* File uploader dropzone and Browse button */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section *,
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button *,

/* Links */
a,
a * {
  cursor: pointer !important;
}

/* ============================================================
   CURSOR STYLES: Slider (track, thumb, value text)
   ============================================================ */
/* Slider track */
[data-testid="stSlider"] [data-baseweb="slider"],
[data-testid="stSlider"] [data-baseweb="slider"] *,
[data-testid="stSlider"] [role="group"],
[data-testid="stSlider"] [role="group"] *,
[data-testid="stSlider"] div[data-orientation="horizontal"],
[data-testid="stSlider"] div[data-orientation="horizontal"] *,
[data-testid="stSlider"] div[style*="touch-action"],
[data-testid="stSlider"] div[style*="touch-action"] * {
  cursor: pointer !important;
}

/* Slider thumb: pointer */
[data-testid="stSlider"] [role="slider"],
[data-testid="stSlider"] [role="slider"] *,
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"],
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"] *,
[data-testid="stSlider"] input[type="range"] {
  cursor: pointer !important;
}

[data-testid="stSlider"] [role="slider"]:active,
[data-testid="stSlider"] [role="slider"]:active *,
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"]:active,
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"]:active *,
[data-testid="stSlider"] input[type="range"]:active {
  cursor: pointer !important;
}

/* While thumb is held down, lock cursor everywhere to pointer and disable text selection */
body:has([data-testid="stSlider"] [role="slider"]:active),
body:has([data-testid="stSlider"] [role="slider"]:active) * {
  cursor: pointer !important;
}

body:has([data-testid="stSlider"] [role="slider"]:active) {
  user-select: none !important;
  -webkit-user-select: none !important;
}

/* Value text above the thumb gets default */
[data-testid="stSlider"] div[data-testid="stSliderThumbValue"],
[data-testid="stSlider"] div[data-testid="stSliderThumbValue"] *,
[data-testid="stSlider"] [data-testid="stSliderThumbValue"],
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] *,
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] p,
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] div,
[data-testid="stSliderThumbValue"],
[data-testid="stSliderThumbValue"] *,
[data-testid="stSliderThumbValue"] p,
[data-testid="stSliderThumbValue"] div {
  cursor: default !important;
}

/* Slider label & tick bar */
[data-testid="stSlider"] label,
[data-testid="stSlider"] label *,
[data-testid="stSlider"] div[data-testid="stSliderTickBar"],
[data-testid="stSlider"] div[data-testid="stSliderTickBar"] *,
[data-testid="stSlider"] [data-testid="stSliderTickBar"],
[data-testid="stSlider"] [data-testid="stSliderTickBar"] *,
[data-testid="stSlider"] [data-testid="stSliderTickBar"] p,
[data-testid="stSlider"] [data-testid="stSliderTickBar"] div,
[data-testid="stSliderTickBar"],
[data-testid="stSliderTickBar"] *,
[data-testid="stSliderTickBar"] p,
[data-testid="stSliderTickBar"] div {
  cursor: default !important;
}

/* ============================================================
   CURSOR STYLES: Text inputs & editable typing areas
   ============================================================ */
input[type="text"],
input[type="search"],
input[type="number"],
input[type="email"],
input[type="password"],
input:not([type]),
textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea,
div[data-baseweb="select"] input,
[data-testid="stSelectbox"] input,
[data-testid="stMultiSelect"] input {
  cursor: text !important;
}

/* ============================================================
   CURSOR STYLES: Disabled controls
   ============================================================ */
:disabled,
:disabled *,
[disabled],
[disabled] *,
button:disabled,
button:disabled *,
button[disabled],
button[disabled] *,
button[aria-disabled="true"],
button[aria-disabled="true"] *,
input:disabled,
textarea:disabled,
select:disabled,
[aria-disabled="true"],
[aria-disabled="true"] *,
[data-disabled="true"],
[data-disabled="true"] *,
[data-testid="stButton"] button:disabled,
[data-testid="stButton"] button:disabled *,
[data-testid="stButton"] button[disabled],
[data-testid="stButton"] button[disabled] *,
div[data-testid="stButton"] button:disabled,
div[data-testid="stButton"] button:disabled *,
div[data-testid="stButton"] button[disabled],
div[data-testid="stButton"] button[disabled] *,
div[data-testid="stFormSubmitButton"] button:disabled,
div[data-testid="stFormSubmitButton"] button:disabled *,
div[data-testid="stFormSubmitButton"] button[disabled],
div[data-testid="stFormSubmitButton"] button[disabled] *,
div[data-testid="stDownloadButton"] button:disabled,
div[data-testid="stDownloadButton"] button:disabled *,
div[data-testid="stDownloadButton"] button[disabled],
div[data-testid="stDownloadButton"] button[disabled] *,
[data-testid="stBaseButton-secondary"]:disabled,
[data-testid="stBaseButton-secondary"]:disabled *,
[data-testid="stBaseButton-secondary"][disabled],
[data-testid="stBaseButton-secondary"][disabled] *,
[data-testid="stBaseButton-primary"]:disabled,
[data-testid="stBaseButton-primary"]:disabled *,
[data-testid="stBaseButton-primary"][disabled],
[data-testid="stBaseButton-primary"][disabled] * {
  cursor: not-allowed !important;
}
"""

DARK_RULES = r"""
:root[data-sg-theme="dark"] {

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

  /* Card and Expander Shapes & Shadow */
  --sg-card-radius: 18px;
  --sg-card-border-width: 1px;
  --sg-card-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  --sg-expander-radius: 18px;
  --sg-card-inner-radius: 10px;
  --tree-line: #60a5fa;

/* Base App Dark Overrides */
[data-testid="stElementToolbar"],
.stElementToolbar,
[data-testid="stElementToolbarButtonContainer"] {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
  height: 0 !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Hide Streamlit heading anchor link icons and action containers */
[data-testid="stHeaderActionElements"],
[data-testid="stHeadingWithActionElements"] [data-testid="stHeaderActionElements"],
[data-testid="stHeadingWithActionElements"] a,
a[data-testid="stHeaderActionElements"],
a[aria-label="Link to heading"],
.stHeadingActionElements,
h1 a[href^="#"],
h2 a[href^="#"],
h3 a[href^="#"],
h4 a[href^="#"],
h5 a[href^="#"],
h6 a[href^="#"] {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
  width: 0 !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.theme-toggle-svg {
  color: var(--text) !important;
  stroke: var(--text) !important;
}

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

.stMarkdown, .stMarkdown p, .stMarkdown span:not(.stMarkdownColoredText), .stMarkdown li, .stMarkdown strong {
  color: var(--text) !important;
}

/* Other Requirements status words in dark mode */
[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText[style*="21, 130, 55"],
[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText[style*="21,130,55"],
[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText[style*="green"],
[class*="st-key-sg_card_other_reqs"] span[style*="21, 130, 55"],
[class*="st-key-sg_card_other_reqs"] span[style*="21,130,55"],
[class*="st-key-sg_card_other_reqs"] span[style*="green"],
.stMarkdown span.stMarkdownColoredText[style*="21, 130, 55"],
.stMarkdown span.stMarkdownColoredText[style*="21,130,55"],
.stMarkdown span.stMarkdownColoredText[style*="green"],
.stMarkdownColoredText[style*="21, 130, 55"],
.stMarkdownColoredText[style*="21,130,55"],
.stMarkdownColoredText[style*="green"] {
  color: #86efac !important;
  -webkit-text-fill-color: #86efac !important;
}

[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText[style*="49, 51, 63"],
[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText[style*="49,51,63"],
[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText[style*="gray"],
[class*="st-key-sg_card_other_reqs"] span[style*="49, 51, 63"],
[class*="st-key-sg_card_other_reqs"] span[style*="49,51,63"],
[class*="st-key-sg_card_other_reqs"] span[style*="gray"],
.stMarkdown span.stMarkdownColoredText[style*="49, 51, 63"],
.stMarkdown span.stMarkdownColoredText[style*="49,51,63"],
.stMarkdown span.stMarkdownColoredText[style*="gray"],
.stMarkdownColoredText[style*="49, 51, 63"],
.stMarkdownColoredText[style*="49,51,63"],
.stMarkdownColoredText[style*="gray"],
[class*="st-key-sg_card_other_reqs"] .stMarkdownColoredText:not([style*="21, 130, 55"]):not([style*="21,130,55"]):not([style*="green"]) {
  color: #94a3b8 !important;
  -webkit-text-fill-color: #94a3b8 !important;
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

/* Phase description text (muted paragraph under phase title) */
.phase-blurb,
p.phase-blurb,
.stMarkdown p.phase-blurb,
.stApp p.phase-blurb,
div[data-testid="stMarkdownContainer"] p.phase-blurb {
  color: #94a3b8 !important;
}

/* ---------- Form Controls in Dark Mode ---------- */
/* 1. Base styles for controls: selectboxes, multiselects, inputs, textareas, file uploader dropzone */
[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[role="group"],
[data-testid="stSelectbox"] .react-aria-ComboBox > div,
[data-testid="stMultiSelect"] div[role="group"],
[data-testid="stMultiSelect"] .react-aria-ComboBox > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"],
[data-testid="stTextInputRootElement"],
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"],
[data-testid="stTextInput"] .react-aria-TextField > div {
  background-color: #0b1220 !important;
  border: 1px solid rgba(148, 163, 184, 0.35) !important;
  border-radius: var(--sg-card-inner-radius, 10px) !important;
  min-height: 40px !important;
  box-sizing: border-box !important;
  outline: none !important;
  box-shadow: none !important;
}

div[data-baseweb="textarea"],
[data-testid="stTextAreaRootElement"],
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"] {
  background-color: #0b1220 !important;
  border: 1px solid rgba(148, 163, 184, 0.35) !important;
  border-radius: var(--sg-card-inner-radius, 10px) !important;
  min-height: 80px !important;
  box-sizing: border-box !important;
  outline: none !important;
  box-shadow: none !important;
}

[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section {
  background-color: #0b1220 !important;
  border: 1px solid rgba(148, 163, 184, 0.35) !important;
  border-radius: var(--sg-card-inner-radius, 10px) !important;
  min-height: 68px !important;
  padding: 12px 16px !important;
  box-sizing: border-box !important;
  outline: none !important;
  box-shadow: none !important;
}

/* BaseWeb container padding if present */
[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
  padding: 0 8px !important;
}
div[data-baseweb="textarea"] {
  padding: 8px 10px !important;
}

/* 2. Hover state */
[data-baseweb="select"] > div:hover,
[data-testid="stSelectbox"] div[role="group"]:hover,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:hover,
[data-testid="stMultiSelect"] div[role="group"]:hover,
[data-testid="stMultiSelect"] .react-aria-ComboBox > div:hover,
div[data-baseweb="input"]:hover,
div[data-baseweb="base-input"]:hover,
[data-testid="stTextInputRootElement"]:hover,
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:hover,
[data-testid="stTextInput"] .react-aria-TextField > div:hover,
div[data-baseweb="textarea"]:hover,
[data-testid="stTextAreaRootElement"]:hover,
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"]:hover,
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] section:hover {
  border: 1px solid #64748b !important;
  border-color: #64748b !important;
}

/* 2b. Focus and focus-within states */
[data-baseweb="select"] > div:focus,
[data-baseweb="select"] > div:focus-within,
[data-testid="stSelectbox"] div[role="group"]:focus,
[data-testid="stSelectbox"] div[role="group"]:focus-within,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:focus,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:focus-within,
[data-testid="stMultiSelect"] div[role="group"]:focus,
[data-testid="stMultiSelect"] div[role="group"]:focus-within,
[data-testid="stMultiSelect"] .react-aria-ComboBox > div:focus,
[data-testid="stMultiSelect"] .react-aria-ComboBox > div:focus-within,
div[data-baseweb="input"]:focus,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus,
div[data-baseweb="base-input"]:focus-within,
[data-testid="stTextInputRootElement"]:focus,
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus,
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextInput"] .react-aria-TextField > div:focus,
[data-testid="stTextInput"] .react-aria-TextField > div:focus-within,
div[data-baseweb="textarea"]:focus,
div[data-baseweb="textarea"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"]:focus,
[data-testid="stTextArea"] [data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stFileUploaderDropzone"]:focus,
[data-testid="stFileUploaderDropzone"]:focus-within,
[data-testid="stFileUploader"] section:focus,
[data-testid="stFileUploader"] section:focus-within {
  border: 1px solid #3b82f6 !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
  outline: none !important;
}

/* Dragover highlight on file uploader dropzone */
[data-testid="stFileUploaderDropzone"].sg-dragover,
[data-testid="stFileUploader"] section.sg-dragover {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
  background-color: #0f1c36 !important;
  transition: border-color 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease !important;
}

/* 3. Placeholder text */
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
[data-testid="stSelectbox"] input::placeholder,
[data-testid="stMultiSelect"] input::placeholder,
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
textarea::placeholder,
input::placeholder {
  color: #94a3b8 !important;
  -webkit-text-fill-color: #94a3b8 !important;
  opacity: 1 !important;
}

/* 3b. Dropdown arrow */
[data-baseweb="select"] svg,
[data-testid="stSelectbox"] svg,
[data-testid="stMultiSelect"] svg {
  color: #94a3b8 !important;
  fill: #94a3b8 !important;
  visibility: visible !important;
  opacity: 1 !important;
}

[data-testid="stSelectbox"] button:hover svg,
[data-testid="stMultiSelect"] button:hover svg {
  color: #e5ecf8 !important;
  fill: #e5ecf8 !important;
}

/* 4. Inner wrapper elements remain transparent with no border/shadow */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea,
[data-testid="stTextInputField"],
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stSelectbox"] input,
[data-testid="stMultiSelect"] input,
[data-testid="stSelectbox"] button,
[data-testid="stMultiSelect"] button,
[data-testid="stMultiSelectTagsContainer"],
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] span,
[data-baseweb="select"] > div > div {
  background-color: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: #e5ecf8 !important;
  caret-color: #e5ecf8 !important;
  -webkit-text-fill-color: #e5ecf8 !important;
}

div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus,
div[data-baseweb="base-input"] input:focus,
div[data-baseweb="base-input"] textarea:focus,
[data-testid="stTextInputField"]:focus,
[data-testid="stTextAreaRootElement"] textarea:focus,
[data-testid="stSelectbox"] input:focus,
[data-testid="stMultiSelect"] input:focus {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
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

/* Unchecked Checkbox */
[data-testid="stCheckbox"] label > div:first-of-type,
[data-testid="stCheckbox"] label > span + div,
[data-testid="stCheckbox"] label > div:not([data-testid="stWidgetLabel"]),
[data-testid="stCheckbox"] [data-baseweb="checkbox"] > span:first-child,
label[data-baseweb="checkbox"] > span:first-child {
  background-color: transparent !important;
  border: 1.5px solid #64748b !important;
  border-radius: 4px !important;
  transition: border-color 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease !important;
}

/* Hover Checkbox (Unchecked) */
[data-testid="stCheckbox"]:hover label > div:first-of-type,
[data-testid="stCheckbox"]:hover label > span + div,
[data-testid="stCheckbox"] label:hover > div:first-of-type,
[data-testid="stCheckbox"] label:hover > span + div,
[data-testid="stCheckbox"]:hover [data-baseweb="checkbox"] > span:first-child,
label[data-baseweb="checkbox"]:hover > span:first-child {
  border-color: #94a3b8 !important;
}

/* Checked Checkbox */
[data-testid="stCheckbox"][data-selected="true"] label > div:first-of-type,
[data-testid="stCheckbox"][data-selected="true"] label > span + div,
[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type,
[data-testid="stCheckbox"] label[data-selected="true"] > span + div,
[data-testid="stCheckbox"]:has(input:checked) label > div:first-of-type,
[data-testid="stCheckbox"]:has(input:checked) label > span + div,
[data-testid="stCheckbox"] label:has(input:checked) > div:first-of-type,
[data-testid="stCheckbox"] label:has(input:checked) > span + div,
[data-testid="stCheckbox"] [data-baseweb="checkbox"][aria-checked="true"] > span:first-child,
label[data-baseweb="checkbox"][aria-checked="true"] > span:first-child {
  background-color: #2563eb !important;
  border: 1.5px solid #2563eb !important;
}

[data-testid="stCheckbox"][data-selected="true"]:hover label > div:first-of-type,
[data-testid="stCheckbox"][data-selected="true"]:hover label > span + div,
[data-testid="stCheckbox"]:has(input:checked):hover label > div:first-of-type,
[data-testid="stCheckbox"]:has(input:checked):hover label > span + div {
  background-color: #2563eb !important;
  border-color: #2563eb !important;
}

/* White Checkbox Tick */
[data-testid="stCheckbox"] svg,
[data-testid="stCheckbox"] svg polyline,
[data-testid="stCheckbox"] svg path {
  stroke: #ffffff !important;
  color: #ffffff !important;
  fill: none !important;
}

/* Subtle Focus Ring */
[data-testid="stCheckbox"]:has(input:focus-visible) label > div:first-of-type,
[data-testid="stCheckbox"]:has(input:focus-visible) label > span + div,
[data-testid="stCheckbox"] label:has(input:focus-visible) > div:first-of-type,
[data-testid="stCheckbox"] label:has(input:focus-visible) > span + div,
[data-testid="stCheckbox"] [data-focus-visible="true"] > div:first-of-type,
[data-testid="stCheckbox"] [data-focus-visible="true"] > span + div,
[data-testid="stCheckbox"]:has([data-focus-visible="true"]) label > div:first-of-type,
[data-testid="stCheckbox"]:has([data-focus-visible="true"]) label > span + div {
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.4) !important;
  outline: none !important;
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

/* File Uploader in Dark Mode */
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] div,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section div,
[data-testid="stFileUploader"] section p {
  color: #94a3b8 !important;
  -webkit-text-fill-color: #94a3b8 !important;
}

[data-testid="stFileUploaderDropzone"] svg,
[data-testid="stFileUploader"] section svg {
  fill: #94a3b8 !important;
  color: #94a3b8 !important;
}

/* File uploader Browse button */
.stApp [data-testid="stFileUploaderDropzone"] button,
.stApp [data-testid="stFileUploader"] section button,
.stApp [data-testid="stFileUploader"] button[kind="secondary"],
.stApp [data-testid="stFileUploader"] button[data-testid="baseButton-secondary"],
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploader"] section button {
  background-color: #16213a !important;
  color: #e5ecf8 !important;
  -webkit-text-fill-color: #e5ecf8 !important;
  border: 1px solid rgba(148, 163, 184, 0.35) !important;
  border-radius: 8px !important;
  box-shadow: none !important;
}

.stApp [data-testid="stFileUploaderDropzone"] button:hover,
.stApp [data-testid="stFileUploader"] section button:hover,
.stApp [data-testid="stFileUploader"] button[kind="secondary"]:hover,
.stApp [data-testid="stFileUploader"] button[data-testid="baseButton-secondary"]:hover,
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploader"] section button:hover {
  background-color: #1e2c52 !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  border-color: #64748b !important;
}

.stApp [data-testid="stFileUploaderDropzone"] button p,
.stApp [data-testid="stFileUploaderDropzone"] button span,
.stApp [data-testid="stFileUploader"] section button p,
.stApp [data-testid="stFileUploader"] section button span,
[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploader"] section button p {
  color: #e5ecf8 !important;
  -webkit-text-fill-color: #e5ecf8 !important;
}

/* File chip after upload */
[data-testid="stFileUploaderFileData"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] {
  background-color: #16213a !important;
  border: 1px solid rgba(148, 163, 184, 0.35) !important;
  border-radius: 8px !important;
  color: #e5ecf8 !important;
}

[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
  color: #e5ecf8 !important;
  -webkit-text-fill-color: #e5ecf8 !important;
  font-weight: 600;
}

[data-testid="stFileUploaderFileData"] small,
[data-testid="stFileUploaderFileData"] span,
[data-testid="stFileUploaderFileData"] div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] small,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] span,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] div {
  color: #94a3b8 !important;
  -webkit-text-fill-color: #94a3b8 !important;
}

.stApp [data-testid="stFileUploaderFileData"] button,
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] button,
[data-testid="stFileUploaderFileData"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #94a3b8 !important;
}

.stApp [data-testid="stFileUploaderFileData"] button:hover,
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] button:hover,
[data-testid="stFileUploaderFileData"] button:hover {
  background-color: #1e2c52 !important;
  color: #ffffff !important;
}

[data-testid="stFileUploaderFileData"] svg,
[data-testid="stFileUploaderFileData"] button svg,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] svg {
  fill: #94a3b8 !important;
  color: #94a3b8 !important;
}

[data-testid="stFileUploaderFileData"] button:hover svg {
  fill: #ffffff !important;
  color: #ffffff !important;
}

/* Page-level wrappers must NEVER look like cards */
.stMainBlockContainer,
[data-testid="stMainBlockContainer"],
.block-container,
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > .main > .block-container,
[data-testid="stAppViewContainer"] > .main > .block-container > div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hero),
div[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .foot),
div[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] [data-testid="stTabs"]),
div[data-testid="stElementContainer"]:has(> .hero),
div[data-testid="stElementContainer"]:has(> .foot),
[data-testid="stTabs"],
[data-baseweb="tab-list"] {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

/* Real Cards in Dark Mode */
[class*="st-key-sg_card_"],
[data-baseweb="tab-panel"] [class*="st-key-sg_card_"],
[data-baseweb="tab-panel"] [data-testid="stVerticalBlockBorderWrapper"],
[data-baseweb="tab-panel"] [data-testid="stForm"] {
  background: var(--surface) !important;
  border: var(--sg-card-border-width) solid rgba(148, 163, 184, 0.2) !important;
  border-radius: var(--sg-card-radius) !important;
  box-shadow: var(--sg-card-shadow) !important;
}

/* A card nested inside another card must not get its own shadow or a second border */
[class*="st-key-sg_card_"] [class*="st-key-sg_card_"],
[data-baseweb="tab-panel"] [data-testid="stForm"] [class*="st-key-sg_card_"] {
  border: none !important;
  box-shadow: none !important;
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

/* Fullscreen Dialogs / Modals (Dark Mode) */
[data-testid="stDialogResizeHandle"],
div[data-testid="stDialog"] [data-testid="stDialogResizeHandle"],
div.stDialog [data-testid="stDialogResizeHandle"],
div[role="dialog"] [data-testid="stDialogResizeHandle"],
.stDialogResizeHandle,
[class*="stDialogResizeHandle"],
[class*="resizeHandle"] {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
  width: 0 !important;
  height: 0 !important;
}

[data-testid="stDialog"], [data-testid="stModal"], [role="dialog"], [role="dialog"] > div,
div[data-testid="stDialog"] > div {
  background-color: var(--surface) !important;
  color: var(--text) !important;
}

[role="dialog"] h2, [role="dialog"] span, [role="dialog"] p,
div[data-testid="stDialog"] h2 {
  color: var(--text) !important;
}

/* Fullscreen Dialog Close Button in Dark Mode */
[data-testid="stDialog"] button[aria-label="Close"],
div[role="dialog"] button[aria-label="Close"] {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 32px !important;
  height: 32px !important;
  border-radius: 50% !important;
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  color: #e5ecf8 !important;
  transition: background-color 0.15s ease, color 0.15s ease !important;
}

[data-testid="stDialog"] button[aria-label="Close"] svg,
div[role="dialog"] button[aria-label="Close"] svg {
  stroke: #e5ecf8 !important;
  color: #e5ecf8 !important;
}

[data-testid="stDialog"] button[aria-label="Close"]:hover,
div[role="dialog"] button[aria-label="Close"]:hover {
  background-color: rgba(255, 255, 255, 0.15) !important;
  border-radius: 50% !important;
  color: #ffffff !important;
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
.stApp [data-testid="stExpander"],
[data-testid="stExpander"],
[data-testid="stExpander"] details {
  background-color: var(--surface-2) !important;
  border: var(--sg-card-border-width) solid var(--line) !important;
  border-radius: var(--sg-expander-radius) !important;
  overflow: hidden !important;
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

/* Final text box text color in dark mode: light text on dark controls */
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
  color: #e5ecf8 !important;
  caret-color: #e5ecf8 !important;
  -webkit-text-fill-color: #e5ecf8 !important;
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
  color: #94a3b8 !important;
  -webkit-text-fill-color: #94a3b8 !important;
  opacity: 1 !important;
}

/* ------------------------------------------------------------
   DARK MODE OVERRIDES: CHIPS & SPINNERS
   ------------------------------------------------------------ */

/* 1. Career Roadmap chips in dark mode */
.tag.sg-chip-interest,
span.tag.sg-chip-interest,
.result-head .tag.sg-chip-interest,
.result-head span.tag.sg-chip-interest {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  vertical-align: middle !important;
  color: var(--tag-text) !important;
  -webkit-text-fill-color: var(--tag-text) !important;
  background: var(--tag-bg) !important;
}

.tag.sg-chip-interest svg,
span.tag.sg-chip-interest svg,
.result-head .tag.sg-chip-interest svg,
svg.sg-interest-icon {
  width: 15px !important;
  height: 15px !important;
  flex-shrink: 0 !important;
  display: inline-block !important;
  vertical-align: middle !important;
  stroke: currentColor !important;
  color: currentColor !important;
}

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
  vertical-align: middle !important;
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

/* ---------- Skill Graph Tree (Dark Mode Overrides) ---------- */
& {
  --tree-line: #60a5fa;
}

.sg-tree-root-pill {
  background: #16213a !important;
  color: #e5ecf8 !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 0.15em 0.8em rgba(0, 0, 0, 0.4) !important;
}

.sg-tree-root-stem {
  background: #60a5fa !important;
}

.sg-tree-row:not(:last-child)::before {
  background: #60a5fa !important;
}

.sg-tree-card-col::before {
  background: #60a5fa !important;
}

.sg-tree-card-col::after {
  background: transparent !important;
  border-color: #60a5fa !important;
}

.sg-tree-card {
  border-color: rgba(148, 163, 184, 0.22) !important;
  background: #111a2e !important;
  box-shadow: 0 0.15em 0.8em rgba(0, 0, 0, 0.3) !important;
}

.sg-tree-card-header {
  background: #16213a !important;
  color: #e5ecf8 !important;
  border-bottom-color: rgba(148, 163, 184, 0.2) !important;
}

.sg-tree-card-body {
  background: #111a2e !important;
}

.sg-node-matched,
.sg-tree-node.sg-node-matched,
span.sg-tree-node.sg-node-matched,
div.sg-tree-node.sg-node-matched,
.stApp .sg-node-matched,
.stMarkdown .sg-node-matched {
  background: #2563eb !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  border-color: #3b82f6 !important;
}

.sg-node-partial,
.sg-tree-node.sg-node-partial,
span.sg-tree-node.sg-node-partial,
div.sg-tree-node.sg-node-partial,
.stApp .sg-node-partial,
.stMarkdown .sg-node-partial {
  background: #fbbf24 !important;
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  border-color: #d97706 !important;
}

.sg-node-missing,
.sg-tree-node.sg-node-missing,
span.sg-tree-node.sg-node-missing,
div.sg-tree-node.sg-node-missing,
.stApp .sg-node-missing,
.stMarkdown .sg-node-missing {
  background: transparent !important;
  color: #e5ecf8 !important;
  -webkit-text-fill-color: #e5ecf8 !important;
  border-color: rgba(148, 163, 184, 0.45) !important;
}

/* ============================================================
   CURSOR STYLES: Default cursor for non-editable text & content
   ============================================================ */
&,
  & body,
  & .stApp,
h1, h2, h3, h4, h5, h6,
p, span, div, li, ul, ol,
table, th, td, caption,
[data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"],
.tag, .tag *, .badge, .badge *,
.career, .summary, .note, .note *, .tips, .tips *, .goal, .goal *, .result-head, .pcount,
.sg-tree-wrapper, .sg-tree-wrapper *,
.sg-tree-card, .sg-tree-card *,
.sg-tree-card-header, .sg-tree-card-body,
.sg-tree-node, .sg-tree-node *,
.sg-tree-legend, .sg-tree-legend *,
.sg-tree-root-pill, .sg-tree-root-pill *,
[data-testid="stVegaLiteChart"], [data-testid="stVegaLiteChart"] * {
  cursor: default;
}

/* ============================================================
   CURSOR STYLES: Clickable interactive elements
   ============================================================ */
/* Tabs and all their inner elements */
[role="tab"],
[role="tab"] *,
[role="tab"] p,
[role="tab"] div,
[role="tab"] span,
button[role="tab"],
button[role="tab"] *,
button[role="tab"] p,
button[role="tab"] div,
div[role="tab"],
div[role="tab"] *,
div[role="tab"] p,
div[role="tab"] div,
[data-baseweb="tab"],
[data-baseweb="tab"] *,
[data-baseweb="tab"] p,
[data-baseweb="tab"] div,
[data-testid="stTab"],
[data-testid="stTab"] *,
[data-testid="stTab"] p,
[data-testid="stTab"] div,
[data-testid="stTabs"] [role="tab"],
[data-testid="stTabs"] [role="tab"] *,
[data-testid="stTabs"] [role="tab"] p,
[data-testid="stTabs"] [role="tab"] div,
[data-testid="stTabs"] button,
[data-testid="stTabs"] button *,
div[data-baseweb="tab-list"] button,
div[data-baseweb="tab-list"] button *,
div[data-baseweb="tab-list"] [role="tab"],
div[data-baseweb="tab-list"] [role="tab"] *,

/* Expander summaries */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
details summary,
details summary *,
summary,
summary *,

/* All buttons and their inner text */
button,
button *,
div[data-testid="stButton"] button,
div[data-testid="stButton"] button *,
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stFormSubmitButton"] button *,
div[data-testid="stDownloadButton"] button,
div[data-testid="stDownloadButton"] button *,
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondary"] *,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] *,

/* Theme toggle */
.st-key-theme_btn,
.st-key-theme_btn *,
.stButton.st-key-theme_btn,
.stButton.st-key-theme_btn *,
.theme-toggle-icon,
.theme-toggle-icon *,
.theme-toggle-svg,

/* Dialog close button */
div[data-testid="stDialog"] button[aria-label="Close"],
div[data-testid="stDialog"] button[aria-label="Close"] *,
div[role="dialog"] button[aria-label="Close"],
div[role="dialog"] button[aria-label="Close"] *,
[data-testid="stDialogCloseButton"],
[data-testid="stDialogCloseButton"] *,

/* Checkboxes and labels */
[data-testid="stCheckbox"],
[data-testid="stCheckbox"] *,
label[data-baseweb="checkbox"],
label[data-baseweb="checkbox"] *,

/* Selectbox and multiselect containers and options */
div[data-baseweb="select"],
div[data-baseweb="select"] *:not(input),
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] *:not(input),
[data-testid="stMultiSelect"] div[data-baseweb="select"],
[data-testid="stMultiSelect"] div[data-baseweb="select"] *:not(input),
[data-testid="stSelectbox"] .react-aria-ComboBox,
[data-testid="stSelectbox"] .react-aria-ComboBox *:not(input),
[data-testid="stMultiSelect"] .react-aria-ComboBox,
[data-testid="stMultiSelect"] .react-aria-ComboBox *:not(input),
[data-testid="stSelectbox"] [role="group"],
[data-testid="stSelectbox"] [role="group"] *:not(input),
[data-testid="stMultiSelect"] [role="group"],
[data-testid="stMultiSelect"] [role="group"] *:not(input),
[data-testid="stSelectbox"] button,
[data-testid="stSelectbox"] button *,
[data-testid="stMultiSelect"] button,
[data-testid="stMultiSelect"] button *,
[role="listbox"],
[role="listbox"] *,
[role="option"],
[role="option"] *,
li[role="option"],
li[role="option"] *,
.react-aria-ListBoxItem,
.react-aria-ListBoxItem *,
[data-baseweb="menu"],
[data-baseweb="menu"] *,
[data-baseweb="popover"] li,
[data-baseweb="popover"] li *,
[data-baseweb="tag"],
[data-baseweb="tag"] *,

/* File uploader dropzone and Browse button */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section *,
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button *,

/* Links */
a,
a * {
  cursor: pointer !important;
}

/* ============================================================
   CURSOR STYLES: Slider (track, thumb, value text)
   ============================================================ */
/* Slider track */
[data-testid="stSlider"] [data-baseweb="slider"],
[data-testid="stSlider"] [data-baseweb="slider"] *,
[data-testid="stSlider"] [role="group"],
[data-testid="stSlider"] [role="group"] *,
[data-testid="stSlider"] div[data-orientation="horizontal"],
[data-testid="stSlider"] div[data-orientation="horizontal"] *,
[data-testid="stSlider"] div[style*="touch-action"],
[data-testid="stSlider"] div[style*="touch-action"] * {
  cursor: pointer !important;
}

/* Slider thumb: pointer */
[data-testid="stSlider"] [role="slider"],
[data-testid="stSlider"] [role="slider"] *,
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"],
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"] *,
[data-testid="stSlider"] input[type="range"] {
  cursor: pointer !important;
}

[data-testid="stSlider"] [role="slider"]:active,
[data-testid="stSlider"] [role="slider"]:active *,
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"]:active,
[data-testid="stSlider"] div[style*="translate(-50%, -50%)"]:active *,
[data-testid="stSlider"] input[type="range"]:active {
  cursor: pointer !important;
}

/* While thumb is held down, lock cursor everywhere to pointer and disable text selection */
& body:has([data-testid="stSlider"] [role="slider"]:active),
& body:has([data-testid="stSlider"] [role="slider"]:active) * {
  cursor: pointer !important;
}

& body:has([data-testid="stSlider"] [role="slider"]:active) {
  user-select: none !important;
  -webkit-user-select: none !important;
}

/* Value text above the thumb gets default */
[data-testid="stSlider"] div[data-testid="stSliderThumbValue"],
[data-testid="stSlider"] div[data-testid="stSliderThumbValue"] *,
[data-testid="stSlider"] [data-testid="stSliderThumbValue"],
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] *,
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] p,
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] div,
[data-testid="stSliderThumbValue"],
[data-testid="stSliderThumbValue"] *,
[data-testid="stSliderThumbValue"] p,
[data-testid="stSliderThumbValue"] div {
  cursor: default !important;
}

/* Slider label & tick bar */
[data-testid="stSlider"] label,
[data-testid="stSlider"] label *,
[data-testid="stSlider"] div[data-testid="stSliderTickBar"],
[data-testid="stSlider"] div[data-testid="stSliderTickBar"] *,
[data-testid="stSlider"] [data-testid="stSliderTickBar"],
[data-testid="stSlider"] [data-testid="stSliderTickBar"] *,
[data-testid="stSlider"] [data-testid="stSliderTickBar"] p,
[data-testid="stSlider"] [data-testid="stSliderTickBar"] div,
[data-testid="stSliderTickBar"],
[data-testid="stSliderTickBar"] *,
[data-testid="stSliderTickBar"] p,
[data-testid="stSliderTickBar"] div {
  cursor: default !important;
}

/* ============================================================
   CURSOR STYLES: Text inputs & editable typing areas
   ============================================================ */
input[type="text"],
input[type="search"],
input[type="number"],
input[type="email"],
input[type="password"],
input:not([type]),
textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea,
div[data-baseweb="select"] input,
[data-testid="stSelectbox"] input,
[data-testid="stMultiSelect"] input {
  cursor: text !important;
}

/* ============================================================
   CURSOR STYLES: Disabled controls
   ============================================================ */
:disabled,
:disabled *,
[disabled],
[disabled] *,
button:disabled,
button:disabled *,
button[disabled],
button[disabled] *,
button[aria-disabled="true"],
button[aria-disabled="true"] *,
input:disabled,
textarea:disabled,
select:disabled,
[aria-disabled="true"],
[aria-disabled="true"] *,
[data-disabled="true"],
[data-disabled="true"] *,
[data-testid="stButton"] button:disabled,
[data-testid="stButton"] button:disabled *,
[data-testid="stButton"] button[disabled],
[data-testid="stButton"] button[disabled] *,
div[data-testid="stButton"] button:disabled,
div[data-testid="stButton"] button:disabled *,
div[data-testid="stButton"] button[disabled],
div[data-testid="stButton"] button[disabled] *,
div[data-testid="stFormSubmitButton"] button:disabled,
div[data-testid="stFormSubmitButton"] button:disabled *,
div[data-testid="stFormSubmitButton"] button[disabled],
div[data-testid="stFormSubmitButton"] button[disabled] *,
div[data-testid="stDownloadButton"] button:disabled,
div[data-testid="stDownloadButton"] button:disabled *,
div[data-testid="stDownloadButton"] button[disabled],
div[data-testid="stDownloadButton"] button[disabled] *,
[data-testid="stBaseButton-secondary"]:disabled,
[data-testid="stBaseButton-secondary"]:disabled *,
[data-testid="stBaseButton-secondary"][disabled],
[data-testid="stBaseButton-secondary"][disabled] *,
[data-testid="stBaseButton-primary"]:disabled,
[data-testid="stBaseButton-primary"]:disabled *,
[data-testid="stBaseButton-primary"][disabled],
[data-testid="stBaseButton-primary"][disabled] * {
  cursor: not-allowed !important;
}
}
"""

CSS = "<style>\n" + LIGHT_RULES.strip() + "\n\n" + DARK_RULES.strip() + "\n</style>\n"

DARK_CSS = "<style>\n" + DARK_RULES.strip() + "\n</style>\n"
