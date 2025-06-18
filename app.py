# ==============================================================================
# Precify.AI - Sprint 1: Implementação do Painel de Configurações
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
            'timestamp': firestore.SERVER_TIMESTAMP, # Usa o timestamp do servidor Firebase
            'usuario_email': usuario_email,
            'acao': acao,
            'detalhes': detalhes
        }
        db_client.collection('agencias').document(agencia_id).collection('historico_alteracoes').add(log_data)
    except Exception as e:
        st.warning(f"Não foi possível registrar a alteração no histórico: {e}")

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
        
        # Registrar o log da alteração
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

    view = st.sidebar.radio("Menu", ["Painel Principal", "Configurações"], label_visibility="collapsed")

    # --- ROTEAMENTO DE TELAS ---
    if view == "Painel Principal":
        st.header("Painel Principal")
        st.write("Em breve: um dashboard com seus principais KPIs e orçamentos recentes.")

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência")
        st.caption("Defina os perfis de equipe e as margens que alimentarão seus orçamentos.")

        agencia_id = user_info['uid']

        # --- SEÇÃO CRUD PERFIS DE EQUIPE ---
        with st.expander("Gerenciar Perfis de Equipe", expanded=True):
            st.subheader("Adicionar Novo Perfil")
            with st.form("new_profile_form", clear_on_submit=True):
                col1, col2 = st.columns([2, 1])
                funcao = col1.text_input("Nome da Função/Cargo", placeholder="Ex: Designer Gráfico Sênior")
                custo_hora = col2.number_input("Custo por Hora (R$)", min_value=0.0, step=5.0, format="%.2f")
                submitted = st.form_submit_button("Adicionar Perfil")

                if submitted and funcao and custo_hora > 0:
                    novo_perfil = {"funcao": funcao, "custo_hora": custo_hora}
                    db.collection('agencias').document(agencia_id).collection('perfis_equipe').add(novo_perfil)
                    st.toast(f"Perfil '{funcao}' adicionado!", icon="✅")
                    
                    detalhes_log = f"Novo perfil '{funcao}' adicionado com custo/hora de R$ {custo_hora:.2f}."
                    registrar_log_alteracao(db, agencia_id, user_info['email'], "Adição de Perfil", detalhes_log)
            st.divider()

            st.subheader("Perfis Cadastrados")
            perfis_ref = db.collection('agencias').document(agencia_id).collection('perfis_equipe').stream()
            perfis_lista = list(perfis_ref)

            if not perfis_lista:
                st.info("Nenhum perfil cadastrado. Adicione seu primeiro perfil acima.")
            else:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write("**Função**"); c2.write("**Custo/Hora**"); c3.write("**Ação**")
                for perfil_doc in perfis_lista:
                    perfil_data = perfil_doc.to_dict()
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1: st.text(perfil_data.get("funcao", "N/A"))
                    with col2: st.text(f"R$ {perfil_data.get('custo_hora', 0):.2f}")
                    with col3:
                        if st.button("Deletar", key=f"del_{perfil_doc.id}", type="primary"):
                            funcao_deletada = perfil_data.get('funcao', 'Desconhecido')
                            db.collection('agencias').document(agencia_id).collection('perfis_equipe').document(perfil_doc.id).delete()
                            st.toast(f"Perfil '{funcao_deletada}' deletado.")
                            
                            # Registrar o log da deleção
                            detalhes_log = f"O perfil '{funcao_deletada}' foi removido."
                            registrar_log_alteracao(db, agencia_id, user_info['email'], "Deleção de Perfil", detalhes_log)
                            st.rerun()

        st.divider()

        # --- SEÇÃO DE CONFIGURAÇÕES FINANCEIRAS ---
        if 'config_financeiras' not in st.session_state:
            st.session_state.config_financeiras = carregar_configuracoes_financeiras(db, agencia_id)

        defaults = {"margem_lucro": 20.0, "impostos": 15.0, "custos_fixos": 10.0, "taxa_coordenacao": 10.0}
        
        st.subheader("⚙️ Configurações Financeiras da Agência")
        st.caption("Defina as margens e taxas padrão.")

        with st.form(key="form_configuracoes_financeiras"):
            col1, col2 = st.columns(2)
            with col1:
                margem_lucro = st.number_input("Margem de Lucro (%)", value=st.session_state.config_financeiras.get("margem_lucro", defaults["margem_lucro"]), min_value=0.0, step=1.0, format="%.2f")
                impostos = st.number_input("Impostos (%)", value=st.session_state.config_financeiras.get("impostos", defaults["impostos"]), min_value=0.0, step=0.5, format="%.2f")
            with col2:
                custos_fixos = st.number_input("Custos Fixos/Operacionais (%)", value=st.session_state.config_financeiras.get("custos_fixos", defaults["custos_fixos"]), min_value=0.0, step=1.0, format="%.2f")
                taxa_coordenacao = st.number_input("Taxa de Coordenação/GP (%)", value=st.session_state.config_financeiras.get("taxa_coordenacao", defaults["taxa_coordenacao"]), min_value=0.0, step=0.5, format="%.2f")
            
            submitted_configs = st.form_submit_button("Salvar Configurações Financeiras")

            if submitted_configs:
                novas_configs = {
                    "margem_lucro": margem_lucro, "impostos": impostos,
                    "custos_fixos": custos_fixos, "taxa_coordenacao": taxa_coordenacao
                }
                salvar_configuracoes_financeiras(db, agencia_id, novas_configs, user_info['email'])