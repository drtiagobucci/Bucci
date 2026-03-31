import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Clinic - Temas e Cuidado", layout="wide", page_icon="🧠")

# --- 1. CONTEÚDO GLOBAL (Temas da Clínica) ---
TEMAS_CLINICOS = {
    "👥 SAÚDE MENTAL NA FAMÍLIA": """
        ### Família: O Elo que Sustenta o Cuidado
        A família é o fator preditivo mais forte para o sucesso do tratamento. A participação familiar, com apoio e compreensão, é decisiva.
        * **Rede de Apoio:** Acolhimento substitui o julgamento. Ouvir e entender contribui para uma recuperação rápida.
        * **Ambiente:** A validação emocional atua como um protetor neurobiológico e psicológico.
        * **Cuidar de quem cuida:** O suporte ao cuidador evita a sobrecarga; quem cuida também adoece e precisa de suporte.
    """,
    "🧸 PSIQUIATRIA INFANTIL": """
        ### Desenvolvimento e Saúde Mental na Infância
        A infância é uma fase crítica de desenvolvimento neurobiológico. Identificar sinais de sofrimento precocemente garante um crescimento saudável.
        * **Sinais de Alerta:** Mudanças bruscas de comportamento, isolamento social, e quedas no rendimento escolar.
        * **Transtornos Comuns:** Abordagem multidisciplinar para TDAH, TEA (Autismo) e Transtornos de Aprendizado.
        * **Papel dos Pais:** Pais bem orientados são o principal pilar que sustenta a evolução terapêutica da criança.
    """,
    "⚖️ TRANSTORNOS DE ANSIEDADE": """
        ### Além do Medo Comum
        A ansiedade patológica desregula o sistema de alerta do cérebro, gerando insegurança e medos sem fator desencadeante claro.
        * **Quadros Comuns:** TAG, Pânico e Fobias têm a ansiedade como núcleo do sofrimento.
        * **Sintomas Físicos:** Insônia, taquicardia, vertigem e dificuldade de concentração são sinais de sobrecarga neuroquímica.
        * **Tratamento:** O objetivo da medicação e terapia é possibilitar ao paciente uma **vida normal e funcional**.
    """,
    "🕯️ DEPRESSÃO E TRANSTORNO BIPOLAR": """
        ### Vitalidade e Regulação do Humor
        A depressão vai muito além da tristeza; é uma alteração na vitalidade e na capacidade de sentir prazer (anedonia).
        * **Depressão:** Fadiga crônica, alterações de sono/apetite, irritabilidade e isolamento social.
        * **Transtorno Bipolar:** Alternância entre polos depressivos e episódios de euforia (mania/hipomania), caracterizados por aumento de energia, impulsividade e gastos excessivos.
        * **Cuidado Integrado:** Tratamos o indivíduo como um todo, respeitando suas crenças e validando seu sofrimento.
    """,
    "🧠 PSICOSES": """
        ### Perda do Contato com a Realidade
        As psicoses caracterizam-se pela dificuldade em discernir o que é realidade e o que é imaginação ou delírio.
        * **Esquizofrenia:** Principal doença do grupo, exigindo tratamento contínuo para prevenir a deterioração cognitiva.
        * **Sintomas:** Alucinações (ouvir vozes ou ver vultos) e Delírios (crenças irreais mas inabaláveis).
        * **Urgência:** O diagnóstico e o início do tratamento medicamentoso precoce são cruciais para a proteção do sistema nervoso.
    """
}

# --- 2. MOTOR DE IA (ASSISTENTE VIRTUAL) ---
def chamar_ai_assistente(pergunta):
    try:
        # Carrega a chave dos Secrets (Certifique-se de atualizar se a antiga vazou!)
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # Autodescoberta de modelo
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_final = modelos[0] if modelos else "gemini-1.5-flash"
        model = genai.GenerativeModel(modelo_final)
        
        # Contexto Educativo
        contexto = f"""
        Você é o Assistente Virtual da Bucci Family Psychiatric Clinic.
        Sua missão é educar pacientes sobre saúde mental usando estes temas como base: {list(TEMAS_CLINICOS.keys())}.
        
        DIRETRIZES:
        1. Seja acolhedor, empático e profissional.
        2. Nunca dê diagnósticos nem sugira doses de remédios.
        3. Sempre termine reforçando que o diagnóstico exige consulta médica na Bucci Clinic.
        
        Pergunta: {pergunta}
        """
        response = model.generate_content(contexto)
        return response.text
    except Exception as e:
        return f"Desculpe, tive um problema técnico. Por favor, tente novamente. (Erro: {e})"

# --- 3. CSS PERSONALIZADO (AZUL BUCCI) ---
cor_bucci = "#1a3a5a"

st.markdown(f"""
    <style>
    /* Estilo dos Expanders */
    div[data-testid="stExpander"] {{
        border-left: 6px solid {cor_bucci} !important;
        border-radius: 10px !important;
        background-color: #f8f9fa !important;
        margin-bottom: 15px;
    }}
    
    /* Botões da Sidebar */
    .stButton > button {{
        width: 100% !important; border-radius: 5px !important; height: 3.5em !important;
        background-color: transparent; color: #333; border: 1px solid #ddd;
    }}
    
    /* Hover e Seleção Azul */
    .stButton > button:hover {{ border-color: {cor_bucci} !important; color: {cor_bucci} !important; }}
    .active-btn > div > button {{
        background-color: {cor_bucci} !important; color: white !important; border: none !important;
    }}

    /* Estilo do Botão de Link (Prontuário) */
    .stLinkButton > a {{
        width: 100% !important; background-color: {cor_bucci} !important; color: white !important;
        border-radius: 5px !important; text-align: center !important; font-weight: bold !important;
        text-decoration: none !important; display: inline-block !important; padding: 0.8em 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONTROLE DE NAVEGAÇÃO ---
if 'pagina_active' not in st.session_state:
    st.session_state.pagina_active = "Início"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def mudar_pagina(nome):
    st.session_state.pagina_active = nome

# --- 5. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo_bucci.jpg"):
        st.image("logo_bucci.jpg", use_container_width=True)
    else:
        st.title("Bucci Clinic")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navegação com Destaque Azul
    st.markdown("### 🌐 Navegação")
    btns = {"🏠 INÍCIO": "Início", "📑 TEMAS": "Temas", "🤖 ASSISTENTE": "Assistente"}
    for label, pg in btns.items():
        is_active = "active-btn" if st.session_state.pagina_active == pg else ""
        st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
        if st.button(label, key=f"btn_{pg}"):
            mudar_pagina(pg)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # ÁREA DO MÉDICO (LINK PARA O PRONTUÁRIO)
    st.markdown("### 🔐 Acesso Médico")
    st.link_button("📂 PRONTUÁRIO ELETRÔNICO", "https://tiagobucci.streamlit.app/")

    st.divider()
    st.caption("📞 (16) 3724-0791 | (16) 99967-4172")
    st.caption("📍 Franca/SP")

# --- 6. CONTEÚDO DAS PÁGINAS ---

if st.session_state.pagina_active == "Início":
    st.title("Bucci Family Psychiatric Clinic")
    st.subheader("Excelência em Saúde Mental e Cuidado Familiar.")
    
    col_msg, col_contato = st.columns([2, 1])
    with col_msg:
        st.write("""
        Atendimento humanizado voltado para o acolhimento do indivíduo e da família. 
        Entendemos que nos quadros emocionais, o sofrimento nunca é isolado; ele reverbera em todo o sistema familiar. 
        Nossa missão é oferecer acolhimento, diagnóstico preciso e tratamento baseado nas melhores evidências científicas mundiais.
        """)
        st.success("✨ **Diferencial:** Tratamento integrado entre biologia, psicoterapia e suporte familiar.")
    
    with col_contato:
        st.markdown("### Agendamentos")
        st.link_button("💬 WhatsApp de Agendamento", "https://wa.me/5516999674172")
        st.write("📞 Telefone Fixo: (16) 3724-0791")

elif st.session_state.pagina_active == "Temas":
    st.title("Conhecimento e Cuidado")
    st.write("Selecione um tema para expandir as informações clínicas:")
    
    for titulo, conteudo in TEMAS_CLINICOS.items():
        with st.expander(titulo):
            st.markdown(conteudo)

elif st.session_state.pagina_active == "Assistente":
    st.title("🤖 Assistente Virtual Bucci")
    st.info("Tire suas dúvidas sobre temas de saúde mental. Este assistente é apenas informativo.")

    # Exibir histórico de chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada do usuário
    if prompt := st.chat_input("Ex: Quais os sinais de ansiedade patológica?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conhecimento clínica..."):
                resposta = chamar_ai_assistente(prompt)
                st.markdown(resposta)
                st.session_state.chat_history.append({"role": "assistant", "content": resposta})