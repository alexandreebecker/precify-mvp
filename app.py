git add app.py
git commit -m "Feat: Integra painel principal à área logada"
        c1.metric("Custo Total", f"R$ {custos['custo_total']:,.2f}".replace(",", "."))
        c2.metric("Preço Final", f"R$ {preco_sugerido:,.2f}".replace(",", "."))
    with st.container(border=True): st.subheader("Justificativa"); st.write(orcamento["justificativa"])
    if st.button("Salvar no Histórico", type="primary"):
        with st.spinner("Salvando..."):
            orcamento_para_salvar = orcamento.copy(); orcamento_para_salvar['estimativa_custos']['preco_sugerido'] = preco_sugerido
            db.collection("orçamentos").add(orcamento_para_salvar)
            st.toast("Salvo!", icon="✅"); time.sleep(1); st.rerun()

def render_historico():
    st.header("Histórico de Orçamentos")
    docs = db.collection("orçamentos").where("uid", "==", user_info['uid']).order_by("data_orcamento", direction=firestore.Query.DESCENDING).stream()
    orcamentos_lista = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    if orcamentos_lista:
        display_data = [{"Data": item["data_orcamento"].strftime("%d/%m/%Y"), "Projeto": item["interpretacao_ia"]["tipo_projeto_detectado"], "Preço": f"R$ {item['estimativa_custos']['preco_sugerido']:,.2f}".replace(",", ".")} for item in orcamentos_lista]
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
    else: st.info("Nenhum orçamento salvo no histórico.")

# Roteador principal do app
st.sidebar.title(f"Bem-vindo(a), {user_info['name']}!")
if st.sidebar.
        c2.metric("Preço Final", f"R$ {preco_sugerido:,.2f}".replace(",", "."))
    with st.container(border=True): st.subheader("Justificativa"); st.write(orcamento["justificativa"])
    if st.button("Salvar no Histórico", type="primary"):
        with st.spinner("Salvando..."):
            orcamento_para_salvar = orcamento.copy(); orcamento_para_salvar['estimativa_custos']['preco_sugerido'] = preco_sugerido
            db.collection("orçamentos").add(orcamento_para_salvar)
            st.toast("Salvo!", icon="✅"); time.sleep(1); st.rerun()

def render_historico():
    st.header("Histórico de Orçamentos")
    docs = db.collection("orçamentos").where("uid", "==", user_info['uid']).order_by("data_orcamento", direction=firestore.Query.DESCENDING).stream()
    orcamentos_lista = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    if orcamentos_lista:
        display_data = [{"Data": item["data_orcamento"].strftime("%d/%m/%Y"), "Projeto": item["interpretacao_ia"]["tipo_projeto_detectado"], "Preço": f"R$ {item['estimativa_custos']['preco_sugerido']:,.2f}".replace(",", ".")} for item in orcamentos_lista]
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
    else: st.info("Nenhum orçamento salvo no histórico.")
    
# Roteamento da aplicação
if "page" not in st.session_state: st.session_state.page = "inicial"

app_mode = st.sidebar.radio("Navegação", ["Gerar Orçamento", "Histórico"])
if app_mode == "Gerar Orçamento":
    if st.session_state.page == "inicial": render_pagina_inicial()
    elif st.session_state.page == "input_briefing": render_input_briefing()
    else: render_orcamento_gerado()
else: render_historico()