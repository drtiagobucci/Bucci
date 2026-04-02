import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Psychiatry AI - Cloud Edition", layout="wide", page_icon="🧠")

# --- 1. CONEXÕES (IA E SUPABASE) ---
try:
    # Carregar Chaves dos Secrets
    API_KEY_AI = st.secrets["GOOGLE_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    
    # Inicializar Clientes
    genai.configure(api_key=API_KEY_AI)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    st.sidebar.success("✅ Cloud & IA Conectados")
except Exception as e:
    st.sidebar.error(f"Erro de Conexão: {e}")
    st.stop()

# --- 2. MOTOR DE IA (VALIDAÇÃO CANMAT + APA) ---
def validacao_multi_diretrizes(ana, con, p_idade, p_sexo, escores):
    # Tenta carregar a chave novamente caso não tenha sido inicializada no topo
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return "❌ Erro: Chave API não encontrada nos Secrets do Streamlit."
        
    genai.configure(api_key=api_key)
    
    prompt = f"""
    Analise a conduta comparando CANMAT (2016/2023) e APA.
    DADOS: Idade {p_idade}, Sexo {p_sexo}, Escalas {escores}.
    CASO: {ana}
    CONDUTA: {con}
    """
    
    try:
        # Tenta usar o modelo Flash 1.5 que é o mais estável
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # EXIBE O ERRO REAL PARA DIAGNÓSTICO
        return f"❌ Erro Técnico da IA: {str(e)}"
        
def transcrever_audio_clinico(audio_bytes):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(["Transcreva este áudio médico separando 'Médico:' e 'Paciente:'.", 
                                      {"mime_type": "audio/wav", "data": audio_bytes}])
        return res.text
    except: return "Erro na transcrição."

# --- 3. LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🔐 Bucci Clinic - Acesso Restrito")
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar", use_container_width=True):
            if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
                st.session_state.logado = True
                st.rerun()
            else: st.error("Credenciais Inválidas")
    st.stop()

# --- 4. INTERFACE ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    st.divider()
    menu = st.radio("Navegação", ["📅 Agenda", "📝 Atendimento", "📂 Histórico", "🚪 Sair"])

# --- PÁGINA: AGENDA ---
if menu == "📅 Agenda":
    st.header("Agenda de Consultas (Nuvem)")
    
    with st.expander("➕ Novo Agendamento"):
        c_nome = st.text_input("Nome")
        c_cpf = st.text_input("CPF")
        c_tel = st.text_input("WhatsApp")
        c_data = st.date_input("Data")
        c_hora = st.time_input("Hora")
        if st.button("Confirmar Agendamento"):
            # Salva o paciente e depois agenda
            paciente_min = {"cpf": c_cpf, "nome": c_nome, "tel": c_tel}
            supabase.table("pacientes").upsert(paciente_min).execute()
            
            agendamento = {"paciente_cpf": c_cpf, "data": c_data.strftime("%d/%m/%Y"), "horario": c_hora.strftime("%H:%M")}
            supabase.table("agenda").insert(agendamento).execute()
            st.success("Agendado com sucesso!")

    st.subheader("Próximas Consultas")
    data_filtro = st.date_input("Filtrar Data", value=datetime.now())
    res_agenda = supabase.table("agenda").select("horario, pacientes(nome, tel)").eq("data", data_filtro.strftime("%d/%m/%Y")).execute()
    
    if res_agenda.data:
        for item in res_agenda.data:
            col_h, col_n, col_w = st.columns([1, 3, 2])
            col_h.write(f"🕒 {item['horario']}")
            col_n.write(item['pacientes']['nome'])
            tel = item['pacientes']['tel']
            col_w.markdown(f"[📱 WhatsApp](https://wa.me/{tel})")
    else: st.info("Nenhuma consulta para esta data.")

# --- PÁGINA: ATENDIMENTO ---
elif menu == "📝 Atendimento":
    st.header("Prontuário com IA (CANMAT/APA)")
    
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        p_nome = c1.text_input("Paciente")
        p_cpf = c2.text_input("CPF")
        p_idade = c3.number_input("Idade", 0, 120)
        p_sexo = c4.selectbox("Sexo", ["M", "F"])

    st.divider()
    # Escalas Simplificadas para o exemplo
    st.subheader("📊 Escalas Clínicas")
    col_e1, col_e2 = st.columns(2)
    phq = col_e1.slider("PHQ-9 (Depressão)", 0, 27, 0)
    gad = col_e2.slider("GAD-7 (Ansiedade)", 0, 21, 0)
    escores = {"PHQ9": phq, "GAD7": gad}

    st.divider()
    col_txt, col_ia = st.columns(2)
    
    with col_txt:
        audio = mic_recorder(start_prompt="🎙️ Gravar Sessão", stop_prompt="🛑 Transcrever", key='mic')
        if audio and "last_audio" not in st.session_state:
            st.session_state.transc = transcrever_audio_clinico(audio['bytes'])
            st.session_state.last_audio = True
        
        anamnese = st.text_area("Anamnese / Exame Psíquico", value=st.session_state.get('transc', ""), height=300)
        conduta = st.text_area("Conduta Terapêutica", height=150)

    with col_ia:
        if st.button("🚀 Validar com IA (CANMAT + APA)"):
            st.session_state.ia_res = validacao_multi_diretrizes(anamnese, conduta, p_idade, p_sexo, escores)
        if "ia_res" in st.session_state: st.info(st.session_state.ia_res)

    if st.button("💾 Finalizar e Salvar na Nuvem", use_container_width=True):
        try:
            # 1. Salvar Paciente
            paciente_data = {"cpf": p_cpf, "nome": p_nome, "idade": p_idade, "sexo": p_sexo}
            supabase.table("pacientes").upsert(paciente_data).execute()
            # 2. Salvar Consulta
            consulta_data = {"cpf": p_cpf, "anamnese": anamnese, "conduta": conduta, "escores": str(escores), "analise_ia": st.session_state.get('ia_res', "")}
            supabase.table("consultas").insert(consulta_data).execute()
            st.success("Prontuário salvo permanentemente!")
            for k in ['transc', 'ia_res', 'last_audio']: 
                if k in st.session_state: del st.session_state[k]
        except Exception as e: st.error(f"Erro ao salvar: {e}")

# --- PÁGINA: HISTÓRICO ---
elif menu == "📂 Histórico":
    st.header("Busca no Histórico")
    cpf_busca = st.text_input("CPF do Paciente")
    if cpf_busca:
        res = supabase.table("consultas").select("*").eq("cpf", cpf_busca).order("data_hora", desc=True).execute()
        if res.data:
            for item in res.data:
                with st.expander(f"Consulta em {item['data_hora']}"):
                    st.write(f"**Escores:** {item['escores']}")
                    st.write(f"**Conduta:** {item['conduta']}")
                    st.info(f"**Validação IA:**\n{item['analise_ia']}")
        else: st.warning("Paciente não encontrado.")

elif menu == "🚪 Sair":
    st.session_state.logado = False; st.rerun()
