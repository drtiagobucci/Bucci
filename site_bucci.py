import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

def chamar_ai_assistente(pergunta):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave de API não configurada."

    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # TENTATIVA 1: Gemini 1.5 Flash (Moderno)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(pergunta)
        return response.text
    except Exception as e:
        if "404" in str(e):
            # TENTATIVA 2: Gemini Pro (Estável) se o Flash não for encontrado
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(pergunta)
                return response.text
            except Exception as e2:
                return f"❌ Erro em ambos os modelos: {str(e2)}"
        return f"❌ Erro de Conexão: {str(e)}"

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
    .stLinkButton > a {
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)

# Botões de Navegação
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Atendimento especializado em saúde mental e cuidado familiar.</div>", unsafe_allow_html=True)

is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_final_v2", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida:")
        if st.form_submit_button("Consultar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 AGENDAR WHATSAPP", "https://wa.me/5516999674172")
