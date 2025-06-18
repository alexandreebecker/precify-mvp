# ==============================================================================
# Precify.AI - Sprint 2: Tela de Validação de Escopo
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json
from datetime import date, timedelta

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precify.AI", layout="wide", initial_sidebar_state="auto")

# --- 2. FUNÇÕES DE SUPORTE E RENDERIZAÇÃO ---

def get_sugestoes_entregaveis(categoria):
    """Simula a IA, sugerindo entregáveis com base na categoria do projeto."""
    sugestoes = {
        "Campanha Online": ["Criação de Key Visual (KV) da Campanha", "Produção de 10 Posts Estáticos para Feed", "Produção de 2 Vídeos (Reels/Shorts)", "Gerenciamento de Tráfego Pago", "Relatório de Performance Mensal"],
        "Campanha Offline": ["Criação de Identidade Visual do Evento", "Produção de Material Gráfico (Flyers, Banners)", "Planejamento e Execução de Ativação de Marca", "Produção de Brindes"],
        "Campanha 360": ["Planejamento Estratégico Integrado (Online/Offline)", "Criação de Conceito Criativo da Campanha", "Desdobramento do KV para peças Online e Offline", "Plano de Mídia Integrado", "Ação com Influenciadores"],
        "Projeto Estratégico": ["Diagnóstico de Reputação e Imagem de Marca", "Planejamento de Gestão de Crise", "Desenvolvimento de Plataforma de Comunicação", "Assessoria de Imprensa Estratégica", "Workshop de Posicionamento com C-Level"]
    }
    return sugestoes.get(categoria, ["Definição do Escopo do Projeto"])

def render_form_campanha_online():
    with st.form(key="briefing_online_form"):
        st.info("Descreva o projeto com o máximo de detalhes possível.")
        dados_form = {"tipo_campanha": "Campanha Online"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo principal da campanha", help="Ex: 'Queremos uma campanha para aumentar o alcance...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais'] = st.multiselect("Canais digitais", ["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn", "Google Ads", "Outro"])
            dados_form['pecas_estimadas'] = st.number_input("Quantidade de peças", min_value=1, step=1, value=10)
            midia_paga = st.radio("Haverá mídia paga?", ("Não", "Sim"), horizontal=True, key="online_midia")
            dados_form['midia_paga'] = (midia_paga == "Sim")
            if dados_form['midia_paga']:
                dados_form['verba_midia'] = st.number_input("Verba de mídia (R$)", min_value=0.0, step=100.0)
        with col2:
            dados_form['publico_alvo'] = st.text_area("Público-alvo")
            dados_form['urgencia'] = st.select_slider("Urgência", ["Baixa", "Média", "Alta"], value="Média")
            periodo = st.date_input("Período da campanha", value=(date.today(), date.today() + timedelta(days=30)))
            if len(periodo) == 2: dados_form['periodo_inicio'], dados_form['periodo_fim'] = str(periodo[0]), str(periodo[1])
            pos_campanha = st.radio("Acompanhamento pós-campanha?", ("Não", "Sim"), horizontal=True, key="online_pos")
            dados_form['pos_campanha'] = (pos_campanha == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

def render_form_campanha_offline():
    with st.form(key="briefing_offline_form"):
        st.info("Detalhe a ação offline para estimarmos produção e logística.")
        dados_form = {"tipo_campanha": "Campanha Offline"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo principal", help="Ex: 'Participar da feira XYZ...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['tipo_acao_offline'] = st.selectbox("Tipo de ação", ["Evento", "Material Impresso", "Mídia OOH", "Outro"])
            dados_form['local_execucao'] = st.text_input("Local de execução", help="Cidade, estado ou país")
            dados_form['prazo_execucao'] = str(st.date_input("Prazo final"))
        with col2:
            dados_form['publico_estimado'] = st.number_input("Público estimado", min_value=0, step=100)
            prod_fisica = st.radio("Produção física?", ("Não", "Sim"), horizontal=True, key="offline_prod")
            dados_form['producao_fisica'] = (prod_fisica == "Sim")
            if dados_form['producao_fisica']: dados_form['itens_producao'] = st.multiselect("Itens?", ["Banner", "Brinde", "Estande"])
            terceiros = st.radio("Terceiros envolvidos?", ("Não", "Sim"), horizontal=True, key="offline_terceiros")
            dados_form['terceiros_envolvidos'] = (terceiros == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

def render_form_campanha_360():
    with st.form(key="briefing_360_form"):
        st.info("Detalhe a campanha integrada, envolvendo múltiplos canais.")
        dados_form = {"tipo_campanha": "Campanha 360"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo", help="Ex: 'Lançar nova identidade visual...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais_envolvidos'] = st.multiselect("Canais", ["Digital", "Físico (Evento)", "Mídia (TV, Rádio)"])
            verba_frente = st.radio("Verba por frente?", ("Não", "Sim"), horizontal=True, key="360_verba")
            if verba_frente == "Sim": dados_form['verba_detalhada'] = st.text_area("Detalhar verbas")
        with col2:
            dados_form['acompanhamento_estrategico'] = (st.radio("Acompanhamento estratégico?", ("Não", "Sim"), horizontal=True) == "Sim")
            duracao = st.date_input("Duração da campanha", value=(date.today(), date.today() + timedelta(days=90)))
            if len(duracao) == 2: dados_form['duracao_inicio'], dados_form['duracao_fim'] = str(duracao[0]), str(duracao[1])
            dados_form['segmentacao_geografica'] = st.selectbox("Segmentação", ["Local", "Regional", "Nacional"])
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form
            st.session_state.orcamento_step = 3
            st.rerun()

def render_form_projeto_estrategico():
    with st.form(key="briefing_estrategico_form"):
        st.info("Descreva o desafio de negócio ou de marca a ser resolvido.")
        dados_form = {"tipo_campanha": "Projeto Estratégico"}
        dados_form['desafio_principal'] = st.text_area("Qual o desafio?", help="Ex: 'Reverter percepção pública negativa.'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.radio("Ações anteriores?", ("Não", "Sim")) == "Sim":
                dados_form['detalhes_acoes_anteriores'] = st.text_area("Descreva")
            dados_form['apoio_estrategico_criativo'] = (st.radio("Apoio criativo?", ("Não", "Sim")) == "Sim")
            dados_form['diagnostico_reputacao'] = (st.radio("Diagnóstico de reputação?", ("Não", "Sim")) == "Sim")
        with col2:
            dados_form['imprensa_influenciadores'] = st.multiselect("Imprensa/Influencers?", ["Assesoria", "Mkt Influência"])
            if st.radio("Verba disponível?", ("Não", "Sim")) == "Sim":
                dados_form['valor_verba'] = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Analisar Briefing ➡️"):
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
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith(('orcamento_', 'dados_briefing', 'entregaveis'))]
        for key in keys_to_delete: del st.session_state[key]
    st.session_state.current_view = view

    if view == "Painel Principal":
        st.header("Painel Principal")
        st.write("Em breve.")
    
    elif view == "Novo Orçamento":
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1
        
        if st.session_state.orcamento_step == 1:
            st.header("🚀 Iniciar Novo Orçamento")
            st.caption("Selecione o tipo de projeto para carregar o formulário.")
            categorias = ["Selecione...", "Campanha Online", "Campanha Offline", "Campanha 360", "Projeto Estratégico"]
            cat = st.selectbox("Tipo de Campanha", categorias, index=0)
            if st.button("Iniciar", disabled=(cat == "Selecione...")):
                st.session_state.orcamento_categoria = cat
                st.session_state.orcamento_step = 2
                st.rerun()

        elif st.session_state.orcamento_step == 2:
            st.header(f"Briefing: {st.session_state.get('orcamento_categoria', 'N/A')}")
            cat = st.session_state.get('orcamento_categoria')
            if cat == "Campanha Online": render_form_campanha_online()
            elif cat == "Campanha Offline": render_form_campanha_offline()
            elif cat == "Campanha 360": render_form_campanha_360()
            elif cat == "Projeto Estratégico": render_form_projeto_estrategico()
            if st.button("⬅️ Voltar"):
                st.session_state.orcamento_step = 1
                del st.session_state.orcamento_categoria
                st.rerun()

        elif st.session_state.orcamento_step == 3:
            st.header("🤖 Validação do Escopo")
            st.info("Ajuste a lista de entregáveis sugerida pela IA.")
            cat = st.session_state.get('orcamento_categoria', 'N/A')
            if 'entregaveis' not in st.session_state:
                sugestoes = get_sugestoes_entregaveis(cat)
                st.session_state.entregaveis = [{"descricao": item} for item in sugestoes]
            
            c1, c2 = st.columns([3, 1])
            novo = c1.text_input("Novo entregável", placeholder="Digite e pressione 'Adicionar'", label_visibility="collapsed")
            if c2.button("Adicionar", use_container_width=True) and novo:
                st.session_state.entregaveis.append({"descricao": novo})
                st.rerun()
            st.divider()
            
            if not st.session_state.entregaveis:
                st.warning("Adicione ao menos um entregável.")
            else:
                for i, item in enumerate(st.session_state.entregaveis):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f" • {item['descricao']}")
                    if c2.button("Remover", key=f"rm_{i}", use_container_width=True):
                        st.session_state.entregaveis.pop(i)
                        st.rerun()
            st.divider()

            c1, c2 = st.columns(2)
            if c1.button("⬅️ Editar Briefing"):
                st.session_state.orcamento_step = 2
                del st.session_state.entregaveis
                st.rerun()
            if c2.button("Confirmar Escopo ➡️", type="primary", use_container_width=True, disabled=not st.session_state.entregaveis):
                st.session_state.orcamento_step = 4
                st.rerun()
        
        elif st.session_state.orcamento_step == 4:
            st.header("👨‍💻 Alocação de Horas")
            st.success("Escopo confirmado:")
            for item in st.session_state.get('entregaveis', []):
                st.write(f"- {item['descricao']}")
            st.info("Próximo passo: Alocar perfis e horas para cada entregável.")
            if st.button("⬅️ Editar Escopo"):
                st.session_state.orcamento_step = 3
                st.rerun()

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência")
        st.caption("Defina os perfis de equipe e as margens que alimentarão seus orçamentos.")
        # O código completo da tela de configurações, que já funciona, deve ser inserido aqui.
        st.info("Aqui entra todo o código da tela de Configurações (CRUD de Perfis, Configs Financeiras, Histórico).")
        # Por favor, substitua esta linha pelo código completo da view de configurações que já temos.