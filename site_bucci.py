import streamlit as st
from google import genai  # Nova biblioteca oficial do Google
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (NOVO PADRÃO GOOGLE GENAI) ---
def chamar_ai_assistente(pergunta):
    # Verificação de Segurança da Chave nos Secrets
    if "GOOGLE_API_KEY" not in st.secrets:
        return "❌ Chave de API não configurada. Verifique os Secrets do Streamlit."

    try:
        # Inicializa o cliente com o novo padrão
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        
        prompt_config = f"""
        Você é o Dr. Tiago Bucci, psiquiatra da Bucci Clinic. 
        Sua missão é responder de forma médica, detalhada e empática.
        Fale sobre sintomas, biologia cerebral e a importância da família no tratamento.
        NUNCA dê doses de remédios. Termine incentivando o agendamento.
        
        Pergunta do Paciente: {pergunta}
        """

        # Chamada usando o novo SDK
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt_config
        )
        
        if response.text:
            return response.text

    except Exception as e:
        # Se a IA falhar (erro de cota ou conexão), usamos a Base Local de Segurança
        print(f"Erro na IA: {e}") # Log para debug
        pass

    # --- 3. BASE LOCAL DE SEGURANÇA (FALLBACK) ---
    p_min = pergunta.lower()
    if "depress" in p_min:
        return """### 🕯️ Depressão (Base Local)
        A depressão é uma condição neurobiológica que afeta a vitalidade e o prazer (Anedonia).
        Sintomas comuns: Fadiga extrema, alterações no sono/apetite e sentimentos de desesperança.
        Na Bucci Clinic, focamos na regulação neuroquímica e no suporte familiar para a recuperação total."""
    
    if "ansiedade" in p_min or "tag" in p_min:
        return """### ⚖️ Ansiedade e TAG (Base Local)
        A ansiedade patológica é um estado de alerta constante. 
        Sintomas: Preocupação excessiva, tensão muscular, taquicardia e insônia.
        O tratamento visa devolver a funcionalidade e o controle emocional ao paciente."""

    return "Não consegui processar os detalhes agora. Por favor, tente perguntar de outra forma ou fale conosco pelo WhatsApp."

# --- 4. CSS DESIGN (OTIMIZADO MOBILE) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .main-title {{ color: {cor_bucci}; text-align: center; font-size: 26px; font-weight: 800; margin: 0; }}
    .sub-title {{ text-align: center; color: #555; font-size: 15px; margin-bottom: 20px; }}
    
    /* Botões Tipo Aba */
    div.stButton > button {{
        width: 100% !important; border-radius: 12px !important; height: 3.8em !important;
        background-color: #f0f2f6; color: {cor_bucci}; border: none; font-weight: bold;
        text-align: left; padding-left: 20px; font-size: 16px; margin-top: 10px;
    }}
    .btn-active > div > button {{ background-color: {cor_bucci} !important; color: white !important; }}

    /* Área de Conteúdo */
    .content-area {{ 
        background-color: white; padding: 20px; border-radius: 0 0 12px 12px; 
        border: 1px solid #eee; border-top: none; margin-bottom: 15px;
    }}

    /* WhatsApp */
    .stLinkButton > a {{
        width: 100% !important; background-color: {cor_whatsapp} !important; color: white !important;
        border-radius: 12px !important; font-weight: bold !important; text-align: center !important;
        padding: 1.2em 0 !important; display: block !important; margin-top: 10px; text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE NAVEGAÇÃO ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# --- BOTÕES E CONTEÚDO (EFEITO ACORDEON) ---

# ABA INÍCIO
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 SOBRE A CLÍNICA"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Atendimento humanizado em Franca/SP com foco em diagnóstico preciso e suporte sistêmico familiar.</div>", unsafe_allow_html=True)

# ABA CHATBOT
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (DÚVIDAS)"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_new", clear_on_submit=True):
        u_input = st.text_input("Ex: Quais os sintomas de depressão?")
        if st.form_submit_button("Consultar IA"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Analisando base clínica..."):
                    res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# WHATSAPP FIXO
st.link_button("💬 AGENDAR VIA WHATSAPP", "https://wa.me/5516999674172")
