import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace st.subheader(...) with st.subheader(..., anchor=False)
content = re.sub(r'st\.subheader\((.*?)\)', r'st.subheader(\1, anchor=False)', content)

# Replace st.markdown("#### ...") with st.subheader("...", anchor=False)
content = re.sub(r'st\.markdown\(\s*[\"\'\']#{1,4}\s+(.*?)[\"\'\']\s*\)', r'st.subheader("\1", anchor=False)', content)

# Add CSS injection
css_injection = '''st.title("📄 AI Resume & Job-Readiness Analyzer")
    st.markdown("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>", unsafe_allow_html=True)'''
content = content.replace('st.title("📄 AI Resume & Job-Readiness Analyzer")', css_injection)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
