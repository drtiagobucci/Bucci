import streamlit as st
import google.generativeai as genai
import warnings

# Silencia o aviso de "FutureWarning" para não sujar os logs
warnings.filterwarnings("ignore", category=FutureWarning)

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (VERSÃO ESTÁVEL) ---
def chamar_ai_assistente(pergunta):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Chave de API não encontrada nos Secrets do Dashboard."

    try:
        # Configuração estável
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # Usando o modelo 1.5-flash que é o mais rápido e estável
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt_clinico = f"""
        Você é o Dr. Tiago Bucci, psiquiatra da Bucci Family Psychiatric Clinic.
        Sua missão é educar o paciente de forma empática e detalhada.
        Pergunta: {pergunta}
        
        REGRAS: 
        1. Explique sintomas de forma clara com listas.
        2. Destaque a importância da biologia cerebral e do apoio familiar.
        3. Nunca dê dosagens de medicamentos.
        4. Sempre recomende a consulta para diagnóstico.
        """
        
        response = model.generate_content(prompt_clinico)
        
        if response and response.text:
            return response.text
        else:
            return "O assistente está processando muitas informações. Tente novamente em instantes."

    except Exception as e:
        # Se der erro, ele vai te mostrar aqui
        return f"❌ Erro de Conexão: {str(e)}"

# --- 3. ESTILO CSS (DESIGN OTIMIZADO) ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .main-title {{ color: #1a3a5a; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 0px; }}
    .sub-title {{ text-align: center; color: #555; font-size: 15px; margin-bottom: 20px; }}
    
    div.stButton > button {{
        width: 100% !important; border-radius: 10px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: #1a3a5a; border: none; font-weight: bold;
        font-size: 16px; margin-top: 10px; text-align: left; padding-left: 20px;
    }}
    .btn-active > div > button {{ background-color: #1a3a5a !important; color: white !important; }}
    .content-area {{ background-color: white; padding: 20px; border: 1px solid #eee; border-radius: 0 0 10px 10px; margin-bottom: 10px; }}
    
    .stLinkButton > a {{
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; margin-top: 10px; text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Saúde Mental e Cuidado Familiar</p>", unsafe_allow_html=True)

# ABA INÍCIO
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 SOBRE A CLÍNICA"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Atendimento especializado em Franca/SP com foco em diagnóstico preciso e suporte sistêmico familiar.</div>", unsafe_allow_html=True)

# ABA CHAT
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (CHAT)"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_stable", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida (ex: sintomas de depressão):")
        if st.form_submit_button("Consultar Inteligência Clínica"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Analisando..."):
                    res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")
