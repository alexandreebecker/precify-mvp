# ==============================================================================
# Precify.AI - Sprint 2: Tela de Alocação de Horas
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
    sugestoes = {
        "Campanha Online": ["Criação de Key Visual (KV)", "Produção de Posts", "Produção de Vídeos (Reels)", "Gerenciamento de Tráfego", "Relatório de Performance"],
        "Campanha Offline": ["Identidade Visual do Evento", "Material Gráfico", "Ativação de Marca", "Produção de Brindes"],
        "Campanha 360": ["Planejamento Estratégico", "Conceito Criativo", "Desdobramento de Peças", "Plano de Mídia"],
        "Projeto Estratégico": ["Diagnóstico de Marca", "Planejamento de Crise", "Plataforma de Comunicação", "Assessoria de Imprensa"]
    }
    return sugestoes.get(categoria, ["Definição do Escopo"])

# ... (Todas as funções render_form_* permanecem aqui) ...
def render_form_campanha_online():
    # ... código completo ...
    pass
def render_form_campanha_offline():
    # ... código completo ...
    pass
def render_form_campanha_360():
    # ... código completo ...
    pass
def render_form_projeto_estrategico():
    # ... código completo ...
    pass


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

@st.cache_data(ttl=300)
def carregar_perfis_equipe(_db_client, agencia_id):
    """Carrega os perfis de equipe do Firestore e armazena em cache."""
    try:
        perfis_ref = _db_client.collection('agencias').document(agencia_id).collection('perfis_equipe').stream()
        perfis = [{"id": doc.id, **doc.to_dict()} for doc in perfis_ref]
        return perfis
    except Exception as e:
        st.error(f"Erro ao carregar perfis de equipe: {e}")
        return []

def sign_up(email, password, name):
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        db.collection('agencias').document(user.uid).set({'nome': f"Agência de {name}", 'uid_admin': user.uid})
        st.success("Usuário e Agência registrados! Por favor, faça o login.")
    except Exception as e: st.error(f"Erro no registro: {e}")

# ... (outras funções de dados do Sprint 1, como registrar_log_alteracao, etc., devem estar aqui) ...

# --- 4. INICIALIZAÇÃO E LÓGICA DE LOGIN ---
db = initialize_firebase()
if db is None: st.stop()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # ... (Código de Login/Registro) ...
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
    agencia_id = user_info['uid']

    nome_display = user_info.get('name')
    saudacao = f"Olá, {nome_display.split()[0]}!" if nome_display and nome_display.strip() else "Olá!"
    st.sidebar.title(saudacao)
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.sidebar.divider()
    if 'current_view' not in st.session_state: st.session_state.current_view = "Painel Principal"
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento", "Configurações"], key="navigation")
    
    # Lógica de reset do fluxo
    if st.session_state.current_view == "Novo Orçamento" and view != "Novo Orçamento":
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith(('orcamento_', 'dados_briefing', 'entregaveis'))]
        for key in keys_to_delete: del st.session_state[key]
    st.session_state.current_view = view

    # --- ROTEAMENTO DE TELAS ---
    if view == "Painel Principal":
        st.header("Painel Principal")
        st.write("Em breve.")
    
    elif view == "Novo Orçamento":
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1
        
        # ETAPAS 1, 2, 3 (sem mudanças)
        if st.session_state.orcamento_step in [1, 2, 3]:
            # ... (Coloque o código das etapas 1, 2 e 3 aqui, conforme a versão anterior) ...
            st.info("Etapas 1, 2 e 3 (Seleção, Briefing, Validação de Escopo) estão aqui.")

        # ETAPA 4: ALOCAÇÃO DE HORAS
        elif st.session_state.orcamento_step == 4:
            st.header("👨‍💻 Alocação de Horas por Entregável")
            st.info("Para cada entregável do escopo, adicione os perfis da equipe e a estimativa de horas.")

            perfis_equipe = carregar_perfis_equipe(db, agencia_id)
            if not perfis_equipe:
                st.warning("Nenhum perfil de equipe cadastrado. Por favor, vá em 'Configurações' para adicionar perfis antes de continuar.")
                st.stop()
            
            nomes_perfis = [p['funcao'] for p in perfis_equipe]

            total_horas_orcamento = 0
            for i, entregavel in enumerate(st.session_state.entregaveis):
                if 'alocacoes' not in entregavel:
                    entregavel['alocacoes'] = []
                
                total_horas_entregavel = sum(aloc['horas'] for aloc in entregavel['alocacoes'])
                total_horas_orcamento += total_horas_entregavel
                
                with st.expander(f"**{i+1}. {entregavel['descricao']}** - ({total_horas_entregavel}h totais)"):
                    st.write("Alocações atuais:")
                    if not entregavel['alocacoes']:
                        st.caption("Nenhum perfil alocado.")
                    else:
                        for j, aloc in enumerate(entregavel['alocacoes']):
                            c1, c2, c3 = st.columns([2,1,1])
                            c1.write(f"• **Perfil:** {aloc['perfil_funcao']}")
                            c2.write(f"**Horas:** {aloc['horas']}")
                            if c3.button("Remover", key=f"rem_aloc_{i}_{j}", type="primary"):
                                st.session_state.entregaveis[i]['alocacoes'].pop(j)
                                st.rerun()
                    
                    st.divider()
                    st.write("**Adicionar nova alocação:**")
                    c1, c2, c3 = st.columns([2,1,1])
                    perfil_selecionado = c1.selectbox("Perfil", options=nomes_perfis, key=f"sel_perfil_{i}", index=None, placeholder="Selecione um perfil")
                    horas_estimadas = c2.number_input("Horas", min_value=0.5, step=0.5, key=f"num_horas_{i}")
                    if c3.button("Adicionar", key=f"add_aloc_{i}", use_container_width=True, disabled=not perfil_selecionado):
                        perfil_data = next((p for p in perfis_equipe if p['funcao'] == perfil_selecionado), None)
                        if perfil_data:
                            nova_alocacao = {
                                "perfil_id": perfil_data['id'],
                                "perfil_funcao": perfil_data['funcao'],
                                "custo_hora": perfil_data['custo_hora'],
                                "horas": horas_estimadas
                            }
                            st.session_state.entregaveis[i]['alocacoes'].append(nova_alocacao)
                            st.rerun()
            
            st.divider()
            st.header(f"Total de Horas Estimadas: {total_horas_orcamento}h")
            
            c1, c2 = st.columns(2)
            c1.button("⬅️ Editar Escopo", on_click=lambda: st.session_state.update(orcamento_step=3))
            c2.button("Calcular Orçamento Preliminar ➡️", type="primary", use_container_width=True, disabled=(total_horas_orcamento==0), on_click=lambda: st.session_state.update(orcamento_step=5))

        # ETAPA 5: ORÇAMENTO FINAL (Placeholder)
        elif st.session_state.orcamento_step == 5:
            st.header("📊 Orçamento Preliminar")
            st.info("Próximo passo: Calcular todos os custos com base nas horas e perfis, aplicar as margens e exibir o resultado final.")
            
            with st.expander("Dados de Alocação para Cálculo"):
                st.json(st.session_state.get('entregaveis', []))

            st.button("⬅️ Editar Alocação de Horas", on_click=lambda: st.session_state.update(orcamento_step=4))

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência")
        st.caption("Defina os perfis de equipe e as margens que alimentarão seus orçamentos.")
        # O código completo da tela de configurações, que já funciona, deve ser inserido aqui.
        st.info("Aqui entra todo o código da tela de Configurações (CRUD de Perfis, Configs Financeiras, Histórico).")
        # Por favor, substitua esta linha pelo código completo da view de configurações que já temos.