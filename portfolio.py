import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import random

# Sahifa sozlamalari
st.set_page_config(
    page_title="Ozoda | Portfolio",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# QIZLARGA MOS PREMIUM CSS ANIMATSIYALAR
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Falling flowers animation */
    .flower-rain {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Main container with glass effect */
    .main-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        border-radius: 30px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.5);
        animation: fadeInUp 1s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Soft neon text */
    .soft-neon {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        animation: softGlow 3s ease-in-out infinite;
        letter-spacing: 2px;
    }
    
    @keyframes softGlow {
        0%, 100% { filter: drop-shadow(0 0 15px rgba(240, 147, 251, 0.3)); }
        50% { filter: drop-shadow(0 0 40px rgba(245, 87, 108, 0.6)); }
    }
    
    /* Elegant card */
    .elegant-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.8);
        backdrop-filter: blur(10px);
        height: 100%;
        animation: scaleIn 0.8s ease-out;
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .elegant-card::after {
        content: '🌸';
        position: absolute;
        bottom: -20px;
        right: -20px;
        font-size: 100px;
        opacity: 0.1;
        transform: rotate(15deg);
        animation: rotateSlow 20s linear infinite;
    }
    
    @keyframes rotateSlow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .elegant-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 40px 80px rgba(240, 147, 251, 0.3);
    }
    
    /* Soft badge */
    .soft-badge {
        display: inline-block;
        padding: 0.6rem 1.5rem;
        margin: 0.3rem;
        background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
        color: white;
        border-radius: 50px;
        font-weight: 500;
        font-size: 0.9rem;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.3);
        transition: all 0.3s ease;
        animation: float 3s ease-in-out infinite;
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .soft-badge:hover {
        transform: scale(1.15) rotate(2deg);
        box-shadow: 0 15px 30px rgba(240, 147, 251, 0.6);
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    /* Gradient text */
    .gradient-soft {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        animation: shimmer 3s infinite;
        background-size: 200% auto;
    }
    
    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Stats card */
    .stats-card-soft {
        background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(240, 147, 251, 0.2);
        animation: pulseSoft 2s ease-in-out infinite;
    }
    
    .stats-card-soft:hover {
        transform: scale(1.05) rotate(1deg);
        box-shadow: 0 30px 50px rgba(240, 147, 251, 0.5);
    }
    
    @keyframes pulseSoft {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Timeline */
    .timeline-soft {
        padding: 1.2rem;
        border-left: 3px solid #fbc2eb;
        margin: 1rem 0;
        position: relative;
        animation: slideInSoft 0.6s ease-out;
        background: rgba(255,255,255,0.8);
        border-radius: 0 15px 15px 0;
        transition: all 0.3s ease;
    }
    
    .timeline-soft:hover {
        transform: translateX(10px);
        background: rgba(255,255,255,0.95);
    }
    
    @keyframes slideInSoft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .timeline-soft::before {
        content: '🌸';
        position: absolute;
        left: -12px;
        top: 50%;
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
        border-radius: 50%;
        transform: translateY(-50%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: white;
    }
    
    /* Typing animation */
    .typing-animation {
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid #f093fb;
        animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
        display: inline-block;
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #f093fb; }
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for floating elements
st.markdown("""
<script>
function createFloatingElements() {
    const elements = ['🌸', '✨', '💖', '🌺', '🌷', '🌟'];
    for(let i = 0; i < 20; i++) {
        const div = document.createElement('div');
        div.style.position = 'fixed';
        div.style.left = Math.random() * 100 + '%';
        div.style.top = Math.random() * 100 + '%';
        div.style.animation = 'float 4s ease-in-out infinite';
        div.style.fontSize = (Math.random() * 20 + 10) + 'px';
        div.style.pointerEvents = 'none';
        div.style.zIndex = '-1';
        div.style.opacity = '0.3';
        div.innerHTML = elements[Math.floor(Math.random() * elements.length)];
        document.body.appendChild(div);
    }
}
window.onload = createFloatingElements;
</script>

<style>
@keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    25% { transform: translateY(-20px) rotate(10deg); }
    75% { transform: translateY(20px) rotate(-10deg); }
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 class='soft-neon'>🌸 Ozoda Olimova</h1>
    <div class='typing-animation' style='font-size: 1.3rem; margin-top: 0.5rem; color: #666;'>
        Python Developer & Bot Creator
    </div>
    <div style='display: flex; gap: 0.8rem; justify-content: center; margin: 1.5rem 0; flex-wrap: wrap;'>
        <span class='soft-badge' style='animation-delay: 0s;'>✨ Python</span>
        <span class='soft-badge' style='animation-delay: 0.2s;'>🤖 Bot Creator</span>
        <span class='soft-badge' style='animation-delay: 0.4s;'>💻 Django</span>
        <span class='soft-badge' style='animation-delay: 0.6s;'>📊 Data Science</span>
        <span class='soft-badge' style='animation-delay: 0.8s;'>🎨 UI/UX</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Loading animation
with st.spinner('🌸 Ochilyapti...'):
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    time.sleep(0.5)
    progress_bar.empty()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class='elegant-card' style='text-align: center;'>
        <div style='position: relative; display: inline-block;'>
            <img src='https://via.placeholder.com/150/fbc2eb/ffffff?text=🌸' 
                 style='border-radius: 50%; border: 5px solid #fbc2eb; margin-bottom: 1rem; width: 150px; height: 150px;'>
        </div>
        <h2 class='gradient-soft'>Ozoda Olimova</h2>
        <p style='color: #666;'>3-kurs talabasi</p>
        <p style='color: #f5576c;'>Rennesans Ta'lim Universiteti</p>
        <div style='margin: 1rem 0;'>
            <span style='color: #fbc2eb;'>★★★★★</span> 5.0
        </div>
        <hr style='border: 1px solid #fbc2eb; opacity: 0.3;'>
        <div style='text-align: left;'>
            <p>📍 Toshkent, O'zbekiston</p>
            <p>📧 ozoda@example.com</p>
            <p>📱 +998 90 123 45 67</p>
            <p>🎓 3-kurs | Kompyuter injiniringi</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Social links
    st.markdown("""
    <div style='display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;'>
        <a href='#' style='text-decoration: none; color: #f093fb;'>🐙 GitHub</a>
        <a href='#' style='text-decoration: none; color: #f093fb;'>🔗 LinkedIn</a>
        <a href='#' style='text-decoration: none; color: #f093fb;'>📱 Telegram</a>
        <a href='#' style='text-decoration: none; color: #f093fb;'>📷 Instagram</a>
    </div>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Bosh sahifa", 
    "💼 Loyihalar", 
    "🤖 Botlar", 
    "🎓 Ta'lim", 
    "📬 Aloqa"
])

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class='elegant-card'>
            <h2 class='gradient-soft'>🌸 Men haqimda</h2>
            <p style='font-size: 1.1rem; line-height: 1.8; color: #555;'>
                Assalomu alaykum! Men Olimova Ozoda, Rennesans Ta'lim Universitetining 
                3-kurs talabasi. Python dasturlash va bot yaratishga qiziqaman. 
                Hozirgacha 10+ dan ortiq Telegram botlar yaratganman va doimiy 
                ravishda yangi texnologiyalarni o'rganaman.
            </p>
            <div style='margin-top: 1rem;'>
                <span class='soft-badge'>🎯 Maqsad: Senior Developer</span>
                <span class='soft-badge'>💡 Hobby: Kitob o'qish</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Skills
        st.markdown("<h2 class='gradient-soft'>🛠 Ko'nikmalar</h2>", unsafe_allow_html=True)
        
        skills = {
            "Python": 90,
            "Bot yaratish": 95,
            "Django": 75,
            "Data Science": 70,
            "SQL": 80,
            "Git": 75
        }
        
        for skill, level in skills.items():
            st.markdown(f"**{skill}**")
            st.progress(level/100)
    
    with col2:
        # Stats
        st.markdown("<h2 class='gradient-soft'>📊 Statistika</h2>", unsafe_allow_html=True)
        
        stats = [
            {"value": "15+", "label": "Loyihalar"},
            {"value": "10+", "label": "Botlar"},
            {"value": "3", "label": "Kurs"},
            {"value": "∞", "label": "Kofe"}
        ]
        
        for stat in stats:
            st.markdown(f"""
            <div class='stats-card-soft' style='margin-bottom: 1rem;'>
                <h1 style='font-size: 2.5rem; margin: 0;'>{stat['value']}</h1>
                <p style='margin: 0;'>{stat['label']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("<h1 class='gradient-soft' style='text-align: center;'>💼 Loyihalarim</h1>", unsafe_allow_html=True)
    
    projects = [
        {
            "title": "Online Kurs Platformasi",
            "desc": "Django asosida yaratilgan onlayn ta'lim platformasi",
            "tech": ["Python", "Django", "PostgreSQL"],
            "emoji": "📚"
        },
        {
            "title": "AI Yordamchi Bot",
            "desc": "Sun'iy intellekt asosidagi Telegram bot",
            "tech": ["Python", "AI", "Telegram API"],
            "emoji": "🤖"
        },
        {
            "title": "Talabalar Portali",
            "desc": "Universitet talabalari uchun portal",
            "tech": ["Flask", "SQLite", "Bootstrap"],
            "emoji": "🎓"
        }
    ]
    
    cols = st.columns(3)
    for idx, project in enumerate(projects):
        with cols[idx]:
            st.markdown(f"""
            <div class='elegant-card' style='height: 280px;'>
                <div style='font-size: 3rem; text-align: center;'>{project['emoji']}</div>
                <h3>{project['title']}</h3>
                <p>{project['desc']}</p>
                <div style='margin: 1rem 0;'>
                    {' '.join([f'<span class="soft-badge" style="font-size: 0.8rem;">{t}</span>' for t in project['tech']])}
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("<h1 class='gradient-soft' style='text-align: center;'>🤖 Mening Botlarim</h1>", unsafe_allow_html=True)
    
    bots = [
        {
            "name": "📚 Quiz Bot",
            "desc": "Talabalar uchun test va viktorina boti",
            "users": "500+ foydalanuvchi",
            "features": ["Testlar", "Reyting", "Sovrinlar"]
        },
        {
            "name": "📅 Dars Jadvali Boti",
            "desc": "Universitet dars jadvalini eslatuvchi bot",
            "users": "300+ talaba",
            "features": ["Eslatma", "O'zgartirish", "Xabar yuborish"]
        },
        {
            "name": "🎓 AI Assistant Bot",
            "desc": "Talabalarga yordam beruvchi AI bot",
            "users": "200+ foydalanuvchi",
            "features": ["Savol-javob", "Kod yozish", "Tushuntirish"]
        }
    ]
    
    for bot in bots:
        with st.container():
            st.markdown(f"""
            <div class='elegant-card' style='margin-bottom: 1rem;'>
                <h3>{bot['name']}</h3>
                <p>{bot['desc']}</p>
                <p><strong>👥 Foydalanuvchilar:</strong> {bot['users']}</p>
                <p><strong>✨ Xususiyatlari:</strong> {', '.join(bot['features'])}</p>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("<h1 class='gradient-soft' style='text-align: center;'>🎓 Ta'lim</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='elegant-card'>
            <h3>📚 Universitet</h3>
            <p><strong>Rennesans Ta'lim Universiteti</strong></p>
            <p>🎓 Fakultet: Kompyuter dasturlash</p>
            <p>📅 Kurs: 3-kurs</p>
            
        </div>
        
        <div class='elegant-card' style='margin-top: 1rem;'>
            <h3>📖 Kurslar</h3>
            <div class='timeline-soft'>Python Development (Coursera)</div>
            <div class='timeline-soft'>Telegram Bot Creation (Udemy)</div>
            <div class='timeline-soft'>Data Science (Stepik)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='elegant-card'>
            <h3>🏆 Sertifikatlar</h3>
        </div>
        """, unsafe_allow_html=True)
        
        certificates = [
            {"name": "Python Developer", "org": "Coursera", "year": "2024"},
            {"name": "Bot Development", "org": "Udemy", "year": "2023"},
            {"name": "Django Expert", "org": "Stepik", "year": "2024"},
            {"name": "AI Fundamentals", "org": "Google", "year": "2024"}
        ]
        
        for cert in certificates:
            st.markdown(f"""
            <div class='elegant-card' style='padding: 1rem; margin-bottom: 0.5rem;'>
                <p><strong>📜 {cert['name']}</strong><br>
                <small>{cert['org']} | {cert['year']}</small></p>
            </div>
            """, unsafe_allow_html=True)

with tab5:
    st.markdown("<h1 class='gradient-soft' style='text-align: center;'>📬 Bog'lanish</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("contact_form"):
            st.markdown("<h3>📝 Xabar qoldiring</h3>", unsafe_allow_html=True)
            name = st.text_input("Ismingiz")
            email = st.text_input("Email")
            subject = st.selectbox("Mavzu", ["Bot yaratish", "Hamkorlik", "Savol", "Boshqa"])
            message = st.text_area("Xabar", height=150)
            
            if st.form_submit_button("🌸 Yuborish", use_container_width=True):
                st.balloons()
                st.snow()
                st.success("Xabaringiz qabul qilindi! Tez orada javob beraman 🌸")
    
    with col2:
        st.markdown("""
        <div class='elegant-card'>
            <h3>📞 Aloqa ma'lumotlari</h3>
            <p><strong>📍 Manzil:</strong> Toshkent,Samarqand O'zbekiston</p>
            <p><strong>📧 Email:</strong> olimovaozoda33@gmail.com</p>
            <p><strong>📱 Telegram:</strong> ozoda_backend</p>
            <p><strong>📞 Telefon:</strong> +998 91 007 12 76</p>
        </div>
        
        <div class='elegant-card' style='margin-top: 1rem;'>
            <h3>⚡ Hozirgi holat</h3>
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <div style='width: 15px; height: 15px; background: #4CAF50; border-radius: 50%; animation: pulseSoft 1s infinite;'></div>
                <p><strong>Loyiha qabul qilaman</strong></p>
            </div>
            <p>Javob vaqti: 1-2 soat</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <p class='gradient-soft'>
        © 2024 Ozoda Olimova | Rennesans Ta'lim Universiteti | 3-kurs talabasi
    </p>
    <div style='display: flex; gap: 2rem; justify-content: center; margin-top: 1rem;'>
        <span class='soft-badge'>🐍 Python</span>
        <span class='soft-badge'>🤖 Bot Creator</span>
        <span class='soft-badge'>🎓 3-kurs</span>
        <span class='soft-badge'>🌸 Ozoda</span>
    </div>
</div>
""", unsafe_allow_html=True)