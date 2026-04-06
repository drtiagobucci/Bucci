import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Bucci Clinic | Saúde Mental",
    layout="centered", # Layout centralizado é melhor para celular
    page_icon="🧠"
)

# --- 2. ESTILO CSS (Otimizado para Celular) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    /* Esconde a barra lateral e menus padrão do Streamlit */
    [data-testid="stSidebar"] {{ display: none; }}
    
    /* Estilo do Título e Texto */
    .main-title {{
        color: {cor_bucci};
        text-align: center;
        font-size: 24px;
        font-weight: 800;
        margin-bottom: 5px;
    }}
    .sub-title {{
        text-align: center;
        color: #555;
        font-size: 16px;
        margin-bottom: 25px;
    }}

    /* Botões Verticais de Navegação */
    div.stButton > button {{
        width: 100% !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        background-color: white;
        color: {cor_bucci};
        border: 2px solid {cor_bucci};
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 10px;
        transition: 0.3s;
    }}
    
    /* Destaque para o botão ativo (Simulação via CSS injetado pelo Streamlit) */
    div.stButton > button:active, div.stButton > button:focus {{
        background-color: {cor_bucci} !important;
        color: white !important;
    }}

    /* Botão WhatsApp Especial */
    .stLinkButton > a {{
        width: 100% !important;
        background-color: {cor_whatsapp} !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 1em 0 !important;
        display: block !important;
        text-decoration: none !important;
        font-size: 16px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* Estilo dos Expanders e Cartões */
    .stExpander {{
        border: 1px solid #ddd !important;
        border-radius: 12px !important;
        background-color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def mudar_aba(nome):
    st.session_state.pagina = nome

# --- 4. CABEÇALHO ---
st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Saúde Mental e Cuidado Familiar</p>", unsafe_allow_html=True)

# Texto Introdutório Curto (Ideal para mobile)
st.write("Atendimento humanizado com foco no diagnóstico preciso e suporte à família. Escolha uma opção abaixo:")

# --- 5. MENU VERTICAL (BOTOÕES UM ABAIXO DO OUTRO) ---
# Usar colunas vazias nas laterais no desktop para não ficar largo demais, 
# mas no celular o Streamlit empilha automaticamente.
col_menu, _ = st.columns([1, 0.01]) 

with col_menu:
    if st.button("🏠 IR PARA O INÍCIO"):
        mudar_aba("Início")
        
    if st.button("📑 CONHECER TEMAS CLÍNICOS"):
        mudar_aba("Temas")
        
    if st.button("🤖 FALAR COM ASSISTENTE AI"):
        mudar_aba("Assistente")
        
    st.link_button("💬 AGENDAR VIA WHATSAPP", "https://wa.me/5516999674172")

st.markdown("---")

# --- 6. CONTEÚDO DINÂMICO ---

if st.session_state.pagina == "Início":
    st.subheader("Bem-vindo")
    st.write("""
    Na Bucci Clinic, entendemos que o cuidado emocional envolve 
    não apenas o paciente, mas todo o seu sistema familiar.
    
    **Direção:** Dr. Tiago Bucci
    **Local:** Franca/SP
    """)
    st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=800", caption="Cuidado especializado")

elif st.session_state.pagina == "Temas":
    st.subheader("📚 Temas de Especialidade")
    
    temas = {
        "👥 Saúde Mental na Família": "A família é o fator preditivo mais forte para o sucesso do tratamento.",
        "🧸 Psiquiatria Infantil": "Identificar sinais precocemente garante um crescimento saudável.",
        "⚖️ Ansiedade": "TAG, Pânico e Fobias. O objetivo é retomar a vida normal.",
        "🕯️ Depressão e Bipolaridade": "Tratamos a vitalidade e a regulação do humor.",
        "🧠 Psicoses": "Diagnóstico rápido para proteção do sistema nervoso."
    }
    
    for titulo, texto in temas.items():
        with st.expander(titulo):
            st.write(texto)

elif st.session_state.pagina == "Assistente":
    st.subheader("🤖 Assistente Virtual")
    st.caption("Tire dúvidas gerais sobre saúde mental.")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ex: O que é TDAH?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        resposta = "Este é um exemplo de resposta. Para informações oficiais, consulte o Dr. Tiago Bucci."
        
        with st.chat_message("assistant"):
            st.markdown(resposta)
            st.session_state.chat_history.append({"role": "assistant", "content": resposta})

# --- 7. RODAPÉ ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 14px;'>
        <p>📞 (16) 3724-0791<br>
        📍 Franca/SP</p>
    </div>
""", unsafe_allow_html=True)
