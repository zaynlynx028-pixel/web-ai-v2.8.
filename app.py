import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import os
import json
import re
import ast
from datetime import datetime
import uuid

# ==============================================================================
# 1. INITIAL SYSTEM SETUP & CORE CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="oXy AI • Nexus OS v5.0", page_icon="🌐", layout="centered")

# Injeksi Bahasa Visual Antarmuka Nexus OS v5.0
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important; }
    .terminal-text, code, pre { font-family: 'Fira Code', monospace !important; }

    .stApp {
        background: radial-gradient(circle at 50% 15%, #05040a 0%, #010103 70%, #000000 100%) !important;
        color: #e2dcf0 !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden !important; }

    /* 🌐 THE LIVING ORB - STATE ENGINE */
    .cyber-core-container { display: flex; justify-content: center; align-items: center; margin-top: 2%; margin-bottom: 10px; position: relative; }
    .cyber-core-container::after {
        content: ''; position: absolute; width: 120px; height: 120px; border-radius: 50%;
        background: rgba(56, 189, 248, 0.08); filter: blur(20px); animation: orbPulse 3s ease-in-out infinite alternate;
    }
    .cyber-planet {
        width: 80px; height: 80px; border-radius: 50%; position: relative; overflow: hidden;
        box-shadow: inset -6px -6px 18px rgba(0,0,0,0.85), inset 8px 10px 15px rgba(255,255,255,0.7);
        z-index: 1; transition: all 0.5s ease;
    }

    /* EXTENDED STATE MATRIX COLORS */
    .state-idle { background: radial-gradient(circle at 30% 30%, #ffffff 0%, #a5f3fc 20%, #38bdf8 55%, #0369a1 100%); animation: spinOrb 30s linear infinite; }
    .state-flow { background: radial-gradient(circle at 30% 30%, #ffffff 0%, #c084fc 25%, #8b5cf6 60%, #4c1d95 100%); animation: spinOrb 5s linear infinite; box-shadow: 0 0 25px rgba(139, 92, 246, 0.5); }
    .state-forge { background: radial-gradient(circle at 30% 30%, #ffffff 0%, #fde047 25%, #eab308 60%, #854d0e 100%); animation: flashOrb 0.8s ease-in-out infinite alternate; color: #eab308; }
    .state-tool { background: radial-gradient(circle at 30% 30%, #ffffff 0%, #86efac 25%, #22c55e 60%, #14532d 100%); animation: spinOrb 12s linear infinite; box-shadow: 0 0 20px rgba(34, 197, 94, 0.4); }
    .state-warning { background: radial-gradient(circle at 30% 30%, #ffffff 0%, #fca5a5 25%, #ef4444 60%, #991b1b 100%); animation: flashOrb 0.4s ease-in-out infinite alternate; color: #ef4444; }

    @keyframes spinOrb { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes orbPulse { 0% { transform: scale(0.96); opacity: 0.3; } 100% { transform: scale(1.06); opacity: 0.6; } }
    @keyframes flashOrb { 0% { filter: drop-shadow(0 0 2px rgba(255,255,255,0.1)); } 100% { filter: drop-shadow(0 0 15px currentColor); } }

    /* UTILITIES UI COMPONENTS */
    .bubble-user {
        background: rgba(14, 165, 233, 0.08) !important; color: #f8fafc !important;
        padding: 10px 16px !important; border-radius: 14px 14px 4px 14px !important;
        border: 1px solid rgba(56, 189, 248, 0.1) !important; max-width: 85%;
    }
    .bubble-core {
        background: rgba(8, 6, 14, 0.5) !important; border: 1px solid rgba(56, 189, 248, 0.08) !important;
        border-radius: 4px 14px 14px 14px !important; padding: 14px 16px !important; margin-bottom: 12px !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

components.html("""
<script>
    setInterval(() => {
        const elements = window.parent.document.querySelectorAll('div[data-testid="stBottom"], div[data-testid="stBottomBlockContainer"], .stChatInputContainer, form');
        elements.forEach(el => {
            el.style.setProperty('background-color', 'transparent', 'important');
            el.style.setProperty('box-shadow', 'none', 'important');
            el.style.setProperty('border', 'none', 'important');
        });
    }, 50);
</script>
""", height=0, width=0)

# ==============================================================================
# 2. PERSISTENT SYSTEM REPOSITORY MATRIX
# ==============================================================================
DIR_ARCHIVE = "archive"
DIR_NEXUS = "nexus_system"
FILE_METRICS = os.path.join(DIR_NEXUS, "metrics.json")
FILE_LONGTERM_MEM = os.path.join(DIR_NEXUS, "longterm_memory.json")

for folder in [DIR_ARCHIVE, DIR_NEXUS]:
    if not os.path.exists(folder): os.makedirs(folder)

def load_json_file(path, default_value):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default_value
    return default_value

def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

# Instansiasi Memori Sistem Lokal
sys_metrics = load_json_file(FILE_METRICS, {"total_prompts": 0, "total_responses": 0, "processed_words": 0, "total_prompt_tokens": 0, "total_completion_tokens": 0})
longterm_memory = load_json_file(FILE_LONGTERM_MEM, {"user_facts": [], "project_intelligence": {}})

if "sudah_masuk" not in st.session_state: st.session_state.sudah_masuk = False
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "active_session_id" not in st.session_state: st.session_state.active_session_id = "default_core"
if "planet_state" not in st.session_state: st.session_state.planet_state = "state-idle"
if "system_terminal_logs" not in st.session_state: st.session_state.system_terminal_logs = []

# --- 🔒 SECURITY ENFORCER LAYER ---
if not st.session_state.authenticated:
    st.markdown("<h3 style='text-align: center; margin-top: 15%; color:#38bdf8;'>🔒 oXy Nexus • Enforcer v5.0</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        input_pass = st.text_input("Enter Nexus Authentication Key...", type="password")
        if st.button("Unlock Nexus Core Matrix 🔮", use_container_width=True):
            if input_pass == st.secrets.get("LOGIN_PASSWORD", "zayn"):
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Passcode Rejected.")
    st.stop()

# ==============================================================================
# 3. SAFE ISOLATED MATHEMATICAL PARSER (REPLACING EVAL)
# ==============================================================================
def safe_eval_expr(expr):
    try:
        node = ast.parse(expr, mode='eval')
        def _eval(n):
            if isinstance(n, ast.Expression): return _eval(n.body)
            elif isinstance(n, ast.BinOp):
                left = _eval(n.left)
                right = _eval(n.right)
                if isinstance(n.op, ast.Add): return left + right
                elif isinstance(n.op, ast.Sub): return left - right
                elif isinstance(n.op, ast.Mult): return left * right
                elif isinstance(n.op, ast.Div): return left / right
                elif isinstance(n.op, ast.Pow): return left ** right
            elif isinstance(n, ast.UnaryOp):
                operand = _eval(n.operand)
                if isinstance(n.op, ast.USub): return -operand
            elif isinstance(n, ast.Constant): return n.value
            raise TypeError(f"Unsupported syntax tree element: {type(n)}")
        return _eval(node)
    except Exception as err:
        return f"Safe Parser Error: {err}"

# ==============================================================================
# 4. OS DASHBOARD DIAGNOSTIC GATEWAY (LANDING PAGE)
# ==============================================================================
if not st.session_state.sudah_masuk:
    st.markdown(f'<div class="cyber-core-container"><div class="cyber-planet state-idle"></div></div>', unsafe_allow_html=True)
    st.markdown(f'<h1 style="text-align:center; font-weight:800; color:#fff; font-size:2rem; margin-bottom:2px;">Welcome Back, Zayn.</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748b; font-size:0.8rem; margin-bottom:15px;">oXy OS Core Interface • Architecture Stabilized</p>', unsafe_allow_html=True)
    
    archive_count = len([f for f in os.listdir(DIR_ARCHIVE) if f.endswith(".json")])
    facts_count = len(longterm_memory.get("user_facts", []))
    
    st.html(f"""
    <div style="background:rgba(6,4,12,0.8); border:1px solid rgba(56,189,248,0.15); border-radius:14px; padding:16px; margin:10px auto; max-width:480px;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); padding:8px; border-radius:6px; text-align:center;">
                <div style="font-size:1rem; color:#38bdf8; font-weight:700;">{sys_metrics.get("total_prompts", 0)}</div><div style="font-size:0.65rem; color:#64748b;">TOTAL PROMPTS</div>
            </div>
            <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); padding:8px; border-radius:6px; text-align:center;">
                <div style="font-size:1rem; color:#a855f7; font-weight:700;">{archive_count}</div><div style="font-size:0.65rem; color:#64748b;">WORKSPACES</div>
            </div>
            <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); padding:8px; border-radius:6px; text-align:center;">
                <div style="font-size:1rem; color:#22c55e; font-weight:700;">{facts_count}</div><div style="font-size:0.65rem; color:#64748b;">FACTS RECORDED</div>
            </div>
            <div style="background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); padding:8px; border-radius:6px; text-align:center;">
                <div style="font-size:0.85rem; color:#eab308; font-weight:700; font-family:'Fira Code', monospace !important;">P:{sys_metrics.get("total_prompt_tokens",0)} | C:{sys_metrics.get("total_completion_tokens",0)}</div>
                <div style="font-size:0.65rem; color:#64748b; margin-top:2px;">ACCUMULATED TOKENS</div>
            </div>
        </div>
    </div>
    """)
    if st.button("Boot Nexus Runtime Link 🌐", use_container_width=True):
        st.session_state.sudah_masuk = True
        st.rerun()
    st.stop()

# ==============================================================================
# 5. RUNTIME ENVIRONMENT MANAGEMENT & OPENROUTER PIPELINE
# ==============================================================================
openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
if not openrouter_key: st.error("Token API Key Missing."); st.stop()
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)

# SIDEBAR CONTROL DECK INTERFACE
with st.sidebar:
    st.markdown("<h3 style='color:#38bdf8; font-size:1.1rem;'>🌐 Nexus Control Unit</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.75rem; color:#64748b; font-weight:bold; margin-bottom:2px;'>⚙️ CORE COMPUTE TUNER</p>", unsafe_allow_html=True)
    selected_model = st.selectbox("Compute Base Engine:", [
        "google/gemini-2.5-flash",
        "google/gemini-2.5-pro",
        "deepseek/deepseek-chat",
        "meta-llama/llama-3.3-70b-instruct"
    ], label_visibility="collapsed")
    
    core_temperature = st.slider("Flow Variance (Temp):", 0.0, 1.0, 0.3, step=0.1)
    
    st.markdown("---")
    
    st.markdown("<p style='font-size:0.75rem; color:#64748b; font-weight:bold;'>📂 ACTIVE WORKSPACES</p>", unsafe_allow_html=True)
    new_title = st.text_input("Forge Target Workspace...", placeholder="Title...", label_visibility="collapsed")
    if st.button("➕ Inisialisasi Workspace", use_container_width=True):
        if new_title.strip():
            n_id = f"session_{int(time.time())}"
            save_json_file(os.path.join(DIR_ARCHIVE, f"{n_id}.json"), {
                "title": new_title.strip(), "created": datetime.now().strftime("%Y-%m-%d"),
                "updated": datetime.now().strftime("%Y-%m-%d"), "messages": []
            })
            st.session_state.active_session_id = n_id
            st.rerun()
            
    search_q = st.text_input("🔍 Filter Workspace Title...", placeholder="Search...", label_visibility="collapsed")
    archives = []
    for file_name in os.listdir(DIR_ARCHIVE):
        if file_name.endswith(".json"):
            f_id = file_name.replace(".json", "")
            data_load = load_json_file(os.path.join(DIR_ARCHIVE, file_name), {})
            if data_load: archives.append({"id": f_id, "title": data_load.get("title", f_id), "updated": data_load.get("updated", "")})
            
    if search_q.strip(): archives = [a for a in archives if search_q.lower() in a["title"].lower()]
    archives.sort(key=lambda x: x["updated"], reverse=True)
    
    if not archives:
        save_json_file(os.path.join(DIR_ARCHIVE, "default_core.json"), {"title": "Main System Workspace", "created": datetime.now().strftime("%Y-%m-%d"), "updated": datetime.now().strftime("%Y-%m-%d"), "messages": []})
        archives = [{"id": "default_core", "title": "Main System Workspace"}]

    for item in archives:
        style_lbl = f"⭐ {item['title']}" if item["id"] == st.session_state.active_session_id else f"📁 {item['title']}"
        if st.button(style_lbl, key=f"sb_btn_{item['id']}", use_container_width=True):
            st.session_state.active_session_id = item["id"]
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-size:0.75rem; color:#64748b; font-weight:bold;'>🧠 FLOW DIRECTIVES</p>", unsafe_allow_html=True)
    flow_mode = st.radio("Logic Directives Switch:", ["Pulse Speed", "Deep Flow", "Forge Engine"], label_visibility="collapsed")

# Mempersiapkan Data Workspace Aktif
active_file_path = os.path.join(DIR_ARCHIVE, f"{st.session_state.active_session_id}.json")
active_archive_data = load_json_file(active_file_path, {"title": "Workspace Link", "messages": []})

# Render Antarmuka Visual Atas
st.markdown(f'<div class="cyber-core-container"><div class="cyber-planet {st.session_state.planet_state}"></div></div>', unsafe_allow_html=True)

proj_intel = longterm_memory["project_intelligence"].get(st.session_state.active_session_id, {"lang": "General", "progress": "0%", "objective": "General Scope Tasks"})

st.html(f"""
<div style="display:flex; justify-content:center; gap:8px; margin-bottom:10px; font-size:0.75rem;">
    <div style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.2); padding:4px 10px; border-radius:12px; color:#38bdf8;">📂 Core: {active_archive_data.get("title")}</div>
    <div style="background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.2); padding:4px 10px; border-radius:12px; color:#c084fc;">🛠️ Intelligence: {proj_intel['lang']} | Progres: {proj_intel['progress']}</div>
</div>
""")

# Render Seluruh Riwayat Pesan Workspace
for msg in active_archive_data.get("messages", []):
    if msg["role"] == "user":
        st.html(f'<div style="display:flex; justify-content:flex-end; margin-bottom:12px;"><div class="bubble-user">{msg["content"]}</div></div>')
    elif msg["role"] == "assistant":
        with st.container():
            st.html('<div style="display:flex; justify-content:flex-start;"><div class="bubble-core"><div style="display:flex; align-items:center; gap:5px; margin-bottom:5px;"><div style="width:7px; height:7px; border-radius:50%; background:#38bdf8;"></div><div style="font-weight:700; color:#fff; font-size:0.8rem;">oXy AI</div></div><div style="color:#e2e8f0; line-height:1.6; font-size:0.95rem;">')
            st.markdown(msg["content"])
            st.html('</div></div></div>')

# Output Terminal Eksekusi Perintah Bawaan Internal System
if st.session_state.system_terminal_logs:
    with st.chat_message("assistant"):
        st.markdown("**🌐 oXy Built-In Tools System Execution Output**")
        for log in st.session_state.system_terminal_logs:
            st.code(log, language="bash")
    st.session_state.system_terminal_logs = []

# ==============================================================================
# 6. COMMANDS PROCESSOR MECHANISM
# ==============================================================================
def execute_internal_tool_command(user_text):
    text_cleaned = user_text.strip()
    if not text_cleaned.startswith("/"): return False
        
    parts = text_cleaned.split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    st.session_state.planet_state = "state-tool"
    
    if cmd == "/help":
        st.session_state.system_terminal_logs = [
            "oXy Nexus Core OS v5.0 Command Protocol Manifest:",
            "  /help                Show active system command protocols manifest",
            "  /calc [expr]         Safe AST isolated mathematical token evaluation",
            "  /uuid                Forge cryptographic absolute identifier token",
            "  /facts               Display long-term injected knowledge facts matrix",
            "  /clear-facts         Wipe all metadata facts inside memory database layer",
            "  /erase-workspace     Delete active workspace architecture permanently"
        ]
    elif cmd == "/calc":
        if not args:
            st.session_state.system_terminal_logs = ["Tool Error: Input calculation argument empty."]
        else:
            res = safe_eval_expr(args)
            st.session_state.system_terminal_logs = [f"Input Expression: {args}", f"Safe Numerical Output: {res}"]
    elif cmd == "/uuid":
        st.session_state.system_terminal_logs = [f"Cryptographic Identification Token Issued: {uuid.uuid4()}"]
    elif cmd == "/facts":
        facts = longterm_memory.get("user_facts", [])
        st.session_state.system_terminal_logs = ["Retrieving Long-Term Memory Core Fact Arrays:"] + [f" - {f}" for f in facts] if facts else ["Memory Database: No facts recorded."]
    elif cmd == "/clear-facts":
        longterm_memory["user_facts"] = []
        save_json_file(FILE_LONGTERM_MEM, longterm_memory)
        st.session_state.system_terminal_logs = ["Long-Term Knowledge Fact layers successfully wiped."]
    elif cmd == "/erase-workspace":
        if os.path.exists(active_file_path): os.remove(active_file_path)
        st.session_state.active_session_id = "default_core"
        st.session_state.system_terminal_logs = ["Target workspace folder unlinked from architecture. Session reset."]
    else:
        st.session_state.system_terminal_logs = [f"Protocol Command Error: Unknown directive '{cmd}'. Type /help for assistance."]
        st.session_state.planet_state = "state-warning"
        
    return True

# ==============================================================================
# 7. LOGIC DISTRIBUTION PIPELINE CONTROL LOOP
# ==============================================================================
if user_input := st.chat_input("Transmit logic instruction or enter command (/help)..."):
    st.html(f'<div style="display:flex; justify-content:flex-end; margin-bottom:12px;"><div class="bubble-user">{user_input}</div></div>')
    
    if user_input.strip().startswith("/"):
        execute_internal_tool_command(user_input)
        st.rerun()

    # Ekstraksi Injeksi Pengetahuan Jangka Panjang
    extracted_facts_block = "\n".join([f"- {fact}" for fact in longterm_memory.get("user_facts", [])])
    
    # MASTER SYSTEM PROMPT ARCHITECTURE (FIXED TRIPLE QUOTES ARCHITECTURE)
    base_identity = f"""OXY CORE ARCHITECTURE PERSONALITY MATRIX v5.0:
Name: oXy
Creator: Zayn
Branding Vocabulary Dictionary: Koneksi=Pulse, Berpikir=Flow, Menulis Kode=Forge, 
