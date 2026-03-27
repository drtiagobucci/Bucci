import streamlit as st

st.set_page_config(page_title="Bucci Clinic - Temas", layout="wide")

# --- CONTROLE DE NAVEGAÇÃO ---
if 'pagina_active' not in st.session_state:
    st.session_state.pagina_active = "Início"

def mudar_pagina(nome):
    st.session_state.pagina_active = nome

# --- CSS ADAPTÁVEL COM CORREÇÃO DE CONTRASTE NO DARK MODE ---
cor_primaria = "#1a3a5a" # Azul da logo

st.markdown(f"""
    <style>
    /* 1. Cards Adaptáveis */
    div[data-testid="stExpander"] {{
        background-color: rgba(128, 128, 128, 0.08) !important;
        border-radius: 15px !important;
        border-left: 12px solid {cor_primaria} !important;
        margin-bottom: 25px !important;
    }}
    
    div[data-testid="stExpander"] summary p {{
        font-size: 22px !important; 
        font-weight: 700 !important;
    }}

    /* 2. AJUSTE DOS NEGRITOS (Contraste Inteligente) */
    strong {{
        /* No Light Mode usa o azul, no Dark Mode o navegador ajusta o brilho se usarmos filtros */
        color: #3d7fb9 !important; /* Um azul um pouco mais vivo para brilhar no Dark e aparecer no Light */
        background-color: rgba(61, 127, 185, 0.15); 
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 700;
    }}

    /* 3. Estilo dos Botões da Sidebar */
    .stButton > button {{
        width: 100% !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        font-weight: 600 !important;
        border: 2px solid {cor_primaria} !important;
    }}

    /* Cores dos Botões baseadas no estado */
    button[key="btn_inicio"] {{
        background-color: {"#1a3a5a" if st.session_state.pagina_active == "Início" else "transparent"} !important;
        color: {"white" if st.session_state.pagina_active == "Início" else "inherit"} !important;
    }}
    
    button[key="btn_temas"] {{
        background-color: {"#1a3a5a" if st.session_state.pagina_active == "Temas Psiquiátricos" else "transparent"} !important;
        color: {"white" if st.session_state.pagina_active == "Temas Psiquiátricos" else "inherit"} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    try:
        st.image("logo_bucci.jpg", use_container_width=True)
    except:
        st.warning("Logo não encontrado.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.button("🏠 INÍCIO", key="btn_inicio", on_click=mudar_pagina, args=("Início",))
    st.button("📑 TEMAS CLÍNICOS", key="btn_temas", on_click=mudar_pagina, args=("Temas Psiquiátricos",))

# --- CONTEÚDO (TEXTOS ORIGINAIS MANTIDOS) ---
secao = st.session_state.pagina_active

if secao == "Início":
    st.title("Bem-vindo à Bucci Family Psychiatric Clinic")
    st.subheader("Excelência em Saúde Mental e Cuidado Familiar.")
    st.write("Atendimento humanizado voltados para o acolhimento do inidividuo e da família. Nos quadros emocionais toda a família sofre.")
    st.write("Agende uma avaliação, nós podemos te ajudar.")
    st.info("📍 Localização: Rua Saldanha Marinho, 2615 - Franca/SP | 📞 Contato: (16) 3724-0791 || (16) 99967-4172")

elif secao == "Temas Psiquiátricos":
    st.title("Conhecimento e Cuidado")
    
    with st.expander("👥 SAÚDE MENTAL NA FAMÍLIA", expanded=False):
        st.markdown("""
        ### Família o Elo que Sustenta o Cuidado
        Estudos mostram que a família é o fator preditivo mais forte para o sucesso do tratamento,
        dessa forma a participação familiar, com apoio e compreensão do quadro emocional, é um 
        fator decisivo para a recuperação plena do paciente.
        
        * **Rede de Apoio:** Acolhimento substitui o julgamento, assim ouvir, entender e ajudar
             contribui para uma recuperação rápida e duradora, enquanto que a 
             crítica e a desvalorização dos sentimentos pioram o quadro emocional.
        * **Ambiente:** Validação emocional atua como protetor biológico e psicológico.
        * **Cuidar de quem cuida:** O suporte ao cuidador evita a sobrecarga do sistema familiar,
            pois quem cuida também sofre e também adoece.
        """)

    with st.expander("🧸 PSIQUIATRIA INFANTIL", expanded=False):
        st.markdown("""
        ### O Desenvolvimento e a Saúde Mental na Infância
        A infância é uma fase crítica de desenvolvimento neurobiológico e emocional. Identificar precocemente sinais de sofrimento é fundamental para garantir um crescimento saudável.
        
        * **Sinais de Alerta:** Mudanças bruscas no comportamento, dificuldades escolares, agressividade excessiva ou isolamento social podem indicar a necessidade de uma avaliação.
        * **Transtornos Comuns:** O diagnóstico e manejo de quadros como **TDAH, TEA (Autismo) e Transtornos de Aprendizado** exigem uma abordagem multidisciplinar e acolhedora.
        * **Papel dos Pais:** O suporte familiar e a orientação parental são os pilares que sustentam a evolução terapêutica da criança.
        """)

    with st.expander("⚖️ TRANSTORNOS DE ANSIEDADE"):
        st.markdown("""
        ### Além do Medo Comum
        A ansiedade patológica desregula o sistema de alerta do cérebro, dessa forma o paciente
        evolui com sentimentos de insegurança, ansiedade e medos sem um fator desencadeante claro.
        
        * **Transtornos:** TAG, Pânico e Fobias, são quadros diagnósticos que possuem como centro a ansiedade.
        * **Físico:** Insônia, taquicardia, dificuldade de concentração e vertigem são sinais de sobrecarga neuroquímica.
        * **Tratamento:** Ajuste medicamentoso individual, respeitando particularidades e comorbidades. O medicamento existe para possibilitar ao paciente uma **vida normal**.
        """)

    with st.expander("🕯️ DEPRESSÃO E TRANSTORNO BIPOLAR"):
        st.markdown("""
        ### Entendendo a Vitalidade e o Humor
        A depressão vai além da tristeza; é uma **alteração na capacidade de sentir prazer e uma falta de energia**.
        * **Sintomas:** Anedonia, tristeza, fadiga crônica e alterações de sono e de apetite, irritabilidade, dificuldade de concentração e memorização, indecisão, falta de iniciativa, isolamento social, são caracteristicas que podem estar presentes em um quadro depressivo.
        * **Transtorno Bipolar:** É muito mais que somente oscilações recorrentes de humor, é uma quadro emocional caracterizado por dois polos, um com sintomas depressivos e outro o oposto com sintomas de euforia, aumento de energia, diminuição da necessidade de sono, irritabilidade, impulsividade, gastos excessivos, comportamentos de riscos, prolixidade, o individuo muda seu jeito de ser.
        * **Cuidado:** Requer abordagem integrada entre biologia e psicoterapia, é entendendo o individuo como um todo e não somente como uma doença que podemos ajudar a cada um a alcançar a plena recuperação, validando suas queixas e sofrimento e respeitando suas crenças e seu modo de viver.
        """)