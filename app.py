# ==============================================================================
# Precify.AI - Sprint 2: Fluxo de Orçamentação
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precify.AI", layout="wide", initial_sidebar_state="auto")

# --- 2. FUNÇÕES DE INICIALIZAÇÃO E AUTENTICAÇÃO ---
@st.cache_resource
def initialize_firebase():
    """Inicializa o Firebase de forma segura e retorna o cliente do Firestore."""
    try:
        creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e:
        st.error(f"FALHA NA CONEXÃO COM FIREBASE: {e}")
        return None

def sign_up(email, password, name):
    """Cria um novo usuário e um documento de agência correspondente."""
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        db.collection('agencias').document(user.uid).set({
            'nome': f"Agência de {name}",
            'uid_admin': user.uid
        })
        st.success("Usuário e Agência registrados com sucesso! Por favor, faça o login.")
    except Exception as e: st.error(f"Erro no registro: {e}")

# --- 3. FUNÇÕES DE DADOS (FIRESTORE) ---

def registrar_log_alteracao(db_client, agencia_id, usuario_email, acao, detalhes):
    """Registra um evento no histórico de alterações da agência."""
    try:
        log_data = {
            'timestamp': firestore.SERVER_TIMESTAMP,
            'usuario_email': usuario_email,
            'acao': acao,
            'detalhes': detalhes
        }
        db_client.collection('agencias').document(agencia_id).collection('historico_alteracoes').add(log_data)
    except Exception as e:
        st.warning(f"Não foi possível registrar a alteração no histórico: {e}")

def carregar_historico(db_client, agencia_id, limit=20):
    """Carrega as últimas N alterações do histórico da agência, ordenadas pela data."""
    try:
        historico_ref = (db_client.collection('agencias').document(agencia_id)
                         .collection('historico_alteracoes')
                         .order_by('timestamp', direction=firestore.Query.DESCENDING)
                         .limit(limit)
                         .stream())
        return list(historico_ref)
    except Exception as e:
        st.warning(f"Não foi possível carregar o histórico: {e}")
        return []

def carregar_configuracoes_financeiras(db_client, agencia_id):
    """Carrega as configurações financeiras de uma agência do Firestore."""
    try:
        doc_ref = db_client.collection('agencias').document(agencia_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('configuracoes_financeiras', {})
    except Exception as e:
        st.error(f"Erro ao carregar configurações: {e}")
    return {}

def salvar_configuracoes_financeiras(db_client, agencia_id, configs, usuario_email):
    """Salva as configurações financeiras e registra o log da alteração."""
    try:
        doc_ref = db_client.collection('agencias').document(agencia_id)
        doc_ref.update({'configuracoes_financeiras': configs})
        st.success("Configurações financeiras salvas com sucesso!")
        st.session_state.config_financeiras = configs
        
        detalhes_log = (f"Margens atualizadas: Lucro({configs['margem_lucro']}), Impostos({configs['impostos']}), "
                        f"Fixos({configs['custos_fixos']}), Coord.({configs['taxa_coordenacao']})")
        registrar_log_alteracao(db_client, agencia_id, usuario_email, "Atualização de Config. Financeiras", detalhes_log)
    except Exception as e:
        st.error(f"Erro ao salvar configurações: {e}")

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
    
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento", "Configurações"], label_visibility="collapsed", key="navigation")

    # Se a view mudou para fora de "Novo Orçamento", reseta o estado do formulário
    if st.session_state.current_view == "Novo Orçamento" and view != "Novo Orçamento":
        if 'orcamento_step' in st.session_state:
            del st.session_state.orcamento_step
        if 'orcamento_categoria' in st.session_state:
            del st.session_state.orcamento_categoria
    st.session_state.current_view = view
    

    # --- ROTEAMENTO DE TELAS ---
    if view == "Painel Principal":
        st.header("Painel Principal")
        st.write("Em breve: um dashboard com seus principais KPIs e orçamentos recentes.")

    elif view == "Novo Orçamento":
        st.header("🚀 Iniciar Novo Orçamento")
        st.caption("Primeiro, selecione o tipo de projeto para carregar o formulário de briefing correto.")

        # Gerencia o estado do formulário multi-etapas
        if 'orcamento_step' not in st.session_state:
            st.session_state.orcamento_step = 1

        # ETAPA 1: Seleção da Categoria
        if st.session_state.orcamento_step == 1:
            categorias = [
                "Selecione o tipo de campanha...",
                "Campanha Online",
                "Campanha Offline",
                "Campanha 360",
                "Projeto Estratégico"
            ]
            categoria_escolhida = st.selectbox("Tipo de Campanha", options=categorias, index=0)

            if st.button("Iniciar Orçamento", disabled=(categoria_escolhida == categorias[0])):
                st.session_state.orcamento_categoria = categoria_escolhida
                st.session_state.orcamento_step = 2
                st.rerun()

        # ETAPA 2: Formulário de Briefing (Placeholder)
        elif st.session_state.orcamento_step == 2:
            categoria = st.session_state.get('orcamento_categoria', 'N/A')
            st.subheader(f"Briefing para: {categoria}")
            st.info("O formulário de briefing detalhado aparecerá aqui no próximo passo.")
            
            if st.button("⬅️ Voltar e escolher outra categoria"):
                st.session_state.orcamento_step = 1
                if 'orcamento_categoria' in st.session_state:
                    del st.session_state.orcamento_categoria
                st.rerun()

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência")
        st.caption("Defina os perfis de equipe e as margens que alimentarão seus orçamentos.")

        agencia_id = user_info['uid']

        # --- SEÇÃO CRUD PERFIS DE EQUIPE ---
        with st.expander("Gerenciar Perfis de Equipe", expanded=True):
            # ... (código do CRUD de perfis)
            st.subheader("Adicionar Novo Perfil")
            with st.form("new_profile_form", clear_on_submit=True):
                col1, col2 = st.columns([2, 1]); funcao = col1.text_input("Função"); custo_hora = col2.number_input("Custo/Hora (R$)")
                if st.form_submit_button("Adicionar"):
                    if funcao and custo_hora > 0:
                        novo_perfil = {"funcao": funcao, "custo_hora": custo_hora}
                        db.collection('agencias').document(agencia_id).collection('perfis_equipe').add(novo_perfil)
                        st.toast(f"Perfil '{funcao}' adicionado!")
                        detalhes_log = f"Novo perfil '{funcao}' adicionado com custo/hora de R$ {custo_hora:.2f}."
                        registrar_log_alteracao(db, agencia_id, user_info['email'], "Adição de Perfil", detalhes_log)
                        st.rerun()
            st.divider()
            st.subheader("Perfis Cadastrados")
            # ... (código de listagem e deleção de perfis)

        st.divider()

        # --- SEÇÃO DE CONFIGURAÇÕES FINANCEIRAS ---
        # ... (código das configs financeiras)

        st.divider()

        # --- SEÇÃO: HISTÓRICO DE ALTERAÇÕES ---
        # ... (código do histórico)