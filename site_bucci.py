import streamlit as st
from google import genai
import os

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (COM EXIBIÇÃO DE ERRO REAL) ---
def chamar_ai_assistente(pergunta):
    # Verificação amigável de segredos
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: A chave GOOGLE_API_KEY não foi encontrada nos Secrets do Streamlit Cloud."

    try:
        # Tenta conectar usando o novo padrão
        api_key = st.secrets["GOOGLE_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Você é o Dr. Tiago Bucci. Responda: {pergunta}"
        )
        
        if response and response.text:
            return response.text
        else:
            return "O Google não devolveu uma resposta. Tente novamente."

    except Exception as e:
        # ESTE PONTO É CRUCIAL: Vai mostrar o erro real no seu site
        return f"❌ Erro Técnico da IA: {str(e)}"

# --- 3. CSS DESIGN ---
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
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)

# Botão Início
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Bem-vindo à nossa clínica.</div>", unsafe_allow_html=True)

# Botão Chat
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_web", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida:")
        if st.form_submit_button("Enviar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 WHATSAPP", "https://wa.me/5516999674172")
