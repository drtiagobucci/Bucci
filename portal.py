import streamlit as st
import requests
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. MOTOR DE IA (PESQUISA PURA VIA GOOGLE GEMINI) ---
def chamar_ai_assistente(pergunta):
    # Verificação da Chave
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Erro: Chave de API não configurada nos Secrets do Streamlit."

    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # URL da API (Versão v1beta é a que melhor aceita o modelo flash atualmente)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Prompt com as diretrizes da clínica
    prompt_clinico = {
        "contents": [{
            "parts": [{
                "text": f"Você é o Dr. Tiago Bucci, psiquiatra da Bucci Family Clinic. Responda de forma detalhada, técnica e empática em português. Use listas e negritos. Nunca dê dosagens de medicamentos. Pergunta: {pergunta}"
            }]
        }]
    }

    try:
        # Chamada direta via POST
        response = requests.post(url, headers=headers, data=json.dumps(prompt_clinico), timeout=15)
        res_json = response.json()
        
        if response.status_code == 200:
            # Extração da resposta de texto
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # Mostra o erro real do Google para facilitar o diagnóstico
            detalhe_erro = res_json.get('error', {}).get('message', 'Erro desconhecido no servidor do Google.')
            return f"❌ Erro na IA: {detalhe_erro}"

    except Exception as e:
        return f"❌ Erro de Conexão: Ocorreu um problema ao falar com o servidor. ({str(e)})"

# --- 3. DESIGN CSS (ESTILO VERTICAL MOBILE-FIRST) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer { display: none; }
    .main-title { color: #1a3a5a; text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #555; font-size: 15px; margin-bottom: 25px; }
    
    /* Estilo dos Botões */
    div.stButton > button {
        width: 100% !important; border-radius: 12px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: #1a3a5a; border: none; font-weight: bold;
        font-size: 16px; margin-top: 10px; text-align: left; padding-left: 20px;
    }
    .btn-active > div > button { background-color: #1a3a5a !important; color: white !important; }

    /* Área de Conteúdo abaixo do botão */
    .content-area { 
        background-color: white; padding: 20px; border: 1px solid #eee; 
        border-radius: 0 0 12px 12px; border-top: none; margin-bottom: 15px;
    }
    
    /* Botão WhatsApp */
    .stLinkButton > a {
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 12px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; margin-top: 10px; text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE NAVEGAÇÃO ---
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
        Bem-vindo à Bucci Clinic. Atendimento humanizado em Franca/SP voltado para o acolhimento do indivíduo e da família. 
        Utilizamos tecnologia e evidências científicas para o melhor cuidado em saúde mental.
    </div>""", unsafe_allow_html=True)

# --- BOTÃO 2: ASSISTENTE VIRTUAL ---
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (PESQUISA IA)"):
    st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    
    # Histórico do Chat
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    # Campo de Pergunta
    with st.form(key="chat_ia_pura", clear_on_submit=True):
        u_input = st.text_input("Digite sua dúvida sobre saúde mental:")
        if st.form_submit_button("Consultar Inteligência Clínica"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                with st.spinner("Pesquisando na base de dados clínica..."):
                    resposta_ia = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- BOTÃO 3: WHATSAPP ---
st.link_button("💬 AGENDAR CONSULTA VIA WHATSAPP", "https://wa.me/5516999674172")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 12px;'>📞 (16) 3724-0791 | Franca/SP</p>", unsafe_allow_html=True)
