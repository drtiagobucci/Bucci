import streamlit as st
import requests
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 3. MOTOR DE IA (COM MÚLTIPLAS TENTATIVAS) ---
def chamar_ai_assistente(pergunta):
    # 1. Checa Base Local Primeiro (Mais rápido e seguro)
    p_min = pergunta.lower()
    for chave, resposta in BASE_LOCAL.items():
        if chave in p_min:
            return resposta

    # 2. Se não estiver na base local, tenta a IA do Google
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave de API não configurada."

    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Lista de URLs para tentar (v1beta e v1 com diferentes modelos)
    tentativas = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    ]

    payload = {"contents": [{"parts": [{"text": f"Você é o médico da Bucci Clinic. Responda: {pergunta}"}]}]}
    headers = {'Content-Type': 'application/json'}

    for url in tentativas:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                return res_json['candidates'][0]['content']['parts'][0]['text']
        except:
            continue # Tenta a próxima URL se esta falhar

    return "Não consegui detalhes específicos agora. Por favor, tente reformular a pergunta ou agende uma consulta via WhatsApp."

# --- 4. DESIGN CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer { display: none; }
    .main-title { color: #1a3a5a; text-align: center; font-size: 26px; font-weight: 800; }
    div.stButton > button {
        width: 100% !important; border-radius: 10px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: #1a3a5a; border: none; font-weight: bold;
    }
    .btn-active > div > button { background-color: #1a3a5a !important; color: white !important; }
    .content-area { background-color: white; padding: 20px; border: 1px solid #eee; border-radius: 0 0 10px 10px; margin-bottom: 10px; }
    .stLinkButton > a {
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. INTERFACE ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)

# Navegação
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Excelência em Saúde Mental e Cuidado Familiar.</div>", unsafe_allow_html=True)

is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_final_ultra", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida (ex: sintomas de depressão):")
        if st.form_submit_button("Consultar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Buscando informações clínicas..."):
                    res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 AGENDAR CONSULTA (WHATSAPP)", "https://wa.me/5516999674172")
