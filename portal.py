import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA ---
def chamar_ai_assistente(pergunta):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave não configurada nos Secrets."

    try:
        # Configura a API
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # IMPORTANTE: Em versões novas, não usamos o prefixo 'models/'
        # O modelo 'gemini-1.5-flash' é o padrão atual.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(pergunta)
        
        if response and response.text:
            return response.text
        else:
            return "O Google não retornou texto. Tente reformular a pergunta."

    except Exception as e:
        return f"❌ Erro Técnico: {str(e)}"

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

# Navegação
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
    
    with st.form(key="chat_final_v3", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida:")
        if st.form_submit_button("Consultar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 WHATSAPP", "https://wa.me/5516999674172")
