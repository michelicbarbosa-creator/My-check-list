with tab6:
    st.header("Finalisation, Database & PDF Export")
    bom_revision = st.selectbox("BOM REVISION", status_options, index=0)
    m_chart_revision = st.selectbox("MEASUREMENT CHART REVISION", status_options, index=0)
    care_label = st.selectbox("CARE LABEL", status_options, index=0)
    cert_docs = st.selectbox("CERTIFICATES DOCS ARCHIVE", status_options, index=0)
    inspec_report = st.selectbox("INSPECTION REPORT SAVED IN FOLDER", status_options, index=0)
    
    st.markdown("---")
    col_db, col_pdf = st.columns(2)
    
    # 🗄️ BOTÃO 1: GUARDAR NA BASE DE DADOS
    with col_db:
        if st.button("💾 Save Progress to Database"):
            conn = sqlite3.connect('checklist_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (
                    project_name, folder_number, model_name, article_name_t1, cert_type,
                    material, doc_art_name, doc_art_num, oekotex, text_report, add_bom, expiration_date,
                    t_splag, t_confirmed, m_chart, m_check, saved_folder, label_status,
                    s_inprogress, s_revision, s_confirmed, s_sent_oeti, s_excel, samples_made, date_made, samples_sent, date_sent,
                    mockup_article, mockups_ready, fabric_used, roll_number, fabric_number, date_sent_lab,
                    bom_revision, m_chart_revision, care_label, cert_docs, inspec_report
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                project_name, folder_number, model_name, article_name_t1, cert_type,
                material, doc_art_name, doc_art_num, int(oekotex), int(text_report), int(add_bom), str(expiration_date),
                t_splag, t_confirmed, m_chart, m_check, saved_folder, label_status,
                s_inprogress, s_revision, s_confirmed, s_sent_oeti, s_excel, samples_made, str(date_made), samples_sent, str(date_sent),
                mockup_article, mockups_ready, fabric_used, roll_number, fabric_number, str(date_sent_lab),
                bom_revision, m_chart_revision, care_label, cert_docs, inspec_report
            ))
            conn.commit()
            conn.close()
            st.success("🎉 All checklist items safely saved to the database!")

    # 📄 BOTÃO 2: GERAR RELATÓRIO COMPLETO
    with col_pdf:
        if st.button("📄 Compile Full Report (PDF)"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor("#1A365D"), alignment=1)
            body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)
            
            story = []
            story.append(Paragraph("<b>CERTIFICATION CHECKLIST FINAL REPORT</b>", title_style))
            story.append(Spacer(1, 15))
            
            all_items_data = [
                [Paragraph("<b>CHECKLIST ITEM / FIELD</b>", body_style), Paragraph("<b>VALUE / STATUS SELECTED</b>", body_style)],
                [Paragraph("<b>[TAB 1] Project Name</b>", body_style), Paragraph(project_name, body_style)],
                [Paragraph("<b>[TAB 1] Folder Number</b>", body_style), Paragraph(folder_number, body_style)],
                [Paragraph("<b>[TAB 1] Model Name</b>", body_style), Paragraph(model_name, body_style)],
                [Paragraph("<b>[TAB 1] Certification Type</b>", body_style), Paragraph(cert_type, body_style)],
                [Paragraph("<b>[TAB 2] Material Type</b>", body_style), Paragraph(material, body_style)],
                [Paragraph("<b>[TAB 2] Document Expiration</b>", body_style), Paragraph(f"{expiration_date} ({alert_msg})", body_style)],
                [Paragraph("<b>[TAB 2] OEKO-TEX / TEXT REPORT</b>", body_style), Paragraph(f"OEKO: {oekotex} | Report: {text_report} | BOM: {add_bom}", body_style)],
                [Paragraph("<b>[TAB 3] TECH DOCUMENTATION SPLAG</b>", body_style), Paragraph(t_splag, body_style)],
                [Paragraph("<b>[TAB 3] TECH DOCUMENTATION CONFIRMED</b>", body_style), Paragraph(t_confirmed, body_style)],
                [Paragraph("<b>[TAB 3] MEASUREMENT CHART</b>", body_style), Paragraph(m_chart, body_style)],
                [Paragraph("<b>[TAB 3] SAVED IN FOLDER / LABEL</b>", body_style), Paragraph(f"Folder: {saved_folder} | Label: {label_status}", body_style)],
                [Paragraph("<b>[TAB 4] SAMPLE IN PROGRESS</b>", body_style), Paragraph(s_inprogress, body_style)],
                [Paragraph("<b>[TAB 4] SAMPLE SENT TO OETI</b>", body_style), Paragraph(f"{s_sent_oeti} (Qty: {samples_sent} on {date_sent})", body_style)],
                [Paragraph("<b>[TAB 5] MOCK-UPS READY STATUS</b>", body_style), Paragraph(mockups_ready, body_style)],
                [Paragraph("<b>[TAB 5] Fabric / Roll / Fabric No.</b>", body_style), Paragraph(f"{fabric_used} / {roll_number} / {fabric_number}", body_style)],
                [Paragraph("<b>[TAB 6] BOM REVISION</b>", body_style), Paragraph(bom_revision, body_style)],
                [Paragraph("<b>[TAB 6] MEASUREMENT CHART REVISION</b>", body_style), Paragraph(m_chart_revision, body_style)],
                [Paragraph("<b>[TAB 6] CARE LABEL</b>", body_style), Paragraph(care_label, body_style)],
                [Paragraph("<b>[TAB 6] CERTIFICATES DOCS ARCHIVE</b>", body_style), Paragraph(cert_docs, body_style)],
                [Paragraph("<b>[TAB 6] INSPECTION REPORT</b>", body_style), Paragraph(inspec_report, body_style)]
            ]
            
            table = Table(all_items_data, colWidths=[250, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), colors.HexColor("#2B6CB0")),
                ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            
            story.append(table)
            doc.build(story)
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Complete PDF Report",
                data=buffer,
                file_name=f"Full_Report_{folder_number}.pdf",
                mime="application/pdf"
            )

    # ================= 🔍 VISUALIZADOR DA BASE DE DADOS COM FILTRO =================
    st.markdown("---")
    st.subheader("🔍 Search & Filter Saved Checklists")
    
    # Campo de Texto para Pesquisa Global
    search_query = st.text_input("Search by Project Name, Folder Number, or Material Type:", value="")
    
    conn = sqlite3.connect('checklist_database.db')
    import pandas as pd
    try:
        # Carregar todas as colunas relevantes para permitir filtros avançados
        query = "SELECT id, project_name, folder_number, material, cert_type, expiration_date, saved_at FROM projects ORDER BY saved_at DESC"
        df = pd.read_sql_query(query, conn)
        
        if not df.empty:
            # Aplicar o filtro se o usuário digitou alguma coisa
            if search_query:
                search_query = search_query.lower()
                filtered_df = df[
                    df['project_name'].str.lower().str.contains(search_query, na=False) |
                    df['folder_number'].str.lower().str.contains(search_query, na=False) |
                    df['material'].str.lower().str.contains(search_query, na=False)
                ]
                
                if not filtered_df.empty:
                    st.write(f"🔍 Found {len(filtered_df)} match(es):")
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.warning("No records matched your search terms.")
            else:
                # Se a barra estiver vazia, mostra todo o histórico
                st.write("📊 Showing all historical records:")
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No records found in database yet. Fill out the form and click Save above.")
    except Exception as e:
        st.error(f"Error loading database: {e}")
    finally:
        conn.close()
