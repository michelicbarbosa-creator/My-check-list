import streamlit as st
import datetime
import sqlite3
import json

# Configuração Principal do Programa
st.set_page_config(page_title="Certification Checklist", layout="wide")
st.title("📋 Certification Checklist Program")

# 1. INICIALIZAÇÃO DE MEMÓRIA GLOBAL
if 'materials_list' not in st.session_state:
    st.session_state.materials_list = []
if 'sizes_history' not in st.session_state:
    st.session_state.sizes_history = []
if 'institute_shipments' not in st.session_state:
    st.session_state.institute_shipments = []
if 'mockups_history' not in st.session_state:
    st.session_state.mockups_history = []

status_options = [
    "NO NEED", 
    "IN PROGRESS / EM PROCESSO", 
    "GREEN / OK / TERMINADO"
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

# Variáveis padrão de status técnico das outras abas
t_splag, t_confirmed, m_chart, m_check, saved_folder, label_status = status_options, status_options, status_options, status_options, status_options, status_options
s_inprogress, s_revision, s_confirmed, s_sent_oeti, s_excel = status_options, status_options, status_options, status_options, status_options
bom_revision, m_chart_revision, care_label, cert_docs, inspec_report = status_options, status_options, status_options, status_options, status_options

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
    "1. Project Info", "2. Documents (Multi-Material)", "3. Technical Documentation", 
    "4. Sample Garment (3-Sections Log)", "5. Sample Mockups (Dynamic History)", "6. Preview & Finalisation"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value=st.session_state.project_name)
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value=st.session_state.folder_number)
    model_name = st.text_input("MODEL", value=st.session_state.model_name)
    article_name_t1 = st.text_input("ARTICLE", value=st.session_state.article_name_t1)
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"])
    
    st.markdown("---")
    st.subheader("🏛️ TARGET CERTIFICATION INSTITUTE")
    inst_oeti = st.checkbox("OETI", value=st.session_state.inst_oeti)
    inst_testex = st.checkbox("TESTEX", value=st.session_state.inst_testex)
    inst_hohenstein = st.checkbox("HOHENSTEIN", value=st.session_state.inst_hohenstein)
    
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)", value=st.session_state.add_bom)
    bom_notes = st.text_area("BOM NOTES / REVISIONS (e.g., BOM 1 for main fabric, BOM 2 for lining)", value=st.session_state.bom_notes)

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    st.subheader("Add Material Item")
    
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"])
    doc_art_name = st.text_input("ARTICLE NAME (for this material)", value=article_name_t1)
    doc_art_num = st.text_input("ARTICLE NUMBER", value="ART-9922")
    
    col1, col2 = st.columns(2)
    with col1: oekotex = st.checkbox("OEKO-TEX Compliance")
    with col2: text_report = st.checkbox("TEXT REPORT Attached")
    
    expiration_date = st.date_input("EXPIRATION DATE", datetime.date.today() + datetime.timedelta(days=2))
    alert_msg, alert_type = check_expiration(expiration_date)
    
    if alert_type == "error": st.error(alert_msg)
    elif alert_type == "warning": st.warning(alert_msg)
    else: st.success(alert_msg)
    
    if st.button("➕ Add Material to Project List"):
        st.session_state.materials_list.append({
            "type": material, "name": doc_art_name, "number": doc_art_num,
            "oekotex": "YES" if oekotex else "NO", "report": "YES" if text_report else "NO",
            "expiry": str(expiration_date), "status": alert_msg
        })
        st.success(f"Added {material} successfully!")

    st.markdown("---")
    st.subheader("📋 Current Project Materials List")
    if st.session_state.materials_list:
        st.dataframe(st.session_state.materials_list, use_container_width=True)
        if st.button("🗑️ Clear Materials List"):
            st.session_state.materials_list = []
            st.rerun()
    else:
        st.info("No materials added yet.")

# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options, index=0)
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options, index=0)
    m_chart = st.selectbox("MEASUREMENT CHART", status_options, index=0)
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options, index=0)
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options, index=0)
    label_status = st.selectbox("LABEL", status_options, index=0)

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment & Institute Shipment Tracking")
    st.subheader("⚙️ General Checklist Status")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options, index=0)
        s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options, index=0)
    with col_s2:
        s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options, index=0)
        s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options, index=0)
    with col_s3:
        s_excel = st.selectbox("SAMPLE ENTERED IN OVERVIEW (EXCEL)", status_options, index=0)

    st.markdown("---")
    col_sizes, col_ship = st.columns(2)
    
    with col_sizes:
        st.subheader("📦 Production Size Log (Size)")
        input_order_num = st.text_input("ORDER NUMBER (Order No.)", value="ORD-2026", key="sz_ord")
        input_size_qty = st.number_input("QUANTITY (Qty)", min_value=1, value=1, key="sz_qty")
        input_size = st.text_input("SIZE (e.g., M, L, 42)", value="M", key="sz_val")
        input_size_date = st.date_input("PRODUCTION DATE", datetime.date.today(), key="sz_date")
        
        if st.button("➕ Add Size Entry"):
            st.session_state.sizes_history.append({
                "Order Number": input_order_num, "Qty": input_size_qty, "Size": input_size, "Date": str(input_size_date)
            })
            st.success("Size log entry recorded!")

    with col_ship:
        st.subheader("🚚 Institute Shipment Log")
        ship_order = st.text_input("ORDER NUMBER", value="ORD-2026", key="sh_ord")
        ship_qty = st.number_input("QUANTITY SENT", min_value=1, value=1, key="sh_qty")
        ship_size = st.text_input("SIZE", value="L", key="sh_sz")
        ship_fabric = st.text_input("MAIN FABRIC", value="100% Polyester", key="sh_fab")
        ship_date = st.date_input("SHIPMENT DATE", datetime.date.today(), key="sh_dt")
        ship_status = st.selectbox("APPROVAL STATUS", ["PENDING / EM AVALIAÇÃO", "🟩 APPROVED", "🟥 NOT APPROVED"], key="sh_st")

        if st.button("➕ Add Shipment to Institute"):
            st.session_state.institute_shipments.append({
                "Order": ship_order, "Qty Sent": ship_qty, "Size": ship_size, "Main Fabric": ship_fabric, "Date": str(ship_date), "Status": ship_status
            })
            st.success("Shipment registered successfully!")

    st.markdown("---")
    st.subheader("📋 Independent Size History")
    if st.session_state.sizes_history:
        st.dataframe(st.session_state.sizes_history, use_container_width=True)
        if st.button("🗑️ Clear Size History"):
            st.session_state.sizes_history = []
            st.rerun()

    st.markdown("---")
    st.subheader("🚚 History of Registered Institute Shipments")
    if st.session_state.institute_shipments:
        total_pieces_sent = sum(item["Qty Sent"] for item in st.session_state.institute_shipments)
        st.metric(label="📊 Total Pieces Sent to Institutes", value=f"{total_pieces_sent} units")
        st.dataframe(st.session_state.institute_shipments, use_container_width=True)
        if st.button("🗑️ Clear Shipment History"):
            st.session_state.institute_shipments = []
            st.rerun()

# ================= TAB 5: SAMPLE MOCKUPS (ALINHAMENTO TÉCNICO CORRIGIDO) =================
with tab5:
    st.header("Sample Mockups Configuration & Tracking")
    
    col_mock1, col_mock2 = st.columns(2)
    
    with col_mock1:
        st.subheader("📝 Mockup Data Details")
        mockup_article = st.text_input("ARTICLE OF MOCKUPS", value="Mock-UX Fabric")
        mock_order_num = st.text_input("ORDER NUMBER", value="ORD-2026", key="mk_ord")
        fabric_used = st.text_input("FABRIC USED", value="Cotton Blend 230g")
