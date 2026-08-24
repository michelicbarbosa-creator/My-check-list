import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="OEKO-Tex & Production Technical Manager 2026")

# ==========================================
# 1. DATABASE CONNECTION & CREATION (SQLITE)
# ==========================================
def connect_db():
    return sqlite3.connect("certification_manager_v6.db")

def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()
    
    # New Table: Projects List
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT UNIQUE
        )
    """)
    
    # Table 2: Checklist associated with a specific project
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            project_id INTEGER,
            phase TEXT, task TEXT, status TEXT
        )
    """)
    
    # Table 3: Components associated with a specific project
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            category TEXT, material_name TEXT, doc_type TEXT, certificate_num TEXT, expiry_date TEXT,
            mockup_status TEXT, mockup_approved TEXT, production_order TEXT, related_articles TEXT,
            seam_ready_qty INTEGER, seam_sent_oeti_qtd INTEGER, comments TEXT
        )
    """)
    
    # Insert default project if database is completely new
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone() == 0:
        cursor.execute("INSERT INTO projects (project_name) VALUES (?)", ("35.1a-d winter + rain parkas",))
        default_id = cursor.lastrowid
        
        tasks = [
            ("Documentation", "Application form OETI", "Pending"),
            ("Documentation", "Technical document OETI", "Pending"),
            ("Technical documentation", "Technical documentation SPLAG", "Completed"),
            ("Technical documentation", "Measurement chart", "Pending"),
            ("Technical documentation", "Care label", "Pending"),
            ("Sample garment", "Sample in progress", "In Progress"),
            ("Sample garment", "Sample sent to OETI!", "Pending"),
            ("Finalisation", "Technical sheet revision", "Pending"),
            ("Finalisation", "BOM revision", "Pending"),
            ("Finalisation", "Care label revision", "Pending")
        ]
        for phase, task, status in tasks:
            cursor.execute("INSERT INTO project_checklist (project_id, phase, task, status) VALUES (?, ?, ?, ?)", 
                           (default_id, phase, task, status))
            
    conn.commit()
    conn.close()

initialize_db()

# ==========================================
# 2. MULTI-PROJECT SELECTION UPPER BAR
# ==========================================
st.title("📋 Technical Production & Certification Manager")

conn = connect_db()
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)

col_proj1, col_proj2 = st.columns([2, 1])

with col_proj1:
    # Dropdown menu to select the project
    selected_project_name = st.selectbox(
        "Select Active Project", 
        df_projects["project_name"].tolist() if not df_projects.empty else ["No projects found"]
    )

with col_proj2:
    # Option to create a new project on the fly
    with st.popover("➕ Create New Project"):
        with st.form("new_project_form", clear_on_submit=True):
            new_proj_name = st.text_input("New Project Name / Code")
            if st.form_submit_button("Add Project"):
                if new_proj_name:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO projects (project_name) VALUES (?)", (new_proj_name,))
                        new_id = cursor.lastrowid
                        
                        # Clone standard checklist template to the new project
                        tasks_template = [
                            ("Documentation", "Application form OETI", "Pending"),
                            ("Documentation", "Technical document OETI", "Pending"),
                            ("Technical documentation", "Technical documentation SPLAG", "Pending"),
                            ("Technical documentation", "Measurement chart", "Pending"),
                            ("Technical documentation", "Care label", "Pending"),
                            ("Sample garment", "Sample in progress", "Pending"),
                            ("Sample garment", "Sample sent to OETI!", "Pending"),
                            ("Finalisation", "Technical sheet revision", "Pending"),
                            ("Finalisation", "BOM revision", "Pending"),
                            ("Finalisation", "Care label revision", "Pending")
                        ]
                        for phase, task, status in tasks_template:
                            cursor.execute("INSERT INTO project_checklist (project_id, phase, task, status) VALUES (?, ?, ?, ?)", 
                                           (new_id, phase, task, status))
                        conn.commit()
                        st.success(f"Project '{new_proj_name}' created!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("This project name already exists.")

# Fetch active project ID
if not df_projects.empty and selected_project_name != "No projects found":
    active_project_id = int(df_projects[df_projects["project_name"] == selected_project_name]["id"].values[0])
else:
    active_project_id = 0

# Load filtered data for the selected project
df_checklist = pd.read_sql_query(f"SELECT * FROM project_checklist WHERE project_id = {active_project_id}", conn)
df_components = pd.read_sql_query(f"SELECT * FROM production_components WHERE project_id = {active_project_id}", conn)
conn.close()

detailed_categories = ["Fabric", "Reflex", "Elastic", "Button", "Velcro", "Thread", "Zipper"]

# ==========================================
# 3. REAL-TIME EXPIRY CONTROL (ALARM CLOCK)
# ==========================================
today = date.today()
expired_today = []

if not df_components.empty:
    for idx, r in df_components.iterrows():
        try:
            expiry = datetime.strptime(r["expiry_date"], "%Y-%m-%d").date()
            if expiry <= today:
                expired_today.append({
                    "Material": r["material_name"], "Category": r["category"],
                    "Type": r["doc_type"], "Number": r["certificate_num"], "Date": r["expiry_date"]
                })
        except:
            pass

# ==========================================
# 4. SECTION 1: CERTIFICATES & DEADLINES
# ==========================================
st.header("1. Certificate Status & Active Expiry Alerts")
col_quad1, col_quad2 = st.columns(2)

with col_quad1:
    st.markdown("#### 🚨 Active Expiry Alarms by Component Type")
    if expired_today:
        for doc in expired_today:
            st.error(f"⏰ **EXPIRED!** [{doc['Category']}] - The document **{doc['Type']}** ({doc['Number']}) for **{doc['Material']}** expired on {doc['Date']}!")
    else:
        st.success("✅ All certificates for this project are up to date and valid.")

with col_quad2:
    st.markdown("#### 📥 Add New Certificate & Expiry Date")
    with st.popover("➕ Configure New Certificate"):
        with st.form("form_deadlines_english", clear_on_submit=True):
            cat_p = st.selectbox("Select Component Option", detailed_categories)
            nome_p = st.text_input("Material Name / Reference")
            tipo_p = st.selectbox("Document Type", ["OEKO-Tex Standard 100", "Test Report Fabric", "Test Report Accessories"])
            num_p = st.text_input("Certificate / Test Report Number")
            data_p = st.date_input("Expiry Date", today)
            
            if st.form_submit_button("Save Certificate to Database"):
                if nome_p and active_project_id > 0:
                    conn = connect_db()
                    conn.execute("""
                        INSERT INTO production_components (project_id, category, material_name, doc_type, certificate_num, expiry_date, mockup_status, mockup_approved, production_order, related_articles, seam_ready_qty, seam_sent_oeti_qtd, comments)
                        VALUES (?, ?, ?, ?, ?, ?, 'Mock-ups needed', 'Pending', '', '', 0, 0, '')
                    """, (active_project_id, cat_p, nome_p, tipo_p, num_p, str(data_p)))
                    conn.commit()
                    conn.close()
                    st.rerun()

st.markdown("---")

# ==========================================
# 5. SECTION 2: TIMELINE CHECKLIST
# ==========================================
st.header("2. Project Validation Timeline")
c_fase1, c_fase2, c_fase3 = st.columns(3)

with c_fase1:
    st.markdown("#### 📑 Documentation & Tech")
    for idx, r in df_checklist[df_checklist["phase"].isin(["Documentation", "Technical documentation"])].iterrows():
        st.text(f"• [{r['status']}] {r['task']}")

with c_fase2:
    st.markdown("#### 👕 Sample Garment")
    for idx, r in df_checklist[df_checklist["phase"] == "Sample garment"].iterrows():
        st.text(f"• [{r['status']}] {r['task']}")

with c_fase3:
    st.markdown("#### 🏁 Finalisation")
    for idx, r in df_checklist[df_checklist["phase"] == "Finalisation"].iterrows():
        st.text(f"• [{r['status']}] {r['task']}")

st.markdown("---")

# ==========================================
# 6. SECTION 3: MANUFACTURING CONTROL & QUANTITIES
# ==========================================
st.header("3. Manufacturing Control & Seam Samples")

with st.form("form_production_english", clear_on_submit=True):
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("##### 🧵 Sample Mock-up Status")
