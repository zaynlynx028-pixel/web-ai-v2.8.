import streamlit as st
import sqlite3
import os
import io
import time
from openai import OpenAI
from pypdf import PdfReader
import docx2txt
from gtts import gTTS

# ==========================================
# 1. DATABASE & SECURITY ENGINE (WAL & FTS5)
# ==========================================
DB_FILE = "database.db"

def get_db_connection():
    """Membuka koneksi SQLite dengan optimasi WAL Mode."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    """Inisialisasi tabel standar dan tabel pencarian virtual FTS5."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tabel Riwayat Chat Utama
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Tabel Virtual FTS5 untuk Pencarian Super Cepat
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chat_search USING fts5(
            content,
            content_rowid=id
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content):
    """Menyimpan pesan baru ke database standar dan indeks FTS5."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    row_id = cursor.lastrowid
    cursor.execute("INSERT INTO chat_search (rowid, content) VALUES (?, ?)", (row_id, content))
    conn.commit()
    conn.close()

def load_messages():
    """Memuat seluruh riwayat pesan dari database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

def clear_db():
    """Menghapus semua riwayat pesan dan membersihkan indeks."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    cursor.execute("INSERT INTO chat_search(chat_search) VALUES('rebuild')")
    conn.commit()
    conn.close()

def search_history(query):
    """Melakukan pencarian kata kunci secara instan menggunakan indeks FTS5."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.role, h.content, h.timestamp 
        FROM chat_history h
        JOIN chat_search s ON h.id = s.rowid
        WHERE chat_search MATCH ?
        ORDER BY h.id DESC
    """, (query,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Jalankan Inisialisasi Database saat aplikasi dimulai
init_db()

# ==========================================
# 2. SISTEM KEAMANAN & VERIFIKASI SANDI
# ==========================================
def check_password():
    """Memastikan user memasukkan password yang benar dari secrets."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # Desain Halaman Login Minimalis & Premium
    st.markdown("""
        <style>
            .login-container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-top: 100px;
            }
            .login-title {
                font-family: 'Courier New', monospace;
                font-size: 28px;
                color: #a855f7;
                letter-spacing: 2px;
                margin-bottom: 20px;
            }
        </style>
        <div class="login-container">
            <div class="login-title">⚙️ oXy AI Enforcer v2.8 ⚙️</div>
        </div>
    """, unsafe_allow_html=True)

    pwd_input = st.text_input("Masukan Akses Kode Sistem:", type="password", placeholder="Kunci Kontrol...")
    submit_btn = st.button("Unlock Overdrive Core 🔮", use_container_width=True)

    if submit_btn:
        expected_password = st.secrets.get("LOGIN_PASSWORD", "zayn")
        if pwd_input == expected_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Akses Ditolak: Kode salah atau tidak terdaftar.")
    return False

if not check_password():
    st.stop()

# ==========================================
# 3. KONEKSI KE OTAK AI (OPENROUTER ENGINE)
# ==========================================
API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
if not API_KEY:
    st.error("Kunci API OpenRouter tidak terdeteksi di Secrets Streamlit!")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

# ==========================================
# 4. MEMBUAT INTERFACE DAN FITUR MULTIMODAL
# ==========================================
st.set_page_config(page_title="oXy AI v2.8", page_icon="🔮", layout="wide")

# Custom CSS Premium Dark Theme
st.markdown("""
    <style>
        .stApp {
            background-color: #0d0e15;
            color: #e2e8f0;
        }
        .main-header {
            font-family: 'Courier New', monospace;
            background: linear-gradient(45deg, #a855f7, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 25px;
        }
        .message-bubble {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            line-height: 1.5;
        }
        .user-bubble {
            background-color: #1e1b4b;
            border-left: 5px solid #a855f7;
        }
        .assistant-bubble {
            background-color: #0f172a;
            border-left: 5px solid #3b82f6;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">oXy AI v2.8 "Aether-Quantum"</div>', unsafe_allow_html=True)

# Memuat Pesan Awal ke Session State agar Sinkron
if "messages" not in st.session_state:
    st.session_state["messages"] = load_messages()

# Sidebar: Pengaturan Model, Dokumen, dan Pencarian FTS5
with st.sidebar:
    st.markdown("### ⚙️ Pusat Kontrol Sistem")
    
    # Pilih Model Kecerdasan
    model_choice = st.selectbox(
        "Pilih Model Berpikir:",
        [
            "google/gemini-2.5-flash",
            "meta-llama/llama-3.3-70b-instruct",
            "deepseek/deepseek-chat"
        ]
    )
    
    st.markdown("---")
    
    # Fitur Analisis Dokumen
    st.markdown("### 📄 Pengumpan Dokumen")
    uploaded_file = st.file_input("Unggah PDF atau DOCX:", type=["pdf", "docx"])
    doc_text = ""
    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext == ".pdf":
            try:
                pdf_reader = PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    doc_text += page.extract_text() or ""
                st.success("Dokumen PDF berhasil dibaca!")
            except Exception as e:
                st.error(f"Gagal membaca PDF: {e}")
        elif file_ext == ".docx":
            try:
                doc_text = docx2txt.process(uploaded_file)
                st.success("Dokumen Word berhasil dibaca!")
            except Exception as e:
                st.error(f"Gagal membaca DOCX: {e}")

    st.markdown("---")
    
    # Pencarian FTS5 Real-time
    st.markdown("### 🔍 Pencarian Riwayat Cepat (FTS5)")
    search_query = st.text_input("Ketik kata kunci untuk mencari chat lama:")
    if search_query:
        search_results = search_history(search_query)
        if search_results:
            st.write(f"Ditemukan {len(search_results)} pesan:")
            for role, content, ts in search_results:
                emoji = "👤" if role == "user" else "🔮"
                st.markdown(f"**[{ts}] {emoji} {role.capitalize()}:** {content[:100]}...")
        else:
            st.info("Kata kunci tidak ditemukan.")

    st.markdown("---")
    
    # Tombol Reset Database
    if st.button("🗑️ Bersihkan Semua Riwayat", use_container_width=True):
        clear_db()
        st.session_state["messages"] = []
        st.success("Semua riwayat chat di database telah dibersihkan!")
        time.sleep(1)
        st.rerun()

# ==========================================
# 5. HALAMAN UTAMA: ALUR INTERAKSI CHAT
# ==========================================

# Menampilkan Riwayat Obrolan Aktif
for msg in st.session_state["messages"]:
    bubble_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    st.markdown(f"""
        <div class="message-bubble {bubble_class}">
            <strong>{"👤 Tuan Zayn" if msg["role"] == "user" else "🔮 oXy AI"}:</strong><br>
            {msg["content"]}
        </div>
    """, unsafe_allow_html=True)

# Tempat Input Pengguna
user_input = st.chat_input("Ketik instruksi di sini...")

if user_input:
    # Gabungkan teks dokumen jika ada dokumen yang aktif diunggah
    final_prompt = user_input
    if doc_text:
        final_prompt = f"[INFORMASI DOKUMEN YANG DIUNGGAH USER]:\n{doc_text}\n\n[PERTANYAAN USER]:\n{user_input}"
    
    # Tampilkan & Simpan Pesan User
    st.markdown(f"""
        <div class="message-bubble user-bubble">
            <strong>👤 Tuan Zayn:</strong><br>
            {user_input}
        </div>
    """, unsafe_allow_html=True)
    
    save_message("user", user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Buat format pesan untuk dikirim ke API
    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]]
    
    # Jalankan Panggilan Stream ke OpenRouter
    with st.chat_message("assistant", avatar="🔮"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=model_choice,
                messages=api_messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Sistem Gagal Berpikir: {e}")
            full_response = "Maaf Tuan, sistem mengalami gangguan koneksi ke OpenRouter."
            message_placeholder.markdown(full_response)
            
    # Simpan Respons Asisten ke Database
    save_message("assistant", full_response)
    st.session_state["messages"].append({"role": "assistant", "content": full_response})
    
    # Tambahkan Fitur Text-to-Speech Otomatis di bawah pesan jika diinginkan
    try:
        tts = gTTS(text=full_response[:300], lang='id')  # Batasi 300 karakter untuk menghemat memori
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format="audio/mp3")
    except Exception as e:
        pass # Lewati jika internet terlalu lambat untuk memproses TTS
