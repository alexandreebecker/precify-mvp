# ==============================================================================
# Precify.AI - Sprint 2: Fluxo de Orçamentação
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json
from datetime import date, timedelta

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precify.AI", layout="wide", initial_sidebar_state="auto")

# --- 2. FUNÇÕES DE RENDERIZAÇÃO DE FORMULÁRIOS (SPRINT 2) ---

def render_form_campanha_online():
    """Renderiza o formulário de briefing para Campanha Online."""
    with st.form(key="briefing_online_form"):
        st.info("Descreva o projeto com o máximo de detalhes possível para uma estimativa mais precisa.")
        
        dados_form = {}

        dados_form['briefing_semantico'] = st.text_area(
            "Descreva o objetivo principal da campanha (Campo Semântico)",
            help="Ex: 'Queremos uma campanha para aumentar o alcance no Instagram, com foco em geração de leads.'"
        )
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais'] = st.multiselect(
                "Quais canais digitais serão envolvidos?",
                options=["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn", "Google Ads", "Outro"]
            )
            dados_form['pecas_estimadas'] = st.number_input(
                "Quantidade de peças estimadas",
                min_value=1, step=1, format="%d", value=10,
                help="Número aproximado de posts, vídeos, stories, etc."
            )
            midia_paga = st.radio("Haverá mídia paga?", ("Não", "Sim"), horizontal=True)
            dados_form['midia_paga'] = (midia_paga == "Sim")
            
            dados_form['verba_midia'] = 0.0
            if dados_form['midia_paga']:
                dados_form['verba_midia'] = st.number_input(
                    "Qual a verba estimada para a mídia? (R$)",
                    min_value=0.0, step=100.0, format="%.2f"
                )
        with col2:
            dados_form['publico_alvo'] = st.text_area("Descreva o Público-alvo")
            dados_form['urgencia'] = st.select_slider(
                "Qual a urgência do projeto?",
                options=["Baixa", "Média", "Alta"], value="Média"
            )
            today = date.today()
            periodo_campanha = st.date_input(
                "Período da campanha (início e fim)",
                value=(today, today + timedelta(days=30))
            )
            if len(periodo_campanha) == 2:
                dados_form['periodo_inicio'] = str(periodo_campanha[0])
                dados_form['periodo_fim'] = str(periodo_campanha[1])
            
            pos_campanha = st.radio("Deseja acompanhamento pós-campanha?", ("Não", "Sim"), horizontal=True)
            dados_form['pos_campanha'] = (pos_campanha == "Sim")

        submitted = st.form_submit_button("Analisar Briefing e ir para Próximo Passo ➡️")
        
        if submitted:
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3 # Avança para a próxima etapa
            st.rerun()

# --- 3. FUNÇÕES DE DADOS (FIRESTORE) E AUTH ---
# (Todas as funções do Sprint 1 permanecem aqui, sem alterações)
@st.cache_resource
def initialize_firebase():
    try:
        creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e:
        st.error(f"FALHA NA CONEXÃO COM FIREBASE: {e}"); return None

def sign_up(email, password, name):
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        db.collection('agencias').document(user.uid).set({'nome': f"Agência de {name}", 'uid_admin': user.uid})
        st.success("Usuário e Agência registrados! Por favor, faça o login.")
    except Exception as e: st.error(f"Erro no registro: {e}")

def registrar_log_alteracao(db_client, agencia_id, usuario_email, acao, detalhes):
    try:
        log_data = {'timestamp': firestore.SERVER_TIMESTAMP, 'usuario_email': usuario_email, 'acao': acao, 'detalhes': detalhes}
        db_client.collection('agencias').document(agencia_id).collection('historico_alteracoes').add(log_data)
    except Exception as e: st.warning(f"Log não registrado: {e}")

# ... (outras funções de dados como carregar_historico, etc. devem estar aqui) ...

# --- 4. INICIALIZAÇÃO E LÓGICA DE LOGIN ---
db = initialize_firebase()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Bem-vindo ao Precify.AI")
    choice = st.selectbox("Acessar Plataforma", ["Login", "Registrar"], label_visibility="collapsed")
    if choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Login"):
                try:
                    user = auth.get_user_by_email(email)
                    st.session_state.logged_in = True
                    st.session_state.user_info = {"name": user.display_name, "email": user.email, "uid": user.uid}
                    st.rerun()
                except Exception: st.error("Email não encontrado ou credenciais inválidas.")
    else:
        with st.form("register_form"):
            name = st.text_input("Seu Nome"); email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    # ==================================================
    # --- APLICAÇÃO PRINCIPAL (Área Logada) ---
    # ==================================================
    user_info = st.session_state.user_info

    # --- BARRA LATERAL DE NAVEGAÇÃO ---
    nome_display = user_info.get('name')
    saudacao = f"Olá, {nome_display.split()[0]}!" if nome_display and nome_display.strip() else "Olá!"
    st.sidebar.title(saudacao)

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.sidebar.divider()

    # Gerenciamento de estado da view para resetar o fluxo de orçamento
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "Painel Principal"
    
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento", "Configurações"], key="navigation")

    if st.session_state.current_view == "Novo Orçamento" and view != "Novo Orçamento":
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith('orcamento_') or k.startswith('dados_briefing')]
        for key in keys_to_delete:
            del st.session_state[key]
    st.session_state.current_view = view

    # --- ROTEAMENTO DE TELAS ---
    if view == "Painel Principal":
        st.header("Painel Principal")
        st.write("Em breve: um dashboard com seus principais KPIs e orçamentos recentes.")

    elif view == "Novo Orçamento":
        st.header("🚀 Iniciar Novo Orçamento")

        if 'orcamento_step' not in st.session_state:
            st.session_state.orcamento_step = 1

        # ETAPA 1: Seleção da Categoria
        if st.session_state.orcamento_step == 1:
            st.caption("Primeiro, selecione o tipo de projeto para carregar o formulário de briefing correto.")
            categorias = ["Selecione...", "Campanha Online", "Campanha Offline", "Campanha 360", "Projeto Estratégico"]
            categoria_escolhida = st.selectbox("Tipo de Campanha", options=categorias, index=0)

            if st.button("Iniciar Orçamento", disabled=(categoria_escolhida == "Selecione...")):
                st.session_state.orcamento_categoria = categoria_escolhida
                st.session_state.orcamento_step = 2
                st.rerun()

        # ETAPA 2: Formulário de Briefing (Dinâmico)
        elif st.session_state.orcamento_step == 2:
            categoria = st.session_state.get('orcamento_categoria', 'N/A')
            st.subheader(f"Briefing para: {categoria}")

            if categoria == "Campanha Online":
                render_form_campanha_online()
            elif categoria == "Campanha Offline":
                st.info("Formulário para 'Campanha Offline' em construção.")
            elif categoria == "Campanha 360":
                st.info("Formulário para 'Campanha 360' em construção.")
            elif categoria == "Projeto Estratégico":
                st.info("Formulário para 'Projeto Estratégico' em construção.")

            if st.button("⬅️ Voltar e escolher outra categoria"):
                st.session_state.orcamento_step = 1
                del st.session_state.orcamento_categoria
                st.rerun()
        
        # ETAPA 3: Análise da IA (Placeholder)
        elif st.session_state.orcamento_step == 3:
            st.subheader("🤖 Análise da IA e Estimativas (Mockup)")
            st.success("Briefing recebido com sucesso!")
            st.write("Esta é a tela onde a IA apresentará sua interpretação e sugestões (Sprint 3).")
            
            with st.expander("Ver dados coletados do briefing", expanded=False):
                st.json(st.session_state.get('dados_briefing', {}))

            if st.button("⬅️ Editar Briefing"):
                st.session_state.orcamento_step = 2
                st.rerun()

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência")
        st.caption("Defina os perfis de equipe e as margens que alimentarão seus orçamentos.")
        # O código completo da tela de configurações, que já funciona, deve estar aqui.
        # Por questão de brevidade, estou omitindo, mas ele NÃO deve ser removido do seu arquivo.
        st.info("Aqui entra todo o código da tela de Configurações (CRUD de Perfis, Configs Financeiras, Histórico).")