import streamlit as st
import sqlite3
import hashlib
import io
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bucci Family Psychiatric Clinic", layout="wide")

# Caminho do Banco de Dados e da Logo
db_path = "clinica_web.db"
logo_path = "logo_bucci.jpg"

def conectar(): return sqlite3.connect(db_path)
def hash_s(s): return hashlib.sha256(str.encode(s)).hexdigest()

def init_db():
    conn = conectar(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios 
                 (username TEXT PRIMARY KEY, senha TEXT, nivel TEXT, nome TEXT, crm TEXT, rqe TEXT, recuperacao TEXT)""")
    c.execute("CREATE TABLE IF NOT EXISTS pacientes (cpf TEXT PRIMARY KEY, nome TEXT, nascimento TEXT, tel TEXT, endereco TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS consultas (id INTEGER PRIMARY KEY AUTOINCREMENT, cpf TEXT, data TEXT, 
                 anamnese TEXT, mental TEXT, conduta TEXT, medico TEXT)""")
    c.execute("CREATE TABLE IF NOT EXISTS receitas (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_cpf TEXT, data TEXT, conteudo TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_cpf TEXT, 
                 data TEXT, horario TEXT, status TEXT DEFAULT 'Agendado')""")
    conn.commit(); conn.close()

init_db()

# --- CONTROLE DE SESSÃO ---
if "logado" not in st.session_state: st.session_state.logado = False

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    conn = conectar(); c = conn.cursor(); c.execute("SELECT COUNT(*) FROM usuarios"); tem_user = c.fetchone()[0] > 0; conn.close()

    if not tem_user:
        st.warning("🆕 Primeiro Acesso: Cadastre o Médico Administrador (Mestre)")
        with st.form("cad_mestre"):
            u, s = st.text_input("Usuário de Login"), st.text_input("Senha", type="password")
            n, c_m, r_q = st.text_input("Nome Completo"), st.text_input("CRM"), st.text_input("RQE")
            p_c = st.text_input("Palavra-Chave de Recuperação")
            if st.form_submit_button("Criar Conta Mestre"):
                conn = conectar(); c = conn.cursor()
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?)", (u, hash_s(s), "mestre", n, c_m, r_q, p_c.lower()))
                conn.commit(); conn.close(); st.success("Conta Mestre criada! Faça login."); st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 Login", "🔑 Recuperar Senha"])
        with t1:
            u_in, p_in = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.button("Entrar"):
                conn = conectar(); c = conn.cursor()
                c.execute("SELECT nivel, nome, crm, rqe FROM usuarios WHERE username=? AND senha=?", (u_in, hash_s(p_in)))
                res = c.fetchone()
                if res:
                    st.session_state.logado, st.session_state.user = True, u_in
                    st.session_state.m_nome, st.session_state.m_crm, st.session_state.m_rqe = res[1], res[2], res[3]
                    st.rerun()
                else: st.error("Dados incorretos."); conn.close()
        with t2:
            u_rec, p_rec, n_s = st.text_input("Usuário "), st.text_input("Palavra-Chave "), st.text_input("Nova Senha", type="password")
            if st.button("Redefinir"):
                conn = conectar(); c = conn.cursor()
                c.execute("UPDATE usuarios SET senha=? WHERE username=? AND recuperacao=?", (hash_s(n_s), u_rec, p_rec.lower()))
                if conn.total_changes > 0: conn.commit(); st.success("Senha alterada!"); conn.close()
                else: st.error("Dados incorretos."); conn.close()

else:
    # --- SISTEMA LOGADO ---
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        st.sidebar.title("BUCCI CLINIC")
        
    st.sidebar.subheader(f"👨‍⚕️ Dr(a). {st.session_state.m_nome}")
    menu = st.sidebar.radio("Navegação", ["Agenda", "Atendimento", "Histórico / Receituário", "Sair"])

    if menu == "Sair": 
        st.session_state.logado = False
        st.rerun()

    # --- ABA AGENDA ---
    elif menu == "Agenda":
        st.header("📅 Agenda de Consultas")
        t_m, t_v = st.tabs(["Marcar Consulta", "Ver Agenda do Dia"])
        with t_m:
            cp_ag = st.text_input("CPF do Paciente")
            dt_ag = st.date_input("Data", min_value=datetime.now())
            hr_ag = st.selectbox("Horário", [f"{h:02d}:{m:02d}" for h in range(8,19) for m in (0,30)])
            if st.button("Confirmar Agendamento"):
                conn = conectar(); c = conn.cursor()
                c.execute("SELECT id FROM agenda WHERE data=? AND horario=?", (dt_ag.strftime("%d/%m/%Y"), hr_ag))
                if c.fetchone(): st.error("⚠️ Horário já ocupado!")
                else:
                    c.execute("INSERT INTO agenda (paciente_cpf, data, horario) VALUES (?,?,?)", (cp_ag, dt_ag.strftime("%d/%m/%Y"), hr_ag))
                    conn.commit(); st.success("✅ Consulta agendada!"); conn.close()
        with t_v:
            dt_f = st.date_input("Filtrar por Dia", value=datetime.now())
            conn = conectar(); c = conn.cursor()
            c.execute("SELECT a.horario, p.nome, a.id, a.paciente_cpf FROM agenda a LEFT JOIN pacientes p ON a.paciente_cpf = p.cpf WHERE a.data=?", (dt_f.strftime("%d/%m/%Y"),))
            for h, n, i, cp in c.fetchall():
                with st.expander(f"⏰ {h} - {n if n else 'Paciente Novo ('+cp+')'}"):
                    if st.button("Remover", key=f"r{i}"):
                        c.execute("DELETE FROM agenda WHERE id=?", (i,)); conn.commit(); st.rerun()
            conn.close()

    # --- ABA ATENDIMENTO ---
    elif menu == "Atendimento":
        st.header("📝 Novo Prontuário")
        c1, c2, c3 = st.columns(3)
        p_nome = c1.text_input("Nome do Paciente")
        p_cpf = c2.text_input("CPF")
        p_nasc = c3.text_input("Data de Nascimento")
        p_tel = st.text_input("Telefone / WhatsApp")
        p_end = st.text_input("Endereço Completo")
        
        tab_a, tab_m, tab_c = st.tabs(["Anamnese", "Exame Mental", "Conduta e Plano Terapêutico"])
        ana = tab_a.text_area("Descrição detalhada", height=200, key="ana")
        men = tab_m.text_area("Estado Mental atual", height=200, key="men")
        con = tab_c.text_area("Conduta e Prescrição", height=200, key="con")
        
        if st.button("💾 SALVAR PRONTUÁRIO"):
            if p_nome and p_cpf:
                conn = conectar(); c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO pacientes VALUES (?,?,?,?,?)", (p_cpf, p_nome, p_nasc, p_tel, p_end))
                c.execute("INSERT INTO consultas (cpf, data, anamnese, mental, conduta, medico) VALUES (?,?,?,?,?,?)",
                           (p_cpf, datetime.now().strftime("%d/%m/%Y"), ana, men, con, st.session_state.m_nome))
                conn.commit(); conn.close(); st.success("✅ Atendimento salvo com sucesso!")
            else: st.error("Nome e CPF são obrigatórios.")

    # --- ABA HISTÓRICO / RECEITUÁRIO ---
    elif menu == "Histórico / Receituário":
        st.header("🔍 Central do Paciente")
        busca = st.text_input("Pesquisar por Nome ou CPF")
        if busca:
            conn = conectar(); c = conn.cursor()
            c.execute("SELECT * FROM pacientes WHERE nome LIKE ? OR cpf=?", (f"%{busca}%", busca))
            pac = c.fetchone()
            if pac:
                st.subheader(f"👤 {pac[1]} | Tel: {pac[3]}")
                st.info(f"Endereço: {pac[4]}")
                
                # Histórico Clínico
                st.divider()
                st.subheader("📚 Consultas Anteriores")
                c.execute("SELECT data, conduta, medico, anamnese FROM consultas WHERE cpf=? ORDER BY id DESC", (pac[0],))
                for d, co, m, a in c.fetchall():
                    with st.expander(f"📅 Consulta em {d} - Dr. {m}"):
                        st.write("**Anamnese:**", a)
                        st.write("**Conduta:**", co)
                
                # Receituário A5
                st.divider()
                st.subheader("💊 Emitir Receita A5")
                
                # Histórico de Receitas Lateral
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.write("**Histórico de Receitas**")
                    c.execute("SELECT id, data, conteudo FROM receitas WHERE paciente_cpf=? ORDER BY id DESC", (pac[0],))
                    for rid, rdt, rct in c.fetchall():
                        if st.button(f"📄 {rdt}", key=f"rec_{rid}"):
                            st.session_state.temp_rec = rct
                
                with c2:
                    if 'temp_rec' not in st.session_state: st.session_state.temp_rec = ""
                    rec_texto = st.text_area("Prescrição", value=st.session_state.temp_rec, height=300)
                    
                    if st.button("💾 Salvar Receita no Banco"):
                        c.execute("INSERT INTO receitas (paciente_cpf, data, conteudo) VALUES (?,?,?)", 
                                   (pac[0], datetime.now().strftime("%d/%m/%Y"), rec_texto))
                        conn.commit(); st.success("Receita gravada no histórico!")

                    # Gerar PDF A5 com Logo
                    buf = io.BytesIO(); pdf = canvas.Canvas(buf, pagesize=A5); w, h = A5
                    if os.path.exists(logo_path):
                        pdf.drawImage(logo_path, w/2-50, h-70, width=100, preserveAspectRatio=True)
                    
                    pdf.setFont("Helvetica-Bold", 12); pdf.drawCentredString(w/2, h-85, "BUCCI FAMILY PSYCHIATRIC CLINIC")
                    pdf.setFont("Helvetica", 9); pdf.drawString(40, h-110, f"Paciente: {pac[1]} | Data: {datetime.now().strftime('%d/%m/%Y')}")
                    pdf.line(40, h-115, w-40, h-115); y = h-135
                    
                    pdf.setFont("Helvetica", 11)
                    for linha in rec_texto.split('\n'): 
                        pdf.drawString(50, y, linha); y -= 18
                    
                    # Rodapé
                    pdf.line(w*0.2, 60, w*0.8, 60)
                    pdf.setFont("Helvetica-Bold", 9); pdf.drawCentredString(w/2, 48, f"Dr(a). {st.session_state.m_nome}")
                    pdf.setFont("Helvetica", 8); pdf.drawCentredString(w/2, 38, f"CRM: {st.session_state.m_crm} | RQE: {st.session_state.m_rqe}")
                    pdf.save(); buf.seek(0)
                    
                    st.download_button("📄 Baixar Receita PDF A5", buf, f"receita_{pac[1]}.pdf", "application/pdf")
            else: st.warning("Paciente não localizado.")
            conn.close()