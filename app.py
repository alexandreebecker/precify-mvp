# ==============================================================================
# Precify MVP - Painel de Precificação com Streamlit e Firebase
# VERSÃO DA VITÓRIA ABSOLUTA - A CORREÇÃO FINAL
# ==============================================================================

# --- 1. Importações de Bibliotecas ---
import streamlit as st
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import pandas as pd
import json

from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_resource

# --- 2. Configuração da Conexão com Firebase (Método Final) ---

class FirebaseConnection(ExperimentalBaseConnection[firestore.Client]):
    def _connect(self, **kwargs) -> firestore.Client:
        creds = None
        
        # Tenta carregar dos segredos do Streamlit (para deploy)
        if "FIREBASE_SECRETS_JSON" in st.secrets:
            try:
                creds_string = st.secrets["FIREBASE_SECRETS_JSON"]
                
                # AQUI ESTÁ A LINHA MÁGICA E DEFINITIVA:
                # 1. .strip() remove os caracteres invisíveis do início e fim.
                # 2. .replace() conserta as quebras de linha internas.
                creds_dict = json.loads(creds_string.strip().replace('\n', '\\n'))
                
                creds = credentials.Certificate(creds_dict)
            except Exception as e:
                st.error(f"Erro ao processar o segredo FIREBASE_SECRETS_JSON: {e}")
                return None
        
        # Se não estiver na nuvem, tenta carregar localmente
        else:
            try:
                load_dotenv()
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                creds = credentials.Certificate(cred_path)
            except Exception as e:
                st.error(f"Credenciais locais do Firebase não encontradas: {e}")
                return None
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(creds)
        
        return firestore.client()

    def get_client(self) -> firestore.Client:
        return self._instance

# --- 3. Inicialização da Aplicação e Conexão ---

st.set_page_config(page_title="Precify MVP", layout="wide")
st.title("📊 Painel de Precificação - Precify MVP")

try:
    conn = st.connection("firebase", type=FirebaseConnection)
    db = conn.get_client()
except Exception as e:
    st.error(f"❌ Falha crítica ao inicializar a conexão: {e}")
    db = None

# --- 4. Interface Principal da Aplicação ---

if not db:
    st.warning("A aplicação não pode ser carregada pois a conexão com o banco de dados falhou.")
    st.stop()
else:
    # O RESTANTE DO CÓDIGO PERMANECE IDÊNTICO E FUNCIONAL
    
    produtos_ref = db.collection('produtos')
    menu = ["Visualizar Produtos", "Adicionar Produto", "Atualizar Produto", "Deletar Produto"]
    choice = st.sidebar.selectbox("Menu de Operações", menu)

    if choice == "Visualizar Produtos":
        st.subheader("Todos os Produtos Cadastrados")
        docs = produtos_ref.order_by("nome").stream()
        produtos_lista = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
        if produtos_lista:
            st.dataframe(pd.DataFrame(produtos_lista), use_container_width=True)
        else:
            st.info("Nenhum produto cadastrado ainda.")

    elif choice == "Adicionar Produto":
        st.subheader("Adicionar Novo Produto")
        with st.form("add_form", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
            descricao = st.text_area("Descrição")
            if st.form_submit_button("Adicionar Produto"):
                if nome:
                    produtos_ref.add({"nome": nome, "preco": preco, "descricao": descricao})
                    st.success(f"Produto '{nome}' adicionado!")
                    st.balloons()
                else:
                    st.warning("O nome do produto é obrigatório.")

    elif choice == "Atualizar Produto":
        st.subheader("Atualizar um Produto Existente")
        docs = produtos_ref.order_by("nome").stream()
        produtos_dict = {doc.id: doc.to_dict().get('nome', 'Sem nome') for doc in docs}
        if produtos_dict:
            id_para_atualizar = st.selectbox("Selecione o produto", options=list(produtos_dict.keys()), format_func=produtos_dict.get)
            if id_para_atualizar:
                produto_atual = produtos_ref.document(id_para_atualizar).get().to_dict()
                with st.form("update_form"):
                    novo_nome = st.text_input("Nome", value=produto_atual.get('nome'))
                    novo_preco = st.number_input("Preço (R$)", value=float(produto_atual.get('preco', 0.0)), format="%.2f")
                    nova_descricao = st.text_area("Descrição", value=produto_atual.get('descricao'))
                    if st.form_submit_button("Atualizar Produto"):
                        updates = {"nome": novo_nome, "preco": novo_preco, "descricao": nova_descricao}
                        produtos_ref.document(id_para_atualizar).update(updates)
                        st.success(f"Produto '{novo_nome}' atualizado!")
                        
    elif choice == "Deletar Produto":
        st.subheader("Deletar um Produto")
        docs = produtos_ref.order_by("nome").stream()
        produtos_dict = {doc.id: doc.to_dict().get('nome', 'Sem nome') for doc in docs}
        if produtos_dict:
            id_para_deletar = st.selectbox("Selecione o produto para deletar", options=list(produtos_dict.keys()), format_func=produtos_dict.get)
            if st.button(f"Deletar '{produtos_dict.get(id_para_deletar)}'", type="primary"):
                produtos_ref.document(id_para_deletar).delete()
                st.success("Produto deletado.")
                st.experimental_rerun()