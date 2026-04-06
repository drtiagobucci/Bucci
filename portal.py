import streamlit as st
import requests
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (PESQUISA VIA GEMINI-PRO - ALTA COMPATIBILIDADE) ---
def chamar_ai_assistente(pergunta):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave de API não configurada nos Secrets do Streamlit."

    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Usando o modelo gemini-pro que é o mais estável para evitar o erro 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Configuração do Prompt Clínico
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Você é o Dr. Tiago Bucci, psiquiatra da Bucci Clinic. "
                    f"Responda de forma detalhada, empática e profissional em português. "
                    f"Use listas e negritos para facilitar a leitura. "
                    f"Diretriz: Nunca forneça dosagens de remédios. "
                    f"Pergunta do paciente: {pergunta}"
                )
            }]
        }]
    }

    try:
        # Requisição direta para o servidor do Google
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
        res_json = response.json()
        
        if response.status_code == 200:
            # Caminho de extração do texto na resposta do Google
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # Captura o erro específico para diagnóstico
            msg_erro = res_json.get('error', {}).get('message', 'Erro desconhecido.')
            return f"❌ Erro do Google (Status {response.status_code}): {msg_erro}"

    except Exception as e:
        return f"❌ Falha na conexão com a IA: {str(e)}"

# --- 3. DESIGN CSS (ESTILO VERTICAL MOBILE) ---
st.markdown("""
    <style>
    /* Remove menus do Streamlit */
    [data-testid="stSidebar"], footer, header { display: none; }
    
    .main-title { color: #1a3a5a; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #555; font-size: 15px; margin-bottom: 25px; }
    
    /* Botões Verticais */
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
    
    /* Destaque para o botão da aba aberta */
    .btn-active > div > button { 
        background-color: #1a3a5a !important; 
        color: white !important; 
    }

    /* Área de Conteúdo */
    .content-area { 
        background-color: white; 
        padding: 20px; 
        border: 1px solid #eee; 
        border-radius: 0 0 12px 12px; 
        border-top: none; 
        margin-bottom: 15px;
    }
    
    /* Botão WhatsApp em Verde */
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

# --- BOTÃO: INÍCIO ---
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO / SOBRE NÓS"):
    st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Início":
    st.markdown("""<div class='content-area'>
        Bem-vindo à Bucci Clinic. Atendimento especializado em Franca/SP com foco em diagnóstico preciso e suporte sistêmico familiar. 
        Utilizamos ciência e acolhimento para o melhor cuidado em saúde mental.
    </div>""", unsafe_allow_html=True)

# --- BOTÃO: ASSISTENTE VIRTUAL ---
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (PESQUISA IA)"):
    st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    
    # Exibe as mensagens do chat
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    # Formulário de pergunta
    with st.form(key="chat_bucci_v1", clear_on_submit=True):
        u_input = st.text_input("Como posso ajudar hoje? (ex: o que é depressão?)")
        if st.form_submit_button("Consultar Inteligência Clínica"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Analisando com Inteligência Artificial..."):
                    resposta_ia = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- BOTÃO: WHATSAPP ---
st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 12px;'>📞 (16) 3724-0791 | Franca/SP</p>", unsafe_allow_html=True)
