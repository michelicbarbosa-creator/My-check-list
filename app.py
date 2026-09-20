import streamlit as st
import datetime
import sqlite3
import json
import os

# Configuração Principal do Programa
st.set_page_config(page_title="Certification Checklist", layout="wide")
st.title("📋 Certification Checklist Program")

# BANCO DE DADOS LOCAL/NUVEM SIMPLIFICADO
DB_FILE = "projects_database.json"

def load_all_projects():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_project_to_db(project_id, data):
    projects = load_all_projects()
    projects[project_id] = data
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=4, ensure_ascii=False)

def delete_project_from_db(project_id):
    projects = load_all_projects()
    if project_id in projects:
        del projects[project_id]
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=4, ensure_ascii=False)

# 1. INICIALIZAÇÃO DE MEMÓRIA GLOBAL COM VALORES PADRÃO SEGUROS
if 'materials_list' not in st.session_state: st.session_state.materials_list = []
if 'sizes_history' not in st.session_state: st.session_state.sizes_history = []
if 'institute_shipments' not in st.session_state: st.session_state.institute_shipments = []
if 'mockups_v2_history' not in st.session_state: st.session_state.mockups_v2_history = []

if 't1_p_name' not in st.session_state: st.session_state['t1_p_name'] = "Project Alpha"
if 't1_f_num' not in st.session_state: st.session_state['t1_f_num'] = "F-2026-001"
if 't1_m_name' not in st.session_state: st.session_state['t1_m_name'] = "Standard V1"
if 't1_art' not in st.session_state: st.session_state['t1_art'] = "Premium Cotton Fabric"
if 't1_bom_notes' not in st.session_state: st.session_state['t1_bom_notes'] = ""

# Suas opções customizadas mantidas aqui:
status_options = ["NO ", "IN PROGRESS ", " OK "]

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today: return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1: return "🟨 WARNING: Expires Tomorrow!", "warning"
    else: return "🟩 Valid Document", "success"

# --- PAINEL DE PESQUISA NA NUVEM (Histórico) ---
st.sidebar.header("🔍 Search & Load Project")
all_saved_projects = load_all_projects()
if all_saved_projects:
    search_options = ["-- Select a Project --"] + list(all_saved_projects.keys())
    selected_proj = st.sidebar.selectbox("Saved Projects", search_options)
    
    if selected_proj != "-- Select a Project --":
        col_side1, col_side2 = st.sidebar.columns(2)
        
        with col_side1:
            if st.button("📂 Load Project"):
                p_data = all_saved_projects[selected_proj]
                st.session_state.materials_list = p_data.get("materials", [])
                st.session_state.sizes_history = p_data.get("production_sizes_and_rolls", [])
                st.session_state.institute_shipments = p_data.get("shipments", [])
                st.session_state.mockups_v2_history = p_data.get("mockups", [])
                
                info = p_data.get("project_info", {})
                st.session_state['t1_p_name'] = info.get("name", " ")
                st.session_state['t1_f_num'] = info.get("folder", " ")
                st.session_state['t1_m_name'] = info.get("model", " ")
                st.session_state['t1_art'] = info.get("article_name_t1", " ")
                st.session_state['t1_cert'] = info.get("certification_type", " ")
                st.session_state['t1_bom_notes'] = info.get("bom_notes", "")
                
                st.success(f"Loaded: {selected_proj}")
                st.rerun()
                
        with col_side2:
            if st.button("🗑️ Delete Cloud"):
                delete_project_from_db(selected_proj)
                st.sidebar.warning(f"Deleted: {selected_proj}")
                st.rerun()
else:
    st.sidebar.info("No projects saved in cloud database yet.")

if st.sidebar.button("➕ Start New Project Blank"):
    st.session_state.materials_list = []
    st.session_state.sizes_history = []
    st.session_state.institute_shipments = []
    st.session_state.mockups_v2_history = []
    st.session_state['t1_p_name'] = ""
    st.session_state['t1_f_num'] = ""
    st.session_state['t1_m_name'] = ""
    st.session_state['t1_art'] = ""
    st.session_state['t1_bom_notes'] = ""
    st.rerun()

# --- ESTRUTURA DAS 6 ABAS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents ", "3. Technical Documentation", 
    "4. Sample Garment ", "5. Sample Mockups ", "6. Preview & Finalisation"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    
    project_name = st.text_input("PROJECT NAME", value=st.session_state['t1_p_name'], key="t1_p_name_input")
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value=st.session_state['t1_f_num'], key="t1_f_num_input")
    model_name = st.text_input("MODEL", value=st.session_state['t1_m_name'], key="t1_m_name_input")
    article_name_t1 = st.text_input("ARTICLE", value=st.session_state['t1_art'], key="t1_art_input")
    
    st.session_state['t1_p_name'] = project_name
    st.session_state['t1_f_num'] = folder_number
    st.session_state['t1_m_name'] = model_name
    st.session_state['t1_art'] = article_name_t1
    
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"], key="t1_cert")
    
    st.markdown("---")
    st.subheader("🏛️ TARGET CERTIFICATION INSTITUTE")
    inst_oeti = st.checkbox("OETI", key="t1_oeti")
    inst_testex = st.checkbox("TESTEX", key="t1_testex")
    inst_hohenstein = st.checkbox("HOHENSTEIN", key="t1_hoh")
    
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)", key="t1_add_bom")
    bom_notes = st.text_area("BOM NOTES / REVISIONS", value=st.session_state['t1_bom_notes'], key="t1_bom_notes_input")
    st.session_state['t1_bom_notes'] = bom_notes

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    st.subheader("Add Material Item")
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"], key="t2_mat_type")
    
    default_article_name = st.session_state.get("t1_art", "")
    doc_art_name = st.text_input("ARTICLE NAME (for this material)", value=default_article_name, key="t2_art_name")
    doc_art_num = st.text_input("ARTICLE NUMBER", value="ART-9922", key="t2_art_num")
    
    col1, col2 = st.columns(2)
    with col1: oekotex = st.checkbox("OEKO-TEX Compliance", key="t2_oeko")
    with col2: text_report = st.checkbox("TEXT REPORT Attached", key="t2_report")
    
    expiration_date = st.date_input("EXPIRATION DATE", value=datetime.date.today() + datetime.timedelta(days=2), key="t2_exp_date")
    alert_msg, alert_type = check_expiration(expiration_date)
    
    if alert_type == "error": st.error(alert_msg)
    elif alert_type == "warning": st.warning(alert_msg)
    else: st.success(alert_msg)
    
    if st.button("➕ Add Material to Project List", key="t2_add_btn"):
        st.session_state.materials_list.append({
            "type": material, "name": doc_art_name, "number": doc_art_num,
            "oekotex": "YES" if oekotex else "NO", "report": "YES" if text_report else "NO",
            "expiry": str(expiration_date), "status": alert_msg
        })
        st.success("Material added successfully!")

    st.markdown("---")
    st.subheader("📋  Project Materials List")
    if st.session_state.materials_list:
        edited_materials = st.data_editor(st.session_state.materials_list, use_container_width=True, num_rows="dynamic", key="editable_materials_table")
        st.session_state.materials_list = edited_materials

# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options, index=0, key="t3_splag")
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options, index=0, key="t3_conf")
    m_chart = st.selectbox("MEASUREMENT CHART", status_options, index=0, key="t3_chart")
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options, index=0, key="t3_check")
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options, index=0, key="t3_folder")
    label_status = st.selectbox("LABEL", status_options, index=0, key="t3_label")

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment ")
    st.subheader("⚙️ General Checklist Status")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options, index=0, key="t4_in_prog")
        s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options, index=0, key="t4_rev")
    with col_s2:
        s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options, index=0, key="t4_conf")
        s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options, index=0, key="t4_sent")
    with col_s3:
        s_excel = st.selectbox("SAMPLE ENTERED IN OVERVIEW (EXCEL)", status_options, index=0, key="t4_excel")

    st.markdown("---")
    col_sizes, col_ship = st.columns(2)
    
    with col_sizes:
        st.subheader("📦 Production ")
        input_order_num = st.text_input("ORDER NUMBER (Order No.)", value="ORD-2026", key="t4_sz_ord")
        input_size_qty = st.number_input("QUANTITY (Qty)", min_value=1, value=1, key="t4_sz_qty")
        input_size = st.text_input("SIZE (e.g., M, L, 42)", value="M", key="t4_sz_val")
        input_size_date = st.date_input("PRODUCTION DATE", datetime.date.today(), key="t4_sz_date")
        
