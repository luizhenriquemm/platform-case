drop table if exists public.tbsaldos;
drop table if exists public.tbtransacoes;
drop table if exists public.tbcontas;

create table public.tbsaldos (
	id_conta bigint NOT NULL,
	saldo numeric NOT NULL,
    CONSTRAINT tbsaldos_pk PRIMARY KEY (id_conta)
);

create table public.tbtransacoes (
    id_conta bigint NOT NULL,
    tipo varchar(32) NOT NULL,
    valor numeric NOT NULL,
    descricao varchar(255) NOT NULL,
    hora timestamp NULL DEFAULT now()
);

create table public.tbcontas (
    id_conta serial NOT NULL,
    cpf varchar(64) NOT NULL,
    nome varchar(64) NOT NULL,
    data_nascimento varchar(64) NOT NULL,
    endereco varchar(128) NOT NULL,
    CONSTRAINT tbcontas_pk PRIMARY KEY (id_conta)
);
create index tbcontas_id_conta_idx on public.tbcontas (id_conta);