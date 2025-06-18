# ==============================================================================
# Precify.AI MVP - Versão Final (Lógica de Autenticação Robusta)
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
    users_config, 'precify_cookie_v9', 'precify_key_v9', 30
)

# --- 5. LÓGICA DE LOGIN/REGISTRO (INFALÍVEL) ---

# Primeiro, renderiza o formulário de login na área principal.
# Esta chamada apenas mostra o widget, não tentamos desempacotar o resultado.
authenticator.login('Login', 'main')

# Agora, verificamos o estado da sessão que a biblioteca atualiza.
if st.session_state.get("authentication_status"):
    # --- SE O LOGIN FOI BEM SUCEDIDO ---
    name = st.session_state["name"]
    username = st.session_state["username"]
    
    st.sidebar.title(f"Bem-vindo, {name}!")
    authenticator.logout('Logout', 'sidebar')

    # O RESTO DO SEU APLICATIVO VAI AQUI DENTRO
    # ... (cole aqui suas funções de renderização, como render_pagina_inicial, etc.)

    st.title("Painel Principal do Precify.AI")
    st.write("Você está logado e pronto para começar!")


elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorreto(a)')
    st.session_state["authentication_status"] = None # Reseta para permitir nova tentativa

elif st.session_state.get("authentication_status") is None:
    # Lógica de Registro (Aparece se o usuário não está logado)
    try:
        if authenticator.register_user('Registrar novo usuário', preauthorization=False):
            email = st.session_state['email']
            name = st.session_state['name']
            password = st.session_state['password']
            
            # Cria o usuário no Firebase Authentication
            user = auth.create_user(email=email, password=password, display_name=name)
            
            st.success('Usuário registrado com sucesso! Por favor, faça o login.')
    except Exception as e:
        st.error(e)