# ==============================================================================
# Precify.AI MVP - Versão da Vitória (Login/Registro Infalível)
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
        st.error(f"FALHA NA CONEXÃO: Verifique seus Secrets. Erro: {e}")
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
    users_config, 'precify_cookie_v6', 'precify_key_v6', 30
)

# --- 5. LÓGICA DE LOGIN/REGISTRO (A MAIS SIMPLES POSSÍVEL) ---
name, authentication_status, username = authenticator.login()

if authentication_status:
    # --- APP PRINCIPAL (QUANDO O USUÁRIO ESTÁ LOGADO) ---
    st.sidebar.title(f"Bem-vindo, {name}!")
    authenticator.logout()

    st.title("Painel Principal do Precify.AI")
    st.write("Você está logado e pronto para começar!")
    # Aqui entra o seu roteamento de páginas (render_pagina_inicial, etc.)

elif authentication_status == False:
    st.error('Usuário ou senha incorreto(a)')

elif authentication_status == None:
    st.title("Bem-vindo ao Precify.AI")
    st.warning('Por favor, faça o login ou registre-se.')
    
    # Lógica de Registro de Novo Usuário (Simplificada)
    try:
        if authenticator.register_user("Registrar novo usuário"):
            email = st.session_state['email']
            name = st.session_state['name']
            password = st.session_state['password']
            
            # Cria o usuário no Firebase Authentication
            user = auth.create_user(email=email, password=password, display_name=name)
            
            st.success('Usuário registrado com sucesso! Por favor, recarregue a página e faça o login.')
    except Exception as e:
        st.error(e)