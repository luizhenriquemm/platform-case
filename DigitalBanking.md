tbsaldos
    id_conta integer não nulo
    saldo decimal(16,2) não nulo

tbtransacoes
    id_conta integer não nulo
    tipo string não nulo (entrada ou saida)
    valor decimal(16,2) não nulo
    descricao string nulo

tbcontas
    id_conta serial não nulo
    cpf string(64) não nulo
    nome string(64) não nulo
    data_nascimento string(64) não nulo
    endereco string(128) não nulo