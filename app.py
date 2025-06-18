# ==============================================================================
# Precify.AI MVP - Sprint 1: Implementação do Fluxo Principal de 4 Telas
# Versão Limpa, Corrigida e Completa
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json
import time
import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando do Streamlit) ---
st.set_page_config(page_title="Precify.AI", layout="wide", initial_sidebar_state="auto")

# --- 2. FUNÇÃO DE CONEXÃO COM O FIREBASE (Robusta e com Cache) ---
@st.cache_resource
def initialize_firebase():
    """
    Inicializa a conexão com o Firebase de forma segura usando st.secrets.
    Retorna o cliente do Firestore ou None se a conexão falhar.
    """
    try:
        creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e:
        st.error(f"FALHA NA CONEXÃO COM O FIREBASE: Verifique seus Secrets. Erro: {e}")
        return None

# --- 3. INICIALIZAÇÃO DA CONEXÃO ---
db = initialize_firebase()

# --- 4. FUNÇÕES DO APLICATIVO ---

def sign_up(email, password, name):
    """Cria um novo usuário no Firebase Authentication."""
    try:
        auth.create_user(email=email, password=password, display_name=name)
        st.success("Usuário registrado com sucesso! Por favor, faça o login.")
        time.sleep(2)
        st.rerun()
    except Exception as e:
        st.error(f"Erro no registro: {e}")

# --- FUNÇÕES DE RENDERIZAÇÃO PARA CADA TELA ---

def render_tela1_categoria():
    st.header("Passo 1: Selecione a Categoria do Projeto")
    st.write("Escolher a categoria principal ajuda a IA a adaptar o formulário e a estimativa.")
    
    categorias = ["Online", "Offline", "360 (Integrado)", "Estratégico"]
    
    col1, col2 = st.columns(2)
    colunas = [col1, col2]
    
    for i, categoria in enumerate(categorias):
        with colunas[i % 2]:
            if st.button(categoria, use_container_width=True, key=f"cat_{categoria}"):
                st.session_state.categoria_selecionada = categoria
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
        else:
            st.info("Campos específicos para esta categoria aparecerão aqui.")
        
        prazo = st.date_input("Prazo desejado", min_value=datetime.date.today())
        
        submitted = st.form_submit_button("Analisar Briefing e Propor Escopo", type="primary")
    
    if submitted:
        if briefing_texto:
            st.session_state.briefing_data = {"texto": briefing_texto, "prazo": prazo}
            st.session_state.view = 'tela3_analise_ia'
            st.rerun()
        else:
            st.warning("Por favor, preencha o campo de briefing.")

def render_tela3_analise_ia():
    st.header("Passo 3: Análise da IA e Escopo Sugerido")
    with st.status("Analisando briefing com LLM...", expanded=True) as status:
        time.sleep(1); st.write("Interpretando complexidade...");
        time.sleep(1); st.write("Propondo escopo de entregáveis...");
        time.sleep(1); status.update(label="Análise completa!", state="complete", expanded=False)

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
    
    data = {'Item': ['Criação', 'Mídia Paga', 'Gestão'], 'Custo Estimado': [2500, 5000, 1200]}
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    st.success("Orçamento final gerado!")

# --- 5. LÓGICA DE EXECUÇÃO E ROTEAMENTO ---

# Se a conexão com o banco falhou, para o app.
if not db:
    st.error("A conexão com o banco de dados falhou. O aplicativo não pode continuar.")
    st.stop()

# Inicializa o estado da sessão
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'view' not in st.session_state: st.session_state.view = 'tela1_categoria'

# Roteador Principal: Decide se mostra a tela de Login ou o App
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
    else: # Registrar
        with st.form("register_form"):
            name = st.text_input("Nome"); email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    # --- APLICAÇÃO PRINCIPAL (QUANDO O USUÁRIO ESTÁ LOGADO) ---
    user_info = st.session_state.user_info
    
    # Lógica de saudação segura
    nome_display = user_info.get('name')
    saudacao = f"Olá, {nome_display.split()[0]}" if nome_display else "Olá!"
    st.sidebar.title(saudacao)

    if st.sidebar.button("Logout"):
        # Limpa todo o estado da sessão para um logout completo
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
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
        # Se nenhum estado de 'view' for encontrado, volta para a primeira tela.
        render_tela1_categoria()