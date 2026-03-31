import streamlit as st
import sqlite3
import urllib.parse
import os
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Bucci Psychiatry AI - CANMAT/APA", layout="wide", page_icon="🧠")

# --- 1. SEGURANÇA: CARREGAR CHAVE SECRETA ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.sidebar.error("❌ Erro: Chave API não encontrada em .streamlit/secrets.toml")
    st.stop()

# --- 2. BANCO DE DADOS ---
def conectar(): return sqlite3.connect("clinica_bucci.db", check_same_thread=False)

def init_db():
    conn = conectar(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS pacientes (
        cpf TEXT PRIMARY KEY, nome TEXT, tel TEXT, idade INTEGER, sexo TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        cpf TEXT, data TEXT, anamnese TEXT, conduta TEXT, 
        escores_escalas TEXT, analise_ia TEXT)""")
    c.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_cpf TEXT, data TEXT, horario TEXT)")
    
    # Migração automática de colunas
    try:
        c.execute("ALTER TABLE pacientes ADD COLUMN idade INTEGER")
        c.execute("ALTER TABLE pacientes ADD COLUMN sexo TEXT")
    except: pass
    
    conn.commit(); conn.close()

init_db()

# --- 3. MOTOR DE IA: VALIDAÇÃO CANMAT + APA (ANONIMIZADO) ---
def validacao_multi_diretrizes(ana, con, p_idade, p_sexo, escores):
    prompt = f"""
    Você é um consultor psiquiátrico sênior especializado em medicina baseada em evidências.
    Analise a conduta médica comparando as diretrizes CANMAT (2016/2023) e APA (American Psychiatric Association).

    DADOS CLÍNICOS (ANONIMIZADOS):
    - Perfil: Idade {p_idade}, Sexo {p_sexo}
    - Escalas Aplicadas: {str(escores)}
    - Descrição do Caso: {ana}
    - Conduta Terapêutica Planejada: {con}

    ESTRUTURA DA RESPOSTA:
    1. **Diagnóstico e Severidade**
    2. **Validação CANMAT (Canadá)**: (Linha de tratamento e evidência)
    3. **Validação APA (EUA)**: (Concordância ou divergência)
    4. **Suporte Neuromodulação (EMTr)**: (Validação do protocolo ou indicação)
    5. **Segurança**: (Interações, riscos metabólicos ou virada maníaca)
    6. **Veredito Bucci AI**: (Consensual, Parcial ou Requer Ajustes)
    """
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_final = modelos[0] if modelos else "gemini-1.5-flash"
        model = genai.GenerativeModel(modelo_final)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na análise clínica: {e}"

def transcrever_audio_clinico(audio_bytes):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(["Transcreva este áudio médico separando 'Médico:' e 'Paciente:'.", 
                                      {"mime_type": "audio/wav", "data": audio_bytes}])
        return res.text
    except Exception as e:
        return f"Erro na transcrição: {e}"

# --- 4. ESCALAS CLÍNICAS ---
def renderizar_escalas():
    st.subheader("📊 Escalas de Rastreamento (Cálculo Automático)")
    t1, t2, t3, t4 = st.tabs(["PHQ-9 (Depressão)", "GAD-7 (Ansiedade)", "ASRS-18 (TDAH)", "SNAP-IV (TOD)"])
    res = {}
    
    with t1:
        soma = 0
        pergs = ["Interesse/Prazer", "Deprimido", "Sono", "Energia", "Apetite", "Autoestima", "Concentração", "Lentidão/Agitação", "Autodestruição"]
        cols = st.columns(3)
        for i, p in enumerate(pergs):
            val = cols[i % 3].selectbox(f"{p}", [0, 1, 2, 3], key=f"phq_{i}")
            soma += val
        res['PHQ9'] = soma
        st.metric("Total PHQ-9", soma)

    with t2:
        soma_g = 0
        pergs_g = ["Nervosismo", "Não controlar preocupação", "Preocupação diversa", "Dificuldade relaxar", "Inquietude", "Irritabilidade", "Medo"]
        cols_g = st.columns(3)
        for i, p in enumerate(pergs_g):
            val = cols_g[i % 3].selectbox(f"{p}", [0, 1, 2, 3], key=f"gad_{i}")
            soma_g += val
        res['GAD7'] = soma_g
        st.metric("Total GAD-7", soma_g)

    with t3: res['ASRS18'] = st.slider("Escore ASRS-18 (TDAH Adulto)", 0, 18, 0)
    with t4: res['TOD'] = st.slider("Escore SNAP-IV (TOD Opositor)", 0, 8, 0)
    
    return res

# --- 5. LOGIN SEGURO VIA SECRETS ---
if "logado" not in st.session_state: 
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Bucci Psychiatry AI - Acesso Restrito")
    
    # Centralizar o formulário de login
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        u_input = st.text_input("Usuário")
        p_input = st.text_input("Senha", type="password")
        
        if st.button("Acessar Sistema", use_container_width=True):
            # Tenta ler as credenciais dos segredos
            try:
                user_correto = st.secrets["LOGIN_USER"]
                pass_correto = st.secrets["LOGIN_PASSWORD"]
                
                if u_input == user_correto and p_input == pass_correto:
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("❌ Usuário ou Senha incorretos.")
            except Exception:
                st.error("⚠️ Erro: Credenciais de login não configuradas nos Secrets.")
    st.stop()

# --- 6. BARRA LATERAL (SIDEBAR) COM LOGO ---
with st.sidebar:
    # Tenta carregar imagem local, se não existir mostra ícone
    if os.path.exists("logo_bucci.jpg"):
        st.image("logo_bucci.jpg", use_container_width=True)
    else:
        st.title("🧠 Bucci Clinic AI")
    
    st.markdown("---")
    menu = st.radio("Navegação", ["📅 Agenda", "📝 Atendimento", "📂 Histórico de Pacientes", "🚪 Sair"])
    st.markdown("---")
    st.caption("v4.0 - CANMAT/APA Compliance")

# --- 7. INTERFACE PRINCIPAL ---
if menu == "📝 Atendimento":
    st.header("📝 Atendimento Clínico Especializado")
    
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        p_nome = c1.text_input("Nome do Paciente")
        p_cpf = c2.text_input("CPF")
        p_idade = c3.number_input("Idade", 0, 120)
        p_sexo = c4.selectbox("Sexo", ["M", "F"])

    st.divider()
    escores = renderizar_escalas()
    st.divider()

    col_txt, col_ia = st.columns(2)
    with col_txt:
        st.subheader("📋 Registro de Evolução")
        audio = mic_recorder(start_prompt="🎙️ Gravar Sessão", stop_prompt="🛑 Transcrever", key='mic_vfinal')
        if audio and "last_audio" not in st.session_state:
            with st.spinner("IA Transcrevendo..."):
                st.session_state.transc = transcrever_audio_clinico(audio['bytes'])
                st.session_state.last_audio = True
        
        anamnese = st.text_area("Anamnese / Exame Psíquico", value=st.session_state.get('transc', ""), height=300)
        conduta = st.text_area("Conduta Terapêutica (Prescrição/EMTr)", height=150)

    with col_ia:
        st.subheader("🧠 Suporte à Decisão (CANMAT + APA)")
        if st.button("🚀 Executar Validação Cruzada"):
            if anamnese and conduta:
                with st.spinner("Cruzando evidências mundiais..."):
                    st.session_state.ia_res = validacao_multi_diretrizes(anamnese, conduta, p_idade, p_sexo, escores)
            else: st.warning("Preencha Anamnese e Conduta.")
        
        if "ia_res" in st.session_state:
            st.info(st.session_state.ia_res)

    if st.button("💾 Finalizar e Salvar Atendimento", use_container_width=True):
        conn = conectar(); c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO pacientes (cpf, nome, idade, sexo) VALUES (?,?,?,?)", (p_cpf, p_nome, p_idade, p_sexo))
        c.execute("INSERT INTO consultas (cpf, data, anamnese, conduta, escores_escalas, analise_ia) VALUES (?,?,?,?,?,?)",
                  (p_cpf, datetime.now().strftime("%d/%m/%Y %H:%M"), anamnese, conduta, str(escores), st.session_state.get('ia_res', "")))
        conn.commit(); conn.close()
        st.success(f"Atendimento de {p_nome} salvo!")
        for k in ['transc', 'ia_res', 'last_audio']:
            if k in st.session_state: del st.session_state[k]

elif menu == "📂 Histórico de Pacientes":
    st.header("Busca de Histórico")
    cpf_busca = st.text_input("Digite o CPF")
    if cpf_busca:
        conn = conectar(); c = conn.cursor()
        c.execute("SELECT data, conduta, escores_escalas, analise_ia FROM consultas WHERE cpf=? ORDER BY id DESC", (cpf_busca,))
        for d, co, esc, ia in c.fetchall():
            with st.expander(f"Consulta: {d}"):
                st.write(f"**Escores:** {esc}")
                st.write(f"**Conduta:** {co}")
                st.info(f"**Análise IA:**\n{ia}")
        conn.close()

elif menu == "📅 Agenda":
    st.header("Agenda Clínica")
    nome = st.text_input("Nome"); cpf = st.text_input("CPF"); tel = st.text_input("WhatsApp")
    data = st.date_input("Data"); hora = st.time_input("Hora")
    if st.button("Confirmar Agendamento"):
        conn = conectar(); c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO pacientes (cpf, nome, tel) VALUES (?,?,?)", (cpf, nome, tel))
        c.execute("INSERT INTO agenda (paciente_cpf, data, horario) VALUES (?,?,?)", (cpf, data.strftime("%d/%m/%Y"), hora.strftime("%H:%M")))
        conn.commit(); conn.close(); st.success("Agendado!")

elif menu == "🚪 Sair":
    st.session_state.logado = False; st.rerun()
