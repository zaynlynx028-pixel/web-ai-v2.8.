import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime

# Setup dasar
st.set_page_config(page_title="oXy Nexus v5.1", layout="centered")

# Inisialisasi Klien API (Pastikan API Key sudah di-setting di Streamlit Secrets)
api_key = st.secrets.get("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

# Inisialisasi State
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- KOMPONEN UI ---
st.title("🌐 oXy Nexus v5.1")

# Menampilkan chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- PROSES CHAT (LOGIC FIX) ---
if prompt := st.chat_input("Transmit logic instruction..."):
    # 1. Tampilkan input user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Proses API Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Menggunakan stream untuk menghindari timeout
            stream = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Nexus Error: {e}")
            st.write("DEBUG: Pastikan OPENROUTER_API_KEY sudah benar di Settings > Secrets.")

