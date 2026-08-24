import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="OEKO-Tex Master Certification System 2026")

# ==========================================
# 1. DATABASE MANAGEMENT (PERMANENT SQLITE)
# ==========================================
def connect_db():
    return sqlite3.connect("oeko_tex_perfect_v16.db")

def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Project Header Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_name TEXT UNIQUE,
            article_number TEXT, model_no TEXT, bom_status TEXT
        )
    """)
    
    # Checklist Table for Boxes 2, 4 & 5
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER,
            box_num TEXT, phase TEXT, task TEXT, status TEXT, last_update TEXT
        )
    """)
    
    # Component Matrix Table for Box 1 & Box 3
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER,
            category TEXT, material_name TEXT, doc_type TEXT, certificate_num TEXT, expiry_date TEXT,
            mockup_status TEXT, mockup_approved TEXT, production_order TEXT, related_articles TEXT,
            seam_ready_qty INTEGER, seam_sent_oeti_qtd INTEGER, comments TEXT
        )
    """)
    
    # Seed Baseline Template if completely empty
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone() == 0:
        cursor.execute("""
            INSERT INTO projects (project_name, article_number, model_no, bom_status) 
            VALUES (?, ?, ?, ?)
        """, ("35. ta-d winter + rain parkas", "409 130 - 409 110", "4100-M-ZR-ZH-U", "BOM-L + BOM-C"))
        default_id = cursor.lastrowid
        
        tasks = [
            ("2", "Documentation & Application", "New Certification", "Pending", ""),
            ("2", "Documentation & Application", "Application for extension", "Pending", ""),
            ("2", "Documentation & Application", "Application form OETI", "Pending", ""),
            ("2", "Documentation & Application", "Technical document OETI", "Pending", ""),
            ("2", "OEKO-Tex & Re-certification", "Re-certification", "Pending", ""),
            ("2", "OEKO-Tex & Re-certification", "Test Reports fabric (OEKO-Tex)", "Completed", ""),
            ("2", "OEKO-Tex & Re-certification", "Test Reports lining (OEKO-Tex)", "Completed", ""),
            ("2", "OEKO-Tex & Re-certification", "Test Reports accessories (OEKO-Tex)", "Pending", ""),
            ("2", "Technical Documentation", "Technical documentation SPLAG", "Completed", "2026-08-24"),
            ("2", "Technical Documentation", "Technical documentation confirmed", "Completed", ""),
            ("2", "Technical Documentation", "Measurement chart", "Completed", ""),
            ("2", "Technical Documentation", "Care label", "Pending", ""),
            ("4", "Sample Garment", "Sample in progress", "Pending", ""),
            ("4", "Sample Garment", "Sample revision at KUNG", "Pending", ""),
            ("4", "Sample Garment", "Sample confirmed", "Pending", ""),
            ("4", "Sample Garment", "Sample sent to OETI!", "Pending", ""),
            ("4", "Sample Mock-up", "Mock-ups needed", "Pending", ""),
            ("4", "Sample Mock-up", "Seam samples ready", "Pending", ""),
            ("4", "Sample Mock-up", "Fabric needed", "Pending", ""),
            ("4", "Sample Mock-up", "Fabric sent to OETI", "Pending", ""),
            ("5", "Finalisation", "Technical sheet revision", "Pending", ""),
            ("5", "Finalisation", "BOM revision", "Pending", ""),
            ("5", "Finalisation", "Care label revision", "Pending", "")
        ]
        for box, phase, task, status, dt in tasks:
            cursor.execute("INSERT INTO project_checklist (project_id, box_num, phase, task, status, last_update) VALUES (?, ?, ?, ?, ?, ?)", 
                           (default_id, box, phase, task, status, dt))
            
    conn.commit()
    conn.close()

initialize_db()

# ==========================================
# 2. MAIN HEADER & PROJ MANAGER
# ==========================================
st.title("📋 Technical Product Certification System")

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
                        cursor.execute("INSERT INTO projects (project_name, article_number, model_no, bom_status) VALUES (?, '', '', '')", (p_name,))
                        p_id = cursor.lastrowid
                        cursor.execute("SELECT box_num, phase, task, status, last_update FROM project_checklist WHERE project_id = 1")
                        template = cursor.fetchall()
                        for b, ph, tk, st_t, dt_t in template:
                            cursor.execute("INSERT INTO project_checklist (project_id, box_num, phase, task, status, last_update) VALUES (?, ?, ?, ?, ?, ?)", (p_id, b, ph, tk, "Pending", ""))
                        conn.commit()
                        st.success("Project generated!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Project name already exists.")

if not df_projects.empty and selected_project != "No projects found":
    df_filtered_proj = df_projects[df_projects["project_name"] == selected_project]
    if not df_filtered_proj.empty:
        proj_row = df_filtered_proj.iloc[0]
        active_project_id = int(proj_row["id"])
    else: active_project_id = 0
else: active_project_id = 0

if active_project_id > 0:
    with st.expander("📝 Edit Project Header Fields (Articles, Model, BOM)", expanded=False):
        with st.form("edit_project_header"):
            col_h1, col_h2, col_h3 = st.columns(3)
            h_article = col_h1.text_input("Article Number", value=proj_row["article_number"])
            h_model = col_h2.text_input("Model No.", value=proj_row["model_no"])
            h_bom = col_h3.text_input("BOM Status", value=proj_row["bom_status"])
            if st.form_submit_button("Save Header Records"):
                cursor = conn.cursor()
                cursor.execute("UPDATE projects SET article_number=?, model_no=?, bom_status=? WHERE id=?", (h_article, h_model, h_bom, active_project_id))
                conn.commit()
                st.success("Header records updated!")
                st.rerun()

df_checklist = pd.read_sql_query(f"SELECT * FROM project_checklist WHERE project_id = {active_project_id}", conn)
df_components = pd.read_sql_query(f"SELECT * FROM production_components WHERE project_id = {active_project_id}", conn)
conn.close()

detailed_categories = ["Fabric", "Zipper", "Lining", "Elastic", "Button", "Thread", "Reflex", "Velcro"]
today = date.today()

# ==========================================
# 3. SEPARATED BOX CODE IMPLEMENTATION
# ==========================================
st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 BOX 1: Expiry & Add", 
    "📑 BOX 2: Documentation", 
    "🛠️ BOX 3: Database Logs", 
    "👕 BOX 4: Samples & Mock-ups", 
    "🏁 BOX 5: Finalisation"
])

# --- 1️⃣ INDEPENDENT BOX 1 CODE ---
with tab1:
    st.header("1️⃣ BOX 1: Certificate Expiry Control")
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
        st.markdown("#### 📥 Add New Certification Record / Protocol Data")
        c1, c2, c3 = st.columns(3)
        with c1:
            c_cat = st.selectbox("Component Option", detailed_categories, key="b1_cat")
            c_name = st.text_input("Item Specification / Name", key="b1_name")
        with c2:
            c_type = st.selectbox("Protocol/Doc Type", ["New Certification", "Application for extension", "Re-certification", "OEKO-Tex Standard 100", "Test Report Fabric", "Test Report Accessories"], key="b1_type")
            c_num = st.text_input("Certificate / Report Unique ID", key="b1_num")
        with c3:
            c_exp = st.date_input("Document Expiry Date", today, key="b1_date")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save Item Validity Data"):
                if c_name and active_project_id > 0:
                    conn = connect_db()
