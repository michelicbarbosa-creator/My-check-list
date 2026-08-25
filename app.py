import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="OEKO-Tex Master Certification System 2026")

# ==========================================
# 1. DATABASE MANAGEMENT (PERMANENT SQLITE)
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
    else: active_project_id = 0
else: active_project_id = 0

# --- AUTO-SEED DATA INJECTION FOR SAFETY ---
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

# Reload records after seeding
df_checklist = pd.read_sql_query(f"SELECT * FROM project_checklist WHERE project_id = {active_project_id}", conn)
df_components = pd.read_sql_query(f"SELECT * FROM production_components WHERE project_id = {active_project_id}", conn)
conn.close()

detailed_categories = ["Fabric", "Zipper", "Lining", "Elastic", "Button", "Thread", "Reflex", "Velcro"]
today = date.today()

# ==========================================
# 2. PROJECT HEADER & PROTOCOL STATUS
# ==========================================
if active_project_id > 0:
    with st.expander("📝 Project Header & Certification Status", expanded=True):
        with st.form("edit_project_header"):
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.markdown("#### 🔍 Project Context")
                h_article = st.text_input("Article Number", value=proj_row["article_number"])
                h_model = st.text_input("Model No.", value=proj_row["model_no"])
                h_bom = st.text_input("BOM Status", value=proj_row["bom_status"])
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

# ==========================================
# 3. ABAS PRINCIPAIS - APENAS NÚMEROS (TRADUZIDAS)
# ==========================================
st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 1: Expiry & Add", "📑 2: Documentation", "🛠️ 3: Database Logs", "👕 4: Samples & Mock-ups", "🏁 5: Finalisation"
])

# --- TAB 1: 1 ---
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

# --- TAB 2: 2 COLOR CARDS ---
with tab2:
    st.header("2️⃣ 2: Project Documentation & Validation Checklist")
    if not df_checklist.empty:
        conn = connect_db()
