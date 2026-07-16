import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import os
import json

# 1. Konfigurasi Halaman Utama
st.set_page_config(page_title="oXy AI • Core", page_icon="🌐", layout="centered")

# 2. INJEKSI CSS STRUKTUR: TRANSISI SPLASH SCREEN SINKRON & PLANET 3D BUMI LIQUID GLASS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Background Deep Nebula */
    .stApp {
        background: radial-gradient(circle at 50% 15%, #0e0a21 0%, #06040d 70%, #020105 100%) !important;
        color: #e2dcf0 !important;
        overflow-x: hidden;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden !important; }

    /* 🎬 ANIMASI PEMUNCULAN ELEMEN (SPLASH EFFECT) */
    .splash-fade-in {
        animation: splashIn 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    .content-fade-in {
        animation: contentIn 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    
    @keyframes splashIn {
        from { opacity: 0; transform: scale(0.92); filter: blur(8px); }
        to { opacity: 1; transform: scale(1); filter: blur(0); }
    }
    @keyframes contentIn {
        from { opacity: 0; transform: translateY(20px); filter: blur(4px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

    /* 🌐 ANIMATED CYBER EARTH PLANET (BIRU MUDA + LIQUID GLASS PUTIH HD) */
    .cyber-core-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 8%;
        margin-bottom: 20px;
    }
    
    .cyber-planet {
        width: 125px;
        height: 125px;
        border-radius: 50%;
        position: relative;
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #a5f3fc 25%, #38bdf8 60%, #0369a1 100%);
        box-shadow: 
            0 0 25px rgba(56, 189, 248, 0.35),
            0 0 55px rgba(14, 165, 233, 0.5),
            inset -10px -10px 30px rgba(3, 105, 161, 0.7),
            inset 15px 15px 25px rgba(255, 255, 255, 0.9);
        overflow: hidden;
        animation: rotatePlanet 12s linear infinite;
    }

    .cyber-planet::before {
        content: '';
        position: absolute;
        width: 200%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.4) 8%, transparent 9%),
            radial-gradient(circle at 35% 70%, rgba(2, 132, 199, 0.5) 12%, transparent 13%),
            radial-gradient(circle at 60% 40%, rgba(255, 255, 255, 0.5) 6%, transparent 7%),
            radial-gradient(circle at 75% 75%, rgba(2, 132, 199, 0.4) 10%, transparent 11%),
            radial-gradient(circle at 90% 25%, rgba(255, 255, 255, 0.3) 14%, transparent 15%),
            linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 20%, rgba(255,255,255,0.6) 40%, transparent 60%);
        background-size: 50% 100%;
        animation: moveClouds 6s linear infinite;
    }

    .cyber-planet::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, transparent 50%, rgba(0,0,0,0.3) 100%);
        pointer-events: none;
    }

    @keyframes rotatePlanet {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes moveClouds {
        0% { background-position: 0px 0px; }
        100% { background-position: 125px 0px; }
    }

    /* TEKS UTAMA BRANDING */
    .oxy-title {
        text-align: center;
        font-weight: 800 !important;
        font-size: 2.6rem !important;
        color: #ffffff !important;
        margin-bottom: 2px !important;
        letter-spacing: -0.5px;
    }
    .oxy-sub-title {
        text-align: center;
        color: #94a3b8 !important;
        font-size: 1rem;
        margin-bottom: 25px !important;
        font-weight: 500;
    }

    /* KARTU PROFIL UTAMA */
    .welcome-card-cyber {
        background: rgba(15, 23, 42, 0.5) !important;
        border-radius: 28px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        padding: 40px 30px;
        text-align: center;
        margin: 20px auto;
        max-width: 500px;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
    }
    .welcome-h1 { font-size: 2.2rem !important; font-weight: 800 !important; color: #38bdf8 !important; margin-bottom: 20px; }
    .welcome-p { font-size: 1.1rem; color: #e2e8f0; line-height: 1.7; font-weight: 500; }

    /* BUTTON HUB KREATOR */
    div[data-testid="stElementContainer"] button[key="enter_cyber_btn"] {
        background: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 14px 40px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4) !important;
    }

    /* 📱 KAPSUL LAYOUT OPSI MENU CEPAT PERSIS SEPERTI DI VIDEO */
    .capsule-menu-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        max-width: 480px;
        margin: 0 auto 25px auto;
    }
    .capsule-item {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 0.9rem;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* CHAT BUBBLE CUSTOM */
    div[data-testid="stChatInputContainer"] > div {
        border-radius: 30px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        background: rgba(10, 15, 30, 0.85) !important;
    }
    .cyber-user-bubble {
        background: rgba(14, 165, 233, 0.2) !important;
        color: #f8fafc !important;
        padding: 12px 20px !important;
        border-radius: 20px 20px 4px 20px !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
    }
    .cyber-ai-bubble-box {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        border-radius: 4px 20px 20px 20px !important;
        padding: 16px 20px !important;
        margin-bottom: 20px !important;
    }
    .ai-header-inline { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
    .ai-mini-orb { width: 14px; height: 14px; border-radius: 50%; background: radial-gradient(circle, #ffffff 0%, #38bdf8 70%); }

    /* INDIKATOR PENGETIKAN */
    .typing-indicator { display: flex; gap: 4px; padding: 4px; }
    .typing-dot { width: 6px; height: 6px; background-color: #38bdf8; border-radius: 50%; animation: cb 1.4s infinite both; }
    .typing-dot:nth-child(2) { animation-delay: .2s; }
    .typing-dot:nth-child(3) { animation-delay: .4s; }
    @keyframes cb { 0%, 100% { transform: scale(0.8); opacity: 0.4; } 50% { transform: scale(1.2); opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# 3. FIX OVERLAY INTERFACE & JAVASCRIPT AUTO-SCROLL LOADER
components.html("""
<script>
    function fixInputStyle() {
        const plates = window.parent.document.querySelectorAll('div[data-testid="stBottom"], div[data-testid="stBottomBlockContainer"], .stChatInputContainer, form');
        plates.forEach(el => {
            el.style.setProperty('background-color', 'transparent', 'important');
            el.style.setProperty('box-shadow', 'none', 'important');
            el.style.setProperty('border', 'none', 'important');
        });
    }
    function scrollToBottom() {
        window.parent.scrollTo({ top: window.parent.document.body.scrollHeight, behavior: 'smooth' });
    }
    setInterval(fixInputStyle, 50);
    setInterval(scrollToBottom, 400);
</script>
""", height=0, width=0)

# ================= MANAJEMEN SESSION HALAMAN APP =================
if "sudah_masuk" not in st.session_state:
    st.session_state.sudah_masuk = False
if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

# --- PROTEKSI KODE SANDI (ENFORCER) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; margin-top: 15%;'>⚙️ oXy AI Enforcer v2.8 ⚙️</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        st.write("Masukan Akses Kode Sistem:")
        input_pass = st.text_input("Kunci Kontrol...", type="password", label_visibility="collapsed")
        if st.button("Unlock Overdrive Core 🔮", use_container_width=True):
            if input_pass == st.secrets.get("LOGIN_PASSWORD", "zayn"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Kode Akses Salah!")
    st.stop()

# 🏠 HALAMAN 1: PROFIL SCREEN (AWAL DIBUKA)
if not st.session_state.sudah_masuk:
    st.markdown('<div class="content-fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="cyber-core-container"><div class="cyber-planet"></div></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="oxy-title">oXy AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="oxy-sub-title">Apa yang bisa saya bantu?</p>', unsafe_allow_html=True)
    
    st.html("""
    <div class="welcome-card-cyber">
        <div class="welcome-h1">Halo, Saya oXy</div>
        <div class="welcome-p">
            Seorang <strong>Asisten Kecerdasan Buatan</strong> yang siap membantumu kapan saja.
        </div>
    </div>
    """)
    
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("Masuk ke Core 🔮", key="enter_cyber_btn", use_container_width=True):
            st.session_state.sudah_masuk = True
            st.session_state.splash_time = time.time()
            st.rerun()
            
    st.html("""
    <div style="text-align:center; margin-top:50px;">
        <div style="font-size:1.8rem !important; font-weight:800 !important; color:#38bdf8 !important; margin-bottom:20px;">Tentang Kreator</div>
        <div style="width:140px; height:140px; border-radius:50%; border:2px solid #0284c7; box-shadow:0 0 30px rgba(56,189,248,0.3); margin:0 auto 20px auto; display:flex; justify-content:center; align-items:center; background:rgba(15,23,42,0.6);">
            <div style="font-size:1rem; font-weight:600; color:#fff; opacity:0.8;">Zayn Profile</div>
        </div>
    </div>
    <div style="max-width:500px; margin:0 auto 60px auto; padding:0 20px; text-align:center;">
        <p style="font-size:0.95rem; color:#94a3b8; line-height:1.7;">
            <span style="color:#7dd3fc; font-weight:600;">oXy AI</span> adalah entitas sistem kecerdasan buatan siber mutakhir yang dirancang khusus oleh <span style="color:#7dd3fc; font-weight:600;">Zayn</span> untuk membantu mempercepat alur kerja pengembangan perangkat lunak secara cerdas.
        </p>
    </div>
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# 💬 HALAMAN 2: INTERFACE CHAT CORE UTAMA
else:
    if not st.session_state.splash_done:
        st.markdown('<div class="splash-fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="cyber-core-container" style="margin-top:15%;"><div class="cyber-planet" style="width:130px; height:130px;"></div></div>', unsafe_allow_html=True)
        st.markdown('<h1 class="oxy-title" style="font-size:3rem !important;">oXy\'s</h1>', unsafe_allow_html=True)
        st.markdown('<p class="oxy-sub-title" style="font-size:1.2rem; color:#38bdf8 !important;">AI Assistant</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        time.sleep(2.2)
        st.session_state.splash_done = True
        st.rerun()

    else:
        st.markdown('<div class="content-fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="cyber-core-container" style="margin-top:2%; margin-bottom:15px;"><div class="cyber-planet" style="width:75px; height:75px;"></div></div>', unsafe_allow_html=True)
        st.markdown('<h1 class="oxy-title" style="font-size: 1.8rem !important;">Selamat datang di oXy\'s</h1>', unsafe_allow_html=True)
        st.markdown('<p class="oxy-sub-title" style="margin-bottom:15px !important; font-size:0.9rem;">Saya asisten AI yang siap membantu Anda.</p>', unsafe_allow_html=True)

        st.html("""
        <div class="capsule-menu-container">
            <div class="capsule-item">🌏 Indonesia</div>
            <div class="capsule-item">✨ Puisi</div>
            <div class="capsule-item">🤖 AI (English)</div>
            <div class="capsule-item">🇪🇸 Español</div>
        </div>
        """)

        openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
        if not openrouter_key:
            st.error("⚠️ Token OPENROUTER_API_KEY tidak ditemukan di Secrets Streamlit.")
            st.stop()

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
        FILE_ARSIP = "arsip_chat.json"

        if "messages" not in st.session_state:
            if os.path.exists(FILE_ARSIP):
                try:
                    with open(FILE_ARSIP, "r", encoding="utf-8") as f: st.session_state.messages = json.load(f)
                except: st.session_state.messages = []
            else: st.session_state.messages = []

        col_reset, _ = st.columns([2, 2])
        with col_reset:
            if st.button("🗑️ Kosongkan Sesi oXy", key="cyber_reset"):
                if os.path.exists(FILE_ARSIP): os.remove(FILE_ARSIP)
                st.session_state.messages = []
                st.rerun()

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.html(f'<div style="display:flex; justify-content:flex-end; margin-bottom:15px;"><div class="cyber-user-bubble">{msg["content"]}</div></div>')
            elif msg["role"] == "assistant":
                with st.container():
                    st.html('<div style="display:flex; justify-content:flex-start;"><div class="cyber-ai-bubble-box"><div class="ai-header-inline"><div class="ai-mini-orb"></div><div style="font-weight:700; color:#fff; font-size:0.9rem;">oXy AI</div></div><div style="color:#e2e8f0; line-height:1.7;">')
                    st.markdown(msg["content"])
                    st.html('</div></div></div>')

        if user_input := st.chat_input("Ketik pesan..."):
            st.html(f'<div style="display:flex; justify-content:flex-end; margin-bottom:15px;"><div class="cyber-user-bubble">{user_input}</div></div>')
            
            if len(st.session_state.messages) == 0:
                st.session_state.messages.append({
                    "role": "system", 
                    "content": "Sebagai oXy AI yang dikembangkan oleh Zayn, saya tidak menggunakan API key dari AI lain. Saya beroperasi di infrastruktur yang dikelola oleh tim pengembang saya."
                })
                
            st.session_state.messages.append({"role": "user", "content": user_input})
            with open(FILE_ARSIP, "w", encoding="utf-8") as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
                
            try:
                placeholder_loading = st.empty()
                with placeholder_loading.container():
                    st.html("""
                    <div style="display:flex; justify-content:flex-start;">
                        <div class="cyber-ai-bubble-box">
                            <div class="ai-header-inline">
                                <div class="ai-mini-orb"></div>
                                <div style="font-weight:700; color:#fff; font-size:0.9rem;">oXy AI berpikir...</div>
                            </div>
                            <div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
                        </div>
                    </div>
                    """)
                
                # MENGGUNAKAN MODEL OTOMATIS/TERJANGKAU SESUAI KODE ASLI TUAN
                response_stream = client.chat.completions.create(
                    model="openrouter/auto", 
                    messages=[m for m in st.session_state.messages if m["role"] != "system"] or st.session_state.messages,
                    stream=True
                )
                placeholder_loading.empty()
                
                def generate_stream_data():
                    for chunk in response_stream:
                        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content:
                                yield delta.content

                with st.container():
                    st.html('<div style="display:flex; justify-content:flex-start;"><div class="cyber-ai-bubble-box"><div class="ai-header-inline"><div class="ai-mini-orb"></div><div style="font-weight:700; color:#fff; font-size:0.9rem;">oXy AI</div></div><div style="color:#e2e8f0; line-height:1.7;">')
                    full_response = st.write_stream(generate_stream_data)
                    st.html('</div></div></div>')
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with open(FILE_ARSIP, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
                st.rerun()
                
            except Exception as e:
                placeholder_loading.empty()
                st.error(f"Gagal mengambil respons: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
