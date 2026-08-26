import streamlit as st
import datetime
import sqlite3
import json

# Configuração Principal do Programa
st.set_page_config(page_title="Certification Checklist", layout="wide")
st.title("📋 Certification Checklist Program")

# 1. INICIALIZAÇÃO DE MEMÓRIA GLOBAL (Garante estabilidade ao mudar de aba)
if 'materials_list' not in st.session_state:
    st.session_state.materials_list = []
if 'sizes_history' not in st.session_state:
    st.session_state.sizes_history = []
if 'institute_shipments' not in st.session_state:
    st.session_state.institute_shipments = []
if 'mockups_v2_history' not in st.session_state:
    st.session_state.mockups_v2_history = []

status_options = [
    "NO NEED", 
    "IN PROGRESS ", 
    "GREEN / OK "
]

# CRIAÇÃO DOS VALORES PADRÃO DA SESSÃO
if 'project_name' not in st.session_state: st.session_state.project_name = "Project Alpha"
if 'folder_number' not in st.session_state: st.session_state.folder_number = "F-2026-001"
if 'model_name' not in st.session_state: st.session_state.model_name = "Standard V1"
if 'article_name_t1' not in st.session_state: st.session_state.article_name_t1 = "Premium Cotton Fabric"
if 'cert_type' not in st.session_state: st.session_state.cert_type = "NEW CERTIFICATION"
if 'inst_oeti' not in st.session_state: st.session_state.inst_oeti = False
if 'inst_testex' not in st.session_state: st.session_state.inst_testex = False
if 'inst_hohenstein' not in st.session_state: st.session_state.inst_hohenstein = False
if 'add_bom' not in st.session_state: st.session_state.add_bom = False
if 'bom_notes' not in st.session_state: st.session_state.bom_notes = ""

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today:
        return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1:
        return "🟨 WARNING: Expires Tomorrow!", "warning"
    else:
        return "🟩 Valid Document", "success"

# --- ESTRUTURA DAS 6 ABAS NA TELA ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents ", "3. Technical Documentation", 
    "4. Sample Garment ", "5. Sample Mockups ", "6. Preview & Finalisation"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value=st.session_state.project_name, key="t1_p_name")
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value=st.session_state.folder_number, key="t1_f_num")
    model_name = st.text_input("MODEL", value=st.session_state.model_name, key="t1_m_name")
    article_name_t1 = st.text_input("ARTICLE", value=st.session_state.article_name_t1, key="t1_art")
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"], key="t1_cert")
    
    st.markdown("---")
    st.subheader("🏛️ TARGET CERTIFICATION INSTITUTE")
    inst_oeti = st.checkbox("OETI", value=st.session_state.inst_oeti, key="t1_oeti")
    inst_testex = st.checkbox("TESTEX", value=st.session_state.inst_testex, key="t1_testex")
    inst_hohenstein = st.checkbox("HOHENSTEIN", value=st.session_state.inst_hohenstein, key="t1_hoh")
    
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)", value=st.session_state.add_bom, key="t1_add_bom")
    bom_notes = st.text_area("BOM NOTES / REVISIONS (e.g., BOM 1 for main fabric, BOM 2 for lining)", value=st.session_state.bom_notes, key="t1_bom_notes")

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    st.subheader("Add Material Item")
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"], key="t2_mat_type")
    doc_art_name = st.text_input("ARTICLE NAME (for this material)", value=article_name_t1, key="t2_art_name")
    doc_art_num = st.text_input("ARTICLE NUMBER", value="ART-9922", key="t2_art_num")
    
    col1, col2 = st.columns(2)
    with col1: oekotex = st.checkbox("OEKO-TEX Compliance", key="t2_oeko")
    with col2: text_report = st.checkbox("TEXT REPORT Attached", key="t2_report")
    
    expiration_date = st.date_input("EXPIRATION DATE", datetime.date.today() + datetime.timedelta(days=2), key="t2_exp_date")
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
        st.dataframe(st.session_state.materials_list, use_container_width=True)
        if st.button("🗑️ Clear Materials List", key="t2_clear_btn"):
            st.session_state.materials_list = []
            st.rerun()

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
        if st.button("➕ Add Size Entry", key="t4_add_sz_btn"):
            st.session_state.sizes_history.append({"Order Number": input_order_num, "Qty": input_size_qty, "Size": input_size, "Date": str(input_size_date)})
            st.success("Size log entry recorded!")

    with col_ship:
        st.subheader("🚚 Institute Shipment ")
        ship_order = st.text_input("ORDER NUMBER", value="ORD-2026", key="t4_sh_ord")
        ship_qty = st.number_input("QUANTITY SENT", min_value=1, value=1, key="t4_sh_qty")
        ship_size = st.text_input("SIZE", value="L", key="t4_sh_sz")
        ship_fabric = st.text_input("MAIN FABRIC", value="100% Polyester", key="t4_sh_fab")
        ship_date = st.date_input("SHIPMENT DATE", datetime.date.today(), key="t4_sh_dt")
        ship_status = st.selectbox("APPROVAL STATUS", ["PENDING / EM AVALIAÇÃO", "🟩 APPROVED", "🟥 NOT APPROVED"], key="t4_sh_st")
        if st.button("➕ Add Shipment to Institute", key="t4_add_sh_btn"):
            st.session_state.institute_shipments.append({"Order": ship_order, "Qty Sent": ship_qty, "Size": ship_size, "Main Fabric": ship_fabric, "Date": str(ship_date), "Status": ship_status})
            st.success("Shipment registered successfully!")

    st.markdown("---")
    st.subheader("📋 Production History")
    if st.session_state.sizes_history:
        st.dataframe(st.session_state.sizes_history, use_container_width=True)
        if st.button("🗑️ Clear Size History", key="t4_clear_sz"):
            st.session_state.sizes_history = []
            st.rerun()

    st.markdown("---")
    st.subheader("🚚 History of Registered Institute Shipments")
    if st.session_state.institute_shipments:
        total_pieces_sent = sum(item["Qty Sent"] for item in st.session_state.institute_shipments)
        st.metric(label="📊 Total Pieces Sent to Institutes", value=f"{total_pieces_sent} units")
        st.dataframe(st.session_state.institute_shipments, use_container_width=True)
        if st.button("🗑️ Clear Shipment History", key="t4_clear_sh"):
            st.session_state.institute_shipments = []
            st.rerun()

# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Configuration & Tracking")
    col_mock1, col_mock2 = st.columns(2)
    
    with col_mock1:
        st.subheader("📝 Mockup Production Details")
        mockup_article = st.text_input("ARTICLE OF MOCKUPS", value="Mock-UX Fabric", key="m5_art")
        mock_order_num = st.text_input("ORDER NUMBER", value="ORD-2026", key="m5_ord")
        fabric_used = st.text_input("FABRIC USED (Tecidos)", value="Cotton Blend 230g", key="m5_fab")
