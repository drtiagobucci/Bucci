import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA (SEO e Layout) ---
st.set_page_config(
    page_title="Bucci Clinic | Saúde Mental",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# --- 2. TEMAS CLÍNICOS (Organizados para melhor leitura) ---
TEMAS_CLINICOS = {
    "👥 Família e Suporte": {
        "icon": "👥",
        "texto": """A família é o elo decisivo. O acolhimento substitui o julgamento, atuando como protetor neurobiológico."""
    },
    "🧸 Psiquiatria Infantil": {
        "icon": "🧸",
        "texto": """Fase crítica. Sinais como isolamento ou queda escolar exigem olhar atento e multidisciplinar."""
    },
    "⚖️ Ansiedade": {
        "icon": "⚖️",
        "texto": """Além do medo comum. O tratamento visa devolver a funcionalidade e o controle emocional ao paciente."""
    },
    "🕯️ Humor (Depressão/Bipolar)": {
        "icon": "🕯️",
        "texto": """Vitalidade e regulação. Tratamos a anedonia e as oscilações de humor com foco na biologia e terapia."""
    },
    "🧠 Psicoses": {
        "icon": "🧠",
        "texto": """Urgência no diagnóstico. O tratamento precoce protege o sistema nervoso contra deterioração cognitiva."""
    }
}

# --- 3. MOTOR DE IA (Refatorado) ---
def chamar_ai_assistente(pergunta):
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        contexto = f"""
        Você é o Assistente Virtual da Bucci Clinic (Dr. Tiago Bucci).
        Use o tom: Médico, empático, sério, porém acessível.
        Baseie-se nestes pilares: {list(TEMAS_CLINICOS.keys())}.
        
        REGRAS CRÍTICAS:
        1. Se perguntarem sobre doses ou remédios específicos, diga que a automedicação é perigosa e apenas o médico ajusta doses.
        2. Se houver menção a ideação suicida, forneça o link do CVV (188) imediatamente.
        3. Enfatize que você é uma IA e não substitui a consulta.
        
        Pergunta do Paciente: {pergunta}
        """
        response = model.generate_content(contexto)
        return response.text
    except Exception as e:
        return "Estou passando por uma manutenção técnica breve. Por favor, tente novamente em instantes."

# --- 4. CSS PERSONALIZADO (Estética Premium) ---
cor_primaria = "#1a3a5a"  # Azul Marinho Bucci
cor_fundo = "#f0f2f6"

st.markdown(f"""
    <style>
    /* Importando fonte elegante */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Estilização de Containers */
    .stApp {{
        background-color: {cor_fundo};
    }}
    
    /* Cartões de Conteúdo */
    .content-card {{
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid {cor_primaria};
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}

    /* Botões Laterais */
    .stButton > button {{
        width: 100%;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
        font-weight: 500;
    }}
    
    .stButton > button:hover {{
        border-color: {cor_primaria};
        color: {cor_primaria};
        background-color: #f0f7ff;
    }}

    /* Ajuste de Títulos */
    h1, h2, h3 {{
        color: {cor_primaria};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'mensagens' not in st.session_state:
    st.session_state.mensagens = []

def ir_para(nome):
    st.session_state.pagina = nome

# --- 6. BARRA LATERAL (Sidebar) ---
with st.sidebar:
    # Logo Centralizada
    st.markdown(f"<h1 style='text-align: center; color: {cor_primaria};'>Bucci Clinic</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Menu de Navegação
    st.subheader("Menu")
    if st.button("🏠 Início"): ir_para("Início")
    if st.button("📑 Temas Clínicos"): ir_para("Temas")
    if st.button("🤖 Assistente AI"): ir_para("Assistente")
    
    st.markdown("---")
    st.subheader("Área Restrita")
    st.link_button("📂 Prontuário Eletrônico", "https://tiagobucci.streamlit.app/", use_container_width=True)
    
    # Rodapé da Sidebar
    st.markdown("---")
    st.caption("📍 Franca/SP")
    st.caption("📞 (16) 3724-0791")

# --- 7. PÁGINAS ---

if st.session_state.pagina == "Início":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("Excelência em Saúde Mental")
        st.markdown(f"""
            <div class='content-card'>
                <h3>Bem-vindo à Bucci Family Psychiatric Clinic</h3>
                <p>Nossa abordagem integra a biologia neuroquímica com o suporte emocional familiar. 
                Acreditamos que o tratamento eficaz olha para o indivíduo como um todo, não apenas para o sintoma.</p>
                <br>
                <b>"Cuidar de uma pessoa é cuidar de todo o seu sistema."</b>
            </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Dica:** Use nosso Assistente Virtual na barra lateral para tirar dúvidas rápidas sobre transtornos.")

    with col2:
        st.markdown("### Agendamento")
        st.link_button("💬 WhatsApp", "https://wa.me/5516999674172", use_container_width=True)
        st.markdown("""
        **Horário de Atendimento:**  
        Segunda a Sexta: 08h - 18h  
        """)

elif st.session_state.pagina == "Temas":
    st.title("Biblioteca de Saúde Mental")
    st.write("Explore os principais temas tratados em nossa clínica:")
    
    # Organização em Grid (Colunas)
    cols = st.columns(2)
    for i, (titulo, info) in enumerate(TEMAS_CLINICOS.items()):
        with cols[i % 2]:
            with st.expander(f"{info['icon']} {titulo}", expanded=False):
                st.markdown(info['texto'])
                st.button("Saiba mais sobre isso", key=f"btn_{titulo}", on_click=ir_para, args=("Assistente",))

elif st.session_state.pagina == "Assistente":
    st.title("🤖 Assistente de Orientação")
    
    # Botão para limpar conversa
    if st.button("Limpar Histórico", type="secondary"):
        st.session_state.mensagens = []
        st.rerun()

    # Chat
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Como posso te ajudar hoje?"):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                full_response = chamar_ai_assistente(prompt)
                st.markdown(full_response)
                st.session_state.mensagens.append({"role": "assistant", "content": full_response})
