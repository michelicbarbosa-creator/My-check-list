import streamlit as st
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# Configuração da Página
st.set_page_config(page_title="Certification Checklist Program", layout="wide")
st.title("📋 Certification Checklist Program")

# Inicializar estados para salvar os dados na sessão
if 'project_data' not in st.session_state:
    st.session_state.project_data = {}

# --- FUNÇÃO AUXILIAR PARA COR DE STATUS ---
def get_status_color(status):
    if status == "OK / TERMINADO": return "🟩 GREEN"
    if status == "IN PROGRESS / EM PROCESSO": return "🟨 YELLOW"
    return "🟥 RED (NOT READY / EM FALTA)"

# --- FUNÇÃO PARA ALERTA DE VENCIMENTO (ABA 2) ---
def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today:
        return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1:
        return "🟨 WARNING: Expires Tomorrow!", "warning"
    else:
        return "🟩 Valid", "success"

# ----------------- NAVEGAÇÃO POR ABAS -----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", 
    "2. Documents", 
    "3. Technical Documentation", 
    "4. Sample Garment", 
    "5. Sample Mockups", 
    "6. Finalisation"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value="Project Alpha")
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value="F-2026-001")
    model_name = st.text_input("MODEL", value="Standard V1")
    article_name_t1 = st.text_input("ARTICLE", value="Premium Cotton Fabric")
    
    cert_type = st.radio(
        "CERTIFICATION TYPE",
        ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"]
    )

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    
    # Seleção de tipo de material
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"])
    doc_art_name = st.text_input("ARTICLE NAME (Doc)", value=article_name_t1)
    doc_art_num = st.text_input("ARTICLE NUMBER", value="ART-9922")
    
    # Opções adicionais
    col1, col2, col3 = st.columns(3)
    with col1: oekotex = st.checkbox("OEKO-TEX")
    with col2: text_report = st.checkbox("TEXT REPORT")
    with col3: add_bom = st.checkbox("ADD BOM")
    
    # Controle de Vencimento
    expiration_date = st.date_input("EXPIRATION DATE", datetime.date.today() + datetime.timedelta(days=2))
    alert_msg, alert_type = check_expiration(expiration_date)
    
    if alert_type == "error": st.error(alert_msg)
    elif alert_type == "warning": st.warning(alert_msg)
    else: st.success(alert_msg)

# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    status_options = ["NOT READY / EM FALTA", "IN PROGRESS / EM PROCESSO", "OK / TERMINADO"]
    
    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options)
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options)
    m_chart = st.selectbox("MEASUREMENT CHART", status_options)
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options)
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options)
    label_status = st.selectbox("LABEL", status_options)
    
    # Exibição visual de cores rápida
    st.write(f"SPLAG: {get_status_color(t_splag)} | Confirmed: {get_status_color(t_confirmed)} | Folder: {get_status_color(saved_folder)}")

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment Tracking")
    
    s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options)
    s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options)
    s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options)
    s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options)
    s_excel = st.selectbox("SAMPLE ENTERED IN 'OVERVIEW OF REQUIRED SAMPLE (EXCEL FILE)'", status_options)
    
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
    mockups_ready = st.selectbox("MOCK-UPS READY Status", status_options)
    
    st.subheader("Fabric Information")
    fabric_used = st.text_input("FABRIC USED")
    roll_number = st.text_input("ROLL NUMBER")
    fabric_number = st.text_input("FABRIC NUMBER")
    date_sent_lab = st.date_input("WHEN WAS IT SENT TO LABORATORY?")
    
    st.write(f"Mockups Readiness: {get_status_color(mockups_ready)}")

# ================= TAB 6: FINALISATION =================
with tab6:
    st.header("Finalisation & PDF Export")
    
    bom_revision = st.selectbox("BOM REVISION", status_options)
    m_chart_revision = st.selectbox("MEASUREMENT CHART REVISION", status_options)
    care_label = st.selectbox("CARE LABEL", status_options)
    cert_docs = st.selectbox("CERTIFICATES DOCS ARCHIVE", status_options)
    inspec_report = st.selectbox("INSPECTION REPORT SAVED IN FOLDER", status_options)
    
    st.markdown("---")
    
    # Compilar dados para gerar o relatório
    if st.button("Generate Final Certification Report (PDF)"):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph(f"<b>Certification Report: {project_name}</b>", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Folder Number: {folder_number}", styles['Normal']))
        story.append(Paragraph(f"Certification Type: {cert_type}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Tab 3 Status - SPLAG:</b> {t_splag}", styles['Normal']))
        story.append(Paragraph(f"<b>Tab 4 Status - Sent to OETI:</b> {s_sent_oeti} ({samples_sent} sent)", styles['Normal']))
        story.append(Paragraph(f"<b>Tab 6 Status - Care Label:</b> {care_label}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        st.success("PDF report compiled successfully!")
        st.download_button(
            label="📥 Download PDF Certification Document",
            data=buffer,
            file_name=f"Report_{project_name}.pdf",
            mime="application/pdf"
        )
