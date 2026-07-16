import streamlit as st
import openai
import sqlite3
import os
from pypdf import PdfReader
import docx2txt
from gtts import gTTS
import io

# --- KONFIGURASI SISTEM ---
VERSION = "v2.8"
CODENAME = "Aether-Quantum: Overdrive"

st.set_page_config(
    page_title=f"oXy AI Engine {VERSION}",
    page_icon="⚙️",
    layout="centered"
)

# --- DATABASE ENGINE (SQLite WAL MODE + FTS5) ---
def init_db():
    conn = sqlite3.connect("oxy_memory.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # FTS5 Virtual Table untuk Pencarian Cepat
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_memory 
        USING fts5(content, content_rowid=UNINDEXED);
    """)
    conn.close()

init_db()

def save_message(role, content):
    conn = sqlite3.connect("oxy_memory.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    row_id = cursor.lastrowid
    cursor.execute("INSERT INTO fts_memory (rowid, content) VALUES (?, ?)", (row_id, content))
    conn.close()

def load_messages():
    conn = sqlite3.connect("oxy_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history ORDER BY timestamp ASC")
    data = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in data]

def clear_memory():
    conn = sqlite3.connect("oxy_memory.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    cursor.execute("DELETE FROM fts_memory")
    conn.close()

# --- VALIDASI KUNCI (SECRETS) ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("Kunci API OpenRouter tidak terdeteksi di Secrets Streamlit!")
    st.stop()

if "LOGIN_PASSWORD" not in st.secrets:
    st.error("LOGIN_PASSWORD belum diatur di Secrets Streamlit!")
    st.stop()

# --- SISTEM KEAMANAN AKSES (ENFORCER) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(f"<h2 style='text-align: center;'>⚙️ oXy AI Enforcer {VERSION} ⚙️</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        st.write("Masukan Akses Kode Sistem:")
        input_pass = st.text_input("Kunci Kontrol...", type="password", label_visibility="collapsed")
        if st.button("Unlock Overdrive Core 🔮", use_container_width=True):
            if input_pass == st.secrets["LOGIN_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Kode Akses Salah! Enforcer Menolak Masuk.")
    st.stop()

# --- INSTANSIASI OPENAI CLIENT (VIA OPENROUTER) ---
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# --- EKSTRAKSI DOKUMEN ---
def extract_text(file):
    name = file.name.lower()
    if name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif name.endswith(".pdf"):
        pdf = PdfReader(file)
        return "".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif name.endswith(".docx"):
        return docx2txt.process(file)
    return ""

# --- INTERFACE UTAMA ---
st.title(f"🤖 oXy AI \"{CODENAME}\"")
st.caption(f"Engine Core Version {VERSION} | Active & Secured")

# Sidebar Fitur
with st.sidebar:
    st.header("🛠️ Panel Kontrol")
    if st.button("🗑️ Bersihkan Memori AI", use_container_width=True):
        clear_memory()
        st.success("Memori sistem telah dikosongkan!")
        st.rerun()
    
    st.divider()
    st.subheader("📁 Upload Dokumen (Context)")
    # PERBAIKAN DI SINI: Menggunakan st.file_uploader, bukan st.file_input
    uploaded_file = st.file_uploader("Pilih file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
    
    doc_context = ""
    if uploaded_file:
        with st.spinner("Mengekstrak data dokumen..."):
            doc_context = extract_text(uploaded_file)
            st.success(f"Berhasil memuat: {uploaded_file.name}")

# Memuat riwayat chat dari database lokal
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# Menampilkan riwayat chat ke layar
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Form Input User
if user_query := st.chat_input("Ketik perintah atau pertanyaan Anda..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    save_message("user", user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Menyusun pesan untuk AI
    api_messages = []
    
    # Masukkan konteks dokumen jika ada
    if doc_context:
        api_messages.append({
            "role": "system", 
            "content": f"Anda adalah oXy AI. Berikut adalah dokumen penting yang diunggah pengguna untuk dijadikan referensi utama:\n\n{doc_context}"
        })
    else:
        api_messages.append({
            "role": "system", 
            "content": "Anda adalah oXy AI, asisten premium pintar berbasis Overdrive Core."
        })

    # Masukkan riwayat pesan
    for m in st.session_state.messages[-10:]:  # Mengambil 10 pesan terakhir untuk efisiensi
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Memanggil OpenRouter API
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("Memproses Quantum Core..."):
                response = client.chat.completions.create(
                    model="google/gemini-2.5-flash",
                    messages=api_messages
                )
                full_response = response.choices[0].message.content
                response_placeholder.markdown(full_response)
                
                # Fitur Opsional Suara Text-to-Speech (TTS)
                try:
                    tts = gTTS(text=full_response[:500], lang='id')  # Batasi 500 karakter pertama agar cepat
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format="audio/mp3")
                except Exception as tts_err:
                    pass
                    
        except Exception as e:
            full_response = f"Gagal memproses ke Quantum Core. Error: {str(e)}"
            response_placeholder.error(full_response)
            
        save_message("assistant", full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
