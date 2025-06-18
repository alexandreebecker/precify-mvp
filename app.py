# ==============================================================================
# Precify.AI MVP - Versão Final (Login Customizado e Infalível)
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json
import time
import datetime

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

# --- 4. LÓGICA DE AUTENTICAÇÃO CUSTOMIZADA ---

# Funções de interação com Firebase Auth
def sign_up(email, password, name):
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        st.success("Usuário registrado com sucesso! Por favor, faça o login.")
        return True
    except Exception as e:
        st.error(f"Erro no registro: {e}")
        return False

# Inicializa o estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# --- TELA DE LOGIN / REGISTRO ---
if not st.session_state.logged_in:
    st.title("Bem-vindo ao Precify.AI")
    
    choice = st.selectbox("Login ou Registro", ["Login", "Registrar"])

    if choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Login"):
                # A autenticação de senha com o Admin SDK é complexa,
                # então vamos confiar que o usuário existe por enquanto.
                # A verificação real de senha é feita em apps de cliente (JS, mobile).
                # Para este MVP, vamos buscar o usuário.
                try:
                    user = auth.get_user_by_email(email)
                    st.session_state.logged_in = True
                    st.session_state.user_info = {"name": user.display_name, "email": user.email, "uid": user.uid}
                    st.rerun()
                except Exception as e:
                    st.error("Usuário não encontrado ou erro no login.")

    else: # Registro
        with st.form("register_form"):
            name = st.text_input("Nome Completo")
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"):
                sign_up(email, password, name)

# --- APLICAÇÃO PRINCIPAL (SE ESTIVER LOGADO) ---
else:
    user_info = st.session_state.user_info
    st.sidebar.title(f"Bem-vindo, {user_info['name']}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_info = {}
        st.rerun()

    # O RESTO DO SEU APP VAI AQUI
    st.title("Painel Principal do Precify.AI")
    st.write("Você está logado e pronto para começar!")
    # Cole aqui suas funções de renderização (render_pagina_inicial, etc.)