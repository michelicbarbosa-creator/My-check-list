import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="Calculadora de Prazos OEKO-Tex")

st.title("📋 Analisador de Certificações e Amostras em Tempo Real")
st.caption("Nota: Este programa não salva dados. Ao fechar ou atualizar a página, as informações serão limpas.")

# 1. Janela de Configuração de Alertas (Na barra lateral)
st.sidebar.header("⚙️ Configuração de Alerta")
dias_aviso = st.sidebar.number_input("Dias de antecedência para o Alerta", min_value=1, max_value=120, value=30)

# 2. Inicializar uma lista simples na memória temporária da sessão da página
if 'dados_temporarios' not in st.session_state:
    st.session_state.dados_temporarios = []

# 3. Formulário único para adicionar os itens na tela
with st.form("formulario_analise", clear_on_submit=True):
    st.markdown("### ➕ Inserir Item para Análise")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        categoria = c1.selectbox("Categoria", ["Tecido", "Reflex", "Elastic", "Buttons", "Extras"])
        nome = c1.text_input("Nome/Ref do Material")
    with c2:
        doc = c2.selectbox("Documento", ["OEKO-Tex Standard 100", "Test Report Fabric", "Test Report Accessories"])
        amostra = c2.selectbox("Status da Amostra", ["Pendente", "Em Progresso", "Feita"])
    with c3:
        aprovado = c3.selectbox("Amostra Aprovada?", ["Pendente", "Sim", "Não"])
        tab_medidas = c3.selectbox("Tabela de Medidas Aprovada?", ["Pendente", "Sim", "Não", "N/A"])
    with c4:
        num_cert = c4.text_input("Número do Certificado")
        data_expira = c4.date_input("Data de Expiração do Doc", date.today())
        
    enviar = st.form_submit_button("Adicionar à Tabela de Análise")
    
    if enviar and nome:
        st.session_state.dados_temporarios.append({
            "Categoria": categoria, "Nome": nome, "Doc": doc, "Amostra": amosta,
            "Aprovado": aprovado, "Medidas": tab_medidas, "Certificado": num_cert if num_cert else "N/A",
            "Expira": str(data_expira)
        })

# 4. Processar e exibir os dados na tela com os alertas calculados na hora
if st.session_state.dados_temporarios:
    hoje = date.today()
    dados_finais = []
    
    st.markdown("### 🔍 Resultados e Alertas de Expiração")
    
    # Processa cada item inserido para calcular o status do prazo
    for item in st.session_state.dados_temporarios:
        data_fim = datetime.strptime(item["Expira"], "%Y-%m-%d").date()
        dias_restantes = (data_fim - hoje).days
        
        if dias_restantes < 0:
            status_prazo = f"❌ EXPIRADO ({abs(dias_restantes)} dias atrás)"
            st.error(f"Alerta: O certificado do item **{item['Nome']}** ({item['Categoria']}) já expirou!")
        elif dias_restantes <= dias_aviso:
            status_prazo = f"⚠️ CRÍTICO ({dias_restantes} dias restantes)"
            st.warning(f"Atenção: O item **{item['Nome']}** vence em {dias_restantes} dias.")
        else:
            status_prazo = f"✅ Válido ({dias_restantes} dias)"
            
        item_processado = item.copy()
        item_processado["Status do Prazo"] = status_prazo
        dados_finais.append(item_processado)
        
    # Exibe a tabela final na tela
    df = pd.DataFrame(dados_finais)
    st.markdown("---")
    st.dataframe(df[["Categoria", "Nome", "Doc", "Amostra", "Aprovado", "Medidas", "Certificado", "Expira", "Status do Prazo"]], use_container_width=True)
    
    # Botão para limpar a tela manualmente sem precisar atualizar a página
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.dados_temporarios = []
        st.rerun()
else:
    st.info("Insira um componente no formulário acima para visualizar a análise de prazos e aprovações.")
