import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="Gestor OEKO-Tex Avançado 2026")

# ==========================================
# 1. CONEXÃO E CRIAÇÃO DO BANCO DE DADOS
# ==========================================
def conectar_banco():
    return sqlite3.connect("gestor_certificacoes_v4.db")

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela 1: Checklist e Cronologia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist_processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT, tarefa TEXT, status TEXT
        )
    """)
    
    # Tabela 2: Componentes com Categorias Detalhadas (Atualizada)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS componentes_producao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT, nome_material TEXT, tipo_doc TEXT, num_certificado TEXT, expira TEXT,
            mockup_status TEXT, mockup_aprovado TEXT,
            ordem_producao TEXT, artigos TEXT,
            seam_ready_qtd INTEGER, seam_sent_oeti_qtd INTEGER, notas TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM checklist_processos")
    if cursor.fetchone() == 0:
        tarefas = [
            ("Documentation", "Application form OETI", "Pendente"),
            ("Documentation", "Technical document OETI", "Pendente"),
            ("Technical documentation", "Technical documentation SPLAG", "Concluído"),
            ("Technical documentation", "Measurement chart", "Pendente"),
            ("Technical documentation", "Care label", "Pendente"),
            ("Sample garment", "Sample in progress", "Em Progresso"),
            ("Sample garment", "Sample sent to OETI!", "Pendente"),
            ("Finalisation", "Technical sheet revision", "Pendente"),
            ("Finalisation", "BOM revision", "Pendente"),
            ("Finalisation", "Care label revision", "Pendente")
        ]
        cursor.executemany("INSERT INTO checklist_processos (fase, tarefa, status) VALUES (?, ?, ?)", tarefas)
        
    conn.commit()
    conn.close()

inicializar_banco()

# Carregar dados
conn = conectar_banco()
df_processos = pd.read_sql_query("SELECT * FROM checklist_processos", conn)
df_componentes = pd.read_sql_query("SELECT * FROM componentes_producao", conn)
conn.close()

# Lista de opções separadas solicitadas
categorias_detalhadas = ["Fabric", "Reflex", "Elastic", "Button", "Velcro", "Linha", "Zipper"]

# ==========================================
# 2. CONTROLO EM TEMPO REAL DE VENCIMENTOS
# ==========================================
hoje = date.today()
vencidos_hoje = []

if not df_componentes.empty:
    for idx, r in df_componentes.iterrows():
        try:
            data_vencimento = datetime.strptime(r["expira"], "%Y-%m-%d").date()
            if data_vencimento <= hoje:
                vencidos_hoje.append({
                    "Material": r["nome_material"],
                    "Categoria": r["categoria"],
                    "Tipo": r["tipo_doc"],
                    "Número": r["num_certificado"],
                    "Data": r["expira"]
                })
        except:
            pass

st.title("📋 Gestor Técnico de Produção e Certificação")
st.markdown("### **Projeto:** 35.1a-d winter + rain parkas | **Artigos:** 409 130 - 409 110")

# ==========================================
# 3. PRIMEIRO QUADRADO: JANELA DE CERTIFICADOS SEPARADOS
# ==========================================
st.header("1. Painel de Certificados & Validades Individuais")

col_quad1, col_quad2 = st.columns(2)

with col_quad1:
    st.markdown("#### 🚨 Alertas Ativos por Tipo de Componente")
    if vencidos_hoje:
        for doc in vencidos_hoje:
            st.error(f"⏰ **EXPIRADO!** [{doc['Categoria']}] - O documento **{doc['Tipo']}** ({doc['Número']}) do material **{doc['Material']}** venceu em {doc['Data']}!")
    else:
        st.success("✅ Todos os certificados (Fabric, Reflex, Elastic, etc.) estão dentro do prazo.")

with col_quad2:
    st.markdown("#### 📥 Adicionar Certificado com Data")
    # Janela/Formulário para inserir as opções de forma totalmente separada
    with st.popover("➕ Configurar Novo Certificado"):
        with st.form("form_prazos_detalhado", clear_on_submit=True):
            cat_p = st.selectbox("Selecione a Opção de Componente", categorias_detalhadas)
            nome_p = st.text_input("Nome/Referência do Item", placeholder="Ex: Forro Nylon / Botão Metal")
            tipo_p = st.selectbox("Tipo de Documento", ["OEKO-Tex Standard 100", "Test Report Fabric", "Test Report Accessories"])
            num_p = st.text_input("Número do Certificado")
            data_p = st.date_input("Data de Expiração deste Certificado", hoje)
            
            if st.form_submit_button("Gravar Certificado no Banco"):
                if nome_p:
                    conn = conectar_banco()
                    conn.execute("""
                        INSERT INTO componentes_producao (categoria, nome_material, tipo_doc, num_certificado, expira, mockup_status, mockup_aprovado, ordem_producao, artigos, seam_ready_qtd, seam_sent_oeti_qtd, notas)
                        VALUES (?, ?, ?, ?, ?, 'Mock-ups needed', 'Pendente', '', '', 0, 0, '')
                    """, (cat_p, nome_p, tipo_p, num_p, str(data_p)))
                    conn.commit()
                    conn.close()
                    st.rerun()

st.markdown("---")

# ==========================================
# 4. CRONOLOGIA & CHECKLIST (SEPARADORES DO PAPEL)
# ==========================================
st.header("2. Cronologia de Validação do Projeto")
c_fase1, c_fase2, c_fase3 = st.columns(3)

with c_fase1:
    st.markdown("#### 📑 Documentation & Tech")
    for idx, r in df_processos[df_processos["fase"].isin(["Documentation", "Technical documentation"])].iterrows():
        st.text(f"• [{r['status']}] {r['tarefa']}")

with c_fase2:
    st.markdown("#### 👕 Sample Garment")
    for idx, r in df_processos[df_processos["fase"] == "Sample garment"].iterrows():
        st.text(f"• [{r['status']}] {r['tarefa']}")

with c_fase3:
    st.markdown("#### 🏁 Finalisation")
    for idx, r in df_processos[df_processos["fase"] == "Finalisation"].iterrows():
        st.text(f"• [{r['status']}] {r['tarefa']}")

st.markdown("---")

# ==========================================
# 5. CONTRÔLO DE FABRICAÇÃO E QUANTIDADES (ABAS SEPARADAS)
# ==========================================
st.header("3. Painel de Fabricação & Amostras de Costura")

with st.form("form_producao_completo", clear_on_submit=True):
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("##### 🧵 Status do Mock-up")
        mat_existente = col_p1.selectbox("Selecionar Material Cadastrado", [""] + list(df_componentes["nome_material"].unique()) if not df_componentes.empty else [""])
        mock_st = col_p1.selectbox("Status", ["Mock-ups needed", "Seam samples in progress", "Ready"])
        mock_ap = col_p1.selectbox("Aprovado?", ["Pendente", "Aprovado", "Reprovado"])
    with col_p2:
        st.markdown("##### 📦 Ordem de Produção")
        op_num = col_p2.text_input("Ordem de Produção (OP)")
        art_lista = col_p2.text_area("Artigos vinculados")
    with col_p3:
        st.markdown("##### 📊 Quantidades")
        qtd_feitas = col_p3.number_input("Seam Samples Ready (Qtd Feitas)", min_value=0, value=0)
        qtd_enviadas = col_p3.number_input("Seam Samples Sent OETI (Qtd Enviadas)", min_value=0, value=0)
        obs_p = col_p3.text_input("Notas")

    if st.form_submit_button("Atualizar Dados de Fabricação"):
        if mat_existente:
            conn = conectar_banco()
            conn.execute("""
                UPDATE componentes_producao 
                SET mockup_status=?, mockup_aprovado=?, ordem_producao=?, artigos=?, seam_ready_qtd=?, seam_sent_oeti_qtd=?, notas=?
                WHERE nome_material=?
            """, (mock_st, mock_ap, op_num, art_lista, qtd_feitas, qtd_enviadas, obs_p, mat_existente))
            conn.commit()
            conn.close()
            st.success("Dados de fabricação atualizados com sucesso!")
            st.rerun()

# Exibição das Tabelas divididas exatamente pelas opções pedidas
if not df_componentes.empty:
    abas = st.tabs(categorias_detalhadas)
    for i, aba in enumerate(abas):
        with aba:
            df_f = df_componentes[df_componentes["categoria"] == categories_detalhadas[i]]
            if not df_f.empty:
                st.dataframe(df_f[["nome_material", "tipo_doc", "num_certificado", "expira", "mockup_status", "mockup_aprovado", "ordem_producao", "artigos", "seam_ready_qtd", "seam_sent_oeti_qtd", "notas"]], use_container_width=True)
            else:
                st.info(f"Nenhum registo de certificado inserido para {categorias_detalhadas[i]}.")
