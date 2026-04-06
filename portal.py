import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (VERSÃO ROBUSTA - EVITA ERRO 404) ---
def chamar_ai_assistente(pergunta):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave de API não configurada nos Secrets."
    
    try:
        # Configuração da Chave
        api_key = st.secrets["GOOGLE_API_KEY"].strip()
        genai.configure(api_key=api_key)
        
        # DESCOBERTA AUTOMÁTICA DE MODELO (O segredo para não dar 404)
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not modelos_disponiveis:
            return "❌ Nenhum modelo de IA disponível para esta conta."
            
        # Seleciona o melhor modelo disponível (prioriza o Flash)
        modelo_final = next((m for m in modelos_disponiveis if 'flash' in m), modelos_disponiveis[0])
        model = genai.GenerativeModel(modelo_final)
        
        # Prompt de Identidade do Dr. Tiago Bucci
        prompt_completo = (
            f"Você é o Dr. Tiago Bucci, psiquiatra. Responda de forma detalhada e empática em português, "
            f"usando listas e negritos. Nunca forneça doses de medicamentos. "
            f"Sempre reforce que a resposta é informativa e não substitui consulta. "
            f"Pergunta: {pergunta}"
        )
        
        response = model.generate_content(prompt_completo)
        return response.text

    except Exception as e:
        return f"❌ Erro na conexão com a IA: {str(e)}"

# --- 3. DESIGN CSS (ESTILO VERTICAL MOBILE & DARK MODE) ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    [data-testid="stSidebar"], footer, header { display: none; }
    
    .main-title { color: #1a3a5a; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #555; font-size: 15px; margin-bottom: 25px; }
    
    /* Botões empilhados (Mobile First) */
    div.stButton > button {
        width: 100% !important; 
        border-radius: 12px !important; 
        height: 3.8em !important;
        background-color: rgba(128, 128, 128, 0.1); 
        color: var(--text-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        font-weight: bold;
        font-size: 16px; 
        margin-top: 10px; 
        text-align: left; 
        padding-left: 20px;
    }
    
    /* Destaque para o botão ativo (Azul Bucci) */
    .btn-active > div > button { 
        background-color: #1a3a5a !important; 
        color: white !important; 
        border: none !important;
    }

    /* Área de Conteúdo Adaptável */
    .content-area { 
        background-color: rgba(128, 128, 128, 0.05); 
        padding: 20px; 
        border-radius: 12px; 
        margin-top: 5px;
        margin-bottom: 15px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Botão WhatsApp em destaque */
    .stLinkButton > a {
        width: 100% !important; 
        background-color: #25d366 !important; 
        color: white !important;
        border-radius: 12px !important; 
        font-weight: bold !important; 
        text-align: center !important;
        padding: 1.2em 0 !important; 
        display: block !important; 
        margin-top: 20px; 
        text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE E NAVEGAÇÃO ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat_site' not in st.session_state: st.session_state.chat_site = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# --- BOTÃO 1: INÍCIO ---
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO / SOBRE NÓS"):
    st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Início":
    st.markdown("""<div class='content-area'>
        Bem-vindo à <b>Bucci Clinic</b>. Nosso foco é o atendimento humanizado em Franca/SP, 
        aliando o diagnóstico preciso ao suporte familiar indispensável. 
        <br><br>
        Acreditamos que a tecnologia deve servir para aproximar o conhecimento médico de quem mais precisa.
    </div>""", unsafe_allow_html=True)

# --- BOTÃO 2: ASSISTENTE VIRTUAL ---
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (IA)"):
    st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    st.write("Tire suas dúvidas sobre saúde mental com o Dr. Bucci AI:")
    
    # Exibe histórico do chat
    for m in st.session_state.chat_site:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])
    
    # Input de Chat moderno
    if prompt := st.chat_input("Dúvida (ex: Como ajudar alguém com depressão?)"):
        st.session_state.chat_site.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Dr. Bucci está analisando..."):
                resposta = chamar_ai_assistente(prompt)
                st.markdown(resposta)
                st.session_state.chat_site.append({"role": "assistant", "content": resposta})
    st.markdown("</div>", unsafe_allow_html=True)

# --- BOTÃO 3: WHATSAPP (AÇÃO PRINCIPAL) ---
st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 12px;'>📞 (16) 3724-0791 | Franca/SP</p>", unsafe_allow_html=True)
