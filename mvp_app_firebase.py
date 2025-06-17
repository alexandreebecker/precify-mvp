# ==============================================================================
# MVP do Projeto Precify - API de Produtos com Flask e Firebase (VERSÃO CORRIGIDA)
# ==============================================================================

# --- 1. Importações de Bibliotecas ---
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify

# --- 2. Configuração Inicial ---

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialização do Flask
app = Flask(__name__)

# --- INICIALIZAÇÃO DO FIREBASE (isto fica aqui) ---
# Tenta carregar as credenciais. Se falhar, a variável 'cred' será None.
try:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise ValueError("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não foi definida.")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("✅ Conexão com Firebase estabelecida com sucesso!")
except Exception as e:
    # Apenas imprime o erro aqui. A aplicação será encerrada mais abaixo se a conexão falhar.
    print(f"❌ Erro na configuração do Firebase: {e}")
    # Define db como None para que possamos verificar depois
    db = None
else:
    # Se o 'try' funcionou, define o cliente do banco de dados
    db = firestore.client()
    produtos_ref = db.collection('produtos')

# --- 3. Definição das Rotas da API (CRUD) ---
# (O código do seu CRUD continua aqui exatamente como antes, não precisa mudar nada)

# CREATE: Adicionar um novo produto
@app.route('/produtos', methods=['POST'])
def create_produto():
    if not db: return jsonify({"error": "Conexão com o banco não estabelecida."}), 503
    try:
        data = request.get_json()
        if not data or not 'nome' in data or not 'preco' in data:
            return jsonify({"error": "Dados incompletos. 'nome' e 'preco' são obrigatórios."}), 400
        timestamp, doc_ref = produtos_ref.add(data)
        return jsonify({"success": True, "id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro: {e}"}), 500

# ... TODAS AS SUAS OUTRAS ROTAS (get_produtos, get_produto, update, delete) ...
# ... Elas ficam aqui, sem alterações ...

@app.route('/', methods=['GET'])
def index():
    status = "conectada" if db else "desconectada"
    return jsonify({"message": f"API do Precify está no ar! Conexão com Firebase: {status}"}), 200

# READ (All): Obter todos os produtos
@app.route('/produtos', methods=['GET'])
def get_produtos():
    if not db: return jsonify({"error": "Conexão com o banco não estabelecida."}), 503
    try:
        todos_produtos = []
        for doc in produtos_ref.stream():
            produto = doc.to_dict()
            produto['id'] = doc.id
            todos_produtos.append(produto)
        return jsonify(todos_produtos), 200
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro: {e}"}), 500

# READ (One): Obter um produto específico pelo ID
@app.route('/produtos/<string:id>', methods=['GET'])
def get_produto(id):
    if not db: return jsonify({"error": "Conexão com o banco não estabelecida."}), 503
    try:
        doc = produtos_ref.document(id).get()
        if doc.exists:
            produto = doc.to_dict()
            produto['id'] = doc.id
            return jsonify(produto), 200
        else:
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro: {e}"}), 500

# UPDATE: Atualizar um produto existente pelo ID
@app.route('/produtos/<string:id>', methods=['PUT', 'PATCH'])
def update_produto(id):
    if not db: return jsonify({"error": "Conexão com o banco não estabelecida."}), 503
    try:
        data = request.get_json()
        doc_ref = produtos_ref.document(id)
        if not doc_ref.get().exists:
             return jsonify({"error": "Produto não encontrado para atualizar"}), 404
        doc_ref.update(data)
        return jsonify({"success": True, "message": f"Produto {id} atualizado."}), 200
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro: {e}"}), 500

# DELETE: Deletar um produto pelo ID
@app.route('/produtos/<string:id>', methods=['DELETE'])
def delete_produto(id):
    if not db: return jsonify({"error": "Conexão com o banco não estabelecida."}), 503
    try:
        doc_ref = produtos_ref.document(id)
        if not doc_ref.get().exists:
             return jsonify({"error": "Produto não encontrado para deletar"}), 404
        doc_ref.delete()
        return jsonify({"success": True, "message": f"Produto {id} deletado."}), 200
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro: {e}"}), 500


# --- 4. Execução da Aplicação ---
if __name__ == '__main__':
    # Verifica se a conexão com o banco foi bem sucedida antes de rodar o app
    if not db:
        print("❌ Aplicação não pôde ser iniciada. Verifique o erro de conexão com o Firebase acima.")
        exit() # Agora o exit() está no lugar certo!

    # Use a solução rápida aqui se o erro persistir
    app.run(debug=True, port=5000, use_reloader=False)