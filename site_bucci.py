import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. RESPOSTAS DETALHADAS (SISTEMA DE SEGURANÇA MELHORADO) ---
# Adicionei mais variações de palavras-chave para o robô entender melhor
BASE_CONHECIMENTO = [
    {
        "chaves": ["depressão", "depressivo", "tristeza", "desânimo", "anedonia"],
        "resposta": """**Sintomas Depressivos (Visão Bucci Clinic):**
        A depressão vai além da tristeza. Os principais sinais observados clinicamente são:
        * **Anedonia:** Perda da capacidade de sentir prazer em hobbies ou no convívio social.
        * **Alterações de Energia:** Fadiga extrema, sensação de "corpo pesado" e lentidão.
        * **Sono e Apetite:** Insônia (ou sono excessivo) e perda ou ganho súbito de peso.
        * **Cognição:** Dificuldade de tomar decisões simples e sentimentos de culpa excessiva.
        * **Fator Familiar:** O isolamento afeta a dinâmica da casa, sendo essencial o suporte dos familiares no tratamento."""
    },
    {
        "chaves": ["tag", "ansiedade", "pânico", "fobia", "ansioso", "preocupação"],
        "resposta": """**Transtornos de Ansiedade (TAG e Pânico):**
        A ansiedade patológica é um estado de alerta constante do cérebro.
        * **TAG (Ansiedade Generalizada):** Preocupação excessiva com o futuro, tensão muscular e irritabilidade.
        * **Sintomas Físicos:** Taquicardia, sudorese, "nó na garganta" e dificuldade para relaxar.
        * **Pânico:** Episódios súbitos de medo intenso com sensação de morte iminente.
        * **Tratamento:** O foco é regular a neuroquímica para que o paciente recupere sua funcionalidade e pare de viver em função do medo."""
    }
]

# --- 3. MOTOR DE IA COM DIAGNÓSTICO DE ERRO ---
def chamar_ai_assistente(pergunta):
    pergunta_lower = pergunta.lower()
    
    # 1º TENTATIVA: IA Real
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            contexto = f"Você é o assistente da Bucci Clinic. Responda detalhadamente em português: {pergunta}"
            response = model.generate_content(contexto)
            if response.text:
                return response.text
        else:
            # Isso aparecerá apenas para você no console/logs
            print("AVISO: Chave GOOGLE_API_KEY não encontrada nos Secrets.")
    except Exception as e:
        print(f"ERRO NA IA: {e}")

    # 2º TENTATIVA: Busca Inteligente na Base de Conhecimento (Fallback)
    for item in BASE_CONHECIMENTO:
        for chave in item["chaves"]:
            if chave in pergunta_lower:
                return item["resposta"]
    
    # 3º TENTATIVA: Resposta Padrão Educativa
    return """Ainda não tenho uma resposta detalhada sobre este termo específico em minha base de dados rápida. 
    Contudo, na Bucci Clinic tratamos todos os aspectos da saúde mental (Infantil, Adulto e Idoso). 
    
    Poderia reformular sua pergunta ou gostaria de falar diretamente com nossa equipe de agendamento no WhatsApp?"""

# --- 4. CSS (DESIGN) ---
cor_bucci = "#1a3a5a"
cor_whatsapp = "#25d366"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .main-title {{ color: {cor_bucci}; text-align: center; font-size: 26px; font-weight: 800; margin: 0; }}
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

# --- 5. NAVEGAÇÃO ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

# --- 6. INTERFACE ---
st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# BOTÃO INÍCIO
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Bem-vindo à Bucci Clinic. Excelência no cuidado psiquiátrico com olhar sistêmico familiar.</div>", unsafe_allow_html=True)

# BOTÃO CHATBOT
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (CHAT)"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_f", clear_on_submit=True):
        u_input = st.text_input("Sua dúvida:")
        if st.form_submit_button("Enviar"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 WHATSAPP AGENDAMENTO", "https://wa.me/5516999674172")
