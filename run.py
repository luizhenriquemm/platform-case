from flask import Flask, jsonify, request, abort
import psycopg
import json

# Defina os parâmetros de conexão
conn_info = {
    "host": "localhost",     # Endereço do servidor de banco de dados
    "port": 5432,           # Porta padrão para PostgreSQL
    "dbname": "postgres",  # Nome do banco de dados
    "user": "postgres",  # Nome de usuário
    "password": "password" # Senha do usuário
}

def do_query(query: str):
    with psycopg.connect(**conn_info) as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            # Executar uma consulta
            cur.execute(query)
            # Obter todos os resultados
            rows = cur.fetchall()
            # Processar os resultados
            for row in rows:
                yield row

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    r = do_query("select * from public.clients")
    return jsonify(list(r)), 200

@app.route("/insert", methods=['POST'])
def insert_pg():
    if request.is_json:
        data = request.get_json()
        response = {
            'status': 'success',
            'data': data
        }
        return jsonify(response), 200
    else:
        response = {
            'status': 'error',
            'message': 'Request data must be in JSON format.'
        }
        # return jsonify(response), 400
        abort(400, "Invalid a")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)