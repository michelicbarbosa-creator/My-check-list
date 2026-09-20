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

# NOVA FUNÇÃO: Apaga o projeto do ficheiro da nuvem de forma definitiva
def delete_project_from_db(project_id):
    projects = load_all_projects()
    if project_id in projects:
        del projects[project_id]
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=4, ensure_ascii=False)

# 1. INICIALIZAÇÃO DE MEMÓRIA GLOBAL
if 'materials_list' not in st.session_state: st.session_state.materials_list = []
if 'sizes_history' not in st.session_state: st.session_state.sizes_history = []
if 'institute_shipments' not in st.session_state: st.session_state.institute_shipments = []
if 'mockups_v2_history' not in st.session_state: st.session_state.mockups_v2_history = []

status_options = ["NO NEED", "IN PROGRESS ", "GREEN / OK "]

# VALORES PADRÃO DA SESSÃO
if 'project_name' not in st.session_state: st.session_state.project_name = "Project Alpha"
if 'folder_number' not in st.session_state: st.session_state.folder_number = "F-2026-001"
if 'model_name' not in st.session_state: st.session_state.model_name = "Standard V1"
if 'article_name_t1' not in st.session_state: st.session_state.article_name_t1 = "Premium Cotton Fabric"
if 'cert_type' not in st.session_state: st.session_state.cert_type = "NEW CERTIFICATION"

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today: return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1: return "🟨 WARNING: Expires Tomorrow!", "warning"
    else: return "🟩 Valid Document", "success"

# --- PAINEL DE PESQUISA NA NUVEM (Histórico Atualizado) ---
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
                st.success(f"Loaded: {selected_proj}")
                st.rerun()
                
        with col_side2:
            # BOTÃO DE ELIMINAÇÃO DA NUVEM
            if st.button("🗑️ Delete Cloud"):
                delete_project_from_db(selected_proj)
                st.sidebar.warning(f"Deleted: {selected_proj}")
                st.rerun()
else:
    st.sidebar.info("No projects saved yet.")

# --- ESTRUTURA DAS 6 ABAS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents ", "3. Technical Documentation", 
    "4. Sample Garment ", "5. Sample Mockups ", "6. Preview & Finalisation"
])

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    st.subheader("Add Material Item")
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"], key="t2_mat_type")
    
    # CORREÇÃO: Puxa o valor com segurança da memória global do Streamlit
    default_article_name = st.session_state.get("t1_art", "Premium Cotton Fabric")
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
        st.dataframe(st.session_state.materials_list, use_container_width=True)
        if st.button("🗑️ Clear Materials List", key="t2_clear_btn"):
            st.session_state.materials_list = []

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
        
        input_num_roll_fabric = st.text_input("NUMBER ROLL FABRIC", value="", key="t4_num_roll_fab")
        input_lot_fabric = st.text_input("LOT FABRIC", value="", key="t4_lot_fab")
        input_num_roll_reflex = st.text_input("NUMBER ROLL REFLEX", value="", key="t4_num_roll_ref")

        if st.button("➕ Add Size Entry", key="t4_add_sz_btn"):
            st.session_state.sizes_history.append({
                "Order Number": input_order_num, 
                "Qty": input_size_qty, 
                "Size": input_size, 
                "Date": str(input_size_date),
                "Number Roll Fabric": input_num_roll_fabric, 
                "Lot Fabric": input_lot_fabric, 
                "Number Roll Reflex": input_num_roll_reflex
            })
            st.success("Size log entry recorded!")
            
        if st.session_state.sizes_history:
            # Transformado em data_editor com num_rows="dynamic" para permitir APAGAR linhas da Produção
            edited_sizes = st.data_editor(
                st.session_state.sizes_history, 
                use_container_width=True, 
                num_rows="dynamic",
                key="editable_sizes_table"
            )
            st.session_state.sizes_history = edited_sizes

    with col_ship:
        st.subheader("🚚 Institute Shipment ")
        ship_order = st.text_input("ORDER NUMBER", value="ORD-2026", key="t4_sh_ord")
        ship_qty = st.number_input("QUANTITY SENT", min_value=1, value=1, key="t4_sh_qty")
        ship_size = st.text_input("SIZE", value="L", key="t4_sh_sz")
        ship_fabric = st.text_input("MAIN FABRIC", value="100% Polyester", key="t4_sh_fab")
        ship_date = st.date_input("SHIPMENT DATE", datetime.date.today(), key="t4_sh_dt")
        ship_status = st.selectbox("APPROVAL STATUS", ["PENDING / EM AVALIAÇÃO", "🟩 APPROVED", "🟥 NOT APPROVED"], key="t4_sh_st")
        
        if st.button("➕ Add Shipment to Institute", key="t4_add_sh_btn"):
            st.session_state.institute_shipments.append({
                "Order Number": ship_order, 
                "Qty Sent": ship_qty, 
                "Size": ship_size, 
                "Main Fabric": ship_fabric, 
                "Shipment Date": str(ship_date), 
                "Status": ship_status
            })
            st.success("Shipment entry recorded!")
            
        if st.session_state.institute_shipments:
            # Adicionado num_rows="dynamic" para permitir APAGAR linhas do Envio ao Instituto
            edited_shipments = st.data_editor(
                st.session_state.institute_shipments, 
                use_container_width=True, 
                num_rows="dynamic",
                key="editable_shipments_table"
            )
            st.session_state.institute_shipments = edited_shipments



# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Configuration (V2)")
    st.subheader("Add Mockup Details")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mockup_part = st.text_input("MOCKUP PART / COMPONENT (e.g., Seam, Pocket)", value="Main Seam", key="t5_part")
        mockup_material = st.text_input("MATERIAL USED", value="Reflective Tape Type A", key="t5_mat")
        # NOVO CAMPO: Data de envio do Mockup
        mockup_ship_date = st.date_input("SHIPMENT DATE TO INSTITUTE", datetime.date.today(), key="t5_ship_date")
    with col_m2:
        mockup_qty = st.number_input("MOCKUP QTY", min_value=1, value=1, key="t5_qty")
        mockup_status = st.selectbox("MOCKUP STATUS", status_options, index=1, key="t5_status")
        # NOVO CAMPO: Estado de Aprovação do Mockup
        mockup_approval = st.selectbox("APPROVAL STATUS", ["PENDING / EM AVALIAÇÃO", "🟩 APPROVED", "🟥 NOT APPROVED"], key="t5_approval")
        
    if st.button("➕ Add Mockup to Project", key="t5_add_btn"):
        st.session_state.mockups_v2_history.append({
            "Component/Part": mockup_part,
            "Material": mockup_material,
            "Qty": mockup_qty,
            "Status": mockup_status,
            "Shipment Date": str(mockup_ship_date), # Guarda a nova data
            "Approval": mockup_approval             # Guarda o novo estado
        })
        st.success("Mockup added successfully!")
        
    st.markdown("---")
    st.subheader("📋 Registered Mockups")
    if st.session_state.mockups_v2_history:
        # Transforma a tabela em editável para que possa alterar o Status ou a Aprovação com 2 cliques
        edited_mockups = st.data_editor(st.session_state.mockups_v2_history, use_container_width=True, key="editable_mockups_table")
        st.session_state.mockups_v2_history = edited_mockups
        
        if st.button("🗑️ Clear Mockups List", key="t5_clear_btn"):
            st.session_state.mockups_v2_history = []
# ================= TAB 6: PREVIEW & FINALISATION =================
with tab6:
    st.header("Project Overview & Final Summary")
    
    # --- ESTILIZAÇÃO CSS AVANÇADA E CORRIGIDA PARA IMPRESSÃO ---
    st.markdown(
        """
        <style>
        @media print {
            iframe, button, [data-testid="stSidebar"], header, footer, .stButton, [data-testid="stHeader"] {
                display: none !important;
            }
            @page {
                size: A4 landscape;
                margin: 1.5cm;
            }
            .main .block-container {
                padding-top: 0cm !important;
                padding-bottom: 0cm !important;
                max-width: 100% !important;
            }
            [data-testid="stHorizontalBlock"] {
                display: block !important;
                float: none !important;
                width: 100% !important;
            }
            [data-testid="column"] {
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
                float: none !important;
                padding: 0 !important;
                margin-bottom: 35px !important;
                page-break-inside: avoid;
            }
            .stDataFrame, table {
                width: 100% !important;
                margin-top: 5px !important;
                margin-bottom: 15px !important;
            }
            h1, h2, h3 {
                color: #1E3A8A !important;
                margin-top: 20px !important;
                page-break-after: avoid;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("📌 General Project Info")
    
    # CORREÇÃO CRÍTICA: Lê tudo da memória global com valores padrão de segurança
    p_name_view = st.session_state.get('t1_p_name', 'Project Alpha')
    f_num_view = st.session_state.get('t1_f_num', 'F-2026-001')
    m_name_view = st.session_state.get('t1_m_name', 'Standard V1')
    cert_type_view = st.session_state.get('t1_cert', 'NEW CERTIFICATION')
    
    st.write(f"**Project Name:** {p_name_view}")
    st.write(f"**Folder Number:** {f_num_view}")
    st.write(f"**Model:** {m_name_view}")
    st.write(f"**Type:** {cert_type_view}")
    
    institutes = []
    if st.session_state.get('t1_oeti'): institutes.append("OETI")
    if st.session_state.get('t1_testex'): institutes.append("TESTEX")
    if st.session_state.get('t1_hoh'): institutes.append("HOHENSTEIN")
    st.write(f"**Target Institutes:** {', '.join(institutes) if institutes else 'None Selected'}")
    
    st.markdown("---")
    col_summary1, col_summary2 = st.columns(2)
    
    with col_summary1:
        st.subheader("🗒️ Materials & Expiration Summary")
        if st.session_state.materials_list: 
            st.dataframe(st.session_state.materials_list, use_container_width=True)
        else: 
            st.info("No materials added yet.")
            
        st.subheader("📐 Production Sizes (with Roll Info)")
        if st.session_state.sizes_history: 
            st.dataframe(st.session_state.sizes_history, use_container_width=True)
        else: 
            st.info("No production sizes recorded.")

    with col_summary2:
        st.subheader("🚚 Institute Shipments")
        if st.session_state.institute_shipments: 
            st.dataframe(st.session_state.institute_shipments, use_container_width=True)
        else: 
            st.info("No shipments recorded.")
            
        st.subheader("🎨 Mockups Status")
        if st.session_state.mockups_v2_history: 
            st.dataframe(st.session_state.mockups_v2_history, use_container_width=True)
        else: 
            st.info("No mockups added.")

    st.markdown("---")
    st.subheader("💾 Cloud & Export Options")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    final_data = {
        "project_info": {
            "name": p_name_view,
            "folder": f_num_view,
            "model": m_name_view,
            "certification_type": cert_type_view,
            "institutes": institutes,
            "bom_notes": st.session_state.get('t1_bom_notes', "")
        },
        "materials": st.session_state.materials_list,
        "production_sizes_and_rolls": st.session_state.sizes_history,
        "shipments": st.session_state.institute_shipments,
        "mockups": st.session_state.mockups_v2_history
    }
    
    with col_btn1:
        if st.button("☁️ Save Project to Cloud Database", key="t6_cloud_save"):
            project_id = f"{f_num_view} - {p_name_view}"
            save_project_to_db(project_id, final_data)
            st.success(f"Project '{project_id}' securely stored in Cloud Database!")
            
    with col_btn2:
        if st.button("🖨️ Export PDF / Print Report", key="t6_print_pdf_btn"):
            st.components.v1.html("<script>window.parent.print();</script>", height=0)
            st.info("Opening system print dialog...")
            
    with col_btn3:
        json_string = json.dumps(final_data, indent=4, ensure_ascii=False)
        st.download_button(
            label="📥 Download JSON Backup",
            data=json_string,
            file_name=f"checklist_{f_num_view}.json",
            mime="application/json"
        )
