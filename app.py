import streamlit as st
import datetime
import sqlite3
import io

# Configuração da Página
st.set_page_config(page_title="Certification Checklist Program", layout="wide")
st.title("📋 Certification Checklist Program")

# ================= 🗄️ CONFIGURAÇÃO DA BASE DE DADOS =================
def init_db():
    conn = sqlite3.connect('checklist_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT, folder_number TEXT, model_name TEXT, article_name_t1 TEXT, cert_type TEXT, add_bom INTEGER,
            material TEXT, doc_art_name TEXT, doc_art_num TEXT, oekotex INTEGER, text_report INTEGER, expiration_date TEXT,
            t_splag TEXT, t_confirmed TEXT, m_chart TEXT, m_check TEXT, saved_folder TEXT, label_status TEXT,
            s_inprogress TEXT, s_revision TEXT, s_confirmed TEXT, s_sent_oeti TEXT, s_excel TEXT, samples_made INTEGER, date_made TEXT, samples_sent INTEGER, date_sent TEXT,
            mockup_article TEXT, mockups_ready TEXT, fabric_used TEXT, roll_number TEXT, fabric_number TEXT, date_sent_lab TEXT,
            bom_revision TEXT, m_chart_revision TEXT, care_label TEXT, cert_docs TEXT, inspec_report TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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
    "1. Project Info", "2. Documents", "3. Technical Documentation", 
    "4. Sample Garment", "5. Sample Mockups", "6. Finalisation & Database"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value="Project Alpha")
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value="F-2026-001")
    model_name = st.text_input("MODEL", value="Standard V1")
    article_name_t1 = st.text_input("ARTICLE", value="Premium Cotton Fabric")
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"])
    
    # ADD BOM movido para a Aba 1
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)")

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"])
    doc_art_name = st.text_input("ARTICLE NAME (Doc)", value=article_name_t1)
    doc_art_num = st.text_input("ARTICLE NUMBER", value="ART-9922")
    
    col1, col2 = st.columns(2)
    with col1: oekotex = st.checkbox("OEKO-TEX")
    with col2: text_report = st.checkbox("TEXT REPORT")
    
    st.markdown("---")
    expiration_date = st.date_input("EXPIRATION DATE", datetime.date.today() + datetime.timedelta(days=2))
    alert_msg, alert_type = check_expiration(expiration_date)
    if alert_type == "error": st.error(alert_msg)
    elif alert_type == "warning": st.warning(alert_msg)
    else: st.success(alert_msg)

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

# ================= TAB 6: FINALISATION =================
with tab6:
    st.header("Finalisation, Database & Report Export")
    bom_revision = st.selectbox("BOM REVISION", status_options, index=0)
    m_chart_revision = st.selectbox("MEASUREMENT CHART REVISION", status_options, index=0)
    care_label = st.selectbox("CARE LABEL", status_options, index=0)
    cert_docs = st.selectbox("CERTIFICATES DOCS ARCHIVE", status_options, index=0)
    inspec_report = st.selectbox("INSPECTION REPORT SAVED IN FOLDER", status_options, index=0)
    
    st.markdown("---")
    col_db, col_csv = st.columns(2)
    
    # 🗄️ BOTÃO 1: GUARDAR NA BASE DE DADOS
    with col_db:
        if st.button("💾 Save Progress to Database"):
            conn = sqlite3.connect('checklist_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (
                    project_name, folder_number, model_name, article_name_t1, cert_type, add_bom,
                    material, doc_art_name, doc_art_num, oekotex, text_report, expiration_date,
                    t_splag, t_confirmed, m_chart, m_check, saved_folder, label_status,
                    s_inprogress, s_revision, s_confirmed, s_sent_oeti, s_excel, samples_made, date_made, samples_sent, date_sent,
                    mockup_article, mockups_ready, fabric_used, roll_number, fabric_number, date_sent_lab,
                    bom_revision, m_chart_revision, care_label, cert_docs, inspec_report
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                project_name, folder_number, model_name, article_name_t1, cert_type, int(add_bom),
                material, doc_art_name, doc_art_num, int(oekotex), int(text_report), str(expiration_date),
                t_splag, t_confirmed, m_chart, m_check, saved_folder, label_status,
                s_inprogress, s_revision, s_confirmed, s_sent_oeti, s_excel, samples_made, str(date_made), samples_sent, str(date_sent),
                mockup_article, mockups_ready, fabric_used, roll_number, fabric_number, str(date_sent_lab),
                bom_revision, m_chart_revision, care_label, cert_docs, inspec_report
            ))
            conn.commit()
            conn.close()
            st.success("🎉 All checklist items safely saved to the database!")

    # 📊 BOTÃO 2: GERAR DOCUMENTO DE RELATÓRIO (Formato Excel CSV de Texto)
    with col_csv:
        csv_lines = [
            "CHECKLIST ITEM / FIELD;VALUE / STATUS SELECTED",
            f"Project Name;{project_name}",
            f"Folder Number;{folder_number}",
            f"Model Name;{model_name}",
            f"Certification Type;{cert_type}",
            f"BOM Added (Tab 1);{add_bom}",
            f"Material Type;{material}",
            f"Document Expiration;{expiration_date} ({alert_msg})",
            f"OEKO-TEX Checklist;{oekotex}",
            f"Text Report;{text_report}",
            f"TECH DOC SPLAG;{t_splag}",
            f"TECH DOC CONFIRMED;{t_confirmed}",
            f"MEASUREMENT CHART;{m_chart}",
            f"SAVED IN FOLDER;{saved_folder}",
            f"LABEL STATUS;{label_status}",
            f"SAMPLE IN PROGRESS;{s_inprogress}",
            f"SAMPLE SENT TO OETI;{s_sent_oeti} (Qty: {samples_sent})",
            f"SAMPLES MADE QTY;{samples_made}",
            f"MOCK-UPS READY STATUS;{mockups_ready}",
            f"BOM REVISION;{bom_revision}",
            f"MEASUREMENT CHART REVISION;{m_chart_revision}",
            f"CARE LABEL;{care_label}",
            f"CERTIFICATES ARCHIVE;{cert_docs}"
        ]
        
        csv_data = "\n".join(csv_lines)
        
        st.download_button(
            label="📊 Download Complete Excel Document (CSV)",
            data=csv_data,
            file_name=f"Report_{folder_number}.csv",
            mime="text/csv"
        )

    # ================= 🔍 VISUALIZADOR DA BASE DE DADOS COM FILTRO =================
    st.markdown("---")
    st.subheader("🔍 Search & Filter Saved Checklists")
    
    search_query = st.text_input("Search by Project Name, Folder Number, or Material Type:", value="")
    
    conn = sqlite3.connect('checklist_database.db')
    try:
