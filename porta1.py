import streamlit as st

st.set_page_config(page_title="Bucci Clinic - Temas", layout="wide")

# --- CSS PARA DESTACAR OS NEGRETOS E ESTILIZAR CARDS ---
st.markdown("""
    <style>
    /* Estilo dos Cards (Expanders) */
    div[data-testid="stExpander"] {
        background-color: white !important;
        border-radius: 15px !important;
        border-left: 12px solid #1a3a5a !important;
        box-shadow: 5px 5px 20px rgba(0,0,0,0.08) !important;
        margin-bottom: 25px !important;
        padding: 10px !important;
    }
    
    /* Título do Card */
    div[data-testid="stExpander"] summary p {
        font-size: 24px !important; 
        font-weight: 800 !important;
        color: #1a3a5a !important;
    }

    /* Estilo para o Texto em Negrito (strong) */
    strong {
        color: #1a3a5a !important;
        font-size: 102%;
        background-color: #f0f4f8;
        padding: 1px 5px;
        border-radius: 4px;
        font-weight: 700;
    }

    /* Ajuste de parágrafos e listas dentro dos cards */
    .stMarkdown p, .stMarkdown li {
        font-size: 18px !important;
        line-height: 1.7 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (LOGO E NAVEGAÇÃO) ---
with st.sidebar:
    try:
        st.image("logo_bucci.jpg", use_container_width=True)
    except:
        st.warning("Arquivo 'logo_bucci.jpg' não encontrado na pasta.")
    
    st.markdown("---") # Linha divisória
    secao = st.radio("Navegação", ["Início", "Temas Psiquiátricos"])

# --- CONTEÚDO ---
if secao == "Início":
    st.title("Bem-vindo à Clinica Bucci Saúde Mental da Família")
    st.subheader("Excelência em Saúde Mental e Cuidado Familiar.")
    st.write("Atendimento humanizado voltados para o acolhimento do inidividuo e da família. Nos quadros emocionais toda a família sofre.")
    st.write("Agende uma avaliaçao, nós podemos te ajudar.")
    st.info("📍 Localização: Rua Saldanha Marinho, 2615 - Franca/SP | 📞 Contato: (16) 3724-0791 || (16) 99967-4172")


elif secao == "Temas Psiquiátricos":
    st.title("📚 Temas em Psiquiatria")
    
    # CARD 1 - SAÚDE MENTAL NA FAMÍLIA
    with st.expander("👨‍👩‍👧‍ SAÚDE MENTAL NA FAMÍLIA"):
        st.markdown("""
        ### Família o Elo que Sustenta o Cuidado
        Estudos mostram que a família é o fator preditivo mais forte para o sucesso do tratamento,
        dessa forma a participação familiar, com apoio e compreensão do quadro emocional, é um 
        fator decisivo para a recuperação plena do paciente.
        
        * **Rede de Apoio:** **Acolhimento substitui o julgamento**, assim ouvir, entender e ajudar
             contribui para uma recuperação rápida e duradora, enquanto que a 
             crítica e a desvalorização dos sentimentos pioram o quadro emocional.
        * **Ambiente:** **Validação emocional** atua como protetor biológico.
        * **Cuidar de quem cuida:** O suporte ao cuidador evita a sobrecarga do sistema familiar,
            pois quem cuida também sofre e também adoece.
        """)

    # CARD 2 - TRANSTORNOS DE ANSIEDADE
    with st.expander("🧠 TRANSTORNOS DE ANSIEDADE"):
        st.markdown("""
        ### Além do Medo Comum
        A ansiedade patológica desregula o **sistema de alerta do cérebro**, dessa forma o paciente
        evolui com sentimentos de **insegurança, ansiedade e medos** sem um fator desencadeante claro.
        
        * **Transtornos:** **TAG, Pânico e Fobias**, são exemples de diagnósticos que possuem como centro a ansiedade de forma a gerar um sofrimento para o individuo.
        * **Físico:** **Insônia, taquicardia, dificuldade de concentração e vertigem** são sinais de sobrecarga neuroquímica.
        * **Tratamento:** **Ajuste medicamentoso individual**, respeitando particularidades e comorbidades. O medicamento existe para possibilitar ao paciente uma **vida normal**.
        """)

    # CARD 3 - TRANSTORNOS DE HUMOR E BIPOLARIDADE
    with st.expander("☁️ DEPRESSÃO E TRANSTORNOS DO HUMOR"):
        st.markdown("""
        ### Entendendo a Vitalidade e o Humor
        A depressão vai além da tristeza; é uma **alteração na capacidade de sentir prazer e uma falta de energia**.
        * **Sintomas:** Anedonia, tristeza, fadiga crônica e alterações de sono e de apetite, irritabilidade, dificuldade de concentração e memorização, indecisão, falta de iniciativa, isolamento social, são caracteristicas que podem estar presentes em um quadro depressivo.
        * **Transtorno Bipolar:** É muito mais que somente uma oscilações recorrente, é uma quadro emocional caracterizado por dois polos, um com sintomas depressivos e outro o oposto com sintomas de euforia, aumento de energia, diminuição da necessidade de sono, irritabilidade, impulsividade, gastos excessivos, comportamentos de riscos, prolixidade, o individuo muda seu jeito de ser.
        * **Cuidado:** Requer abordagem integrada entre biologia e psicoterapia, é entendendo o individuo como um todo e não somente como uma doença que podemos ajudar a cada um a alcançar a plena recuperação, validando suas queixas e sofrimento e respeitando suas crenças e seu modo de viver.
        """)

elif secao == "Sobre a Clínica":
    st.title("Sobre a Clínica Bucci")
    st.write("Focamos no atendimento sistêmico, unindo neurociência e humanização.")
    st.info("📍 Localização: Rua Saldanha Marinho, 2615 - Franca/SP | 📞 Contato: (16) 3724-0791 || (16) 99967-4172")