import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Psychiatry AI", layout="wide", page_icon="🧠")

# --- 1. CONEXÕES ---
try:
    API_KEY_AI = st.secrets["GOOGLE_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    genai.configure(api_key=API_KEY_AI)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- 2. CSS ADAPTÁVEL (DARK MODE & DASHBOARD) ---
cor_bucci = "#1a3a5a"
st.markdown(f"""
    <style>
    div[data-testid="stExpander"] {{ border-left: 6px solid {cor_bucci} !important; border-radius: 10px !important; background-color: rgba(128, 128, 128, 0.1) !important; margin-bottom: 15px; }}
    .stButton > button {{ width: 100% !important; border-radius: 8px !important; height: 3.5em !important; background-color: transparent !important; color: var(--text-color) !important; border: 1px solid rgba(128, 128, 128, 0.3) !important; }}
    .stButton > button:hover {{ border-color: {cor_bucci} !important; color: {cor_bucci} !important; }}
    .active-btn > div > button {{ background-color: {cor_bucci} !important; color: white !important; border: none !important; }}
    
    /* Estilo dos Cards do Dashboard */
    .dash-card {{
        padding: 30px;
        border-radius: 15px;
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        text-align: center;
        transition: 0.3s;
        cursor: pointer;
    }}
    .dash-card:hover {{ border-color: {cor_bucci}; transform: translateY(-5px); }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE APOIO ---
def calcular_idade(data_nascimento):
    if not data_nascimento: return 0
    today = date.today()
    return today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))

def formatar_data_br(data_iso):
    try:
        dt = datetime.fromisoformat(data_iso.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except: return data_iso

# --- 4. LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🔐 Bucci Clinic - Acesso Médico")
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
        if st.button("Acessar Sistema"):
            if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
                st.session_state.logado = True
                st.session_state.menu_prontuario = "Início"
                st.rerun()
    st.stop()

# --- 5. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo_bucci.jpg"):
        st.image("logo_bucci.jpg", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    opcoes = {
        "🏠 Início": "Início",
        "👤 Cadastro": "Cadastro",
        "📅 Agenda": "Agenda", 
        "📝 Atendimento": "Atendimento", 
        "📂 Histórico": "Histórico", 
        "🚪 Sair": "Sair"
    }
    
    for label, id_menu in opcoes.items():
        is_active = "active-btn" if st.session_state.menu_prontuario == id_menu else ""
        st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
        if st.button(label, key=f"btn_side_{id_menu}"):
            if id_menu == "Sair": 
                st.session_state.logado = False
                st.rerun()
            st.session_state.menu_prontuario = id_menu
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_prontuario

# --- PÁGINA: INÍCIO (DASHBOARD) ---
if menu == "Início":
    st.title(f"Bem-vindo, Dr. {st.secrets['LOGIN_USER']}")
    st.write("Selecione uma das áreas abaixo para começar:")
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        if st.button("👤 CADASTRAR PACIENTE\n\nNovo registro no sistema"):
            st.session_state.menu_prontuario = "Cadastro"; st.rerun()
    with col2:
        if st.button("📅 AGENDA CLÍNICA\n\nVer consultas do dia"):
            st.session_state.menu_prontuario = "Agenda"; st.rerun()
    with col3:
        if st.button("📝 NOVO ATENDIMENTO\n\nIniciar consulta agora"):
            st.session_state.menu_prontuario = "Atendimento"; st.rerun()
    with col4:
        if st.button("📂 HISTÓRICO COMPLETO\n\nBusca de prontuários"):
            st.session_state.menu_prontuario = "Histórico"; st.rerun()

# --- PÁGINA: CADASTRO DE PACIENTES ---
elif menu == "Cadastro":
    st.header("👤 Cadastro de Paciente")
    with st.form("form_cadastro"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        cpf = c2.text_input("CPF (Somente números)")
        
        c3, c4, c5 = st.columns([1.5, 1, 1])
        nasc = c3.date_input("Data de Nascimento", value=date(1990,1,1), format="DD/MM/YYYY")
        sexo = c4.selectbox("Sexo", ["M", "F", "Outro"])
        tel = c5.text_input("WhatsApp (DDD+Número)")
        
        endereco = st.text_area("Endereço Completo")
        
        if st.form_submit_button("💾 Salvar Cadastro"):
            if nome and cpf:
                paciente_data = {
                    "cpf": cpf, "nome": nome, "tel": tel, 
                    "idade": calcular_idade(nasc), "sexo": sexo, 
                    "nascimento": str(nasc), "endereco": endereco
                }
                supabase.table("pacientes").upsert(paciente_data).execute()
                st.success(f"Paciente {nome} cadastrado com sucesso!")
            else: st.warning("Nome e CPF são obrigatórios.")

# --- PÁGINA: ATENDIMENTO ---
elif menu == "Atendimento":
    st.header("📝 Atendimento Clínico")
    
    # Seleção de paciente simplificada
    p_cpf = st.text_input("Digite o CPF do Paciente para iniciar:")
    
    if p_cpf:
        res_p = supabase.table("pacientes").select("*").eq("cpf", p_cpf).execute()
        if res_p.data:
            p = res_p.data[0]
            st.info(f"Paciente: **{p['nome']}** | Idade: {p['idade']}a | Sexo: {p['sexo']}")
            
            # Form Atendimento
            audio = mic_recorder(start_prompt="🎙️ Gravar Sessão", stop_prompt="🛑 Transcrever", key='mic_atend')
            if audio and "last_audio" not in st.session_state:
                st.session_state.transc = genai.GenerativeModel("gemini-1.5-flash").generate_content(["Transcreva:", {"mime_type": "audio/wav", "data": audio['bytes']}]).text
                st.session_state.last_audio = True

            ana = st.text_area("1. Anamnese / Evolução", value=st.session_state.get('transc', ""), height=250)
            
            # NOVO CAMPO: HIPÓTESE DIAGNÓSTICA
            hipo = st.text_area("2. Hipótese Diagnóstica", height=100, placeholder="Ex: F32.1 - Episódio depressivo moderado")
            
            con = st.text_area("3. Conduta Terapêutica", height=150)
            
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("🚀 Validar com IA (CANMAT/APA)"):
                with st.spinner("Analisando..."):
                    prompt = f"Analise CANMAT/APA: Paciente {p['idade']}a, {p['sexo']}. Caso: {ana}. Hipótese: {hipo}. Conduta: {con}."
                    st.session_state.ia_res = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text
                st.info(st.session_state.ia_res)

            if col_btn2.button("💾 Salvar Atendimento"):
                consulta_data = {
                    "cpf": p_cpf, "anamnese": ana, 
                    "hipotese": hipo, "conduta": con, 
                    "analise_ia": st.session_state.get('ia_res', "")
                }
                supabase.table("consultas").insert(consulta_data).execute()
                st.success("✅ Consulta salva!")
                for k in ['transc', 'ia_res', 'last_audio']: 
                    if k in st.session_state: del st.session_state[k]
        else: st.warning("Paciente não encontrado. Cadastre-o primeiro.")

# --- PÁGINA: HISTÓRICO ---
elif menu == "Histórico":
    st.header("📂 Histórico e Prontuários")
    busca = st.text_input("🔍 Nome ou CPF")
    if busca:
        # Lógica de busca por Nome ou CPF
        if busca.isdigit():
            res = supabase.table("consultas").select("*, pacientes(*)").eq("cpf", busca).order("data_hora", desc=True).execute()
        else:
            res_p = supabase.table("pacientes").select("cpf").ilike("nome", f"%{busca}%").execute()
            cpfs = [item['cpf'] for item in res_p.data]
            res = supabase.table("consultas").select("*, pacientes(*)").in_("cpf", cpfs).order("data_hora", desc=True).execute()

        if res.data:
            for item in res.data:
                dt_br = formatar_data_br(item['data_hora'])
                with st.expander(f"🗓️ {dt_br} - {item['pacientes']['nome']}"):
                    st.write("**📝 Anamnese:**", item['anamnese'])
                    st.write("**🧠 Hipótese:**", item.get('hipotese', 'Não informada'))
                    st.write("**💊 Conduta:**", item['conduta'])
                    st.divider()
                    st.info(f"**Validação IA:**\n\n{item['analise_ia']}")
        else: st.info("Nenhum registro.")

# --- PÁGINA: AGENDA ---
elif menu == "Agenda":
    st.header("📅 Agenda")
    data_sel = st.date_input("Data", format="DD/MM/YYYY")
    res_ag = supabase.table("agenda").select("horario, pacientes(nome, tel)").eq("data", data_sel.strftime("%d/%m/%Y")).execute()
    if res_ag.data:
        for it in res_ag.data:
            with st.container(border=True):
                st.write(f"🕒 **{it['horario']}** - {it['pacientes']['nome']} | 📱 {it['pacientes']['tel']}")
    else: st.info("Sem consultas.")
