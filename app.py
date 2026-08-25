import streamlit as st
import datetime
import sqlite3

# Configuração Principal do Programa
st.set_page_config(page_title="Certification Checklist", layout="wide")
st.title("📋 Certification Checklist Program")

# Inicialização segura das listas dinâmicas em memória
if 'materials_list' not in st.session_state:
    st.session_state.materials_list = []
if 'oeti_shipments' not in st.session_state:
    st.session_state.oeti_shipments = []

status_options = [
    "🟥 NO NEED", 
    "🟨 IN PROGRESS / EM PROCESSO", 
    "🟩 GREEN / OK / TERMINADO"
]

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today:
        return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1:
        return "🟨 WARNING: Expires Tomorrow!", "warning"
    else:
        return "🟩 Valid Document", "success"

# --- ESTRUTURA DAS 7 ABAS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Project Info", "2. Documents (Multi-Material)", "3. Technical Documentation", 
    "4. Sample Garment (Multi-Shipment)", "5. Sample Mockups", "6. Preview Report", "7. Save & Download"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value="Project Alpha")
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value="F-2026-001")
    model_name = st.text_input("MODEL", value="Standard V1")
    article_name_t1 = st.text_input("ARTICLE", value="Premium Cotton Fabric")
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"])
    
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)")
    bom_notes = st.text_area("BOM NOTES / REVISIONS (e.g., BOM 1 for main fabric, BOM 2 for lining)", value="")

# ================= TAB 2: DOCUMENTS (MÚLTIPLOS ITENS) =================
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
        new_material = {
            "type": material, "name": doc_art_name, "number": doc_art_num,
            "oekotex": "YES" if oekotex else "NO", "report": "YES" if text_report else "NO",
            "expiry": str(expiration_date), "status": alert_msg
        }
        st.session_state.materials_list.append(new_material)
        st.success(f"Added {material} ({doc_art_num}) to the checklist!")

    st.markdown("---")
    st.subheader("📋 Current Project Materials List")
    if st.session_state.materials_list:
        st.dataframe(st.session_state.materials_list, use_container_width=True)
        if st.button("🗑️ Clear Materials List"):
            st.session_state.materials_list = []
            st.rerun()
    else:
        st.info("No materials added yet. Fill the form above and click 'Add Material'.")

# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options, index=0)
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options, index=0)
    m_chart = st.selectbox("MEASUREMENT CHART", status_options, index=0)
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options, index=0)
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options, index=0)
    label_status = st.selectbox("LABEL", status_options, index=0)

# ================= TAB 4: SAMPLE GARMENT (MÚLTIPLOS ENVIOS COM APROVAÇÃO) =================
with tab4:
    st.header("Sample Garment Tracking")
    s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options, index=0)
    s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options, index=0)
    s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options, index=0)
    s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options, index=0)
    s_excel = st.selectbox("SAMPLE ENTERED IN 'OVERVIEW OF REQUIRED SAMPLE (EXCEL FILE)'", status_options, index=0)
    
    st.markdown("---")
    st.subheader("Production & OETI Shipment Log")
    col_made, col_log = st.columns(2)
    
    with col_made:
        samples_made = st.number_input("QUANTITY OF SAMPLES MADE", min_value=0, value=1)
        date_made = st.date_input("DATE SAMPLES MADE")
    
    with col_log:
        st.write("Record a specific shipment batch to OETI with its status:")
        shipment_qty = st.number_input("QUANTITY SENT IN THIS BATCH", min_value=1, value=1, key="ship_qty")
        shipment_date = st.date_input("DATE SENT TO OETI", key="ship_date")
        ship_approval = st.selectbox("BATCH APPROVAL STATUS", ["PENDING / IN EVALUATION", "🟩 APPROVED", "🟥 NOT APPROVED"], key="ship_app")
        
        ship_rejection = ""
        if ship_approval == "🟥 NOT APPROVED":
            ship_rejection = st.text_input("Reason for Rejection:", value="", key="ship_rej")
            
        if st.button("➕ Add Shipment to OETI List"):
            status_text = f"{ship_approval}"
            if ship_approval == "🟥 NOT APPROVED" and ship_rejection:
                status_text += f" (Reason: {ship_rejection})"
                
            st.session_state.oeti_shipments.append({
                "qty": shipment_qty, "date": str(shipment_date), "approval": status_text
            })
            st.success(f"Logged shipment batch on {shipment_date}!")

    st.markdown("---")
    st.subheader("🚚 History of Registered OETI Shipments")
    if st.session_state.oeti_shipments:
        st.dataframe(st.session_state.oeti_shipments, use_container_width=True)
        if st.button("🗑️ Clear Shipment History"):
            st.session_state.oeti_shipments = []
            st.rerun()
    else:
        st.info("No shipments registered yet for this project.")

# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Details")
    mockup_article = st.text_input("ARTICLE OF MOCKUPS", value="Mock-UX Fabric")
    mockups_ready = st.selectbox("MOCK-UPS READY Status", status_options, index=0)
    fabric_used = st.text_input("FABRIC USED")
    roll_number = st.text_input("ROLL NUMBER")
    fabric_number = st.text_input("FABRIC NUMBER")
    date_sent_lab = st.date_input("WHEN WAS IT SENT TO LABORATORY?")

# ================= TAB 7: CAMPOS DE FINALIZAÇÃO =================
with tab7:
    st.header("Finalisation & Database Management")
    bom_revision = st.selectbox("BOM REVISION", status_options, index=0)
    m_chart_revision = st.selectbox("MEASUREMENT CHART REVISION", status_options, index=0)
    care_label = st.selectbox("CARE LABEL", status_options, index=0)
    cert_docs = st.selectbox("CERTIFICATES DOCS ARCHIVE", status_options, index=0)
    inspec_report = st.selectbox("INSPECTION REPORT SAVED IN FOLDER", status_options, index=0)

# --- CONSTRUÇÃO DO TEXTO DO RELATÓRIO SEM LOOPS COMPLEXOS DE OUTROS ENVIOS ---
lines = []
lines.append("CERTIFICATION CHECKLIST REPORT\tVALUE / STATUS")
lines.append("==================================================\t====================")
lines.append(f"\n[TAB 1] PROJECT INFO\t")
lines.append(f"Project Name:\t{project_name}")
lines.append(f"Folder Number:\t{folder_number}")
lines.append(f"Model Name:\t{model_name}")
lines.append(f"Article Name:\t{article_name_t1}")
lines.append(f"Certification Type:\t{cert_type}")
lines.append(f"BOM Attached:\t{'YES' if add_bom else 'NO'}")
lines.append(f"BOM Notes & Variations:\t{bom_notes if bom_notes else 'None'}")
lines.append(f"\n[TAB 3] TECHNICAL DOCUMENTATION STATUS\t")
lines.append(f"TECHNICAL DOCUMENTATION SPLAG:\t{t_splag}")
lines.append(f"TECHNICAL DOCUMENTATION CONFIRMED:\t{t_confirmed}")
lines.append(f"MEASUREMENT CHART:\t{m_chart}")
lines.append(f"MEASUREMENT CHECK OF SAMPLE:\t{m_check}")
lines.append(f"SAVED IN FOLDER:\t{saved_folder}")
lines.append(f"LABEL:\t{label_status}")
lines.append(f"\n[TAB 4] SAMPLE GARMENT\t")
lines.append(f"SAMPLE IN PROGRESS:\t{s_inprogress}")
lines.append(f"SAMPLE REVISION AT KUNG:\t{s_revision}")
lines.append(f"SAMPLE CONFIRMED:\t{s_confirmed}")
lines.append(f"SAMPLE SENT TO OETI:\t{s_sent_oeti}")
lines.append(f"SAMPLE ENTERED IN EXCEL FILE:\t{s_excel}")
lines.append(f"Total Samples Made:\t{samples_made} on {date_made}")
lines.append(f"\n[TAB 5] SAMPLE MOCKUPS\t")
lines.append(f"ARTICLE OF MOCKUPS:\t{mockup_article}")
lines.append(f"MOCK-UPS READY Status:\t{mockups_ready}")
lines.append(f"FABRIC USED:\t{fabric_used}")
lines.append(f"ROLL NUMBER:\t{roll_number}")
lines.append(f"FABRIC NUMBER:\t{fabric_number}")
lines.append(f"WHEN WAS IT SENT TO LABORATORY:\t{date_sent_lab}")
lines.append(f"\n[TAB 6 & 7] FINALISATION\t")
lines.append(f"BOM REVISION:\t{bom_revision}")
lines.append(f"MEASUREMENT CHART REVISION:\t{m_chart_revision}")
lines.append(f"CARE LABEL:\t{care_label}")
lines.append(f"CERTIFICATES DOCS ARCHIVE:\t{cert_docs}")
lines.append(f"INSPECTION REPORT SAVED IN FOLDER:\t{inspec_report}")
lines.append("==================================================\t====================")

preview_text = "\n".join(lines)

# ================= TAB 6: PREVIEW REPORT (EXCLUSIVA) =================
with tab6:
