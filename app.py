import streamlit as st
import datetime
import sqlite3
import io

# Configuração da Página
st.set_page_config(page_title="Certification Checklist Program", layout="wide")
st.title("📋 Certification Checklist Program")

# Inicializar listas na sessão para permitir múltiplos materiais
if 'materials_list' not in st.session_state:
    st.session_state.materials_list = []

# --- OPÇÕES DE CORES DIRETAS PARA AS CAIXAS ---
status_options = [
    "🟥 RED (NOT READY / EM FALTA)", 
    "🟨 YELLOW (IN PROGRESS / EM PROCESSO)", 
    "🟩 GREEN (OK / TERMINADO)"
]

# --- LÓGICA DE ALERTA DE VENCIMENTO ---
def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today:
        return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1:
        return "🟨 WARNING: Expires Tomorrow!", "warning"
    else:
        return "🟩 Valid Document", "success"

# ================= 🧭 NAVEGAÇÃO POR ABAS =================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents (Multi-Material)", "3. Technical Documentation", 
    "4. Sample Garment", "5. Sample Mockups", "6. Preview & Finalisation"
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
            "type": material,
            "name": doc_art_name,
            "number": doc_art_num,
            "oekotex": "YES" if oekotex else "NO",
            "report": "YES" if text_report else "NO",
            "expiry": str(expiration_date),
            "status": alert_msg
        }
        st.session_state.materials_list.append(new_material)
        st.success(f"Added {material} ({doc_art_num}) to the list below!")

    st.markdown("---")
    st.subheader("📋 Current Project Materials List")
    if st.session_state.materials_list:
        for idx, m in enumerate(st.session_state.materials_list):
            st.text(f"[{idx+1}] {m['type']} - Art: {m['name']} ({m['number']}) | OEKO: {m['oekotex']} | Report: {m['report']} | Expires: {m['expiry']} ({m['status']})")
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

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment Tracking")
    s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options, index=0)
    s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options, index=0)
    s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options, index=0)
    s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options, index=0)
    s_excel = st.selectbox("SAMPLE ENTERED IN 'OVERVIEW OF REQUIRED SAMPLE (EXCEL FILE)'", status_options, index=0)
    
    col_made, col_sent = st.columns(2)
    with col_made:
        samples_made = st.number_input("QUANTITY OF SAMPLES MADE", min_value=0, value=1)
        date_made = st.date_input("DATE SAMPLES MADE")
    with col_sent:
        samples_sent = st.number_input("QUANTITY OF SAMPLES SENT TO OETI", min_value=0, value=1)
        date_sent = st.date_input("DATE SAMPLES SENT TO OETI")

# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Details")
    mockup_article = st.text_input("ARTICLE OF MOCKUPS", value="Mock-UX Fabric")
    mockups_ready = st.selectbox("MOCK-UPS READY Status", status_options, index=0)
    
    st.subheader("Fabric Information")
    fabric_used = st.text_input("FABRIC USED")
    roll_number = st.text_input("ROLL NUMBER")
    fabric_number = st.text_input("FABRIC NUMBER")
    date_sent_lab = st.date_input("WHEN WAS IT SENT TO LABORATORY?")

# ================= TAB 6: PREVIEW & FINALISATION =================
with tab6:
    st.header("Live Preview, Database & Document Export")
    bom_revision = st.selectbox("BOM REVISION", status_options, index=0)
    m_chart_revision = st.selectbox("MEASUREMENT CHART REVISION", status_options, index=0)
    care_label = st.selectbox("CARE LABEL", status_options, index=0)
    cert_docs = st.selectbox("CERTIFICATES DOCS ARCHIVE", status_options, index=0)
    inspec_report = st.selectbox("INSPECTION REPORT SAVED IN FOLDER", status_options, index=0)
    
    st.markdown("---")
    st.subheader("👀 Checklist Report Preview (Review before download)")
    
    preview_text = f"""==================================================
CERTIFICATION CHECKLIST LIVE PREVIEW
==================================================
[TAB 1] PROJECT INFO
- Project Name: {project_name}
- Folder Number: {folder_number}
- Model Name: {model_name}
- Certification Type: {cert_type}
- BOM Attached: {"YES" if add_bom else "NO"}
- BOM Notes & Variations: {bom_notes if bom_notes else "None"}

[TAB 2] ADDED MATERIALS"""
    
    if st.session_state.materials_list:
        for idx, m in enumerate(st.session_state.materials_list):
            preview_text += f"\n  ({idx+1}) {m['type']} | Art: {m['name']} | Num: {m['number']} | Expiry: {m['expiry']} ({m['status']})"
    else:
        preview_text += "\n  No material items added to this project."
        
    preview_text += f"""

[TAB 3] TECHNICAL DOCUMENTATION STATUS
- SPLAG: {t_splag}
- Confirmed: {t_confirmed}
- Measurement Chart: {m_chart}
- Measurement Check: {m_check}
- Saved in Folder: {saved_folder}
- Label: {label_status}

[TAB 4] SAMPLE GARMENT TRACKING
- In Progress: {s_inprogress} | Revision Kung: {s_revision}
- Confirmed: {s_confirmed} | Sent OETI: {s_sent_oeti}
- Samples Made Qty: {samples_made} on {date_made}
- Sent to OETI Qty: {samples_sent} on {date_sent}

[TAB 5] SAMPLE MOCKUPS
- Mock-ups Status: {mockups_ready} | Article: {mockup_article}
- Fabric Used: {fabric_used} | Roll: {roll_number} | Fabric Num: {fabric_number}

[TAB 6] FINALISATION
- BOM Revision: {bom_revision} | Chart Revision: {m_chart_revision}
- Care Label: {care_label} | Docs Archive: {cert_docs} | Inspection: {inspec_report}
=================================================="""
    
    st.code(preview_text, language="text")
    
    st.markdown("---")
    col_db, col_csv = st.columns(2)
    
    # 🗄️ BOTÃO 1: GUARDAR NA BASE DE DADOS
    with col_db:
        if st.button("💾 Save Progress to Database"):
            try:
                conn = sqlite3.connect('checklist_database.db')
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, project_name TEXT, folder_number TEXT, material TEXT, saved_at TEXT
                    )
                ''')
                cursor.execute('''
                    INSERT INTO projects (project_name, folder_number, material, saved_at) 
                    VALUES (?, ?, ?, ?)
                ''', (project_name, folder_number, material, str(datetime.datetime.now())))
                conn.commit()
                conn.close()
                st.success("🎉 All checklist items safely saved to the database!")
            except Exception as db_err:
                st.error(f"Database error: {db_err}")

    # 📊 BOTÃO 2: DESCARREGAR DOCUMENTO
    with col_csv:
        st.download_button(
            label="📊 Download Complete Document (TXT/Excel)",
            data=preview_text,
            file_name=f"Full_Report_{folder_number}.txt",
            mime="text/plain"
        )

# ================= 🔍 VISUALIZADOR DA BASE DE DADOS COM FILTRO =================
st.markdown("---")
st.subheader("🔍 Search & Filter Saved Checklists")
search_query = st.text_input("Search by Project Name, Folder Number, or Material Type:", value="")

try:
    conn = sqlite3.connect('checklist_database.db')
