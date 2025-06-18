# ==============================================================================
# Precify.AI - Sprint 1: Implementação do Painel de Configurações
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA E FUNÇÕES ESSENCIAIS ---
st.set_page_config(page_title="Configurações - Precify.AI", layout="wide", initial_sidebar_state="auto")

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
    """Cria um novo usuário no Firebase Authentication."""
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        # Ao criar um usuário, também criamos um documento de agência para ele
        db.collection('agencias').document(user.uid).set({'nome': f"Agência de {name}", 'uid_admin': user.uid})
        st.success("Usuário e Agência registrados com sucesso! Por favor, faça o login.")
    except Exception as e: st.error(f"Erro no registro: {e}")

# --- 2. INICIALIZAÇÃO E AUTENTICAÇÃO ---
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
                    user = auth.get_user_by_email(email) # Valida se o usuário existe
                    st.session_state.logged_in = True
                    st.session_state.user_info = {"name": user.display_name, "email": user.email, "uid": user.uid}
                    st.rerun()
                except Exception: st.error("Usuário não encontrado.")
    else:
        with st.form("register_form"):
            name = st.text_input("Seu Nome"); email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    # --- APLICAÇÃO PRINCIPAL (Área Logada) ---
    user_info = st.session_state.user_info
    
    # --- BARRA LATERAL DE NAVEGAÇÃO ---
    st.sidebar.title(f"Olá, {user_info.get('name', '').split()[0]}!")
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
        st.write("Defina os perfis de equipe e os custos que alimentarão os orçamentos.")

        agencia_id = user_info['uid'] # Usamos o UID do admin como ID do documento da agência

        # --- SEÇÃO PARA ADICIONAR NOVO PERFIL ---
        st.subheader("Adicionar Novo Perfil de Equipe")
        with st.form("new_profile_form", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            funcao = col1.text_input("Nome da Função/Cargo", placeholder="Ex: Designer Gráfico Sênior")
            custo_hora = col2.number_input("Custo por Hora (R$)", min_value=0.0, step=5.0, format="%.2f")
            submitted = st.form_submit_button("Adicionar Perfil")

            if submitted and funcao and custo_hora > 0:
                novo_perfil = {"funcao": funcao, "custo_hora": custo_hora}
                db.collection('agencias').document(agencia_id).collection('perfis_equipe').add(novo_perfil)
                st.toast(f"Perfil '{funcao}' adicionado com sucesso!", icon="✅")
        
        st.divider()

        # --- SEÇÃO PARA VISUALIZAR E DELETAR PERFIS EXISTENTES ---
        st.subheader("Perfis de Equipe Cadastrados")
        
        perfis_ref = db.collection('agencias').document(agencia_id).collection('perfis_equipe').stream()
        perfis_lista = [doc for doc in perfis_ref] # Converte o gerador para uma lista

        if not perfis_lista:
            st.info("Nenhum perfil cadastrado. Adicione seu primeiro perfil no formulário acima.")
        else:
            # Criando colunas para o layout de tabela
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write("**Função**")
            col2.write("**Custo/Hora**")
            col3.write("**Ação**")

            for perfil_doc in perfis_lista:
                perfil_data = perfil_doc.to_dict()
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.text(perfil_data.get("funcao", "N/A"))
                    col2.text(f"R$ {perfil_data.get('custo_hora', 0):.2f}")
                    if col3.button("Deletar", key=perfil_doc.id, type="primary"):
                        db.collection('agencias').document(agencia_id).collection('perfis_equipe').document(perfil_doc.id).delete()
                        st.toast(f"Perfil '{perfil_data.get('funcao')}' deletado.")
                        st.rerun() # Recarrega para atualizar a lista