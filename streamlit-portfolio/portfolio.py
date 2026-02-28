import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import random

# Sahifa sozlamalari
st.set_page_config(
    page_title="DevPortfolio | Dasturchi",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ANIMATSIYALAR UCHUN CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Fira Code', monospace;
    }
    
    /* Terminal effekti */
    .terminal-text {
        font-family: 'Fira Code', monospace;
        color: #00ff00;
        background: #000;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #00ff00;
        animation: blink 2s infinite;
    }
    
    @keyframes blink {
        0%, 100% { border-color: #00ff00; }
        50% { border-color: transparent; }
    }
    
    /* Kod yozish animatsiyasi */
    .typing-animation {
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid #1E88E5;
        animation: typing 3s steps(40, end), blink-cursor 0.75s step-end infinite;
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-cursor {
        from, to { border-color: transparent; }
        50% { border-color: #1E88E5; }
    }
    
    /* Matrix effekti */
    .matrix-bg {
        background: linear-gradient(45deg, #000 0%, #1a1a1a 100%);
        color: #0f0;
        padding: 20px;
        border-radius: 10px;
        position: relative;
        overflow: hidden;
    }
    
    .matrix-bg::before {
        content: "0101010101010101";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        color: rgba(0,255,0,0.1);
        font-size: 20px;
        animation: matrix 20s linear infinite;
        pointer-events: none;
    }
    
    @keyframes matrix {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100%); }
    }
    
    /* Loading bar animatsiyasi */
    .loading-bar {
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1E88E5, #7B1FA2, #1E88E5);
        background-size: 200% 100%;
        animation: loading 2s linear infinite;
        border-radius: 2px;
    }
    
    @keyframes loading {
        0% { background-position: 0% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* Kartochka animatsiyalari */
    .dev-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .dev-card::before {
        content: "</>";
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 100px;
        opacity: 0.1;
        transform: rotate(15deg);
    }
    
    .dev-card:hover {
        transform: scale(1.05) translateY(-10px);
        box-shadow: 0 20px 30px rgba(102, 126, 234, 0.3);
    }
    
    /* Skill badge animatsiyasi */
    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1E88E5, #1976D2);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        animation: float 3s ease-in-out infinite;
    }
    
    .skill-badge:nth-child(odd) {
        animation-delay: 0.5s;
    }
    
    .skill-badge:nth-child(even) {
        animation-delay: 1s;
    }
    
    .skill-badge:hover {
        transform: scale(1.1);
        box-shadow: 0 5px 15px rgba(30, 136, 229, 0.4);
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Github-style kontribusiya grid */
    .contribution-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        padding: 20px;
        background: #0d1117;
        border-radius: 10px;
    }
    
    .contribution-cell {
        width: 100%;
        aspect-ratio: 1;
        background: #161b22;
        border-radius: 3px;
        transition: all 0.3s ease;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .contribution-cell:nth-child(3n) {
        animation-delay: 0.2s;
    }
    
    .contribution-cell:nth-child(5n) {
        animation-delay: 0.4s;
    }
    
    .contribution-cell:hover {
        background: #1E88E5;
        transform: scale(1.2);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    /* Rotating cube */
    .cube-container {
        perspective: 1000px;
        width: 100px;
        height: 100px;
        margin: 50px auto;
    }
    
    .cube {
        position: relative;
        width: 100%;
        height: 100%;
        transform-style: preserve-3d;
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotateX(0deg) rotateY(0deg); }
        100% { transform: rotateX(360deg) rotateY(360deg); }
    }
    
    /* Code rain */
    .code-rain {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        z-index: -1;
        opacity: 0.05;
    }
</style>
""", unsafe_allow_html=True)

# KOD YOMG'IRI EFFEKTI (Matrix)
code_rain = """
<div class="code-rain" id="code-rain"></div>
<script>
function createCodeRain() {
    const chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
    const container = document.getElementById('code-rain');
    
    for(let i = 0; i < 50; i++) {
        const drop = document.createElement('div');
        drop.style.position = 'absolute';
        drop.style.left = Math.random() * 100 + '%';
        drop.style.top = '-20px';
        drop.style.color = '#0f0';
        drop.style.fontSize = Math.random() * 20 + 10 + 'px';
        drop.style.animation = `rain ${Math.random() * 5 + 5}s linear infinite`;
        drop.style.animationDelay = Math.random() * 5 + 's';
        drop.innerHTML = chars[Math.floor(Math.random() * chars.length)];
        container.appendChild(drop);
    }
}

document.write(`
<style>
@keyframes rain {
    0% { transform: translateY(-100%); opacity: 1; }
    100% { transform: translateY(100vh); opacity: 0; }
}
</style>
`);
createCodeRain();
</script>
"""

# Sarlavha
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <h1 style='font-size: 3rem; background: linear-gradient(120deg, #1E88E5, #7B1FA2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        &lt;Developer/&gt;
    </h1>
    <div class='typing-animation' style='font-size: 1.2rem; color: #666; margin: 1rem 0;'>
        console.log("Hello, World! I'm a Python Developer");
    </div>
</div>
""", unsafe_allow_html=True)

# Loading bar
st.markdown('<div class="loading-bar"></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class='dev-card'>
        <h3 style='color: white;'>{ .profile }</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://via.placeholder.com/200x200", caption="<coder/>")
    
    # Terminal style info
    st.markdown("""
    <div class='terminal-text'>
        $ whoami<br>
        > Python Developer<br>
        $ location<br>
        > Tashkent, UZ<br>
        $ skills<br>
        > [Python, Django, AI]
    </div>
    """, unsafe_allow_html=True)
    
    # Github-style kontribusiya
    st.markdown("### 📊 Kontribusiya")
    cols = st.columns(7)
    for i in range(35):
        with cols[i % 7]:
            intensity = random.randint(1, 4)
            color = ['#161b22', '#0e4429', '#006d32', '#26a641'][intensity-1]
            st.markdown(f"""
            <div style='background: {color}; width: 100%; aspect-ratio: 1; border-radius: 3px; margin: 2px;'></div>
            """, unsafe_allow_html=True)

# Tablar
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home()", "💼 Projects()", "📊 Skills()", "📞 Contact()"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='dev-card'>
            <h2>def about_me():</h2>
            <p style='font-size: 1.1rem;'>
                return {
                    'name': 'Ism Familya',
                    'experience': '3+ years',
                    'focus': 'Backend Development',
                    'languages': ['Python', 'JavaScript', 'SQL']
                }
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Kod bloki
        st.code("""
        # Daily routine
        while True:
            code()
            learn_new_tech()
            solve_problems()
            if tired:
                coffee()
        """, language='python')
    
    with col2:
        # Statistikalar
        st.markdown("""
        <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;'>
            <div class='dev-card' style='text-align: center;'>
                <h1>15+</h1>
                <p>Projects</p>
            </div>
            <div class='dev-card' style='text-align: center;'>
                <h1>1k+</h1>
                <p>Commits</p>
            </div>
            <div class='dev-card' style='text-align: center;'>
                <h1>10+</h1>
                <p>Clients</p>
            </div>
            <div class='dev-card' style='text-align: center;'>
                <h1>∞</h1>
                <p>Coffee</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("## 🚀 Recent Projects")
    
    projects = [
        {
            "name": "AI Chat Bot",
            "desc": "GPT-based telegram bot",
            "tech": ["Python", "OpenAI", "Telegram API"],
            "stars": "⭐ 45"
        },
        {
            "name": "E-commerce API",
            "desc": "REST API for online store",
            "tech": ["Django", "DRF", "PostgreSQL"],
            "stars": "⭐ 32"
        },
        {
            "name": "Portfolio 2024",
            "desc": "This awesome portfolio",
            "tech": ["Python", "Streamlit", "CSS3"],
            "stars": "⭐ 12"
        }
    ]
    
    cols = st.columns(3)
    for idx, project in enumerate(projects):
        with cols[idx]:
            st.markdown(f"""
            <div class='dev-card'>
                <h3>{project['name']}</h3>
                <p>{project['desc']}</p>
                <p>{' '.join([f'<span class="skill-badge">{t}</span>' for t in project['tech']])}</p>
                <p>{project['stars']}</p>
                <div style='display: flex; gap: 1rem;'>
                    <span>🔗 Live</span>
                    <span>💻 Code</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("## 📈 Tech Stack")
    
    # Progress bar animatsiyalari
    skills = {
        "Python": 90,
        "Django": 85,
        "FastAPI": 75,
        "React": 60,
        "Docker": 70,
        "SQL": 80
    }
    
    for skill, level in skills.items():
        st.markdown(f"**{skill}**")
        progress_html = f"""
        <div style='width: 100%; background: #333; border-radius: 10px; height: 20px; margin-bottom: 1rem;'>
            <div style='width: {level}%; background: linear-gradient(90deg, #00ff00, #1E88E5); height: 100%; border-radius: 10px; 
            animation: loadProgress 2s ease-out;'></div>
        </div>
        <style>
        @keyframes loadProgress {{
            from {{ width: 0; }}
            to {{ width: {level}%; }}
        }}
        </style>
        """
        st.markdown(progress_html, unsafe_allow_html=True)

with tab4:
    st.markdown("## 📡 Contact Me")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='dev-card'>
            <h3>Send a message</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("contact"):
            name = st.text_input("Your name")
            email = st.text_input("Your email")
            message = st.text_area("Message")
            
            if st.form_submit_button("📨 Send message"):
                st.balloons()
                st.success("Message sent! 📨")
    
    with col2:
        st.markdown("""
        <div class='terminal-text'>
            $ git config --global user.name<br>
            > Your Name<br>
            $ git config --global user.email<br>
            > email@example.com<br>
            $ cat contact_info<br>
            > GitHub: @username<br>
            > LinkedIn: /in/username<br>
            > Telegram: @username
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <div style='display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;'>
        <span>🐍 Python</span>
        <span>⚡ Streamlit</span>
        <span>🎨 CSS3</span>
    </div>
    <p>© 2024 | Built with 💙 by Developer</p>
    <p style='color: #666; font-size: 0.8rem;'>v2.0.0 | Last commit: today</p>
</div>
""", unsafe_allow_html=True)