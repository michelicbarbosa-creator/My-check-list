import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="OEKO-Tex Master Certification System 2026")

# ==========================================
# DATABASE CONNECTION & INITIALIZATION
# ==========================================
def connect_db():
    return sqlite3.connect("oeko_tex_isolated_tabs_v21.db")

def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_name TEXT UNIQUE,
            article_number TEXT, model_no TEXT, bom_status TEXT, protocol_type TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER,
            box_num TEXT, phase TEXT, task TEXT, status TEXT, last_update TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER,
            category TEXT, material_name TEXT, doc_type TEXT, certificate_num TEXT, expiry_date TEXT,
            mockup_status TEXT, mockup_approved TEXT, production_order TEXT, related_articles TEXT,
            seam_ready_qty INTEGER, seam_sent_oeti_qtd INTEGER, comments TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone() == 0:
        cursor.execute("""
            INSERT INTO projects (project_name, article_number, model_no, bom_status, protocol_type) 
            VALUES (?, ?, ?, ?, ?)
        """, ("35. ta-d winter + rain parkas", "409 130 - 409 110", "4100-M-ZR-ZH-U", "BOM-L + BOM-C", "New Certification"))
    conn.commit()
    conn.close()

initialize_db()
conn = connect_db()
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)

col_p1, col_p2 = st.columns(2)
with col_p1:
    selected_project = st.selectbox("Active Project Selection", df_projects["project_name"].tolist() if not df_projects.empty else ["No projects found"])
with col_p2:
    with st.popover("➕ Create New Project"):
        with st.form("add_project_form", clear_on_submit=True):
            p_name = st.text_input("Project Name / Code")
            if st.form_submit_button("Create Baseline"):
                if p_name:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO projects (project_name, article_number, model_no, bom_status, protocol_type) VALUES (?, '', '', '', 'New Certification')", (p_name,))
                        conn.commit()
                        st.success("Project generated!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Project name already exists.")

if not df_projects.empty and selected_project != "No projects found":
    df_filtered_proj = df_projects[df_projects["project_name"] == selected_project]
    if not df_filtered_proj.empty:
        proj_row = df_filtered_proj.iloc
        active_project_id = int(proj_row["id"])
    else:
        active_project_id = 0
else:
    active_project_id = 0

opcoes_exatas = ["Technical documentation SPLAG", "Technical documentation confirmed", "Measurement chart", "Measurement check of sample", "Care label"]
if active_project_id > 0:
    cursor = conn.cursor()
    for tarefa_nome in opcoes_exatas:
        cursor.execute("SELECT COUNT(*) FROM project_checklist WHERE project_id = ? AND task = ? AND box_num = '2'", (active_project_id, tarefa_nome))
        if cursor.fetchone() == 0:
            cursor.execute("INSERT INTO project_checklist (project_id, box_num, phase, task, status, last_update) VALUES (?, '2', 'Technical Documentation', ?, 'Pending', '')", (active_project_id, tarefa_nome))
    
    tarefas_extras = [
        ("4", "Sample Garment", "Sample in progress"), ("4", "Sample Garment", "Sample revision at KUNG"),
        ("4", "Sample Garment", "Sample confirmed"), ("4", "Sample Garment", "Sample sent to OETI!"),
        ("4", "Sample Mock-up", "Mock-ups needed"), ("4", "Sample Mock-up", "Seam samples ready"),
        ("4", "Sample Mock-up", "Fabric needed"), ("4", "Sample Mock-up", "Fabric sent to OETI"),
        ("5", "Finalisation", "Technical sheet revision"), ("5", "Finalisation", "BOM revision"), ("5", "Finalisation", "Care label revision")
    ]
    for b_num, ph, tk in tarefas_extras:
        cursor.execute("SELECT COUNT(*) FROM project_checklist WHERE project_id = ? AND task = ? AND box_num = ?", (active_project_id, tk, b_num))
        if cursor.fetchone() == 0:
            cursor.execute("INSERT INTO project_checklist (project_id, box_num, phase, task, status, last_update) VALUES (?, ?, ?, ?, 'Pending', '')", (active_project_id, b_num, ph, tk))
    conn.commit()

df_checklist = pd.read_sql_query(f"SELECT * FROM project_checklist WHERE project_id = {active_project_id}", conn)
df_components = pd.read_sql_query(f"SELECT * FROM production_components WHERE project_id = {active_project_id}", conn)
conn.close()

detailed_categories = ["Fabric", "Zipper", "Lining", "Elastic", "Button", "Thread", "Reflex", "Velcro"]
today = date.today()
if active_project_id > 0:
    with st.expander("📝 Project Header & Certification Status", expanded=True):
        with st.form("edit_project_header"):
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.markdown("#### 🔍 Project Context")
                h_article = col_h1.text_input("Article Number", value=proj_row["article_number"])
                h_model = col_h2 = col_h1.text_input("Model No.", value=proj_row["model_no"])
                h_bom = col_h1.text_input("BOM Status", value=proj_row["bom_status"])
            with col_h2:
                st.markdown("#### 📑 Protocol Type")
                lista_protocolos = ["New Certification", "Application for extension", "Re-certification"]
                status_salvo = proj_row["protocol_type"] if "protocol_type" in proj_row and proj_row["protocol_type"] else "New Certification"
                index_proto = lista_protocolos.index(status_salvo) if status_salvo in lista_protocolos else 0
                tipo_protocolo = st.radio("Select Certification Status for this Project:", lista_protocolos, index=index_proto)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save Project & Certification Records"):
                conn = connect_db()
                conn.execute("UPDATE projects SET article_number=?, model_no=?, bom_status=?, protocol_type=? WHERE id=?", (h_article, h_model, h_bom, tipo_protocolo, active_project_id))
                conn.commit()
                conn.close()
                st.success("Project records synchronized!")
                st.rerun()

st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 1: Expiry & Add", "📑 2: Documentation", "🛠️ 3: Database Logs", "👕 4: Samples & Mock-ups", "🏁 5: Finalisation"
])
with tab1:
    st.header("1️⃣ 1: Certificate Expiry Control")
    alarms_triggered = []
    if not df_components.empty:
        for idx, r in df_components.iterrows():
            try:
                exp_date = datetime.strptime(r["expiry_date"], "%Y-%m-%d").date()
                dias_restantes = (exp_date - today).days
                if r["doc_type"] == "OEKO-Tex Standard 100" and dias_restantes <= 1:
                    alarms_triggered.append(f"⚠️ **OEKO-TEX ALERT:** {r['material_name']} ({r['category']}) expires tomorrow or is invalid!")
                elif r["doc_type"] != "OEKO-Tex Standard 100" and dias_restantes <= 21:
                    alarms_triggered.append(f"⚠️ **TEST REPORT ALERT (3 WEEKS):** {r['material_name']} ({r['doc_type']}) expires in {dias_restantes} days.")
            except: pass

    if alarms_triggered:
        for alarm in alarms_triggered: st.warning(alarm)
    else: st.success("✅ All certification timelines for this project are safe.")

    with st.form("box1_flat_form", clear_on_submit=True):
        st.markdown("#### 📥 Register New Component / Material Document")
        c1, c2, c3 = st.columns(3)
        with c1:
            c_cat = st.selectbox("Component Option", detailed_categories, key="b1_cat")
            c_name = st.text_input("Material Name / Reference")
        with c2:
            c_type = st.selectbox("Document Protocol", ["OEKO-Tex Standard 100", "Test Report Fabric", "Test Report Accessories"], key="b1_type")
            c_num = st.text_input("Certificate Unique ID")
        with c3:
            c_exp = st.date_input("Document Expiry Date", today, key="b1_date")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save Item Validity Data"):
                if c_name and active_project_id > 0:
                    conn = connect_db()
                    conn.execute("INSERT INTO production_components (project_id, category, material_name, doc_type, certificate_num, expiry_date, mockup_status, mockup_approved, production_order, related_articles, seam_ready_qty, seam_sent_oeti_qtd, comments) VALUES (?, ?, ?, ?, ?, ?, 'Mock-ups needed', 'Pending', '', '', 0, 0, '')", (active_project_id, c_cat, c_name, c_type, c_num, str(c_exp)))
                    conn.commit()
                    conn.close()
                    st.rerun()

with tab2:
    st.header("2️⃣ 2: Project Documentation & Validation Checklist")
    if not df_checklist.empty:
        conn = connect_db()
        f_box2 = df_checklist[df_checklist["box_num"] == "2"]
        st.markdown("#### Document Status & Color Tracking")
        for tarefa_nome in opcoes_exatas:
            registro = f_box2[f_box2["task"] == tarefa_nome]
            status_actual = registro.iloc["status"] if not registro.empty else "Pending"
            id_tarefa = int(registro.iloc["id"]) if not registro.empty else None
            
            if status_actual == "Completed":
                cor_fundo, texto_cor = "#d4edda", "#155724"
            elif status_actual == "In Progress":
                cor_fundo, texto_cor = "#fff3cd", "#856404"
            else:
                cor_fundo, texto_cor = "#f8d7da", "#721c24"
                
            st.markdown(f'<div style="background-color: {cor_fundo}; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 6px solid {texto_cor};"><strong style="color: {texto_cor}; font-size: 16px;">{tarefa_nome} — Status: {status_actual}</strong></div>', unsafe_allow_html=True)
            lista_status = ["Pending", "In Progress", "Completed"]
            index_atual = lista_status.index(status_actual) if status_actual in lista_status else 0
            novo_status = st.selectbox(f"Update: {tarefa_nome}", lista_status, index=index_atual, key=f"status_box2_{id_tarefa}", label_visibility="collapsed")
            if novo_status != status_actual and id_tarefa:
                conn.execute("UPDATE project_checklist SET status=? WHERE id=?", (novo_status, id_tarefa))
                conn.commit()
                conn.close()
                st.rerun()
        conn.close()
    else: st.info("No checklist benchmarks found.")

with tab3:
    st.header("3️⃣ 3: Active Component Database Overview")
    sub_tabs = st.tabs(detailed_categories)
    for idx, name_cat in enumerate(detailed_categories):
        with sub_tabs[idx]:
            if not df_components.empty:
                df_f = df_components[df_components["category"] == name_cat]
                if not df_f.empty:
                    st.dataframe(df_f[["material_name", "doc_type", "certificate_num", "expiry_date", "mockup_status", "mockup_approved", "production_order", "related_articles", "seam_ready_qty", "seam_sent_oeti_qtd", "comments"]], use_container_width=True)
                else: st.info("No active records found for this category.")
            else: st.info("Database is currently empty.")

with tab4:
    st.header("4️⃣ 4: Sample Garment Lifecycle & Mock-up Status")
    if not df_checklist.empty:
        conn = connect_db()
        f_box4 = df_checklist[df_checklist["box_num"] == "4"]
        col_b4_1, col_b4_2 = st.columns(2)
        with col_b4_1:
            st.markdown("#### Milestone Verification Checks")
            for idx, r in f_box4.iterrows():
                val = st.selectbox(f"{r['task']} ({r['phase']})", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(r["status"]), key=f"sb4_{r['id']}")
                if val != r["status"]:
                    conn.execute("UPDATE project_checklist SET status=? WHERE id=?", (val, r["id"]))
                    conn.commit()
                    conn.close()
                    st.rerun()
        with col_b4_2:
            st.markdown("#### Update Industrial Routing / Volumes")
            if not df_components.empty:
                t_mat = st.selectbox("Choose Target Material to Modify", df_components["material_name"].tolist(), key="sb4_mat")
                df_target_comp = df_components[df_components["material_name"] == t_mat]
                if not df_target_comp.empty:
                    m_row = df_target_comp.iloc
                    with st.form("box4_manufacturing_form"):
                        m_st = st.selectbox("Mock-up Status", ["Mock-ups needed", "Seam samples in progress", "Ready"], index=["Mock-ups needed", "Seam samples in progress", "Ready"].index(m_row["mockup_status"]))
                        m_ap = st.selectbox("Mock-up Evaluation", ["Pending", "Approved", "Rejected"], index=["Pending", "Approved", "Rejected"].index(m_row["mockup_approved"]))
                        m_po = st.text_input("Production Order (PO Number)", value=m_row["production_order"])
                        m_art = st.text_area("Linked Production Articles", value=m_row["related_articles"])
                        m_rdy = st.number_input("Seam Samples Ready (Qty Made)", min_value=0, value=int(m_row["seam_ready_qty"]))
                        m_snt = st.number_input("Seam Samples Sent to OETI (Qty Sent)", min_value=0, value=int(m_row["seam_sent_oeti_qtd"]))
                        m_cm = st.text_input("Line Comments", value=m_row["comments"])
                        if st.form_submit_button("Save Component Changes"):
                            conn_inner = connect_db()
                            conn_inner.execute("UPDATE production_components SET mockup_status=?, mockup_approved=?, production_order=?, related_articles=?, seam_ready_qty=?, seam_sent_oeti_qtd=?, comments=? WHERE material_name=? AND project_id=?", (m_st, m_ap, m_po, m_art, int(m_rdy), int(m_snt), m_cm, t_mat, active_project_id))
                            conn_inner.commit()
                            conn_inner.close()
                            st.rerun()
        conn.close()
    else: st.info("No active milestones mapped.")

with tab5:
    st.header("5️⃣ 5: Project Finalisation Tasks")
    if not df_checklist.empty:
        conn = connect_db()
        f_box5 = df_checklist[df_checklist["box_num"] == "5"]
        for idx, r in f_box5.iterrows():
            val = st.selectbox(f"🏁 {r['task']}", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(r["status"]), key=f"sb5_{r['id']}")
            if val != r["status"]:
                conn.execute("UPDATE project_checklist SET status=? WHERE id=?", (val, r["id"]))
                conn.commit()
                conn.close()
                st.rerun()
        conn.close()
    else: st.info("Closure parameters unassigned.")

