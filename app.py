import streamlit as st
import sqlite3
import hashlib
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Clinic System Web", layout="wide")

def conectar(): return sqlite3.connect("clinica_web.db")
def hash_s(s): return hashlib.sha256(str.encode(s)).hexdigest()

def init_db():
    conn = conectar(); c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nome_clinica TEXT, logo_url TEXT)")
    c.execute("INSERT OR IGNORE INTO config (id, nome_clinica, logo_url) VALUES (1, 'Minha Clínica', '')")
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

# --- LOGIN / ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    conn = conectar(); c = conn.cursor(); c.execute("SELECT COUNT(*) FROM usuarios"); tem_user = c.fetchone()[0] > 0; conn.close()

    if not tem_user:
        st.warning("🆕 Primeiro Acesso: Cadastre o Médico Administrador")
        with st.form("cad_mestre"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            n, c_m, r_q = st.text_input("Nome Completo"), st.text_input("CRM"), st.text_input("RQE")
            p_c = st.text_input("Palavra-Chave de Recuperação")
            if st.form_submit_button("Criar Conta Mestre"):
                conn = conectar(); c = conn.cursor()
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?)", (u, hash_s(s), "mestre", n, c_m, r_q, p_c.lower()))
                conn.commit(); conn.close(); st.success("Criado!"); st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 Login", "🔑 Recuperar"])
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
                else: st.error("Incorreto"); conn.close()
        with t2:
            u_rec, p_rec, n_s = st.text_input("Usuário "), st.text_input("Palavra-Chave "), st.text_input("Nova Senha", type="password")
            if st.button("Redefinir"):
                conn = conectar(); c = conn.cursor()
                c.execute("UPDATE usuarios SET senha=? WHERE username=? AND recuperacao=?", (hash_s(n_s), u_rec, p_rec.lower()))
                conn.commit(); st.success("Senha alterada!"); conn.close()

else:
    # --- SISTEMA ---
    st.sidebar.title(f"👨‍⚕️ {st.session_state.m_nome}")
    menu = st.sidebar.radio("Navegação", ["Agenda", "Novo Atendimento", "Histórico / Receituário", "Sair"])

    if menu == "Sair": st.session_state.logado = False; st.rerun()

    # --- ABA AGENDA ---
    elif menu == "Agenda":
        st.header("📅 Agenda")
        t_m, t_v = st.tabs(["Marcar", "Ver Consultas"])
        with t_m:
            cp_ag = st.text_input("CPF do Paciente")
            dt_ag = st.date_input("Data", min_value=datetime.now())
            hr_ag = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8,19)] + [f"{h:02d}:30" for h in range(8,18)])
            if st.button("Agendar"):
                conn = conectar(); c = conn.cursor()
                c.execute("SELECT id FROM agenda WHERE data=? AND horario=?", (dt_ag.strftime("%d/%m/%Y"), hr_ag))
                if c.fetchone(): st.error("Horário ocupado!")
                else:
                    c.execute("INSERT INTO agenda (paciente_cpf, data, horario) VALUES (?,?,?)", (cp_ag, dt_ag.strftime("%d/%m/%Y"), hr_ag))
                    conn.commit(); st.success("Agendado!")
                conn.close()
        with t_v:
            dt_f = st.date_input("Filtrar Data", value=datetime.now())
            conn = conectar(); c = conn.cursor()
            c.execute("SELECT a.horario, p.nome, a.id FROM agenda a LEFT JOIN pacientes p ON a.paciente_cpf = p.cpf WHERE a.data=?", (dt_f.strftime("%d/%m/%Y"),))
            for h, n, i in c.fetchall():
                with st.expander(f"⏰ {h} - {n if n else 'Paciente Novo'}"):
                    if st.button("Remover", key=f"r{i}"):
                        c.execute("DELETE FROM agenda WHERE id=?", (i,)); conn.commit(); st.rerun()
            conn.close()

    # --- ABA ATENDIMENTO ---
    elif menu == "Novo Atendimento":
        st.header("📝 Prontuário")
        c1, c2, c3 = st.columns(3)
        p_nome, p_cpf = c1.text_input("Nome"), c2.text_input("CPF")
        p_nasc, p_tel = c3.text_input("Nasc"), st.text_input("Tel")
        p_end = st.text_input("Endereço")
        
        tab_a, tab_m, tab_c = st.tabs(["Anamnese", "Exame Mental", "Conduta"])
        ana, men, con = tab_a.text_area("H"), tab_m.text_area("M"), tab_c.text_area("C")
        
        if st.button("💾 SALVAR"):
            conn = conectar(); c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO pacientes VALUES (?,?,?,?,?)", (p_cpf, p_nome, p_nasc, p_tel, p_end))
            c.execute("INSERT INTO consultas (cpf, data, anamnese, mental, conduta, medico) VALUES (?,?,?,?,?,?)",
                       (p_cpf, datetime.now().strftime("%d/%m/%Y"), ana, men, con, st.session_state.user))
            conn.commit(); conn.close(); st.success("Salvo!")

    # --- ABA HISTÓRICO ---
    elif menu == "Histórico / Receituário":
        st.header("🔍 Pesquisa")
        busca = st.text_input("Nome ou CPF")
        if busca:
            conn = conectar(); c = conn.cursor()
            c.execute("SELECT * FROM pacientes WHERE nome LIKE ? OR cpf=?", (f"%{busca}%", busca))
            pac = c.fetchone()
            if pac:
                st.subheader(f"👤 {pac[1]}")
                # Consultas
                c.execute("SELECT data, conduta FROM consultas WHERE cpf=? ORDER BY id DESC", (pac[0],))
                for d, co in c.fetchall():
                    with st.expander(f"Consulta {d}"): st.write(co)
                # Receita
                rec_t = st.text_area("Receita", height=200)
                if st.button("Salvar Receita"):
                    c.execute("INSERT INTO receitas (paciente_cpf, data, conteudo) VALUES (?,?,?)", (pac[0], datetime.now().strftime("%d/%m/%Y"), rec_t))
                    conn.commit(); st.success("Gravada!")
                # PDF
                buf = io.BytesIO(); pdf = canvas.Canvas(buf, pagesize=A5); w, h = A5
                pdf.drawCentredString(w/2, h-40, "RECEITUÁRIO MÉDICO")
                pdf.drawString(40, h-70, f"Paciente: {pac[1]} | Data: {datetime.now().strftime('%d/%m/%Y')}")
                y = h-110
                for l in rec_t.split('\n'): pdf.drawString(50, y, l); y -= 15
                pdf.drawCentredString(w/2, 40, f"{st.session_state.m_nome} | CRM: {st.session_state.m_crm}")
                pdf.save(); buf.seek(0)
                st.download_button("📄 Baixar PDF", buf, f"rec_{pac[0]}.pdf", "application/pdf")
            conn.close()
