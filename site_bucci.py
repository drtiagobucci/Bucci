import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Bucci Clinic | Saúde Mental",
    layout="wide",
    page_icon="🧠"
)

# --- 2. ESTILO CSS (Personalização) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    /* Remove margens extras do Streamlit */
    .block-container {{ padding-top: 2rem; }}
    
    /* Estilo do Título Principal */
    .main-title {{
        color: {cor_bucci};
        text-align: center;
        font-weight: 800;
        margin-bottom: 0px;
    }}
    .sub-title {{
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }}

    /* Estilo dos Botões de Navegação */
    div.stButton > button {{
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: white;
        color: {cor_bucci};
        border: 2px solid {cor_bucci};
        font-weight: bold;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: {cor_bucci};
        color: white;
    }}

    /* Estilo do Botão WhatsApp */
    .stLinkButton > a {{
        width: 100% !important;
        background-color: {cor_whatsapp} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 0.7em 0 !important;
        display: inline-block !important;
        text-decoration: none !important;
    }}

    /* Cartão de Conteúdo */
    .content-card {{
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        border-bottom: 4px solid {cor_bucci};
        margin-top: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def mudar_aba(nome):
    st.session_state.pagina = nome

# --- 4. CABEÇALHO E INTRODUÇÃO ---
st.markdown("<h1 class='main-title'>BUCCI FAMILY PSYCHIATRIC CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Excelência em Saúde Mental e Cuidado Familiar</p>", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; max-width: 800px; margin: 0 auto;'>
        <p>Atendimento humanizado voltado para o acolhimento do indivíduo e da família. 
        Entendemos que o sofrimento emocional reverbera em todo o sistema familiar, 
        por isso oferecemos diagnóstico preciso e tratamento baseado em evidências científicas.</p>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# --- 5. MENU DE BOTÕES (Substituindo a Barra Lateral) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 INÍCIO"):
        mudar_aba("Início")

with col2:
    if st.button("📑 TEMAS CLÍNICOS"):
        mudar_aba("Temas")

with col3:
    if st.button("🤖 ASSISTENTE AI"):
        mudar_aba("Assistente")

with col4:
    st.link_button("💬 WHATSAPP", "https://wa.me/5516999674172")

st.write("---")

# --- 6. CONTEÚDO DINÂMICO ---

# Dados dos Temas
TEMAS_CLINICOS = {
    "👥 Família": "A família é o elo decisivo. O acolhimento substitui o julgamento.",
    "🧸 Psiquiatria Infantil": "Fase crítica. Sinais como isolamento exigem olhar atento.",
    "⚖️ Ansiedade": "O tratamento visa devolver a funcionalidade e o controle emocional.",
    "🕯️ Humor": "Tratamos depressão e bipolaridade com foco na regulação biológica.",
    "🧠 Psicoses": "Diagnóstico precoce é crucial para a proteção do sistema nervoso."
}

if st.session_state.pagina == "Início":
    st.markdown(f"""
        <div class='content-card'>
            <h3>Bem-vindo à nossa Clínica</h3>
            <p>Selecione uma das opções acima para explorar nossos temas de especialidade 
            ou conversar com nossa Inteligência Artificial para orientações rápidas.</p>
            <p><b>Diretor Clínico:</b> Dr. Tiago Bucci<br>
            <b>Localização:</b> Franca/SP</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.pagina == "Temas":
    st.subheader("📚 Biblioteca de Conhecimento")
    cols = st.columns(2)
    for i, (titulo, texto) in enumerate(TEMAS_CLINICOS.items()):
        with cols[i % 2]:
            with st.expander(titulo):
                st.write(texto)

elif st.session_state.pagina == "Assistente":
    st.subheader("🤖 Assistente de Orientação Clínica")
    st.info("Este assistente fornece informações educativas. Não substitui consulta médica.")
    
    # Simulação de Chat ou Integração com Gemini
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Pergunte algo sobre saúde mental..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Aqui entraria sua função chamar_ai_assistente(prompt)
        resposta = "Esta é uma resposta educativa baseada nos protocolos da Bucci Clinic. Para um diagnóstico real, agende uma consulta via WhatsApp."
        
        with st.chat_message("assistant"):
            st.markdown(resposta)
            st.session_state.chat_history.append({"role": "assistant", "content": resposta})

# --- 7. RODAPÉ ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.caption("📞 (16) 3724-0791 | (16) 99967-4172")
with col_f2:
    st.markdown("<p style='text-align:right; color:gray; font-size: 0.8rem;'>Bucci Clinic © 2024</p>", unsafe_allow_html=True)
