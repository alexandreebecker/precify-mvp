# ==============================================================================
# Precify MVP - Painel de Precificação com Streamlit e Firebase
# VERSÃO FINAL CORRIGIDA
# ==============================================================================

# --- 1. Importações de Bibliotecas ---
import streamlit as st
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import pandas as pd
# A importação do ExperimentalBaseConnection pode variar, mas esta é a mais comum
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_resource

# --- 2. Configuração da Conexão com Firebase (Método Moderno e CORRIGIDO) ---

# Classe de Conexão Customizada para o Firebase Admin SDK
class FirebaseConnection(ExperimentalBaseConnection[firestore.Client]):
    def _connect(self, **kwargs) -> firestore.Client:
        # Tenta buscar as credenciais dos segredos do Streamlit (para deploy)
        if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in st.secrets:
            creds_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
            cred = credentials.Certificate(creds_json)
        else:
            # Se não estiver em deploy, tenta conectar localmente usando .env
            try:
                load_dotenv()
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                cred = credentials.Certificate(cred_path)
            except Exception as e:
                st.error(f"Credenciais locais do Firebase não encontradas: {e}")
                return None
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        return firestore.client()

    def get_client(self) -> firestore.Client:
        return self._instance

# --- 3. Inicialização da Aplicação e Conexão ---

st.set_page_config(page_title="Precify MVP", layout="wide")
st.title("📊 Painel de Precificação - Precify MVP")

# Tenta estabelecer a conexão USANDO A FORMA CORRETA
try:
    # AQUI ESTÁ A CORREÇÃO: Usamos st.connection para criar a instância
    conn = st.connection("firebase", type=FirebaseConnection)
    db = conn.get_client()
except Exception as e:
    st.error(f"❌ Falha crítica ao inicializar a conexão com o Firebase: {e}")
    db = None

# --- 4. Interface Principal da Aplicação ---

if not db:
    st.warning("A aplicação não pode ser carregada pois a conexão com o banco de dados falhou.")
    st.stop()
else:
    # O restante do código do CRUD (visualizar, adicionar, etc.) permanece exatamente o mesmo.
    # Não precisa alterar nada daqui para baixo.
    
    produtos_ref = db.collection('produtos')
    menu = ["Visualizar Produtos", "Adicionar Produto", "Atualizar Produto", "Deletar Produto"]
    choice = st.sidebar.selectbox("Menu de Operações", menu)

    if choice == "Visualizar Produtos":
        st.subheader("Todos os Produtos Cadastrados")
        try:
            docs = produtos_ref.order_by("nome").stream()
            produtos_lista = []
            for doc in docs:
                produto = doc.to_dict()
                produto['id'] = doc.id
                produtos_lista.append(produto)

            if produtos_lista:
                df = pd.DataFrame(produtos_lista)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum produto cadastrado ainda.")
        except Exception as e:
            st.error(f"Erro ao buscar produtos: {e}")

    elif choice == "Adicionar Produto":
        st.subheader("Adicionar Novo Produto")
        with st.form("add_form", clear_on_submit=True):
            nome = st.text_input("Nome do Produto", placeholder="Ex: Análise de Concorrentes")
            preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
            descricao = st.text_area("Descrição (Opcional)")
            
            submitted = st.form_submit_button("Adicionar Produto")
            if submitted:
                if nome and preco is not None:
                    data = {"nome": nome, "preco": preco, "descricao": descricao}
                    produtos_ref.add(data)
                    st.success(f"Produto '{nome}' adicionado com sucesso!")
                else:
                    st.warning("Os campos 'Nome' e 'Preço' são obrigatórios.")

    elif choice == "Atualizar Produto":
        st.subheader("Atualizar um Produto Existente")
        try:
            docs = produtos_ref.order_by("nome").stream()
            produtos_dict = {doc.id: doc.to_dict().get('nome', 'Nome não encontrado') for doc in docs}

            if not produtos_dict:
                st.warning("Nenhum produto para atualizar.")
            else:
                id_para_atualizar = st.selectbox("Selecione o produto para atualizar", options=list(produtos_dict.keys()), format_func=lambda x: f"{produtos_dict[x]} (ID: ...{x[-6:]})")
                
                if id_para_atualizar:
                    produto_atual = produtos_ref.document(id_para_atualizar).get().to_dict()
                    
                    with st.form("update_form"):
                        st.write(f"Editando: **{produto_atual.get('nome', '')}**")
                        novo_nome = st.text_input("Novo nome", value=produto_atual.get('nome', ''))
                        novo_preco = st.number_input("Novo preço (R$)", value=float(produto_atual.get('preco', 0.0)), format="%.2f")
                        nova_descricao = st.text_area("Nova descrição", value=produto_atual.get('descricao', ''))
                        
                        update_submitted = st.form_submit_button("Atualizar Produto")
                        if update_submitted:
                            novos_dados = {"nome": novo_nome, "preco": novo_preco, "descricao": nova_descricao}
                            produtos_ref.document(id_para_atualizar).update(novos_dados)
                            st.success(f"Produto '{novo_nome}' atualizado com sucesso!")
                            st.balloons()
        except Exception as e:
            st.error(f"Erro ao carregar produtos para atualização: {e}")

    elif choice == "Deletar Produto":
        st.subheader("Deletar um Produto")
        try:
            docs = produtos_ref.order_by("nome").stream()
            produtos_dict = {doc.id: doc.to_dict().get('nome', 'Nome não encontrado') for doc in docs}
            
            if not produtos_dict:
                st.warning("Nenhum produto para deletar.")
            else:
                id_para_deletar = st.selectbox("Selecione o produto para deletar", options=list(produtos_dict.keys()), format_func=lambda x: f"{produtos_dict[x]} (ID: ...{x[-6:]})")
                
                st.warning(f"⚠️ Atenção! Esta ação é irreversível.")
                if st.button(f"Deletar permanentemente o produto '{produtos_dict.get(id_para_deletar)}'", type="primary"):
                    produtos_ref.document(id_para_deletar).delete()
                    st.success(f"Produto deletado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar produtos para deleção: {e}")