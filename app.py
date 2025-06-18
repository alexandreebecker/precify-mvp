# ==============================================================================
# Precify.AI - Sprint 2: Fluxo de Orçamentação Completo
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
        dados_form = {"tipo_campanha": "Campanha Online"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo principal da campanha", help="Ex: 'Queremos uma campanha para aumentar o alcance no Instagram...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais'] = st.multiselect("Canais digitais envolvidos", ["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn", "Google Ads", "Outro"])
            dados_form['pecas_estimadas'] = st.number_input("Quantidade de peças estimadas", min_value=1, step=1, value=10)
            midia_paga = st.radio("Haverá mídia paga?", ("Não", "Sim"), horizontal=True, key="online_midia")
            dados_form['midia_paga'] = (midia_paga == "Sim")
            dados_form['verba_midia'] = 0.0
            if dados_form['midia_paga']:
                dados_form['verba_midia'] = st.number_input("Verba de mídia (R$)", min_value=0.0, step=100.0)
        with col2:
            dados_form['publico_alvo'] = st.text_area("Descreva o Público-alvo")
            dados_form['urgencia'] = st.select_slider("Urgência do projeto", ["Baixa", "Média", "Alta"], value="Média")
            today = date.today()
            periodo = st.date_input("Período da campanha", value=(today, today + timedelta(days=30)))
            if len(periodo) == 2:
                dados_form['periodo_inicio'], dados_form['periodo_fim'] = str(periodo[0]), str(periodo[1])
            pos_campanha = st.radio("Deseja acompanhamento pós-campanha?", ("Não", "Sim"), horizontal=True, key="online_pos")
            dados_form['pos_campanha'] = (pos_campanha == "Sim")
        
        if st.form_submit_button("Analisar Briefing e ir para Próximo Passo ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

def render_form_campanha_offline():
    """Renderiza o formulário de briefing para Campanha Offline."""
    with st.form(key="briefing_offline_form"):
        st.info("Detalhe a ação offline para estimarmos produção e logística.")
        dados_form = {"tipo_campanha": "Campanha Offline"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo principal da campanha", help="Ex: 'Vamos participar da feira XYZ com uma ativação de marca...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['tipo_acao_offline'] = st.selectbox("Tipo de ação offline", ["Evento", "Material Impresso", "Mídia Out-of-Home (OOH)", "Outro"])
            dados_form['local_execucao'] = st.text_input("Local de execução", help="Cidade, estado ou país")
            dados_form['prazo_execucao'] = str(st.date_input("Prazo final de execução/evento"))
        with col2:
            dados_form['publico_estimado'] = st.number_input("Público estimado (número)", min_value=0, step=100)
            prod_fisica = st.radio("Produção física necessária?", ("Não", "Sim"), horizontal=True, key="offline_prod")
            dados_form['producao_fisica'] = (prod_fisica == "Sim")
            if dados_form['producao_fisica']:
                dados_form['itens_producao'] = st.multiselect("Quais itens?", ["Banner", "Brinde", "Estande", "Impressos", "Outro"])
            terceiros = st.radio("Terceiros envolvidos?", ("Não", "Sim"), horizontal=True, key="offline_terceiros")
            dados_form['terceiros_envolvidos'] = (terceiros == "Sim")

        if st.form_submit_button("Analisar Briefing e ir para Próximo Passo ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

def render_form_campanha_360():
    """Renderiza o formulário de briefing para Campanha 360."""
    with st.form(key="briefing_360_form"):
        st.info("Detalhe a campanha integrada, envolvendo múltiplos canais.")
        dados_form = {"tipo_campanha": "Campanha 360"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo principal da campanha", help="Ex: 'Lançar nova identidade visual com campanha online, evento e mídia OOH...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais_envolvidos'] = st.multiselect("Canais envolvidos", ["Digital (Redes Sociais, Ads)", "Físico (Evento, Ativação)", "Mídia (TV, Rádio, OOH)"])
            verba_frente = st.radio("Verba definida por frente?", ("Não", "Sim"), horizontal=True, key="360_verba")
            dados_form['verba_definida_frente'] = (verba_frente == "Sim")
            if dados_form['verba_definida_frente']:
                dados_form['verba_detalhada'] = st.text_area("Detalhar verbas por frente")
        with col2:
            acompanhamento = st.radio("Acompanhamento estratégico?", ("Não", "Sim"), horizontal=True, key="360_pr")
            dados_form['acompanhamento_estrategico'] = (acompanhamento == "Sim")
            today = date.today()
            duracao = st.date_input("Duração total da campanha", value=(today, today + timedelta(days=90)))
            if len(duracao) == 2:
                dados_form['duracao_inicio'], dados_form['duracao_fim'] = str(duracao[0]), str(duracao[1])
            dados_form['segmentacao_geografica'] = st.selectbox("Segmentação geográfica", ["Local", "Regional", "Nacional"])

        if st.form_submit_button("Analisar Briefing e ir para Próximo Passo ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

def render_form_projeto_estrategico():
    """Renderiza o formulário de briefing para Projeto Estratégico."""
    with st.form(key="briefing_estrategico_form"):
        st.info("Descreva o desafio de negócio ou de marca a ser resolvido.")
        dados_form = {"tipo_campanha": "Projeto Estratégico"}
        dados_form['desafio_principal'] = st.text_area("Qual o desafio principal?", help="Ex: 'Estamos sofrendo com imagem negativa e queremos reverter a percepção pública.'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            acoes_anteriores = st.radio("Já existem ações anteriores?", ("Não", "Sim"), horizontal=True, key="estrategico_acoes")
            if acoes_anteriores == "Sim":
                dados_form['detalhes_acoes_anteriores'] = st.text_area("Descreva ou envie link", key="estrategico_detalhes")
            dados_form['apoio_estrategico_criativo'] = (st.radio("Precisa de apoio estratégico criativo?", ("Não", "Sim"), horizontal=True) == "Sim")
            dados_form['diagnostico_reputacao'] = (st.radio("Requer diagnóstico de reputação?", ("Não", "Sim"), horizontal=True) == "Sim")
        with col2:
            dados_form['imprensa_influenciadores'] = st.multiselect("Envolve imprensa/influenciadores?", ["Assesoria de Imprensa", "Marketing de Influência", "Relações Públicas"])
            verba_disponivel = st.radio("Verba disponível?", ("Não", "Sim"), horizontal=True, key="estrategico_verba")
            dados_form['verba_disponivel'] = (verba_disponivel == "Sim")
            if dados_form['verba_disponivel']:
                dados_form['valor_verba'] = st.number_input("Valor da verba (R$)", min_value=0.0, step=1000.0)

        if st.form_submit_button("Analisar Briefing e ir para Próximo Passo ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

# --- 3. FUNÇÕES DE DADOS (FIRESTORE) E AUTH ---
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

# ... (outras funções de dados do Sprint 1, como registrar_log_alteracao, etc., devem estar aqui) ...

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

    if 'current_view' not in st.session_state: st.session_state.current_view = "Painel Principal"
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento", "Configurações"], key="navigation")

    if st.session_state.current_view == "Novo Orçamento" and view != "Novo Orçamento":
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith(('orcamento_', 'dados_briefing'))]
        for key in keys_to_delete: del st.session_state[key]
    st.session_state.current_view = view

    # --- ROTEAMENTO DE TELAS ---
    if view == "Painel Principal":
        st.header("Painel Principal")
        st.write("Em breve: um dashboard com seus principais KPIs e orçamentos recentes.")

    elif view == "Novo Orçamento":
        st.header("🚀 Iniciar Novo Orçamento")
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1

        if st.session_state.orcamento_step == 1:
            st.caption("Selecione o tipo de projeto para carregar o formulário de briefing correto.")
            categorias = ["Selecione...", "Campanha Online", "Campanha Offline", "Campanha 360", "Projeto Estratégico"]
            categoria_escolhida = st.selectbox("Tipo de Campanha", options=categorias, index=0)
            if st.button("Iniciar Orçamento", disabled=(categoria_escolhida == "Selecione...")):
                st.session_state.orcamento_categoria = categoria_escolhida
                st.session_state.orcamento_step = 2
                st.rerun()

        elif st.session_state.orcamento_step == 2:
            categoria = st.session_state.get('orcamento_categoria', 'N/A')
            st.subheader(f"Briefing para: {categoria}")
            if categoria == "Campanha Online": render_form_campanha_online()
            elif categoria == "Campanha Offline": render_form_campanha_offline()
            elif categoria == "Campanha 360": render_form_campanha_360()
            elif categoria == "Projeto Estratégico": render_form_projeto_estrategico()

            if st.button("⬅️ Voltar e escolher outra categoria"):
                st.session_state.orcamento_step = 1
                del st.session_state.orcamento_categoria
                st.rerun()
        
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
        st.info("Aqui entra todo o código da tela de Configurações (CRUD de Perfis, Configs Financeiras, Histórico).")
        # O código completo da tela de configurações, que já funciona, deve ser inserido aqui.