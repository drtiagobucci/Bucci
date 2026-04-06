import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Bucci Clinic",
    layout="centered",
    page_icon="🧠"
)

# --- 2. ESTILO CSS (Otimizado para Mobile e Acordeon) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    /* Esconde menus desnecessários */
    [data-testid="stSidebar"], footer {{ display: none; }}
    
    .main-title {{
        color: {cor_bucci};
        text-align: center;
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 0px;
    }}
    .sub-title {{
        text-align: center;
        color: #555;
        font-size: 15px;
        margin-bottom: 20px;
    }}

    /* Estilo dos Botões Tipo Aba */
    div.stButton > button {{
        width: 100% !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        background-color: #f0f2f6;
        color: {cor_bucci};
        border: none;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
        text-align: left;
        padding-left: 20px;
    }}
    
    /* Botão Ativo */
    .btn-active > div > button {{
        background-color: {cor_bucci} !important;
        color: white !important;
    }}

    /* Área de Conteúdo que surge abaixo do botão */
    .content-area {{
        background-color: white;
        padding: 20px;
        border: 1px solid #eee;
        border-radius: 0 0 10px 10px;
        margin-bottom: 10px;
        border-top: none;
    }}

    /* Botão WhatsApp */
    .stLinkButton > a {{
        width: 100% !important;
        background-color: {cor_whatsapp} !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 1em 0 !important;
        display: block !important;
        margin-top: 10px;
        text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE ESTADO ---
if 'aba_aberta' not in st.session_state:
    st.session_state.aba_aberta = "Início"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def alternar_aba(nome):
    # Se clicar na mesma aba, ela fecha (opcional), ou apenas muda
    st.session_state.aba_aberta = nome

# --- 4. CABEÇALHO ---
st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# --- 5. INTERFACE EM CASCATA (BOTÃO + CONTEÚDO) ---

# --- ABA 1: INÍCIO ---
is_active = "btn-active" if st.session_state.aba_aberta == "Início" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO / SOBRE NÓS"):
    alternar_aba("Início")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba_aberta == "Início":
    st.markdown("""
        <div class='content-area'>
            <p>Atendimento humanizado voltado para o acolhimento do indivíduo e da família. 
            Nossa missão é oferecer diagnóstico preciso e tratamento baseado em evidências.</p>
            <p><b>Diretor:</b> Dr. Tiago Bucci<br><b>Local:</b> Franca/SP</p>
        </div>
    """, unsafe_allow_html=True)

# --- ABA 2: TEMAS CLÍNICOS ---
is_active = "btn-active" if st.session_state.aba_aberta == "Temas" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("📑 TEMAS E ESPECIALIDADES"):
    alternar_aba("Temas")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba_aberta == "Temas":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    with st.expander("👥 Saúde Mental na Família"):
        st.write("A família é o pilar do sucesso no tratamento psiquiátrico.")
    with st.expander("🧸 Psiquiatria Infantil"):
        st.write("Cuidado especializado para o neurodesenvolvimento na infância.")
    with st.expander("⚖️ Ansiedade e Pânico"):
        st.write("Tratamentos modernos para controle da ansiedade patológica.")
    with st.expander("🧠 Transtornos de Humor"):
        st.write("Abordagem integrada para Depressão e Transtorno Bipolar.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- ABA 3: ASSISTENTE AI (CHATBOT) ---
is_active = "btn-active" if st.session_state.aba_aberta == "Assistente" else ""
st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (DÚVIDAS)"):
    alternar_aba("Assistente")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba_aberta == "Assistente":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    st.info("Tire dúvidas gerais. Este assistente não substitui consulta médica.")
    
    # Exibir histórico de mensagens dentro da aba
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # FORMULÁRIO DE INPUT (Evita que o chat-input suma no mobile)
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Sua pergunta:", placeholder="Ex: O que é depressão?")
        submit_button = st.form_submit_button("Enviar Pergunta")

    if submit_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        # Resposta Simulada (Integre com sua função do Gemini aqui)
        resposta = "Obrigado por sua pergunta. Orientações educativas da Bucci Clinic sugerem que sintomas persistentes devem ser avaliados por um médico. Deseja saber mais sobre algum tema específico?"
        st.session_state.chat_history.append({"role": "assistant", "content": resposta})
        st.rerun() # Atualiza a tela para mostrar a resposta
    st.markdown("</div>", unsafe_allow_html=True)

# --- ABA 4: WHATSAPP (BOTÃO FIXO DE AÇÃO) ---
st.link_button("💬 AGENDAR CONSULTA (WHATSAPP)", "https://wa.me/5516999674172")

# --- 6. RODAPÉ ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 13px; padding: 20px;'>
        <hr>
        📞 (16) 3724-0791 | (16) 99967-4172<br>
        📍 Franca/SP
    </div>
""", unsafe_allow_html=True)
