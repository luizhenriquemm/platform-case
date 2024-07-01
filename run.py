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

@app.route("/api/consultaSaldo/<id_conta>", methods=['GET'])
def consultaSaldo(id_conta):
    r = do_query(f"select * from public.tbsaldos where id_conta = '{id_conta}'")
    return jsonify( list(r) ), 200

@app.route("/api/consultaContas/<id_conta>", methods=['GET'])
def consultaContas(id_conta):
    r = do_query(f"select * from public.tbcontas where id_conta = '{id_conta}'")
    return jsonify( list(r) ), 200

@app.route("/api/criarConta/", methods=['POST'])
def criarConta():
    if request.is_json:
        data = request.get_json()
        cpf = data["cpf"]
        nome = data["nome"]
        data_nascimento = data["data_nascimento"]
        endereco = data["endereco"]

        r = do_query(f"insert into public.tbcontas (cpf, nome, data_nascimento, endereco) values ('{cpf}', '{nome}', '{data_nascimento}', '{endereco}') returning id_conta")
        id_conta = list(r)[0]["id_conta"]
        r2 = do_query(f"inser into public.tbsaldos (id_conta, saldo) values ('{id_conta}', 0.0)")
        return jsonify(id_conta), 200
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")


@app.route("/api/depositar/", methods=['POST'])
def depositar():
    if request.is_json:
        data = request.get_json()
        id_conta = data["id_conta"]
        valor = data["valor"]

        r = do_query(f"insert into public.tbtransacoes (id_conta, tipo, valor, descricao) values ('{id_conta}', 'ENTRADA', '{valor}', 'Deposito de valor') returning valor")
        r2 = do_query(f"update public.tbsaldos set saldo = saldo + {valor} where id_conta = '{id_conta}'")
        return jsonify(id_conta), 200
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)