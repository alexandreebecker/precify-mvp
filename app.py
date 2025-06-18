# ==============================================================================
# Precify.AI MVP - Versão Final (Com Múltiplas Escolhas Corretas)
# ==============================================================================

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import time
import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA (A PRIMEIRA COISA) ---
st.set_page_config(page_title="Precify.AI", layout="centered", initial_sidebar_state="auto")

# --- 2. FUNÇÃO DE CONEXÃO (SIMPLES E DIRETA) ---
@st.cache_resource
def initialize_firebase():
    """Inicializa a conexão com o Firebase usando os segredos."""
    try:
        creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_dict))
        return firestore.client()
    except Exception as e:
        st.error(f"FALHA NA CONEXÃO COM FIREBASE. Verifique seus Secrets. Erro: {e}")
        return None

# --- 3. EXECUÇÃO PRINCIPAL ---
db = initialize_firebase()

# --- 4. FUNÇÕES DE RENDERIZAÇÃO E LÓGICA ---
def chamar_ia_precify(briefing, tipo_projeto, canais, prazo):
    st.toast("Analisando briefing com a IA...", icon="🤖"); time.sleep(2)
    st.toast("Estimando custos...", icon="🧮"); time.sleep(1)
    custo_base = 1000
    if tipo_projeto == "Vídeo": custo_base += 1500
    custo_base += len(canais) * 350 # Aumentei o custo por canal para refletir a complexidade
    if prazo and (prazo - datetime.date.today()).days < 7:
        urgencia = "Alta"; custo_base *= 1.5
    else: urgencia = "Normal"
    return {
        "data_orcamento": datetime.datetime.now(), "briefing_original": briefing,
        "input_usuario": {"tipo_projeto": tipo_projeto, "canais": canais, "prazo": str(prazo)},
        "interpretacao_ia": {"tipo_projeto_detectado": f"Projeto de {tipo_projeto}", "numero_entregas": f"{len(canais) * 3} peças", "complexidade": "Média", "nivel_urgencia": urgencia},
        "estimativa_custos": {"criação_h": 15, "texto_h": 10, "midia_h": 15, "custo_total": custo_base, "margem_aplicada": 0.0, "preco_sugerido": custo_base},
        "justificativa": f"Com base no briefing, estimamos a entrega para os canais {', '.join(canais)}. O nível de urgência é considerado {urgencia.lower()}, impactando o custo final."
    }

def render_pagina_inicial():
    st.title("Precify.AI"); st.header("Cole o briefing. Deixe a IA fazer o orçamento.")
    if st.button("Começar Orçamento", type="primary", use_container_width=True):
        st.session_state.page = "input_briefing"; st.rerun()

def render_input_briefing():
    if st.button("← Voltar para o Início"): st.session_state.page = "inicial"; st.rerun()
    st.header("Input do Briefing")
    with st.form("briefing_form"):
        st.subheader("Cole o briefing do cliente")
        briefing_texto = st.text_area("Briefing", height=200, placeholder="Ex: Campanha de redes sociais para lançamento de produto X, focada em jovens de 18 a 25 anos...")
        
        st.subheader("Preferências rápidas")
        c1, c2 = st.columns(2)
        tipo_projeto = c1.selectbox("Tipo de Projeto (Principal)", ["Campanha digital", "Logo", "Social media", "Vídeo", "Outro"])
        prazo = c2.date_input("Prazo de Entrega", min_value=datetime.date.today())
        
        # AQUI ESTÁ A LÓGICA DE MÚLTIPLAS ESCOLHAS
        canais_disponiveis = ["Instagram", "YouTube", "TV", "Impressos", "TikTok", "Google Ads"]
        canais_selecionados = st.multiselect("Canais de Veiculação", canais_disponiveis)
        
        if st.form_submit_button("Gerar Orçamento", type="primary", use_container_width=True):
            if briefing_texto and canais_selecionados:
                with st.spinner("Aguarde, nossa IA está trabalhando..."):
                    st.session_state.orcamento_gerado = chamar_ia_precify(briefing_texto, tipo_projeto, canais_selecionados, prazo)
                    st.session_state.page = "orcamento_gerado"; st.rerun()
            else:
                st.warning("Por favor, preencha o briefing e selecione pelo menos um canal.")

def render_orcamento_gerado():
    if st.button("← Editar Briefing"): st.session_state.page = "input_briefing"; st.rerun()
    st.header("Orçamento Gerado")
    orcamento = st.session_state.get("orcamento_gerado")
    if not orcamento: return st.error("Erro ao gerar orçamento.")
    interpretacao = orcamento["interpretacao_ia"]; custos = orcamento["estimativa_custos"]
    
    with st.container(border=True):
        st.subheader("Interpretação do Briefing")
        c1, c2 = st.columns(2)
        c1.metric("Tipo de Projeto", interpretacao["tipo_projeto_detectado"]); c2.metric("Nº Entregas", interpretacao["numero_entregas"])
        c1.metric("Complexidade", interpretacao["complexidade"]); c2.metric("Urgência", interpretacao["nivel_urgencia"])
    
    with st.container(border=True):
        st.subheader("Estimativa de Custos")
        margem = st.slider("Margem Aplicada (%)", 0, 100, int(custos["margem_aplicada"]))
        preco_sugerido = custos["custo_total"] * (1 + margem / 100)
        c1, c2 = st.columns(2)
        c1.metric("Custo Total", f"R$ {custos['custo_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        c2.metric("Preço Final", f"R$ {preco_sugerido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    with st.container(border=True):
        st.subheader("Justificativa"); st.write(orcamento["justificativa"])
    
    c1, c2 = st.columns([3, 1])
    if c1.button("Salvar no Histórico", type="primary", use_container_width=True):
        with st.spinner("Salvando..."):
            orcamento_para_salvar = orcamento.copy(); orcamento_para_salvar['estimativa_custos']['preco_sugerido'] = preco_sugerido
            db.collection("orçamentos").add(orcamento_para_salvar)
            st.toast("Orçamento salvo!", icon="✅")
            st.session_state.page = "input_briefing"; st.session_state.orcamento_gerado = None
            time.sleep(1); st.rerun()
    if c2.button("Exportar PDF", use_container_width=True): st.info("Em desenvolvimento!")

def render_historico():
    st.header("Histórico de Orçamentos")
    docs = db.collection("orçamentos").order_by("data_orcamento", direction=firestore.Query.DESCENDING).stream()
    orcamentos_lista = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    if orcamentos_lista:
        display_data = [{"Data": item["data_orcamento"].strftime("%d/%m/%Y"), "Projeto": item["interpretacao_ia"]["tipo_projeto_detectado"], "Preço": f"R$ {item['estimativa_custos']['preco_sugerido']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")} for item in orcamentos_lista]
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
    else: st.info("Nenhum orçamento salvo no histórico.")

# --- 5. ROTEAMENTO DA APLICAÇÃO ---
if not db:
    st.warning("Aplicação bloqueada. Não foi possível conectar ao banco de dados.")
    st.stop()

if "page" not in st.session_state: st.session_state.page = "inicial"
if "orcamento_gerado" not in st.session_state: st.session_state.orcamento_gerado = None

st.sidebar.image("https://i.imgur.com/UnZpTzP.png", width=70)
st.sidebar.title("Precify.AI")
app_mode = st.sidebar.radio("", ["Gerar Novo Orçamento", "Histórico"])

if app_mode == "Gerar Novo Orçamento":
    if st.session_state.page == "inicial": render_pagina_inicial()
    elif st.session_state.page == "input_briefing": render_input_briefing()
    elif st.session_state.page == "orcamento_gerado": render_orcamento_gerado()
else: render_historico()