import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Psychiatry AI - Cloud Edition", layout="wide", page_icon="🧠")

# --- 1. CONEXÕES (IA E SUPABASE) ---
try:
    API_KEY_AI = st.secrets["GOOGLE_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    genai.configure(api_key=API_KEY_AI)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- 2. CSS PERSONALIZADO (IGUAL AO SITE) ---
cor_bucci = "#1a3a5a"
st.markdown(f"""
    <style>
    div[data-testid="stExpander"] {{ border-left: 6px solid {cor_bucci} !important; border-radius: 10px !important; background-color: #f8f9fa !important; }}
    .stButton > button {{ width: 100% !important; border-radius: 5px !important; height: 3em !important; background-color: transparent; color: #333; border: 1px solid #ddd; }}
    .stButton > button:hover {{ border-color: {cor_bucci} !important; color: {cor_bucci} !important; }}
    .active-btn > div > button {{ background-color: {cor_bucci} !important; color: white !important; border: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE APOIO ---
def calcular_idade(data_nascimento):
    today = date.today()
    return today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))

def formatar_data_br(data_iso):
    # Converte 2023-10-25T14:30... para 25/10/2023 14:30
    try:
        dt = datetime.fromisoformat(data_iso.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except: return data_iso

def validacao_multi_diretrizes(ana, con, idade, sexo, escores):
    try:
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_final = modelos_disponiveis[0] if modelos_disponiveis else "gemini-1.5-flash"
        model = genai.GenerativeModel(modelo_final)
        prompt = f"Analise CANMAT/APA: Idade {idade}, Sexo {sexo}, Escalas {escores}. Caso: {ana}. Conduta: {con}."
        return model.generate_content(prompt).text
    except: return "Erro na análise da IA."

# --- 4. LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🔐 Bucci Clinic - Acesso Restrito")
    u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
    if st.button("Acessar"):
        if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
            st.session_state.logado = True
            st.rerun()
    st.stop()

# --- 5. BARRA LATERAL (VISUAL DO SITE) ---
with st.sidebar:
    if os.path.exists("logo_bucci.jpg"):
        st.image("logo_bucci.jpg", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'menu_prontuario' not in st.session_state: st.session_state.menu_prontuario = "Atendimento"

    opcoes = {"📅 Agenda": "Agenda", "📝 Atendimento": "Atendimento", "📂 Histórico": "Histórico", "🚪 Sair": "Sair"}
    for label, id_menu in opcoes.items():
        is_active = "active-btn" if st.session_state.menu_prontuario == id_menu else ""
        st.markdown(f'<div class="{is_active}">', unsafe_allow_html=True)
        if st.button(label, key=f"btn_{id_menu}"):
            if id_menu == "Sair": 
                st.session_state.logado = False
                st.rerun()
            st.session_state.menu_prontuario = id_menu
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_prontuario

# --- PÁGINA: ATENDIMENTO ---
if menu == "Atendimento":
    st.header("📝 Novo Atendimento")
    
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 0.8, 1])
        p_nome = c1.text_input("Nome Completo")
        p_cpf = c2.text_input("CPF")
        p_nasc = c3.date_input("Data de Nascimento", value=date(1990, 1, 1), format="DD/MM/YYYY")
        idade_atual = calcular_idade(p_nasc)
        c4.metric("Idade", f"{idade_atual}a")
        p_sexo = c5.selectbox("Sexo", ["M", "F"])

    st.divider()
    col_txt, col_ia = st.columns(2)
    
    with col_txt:
        audio = mic_recorder(start_prompt="🎙️ Gravar Sessão", stop_prompt="🛑 Transcrever", key='mic')
        if audio and "last_audio" not in st.session_state:
            st.session_state.transc = genai.GenerativeModel("gemini-1.5-flash").generate_content(["Transcreva:", {"mime_type": "audio/wav", "data": audio['bytes']}]).text
            st.session_state.last_audio = True
        
        ana = st.text_area("Anamnese / Evolução", value=st.session_state.get('transc', ""), height=300)
        con = st.text_area("Conduta Terapêutica", height=150)

    with col_ia:
        if st.button("🚀 Validar CANMAT + APA"):
            st.session_state.ia_res = validacao_multi_diretrizes(ana, con, idade_atual, p_sexo, "PHQ9/GAD7")
        if "ia_res" in st.session_state: st.info(st.session_state.ia_res)

    if st.button("💾 Finalizar e Salvar na Nuvem", use_container_width=True):
        try:
            paciente_data = {"cpf": p_cpf, "nome": p_nome, "idade": idade_atual, "sexo": p_sexo, "nascimento": str(p_nasc)}
            supabase.table("pacientes").upsert(paciente_data).execute()
            consulta_data = {"cpf": p_cpf, "anamnese": ana, "conduta": con, "analise_ia": st.session_state.get('ia_res', "")}
            supabase.table("consultas").insert(consulta_data).execute()
            st.success("✅ Atendimento salvo com sucesso!")
            for k in ['transc', 'ia_res', 'last_audio']: 
                if k in st.session_state: del st.session_state[k]
        except Exception as e: st.error(f"Erro ao salvar: {e}")

# --- PÁGINA: HISTÓRICO ---
elif menu == "Histórico":
    st.header("📂 Histórico de Pacientes")
    busca = st.text_input("🔍 Pesquisar por Nome ou CPF")
    
    if busca:
        # Busca inteligente: Filtra por nome (ilike) ou CPF (eq)
        if busca.isdigit():
            res = supabase.table("consultas").select("*, pacientes(*)").eq("cpf", busca).order("data_hora", desc=True).execute()
        else:
            # Busca por parte do nome
            res_pacientes = supabase.table("pacientes").select("cpf").ilike("nome", f"%{busca}%").execute()
            cpfs = [p['cpf'] for p in res_pacientes.data]
            res = supabase.table("consultas").select("*, pacientes(*)").in_("cpf", cpfs).order("data_hora", desc=True).execute()

        if res.data:
            for item in res.data:
                data_br = formatar_data_br(item['data_hora'])
                with st.expander(f"🗓️ {data_br} - {item['pacientes']['nome']}"):
                    st.write("**📝 Anamnese:**")
                    st.write(item['anamnese'])
                    st.divider()
                    st.write("**💊 Conduta:**")
                    st.write(item['conduta'])
                    st.divider()
                    st.info(f"**🧠 Validação IA:**\n\n{item['analise_ia']}")
        else: st.warning("Nenhum prontuário encontrado para esta busca.")

# --- PÁGINA: AGENDA ---
elif menu == "Agenda":
    st.header("📅 Agenda Clínica")
    st.write("Visualização em formato brasileiro (DD/MM/AAAA)")
    data_sel = st.date_input("Filtrar Data", format="DD/MM/YYYY")
    res_ag = supabase.table("agenda").select("horario, pacientes(nome, tel)").eq("data", data_sel.strftime("%d/%m/%Y")).execute()
    
    if res_ag.data:
        for it in res_ag.data:
            st.write(f"🕒 **{it['horario']}** - {it['pacientes']['nome']} | 📱 {it['pacientes']['tel']}")
    else: st.info("Sem compromissos para este dia.")
