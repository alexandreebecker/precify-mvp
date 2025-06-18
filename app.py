# ==============================================================================
# NOVA VERSÃO DA FUNÇÃO render_tela3_analise_ia()
# ==============================================================================

def render_tela3_analise_ia():
    st.header("Passo 3: Análise da IA e Escopo Sugerido")
    
    # Simula o processamento da IA com um status visual
    with st.status("Analisando briefing com LLM...", expanded=True) as status:
        time.sleep(1); st.write("✅ Briefing interpretado.")
        time.sleep(1); st.write("✅ Complexidade e urgência avaliadas.")
        time.sleep(1); st.write("✅ Escopo de entregáveis proposto.")
        status.update(label="Análise completa!", state="complete", expanded=False)

    st.success("A IA interpretou o briefing e sugeriu o escopo abaixo.")
    
    # Placeholder para o escopo sugerido pela IA (mesma estrutura de antes)
    if 'escopo_sugerido' not in st.session_state:
        st.session_state.escopo_sugerido = {
            "Tipo de Projeto Detectado": "Campanha de Lançamento",
            "Complexidade": "Média",
            "Entregáveis Sugeridos": ["10 Posts para Instagram", "3 Anúncios em Vídeo", "1 Landing Page"]
        }
    
    escopo = st.session_state.escopo_sugerido
    
    # --- NOVO LAYOUT DE EXIBIÇÃO ---
    with st.container(border=True):
        st.subheader("📝 Resumo da Análise")
        
        # Usando colunas para uma apresentação limpa
        col1, col2 = st.columns(2)
        col1.metric("Tipo de Projeto Detectado", escopo.get("Tipo de Projeto Detectado", "N/A"))
        col2.metric("Complexidade Estimada", escopo.get("Complexidade", "N/A"))
        
        st.divider()
        
        st.write("**Entregáveis Sugeridos:**")
        # Exibe os entregáveis como uma lista de itens, muito mais legível
        for entregavel in escopo.get("Entregáveis Sugeridos", []):
            st.markdown(f"- {entregavel}")

    st.write("") # Espaçamento
    
    if st.button("Aceitar Escopo e Gerar Orçamento", type="primary", use_container_width=True):
        st.session_state.view = 'tela4_ajustes'
        st.rerun()