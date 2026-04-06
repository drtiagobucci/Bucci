import streamlit as st
import requests
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (CONEXÃO DIRETA VIA HTTP - SEM BIBLIOTECA) ---
def chamar_ai_assistente(pergunta):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Chave de API não configurada nos Secrets."

    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # URL oficial do Google Gemini (Versão v1 estável)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Montagem da pergunta (Prompt)
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Você é o Dr. Tiago Bucci, psiquiatra. Responda de forma detalhada e empática em português: {pergunta}"
            }]
        }]
    }

    try:
        # Faz a chamada direta ao servidor do Google
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        res_json = response.json()
        
        # Extrai a resposta do JSON do Google
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            erro_msg = res_json.get('error', {}).get('message', 'Erro desconhecido')
            return f"❌ Erro no Servidor do Google: {erro_msg}"

    except Exception as e:
        return f"❌ Erro de Conexão: {str(e)}"

# --- 3. DESIGN CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer { display: none; }
    .main-title { color: #1a3a5a; text-align: center; font-size: 26px; font-weight: 800; }
    div.stButton > button {
        width: 100% !important; border-radius: 10px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: #1a3a5a; border: none; font-weight: bold;
    }
    .btn-active > div > button { background-color: #1a3a5a !important; color: white !important; }
    .content-area { background-color: white; padding: 20px; border: 1px solid #eee; border-radius: 0 0 10px 10px; }
    .stLinkButton > a {
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)

# Navegação Simples
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Atendimento especializado em saúde mental.</div>", unsafe_allow_html=True)

is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_direct", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida:")
        if st.form_submit_button("Consultar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Consultando inteligência clínica..."):
                    res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 WHATSAPP", "https://wa.me/5516999674172")
