import streamlit as st
import sqlite3
import hashlib
import io
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Clínico Web", layout="wide")

# --- BANCO DE DADOS ---
def conectar(): return sqlite3.connect("clinica_web.db")
def hash_s(s): return hashlib.sha256(str.encode(s)).hexdigest()

def init_db():
    conn = conectar(); c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS usuarios (username TEXT PRIMARY KEY, senha TEXT, nivel TEXT, nome TEXT, crm TEXT, rqe TEXT, recuperacao TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS pacientes (cpf TEXT PRIMARY KEY, nome TEXT, nascimento TEXT, tel TEXT, endereco TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS consultas (id INTEGER PRIMARY KEY AUTOINCREMENT, cpf TEXT, data TEXT, anamnese TEXT, mental TEXT, conduta TEXT, medico TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS receitas (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_cpf TEXT, data TEXT, conteudo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_cpf TEXT, data TEXT, horario TEXT, status TEXT DEFAULT 'Agendado')")
    c.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nome_clinica TEXT, logo_url TEXT)")
    c.execute("INSERT OR IGNORE INTO config (id, nome_clinica, logo_url) VALUES (1, 'Minha Clínica', '')")
    conn.commit(); conn.close()

def buscar_config():
    conn = conectar(); c = conn.cursor()
    c.execute("SELECT nome_clinica, logo_url FROM config WHERE id = 1")
    res = c.fetchone()
    conn.close()
    return res if res else ("Minha Clínica", "")

init_db()

# --- CONTROLE DE SESSÃO ---
if "logado" not in st.session_state: st.session_state.logado = False

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    conn = conectar(); c = conn.cursor(); c.execute("SELECT COUNT(*) FROM usuarios"); tem_user = c.fetchone()[0] > 0; conn.close()

    if not tem_user:
        st.warning("🆕 Primeiro Acesso: Cadastre o Médico Administrador")
        with st.form("cad_mestre"):
            u, s = st.text_input("Usuário de Login"), st.text_input("Senha", type="password")
            n, c_m, r_q = st.text_input("Nome Completo"), st.text_input("CRM"), st.text_input("RQE")
            p_c = st.text_input("Palavra-Chave de Recuperação")
            if st.form_submit_button("Criar Conta Mestre"):
                conn = conectar(); c = conn.cursor()
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?)", (u, hash_s(s), "mestre", n, c_m, r_q, p_c.lower()))
                conn.commit(); conn.close(); st.success("Criado! Faça login."); st.rerun()
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
                    st.session_state.nvel, st.session_state.m_nome, st.session_state.m_crm, st.session_state.m_rqe = res[0], res[1], res[2], res[3]
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
    n_clinica, l_url = buscar_config()
    st.sidebar.title(f"👨‍⚕️ {st.session_state.m_nome}")
    if l_url: st.sidebar.image(l_url, use_column_width=True)
    
    lista_menu = ["Agenda", "Novo Atendimento", "Histórico / Receituário"]
    if st.session_state.nvel == "mestre": lista_menu.append("Configurações")
    lista_menu.append("Sair")
    
    menu = st.sidebar.radio("Navegação", lista_menu)

    if menu == "Sair": st.session_state.logado = False; st.rerun()

    # --- ABA CONFIGURAÇÕES ---
    elif menu == "Configurações":
        st.header("⚙️ Configurações da Clínica")
        with st.form("f_conf"):
            nc = st.text_input("Nome da Clínica", value=n_clinica)
            lu = st.text_input("URL da Logotipo (PNG/JPG)", value=l_url)
            if st.form_submit_button("Salvar"):
                conn = conectar(); c = conn.cursor()
                c.execute("UPDATE config SET nome_clinica=?, logo_url=? WHERE id=1", (nc, lu))
                conn.commit(); conn.close(); st.success("Atualizado!"); st.rerun()

    # --- ABA AGENDA ---
    elif menu == "Agenda":
        st.header(f"📅 Agenda - {n_clinica}")
        t_m, t_v = st.tabs(["Marcar", "Ver Consultas"])
        with t_m:
            c1, c2, c3 = st.columns(3)
            cp_ag = c1.text_input("CPF do Paciente")
            dt_ag = c2.date_input("Data", min_value=datetime.now())
            hr_ag = c3.selectbox("Horário", [f"{h:02d}:{m:02d}" for h in range(8,19) for m in (0,30)])
            if st.button("Confirmar Agendamento"):
                conn = conectar(); c = conn.cursor()
                c.execute("SELECT id FROM agenda WHERE data=? AND horario=?", (dt_ag.strftime("%d/%m/%Y"), hr_ag))
                if c.fetchone(): st.error("⚠️ Horário já ocupado!")
                else:
                    c.execute("INSERT INTO agenda (paciente_cpf, data, horario) VALUES (?,?,?)", (cp_ag, dt_ag.strftime("%d/%m/%Y"), hr_ag))
                    conn.commit(); st.success("✅ Agendado!"); conn.close()
        with t_v:
            dt_f = st.date_input("Filtrar por Dia", value=datetime.now())
            conn = conectar(); c = conn.cursor()
            c.execute("SELECT a.horario, p.nome, a.id, a.paciente_cpf FROM agenda a LEFT JOIN pacientes p ON a.paciente_cpf = p.cpf WHERE a.data=?", (dt_f.strftime("%d/%m/%Y"),))
            for h, n, i, cp in c.fetchall():
                with st.expander(f"⏰ {h} - {n if n else 'Paciente Novo ('+cp+')'}"):
                    if st.button("Remover Agendamento", key=f"r{i}"):
                        c.execute("DELETE FROM agenda WHERE id=?", (i,)); conn.commit(); st.rerun()
            conn.close()

    # --- ABA ATENDIMENTO ---
    elif menu == "Novo Atendimento":
        st.header(f"📝 Prontuário Digital - {n_clinica}")
        c1, c2, c3 = st.columns([2,1,1])
        p_nome = c1.text_input("Nome")
        p_cpf = c2.text_input("CPF")
        p_nasc = c3.text_input("Nasc (dd/mm/aaaa)")
        p_tel = st.text_input("Telefone")
        p_end = st.text_input("Endereço")
        
        t1, t2, t3 = st.tabs(["Anamnese", "Exame Mental", "Conduta"])
        ana = t1.text_area("Descrição", height=200, key="ana")
        men = t2.text_area("Descrição", height=200, key="men")
        con = t3.text_area("Descrição", height=200, key="con")
        
        if st.button("💾 SALVAR ATENDIMENTO"):
            if p_nome and p_cpf:
                conn = conectar(); c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO pacientes VALUES (?,?,?,?,?)", (p_cpf, p_nome, p_nasc, p_tel, p_end))
                c.execute("INSERT INTO consultas (cpf, data, anamnese, mental, conduta, medico) VALUES (?,?,?,?,?,?)",
                           (p_cpf, datetime.now().strftime("%d/%m/%Y"), ana, men, con, st.session_state.m_nome))
                conn.commit(); conn.close(); st.success("✅ Prontuário Salvo!")
            else: st.error("Nome e CPF são obrigatórios.")

    # --- ABA HISTÓRICO ---
    elif menu == "Histórico / Receituário":
        st.header("🔍 Pesquisa e Receituário")
        busca = st.text_input("Digite Nome ou CPF")
        if busca:
            conn = conectar(); c = conn.cursor()
            c.execute("SELECT * FROM pacientes WHERE nome LIKE ? OR cpf=?", (f"%{busca}%", busca))
            pac = c.fetchone()
            if pac:
                st.subheader(f"👤 {pac[1]} | Tel: {pac[3]}")
                st.write(f"Endereço: {pac[4]}")
                
                # Histórico
                st.write("---")
                c.execute("SELECT data, conduta, medico FROM consultas WHERE cpf=? ORDER BY id DESC", (pac[0],))
                for d, co, m in c.fetchall():
                    with st.expander(f"📅 Atendimento {d} - Dr. {m}"): st.write(co)
                
                # Receita
                st.write("---")
                st.subheader("💊 Nova Prescrição")
                rec_t = st.text_area("Texto da Receita", height=250)
                
                col_r1, col_r2 = st.columns(2)
                if col_r1.button("💾 Salvar no Histórico"):
                    c.execute("INSERT INTO receitas (paciente_cpf, data, conteudo) VALUES (?,?,?)", (pac[0], datetime.now().strftime("%d/%m/%Y"), rec_t))
                    conn.commit(); st.success("Receita gravada!")

                # PDF A5
                buf = io.BytesIO(); pdf = canvas.Canvas(buf, pagesize=A5); w, h = A5
                pdf.setFont("Helvetica-Bold", 14); pdf.drawCentredString(w/2, h-40, n_clinica.upper())
                pdf.setFont("Helvetica", 10); pdf.drawString(40, h-70, f"Paciente: {pac[1]} | Data: {datetime.now().strftime('%d/%m/%Y')}")
                pdf.line(40, h-75, w-40, h-75); y = h-100
                pdf.setFont("Helvetica", 11)
                for l in rec_t.split('\n'): pdf.drawString(50, y, l); y -= 18
                pdf.drawCentredString(w/2, 60, "__________________________")
                pdf.drawCentredString(w/2, 48, st.session_state.m_nome)
                pdf.setFont("Helvetica", 8); pdf.drawCentredString(w/2, 38, f"CRM: {st.session_state.m_crm} | RQE: {st.session_state.m_rqe}")
                pdf.save(); buf.seek(0)
                col_r2.download_button("📄 Baixar Receita A5", buf, f"rec_{pac[1]}.pdf", "application/pdf")
            conn.close()