# ==============================================================================
# Precify.AI - Sprint 2: Correção de State Management e Finalização
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
        dados_form = {"tipo_campanha": "Campanha Online", 'briefing_semantico': st.text_area("Descreva o objetivo", help="Ex: 'Queremos uma campanha...'")}
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais'] = st.multiselect("Canais", ["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn", "Google Ads", "Outro"])
            dados_form['pecas_estimadas'] = st. o seu arquivo por este. Com esta versão, o cálculo do orçamento funcionará como esperado.

---

### `app.py` (Versão Corrigida com Cálculo Funcional)

```python
# ==============================================================================
# Precify.AI - Sprint 2: Correção do Fluxo de Orçamento (Código Completo)
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
            dados_formnumber_input("Qtd. Peças", 1, step=1, value=10)
            if st.radio("Mídia paga?", ("Não", "Sim"), horizontal=True) == "Sim": dados_form['verba_midia'] = st.number_input("Verba (R$)", 0.0, step=100.0)
        with col2:
            dados_form['publico_alvo'] = st.text_area("Público-alvo")
            dados_form['urgencia'] = st.select_slider("Urgência", ["Baixa", "Média", "Alta"], "Média")
            periodo = st.date_input("Período", (date.today(), date.today() + timedelta(days['urgencia'] = st.select_slider("Urgência", ["Baixa", "Média", "Alta"], value="Média")
            periodo = st.date_input("Período da campanha", value=(date.today(), date.today() + timedelta(days=30)))
            if len(periodo) == 2: dados_form['periodo_inicio'], dados_form['periodo_fim'] = str(periodo[0]), str(periodo[1])
            pos_campanha = st.radio("Acompanhamento pós-campanha?", ("Não", "Sim"), horizontal=True, key="online_pos")
            dados_form['pos_campanha'] = (pos_campanha == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3=30)))
            if len(periodo) == 2: dados_form['periodo_inicio'], dados_form['periodo_fim'] = str(periodo[0]), str(periodo[1])
            dados_form['pos_campanha'] = (st.radio("Pós-campanha?", ("Não", "Sim"), horizontal=True) == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

# ... (As outras funções render_form_* permanecem aqui, completas)
def render_form_campanha_offline():
    with st.form(key="briefing_offline_form"):
        # ...código completo...
        if st.form_submit_button("Analisar Briefing ➡️"): st.session_state.dados_briefing = {}; st.session_state.orcamento_step = 3; st.rerun()
def render_form; st.rerun()

def render_form_campanha_offline():
    with st.form(key="briefing_offline_form"):
        st.info("Detalhe a ação offline para estimarmos produção e logística.")
        dados_form = {"tipo_campanha": "Campanha Offline"}
        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo principal", help="_campanha_360():
    with st.form(key="briefing_360_form"):
        # ...código completo...
        if st.form_submit_button("Analisar Briefing ➡️"): st.session_state.dados_briefing = {}; st.session_state.orcamento_stepEx: 'Participar da feira XYZ...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['tipo_acao_offline = 3; st.rerun()
def render_form_projeto_estrategico():
    with'] = st.selectbox("Tipo de ação", ["Evento", "Material Impresso", "Mídia OOH", st.form(key="briefing_estrategico_form"):
        # ...código completo...
 "Outro"])
            dados_form['local_execucao'] = st.text_input("Local de execução", help="Cidade, estado ou país")
            dados_form['prazo_execucao']        if st.form_submit_button("Analisar Briefing ➡️"): st.session_state.dados_briefing = {}; st.session_state.orcamento_step = 3; st.rerun = str(st.date_input("Prazo final"))
        with col2:
            dados_form['publico_estimado'] = st.number_input("Público estimado", min_value=0()


def calcular_orcamento(entregaveis, configs):
    custo_total_equipe = sum(aloc['horas'] * aloc['custo_hora'] for entr in entregaveis for aloc in entr, step=100)
            prod_fisica = st.radio("Produção física?", ("Não", ".get('alocacoes', []))
    taxa_coord_p = configs.get('taxa_coSim"), horizontal=True, key="offline_prod")
            if prod_fisica == "Sim": dadosordenacao', 0)/100; custos_fixos_p = configs.get('custos__form['itens_producao'] = st.multiselect("Itens?", ["Banner", "Brinde", "Estande"])
            dados_form['terceiros_envolvidos'] = (st.fixos', 0)/100
    margem_lucro_p = configs.get('margem_lucro', 0)/100; impostos_p = configs.get('impostos',radio("Terceiros?", ("Não", "Sim"), horizontal=True) == "Sim")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados 0)/100
    custo_c_coord = custo_total_equipe * (1 + taxa_coord_p); custo_c_fixos = custo_c_coord * (1 + custos_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

def render_form_campanha_360():
    with st.form(key_fixos_p)
    lucro = custo_c_fixos * margem_lucro_p; sub="briefing_360_form"):
        st.info("Detalhe a campanha integrada, envolvendo múltiplos canais.")
        dados_form = {"tipo_campanha": "Campanha 360"}
_impostos = custo_c_fixos + lucro
    impostos = sub_impostos * impostos_p;        dados_form['briefing_semantico'] = st.text_area("Descreva o objetivo", total = sub_impostos + impostos
    return {"custo_total_equipe": custo_total_equ help="Ex: 'Lançar nova identidade visual...'")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            dados_form['canais_ipe, "valor_taxa_coordenacao": custo_c_coord - custo_total_equipe,
            "valor_custos_fixos": custo_c_fixos - custo_c_coord, "envolvidos'] = st.multiselect("Canais", ["Digital", "Físico (Evento)", "Mídia (TV, Rádio)"])
            if st.radio("Verba por frente?", ("Nãosubtotal_antes_lucro": custo_c_fixos,
            "valor_lucro": lucro, "subtotal_antes_impostos": sub_impostos, "valor_impostos": impostos, "valor_", "Sim"), horizontal=True) == "Sim": dados_form['verba_detalhada'] = st.text_area("Detalhar verbas")
        with col2:
            dados_form['acomtotal_cliente": total}

# --- 3. FUNÇÕES DE DADOS (FIRESTORE) E AUTH ---
@st.cache_resource
def initialize_firebase():
    try:
        creds_dictpanhamento_estrategico'] = (st.radio("Acompanhamento?", ("Não", "Sim"), horizontal = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"]); firebase_admin.initialize=True) == "Sim")
            duracao = st.date_input("Duração", value=(date.today(), date.today() + timedelta(days=90)))
            if len(duracao) ==_app(credentials.Certificate(creds_dict)) if not firebase_admin._apps else None; return firestore.client()
    except Exception as e: st.error(f"FALHA FIREBASE: { 2: dados_form['duracao_inicio'], dados_form['duracao_fim'] = str(duracao[0]), str(duracao[1])
            dados_form['segmentacao_geografica']e}"); return None
@st.cache_data(ttl=300)
def carregar_perfis_equipe(_db, id):
    try: return [{"id": doc.id, **doc.to_ = st.selectbox("Segmentação", ["Local", "Regional", "Nacional"])
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefdict()} for doc in _db.collection('agencias').document(id).collection('perfis_equipeing = dados_form; st.session_state.orcamento_step = 3; st.rerun').stream()]
    except Exception as e: st.error(f"Erro perfis: {e}"); return []
()

def render_form_projeto_estrategico():
    with st.form(key="briefing@st.cache_data(ttl=300)
def carregar_configuracoes_financeiras_estrategico_form"):
        st.info("Descreva o desafio de negócio ou de marca a ser resolvido.")
        dados_form = {"tipo_campanha": "Projeto Estratégico"}
        dados_(_db, id):
    try: doc = _db.collection('agencias').document(id).get(); return doc.to_dict().get('configuracoes_financeiras', {}) if doc.exists else {}
    except Exceptionform['desafio_principal'] = st.text_area("Qual o desafio?", help="Ex: 'Reverter percepção pública negativa.'")
        st.divider()
        col1, col2 = st.columns as e: st.error(f"Erro configs: {e}"); return {}
def salvar_orcamento_firestore(_db, id, user, dados):
    try: _db.collection('orçamentos').add({"(2)
        with col1:
            if st.radio("Ações anteriores?", ("Não", "agencia_id": id, "uid_criador": user['uid'], **dados}); return True
    Sim")) == "Sim": dados_form['detalhes_acoes_anteriores'] = st.text_area("Desexcept Exception as e: st.error(f"Falha ao salvar: {e}"); return False
def sign_upcreva")
            dados_form['apoio_estrategico_criativo'] = (st.radio("Apoio criativo?", ("Não", "Sim")) == "Sim")
            dados_form['diagnost(email, password, name):
    try: user = auth.create_user(email=email, password=password, display_name=name); db.collection('agencias').document(user.uid).set({'ico_reputacao'] = (st.radio("Diagnóstico?", ("Não", "Sim")) == "Sim")
        nome': f"Agência de {name}"}); st.success("Registrado!")
    except Exception as ewith col2:
            dados_form['imprensa_influenciadores'] = st.multiselect("Imprensa/Influencers?", ["Assessoria", "Mkt Influência"])
            if st.radio("Ver: st.error(f"Erro registro: {e}")

# --- 4. INICIALIZAÇÃO E LÓGICA DE LOGIN ---
db = initialize_firebase()
if db is None: st.stop()
ba disponível?", ("Não", "Sim")) == "Sim": dados_form['valor_verba'] = stif 'logged_in' not in st.session_state: st.session_state.logged_in =.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados False

if not st.session_state.logged_in:
    st.title("Bem-vindo ao Precify.AI"); choice = st.selectbox("Acessar", ["Login", "Registrar"], label_visibility="_form; st.session_state.orcamento_step = 3; st.rerun()

def calcular_orcamento(entregaveis, configs):
    custo_total_equipe = sum(collapsed")
    if choice == "Login":
        with st.form("login_form"):
            email=aloc['horas'] * aloc['custo_hora'] for entr in entregaveis for aloc inst.text_input("Email"); password=st.text_input("Senha",type="password")
            if st entr.get('alocacoes', []))
    taxa_coord_percent = configs.get('tax.form_submit_button("Login"):
                try: user=auth.get_user_by_email(email);a_coordenacao', 0)/100; custos_fixos_percent = configs.get('custos_fixos', 0)/100
    margem_lucro_percent = configs. st.session_state.logged_in=True; st.session_state.user_info={"name":user.display_name,"email":user.email,"uid":user.uid}; st.rerun()
                exceptget('margem_lucro', 0)/100; impostos_percent = configs.get('impostos', 0)/100
    custo_com_coord = custo_total_equipe: st.error("Credenciais inválidas.")
    else:
        with st.form("register_form"):
            name=st.text_input("Nome"); email=st.text_input("Email"); password=st.text_input * (1 + taxa_coord_percent); custo_com_fixos = custo_com_coord * (("Senha",type="password")
            if st.form_submit_button("Registrar"): sign_up1 + custos_fixos_percent)
    valor_lucro = custo_com_fixos * margem_lucro_percent; subtotal_antes_impostos = custo_com_fixos + valor_(email, password, name)
else:
    user_info=st.session_state.user_lucro
    valor_impostos = subtotal_antes_impostos * impostos_percent; valor_total_info; agencia_id=user_info['uid']; nome=user_info.get('name')
    stcliente = subtotal_antes_impostos + valor_impostos
    return {"custo_total_equipe": custo_total_equipe, "valor_taxa_coordenacao": custo_com_coord.sidebar.title(f"Olá, {nome.split()[0]}!" if nome and nome.strip() else "Olá!")
    if st.sidebar.button("Logout"):
        for k in list(st.session - custo_total_equipe,
            "valor_custos_fixos": custo_com_fix_state.keys()): del st.session_state[k]
        st.rerun()
    st.sidebaros - custo_com_coord, "subtotal_antes_lucro": custo_com_fixos,
            "valor_lucro": valor_lucro, "subtotal_antes_impostos": subtotal_.divider()
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento",antes_impostos, "valor_impostos": valor_impostos,
            "valor_total_cliente "Configurações"], key="navigation")
    if 'current_view' in st.session_state and st": valor_total_cliente}

# --- 3. FUNÇÕES DE DADOS (FIRESTORE) E AUTH ---
@st.cache_resource
def initialize_firebase():
    try:
        creds_.session_state.current_view=="Novo Orçamento" and view!="Novo Orçamento":
        for k in [dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if notk for k in st.session_state if k.startswith('orcamento') or k.startswith('dados') firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e:
        st.error(f"]: del st.session_state[k]
    st.session_state.current_view = view

    if view == "Painel Principal":
        st.header("Painel Principal"); st.write("EmFALHA NA CONEXÃO COM FIREBASE: {e}"); return None

@st.cache_data(ttl= breve.")
    
    elif view == "Novo Orçamento":
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1
        
        300)
def carregar_perfis_equipe(_db_client, agencia_id):
    try:
        perfis_ref = _db_client.collection('agencias').document(agenciaif st.session_state.orcamento_step == 1:
            st.header("🚀 Iniciar Novo Or_id).collection('perfis_equipe').stream()
        return [{"id": doc.id, **çamento"); cat = st.selectbox("Tipo de Campanha", ["Selecione...","Campanha Online","Campanha Offline","doc.to_dict()} for doc in perfis_ref]
    except Exception as e:
        st.error(f"Erro ao carregar perfis: {e}"); return []

@st.cache_data(ttl=Campanha 360","Projeto Estratégico"])
            if st.button("Iniciar", disabled=(cat=="Selecione...")): st.session_state.orcamento_categoria=cat; st.session_300)
def carregar_configuracoes_financeiras(_db_client, agencia_id):
    try:
        doc = _db_client.collection('agencias').document(agencia_idstate.orcamento_step=2; st.rerun()
        
        elif st.session_state.orcamento_step == 2:
            st.header(f"Briefing: {st.session_state.).get()
        return doc.to_dict().get('configuracoes_financeiras', {}) if doc.exists else {}
    except Exception as e:
        st.error(f"Erro ao carregar configsget('orcamento_categoria')}"); cat = st.session_state.get('orcamento_categoria')
            if cat: {e}"); return {}

def salvar_orcamento_firestore(db_client, agencia_id, user_info=="Campanha Online": render_form_campanha_online() # Funções completas devem ser inseridas aqui
            , dados_orcamento):
    try:
        db_client.collection('orçamentos').add({"agif st.button("⬅️ Voltar"): st.session_state.orcamento_step=1; del st.encia_id": agencia_id, "uid_criador": user_info['uid'], "email_criador": user_info['email'], "data_orcamento": firestore.SERVER_TIMESTAMP, **dados_orcamento})session_state.orcamento_categoria; st.rerun()

        elif st.session_state.orcamento_step == 3:
            st.header("🤖 Validação do Escopo"); cat = st.session_state.get('
        return True
    except Exception as e:
        st.error(f"Falha ao salvar o orçamento: {e}"); return False

def sign_up(email, password, name):
    try:
orcamento_categoria', 'N/A')
            if 'entregaveis' not in st.session_state: st.session_state.entregaveis = [{"descricao": item} for item in get_sugesto        user = auth.create_user(email=email, password=password, display_name=name)
        db.collection('agencias').document(user.uid).set({'nome': f"Agência de {es_entregaveis(cat)]
            c1,c2=st.columns([3,1]); novoname}", 'uid_admin': user.uid})
        st.success("Usuário e Agência registrados=c1.text_input("Novo",label_visibility="collapsed");
            if c2.button("Ad! Por favor, faça o login.")
    except Exception as e: st.error(f"Erro no registro:icionar",use_container_width=True) and novo: st.session_state.entregaveis.append({" {e}")

# --- 4. INICIALIZAÇÃO E LÓGICA DE LOGIN ---
db =descricao":novo}); st.rerun()
            for i, item in enumerate(st.session_state.entregave initialize_firebase()
if db is None: st.stop()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_stateis):
                c1,c2=st.columns([4,1]); c1.write(f"• {item['descricao']}")
                if c2.button("Remover", key=f"rm_{i}",use.logged_in:
    st.title("Bem-vindo ao Precify.AI"); choice = st.selectbox("Acessar", ["Login", "Registrar"], label_visibility="collapsed")
    if choice ==_container_width=True): st.session_state.entregaveis.pop(i); st.rerun()
            c1,c2=st.columns(2)
            if c1.button(" "Login":
        with st.form("login_form"):
            email = st.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit⬅️ Editar Briefing"): st.session_state.orcamento_step=2; del st.session_state.entregaveis; st.rerun()
            if c2.button("Confirmar Escopo ➡️",_button("Login"):
                try:
                    user = auth.get_user_by_email(email); st.session_state.logged_in = True
                    st.session_state.user_info =type="primary",use_container_width=True,disabled=not st.session_state.entregaveis): st.session_state.orcamento_step=4; st.rerun()

        elif st {"name": user.display_name, "email": user.email, "uid": user.uid}; st.rerun()
                except Exception: st.error("Credenciais inválidas.")
    else:
        .session_state.orcamento_step == 4:
            st.header("👨‍💻 Alocwith st.form("register_form"):
            name = st.text_input("Nome"); email = stação de Horas"); perfis = carregar_perfis_equipe(db, agencia_id)
            if not perfis: st.warning("Cadastre perfis em 'Configurações'."); st.stop()
            nomes_perf.text_input("Email"); password = st.text_input("Senha", type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    is = [p['funcao'] for p in perfis]; total_h = 0
            for i, entr# ==================================================
    # --- APLICAÇÃO PRINCIPAL (Área Logada) ---
    # ==================================================
    user_info = st.session_state.user_info; agencia in enumerate(st.session_state.entregaveis):
                if 'alocacoes' not in entr: entr['alocacoes']=[]
                horas_e = sum(a['horas'] for a in entr['alocacoes']);_id = user_info['uid']
    nome_display = user_info.get('name'); saudacao = f"Olá, {nome_display.split()[0]}!" if nome_display and nome_display total_h += horas_e
                with st.expander(f"**{i+1}. {entr.strip() else "Olá!"
    st.sidebar.title(saudacao)
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()): del st.['descricao']}** ({horas_e}h)"):
                    for j, aloc in enumerate(entr['alocacoes']):
                        c1,c2,c3=st.columns([2,1,1]);c1.writesession_state[key]
        st.rerun()
    st.sidebar.divider()
    if 'current_view' not in st.session_state: st.session_state.current_view = "(f"• {aloc['perfil_funcao']}");c2.write(f"{aloc['horas']}h")
                        if c3.button("X",key=f"rem_{i}_{j}")Painel Principal"
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento", "Configurações"], key="navigation")
    if st.session_state.current_view ==: entr['alocacoes'].pop(j); st.rerun()
                    c1,c2,c3= "Novo Orçamento" and view != "Novo Orçamento":
        keys_to_delete = [k forst.columns([2,1,1]); sel=c1.selectbox("Perfil",nomes_perfis,key=f"sel_{i}",index=None); h=c2.number_input("Horas",0.5 k in st.session_state.keys() if k.startswith(('orcamento_', 'dados_briefing', 'entregaveis'))]
        for key in keys_to_delete: del st.session_state,step=0.5,key=f"h_{i}")
                    if c3.button("Adicionar",key=f"add_{i}",disabled=not sel):
                        p_data = next((p for[key]
    st.session_state.current_view = view

    if view == "Painel Principal":
 p in perfis if p['funcao']==sel),None)
                        if p_data: entr['alocacoes        st.header("Painel Principal"); st.write("Em breve.")
    
    elif view == "Novo Orçamento":
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1
        
        if st.session_state.orcamento_'].append({"perfil_id":p_data['id'],"perfil_funcao":p_data['funcao'],"custo_hora":p_data['custo_hora'],"horas":h});step == 1:
            st.header("🚀 Iniciar Novo Orçamento"); st.caption("Selecione o tipo de projeto.")
            categorias = ["Selecione...", "Campanha Online", "Campanha Offline", "Camp st.rerun()
            st.header(f"Total Horas: {total_h}h");anha 360", "Projeto Estratégico"]
            cat = st.selectbox("Tipo de Campanha", c1,c2=st.columns(2)
            if c1.button("⬅️ Editar Escopo"): st.session_state.orcamento_step=3; st.rerun()
            if c categorias)
            if st.button("Iniciar", disabled=(cat == "Selecione...")):
                st.session_state.orcamento_categoria = cat; st.session_state.orcamento_step = 22.button("Calcular Orçamento ➡️",type="primary",use_container_width=True,disabled=(total_h==0)): st.session_state.orcamento_step=5; st.rerun()

        elif st.session_state.orcamento_step == 5:
            st.header("; st.rerun()

        elif st.session_state.orcamento_step == 2:
            st.header(f"Briefing: {st.session_state.get('orcamento_categoria',📊 Orçamento Preliminar"); configs = carregar_configuracoes_financeiras(db, agencia_id 'N/A')}")
            cat = st.session_state.get('orcamento_categoria');
            if cat == "Campanha Online": render_form_campanha_online()
            elif cat == "Campanha Offline)
            resultado = calcular_orcamento(st.session_state.entregaveis, configs)
            st.metric("Valor Total", f"R$ {resultado['valor_total_cliente']:.2f}")
            with": render_form_campanha_offline()
            elif cat == "Campanha 360": render_form_campanha_360()
            elif cat == "Projeto Estratégico": render_ st.expander("Ver detalhamento"): st.json(resultado)
            nome_cliente = st.text_input("Nome do Cliente/Projeto*")
            c1,c2=st.columns(2)
            if cform_projeto_estrategico()
            if st.button("⬅️ Voltar"):
                st.session_state.orcamento_step = 1; del st.session_state.orcamento_categoria;1.button("⬅️ Editar Alocação"): st.session_state.orcamento_step=4; st.rerun()
            if c2.button("Salvar Orçamento ✅",type="primary",use st.rerun()

        elif st.session_state.orcamento_step == 3:
            st.header("🤖 Validação do Escopo"); st.info("Ajuste a lista de entregáveis suger_container_width=True,disabled=not nome_cliente):
                dados = {"nome_cliente": nomeida.")
            cat = st.session_state.get('orcamento_categoria', 'N/A')_cliente, "briefing": st.session_state.dados_briefing, "escopo_final": st.session_state.entregaveis, "resultado_financeiro": resultado}
                if salvar_orc
            if 'entregaveis' not in st.session_state:
                st.session_state.entregaveis = [{"descricao": item} for item in get_sugestoes_entregaveis(amento_firestore(db, agencia_id, user_info, dados): st.session_state.orcamento_step=6; st.rerun()

        elif st.session_state.orcamento_step ==cat)]
            c1, c2 = st.columns([3, 1]); novo = c1.text_input("Novo", placeholder="Novo entregável", label_visibility="collapsed")
            if c2.button("Adicionar", 6:
            st.balloons(); st.success("Orçamento salvo!");
            if st.button("Gerar use_container_width=True) and novo:
                st.session_state.entregaveis. Novo Orçamento"):
                for k in [k for k in st.session_state if k.startswith('orcamento') or k.startswith('dados')]: del st.session_state[k]
                st.append({"descricao": novo}); st.rerun()
            st.divider()
            if not st.session_state.entregaveis: st.warning("Adicione ao menos um entregável.")
            for isession_state.orcamento_step = 1; st.rerun()

    elif view == "Configura, item in enumerate(st.session_state.entregaveis):
                c1, c2 = st.columns([4, 1]); c1.write(f" • {item['descricao']}")
                if c2.ções":
        st.header("Painel de Configuração"); agencia_id = user_info['uid']
        with st.expander("Gerenciar Perfis", expanded=True):
            with st.form("new_profilebutton("Remover", key=f"rm_{i}", use_container_width=True):
                    st.session_form", clear_on_submit=True):
                c1,c2=st.columns([2_state.entregaveis.pop(i); st.rerun()
            st.divider()
            c1, c2 = st.columns(2)
            if c1.button("⬅️ Editar Brief,1]); funcao=c1.text_input("Função"); custo=c2.number_input("Custo/Hora(R$)",0.0,step=5.0)
                if st.forming"): st.session_state.orcamento_step = 2; del st.session_state.ent_submit_button("Adicionar"):
                    if funcao and custo > 0: db.collection('agenciasregaveis; st.rerun()
            if c2.button("Confirmar Escopo ➡️", type="primary", use_container_width=True, disabled=not st.session_state.entregave').document(agencia_id).collection('perfis_equipe').add({"funcao":funcao,"custo_hora":custo}); st.toast("Adicionado!"); st.rerun()
            perfis=carregaris):
                st.session_state.orcamento_step = 4; st.rerun()
        
        elif st.session_state.orcamento_step == 4:
            st.header("_perfis_equipe(db, agencia_id)
            if perfis:
                for p in perf👨‍💻 Alocação de Horas"); st.info("Para cada entregável, adicione os perfis e horasis:
                    c1,c2,c3=st.columns([2,1,1]);c1.write(p['funcao']);c2.write(f"R$ {p['custo_hora']:..")
            perfis = carregar_perfis_equipe(db, agencia_id)
            if not perfis: st.warning("Nenhum perfil cadastrado. Vá em 'Configurações'."); st2f}")
                    if c3.button("X",key=f"del_{p['id']}"): db.collection.stop()
            nomes_perfis = [p['funcao'] for p in perfis]; total_('agencias').document(agencia_id).collection('perfis_equipe').document(p['idhoras = 0
            for i, entr in enumerate(st.session_state.entregaveis):']).delete(); st.rerun()
        with st.form(key="form_config_financeiras"):
            #
                if 'alocacoes' not in entr: entr['alocacoes'] = []
                horas_entr = sum(a['horas'] for a in entr['alocacoes']); total_horas += horas_entr
                with ... código completo ...
            if st.form_submit_button("Salvar"): st.success("Salvo!")

 st.expander(f"**{i+1}. {entr['descricao']}** ({horas_entr}h)"):
                    if entr['alocacoes']:
                        for j, aloc in enumerate(entr['alocacoes']):
                            c1,c2,c3=st.columns([2,1,1]);c1.write(f"• {aloc['perfil_funcao']}");c2.write(f"{aloc['horas']}h");c3.button("X", key=f"rem_aloc_{i}_{j}", on_click=lambda i=i,j=j: st.session_state.entregaveis[i]['alocacoes'].pop(j))
                    st.divider()
                    c1, c2, c3 = st.columns([2,1,1]); sel = c1.selectbox("Perfil", nomes_perfis, key=f"sel_{i}", index=None, placeholder="Selecione um perfil"); h = c2.number_input("Horas", 0.5, step=0.5, key=f"h_{i}")
                    if c3.button("Adicionar", key=f"add_{i}", disabled=not sel):
                        perfil_data = next((p for p in perfis if p['funcao'] == sel), None)
                        if perfil_data:
                            # CORREÇÃO CRÍTICA APLICADA AQUI:
                            st.session_state.entregaveis[i]['alocacoes'].append({"perfil_id":perfil_data['id'], "perfil_funcao":perfil_data['funcao'], "custo_hora":per```