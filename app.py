# ==============================================================================
# Precify.AI MVP - Versão com Chamadas Padrão do Autenticador
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json
import time
import datetime
import streamlit_authenticator as stauth

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precify.AI", layout="wide", initial_sidebar_state="auto")

# --- 2. FUNÇÃO DE CONEXÃO ---
@st.cache_resource
def initialize_firebase():
    """Inicializa o Firebase e retorna o cliente do Firestore."""
    try:
        creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e:
        st.error(f"FALHA NA CONEXÃO COM FIREBASE: {e}")
        return None

# --- 3. INICIALIZAÇÃO ---
db = initialize_firebase()

# --- 4. PREPARAÇÃO DO AUTENTICADOR ---
users_config = {'usernames': {}}
if db:
    try:
        # Busca os usuários do Firebase para popular o autenticador
        users = auth.list_users().iterate_all()
        for user in users:
            if user.password_hash:
                users_config['usernames'][user.email] = {
                    "email": user.email,
                    "name": user.display_name or user.email.split('@')[0],
                    "password": user.password_hash
                }
    except Exception as e:
        st.warning(f"Não foi possível buscar usuários: {e}.")

authenticator = stauth.Authenticate(
    users_config, 'precify_cookie_v8', 'precify_key_v8', 30
)

# --- 5. LÓGICA DE LOGIN/REGISTRO (USANDO VALORES PADRÃO) ---

# CORREÇÃO: Chamando a função de login da forma mais simples possível.
name, authentication_status, username = authenticator.login()

if authentication_status:
    # --- APP PRINCIPAL (QUANDO O USUÁRIO ESTÁ LOGADO) ---
    st.sidebar.title(f"Bem-vindo, {name}!")
    # CORREÇÃO: Chamando logout da forma mais simples
    authenticator.logout()

    # O resto do seu aplicativo (funções de renderização, etc.) vai aqui.
    # Esta parte não precisa de alteração.
    
    def chamar_ia_precify(briefing, tipo_projeto, canais, prazo):
        st.toast("Analisando briefing...", icon="🤖"); time.sleep(1)
        user_record = auth.get_user_by_email(username)
        return {
            "uid": user_record.uid, "data_orcamento": datetime.datetime.now(),
            "briefing_original": briefing,
            "input_usuario": {"tipo_projeto": tipo_projeto, "canais": canais, "prazo": str(prazo)},
            "interpretacao_ia": {"tipo_projeto_detectado": f"Projeto de {tipo_projeto}", "numero_entregas": f"{len(canais) * 3} peças", "complexidade": "Média", "nivel_urgencia": "Normal"},
            "estimativa_custos": {"criação_h": 15, "texto_h": 10, "midia_h": 15, "custo_total": 1000 + len(canais) * 350, "margem_aplicada": 0.0, "preco_sugerido": 1000 + len(canais) * 350},
            "justificativa": f"Estimativa para {tipo_projeto} nos canais {', '.join(canais)}."
        }
        
    def render_pagina_inicial():
        st.title("Precify.AI"); st.header("Cole o briefing. Deixe a IA fazer o orçamento.")
        if st.button("Começar Orçamento", type="primary", use_container_width=True):
            st.session_state.page = "input_briefing"; st.rerun()

    def render_input_briefing():
        if st.button("← Voltar para o Início"): st.session_state.page = "inicial"; st.rerun()
        st.header("Input do Briefing")
        with st.form("briefing_form"):
            st.subheader("Cole o briefing do cliente")
            briefing_texto = st.text_area("Briefing", height=200, placeholder="Ex: Campanha de redes sociais...")
            st.subheader("Preferências rápidas")
            c1, c2 = st.columns(2)
            tipo_projeto = c1.selectbox("Tipo", ["Campanha digital", "Logo", "Social media", "Vídeo", "Outro"])
            prazo = c2.date_input("Prazo", min_value=datetime.date.today())
            canais = st.multiselect("Canais", ["Instagram", "YouTube", "TV", "Impressos", "TikTok"])
            if st.form_submit_button("Gerar Orçamento", type="primary", use_container_width=True):
                if briefing_texto and canais:
                    with st.spinner("Aguarde, nossa IA está trabalhando..."):
                        st.session_state.orcamento_gerado = chamar_ia_precify(briefing_texto, tipo_projeto, canais, prazo)
                        st.session_state.page = "orcamento_gerado"; st.rerun()
                else: st.warning("Preencha o briefing e selecione pelo menos um canal.")

    def render_orcamento_gerado():
        if st.button("← Editar Briefing"): st.session_state.page = "input_briefing"; st.rerun()
        st.header("Orçamento Gerado")
        orcamento = st.session_state.get("orcamento_gerado")
        if not orcamento: return st.error("Erro ao gerar orçamento.")
        interpretacao = orcamento["interpretacao_ia"]; custos = orcamento["estimativa_custos"]
        with st.container(border=True): st.subheader("Interpretação"); c1, c2 = st.columns(2); c1.metric("Tipo", interpretacao["tipo_projeto_detectado"]); c2.metric("Entregas", interpretacao["numero_entregas"])
        with st.container(border=True):
            st.subheader("Custos")
            margem = st.slider("Margem (%)", 0, 100, int(custos["margem_aplicada"]))
            preco_sugerido = custos["custo_total"] * (1 + margem / 100)
            c1, c2 = st.columns(2)
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
        user_record = auth.get_user_by_email(username)
        docs = db.collection("orçamentos").where("uid", "==", user_record.uid).order_by("data_orcamento", direction=firestore.Query.DESCENDING).stream()
        orcamentos_lista = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
        if orcamentos_lista: st.dataframe(pd.DataFrame(orcamentos_lista), use_container_width=True)
        else: st.info("Nenhum orçamento salvo no histórico.")
        
    if "page" not in st.session_state: st.session_state.page = "inicial"
    app_mode = st.sidebar.radio("Navegação", ["Gerar Orçamento", "Histórico"])
    if app_mode == "Gerar Orçamento":
        if st.session_state.page == "inicial": render_pagina_inicial()
        elif st.session_state.page == "input_briefing": render_input_briefing()
        else: render_orcamento_gerado()
    else: render_historico()


elif authentication_status is False:
    st.error('Usuário ou senha incorreto(a)')

elif authentication_status is None:
    st.warning('Por favor, faça o login para continuar.')
    
    # Lógica de Registro (Simplificada)
    try:
        # CORREÇÃO: Chamando o registro da forma mais simples
        if authenticator.register_user():
            email = st.session_state['email']
            name = st.session_state['name']
            password = st.session_state['password']
            
            # Cria o usuário no Firebase Authentication
            user = auth.create_user(email=email, password=password, display_name=name)
            st.success('Usuário registrado com sucesso! Por favor, recarregue a página e faça o login.')
    except Exception as e:
        st.error(e)