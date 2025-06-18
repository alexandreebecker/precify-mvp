# ==============================================================================
# Precify.AI - Sprint 2: Finalização do Fluxo de Orçamento (Código Completo)
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import json
from datetime import date, timedelta

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precify.AI", layout="wide", initial_sidebar_state="auto")

# --- 2. FUNÇÕES DE SUPORTE, RENDERIZAÇÃO E CÁLCULO ---

def get_sugestoes_entregaveis(categoria):
    sugestoes = {
        "Campanha Online": ["Criação de Key Visual (KV)", "Produção de Posts", "Produção de Vídeos (Reels)", "Gerenciamento de Tráfego", "Relatório de Performance"],
        "Campanha Offline": ["Identidade Visual do Evento", "Material Gráfico", "Ativação de Marca", "Produção de Brindes"],
        "Campanha 360": ["Planejamento Estratégico", "Conceito Criativo", "Desdobramento de Peças", "Plano de Mídia"],
        "Projeto Estratégico": ["Diagnóstico de Marca", "Planejamento de Crise", "Plataforma de Comunicação", "Assessoria de Imprensa"]
    }
    return sugestoes.get(categoria, ["Definição do Escopo"])

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
            if dados_form['midia_paga']: dados_form['verba_midia'] = st.number_input("Verba de mídia (R$)", min_value=0.0, step=100.0)
        with col2:
            dados_form['publico_alvo'] = st.text_area("Público-alvo")
            dados_form['urgencia'] = st.select_slider("Urgência", ["Baixa", "Média", "Alta"], value="Média")
            periodo = st.date_input("Período da campanha", value=(date.today(), date.today() + timedelta(days=30)))
            if len(periodo) == 2: dados_form['periodo_inicio'], dados_form['periodo_fim'] = str(periodo[0]), str(periodo[1])
            pos_campanha = st.radio("Acompanhamento pós-campanha?", ("Não", "Sim"), horizontal=True, key="online_pos")
            dados_form['pos_campanha'] = (pos_campanha == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

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
            if prod_fisica == "Sim": dados_form['itens_producao'] = st.multiselect("Itens?", ["Banner", "Brinde", "Estande"])
            dados_form['terceiros_envolvidos'] = (st.radio("Terceiros?", ("Não", "Sim"), horizontal=True) == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

def render_form_campanha_360():
    with st.form(key="briefing_360_form"):
        st.info("Detalhe a campanha integrada, envolvendo múltiplos canais.")
        dados_form = {"tipo_campanha": "Campanha 360"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo", help="Ex: 'Lançar nova identidade visual...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais_envolvidos'] = st.multiselect("Canais", ["Digital", "Físico (Evento)", "Mídia (TV, Rádio)"])
            if st.radio("Verba por frente?", ("Não", "Sim"), horizontal=True) == "Sim": dados_form['verba_detalhada'] = st.text_area("Detalhar verbas")
        with col2:
            dados_form['acompanhamento_estrategico'] = (st.radio("Acompanhamento?", ("Não", "Sim"), horizontal=True) == "Sim")
            duracao = st.date_input("Duração", value=(date.today(), date.today() + timedelta(days=90)))
            if len(duracao) == 2: dados_form['duracao_inicio'], dados_form['duracao_fim'] = str(duracao[0]), str(duracao[1])
            dados_form['segmentacao_geografica'] = st.selectbox("Segmentação", ["Local", "Regional", "Nacional"])
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

def render_form_projeto_estrategico():
    with st.form(key="briefing_estrategico_form"):
        st.info("Descreva o desafio de negócio ou de marca a ser resolvido.")
        dados_form = {"tipo_campanha": "Projeto Estratégico"}
        dados_form['desafio_principal'] = st.text_area("Qual o desafio?", help="Ex: 'Reverter percepção pública negativa.'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.radio("Ações anteriores?", ("Não", "Sim")) == "Sim": dados_form['detalhes_acoes_anteriores'] = st.text_area("Descreva")
            dados_form['apoio_estrategico_criativo'] = (st.radio("Apoio criativo?", ("Não", "Sim")) == "Sim")
            dados_form['diagnostico_reputacao'] = (st.radio("Diagnóstico?", ("Não", "Sim")) == "Sim")
        with col2:
            dados_form['imprensa_influenciadores'] = st.multiselect("Imprensa/Influencers?", ["Assessoria", "Mkt Influência"])
            if st.radio("Verba disponível?", ("Não", "Sim")) == "Sim": dados_form['valor_verba'] = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

def calcular_orcamento(entregaveis, configs):
    custo_total_equipe = sum(aloc['horas'] * aloc['custo_hora'] for entr in entregaveis for aloc in entr.get('alocacoes', []))
    taxa_coord_percent = configs.get('taxa_coordenacao', 0)/100; custos_fixos_percent = configs.get('custos_fixos', 0)/100
    margem_lucro_percent = configs.get('margem_lucro', 0)/100; impostos_percent = configs.get('impostos', 0)/100
    custo_com_coord = custo_total_equipe * (1 + taxa_coord_percent); custo_com_fixos = custo_com_coord * (1 + custos_fixos_percent)
    valor_lucro = custo_com_fixos * margem_lucro_percent; subtotal_antes_impostos = custo_com_fixos + valor_lucro
    valor_impostos = subtotal_antes_impostos * impostos_percent; valor_total_cliente = subtotal_antes_impostos + valor_impostos
    return {"custo_total_equipe": custo_total_equipe, "valor_taxa_coordenacao": custo_com_coord - custo_total_equipe,
            "valor_custos_fixos": custo_com_fixos - custo_com_coord, "subtotal_antes_lucro": custo_com_fixos,
            "valor_lucro": valor_lucro, "subtotal_antes_impostos": subtotal_antes_impostos, "valor_impostos": valor_impostos,
            "valor_total_cliente": valor_total_cliente}

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
    try:
        perfis_ref = _db_client.collection('agencias').document(agencia_id).collection('perfis_equipe').stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in perfis_ref]
    except Exception as e:
        st.error(f"Erro ao carregar perfis: {e}"); return []

@st.cache_data(ttl=300)
def carregar_configuracoes_financeiras(_db_client, agencia_id):
    try:
        doc = _db_client.collection('agencias').document(agencia_id).get()
        return doc.to_dict().get('configuracoes_financeiras', {}) if doc.exists else {}
    except Exception as e:
        st.error(f"Erro ao carregar configs: {e}"); return {}

def salvar_orcamento_firestore(db_client, agencia_id, user_info, dados_orcamento):
    try:
        db_client.collection('orçamentos').add({"agencia_id": agencia_id, "uid_criador": user_info['uid'], "email_criador": user_info['email'], "data_orcamento": firestore.SERVER_TIMESTAMP, **dados_orcamento})
        return True
    except Exception as e:
        st.error(f"Falha ao salvar o orçamento: {e}"); return False

def sign_up(email, password, name):
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        db.collection('agencias').document(user.uid).set({'nome': f"Agência de {name}", 'uid_admin': user.uid})
        st.success("Usuário e Agência registrados! Por favor, faça o login.")
    except Exception as e: st.error(f"Erro no registro: {e}")

# --- 4. INICIALIZAÇÃO E LÓGICA DE LOGIN ---
db = initialize_firebase()
if db is None: st.stop()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Bem-vindo ao Precify.AI"); choice = st.selectbox("Acessar", ["Login", "Registrar"], label_visibility="collapsed")
    if choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Login"):
                try:
                    user = auth.get_user_by_email(email); st.session_state.logged_in = True
                    st.session_state.user_info = {"name": user.display_name, "email": user.email, "uid": user.uid}; st.rerun()
                except Exception: st.error("Credenciais inválidas.")
    else:
        with st.form("register_form"):
            name = st.text_input("Nome"); email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    # ==================================================
    # --- APLICAÇÃO PRINCIPAL (Área Logada) ---
    # ==================================================
    user_info = st.session_state.user_info; agencia_id = user_info['uid']
    nome_display = user_info.get('name'); saudacao = f"Olá, {nome_display.split()[0]}!" if nome_display and nome_display.strip() else "Olá!"
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
        st.header("Painel Principal"); st.write("Em breve.")
    
    elif view == "Novo Orçamento":
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1
        
        if st.session_state.orcamento_step == 1:
            st.header("🚀 Iniciar Novo Orçamento"); st.caption("Selecione o tipo de projeto.")
            categorias = ["Selecione...", "Campanha Online", "Campanha Offline", "Campanha 360", "Projeto Estratégico"]
            cat = st.selectbox("Tipo de Campanha", categorias)
            if st.button("Iniciar", disabled=(cat == "Selecione...")):
                st.session_state.orcamento_categoria = cat; st.session_state.orcamento_step = 2; st.rerun()

        elif st.session_state.orcamento_step == 2:
            st.header(f"Briefing: {st.session_state.get('orcamento_categoria', 'N/A')}")
            cat = st.session_state.get('orcamento_categoria');
            if cat == "Campanha Online": render_form_campanha_online()
            elif cat == "Campanha Offline": render_form_campanha_offline()
            elif cat == "Campanha 360": render_form_campanha_360()
            elif cat == "Projeto Estratégico": render_form_projeto_estrategico()
            if st.button("⬅️ Voltar"):
                st.session_state.orcamento_step = 1; del st.session_state.orcamento_categoria; st.rerun()

        elif st.session_state.orcamento_step == 3:
            st.header("🤖 Validação do Escopo"); st.info("Ajuste a lista de entregáveis sugerida.")
            cat = st.session_state.get('orcamento_categoria', 'N/A')
            if 'entregaveis' not in st.session_state:
                st.session_state.entregaveis = [{"descricao": item} for item in get_sugestoes_entregaveis(cat)]
            c1, c2 = st.columns([3, 1]); novo = c1.text_input("Novo", placeholder="Novo entregável", label_visibility="collapsed")
            if c2.button("Adicionar", use_container_width=True) and novo:
                st.session_state.entregaveis.append({"descricao": novo}); st.rerun()
            st.divider()
            if not st.session_state.entregaveis: st.warning("Adicione ao menos um entregável.")
            for i, item in enumerate(st.session_state.entregaveis):
                c1, c2 = st.columns([4, 1]); c1.write(f" • {item['descricao']}")
                if c2.button("Remover", key=f"rm_{i}", use_container_width=True):
                    st.session_state.entregaveis.pop(i); st.rerun()
            st.divider()
            c1, c2 = st.columns(2)
            if c1.button("⬅️ Editar Briefing"): st.session_state.orcamento_step = 2; del st.session_state.entregaveis; st.rerun()
            if c2.button("Confirmar Escopo ➡️", type="primary", use_container_width=True, disabled=not st.session_state.entregaveis):
                st.session_state.orcamento_step = 4; st.rerun()
        
        elif st.session_state.orcamento_step == 4:
            st.header("👨‍💻 Alocação de Horas"); st.info("Para cada entregável, adicione os perfis e horas.")
            perfis = carregar_perfis_equipe(db, agencia_id)
            if not perfis: st.warning("Nenhum perfil cadastrado. Vá em 'Configurações'."); st.stop()
            nomes_perfis = [p['funcao'] for p in perfis]; total_horas = 0
            for i, entr in enumerate(st.session_state.entregaveis):
                if 'alocacoes' not in entr: entr['alocacoes'] = []
                horas_entr = sum(a['horas'] for a in entr['alocacoes']); total_horas += horas_entr
                with st.expander(f"**{i+1}. {entr['descricao']}** ({horas_entr}h)"):
                    if entr['alocacoes']:
                        for j, aloc in enumerate(entr['alocacoes']):
                            c1,c2,c3=st.columns([2,1,1]);c1.write(f"• {aloc['perfil_funcao']}");c2.write(f"{aloc['horas']}h");c3.button("X", key=f"rem_{i}_{j}", on_click=lambda i=i,j=j:st.session_state.entregaveis[i]['alocacoes'].pop(j))
                    st.divider()
                    c1, c2, c3 = st.columns([2,1,1]); sel = c1.selectbox("Perfil", nomes_perfis, key=f"sel_{i}", index=None); h = c2.number_input("Horas", 0.5, step=0.5, key=f"h_{i}")
                    if c3.button("Adicionar", key=f"add_{i}", disabled=not sel):
                        p_data = next(p for p in perfis if p['funcao'] == sel)
                        entr['alocacoes'].append({"perfil_id":p_data['id'], "perfil_funcao":p_data['funcao'], "custo_hora":p_data['custo_hora'], "horas":h}); st.rerun()
            st.divider(); st.header(f"Total de Horas: {total_horas}h")
            c1,c2=st.columns(2); c1.button("⬅️ Editar Escopo", on_click=lambda:st.session_state.update(orcamento_step=3)); c2.button("Calcular Orçamento ➡️", type="primary", use_container_width=True, disabled=(total_horas==0), on_click=lambda:st.session_state.update(orcamento_step=5))

        elif st.session_state.orcamento_step == 5:
            st.header("📊 Orçamento Preliminar")
            configs = carregar_configuracoes_financeiras(db, agencia_id)
            if not configs: st.warning("Configs financeiras não encontradas. Ajuste em 'Configurações'.")
            resultado = calcular_orcamento(st.session_state.entregaveis, configs)
            st.metric(label="Valor Total da Proposta", value=f"R$ {resultado['valor_total_cliente']:.2f}")
            with st.expander("Ver detalhamento do cálculo"):
                st.markdown(f"**Custo Equipe:** `R$ {resultado['custo_total_equipe']:.2f}`\n\n**+ Tx. Coordenação ({configs.get('taxa_coordenacao',0)}%):** `R$ {resultado['valor_taxa_coordenacao']:.2f}`\n\n**+ Custos Fixos ({configs.get('custos_fixos',0)}%):** `R$ {resultado['valor_custos_fixos']:.2f}`\n\n**= Subtotal Op.:** `R$ {resultado['subtotal_antes_lucro']:.2f}`\n\n**+ Lucro ({configs.get('margem_lucro',0)}%):** `R$ {resultado['valor_lucro']:.2f}`\n\n**= Subtotal:** `R$ {resultado['subtotal_antes_impostos']:.2f}`\n\n**+ Impostos ({configs.get('impostos',0)}%):** `R$ {resultado['valor_impostos']:.2f}`")
            st.divider()
            nome_cliente = st.text_input("Nome do Cliente/Projeto*", placeholder="Ex: Lançamento Marca XPTO")
            c1,c2=st.columns(2); c1.button("⬅️ Editar Alocação", on_click=lambda:st.session_state.update(orcamento_step=4))
            if c2.button("Salvar Orçamento ✅", type="primary", use_container_width=True, disabled=not nome_cliente):
                dados_orc = {"nome_cliente": nome_cliente, "briefing": st.session_state.dados_briefing, "escopo_final": st.session_state.entregaveis, "resultado_financeiro": resultado}
                if salvar_orcamento_firestore(db, agencia_id, user_info, dados_orc):
                    st.session_state.orcamento_step = 6; st.rerun()

        elif st.session_state.orcamento_step == 6:
            st.balloons(); st.success("Orçamento salvo com sucesso!")
            st.write("O próximo passo é visualizar este orçamento no seu histórico (Sprint 3).")
            if st.button("Gerar Novo Orçamento"):
                keys_to_delete = [k for k in st.session_state if k.startswith(('orcamento_', 'dados_briefing', 'entregaveis'))]
                for key in keys_to_delete: del st.session_state[key]
                st.session_state.orcamento_step = 1; st.rerun()

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência")
        st.caption("Defina os perfis de equipe e as margens que alimentarão seus orçamentos.")
        agencia_id = user_info['uid']
        with st.expander("Gerenciar Perfis de Equipe", expanded=True):
            with st.form("new_profile_form", clear_on_submit=True):
                c1,c2=st.columns([2,1]); funcao=c1.text_input("Função"); custo=c2.number_input("Custo/Hora(R$)",0.0,step=5.0)
                if st.form_submit_button("Adicionar Perfil"):
                    if funcao and custo > 0:
                        db.collection('agencias').document(agencia_id).collection('perfis_equipe').add({"funcao":funcao, "custo_hora":custo}); st.toast("Perfil adicionado")
            st.divider()
            st.subheader("Perfis Cadastrados")
            perfis=carregar_perfis_equipe(db, agencia_id)
            if not perfis: st.info("Nenhum perfil cadastrado.")
            else:
                for p in perfis:
                    c1,c2,c3=st.columns([2,1,1]); c1.write(p['funcao']); c2.write(f"R$ {p['custo_hora']:.2f}"); c3.button("Deletar", key=f"del_{p['id']}", on_click=db.collection('agencias').document(agencia_id).collection('perfis_equipe').document(p['id']).delete)
        st.divider()
        if 'config_financeiras' not in st.session_state:
            st.session_state.config_financeiras = carregar_configuracoes_financeiras(db, agencia_id)
        st.subheader("⚙️ Configurações Financeiras")
        with st.form(key="form_config_financeiras"):
            defaults={"margem_lucro":20.0, "impostos":15.0, "custos_fixos":10.0, "taxa_coordenacao":10.0}
            c1,c2=st.columns(2)
            lucro = c1.number_input("Margem de Lucro (%)", 0.0, value=st.session_state.config_financeiras.get("margem_lucro", defaults["margem_lucro"]))
            impostos = c1.number_input("Impostos (%)", 0.0, value=st.session_state.config_financeiras.get("impostos", defaults["impostos"]))
            fixos = c2.number_input("Custos Fixos (%)", 0.0, value=st.session_state.config_financeiras.get("custos_fixos", defaults["custos_fixos"]))
            coord = c2.number_input("Taxa de Coordenação (%)", 0.0, value=st.session_state.config_financeiras.get("taxa_coordenacao", defaults["taxa_coordenacao"]))
            if st.form_submit_button("Salvar Configs"):
                novas_configs = {"margem_lucro":lucro, "impostos":impostos, "custos_fixos":fixos, "taxa_coordenacao":coord}
                db.collection('agencias').document(agencia_id).update({"configuracoes_financeiras":novas_configs})
                st.session_state.config_financeiras = novas_configs; st.success("Salvo!")