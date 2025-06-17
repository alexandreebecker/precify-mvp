# Arquivo: app.py

import streamlit as st
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import pandas as pd

# --- Configuração Inicial ---
st.set_page_config(page_title="Precify MVP", layout="wide")

# Função para inicializar a conexão com o Firebase
# Usamos @st.singleton para garantir que a conexão seja feita apenas uma vez.
@st.singleton
def firebase_connect():
    try:
        # Carrega as credenciais do arquivo .env (para desenvolvimento local)
        load_dotenv()
        
        # No Streamlit Cloud, usamos st.secrets para segurança
        if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in st.secrets:
            creds_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
            cred = credentials.Certificate(creds_json)
            print("Conectando via st.secrets...")
        else:
            # Conexão para rodar localmente (usa o .env)
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not cred_path:
                st.error("Credenciais do Firebase não encontradas localmente. Verifique o .env")
                return None
            cred = credentials.Certificate(cred_path)
            print("Conectando via arquivo local...")

        # Evita erro de reinicialização
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        print("✅ Conexão com Firebase estabelecida!")
        return firestore.client()

    except Exception as e:
        st.error(f"❌ Erro ao conectar com o Firebase: {e}")
        return None

# Conecta ao Firebase
db = firebase_connect()

# --- Interface do Aplicativo ---
st.title("📊 Painel de Precificação - Precify MVP")

if not db:
    st.warning("A aplicação não pode ser carregada pois a conexão com o banco de dados falhou.")
else:
    # Referência à coleção de produtos
    produtos_ref = db.collection('produtos')

    # --- Seção de CRUD ---
    menu = ["Visualizar Produtos", "Adicionar Produto", "Atualizar Produto", "Deletar Produto"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Visualizar Produtos":
        st.subheader("Todos os Produtos Cadastrados")
        try:
            docs = produtos_ref.stream()
            produtos_lista = []
            for doc in docs:
                produto = doc.to_dict()
                produto['id'] = doc.id
                produtos_lista.append(produto)

            if produtos_lista:
                df = pd.DataFrame(produtos_lista)
                st.dataframe(df)
            else:
                st.info("Nenhum produto cadastrado ainda.")
        except Exception as e:
            st.error(f"Erro ao buscar produtos: {e}")

    elif choice == "Adicionar Produto":
        st.subheader("Adicionar Novo Produto")
        with st.form("add_form", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço do Produto", min_value=0.0, format="%.2f")
            descricao = st.text_area("Descrição (Opcional)")
            
            submitted = st.form_submit_button("Adicionar")
            if submitted:
                if nome and preco:
                    data = {"nome": nome, "preco": preco, "descricao": descricao}
                    produtos_ref.add(data)
                    st.success(f"Produto '{nome}' adicionado com sucesso!")
                else:
                    st.warning("Nome e Preço são obrigatórios.")

    elif choice == "Atualizar Produto":
        st.subheader("Atualizar um Produto Existente")
        
        # Pega a lista de produtos para o selectbox
        docs = produtos_ref.stream()
        produtos_dict = {doc.id: doc.to_dict()['nome'] for doc in docs}

        if not produtos_dict:
            st.warning("Nenhum produto para atualizar.")
        else:
            id_para_atualizar = st.selectbox("Selecione o produto para atualizar", options=list(produtos_dict.keys()), format_func=lambda x: f"{produtos_dict[x]} (ID: {x})")
            
            if id_para_atualizar:
                produto_atual = produtos_ref.document(id_para_atualizar).get().to_dict()
                
                with st.form("update_form"):
                    novo_nome = st.text_input("Novo nome", value=produto_atual.get('nome', ''))
                    novo_preco = st.number_input("Novo preço", value=float(produto_atual.get('preco', 0.0)), format="%.2f")
                    nova_descricao = st.text_area("Nova descrição", value=produto_atual.get('descricao', ''))
                    
                    update_submitted = st.form_submit_button("Atualizar")
                    if update_submitted:
                        novos_dados = {"nome": novo_nome, "preco": novo_preco, "descricao": nova_descricao}
                        produtos_ref.document(id_para_atualizar).update(novos_dados)
                        st.success(f"Produto '{novo_nome}' atualizado com sucesso!")

    elif choice == "Deletar Produto":
        st.subheader("Deletar um Produto")
        
        docs = produtos_ref.stream()
        produtos_dict = {doc.id: doc.to_dict()['nome'] for doc in docs}
        
        if not produtos_dict:
            st.warning("Nenhum produto para deletar.")
        else:
            id_para_deletar = st.selectbox("Selecione o produto para deletar", options=list(produtos_dict.keys()), format_func=lambda x: f"{produtos_dict[x]} (ID: {x})")
            
            if st.button("Deletar Produto Selecionado", type="primary"):
                produtos_ref.document(id_para_deletar).delete()
                st.success(f"Produto deletado com sucesso!")
                st.experimental_rerun() # Recarrega a página para atualizar a lista