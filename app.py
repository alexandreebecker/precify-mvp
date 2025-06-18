# ==============================================================================
# Precify.AI MVP - Versão Funcional Baseada no Wireframe (Ordem Corrigida)
# ==============================================================================

# --- 1. Importações de Bibliotecas ---
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import time
import datetime
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_resource

# --- 2. Conexão com Firebase (DEFINIÇÃO VEM PRIMEIRO) ---

class FirebaseConnection(ExperimentalBaseConnection[firestore.Client]):
    def _connect(self, **kwargs) -> firestore.Client:
        try:
            creds_dict = json.loads(st.secrets["FIREBASE_SECRET_COMPACT_JSON"])
            creds = credentials.Certificate(creds_dict)
        except Exception as e:
            st.error(f"Erro ao processar o segredo JSON. Verifique a configuração no Streamlit Cloud. ERRO: {e}")
            return None
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(creds)
        
        return firestore.client()

    def get_client(self) -> firestore.Client:
        return self._instance

@cache_resource
def get_firebase_connection():
    return st.connection("firebase", type=FirebaseConnection)

# --- 3. Inicialização da Aplicação e Conexão (CHAMADA VEM DEPOIS) ---

# Conecta ao banco de dados logo no início
try:
    db = get_firebase_connection().get_client()
except Exception as e:
    st.error(f"Não foi possível conectar ao banco de dados: {e}")
    db = None # Garante que db exista mesmo com erro para evitar outros NameErrors

# --- 4. Funções e Lógica da Aplicação ---

def chamar_ia_precify(briefing, tipo_projeto, canais, prazo):
    """
    Esta função SIMULA uma chamada para a OpenAI.
    """
    st.toast("Analisando briefing com a IA...", icon="🤖")
    time.sleep(3)
    st.toast("Estimando custos...", icon="🧮")
    time.sleep(2)

    custo_base = 1000
    if tipo_projeto == "Vídeo": custo_base += 1500
    custo_base += len(canais) * 250
    if prazo and (prazo - datetime.date.today()).days < 7:
        urgencia = "Alta"
        custo_base *= 1.5
    else:
        urgencia = "Normal"

    return {
        "data_orcamento": datetime.datetime.now(),
        "briefing_original": briefing,
        "input_usuario": {"tipo_projeto": tipo_projeto, "canais": canais, "prazo": str(prazo)},
        "interpretacao_ia": {
            "tipo_projeto_detectado": f"Projeto de {tipo_projeto} com foco em {' e '.join(canais)}",
            "numero_entregas": f"{len(canais) * 3} peças", "complexidade": "Média", "nivel_urgencia": urgencia,
        },
        "estimativa_custos": {
            "criação_h": 15, "texto_h": 10, "midia_h": 15, "custo_total": custo_base,
            "margem_aplicada": 0.0, "preco_sugerido": custo_base,
        },
        "justificativa": f"Com base no briefing, estimamos a entrega para os canais {', '.join(canais)}. O nível de urgência é considerado {urgencia.lower()}, impactando o custo final."
    }

def render_pagina_inicial():
    st.image("https://i.imgur.com/UnZpTzP.png", width=150)
    st.title("Precify.AI")
    st.header("Cole o briefing. Deixe a IA fazer o orçamento.")
    st.write("")
    if st.button("Começar Orçamento", type="primary", use_container_width=True):
        st.session_state.page = "input_briefing"
        st.experimental_rerun()

def render_input_briefing():
    st.button("← Voltar", on_click=lambda: st.session_state.update(page="inicial"))
    st.header("Input do Briefing")

    with st.form("briefing_form"):
        st.subheader("Cole aqui o briefing do cliente")
        briefing_texto = st.text_area("Briefing", height=200, placeholder="Ex: Queremos uma campanha...")
        
        st.subheader("Preferências rápidas")
        col1, col2 = st.columns(2)
        tipo_projeto = col1.selectbox("Tipo de projeto", ["Campanha digital", "Logo", "Social media", "Vídeo", "Outro"])
        prazo = col2.date_input("Prazo", min_value=datetime.date.today())
        canais = st.multiselect("Canais", ["Instagram", "YouTube", "TV", "Impressos", "TikTok"])
        
        if st.form_submit_button("Gerar Orçamento", type="primary", use_container_width=True):
            if not briefing_texto:
                st.warning("Por favor, cole o briefing do cliente.")
            else:
                with st.spinner("Aguarde, nossa IA está trabalhando..."):
                    orcamento_gerado = chamar_ia_precify(briefing_texto, tipo_projeto, canais, prazo)
                    st.session_state.orcamento_gerado = orcamento_gerado
                    st.session_state.page = "orcamento_gerado"
                    st.experimental_rerun()

def render_orcamento_gerado():
    st.button("← Editar Briefing", on_click=lambda: st.session_state.update(page="input_briefing"))
    st.header("Orçamento Gerado")
    
    orcamento = st.session_state.get("orcamento_gerado")
    if not orcamento: return st.error("Erro ao gerar orçamento.")

    interpretacao = orcamento["interpretacao_ia"]
    custos = orcamento["estimativa_custos"]
    
    with st.container(border=True):
        st.subheader("Interpretação do Briefing")
        c1, c2 = st.columns(2)
        c1.metric("Tipo de Projeto", interpretacao["tipo_projeto_detectado"])
        c2.metric("Nº Entregas", interpretacao["numero_entregas"])
        c1.metric("Complexidade", interpretacao["complexidade"])
        c2.metric("Urgência", interpretacao["nivel_urgencia"])

    with st.container(border=True):
        st.subheader("Estimativa de Custos")
        c1, c2, c3 = st.columns(3)
        c1.metric("H. Criação", f"{custos['criação_h']} h"); c2.metric("H. Texto", f"{custos['texto_h']} h"); c3.metric("H. Mídia", f"{custos['midia_h']} h")
        st.divider()
        margem = st.slider("Margem Aplicada (%)", 0, 100, int(custos["margem_aplicada"]))
        preco_sugerido = custos["custo_total"] * (1 + margem / 100)
        c1, c2 = st.columns(2)
        c1.metric("Custo Total", f"R$ {custos['custo_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        c2.metric("Preço Final", f"R$ {preco_sugerido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with st.container(border=True):
        st.subheader("Justificativa")
        st.write(orcamento["justificativa"])

    st.write("")
    c1, c2 = st.columns([3, 1])
    if c1.button("Salvar no Histórico", type="primary", use_container_width=True):
        if db:
            with st.spinner("Salvando..."):
                orcamento_para_salvar = orcamento.copy()
                orcamento_para_salvar['estimativa_custos']['preco_sugerido'] = preco_sugerido
                db.collection("orçamentos").add(orcamento_para_salvar)
                st.toast("Orçamento salvo!", icon="✅")
                st.session_state.page = "input_briefing"; st.session_state.orcamento_gerado = None
                time.sleep(1); st.experimental_rerun()
        else:
            st.error("Conexão com banco falhou. Não é possível salvar.")
    if c2.button("Exportar PDF", use_container_width=True): st.info("Em desenvolvimento!")

def render_historico():
    st.header("Histórico de Orçamentos")
    if db:
        try:
            docs = db.collection("orçamentos").order_by("data_orcamento", direction=firestore.Query.DESCENDING).stream()
            orcamentos_lista = []
            for doc in docs:
                dado = doc.to_dict()
                orcamentos_lista.append({
                    "Data": dado["data_orcamento"].strftime("%d/%m/%Y"),
                    "Projeto": dado["interpretacao_ia"]["tipo_projeto_detectado"],
                    "Preço": f"R$ {dado['estimativa_custos']['preco_sugerido']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "ID": doc.id
                })
            if orcamentos_lista: st.dataframe(pd.DataFrame(orcamentos_lista), use_container_width=True)
            else: st.info("Nenhum orçamento salvo no histórico.")
        except Exception as e: st.error(f"Erro ao buscar histórico: {e}")
    else: st.error("Conexão com banco falhou.")

# --- 5. Estrutura Principal e Navegação ---
st.set_page_config(page_title="Precify.AI", layout="centered")

if "page" not in st.session_state: st.session_state.page = "inicial"
if "orcamento_gerado" not in st.session_state: st.session_state.orcamento_gerado = None

st.sidebar.title("Menu de Navegação")
app_mode = st.sidebar.radio("Selecione uma página", ["Gerar Novo Orçamento", "Histórico"])

if app_mode == "Gerar Novo Orçamento":
    if st.session_state.page == "inicial": render_pagina_inicial()
    elif st.session_state.page == "input_briefing": render_input_briefing()
    elif st.session_state.page == "orcamento_gerado": render_orcamento_gerado()
else:
    render_historico()