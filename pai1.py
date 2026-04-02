import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Bucci Psychiatry - Supabase Edition", layout="wide")

# --- 1. CONEXÕES (IA E SUPABASE) ---
try:
    # IA Gemini
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Supabase (Chaves salvas no Secrets do Streamlit Cloud)
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- 2. FUNÇÕES DE IA ---
def validacao_ia(ana, con, idade, sexo, escores):
    prompt = f"Paciente {idade}a, {sexo}. Escalas {escores}. Caso: {ana}. Conduta: {con}. Valide via CANMAT/APA."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text
    except: return "Erro na IA."

# --- 3. LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🔐 Bucci Clinic - Acesso Restrito")
    u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
    if st.button("Acessar"):
        if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
            st.session_state.logado = True
            st.rerun()
    st.stop()

# --- 4. INTERFACE ---
menu = st.sidebar.radio("Navegação", ["📝 Atendimento", "📂 Histórico", "🚪 Sair"])

if menu == "📝 Atendimento":
    st.header("Novo Atendimento (Nuvem Supabase)")
    
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        p_nome = c1.text_input("Nome")
        p_cpf = c2.text_input("CPF")
        p_idade = c3.number_input("Idade", 0, 120)
        p_sexo = c4.selectbox("Sexo", ["M", "F"])

    ana = st.text_area("Anamnese", height=200)
    con = st.text_area("Conduta", height=150)
    
    if st.button("✨ Analisar com IA"):
        st.session_state.ia_res = validacao_ia(ana, con, p_idade, p_sexo, "N/A")
        st.info(st.session_state.ia_res)

    if st.button("💾 Salvar Atendimento Definitivo", use_container_width=True):
        try:
            # 1. Salva/Atualiza o Paciente
            paciente_data = {"cpf": p_cpf, "nome": p_nome, "idade": p_idade, "sexo": p_sexo}
            supabase.table("pacientes").upsert(paciente_data).execute()
            
            # 2. Salva a Consulta
            consulta_data = {
                "cpf": p_cpf,
                "anamnese": ana,
                "conduta": con,
                "analise_ia": st.session_state.get('ia_res', "")
            }
            supabase.table("consultas").insert(consulta_data).execute()
            st.success("✅ Prontuário salvo com segurança na nuvem!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

elif menu == "📂 Histórico":
    st.header("Busca no Banco de Dados")
    cpf_busca = st.text_input("Digite o CPF")
    if cpf_busca:
        res = supabase.table("consultas").select("*").eq("cpf", cpf_busca).order("data_hora", desc=True).execute()
        if res.data:
            for item in res.data:
                with st.expander(f"Consulta em {item['data_hora']}"):
                    st.write(f"**Conduta:** {item['conduta']}")
                    st.write(f"**Análise IA:** {item['analise_ia']}")
        else:
            st.warning("Nenhum registro encontrado.")

elif menu == "🚪 Sair":
    st.session_state.logado = False; st.rerun()
