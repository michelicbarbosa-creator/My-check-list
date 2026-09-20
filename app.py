import streamlit as st
import datetime
import sqlite3
import json
import os

# Configuração Principal do Programa com Identidade SPILAG
st.set_page_config(page_title="SPILAG - Certification Checklist", layout="wide")

# ESTILIZAÇÃO VISUAL CORPORATIVA (Vermelho SPILAG #E32119 e Azul SPILAG #00519E)
st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #E32119 !important;
        border-bottom-color: #E32119 !important;
    }
    h1, h2, h3 {
        color: #00519E !important;
    }
    div.stButton > button:first-child {
        background-color: #00519E;
        color: white;
        border-radius: 6px;
    }
    div.stButton > button:first-child:hover {
        background-color: #E32119;
        color: white;
        border-color: #E32119;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibição do Logo no Topo Centralizado
col_logo_1, col_logo_2, col_logo_3 = st.columns([1,2,1])
with col_logo_2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.write("<h2 style='text-align:center; color:#E32119;'>🔺 SPILAG AG</h2>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: -10px;'>📋 Certification Checklist Program</h1>", unsafe_allow_html=True)

# BANCO DE DADOS LOCAL/NUVEM SIMPLIFICADO
DB_FILE = "projects_database.json"

def load_all_projects():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
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

# 1. INICIALIZAÇÃO DE MEMÓRIA GLOBAL TOTALMENTE EM BRANCO
if 'generation_id' not in st.session_state: st.session_state['generation_id'] = 0
if 'materials_list' not in st.session_state: st.session_state.materials_list = []
if 'sizes_history' not in st.session_state: st.session_state.sizes_history = []
if 'institute_shipments' not in st.session_state: st.session_state.institute_shipments = []
if 'mockups_v2_history' not in st.session_state: st.session_state.mockups_v2_history = []

if 't1_p_name' not in st.session_state: st.session_state['t1_p_name'] = ""
if 't1_f_num' not in st.session_state: st.session_state['t1_f_num'] = ""
if 't1_m_name' not in st.session_state: st.session_state['t1_m_name'] = ""
if 't1_art' not in st.session_state: st.session_state['t1_art'] = ""
if 't1_bom_notes' not in st.session_state: st.session_state['t1_bom_notes'] = ""

status_options = ["NO ", "IN PROGRESS ", " OK "]

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today: return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1: return "🟨 WARNING: Expires Tomorrow!", "warning"
    else: return "🟩 Valid Document", "success"

# --- PAINEL DE PESQUISA NA NUVEM ---
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
                st.session_state['t1_p_name'] = info.get("name", "")
                st.session_state['t1_f_num'] = info.get("folder", "")
                st.session_state['t1_m_name'] = info.get("model", "")
                st.session_state['t1_art'] = info.get("article_name_t1", "")
                st.session_state['t1_cert'] = info.get("certification_type", "NEW CERTIFICATION")
                st.session_state['t1_bom_notes'] = info.get("bom_notes", "")
                
                st.session_state['t1_oeti'] = "OETI" in info.get("institutes", [])
                st.session_state['t1_testex'] = "TESTEX" in info.get("institutes", [])
                st.session_state['t1_hoh'] = "HOHENSTEIN" in info.get("institutes", [])
                st.session_state['t1_add_bom'] = info.get("add_bom", False)
                
                tech = p_data.get("technical_documentation", {})
                st.session_state['t3_splag'] = tech.get("splag", "NO ")
                st.session_state['t3_conf'] = tech.get("confirmed", "NO ")
                st.session_state['t3_chart'] = tech.get("measurement_chart", "NO ")
                st.session_state['t3_check'] = tech.get("measurement_check", "NO ")
                st.session_state['t3_folder'] = tech.get("saved_folder", "NO ")
                st.session_state['t3_label'] = tech.get("label_status", "NO ")
                
                garment = p_data.get("sample_garment_status", {})
                st.session_state['t4_in_prog'] = garment.get("inprogress", "NO ")
                st.session_state['t4_rev'] = garment.get("revision", "NO ")
                st.session_state['t4_conf'] = garment.get("confirmed", "NO ")
                st.session_state['t4_sent'] = garment.get("sent_oeti", "NO ")
                st.session_state['t4_excel'] = garment.get("entered_excel", "NO ")
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
    st.session_state['t1_oeti'] = False
    st.session_state['t1_testex'] = False
    st.session_state['t1_hoh'] = False
    st.session_state['t1_add_bom'] = False
    st.session_state['generation_id'] += 1
    st.rerun()

gen = st.session_state['generation_id']

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents ", "3. Technical Documentation", 
    "4. Sample Garment ", "5. Sample Mockups ", "6. Preview & Finalisation"
])
# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value=st.session_state['t1_p_name'], key=f"t1_p_name_input_{gen}")
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value=st.session_state['t1_f_num'], key=f"t1_f_num_input_{gen}")
    model_name = st.text_input("MODEL", value=st.session_state['t1_m_name'], key=f"t1_m_name_input_{gen}")
    article_name_t1 = st.text_input("ARTICLE", value=st.session_state['t1_art'], key=f"t1_art_input_{gen}")
    
    st.session_state['t1_p_name'] = project_name
    st.session_state['t1_f_num'] = folder_number
    st.session_state['t1_m_name'] = model_name
    st.session_state['t1_art'] = article_name_t1
    
    cert_idx = ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"].index(st.session_state.get('t1_cert', "NEW CERTIFICATION")) if st.session_state.get('t1_cert', "NEW CERTIFICATION") in ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"] else 0
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"], index=cert_idx, key=f"t1_cert_input_{gen}")
    st.session_state['t1_cert'] = cert_type
    
    st.markdown("---")
    st.subheader("🏛️ TARGET CERTIFICATION INSTITUTE")
    inst_oeti = st.checkbox("OETI", value=st.session_state.get('t1_oeti', False), key=f"t1_oeti_input_{gen}")
    inst_testex = st.checkbox("TESTEX", value=st.session_state.get('t1_testex', False), key=f"t1_testex_input_{gen}")
    inst_hohenstein = st.checkbox("HOHENSTEIN", value=st.session_state.get('t1_hoh', False), key=f"t1_hoh_input_{gen}")
    
    st.session_state['t1_oeti'] = inst_oeti
    st.session_state['t1_testex'] = inst_testex
    st.session_state['t1_hoh'] = inst_hohenstein
    
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)", value=st.session_state.get('t1_add_bom', False), key=f"t1_add_bom_input_{gen}")
    st.session_state['t1_add_bom'] = add_bom
    bom_notes = st.text_area("BOM NOTES / REVISIONS", value=st.session_state['t1_bom_notes'], key=f"t1_bom_notes_input_{gen}")
    st.session_state['t1_bom_notes'] = bom_notes
# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    st.subheader("Add Material Item")
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"], key=f"t2_mat_type_{gen}")
    
    default_article_name = st.session_state.get("t1_art", "")
    doc_art_name = st.text_input("ARTICLE NAME (for this material)", value=default_article_name, key=f"t2_art_name_{gen}")
    doc_art_num = st.text_input("ARTICLE NUMBER", value="", key=f"t2_art_num_{gen}")
    
    col1, col2 = st.columns(2)
    with col1: oekotex = st.checkbox("OEKO-TEX Compliance", key=f"t2_oeko_{gen}")
    with col2: text_report = st.checkbox("TEXT REPORT Attached", key=f"t2_report_{gen}")
    
    expiration_date = st.date_input("EXPIRATION DATE", value=datetime.date.today() + datetime.timedelta(days=2), key=f"t2_exp_date_{gen}")
    alert_msg, alert_type = check_expiration(expiration_date)
    
    if alert_type == "error": st.error(alert_msg)
    elif alert_type == "warning": st.warning(alert_msg)
    else: st.success(alert_msg)
    
    if st.button("➕ Add Material to Project List", key=f"t2_add_btn_{gen}"):
        st.session_state.materials_list.append({
            "type": material, "name": doc_art_name, "number": doc_art_num,
            "oekotex": "YES" if oekotex else "NO", "report": "YES" if text_report else "NO",
            "expiry": str(expiration_date), "status": alert_msg
        })
        st.success("Material added successfully!")

    st.markdown("---")
    st.subheader("📋  Project Materials List")
    edited_materials = st.data_editor(st.session_state.materials_list, use_container_width=True, num_rows="dynamic", key=f"editable_materials_table_{gen}")
    st.session_state.materials_list = edited_materials
# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    def get_status_idx(session_key):
        val = st.session_state.get(session_key, "NO ")
        return status_options.index(val) if val in status_options else 0

    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options, index=get_status_idx('t3_splag'), key=f"t3_splag_input_{gen}")
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options, index=get_status_idx('t3_conf'), key=f"t3_conf_input_{gen}")
    m_chart = st.selectbox("MEASUREMENT CHART", status_options, index=get_status_idx('t3_chart'), key=f"t3_chart_input_{gen}")
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options, index=get_status_idx('t3_check'), key=f"t3_check_input_{gen}")
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options, index=get_status_idx('t3_folder'), key=f"t3_folder_input_{gen}")
    label_status = st.selectbox("LABEL", status_options, index=get_status_idx('t3_label'), key=f"t3_label_input_{gen}")
    
    st.session_state['t3_splag'] = t_splag
    st.session_state['t3_conf'] = t_confirmed
    st.session_state['t3_chart'] = m_chart
    st.session_state['t3_check'] = m_check
    st.session_state['t3_folder'] = saved_folder
    st.session_state['t3_label'] = label_status

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment ")
    st.subheader("⚙️ General Checklist Status")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options, index=get_status_idx('t4_in_prog'), key=f"t4_in_prog_input_{gen}")
        s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options, index=get_status_idx('t4_rev'), key=f"t4_rev_input_{gen}")
    with col_s2:
        s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options, index=get_status_idx('t4_conf'), key=f"t4_conf_input_{gen}")
        s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options, index=get_status_idx('t4_sent'), key=f"t4_sent_input_{gen}")
    with col_s3:
        s_excel = st.selectbox("SAMPLE ENTERED IN OVERVIEW (EXCEL)", status_options, index=get_status_idx('t4_excel'), key=f"t4_excel_input_{gen}")

    st.session_state['t4_in_prog'] = s_inprogress
    st.session_state['t4_rev'] = s_revision
    st.session_state['t4_conf'] = s_confirmed
    st.session_state['t4_sent'] = s_sent_oeti
    st.session_state['t4_excel'] = s_excel

    st.markdown("---")
    col_sizes, col_ship = st.columns(2)
    
    with col_sizes:
        st.subheader("📦 Production ")
        input_order_num = st.text_input("ORDER NUMBER (Order No.)", value="", key=f"t4_sz_ord_{gen}")
        input_size_qty = st.number_input("QUANTITY (Qty)", min_value=1, value=1, key=f"t4_sz_qty_{gen}")
        input_size = st.text_input("SIZE (e.g., M, L, 42)", value="", key=f"t4_sz_val_{gen}")
        input_size_date = st.date_input("PRODUCTION DATE", datetime.date.today(), key=f"t4_sz_date_{gen}")
        
        input_num_roll_fabric = st.text_input("NUMBER ROLL FABRIC", value="", key=f"t4_num_roll_fab_{gen}")
        input_lot_fabric = st.text_input("LOT FABRIC", value="", key=f"t4_lot_fab_{gen}")
        input_num_roll_reflex = st.text_input("NUMBER ROLL REFLEX", value="", key=f"t4_num_roll_ref_{gen}")

        if st.button("➕ Add Size Entry", key=f"t4_add_sz_btn_{gen}"):
            st.session_state.sizes_history.append({
                "Order Number": input_order_num, "Qty": input_size_qty, "Size": input_size, "Date": str(input_size_date),
                "Number Roll Fabric": input_num_roll_fabric, "Lot Fabric": input_lot_fabric, "Number Roll Reflex": input_num_roll_reflex
            })
            st.success("Size log entry recorded!")
            
        edited_sizes = st.data_editor(st.session_state.sizes_history, use_container_width=True, num_rows="dynamic", key=f"editable_sizes_table_{gen}")
        st.session_state.sizes_history = edited_sizes

    with col_ship:
        st.subheader("🚚 Institute Shipment ")
        ship_order = st.text_input("ORDER NUMBER", value="", key=f"t4_sh_ord_{gen}")
        ship_qty = st.number_input("QUANTITY SENT", min_value=1, value=1, key=f"t4_sh_qty_{gen}")
        ship_size = st.text_input("SIZE", value="", key=f"t4_sh_sz_{gen}")
        ship_fabric = st.text_input("MAIN FABRIC", value="", key=f"t4_sh_fab_{gen}")
        ship_date = st.date_input("SHIPMENT DATE", datetime.date.today(), key=f"t4_sh_dt_{gen}")
        ship_status = st.selectbox("APPROVAL STATUS", ["PENDING / EM AVALIAÇÃO", "🟩 APPROVED", "🟥 NOT APPROVED"], key=f"t4_sh_st_{gen}")
        
        if st.button("➕ Add Shipment to Institute", key=f"t4_add_sh_btn_{gen}"):
            st.session_state.institute_shipments.append({
                "Order Number": ship_order, "Qty Sent": ship_qty, "Size": ship_size, "Main Fabric": ship_fabric, "Shipment Date": str(ship_date), "Status": ship_status
            })
            st.success("Shipment entry recorded!")
            
        edited_shipments = st.data_editor(st.session_state.institute_shipments, use_container_width=True, num_rows="dynamic", key=f"editable_shipments_table_{gen}")
        st.session_state.institute_shipments = edited_shipments
# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Configuration (V2)")
    st.subheader("Add Mockup Details")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mockup_part = st.text_input("MOCKUP PART / COMPONENT (e.g., Seam, Pocket)", value="", key=f"t5_part_{gen}")
        mockup_material = st.text_input("MATERIAL USED", value="", key=f"t5_mat_{gen}")
        mockup_ship_date = st.date_input("SHIPMENT DATE TO INSTITUTE", datetime.date.today(), key=f"t5_ship_date_{gen}")
    with col_m2:
        mockup_qty = st.number_input("MOCKUP QTY", min_value=1, value=1, key=f"t5_qty_{gen}")
        mockup_status = st.selectbox("MOCKUP STATUS", status_options, index=1, key=f"t5_status_{gen}")
        mockup_approval = st.selectbox("APPROVAL STATUS", ["PENDING / EM AVALIAÇÃO", "🟩 APPROVED", "🟥 NOT APPROVED"], key=f"t5_approval_{gen}")
        
    if st.button("➕ Add Mockup to Project", key=f"t5_add_btn_{gen}"):
        st.session_state.mockups_v2_history.append({
            "Component/Part": mockup_part, "Material": mockup_material, "Qty": mockup_qty, "Status": mockup_status,
            "Shipment Date": str(mockup_ship_date), "Approval": mockup_approval
        })
        st.success("Mockup added successfully!")
        
    st.markdown("---")
    st.subheader("📋 Registered Mockups")
    edited_mockups = st.data_editor(st.session_state.mockups_v2_history, use_container_width=True, num_rows="dynamic", key=f"editable_mockups_table_{gen}")
    st.session_state.mockups_v2_history = edited_mockups
# ================= TAB 6: PREVIEW & FINALISATION =================
with tab6:
    st.header("Project Overview & Final Summary")
    
    # --- ESTILIZAÇÃO CSS PROFISSIONAL - COMPACTAÇÃO ANTI-QUEBRA DE PÁGINA ---
    st.markdown(
        """
        <style>
        @media print {
            /* 1. Esconde menus de navegação do Streamlit, barras laterais e botões */
            iframe, button, [data-testid="stSidebar"], header, footer, .stButton, [data-testid="stHeader"], [data-testid="stHeaderBlock"] {
                display: none !important;
            }
            /* 2. Configuração da folha com aproveitamento máximo de espaço horizontal */
            @page { 
                size: A4 landscape; 
                margin: 0.6cm !important; 
            }
            /* 3. CORREÇÃO CRÍTICA DO LOGO ISOLADO: Impede quebras de página no topo */
            [data-testid="stImage"], [data-testid="stElementContainer"], .element-container {
                page-break-after: avoid !important;
                page-break-inside: avoid !important;
                display: block !important;
            }
            [data-testid="stImage"] img, img {
                max-width: 140px !important;
                height: auto !important;
                margin: 0 auto !important;
                display: block !important;
            }
            /* 4. Ajuste global do tamanho real mantendo os blocos unidos */
            .main .block-container { 
                padding-top: 0cm !important; 
                padding-bottom: 0cm !important; 
                max-width: 100% !important; 
                transform: scale(0.85) !important; 
                transform-origin: top left !important;
                margin-top: -20px !important; 
            }
            /* 5. Força as tabelas e colunas a empilharem sem saltar de página à toa */
            [data-testid="stHorizontalBlock"] { 
                display: block !important; 
                float: none !important; 
                width: 100% !important; 
                page-break-inside: avoid !important;
                page-break-after: auto !important;
            }
            [data-testid="column"] { 
                display: block !important; 
                width: 100% !important; 
                max-width: 100% !important; 
                float: none !important; 
                padding: 0 !important; 
                margin-bottom: 15px !important; 
                page-break-inside: avoid !important; 
            }
            /* 6. Ajuste compacto das tabelas de dados */
            .stDataFrame, table { 
                width: 100% !important; 
                margin-top: 2px !important; 
                margin-bottom: 5px !important; 
            }
            h1, h2, h3 { 
                color: #00519E !important; 
                margin-top: 8px !important; 
                margin-bottom: 4px !important;
                page-break-after: avoid !important; 
                page-break-before: avoid !important;
            }
            p, span, div, text {
                page-break-inside: avoid !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("📌 General Project Info")
    
    p_name_view = st.session_state.get('t1_p_name', '')
    f_num_view = st.session_state.get('t1_f_num', '')
    m_name_view = st.session_state.get('t1_m_name', '')
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
        if st.session_state.materials_list: st.dataframe(st.session_state.materials_list, use_container_width=True)
        else: st.info("No materials added yet.")
            
        st.subheader("📐 Production Sizes (with Roll Info)")
        if st.session_state.sizes_history: st.dataframe(st.session_state.sizes_history, use_container_width=True)
        else: st.info("No production sizes recorded.")

    with col_summary2:
        st.subheader("🚚 Institute Shipments")
        if st.session_state.institute_shipments: st.dataframe(st.session_state.institute_shipments, use_container_width=True)
        else: st.info("No shipments recorded.")
            
        st.subheader("🎨 Mockups Status")
        if st.session_state.mockups_v2_history: st.dataframe(st.session_state.mockups_v2_history, use_container_width=True)
        else: st.info("No mockups added.")

    st.markdown("---")
    st.subheader("💾 Cloud & Export Options")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    final_data = {
        "project_info": {
            "name": p_name_view, "folder": f_num_view, "model": m_name_view,
            "article_name_t1": st.session_state.get('t1_art', ''),
            "certification_type": cert_type_view, "institutes": institutes,
            "add_bom": st.session_state.get('t1_add_bom', False),
            "bom_notes": st.session_state.get('t1_bom_notes', "")
        },
        "technical_documentation": {
            "splag": st.session_state.get('t3_splag', "NO "),
            "confirmed": st.session_state.get('t3_conf', "NO "),
            "measurement_chart": st.session_state.get('t3_chart', "NO "),
            "measurement_check": st.session_state.get('t3_check', "NO "),
            "saved_folder": st.session_state.get('t3_folder', "NO "),
            "label_status": st.session_state.get('t3_label', "NO ")
        },
        "sample_garment_status": {
            "inprogress": st.session_state.get('t4_in_prog', "NO "),
            "revision": st.session_state.get('t4_rev', "NO "),
            "confirmed": st.session_state.get('t4_conf', "NO "),
            "sent_oeti": st.session_state.get('t4_sent', "NO "),
            "entered_excel": st.session_state.get('t4_excel', "NO ")
        },
        "materials": st.session_state.materials_list,
        "production_sizes_and_rolls": st.session_state.sizes_history,
        "shipments": st.session_state.institute_shipments,
        "mockups": st.session_state.mockups_v2_history
    }
    
    with col_btn1:
        if st.button("☁️ Save Project to Cloud Database", key=f"t6_cloud_save_{gen}"):
            if p_name_view and f_num_view:
                project_id = f"{f_num_view} - {p_name_view}"
                save_project_to_db(project_id, final_data)
                st.success(f"Project '{project_id}' stored in Cloud Database!")
                st.rerun()
            else:
                st.error("Please fill in Project Name and Folder Number in Tab 1 before saving.")
            
    with col_btn2:
        if st.button("🖨️ Export PDF / Print Report", key=f"t6_print_pdf_btn_{gen}"):
            st.components.v1.html("<script>window.parent.print();</script>", height=0)
            st.info("Opening system print dialog...")
            
    with col_btn3:
        json_string = json.dumps(final_data, indent=4, ensure_ascii=False)
        st.download_button(
            label="📥 Download JSON Backup", data=json_string,
            file_name=f"checklist_{f_num_view if f_num_view else 'export'}.json", mime="application/json",
            key=f"t6_json_dl_btn_{gen}"
        )

