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
    r = []
    with psycopg.connect(**conn_info) as conn:
        tr = False
        if (query[:6].lower() == "insert" or query[:6].lower() == "update"):
            tr = True

        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            if tr:
                cur.execute("begin;")
            # Executar uma consulta
            cur.execute(query)
            # Obter todos os resultados
            rows = cur.fetchall()
            # Processar os resultados
            for row in rows:
                r.append(row)
            if tr:
                conn.commit()
    return r

app = Flask(__name__)

@app.route("/api/consultasaldo/<id_conta>", methods=['GET'])
def consultaSaldo(id_conta):
    r = do_query(f"select * from public.tbsaldos where id_conta = '{id_conta}' limit 1;")
    saldo = r[0]
    return jsonify(saldo), 200

@app.route("/api/consultaconta/<id_conta>", methods=['GET'])
def consultaContas(id_conta):
    r = do_query(f"select * from public.tbcontas where id_conta = '{id_conta}' limit 1;")
    conta = r[0]
    return jsonify(conta), 200

@app.route("/api/criarconta/", methods=['POST'])
def criarConta():
    if request.is_json:
        data = request.get_json()
        cpf = data["cpf"]
        nome = data["nome"]
        data_nascimento = data["data_nascimento"]
        endereco = data["endereco"]

        r = do_query(f"insert into public.tbcontas (cpf, nome, data_nascimento, endereco) values ('{cpf}', '{nome}', '{data_nascimento}', '{endereco}') returning id_conta;")
        id_conta = list(r)[0]["id_conta"]
        r2 = do_query(f"insert into public.tbsaldos (id_conta, saldo) values ('{id_conta}', 0.0) returning saldo;")
        return jsonify(id_conta), 200
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")


@app.route("/api/depositar/", methods=['POST'])
def depositar():
    if request.is_json:
        data = request.get_json()
        id_conta = data["id_conta"]
        valor = data["valor"]

        r = do_query(f"insert into public.tbtransacoes (id_conta, tipo, valor, descricao) values ('{id_conta}', 'ENTRADA', '{valor}', 'Deposito de valor') returning valor;")
        r2 = do_query(f"update public.tbsaldos set saldo = saldo + {valor} where id_conta = '{id_conta}' returning saldo;")
        return jsonify(r2), 200
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")

@app.route("/api/sacar/", methods=['POST'])
def sacar():
    if request.is_json:
        data = request.get_json()
        id_conta = data["id_conta"]
        valor = data["valor"]

        r = do_query(f"insert into public.tbtransacoes (id_conta, tipo, valor, descricao) values ('{id_conta}', 'SAIDA', '{valor}', 'Retirada de valor') returning valor;")
        r2 = do_query(f"update public.tbsaldos set saldo = saldo - {valor} where id_conta = '{id_conta}' returning saldo;")
        return jsonify(r2), 200
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")

@app.route("/api/transferir/", methods=['POST'])
def transferir():
    if request.is_json:
        data = request.get_json()
        id_conta = data["id_conta"]
        id_conta_destino = data["id_conta_destino"]
        valor = data["valor"]

        r = do_query(f"select saldo from public.tbsaldos where id_conta = '{id_conta}';")
        saldo_conta = r[0]["saldo"]

        if saldo_conta >= valor: # Tem saldo suficiente para a transferencia
            r1 = do_query(f"insert into public.tbtransacoes (id_conta, tipo, valor, descricao) values ('{id_conta}', 'SAIDA', '{valor}', 'Transferencia para conta {id_conta_destino}') returning valor;")
            r2 = do_query(f"insert into public.tbtransacoes (id_conta, tipo, valor, descricao) values ('{id_conta_destino}', 'ENTRADA', '{valor}', 'Transferencia recebida da conta {id_conta}') returning valor;")
            r3 = do_query(f"update public.tbsaldos set saldo = saldo - {valor} where id_conta = '{id_conta}' returning saldo;")
            r4 = do_query(f"update public.tbsaldos set saldo = saldo + {valor} where id_conta = '{id_conta_destino}' returning saldo;")
            novo_saldo = r3[0]
            return jsonify(novo_saldo), 200

        else: # Não tem saldo para a transferencia
            return jsonify({
                "erro": "Saldo insuficiente"
            }), 400
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")


@app.route("/api/consultaextrato/", methods=['POST'])
def consultarExtrato():
    if request.is_json:
        data = request.get_json()
        id_conta = data["id_conta"]
        
        r = do_query(f"select * from public.tbtransacoes where id_conta = '{id_conta}' order by hora desc limit 50;")
        return jsonify(r), 200
        
    else:
        abort(400, "Formato invalido, precisa ser JSON")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)