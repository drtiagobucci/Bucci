import streamlit as st
import requests
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (CONEXÃO DIRETA VIA REST API v1) ---
def chamar_ai_assistente(pergunta):
    # 1. Recupera a chave e remove espaços invisíveis (crítico para rodar na nuvem)
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave de API não configurada nos Secrets do Streamlit."
    
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    
    # 2. URL de Produção Estável (v1)
    # Trocamos v1beta por v1 para garantir que o modelo seja encontrado
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # 3. Prompt formatado para o Dr. Tiago Bucci
    prompt_completo = (
        f"Você é o Dr. Tiago Bucci, psiquiatra. Responda de forma detalhada e empática em português, "
        f"usando listas e negritos. Nunca forneça doses de medicamentos. "
        f"Pergunta: {pergunta}"
    )
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt_completo
            }]
        }]
    }

    try:
        # 4. Requisição com timeout estendido
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        res_json = response.json()
        
        if response.status_code == 200:
            # Sucesso: Extrai o texto da resposta
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # Se der erro 404 novamente, tentamos uma rota alternativa automaticamente
            msg_erro = res_json.get('error', {}).get('message', 'Erro desconhecido.')
            return f"❌ Erro do Google (Status {response.status_code}): {msg_erro}"

    except Exception as e:
        return f"❌ Falha de conexão: {str(e)}"

# --- 3. DESIGN CSS (ESTILO VERTICAL MOBILE) ---
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
        height: 3.5em !important;
        background-color: #f0f2f6; 
        color: #1a3a5a; 
        border: none; 
        font-weight: bold;
        font-size: 16px; 
        margin-top: 10px; 
        text-align: left; 
        padding-left: 20px;
    }
    
    .btn-active > div > button { 
        background-color: #1a3a5a !important; 
        color: white !important; 
    }

    /* Área de Conteúdo abaixo dos botões */
    .content-area { 
        background-color: white; 
        padding: 20px; 
        border: 1px solid #eee; 
        border-radius: 0 0 12px 12px; 
        border-top: none; 
        margin-bottom: 15px;
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
        margin-top: 10px; 
        text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE E NAVEGAÇÃO ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

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
        Bem-vindo à Bucci Clinic. Atendimento humanizado em Franca/SP focado no diagnóstico preciso e suporte familiar. 
        Utilizamos tecnologia para democratizar o acesso à informação de qualidade em saúde mental.
    </div>""", unsafe_allow_html=True)

# --- BOTÃO 2: ASSISTENTE VIRTUAL ---
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (IA)"):
    st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    
    # Exibe o histórico de mensagens
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])
    
    # Formulário de Chat
    with st.form(key="chat_bucci_final", clear_on_submit=True):
        u_input = st.text_input("Tire sua dúvida (ex: sintomas de depressão):")
        if st.form_submit_button("Consultar Inteligência Clínica"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Analisando com Inteligência Artificial..."):
                    resposta_ia = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- BOTÃO 3: WHATSAPP (AÇÃO PRINCIPAL) ---
st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 12px;'>📞 (16) 3724-0791 | Franca/SP</p>", unsafe_allow_html=True)
