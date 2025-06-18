# ==============================================================================
# Precify.AI - Sprint 2: Versão Final com Correção de UI no Histórico
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
            if dados_form['midia_paga']: dados_form['verba_midia'] = st.number_input("Verba de mídia (R$)", min_value=0.0, step=100.0, format="%.2f")
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
            dados_form['producao_fisica'] = prod_fisica == "Sim"
            if dados_form['producao_fisica']: dados_form['itens_producao'] = st.multiselect("Itens?", ["Banner", "Brinde", "Estande"])
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
            if st.radio("Verba disponível?", ("Não", "Sim")) == "Sim": dados_form['valor_verba'] = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Analisar Briefing ➡️"):
            st.session_state.dados_briefing = dados_form; st.session_state.orcamento_step = 3; st.rerun()

def calcular_orcamento(entregaveis, configs):
    custo_total_equipe = sum(aloc['horas'] * aloc['custo_hora'] for entr in entregaveis for aloc in entr.get('alocacoes', []))
    taxa_coord_p = configs.get('taxa_coordenacao', 0)/100; custos_fixos_p = configs.get('custos_fixos', 0)/100
    margem_lucro_p = configs.get('margem_lucro', 0)/100; impostos_p = configs.get('impostos', 0)/100
    custo_c_coord = custo_total_equipe * (1 + taxa_coord_p); custo_c_fixos = custo_c_coord * (1 + custos_fixos_p)
    lucro = custo_c_fixos * margem_lucro_p; sub_impostos = custo_c_fixos + lucro
    impostos = sub_impostos * impostos_p; total = sub_impostos + impostos
    return {"custo_total_equipe": custo_total_equipe, "valor_taxa_coordenacao": custo_c_coord - custo_total_equipe,
            "valor_custos_fixos": custo_c_fixos - custo_c_coord, "subtotal_antes_lucro": custo_c_fixos,
            "valor_lucro": lucro, "subtotal_antes_impostos": sub_impostos, "valor_impostos": impostos,
            "valor_total_cliente": total}

# --- 3. FUNÇÕES DE DADOS (FIRESTORE) E AUTH ---
@st.cache_resource
def initialize_firebase():
    try:
        creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if not firebase_admin._apps: firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e: st.error(f"FALHA FIREBASE: {e}"); return None

@st.cache_data(ttl=300)
def carregar_perfis_equipe(_db, agencia_id):
    try: return [{"id": doc.id, **doc.to_dict()} for doc in _db.collection('agencias').document(agencia_id).collection('perfis_equipe').stream()]
    except Exception as e: st.error(f"Erro perfis: {e}"); return []

@st.cache_data(ttl=300)
def carregar_configuracoes_financeiras(_db, agencia_id):
    try:
        doc = _db.collection('agencias').document(agencia_id).get()
        return doc.to_dict().get('configuracoes_financeiras', {}) if doc.exists else {}
    except Exception as e: st.error(f"Erro configs: {e}"); return {}

@st.cache_data(ttl=300)
def carregar_orcamentos(_db, agencia_id):
    try:
        orc_ref = _db.collection('orçamentos').where('agencia_id', '==', agencia_id).order_by('data_orcamento', direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in orc_ref]
    except Exception as e: return []

def salvar_orcamento_firestore(_db, agencia_id, user, dados):
    try:
        _db.collection('orçamentos').add({"agencia_id": agencia_id, "uid_criador": user['uid'], "email_criador": user['email'], "data_orcamento": firestore.SERVER_TIMESTAMP, **dados})
        return True
    except Exception as e: st.error(f"Falha ao salvar: {e}"); return False

def sign_up(email, password, name):
    try:
        user = auth.create_user(email=email, password=password, display_name=name); db.collection('agencias').document(user.uid).set({'nome': f"Agência de {name}"})
        st.success("Registrado!")
    except Exception as e: st.error(f"Erro registro: {e}")

# --- 4. INICIALIZAÇÃO E LÓGICA DE LOGIN ---
db = initialize_firebase()
if db is None: st.stop()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Bem-vindo ao Precify.AI"); choice = st.selectbox("Acessar", ["Login", "Registrar"], label_visibility="collapsed")
    if choice == "Login":
        with st.form("login_form"):
            email=st.text_input("Email"); password=st.text_input("Senha",type="password")
            if st.form_submit_button("Login"):
                try:
                    user=auth.get_user_by_email(email); st.session_state.logged_in=True; st.session_state.user_info={"name":user.display_name,"email":user.email,"uid":user.uid}; st.rerun()
                except Exception: st.error("Credenciais inválidas.")
    else:
        with st.form("register_form"):
            name=st.text_input("Nome"); email=st.text_input("Email"); password=st.text_input("Senha",type="password")
            if st.form_submit_button("Registrar"): sign_up(email, password, name)
else:
    user_info=st.session_state.user_info; agencia_id=user_info['uid']; nome=user_info.get('name')
    st.sidebar.title(f"Olá, {nome.split()[0]}!" if nome and nome.strip() else "Olá!")
    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.sidebar.divider()
    
    if 'current_view' not in st.session_state: st.session_state.current_view = "Painel Principal"
    view = st.sidebar.radio("Menu", ["Painel Principal", "Novo Orçamento", "Meus Orçamentos", "Configurações"], key="navigation")
    
    if st.session_state.current_view=="Novo Orçamento" and view!="Novo Orçamento":
        for k in [k for k in st.session_state if k.startswith(('orcamento_', 'dados_briefing', 'entregaveis'))]: del st.session_state[k]
    st.session_state.current_view = view

    if view == "Painel Principal":
        st.header("Painel Principal"); st.write("Em breve.")
    
    elif view == "Meus Orçamentos":
        st.header("Histórico de Orçamentos")
        orcamentos_data = carregar_orcamentos(db, agencia_id)
        if not orcamentos_data:
            st.info("Nenhum orçamento salvo ainda. Crie seu primeiro em 'Novo Orçamento'.")
        else:
            for orc_data in orcamentos_data:
                res = orc_data.get('resultado_financeiro', {}); data_orc = orc_data.get('data_orcamento')
                data_formatada = data_orc.strftime("%d/%m/%Y") if hasattr(data_orc, 'strftime') else "Sem data"
                with st.expander(f"**{orc_data.get('nome_cliente', 'N/A')}** | {data_formatada} | **R$ {res.get('valor_total_cliente', 0):.2f}**"):
                    st.subheader("Detalhes do Orçamento")
                    st.markdown(f"**Custo Equipe:** `R$ {res.get('custo_total_equipe', 0):.2f}` | **Tx. Coordenação:** `R$ {res.get('valor_taxa_coordenacao', 0):.2f}` | **Custos Fixos:** `R$ {res.get('valor_custos_fixos', 0):.2f}` | **Lucro:** `R$ {res.get('valor_lucro', 0):.2f}` | **Impostos:** `R$ {res.get('valor_impostos', 0):.2f}`")
                    st.subheader("Escopo Final")
                    # --- CORREÇÃO APLICADA AQUI ---
                    for item in orc_data.get('escopo_final', []):
                        st.write(f"- {item['descricao']}")
                    # ---------------------------------
                    st.subheader("Dados do Briefing"); st.json(orc_data.get('briefing', {}))

    elif view == "Novo Orçamento":
        if 'orcamento_step' not in st.session_state: st.session_state.orcamento_step = 1
        
        # O código completo e funcional das etapas 1 a 6 permanece aqui, sem alterações.
        if st.session_state.orcamento_step == 1:
            st.header("🚀 Iniciar Novo Orçamento"); cat = st.selectbox("Tipo de Campanha", ["Selecione...","Campanha Online","Campanha Offline","Campanha 360","Projeto Estratégico"])
            if st.button("Iniciar", disabled=(cat=="Selecione...")): st.session_state.orcamento_categoria=cat; st.session_state.orcamento_step=2; st.rerun()
        
        elif st.session_state.orcamento_step == 2:
            st.header(f"Briefing: {st.session_state.get('orcamento_categoria')}"); cat = st.session_state.get('orcamento_categoria');
            if cat=="Campanha Online": render_form_campanha_online()
            elif cat=="Campanha Offline": render_form_campanha_offline()
            elif cat=="Campanha 360": render_form_campanha_360()
            elif cat=="Projeto Estratégico": render_form_projeto_estrategico()
            if st.button("⬅️ Voltar"): st.session_state.orcamento_step=1; del st.session_state.orcamento_categoria; st.rerun()

        elif st.session_state.orcamento_step == 3:
            st.header("🤖 Validação do Escopo"); cat = st.session_state.get('orcamento_categoria', 'N/A')
            if 'entregaveis' not in st.session_state: st.session_state.entregaveis = [{"descricao": item} for item in get_sugestoes_entregaveis(cat)]
            c1,c2=st.columns([3,1]); novo=c1.text_input("Novo",label_visibility="collapsed")
            if c2.button("Adicionar",use_container_width=True) and novo: st.session_state.entregaveis.append({"descricao":novo}); st.rerun()
            for i, item in enumerate(st.session_state.entregaveis):
                c1,c2=st.columns([4,1]); c1.write(f"• {item['descricao']}")
                if c2.button("Remover", key=f"rm_{i}",use_container_width=True): st.session_state.entregaveis.pop(i); st.rerun()
            st.divider(); c1,c2=st.columns(2)
            if c1.button("⬅️ Editar Briefing"): st.session_state.orcamento_step=2; del st.session_state.entregaveis; st.rerun()
            if c2.button("Confirmar Escopo ➡️",type="primary",use_container_width=True,disabled=not st.session_state.entregaveis): st.session_state.orcamento_step=4; st.rerun()

        elif st.session_state.orcamento_step == 4:
            st.header("👨‍💻 Alocação de Horas"); perfis = carregar_perfis_equipe(db, agencia_id)
            if not perfis: st.warning("Cadastre perfis em 'Configurações'."); st.stop()
            nomes_perfis = [p['funcao'] for p in perfis]; total_h = 0
            for i, entr in enumerate(st.session_state.entregaveis):
                if 'alocacoes' not in entr: entr['alocacoes']=[]
                horas_e = sum(a['horas'] for a in entr['alocacoes']); total_h += horas_e
                with st.expander(f"**{i+1}. {entr['descricao']}** ({horas_e}h)"):
                    for j, aloc in enumerate(entr['alocacoes']):
                        c1,c2,c3=st.columns([2,1,1]); c1.write(f"• {aloc['perfil_funcao']}"); c2.write(f"{aloc['horas']}h")
                        if c3.button("X",key=f"rem_{i}_{j}"): st.session_state.entregaveis[i]['alocacoes'].pop(j); st.rerun()
                    st.divider()
                    c1,c2,c3=st.columns([2,1,1]); sel=c1.selectbox("Perfil",nomes_perfis,key=f"sel_{i}",index=None); h=c2.number_input("Horas",0.5,step=0.5,key=f"h_{i}")
                    if c3.button("Adicionar",key=f"add_{i}",disabled=not sel):
                        p_data = next((p for p in perfis if p['funcao']==sel),None)
                        if p_data: st.session_state.entregaveis[i]['alocacoes'].append({"perfil_id":p_data['id'],"perfil_funcao":p_data['funcao'],"custo_hora":p_data['custo_hora'],"horas":h}); st.rerun()
            st.divider(); st.header(f"Total Horas: {total_h}h")
            c1,c2=st.columns(2)
            if c1.button("⬅️ Editar Escopo"): st.session_state.orcamento_step=3; st.rerun()
            if c2.button("Calcular Orçamento ➡️",type="primary",use_container_width=True,disabled=(total_h==0)): st.session_state.orcamento_step=5; st.rerun()

        elif st.session_state.orcamento_step == 5:
            st.header("📊 Orçamento Preliminar"); configs = carregar_configuracoes_financeiras(db, agencia_id)
            if not configs: st.warning("Configs financeiras não encontradas.")
            resultado = calcular_orcamento(st.session_state.entregaveis, configs)
            st.metric("Valor Total", f"R$ {resultado['valor_total_cliente']:.2f}")
            with st.expander("Ver detalhamento"):
                st.markdown(f"**Custo Equipe:** `R$ {resultado['custo_total_equipe']:.2f}`\n\n**+ Tx. Coordenação ({configs.get('taxa_coordenacao',0)}%):** `R$ {resultado['valor_taxa_coordenacao']:.2f}`\n\n**+ Custos Fixos ({configs.get('custos_fixos',0)}%):** `R$ {resultado['valor_custos_fixos']:.2f}`\n\n**= Subtotal Op.:** `R$ {resultado['subtotal_antes_lucro']:.2f}`\n\n**+ Lucro ({configs.get('margem_lucro',0)}%):** `R$ {resultado['valor_lucro']:.2f}`\n\n**= Subtotal:** `R$ {resultado['subtotal_antes_impostos']:.2f}`\n\n**+ Impostos ({configs.get('impostos',0)}%):** `R$ {resultado['valor_impostos']:.2f}`")
            st.divider()
            nome_cliente = st.text_input("Nome do Cliente/Projeto*")
            c1,c2=st.columns(2)
            if c1.button("⬅️ Editar Alocação"): st.session_state.orcamento_step=4; st.rerun()
            if c2.button("Salvar Orçamento ✅",type="primary",use_container_width=True,disabled=not nome_cliente):
                dados = {"nome_cliente": nome_cliente, "briefing": st.session_state.dados_briefing, "escopo_final": st.session_state.entregaveis, "resultado_financeiro": resultado}
                if salvar_orcamento_firestore(db, agencia_id, user_info, dados): st.session_state.orcamento_step=6; st.rerun()

        elif st.session_state.orcamento_step == 6:
            st.balloons(); st.success("Orçamento salvo!");
            if st.button("Ver Orçamentos Salvos"): st.session_state.current_view = "Meus Orçamentos"; st.rerun()
            if st.button("Gerar Novo Orçamento"):
                for k in [k for k in st.session_state if k.startswith(('orcamento_','dados_briefing','entregaveis'))]: del st.session_state[k]
                st.session_state.orcamento_step = 1; st.rerun()

    elif view == "Configurações":
        st.header("Painel de Configuração da Agência"); agencia_id = user_info['uid']
        with st.expander("Gerenciar Perfis", expanded=True):
            with st.form("new_profile_form", clear_on_submit=True):
                c1,c2=st.columns([2,1]); funcao=c1.text_input("Função"); custo=c2.number_input("Custo/Hora(R$)",0.0,step=5.0,format="%.2f")
                if st.form_submit_button("Adicionar"):
                    if funcao and custo > 0: db.collection('agencias').document(agencia_id).collection('perfis_equipe').add({"funcao":funcao,"custo_hora":custo}); st.toast("Adicionado!"); st.rerun()
            st.divider(); perfis=carregar_perfis_equipe(db, agencia_id)
            if perfis:
                c1,c2,c3=st.columns([2,1,1]);c1.write("**Função**");c2.write("**Custo/Hora**")
                for p in perfis:
                    c1,c2,c3=st.columns([2,1,1]);c1.text(p['funcao']);c2.text(f"R$ {p['custo_hora']:.2f}")
                    if c3.button("Deletar",key=f"del_{p['id']}",type="primary"): db.collection('agencias').document(agencia_id).collection('perfis_equipe').document(p['id']).delete(); st.rerun()
        with st.form(key="form_config_financeiras"):
            st.subheader("⚙️ Configurações Financeiras")
            configs = carregar_configuracoes_financeiras(db, agencia_id)
            defaults={"margem_lucro":20.0, "impostos":15.0, "custos_fixos":10.0, "taxa_coordenacao":10.0}
            c1,c2=st.columns(2)
            lucro = c1.number_input("Margem Lucro (%)", 0.0,value=configs.get("margem_lucro",defaults["margem_lucro"]))
            impostos = c1.number_input("Impostos (%)", 0.0,value=configs.get("impostos",defaults["impostos"]))
            fixos = c2.number_input("Custos Fixos (%)", 0.0,value=configs.get("custos_fixos",defaults["custos_fixos"]))
            coord = c2.number_input("Taxa Coord. (%)", 0.0,value=configs.get("taxa_coordenacao",defaults["taxa_coordenacao"]))
            if st.form_submit_button("Salvar"):
                novas_configs = {"margem_lucro":lucro, "impostos":impostos, "custos_fixos":fixos, "taxa_coordenacao":coord}
                db.collection('agencias').document(agencia_id).update({"configuracoes_financeiras":novas_configs})
                st.session_state.config_financeiras = novas_configs; st.success("Salvo!")