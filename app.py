# ==============================================================================
# Precify.AI MVP - Sprint 1 (Correção Final na Saudação)
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
        st.error(f"FALHA NA CONEXÃO COM O FIREBASE: {e}")
        return None

# --- 3. INICIALIZAÇÃO ---
db = initialize_firebase()

# --- 4. FUNÇÕES DO APLICATIVO ---
def sign_up(email, password, name):
    """Cria um novo usuário no Firebase Authentication."""
    try:
        auth.create_user(email=email, password=password, display_name=name)
        st.success("Usuário registrado com sucesso! Por favor, faça o login.")
        time.sleep(2); st.rerun()
    except Exception as e: st.error(f"Erro no registro: {e}")

def render_tela1_categoria():
    st.header("Passo 1: Selecione a Categoria do Projeto")
    categorias = ["Online", "Offline", "360 (Integrado)", "Estratégico"]
    col1, col2 = st.columns(2)
    for i, categoria in enumerate(categorias):
        col = col1 if i % 2 == 0 else col2
        if col.button(categoria, use_container_width=True, key=f"cat_{categoria}"):
            st.session_state.categoria_selecionada = categoria
            st.session_state.view = 'tela2_briefing'; st.rerun()

def render_tela2_briefing():
    # ... (código desta função e das outras 'render' permanece o mesmo)
    categoria = st.session_state.get('categoria_selecionada', 'N/A')
    st.header(f"Passo 2: Briefing do Projeto ({categoria})")
    if st.button("← Voltar e trocar categoria"): st.session_state.view = 'tela1_categoria'; st.rerun()
    with st.form("briefing_form"):
        st.write("**Descreva o projeto:**"); briefing_texto = st.text_area("...", height=200)
        st.divider(); st.write("**Detalhes estruturados:**")
        if categoria == "Online": st.multiselect("Canais Digitais", ["Instagram", "Google Ads", "TikTok"])
        elif categoria == "Offline": st.multiselect("Mídia Offline", ["Revista", "Rádio", "Outdoor"])
        else: st.info("Campos para esta categoria aqui.")
        prazo = st.date_input("Prazo desejado", min_value=datetime.date.today())
        submitted = st.form_submit_button("Analisar e Propor Escopo", type="primary")
    if submitted:
        if briefing_texto:
            st.session_state.briefing_data = {"texto": briefing_texto, "prazo": prazo}
            st.session_state.view = 'tela3_analise_ia'; st.rerun()
        else: st.warning("Preencha o briefing.")

def render_tela3_analise_ia():
    # ... (código desta função permanece o mesmo)
    st.header("Passo 3: Análise da IA e Escopo Sugerido")
    with st.status("Analisando briefing...", expanded=True) as status:
        time.sleep(1); st.write("✅ Interpretando..."); time.sleep(1)
        st.write("✅ Propondo entregáveis..."); status.update(label="Análise completa!", state="complete", expanded=False)
    st.success("A IA sugeriu o escopo abaixo.")
    if 'escopo_sugerido' not in st.session_state: st.session_state.escopo_sugerido = {"Tipo": "Campanha", "Complexidade": "Média", "Entregáveis": ["10 Posts", "3 Vídeos"]}
    st.json(st.session_state.escopo_sugerido)
    if st.button("Aceitar e Gerar Orçamento", type="primary"): st.session_state.view = 'tela4_ajustes'; st.rerun()

def render_tela4_ajustes():
    # ... (código desta função permanece o mesmo)
    st.header("Passo 4: Ajustes e Orçamento Completo")
    if st.button("← Voltar para Análise"): st.session_state.view = 'tela3_analise_ia'; st.rerun()
    st.subheader("Orçamento Estimado")
    st.info("(Funcionalidade em desenvolvimento)")
    df = pd.DataFrame({'Item': ['Criação', 'Mídia'], 'Custo': [2500, 5000]})
    st.dataframe(df, use_container_width=True)

# --- 5. LÓGICA DE EXECUÇÃO E ROTEAMENTO ---
if not db: st.error("Conexão com banco falhou."); st.stop()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'view' not in st.session_state: st.session_state.view = 'tela1_categoria'

if not st.session_state.logged_in:
    st.title("Bem-vindo ao Precify.AI")
    choice = st.selectbox("Acessar", ["Login", "Registrar"], label_visibility="collapsed")
    if choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Login"):
                try:
                    user = auth.get_user_by_email(email)
                    st.session_state.logged_in = True
                    st.session_state.user_info = {"name": user.display_name, "email": user.email, "uid": user.uid}
                    st.rerun()
                except Exception: st.error("Usuário não encontrado.")
    else:
        with st.form("register_form"):
            name = st.text_input("Nome"); email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    user_info = st.session_state.user_info
    
    # AQUI ESTÁ A CORREÇÃO FINAL:
    nome_display = user_info.get('name') # Pega o nome de forma segura
    # Se o nome existir, pega a primeira palavra. Se não, usa "Usuário".
    saudacao = f"Olá, {nome_display.split()[0]}" if nome_display else "Olá!" 
    st.sidebar.title(saudacao)
    
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.sidebar.divider()
    st.sidebar.write(f"**Projeto:** `{st.session_state.get('categoria_selecionada', 'Nenhum')}`")
    
    view = st.session_state.get('view')
    if view == 'tela1_categoria': render_tela1_categoria()
    elif view == 'tela2_briefing': render_tela2_briefing()
    elif view == 'tela3_analise_ia': render_tela3_analise_ia()
    elif view == 'tela4_ajustes': render_tela4_ajustes()
    else: render_tela1_categoria()