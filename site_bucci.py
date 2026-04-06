import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. RESPOSTAS DE SEGURANÇA (Caso a IA falhe) ---
RESPOSTAS_PADRAO = {
    "depressão": """A depressão na visão da Bucci Clinic envolve sintomas como: 
    - **Anedonia:** Perda de interesse em atividades que antes davam prazer.
    - **Alterações Biológicas:** Distúrbios de sono, fadiga crônica e mudanças no apetite.
    - **Sintomas Cognitivos:** Dificuldade de concentração e sentimentos de desesperança.
    O tratamento foca na regulação neuroquímica e suporte familiar. Recomendamos uma consulta para avaliação detalhada.""",
    "ansiedade": "A ansiedade patológica manifesta-se por preocupação excessiva, taquicardia, insônia e sensação de medo constante. O tratamento visa devolver a funcionalidade ao paciente.",
    "tdah": "O TDAH envolve desatenção, hiperatividade e impulsividade. Na infância, prejudica o aprendizado e socialização; em adultos, afeta a produtividade e organização."
}

# --- 3. MOTOR DE IA ---
def chamar_ai_assistente(pergunta):
    # Tenta usar a IA
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            contexto = f"Você é o médico assistente da Bucci Clinic. Responda de forma detalhada e acolhedora: {pergunta}"
            response = model.generate_content(contexto)
            return response.text
    except Exception:
        pass # Se der erro, cai no sistema de busca abaixo
    
    # Sistema de Busca Simples (Fallback)
    pergunta_min = pergunta.lower()
    for chave in RESPOSTAS_PADRAO:
        if chave in pergunta_min:
            return RESPOSTAS_PADRAO[chave]
    
    return "Para detalhes específicos sobre este tema, recomendamos uma breve conversa com o Dr. Tiago Bucci via WhatsApp, para que possamos oferecer uma orientação segura e personalizada."

# --- 4. ESTILO CSS (Design Mobile-First) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .main-title {{ color: {cor_bucci}; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 0px; }}
    .sub-title {{ text-align: center; color: #555; font-size: 15px; margin-bottom: 20px; }}
    div.stButton > button {{
        width: 100% !important; border-radius: 10px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: {cor_bucci}; border: none;
        font-weight: bold; font-size: 16px; margin-top: 10px; text-align: left; padding-left: 20px;
    }}
    .btn-active > div > button {{ background-color: {cor_bucci} !important; color: white !important; }}
    .content-area {{ background-color: white; padding: 20px; border: 1px solid #eee; border-radius: 0 0 10px 10px; margin-bottom: 10px; border-top: none; }}
    .stLinkButton > a {{
        width: 100% !important; background-color: {cor_whatsapp} !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; margin-top: 10px; text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE NAVEGAÇÃO ---
if 'aba_aberta' not in st.session_state: st.session_state.aba_aberta = "Início"
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def alternar_aba(nome): st.session_state.aba_aberta = nome

# --- 6. INTERFACE ---
st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# ABA INÍCIO
is_active = "btn-active" if st.session_state.aba_aberta == "Início" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO / SOBRE NÓS"): alternar_aba("Início")
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba_aberta == "Início":
    st.markdown("<div class='content-area'>Atendimento humanizado voltado para o acolhimento do indivíduo e da família.</div>", unsafe_allow_html=True)

# ABA TEMAS
is_active = "btn-active" if st.session_state.aba_aberta == "Temas" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("📑 TEMAS E ESPECIALIDADES"): alternar_aba("Temas")
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba_aberta == "Temas":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    with st.expander("Depressão"): st.write(RESPOSTAS_PADRAO["depressão"])
    with st.expander("Ansiedade"): st.write(RESPOSTAS_PADRAO["ansiedade"])
    st.markdown("</div>", unsafe_allow_html=True)

# ABA ASSISTENTE (CHATBOT)
is_active = "btn-active" if st.session_state.aba_aberta == "Assistente" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (CHAT)"): alternar_aba("Assistente")
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba_aberta == "Assistente":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Sua pergunta:")
        if st.form_submit_button("Consultar"):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            resposta = chamar_ai_assistente(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": resposta})
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")
