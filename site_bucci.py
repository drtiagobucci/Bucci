import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (CONEXÃO REAL) ---
def chamar_ai_assistente(pergunta):
    try:
        # Configura a chave (Certifique-se de que está no Secrets do Streamlit)
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        contexto = f"""
        Você é o Assistente Especialista da Bucci Family Psychiatric Clinic.
        Sua missão é educar pacientes sobre saúde mental de forma detalhada, empática e profissional.
        
        DIRETRIZES:
        1. Se o usuário pedir detalhes (ex: sintomas de depressão), forneça uma lista clínica clara (anedonia, fadiga, alterações de sono, etc).
        2. Explique a importância do olhar biológico e familiar (marca registrada da Bucci Clinic).
        3. NUNCA dê um diagnóstico fechado. 
        4. Sempre use termos como "Sinais comuns incluem..." ou "Clinicamente observamos...".
        5. Termine incentivando a avaliação com o Dr. Tiago Bucci para um plano personalizado.
        
        Pergunta do Paciente: {pergunta}
        """
        response = model.generate_content(contexto)
        return response.text
    except Exception as e:
        return "Estou com uma instabilidade técnica momentânea. Por favor, tente novamente em alguns segundos."

# --- 3. ESTILO CSS (Design Mobile-First) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .main-title {{ color: {cor_bucci}; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 0px; }}
    .sub-title {{ text-align: center; color: #555; font-size: 15px; margin-bottom: 20px; }}

    /* Botões Verticais */
    div.stButton > button {{
        width: 100% !important; border-radius: 10px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: {cor_bucci}; border: none;
        font-weight: bold; font-size: 16px; margin-top: 10px; text-align: left; padding-left: 20px;
    }}
    .btn-active > div > button {{ background-color: {cor_bucci} !important; color: white !important; }}

    /* Área de Conteúdo abaixo do botão */
    .content-area {{
        background-color: white; padding: 20px; border: 1px solid #eee;
        border-radius: 0 0 10px 10px; margin-bottom: 10px; border-top: none;
    }}

    /* Botão WhatsApp */
    .stLinkButton > a {{
        width: 100% !important; background-color: {cor_whatsapp} !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; margin-top: 10px; text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE NAVEGAÇÃO ---
if 'aba_aberta' not in st.session_state:
    st.session_state.aba_aberta = "Início"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def alternar_aba(nome):
    st.session_state.aba_aberta = nome

# --- 5. INTERFACE ---
st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# --- ABA 1: INÍCIO ---
is_active = "btn-active" if st.session_state.aba_aberta == "Início" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO / SOBRE NÓS"):
    alternar_aba("Início")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba_aberta == "Início":
    st.markdown("""<div class='content-area'>
        <p>Atendimento humanizado voltado para o acolhimento do indivíduo e da família. 
        Especialistas em diagnóstico preciso e tratamento baseado em evidências.</p>
        <p><b>Diretor:</b> Dr. Tiago Bucci<br><b>Local:</b> Franca/SP</p>
    </div>""", unsafe_allow_html=True)

# --- ABA 2: TEMAS CLÍNICOS ---
is_active = "btn-active" if st.session_state.aba_aberta == "Temas" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("📑 TEMAS E ESPECIALIDADES"):
    alternar_aba("Temas")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba_aberta == "Temas":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    with st.expander("👥 Saúde Mental na Família"):
        st.write("A participação familiar é o fator preditivo mais forte para o sucesso do tratamento.")
    with st.expander("🧸 Psiquiatria Infantil"):
        st.write("Diagnóstico e intervenção precoce em TDAH, TEA e Transtornos de Aprendizado.")
    with st.expander("⚖️ Ansiedade e Pânico"):
        st.write("Tratamento focado na regulação neuroquímica e retomada da funcionalidade.")
    with st.expander("🧠 Transtornos de Humor"):
        st.write("Abordagem detalhada para Depressão (Anedonia) e Transtorno Bipolar.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- ABA 3: ASSISTENTE AI (INTEGRAÇÃO GEMINI) ---
is_active = "btn-active" if st.session_state.aba_aberta == "Assistente" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (PERGUNTAR AO IA)"):
    alternar_aba("Assistente")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba_aberta == "Assistente":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    st.info("O assistente detalhará sintomas e orientações conforme os protocolos clínicos.")
    
    # Histórico do Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Formulário de Pergunta
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Digite sua dúvida (ex: sintomas de depressão):")
        submit_button = st.form_submit_button("Consultar Inteligência Clínica")

    if submit_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("Analisando base de conhecimento..."):
            # CHAMADA REAL DA IA
            resposta_ia = chamar_ai_assistente(user_input)
            
        st.session_state.chat_history.append({"role": "assistant", "content": resposta_ia})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- BOTÃO FINAL: WHATSAPP ---
st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")

st.markdown("<br><hr><p style='text-align: center; color: gray; font-size: 12px;'>📞 (16) 3724-0791 | Franca/SP</p>", unsafe_allow_html=True)
