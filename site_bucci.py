import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- MOTOR DE IA (REVISADO) ---
def chamar_ai_assistente(pergunta):
    pergunta_lower = pergunta.lower()
    
    # 1. TENTATIVA COM GEMINI (IA REAL)
    try:
        # Verifica se a chave existe
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt_clinico = f"""
            Você é o Assistente Virtual da Bucci Family Psychiatric Clinic.
            Responda de forma médica, empática e detalhada.
            Dê ênfase aos sintomas biológicos e à importância da família.
            Pergunta: {pergunta}
            """
            
            response = model.generate_content(prompt_clinico)
            if response and response.text:
                return response.text
        else:
            st.warning("⚠️ Chave de API não configurada nos Secrets do Streamlit.")
    except Exception as e:
        st.error(f"❌ Erro de Conexão com a IA: {e}")

    # 2. SISTEMA DE SEGURANÇA (Se a IA falhar ou não houver chave)
    # Lista de respostas prontas para os temas principais
    base_local = {
        "depress": """**Sintomas Depressivos (Visão Bucci Clinic):**
        * **Anedonia:** Perda da capacidade de sentir prazer.
        * **Energia:** Fadiga extrema e lentidão motora.
        * **Sono/Apetite:** Insônia ou excesso de sono; mudanças no peso.
        * **Cognição:** Sentimentos de culpa e dificuldade de decisão.
        * **Importância:** O tratamento foca na regulação neuroquímica e suporte familiar.""",
        
        "tag": """**Transtorno de Ansiedade Generalizada (TAG):**
        * **Sintomas:** Preocupação excessiva, tensão muscular e irritabilidade.
        * **Físico:** Taquicardia, sudorese e "nó na garganta".
        * **Foco:** O tratamento visa devolver a funcionalidade e o controle emocional.""",
        
        "infantil": "A psiquiatria infantil foca no neurodesenvolvimento (TDAH, TEA) e suporte escolar/familiar."
    }

    # Busca na base local se a palavra-chave estiver na pergunta
    for chave, resposta in base_local.items():
        if chave in pergunta_lower:
            return resposta

    return "Não consegui acessar minha base detalhada agora. Por favor, tente perguntar de outra forma ou entre em contato via WhatsApp."

# --- CSS (DESIGN PREMIUM) ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .stApp {{ background-color: #ffffff; }}
    .main-title {{ color: #1a3a5a; text-align: center; font-size: 28px; font-weight: 800; margin-bottom: 5px; }}
    .sub-title {{ text-align: center; color: #555; font-size: 16px; margin-bottom: 25px; }}
    
    /* Botões de Navegação */
    div.stButton > button {{
        width: 100% !important; border-radius: 12px !important; height: 3.5em !important;
        background-color: #f8f9fa; color: #1a3a5a; border: 1px solid #eee;
        font-weight: bold; font-size: 16px; margin-top: 10px; text-align: left; padding-left: 20px;
    }}
    .btn-active > div > button {{ background-color: #1a3a5a !important; color: white !important; border: none; }}

    /* Área de Chat */
    .content-area {{ background-color: #ffffff; padding: 15px; border-radius: 0 0 12px 12px; border: 1px solid #f0f2f6; border-top: none; }}
    
    /* Botão WhatsApp */
    .stLinkButton > a {{
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 12px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; margin-top: 15px; text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

# --- INTERFACE ---
st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Saúde Mental e Cuidado Familiar</p>", unsafe_allow_html=True)

# ABA INÍCIO
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 SOBRE A CLÍNICA"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Atendimento especializado com foco no diagnóstico preciso e na integração familiar.</div>", unsafe_allow_html=True)

# ABA CHAT
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (CHAT)"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_final", clear_on_submit=True):
        u_input = st.text_input("Digite sua dúvida:")
        if st.form_submit_button("Enviar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Consultando..."):
                    res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 AGENDAR VIA WHATSAPP", "https://wa.me/5516999674172")
