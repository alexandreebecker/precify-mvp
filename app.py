# ==============================================================================
# Precify.AI MVP - Sprint 1: Implementação do Fluxo Principal de 4 Telas
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

# --- 2. FUNÇÃO DE CONEXÃO COM FIREBASE ---
@st.cache_resource
def initialize_firebase():
    """Inicializa a conexão com o Firebase de forma segura."""
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

# --- 4. FUNÇÕES DE AUTENTICAÇÃO ---
def sign_up(email, password, name):
    """Cria um novo usuário no Firebase Authentication."""
    try:
        auth.create_user(email=email, password=password, display_name=name)
        st.success("Usuário registrado com sucesso! Por favor, faça o login.")
        time.sleep(2); st.rerun()
    except Exception as e: st.error(f"Erro no registro: {e}")

# --- 5. FUNÇÕES DE RENDERIZAÇÃO DAS TELAS DO FLUXO ---

def render_tela1_categoria():
    st.header("Passo 1: Selecione a Categoria do Projeto")
    st.write("Escolher a categoria principal ajuda a IA a adaptar o formulário e a estimativa.")
    
    categorias = ["Online", "Offline", "360 (Integrado)", "Estratégico"]
    
    # Usando colunas para um layout mais agradável
    col1, col2 = st.columns(2)
    with col1:
        if st.button(categorias[0], use_container_width=True):
            st.session_state.categoria_selecionada = categorias[0]
            st.session_state.view = 'tela2_briefing'
            st.rerun()
        if st.button(categorias[2], use_container_width=True):
            st.session_state.categoria_selecionada = categorias[2]
            st.session_state.view = 'tela2_briefing'
            st.rerun()
    with col2:
        if st.button(categorias[1], use_container_width=True):
            st.session_state.categoria_selecionada = categorias[1]
            st.session_state.view = 'tela2_briefing'
            st.rerun()
        if st.button(categorias[3], use_container_width=True):
            st.session_state.categoria_selecionada = categorias[3]
            st.session_state.view = 'tela2_briefing'
            st.rerun()

def render_tela2_briefing():
    categoria = st.session_state.get('categoria_selecionada', 'N/A')
    st.header(f"Passo 2: Briefing do Projeto ({categoria})")
    
    if st.button("← Voltar e trocar categoria"):
        st.session_state.view = 'tela1_categoria'
        st.rerun()

    with st.form("briefing_form"):
        st.write("**Descreva o projeto:**")
        briefing_texto = st.text_area("Cole o briefing ou descreva a necessidade do cliente", height=200)
        
        st.divider()
        st.write("**Detalhes estruturados:**")
        # Formulário dinâmico (placeholder por enquanto)
        if categoria == "Online":
            st.multiselect("Canais Digitais", ["Instagram", "Google Ads", "TikTok"])
        elif categoria == "Offline":
            st.multiselect("Mídia Offline", ["Revista", "Rádio", "Outdoor"])
        
        prazo = st.date_input("Prazo desejado", min_value=datetime.date.today())
        
        submitted = st.form_submit_button("Analisar Briefing e Propor Escopo", type="primary")
    
    if submitted and briefing_texto:
        st.session_state.briefing_data = {"texto": briefing_texto, "prazo": prazo}
        st.session_state.view = 'tela3_analise_ia'
        st.rerun()
    elif submitted:
        st.warning("Por favor, preencha o campo de briefing.")

def render_tela3_analise_ia():
    st.header("Passo 3: Análise da IA e Escopo Sugerido")
    with st.status("Analisando briefing com LLM...", expanded=True) as status:
        time.sleep(2)
        st.write("Interpretando complexidade...")
        time.sleep(1)
        st.write("Propondo escopo de entregáveis...")
        time.sleep(2)
        status.update(label="Análise completa!", state="complete", expanded=False)

    st.success("A IA interpretou o briefing e sugeriu o escopo abaixo.")
    
    # Placeholder para o escopo sugerido pela IA
    st.session_state.escopo_sugerido = {
        "Tipo de Projeto Detectado": "Campanha de Lançamento",
        "Complexidade": "Média",
        "Entregáveis Sugeridos": ["10 Posts para Instagram", "3 Anúncios em Vídeo", "1 Landing Page"]
    }
    st.json(st.session_state.escopo_sugerido)
    
    if st.button("Aceitar Escopo e Gerar Orçamento", type="primary"):
        st.session_state.view = 'tela4_ajustes'
        st.rerun()

def render_tela4_ajustes():
    st.header("Passo 4: Ajustes e Orçamento Completo")
    if st.button("← Voltar para Análise"):
        st.session_state.view = 'tela3_analise_ia'
        st.rerun()

    st.subheader("Orçamento Estimado")
    st.info("Aqui você poderá ajustar horas, margens e valores. (Funcionalidade em desenvolvimento)")
    
    # Placeholder para a tabela de custos
    data = {'Item': ['Criação', 'Mídia Paga', 'Gestão'], 'Custo Estimado': [2500, 5000, 1200]}
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    st.success("Orçamento final gerado!")

# --- 6. ROTEAMENTO PRINCIPAL ---
# Inicializa o estado da sessão
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'view' not in st.session_state: st.session_state.view = 'tela1_categoria'

# Se a conexão com o banco falhou, para tudo
if not db: st.stop()

# Roteador: Decide se mostra a tela de Login ou o App
if not st.session_state.logged_in:
    # --- TELA DE LOGIN / REGISTRO ---
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
                except Exception: st.error("Usuário não encontrado.")
    else:
        with st.form("register_form"):
            name = st.text_input("Nome"); email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    # --- APLICAÇÃO PRINCIPAL (QUANDO O USUÁRIO ESTÁ LOGADO) ---
    user_info = st.session_state.user_info
    
    # Barra lateral
    st.sidebar.title(f"Olá, {user_info['name'].split()[0]}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.clear(); st.rerun()
    st.sidebar.divider()
    st.sidebar.write(f"**Projeto Atual:**")
    st.sidebar.write(f"Categoria: `{st.session_state.get('categoria_selecionada', 'Nenhuma')}`")
    
    # Roteamento de telas internas
    view = st.session_state.get('view')
    if view == 'tela1_categoria':
        render_tela1_categoria()
    elif view == 'tela2_briefing':
        render_tela2_briefing()
    elif view == 'tela3_analise_ia':
        render_tela3_analise_ia()
    elif view == 'tela4_ajustes':
        render_tela4_ajustes()
    else:
        # Fallback para a primeira tela se o estado for perdido
        render_tela1_categoria()