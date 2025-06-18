# ==============================================================================
# Precify.AI MVP - Versão Funcional Baseada no Wireframe
# ==============================================================================

# --- 1. Importações de Bibliotecas ---
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import time
import datetime

# --- Conexão com Firebase (O código que já funciona) ---
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_resource

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

# --- Simulador de IA (para desenvolvermos a interface) ---
def chamar_ia_precify(briefing, tipo_projeto, canais, prazo):
    """
    Esta função SIMULA uma chamada para a OpenAI.
    Ela recebe o input do usuário e retorna um orçamento estruturado.
    """
    st.toast("Analisando briefing com a IA...", icon="🤖")
    time.sleep(3) # Simula o tempo de processamento da IA
    st.toast("Estimando custos...", icon="🧮")
    time.sleep(2)

    # Lógica de simulação baseada no input
    custo_base = 1000
    if tipo_projeto == "Vídeo":
        custo_base += 1500
    custo_base += len(canais) * 250
    if prazo and (prazo - datetime.date.today()).days < 7:
        urgencia = "Alta"
        custo_base *= 1.5 # Taxa de urgência
    else:
        urgencia = "Normal"

    orcamento_simulado = {
        "data_orcamento": datetime.datetime.now(),
        "briefing_original": briefing,
        "input_usuario": {
            "tipo_projeto": tipo_projeto,
            "canais": canais,
            "prazo": str(prazo)
        },
        "interpretacao_ia": {
            "tipo_projeto_detectado": f"Projeto de {tipo_projeto} com foco em {' e '.join(canais)}",
            "numero_entregas": f"{len(canais) * 3} peças",
            "complexidade": "Média",
            "nivel_urgencia": urgencia,
        },
        "estimativa_custos": {
            "criação_h": 15,
            "texto_h": 10,
            "midia_h": 15,
            "custo_total": custo_base,
            "margem_aplicada": 0.0,
            "preco_sugerido": custo_base,
        },
        "justificativa": f"Com base no briefing, estimamos a entrega para os canais {', '.join(canais)}. O nível de urgência é considerado {urgencia.lower()}, impactando o custo final. A proposta abrange todo o escopo de criação e gestão de mídia necessário para o sucesso do projeto."
    }
    return orcamento_simulado

# --- Funções para Renderizar as Telas ---

def render_pagina_inicial():
    st.image("https://i.imgur.com/UnZpTzP.png", width=150) # Exemplo de logo
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
        briefing_texto = st.text_area("Briefing", height=200, placeholder="Ex: Queremos uma campanha de redes sociais para lançamento de produto X...")
        
        st.subheader("Preferências rápidas")
        col1, col2 = st.columns(2)
        with col1:
            tipo_projeto = st.selectbox("Tipo de projeto", ["Campanha digital", "Logo", "Social media", "Vídeo", "Outro"])
        with col2:
            prazo = st.date_input("Prazo", min_value=datetime.date.today())
        
        canais = st.multiselect("Canais", ["Instagram", "YouTube", "TV", "Impressos", "TikTok"])
        
        submitted = st.form_submit_button("Gerar Orçamento", type="primary", use_container_width=True)

        if submitted:
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
    if not orcamento:
        st.error("Ocorreu um erro ao gerar o orçamento. Por favor, volte e tente novamente.")
        return

    # --- Layout da tela de resultados ---
    interpretacao = orcamento["interpretacao_ia"]
    custos = orcamento["estimativa_custos"]
    
    with st.container(border=True):
        st.subheader("Interpretação do Briefing")
        col1, col2 = st.columns(2)
        col1.metric("Tipo de Projeto Detectado", interpretacao["tipo_projeto_detectado"])
        col2.metric("Nº Estimado de Entregas", interpretacao["numero_entregas"])
        col1.metric("Complexidade Estimada", interpretacao["complexidade"])
        col2.metric("Nível de Urgência", interpretacao["nivel_urgencia"])

    with st.container(border=True):
        st.subheader("Estimativa de Custos")
        col1, col2, col3 = st.columns(3)
        col1.metric("Horas de Criação", f"{custos['criação_h']} h")
        col2.metric("Horas de Texto", f"{custos['texto_h']} h")
        col3.metric("Horas de Mídia", f"{custos['midia_h']} h")
        st.divider()
        margem = st.slider("Margem Aplicada (%)", 0, 100, int(custos["margem_aplicada"]))
        
        custo_total = custos["custo_total"]
        preco_sugerido = custo_total * (1 + margem / 100)

        col_a, col_b = st.columns(2)
        col_a.metric("Custo Total", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col_b.metric("Preço Sugerido Final", f"R$ {preco_sugerido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with st.container(border=True):
        st.subheader("Justificativa")
        st.write(orcamento["justificativa"])

    # --- Ações ---
    st.write("")
    c1, c2, c3 = st.columns(3)
    if c1.button("Salvar no Histórico", use_container_width=True):
        with st.spinner("Salvando..."):
            db.collection("orçamentos").add(orcamento)
            st.toast("Orçamento salvo com sucesso!", icon="✅")
            # Limpa o estado para poder gerar um novo
            st.session_state.page = "input_briefing"
            st.session_state.orcamento_gerado = None
            time.sleep(1)
            st.experimental_rerun()

    if c2.button("Exportar PDF", use_container_width=True):
        st.success("Funcionalidade de PDF em desenvolvimento!")

def render_historico():
    st.header("Histórico de Orçamentos")
    try:
        docs = db.collection("orçamentos").order_by("data_orcamento", direction=firestore.Query.DESCENDING).stream()
        orcamentos_lista = []
        for doc in docs:
            dado = doc.to_dict()
            orcamento_simplificado = {
                "Data": dado["data_orcamento"].strftime("%d/%m/%Y"),
                "Projeto": dado["interpretacao_ia"]["tipo_projeto_detectado"],
                "Preço Sugerido": f"R$ {dado['estimativa_custos']['preco_sugerido']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "ID": doc.id
            }
            orcamentos_lista.append(orcamento_simplificado)

        if orcamentos_lista:
            df = pd.DataFrame(orcamentos_lista)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum orçamento salvo no histórico ainda.")
    except Exception as e:
        st.error(f"Erro ao buscar histórico: {e}")

# --- Estrutura Principal da Aplicação ---

# Conexão com o banco
db = get_firebase_connection().get_client()

# Inicialização do estado da página
if "page" not in st.session_state:
    st.session_state.page = "inicial"
if "orcamento_gerado" not in st.session_state:
    st.session_state.orcamento_gerado = None

# Navegação principal na barra lateral
st.sidebar.title("Menu de Navegação")
app_mode = st.sidebar.radio(
    "Selecione uma página",
    ["Gerar Novo Orçamento", "Histórico de Orçamentos"]
)

# Renderização condicional baseada na seleção da barra lateral e no estado da página
if app_mode == "Gerar Novo Orçamento":
    if st.session_state.page == "inicial":
        render_pagina_inicial()
    elif st.session_state.page == "input_briefing":
        render_input_briefing()
    elif st.session_state.page == "orcamento_gerado":
        render_orcamento_gerado()
else:
    render_historico()