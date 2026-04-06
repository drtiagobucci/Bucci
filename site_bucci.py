import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Bucci Clinic", layout="centered", page_icon="🧠")

# --- 2. FUNÇÃO DE IA COM DIAGNÓSTICO ATIVO ---
def chamar_ai_assistente(pergunta):
    # Verificação de Segurança da Chave
    if "GOOGLE_API_KEY" not in st.secrets:
        return "❌ ERRO: Chave 'GOOGLE_API_KEY' não encontrada nos Secrets do Streamlit. Verifique as configurações."

    try:
        # Configura e tenta chamada
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Você é o Dr. Tiago Bucci, psiquiatra. 
        Dê uma resposta completa, técnica e acolhedora sobre: {pergunta}.
        Use listas, negritos e explique a importância da família no tratamento.
        """
        
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
            
    except Exception as e:
        # Se a IA falhar, vamos tentar a base local detalhada abaixo:
        pass

    # --- 3. BASE LOCAL DETALHADA (Se a IA falhar, o paciente recebe isso) ---
    pergunta_min = pergunta.lower()
    
    if "depress" in pergunta_min:
        return """
        ### 🕯️ Depressão: Além da Tristeza Passageira
        A depressão é uma condição neurobiológica que afeta a vitalidade. Na Bucci Clinic, observamos os seguintes sinais detalhados:

        **1. Sintomas Emocionais e Cognitivos:**
        *   **Anedonia:** Perda total ou parcial de sentir prazer em atividades (hobbies, comida, sexo).
        *   **Sentimentos de Inutilidade:** Culpa excessiva por eventos passados.
        *   **Dificuldade de Decisão:** Coisas simples como escolher uma roupa tornam-se exaustivas.

        **2. Sintomas Físicos (Biológicos):**
        *   **Alteração do Sono:** Insônia terminal (acordar de madrugada e não dormir mais) ou hipersonia.
        *   **Fadiga Crônica:** Uma sensação de "corpo pesado" mesmo sem esforço físico.
        *   **Psicomotricidade:** Lentidão na fala e nos movimentos.

        **3. O Papel da Família:**
        O suporte familiar é o **principal protetor** contra recaídas. O acolhimento substitui a cobrança ("reaja", "saia dessa"), criando um ambiente neuroprotetores.
        
        *Para um diagnóstico preciso, é fundamental uma avaliação clínica detalhada.*
        """

    if "tag" in pergunta_min or "ansiedade" in pergunta_min:
        return """
        ### ⚖️ Transtorno de Ansiedade Generalizada (TAG)
        A ansiedade patológica é como um "alarme quebrado" que nunca desliga.

        **Principais Sinais Clínicos:**
        *   **Preocupação Incontrolável:** A mente salta de um problema para outro sem solução.
        *   **Tensão Muscular:** Dores nos ombros, pescoço e mandíbula (bruxismo).
        *   **Sintomas Autonômicos:** Taquicardia, sudorese, "nó na garganta" e irritabilidade fácil.
        *   **Impacto no Sono:** Dificuldade em "desligar o pensamento" para adormecer.

        **Tratamento na Bucci Clinic:**
        Focamos em devolver a funcionalidade. O paciente aprende a diferenciar o medo real da ansiedade antecipatória, muitas vezes com auxílio de regulação neuroquímica.
        """

    return "Não consegui processar essa dúvida específica com detalhes agora. Por favor, tente perguntar de outra forma ou fale conosco pelo WhatsApp."

# --- 4. CSS DESIGN ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"], footer {{ display: none; }}
    .main-title {{ color: #1a3a5a; text-align: center; font-size: 28px; font-weight: 800; margin: 0; }}
    .sub-title {{ text-align: center; color: #555; font-size: 15px; margin-bottom: 20px; }}
    div.stButton > button {{
        width: 100% !important; border-radius: 10px !important; height: 3.5em !important;
        background-color: #f0f2f6; color: #1a3a5a; border: none; font-weight: bold; text-align: left; padding-left: 20px;
    }}
    .btn-active > div > button {{ background-color: #1a3a5a !important; color: white !important; }}
    .content-area {{ background-color: white; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #eee; border-top: none; }}
    .stLinkButton > a {{
        width: 100% !important; background-color: #25d366 !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important; text-align: center !important;
        padding: 1em 0 !important; display: block !important; text-decoration: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO ---
if 'aba' not in st.session_state: st.session_state.aba = "Início"
if 'chat' not in st.session_state: st.session_state.chat = []

st.markdown("<h1 class='main-title'>BUCCI CLINIC</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Psiquiatria e Cuidado Familiar</p>", unsafe_allow_html=True)

# BOTÃO INÍCIO
is_act = "btn-active" if st.session_state.aba == "Início" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🏠 INÍCIO"): st.session_state.aba = "Início"
st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.aba == "Início":
    st.markdown("<div class='content-area'>Atendimento especializado em Franca/SP.</div>", unsafe_allow_html=True)

# BOTÃO CHATBOT
is_act = "btn-active" if st.session_state.aba == "Chat" else ""
st.markdown(f'<div class="{is_act}">', unsafe_allow_html=True)
if st.button("🤖 ASSISTENTE VIRTUAL (CHAT)"): st.session_state.aba = "Chat"
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.aba == "Chat":
    st.markdown("<div class='content-area'>", unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    with st.form(key="chat_final", clear_on_submit=True):
        u_input = st.text_input("Ex: Quais os sintomas de depressão?")
        if st.form_submit_button("Consultar Inteligência Clínica"):
            if u_input:
                st.session_state.chat.append({"role": "user", "content": u_input})
                res = chamar_ai_assistente(u_input)
                st.session_state.chat.append({"role": "assistant", "content": res})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.link_button("💬 AGENDAR VIA WHATSAPP", "https://wa.me/5516999674172")
