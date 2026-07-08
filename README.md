# Banco de Dados Revitaliza Pampulha

## Visão Geral
Este repositório reúne scripts Python para apoio operacional ao projeto Revitaliza Pampulha (COPASA), com foco em:
- tratamento e padronização de dados;
- sincronização de planilhas para base SQLite;
- auditoria de inconsistências cadastrais;
- migração de tabelas para PostgreSQL;
- preparação de dados para uso em contexto GIS.

Os caminhos de arquivos, nomes de tabelas e parâmetros de conexão estão configurados com valores de exemplo e devem ser ajustados para o ambiente de execução.

## Objetivos
- Padronizar e consolidar dados de campo e adesão.
- Automatizar cargas periódicas para SQLite.
- Identificar e corrigir irregularidades em chaves de endereço.
- Permitir consultas assistidas por linguagem natural com controle de segurança.
- Viabilizar migração de dados para PostgreSQL.

## Estrutura do Repositório
```text
.
├── src/
│   ├── etl/
│   │   ├── adesao_tratada.py
│   │   ├── comparacao_matricula.py
│   │   ├── resolvendo_irregularidades.py
│   │   └── analista_automatico.py
│   ├── sync/
│   │   ├── sincronia_auto.py
│   │   └── sincronia_cadastro_auto.py
│   └── migration/
│       └── migracao.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Requisitos
- Python 3.10 ou superior
- Ambiente virtual Python (recomendado)
- Banco SQLite local
- Acesso a instância PostgreSQL (para migração)
- Arquivos Excel de entrada conforme layout esperado em cada script

## Instalação
```bash
git clone https://github.com/ghccostagustavo-cpu/Banco_de_Dados_Revitaliza_Pampulha.git
cd Banco_de_Dados_Revitaliza_Pampulha

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Como Executar
Antes da execução, ajuste os caminhos e nomes de tabela diretamente em cada script.

### 1) Sincronização principal (baixas, adesão, baixas secundárias e caça esgoto)
```bash
python src/sync/sincronia_auto.py
```

### 2) Sincronização de cadastro geográfico
```bash
python src/sync/sincronia_cadastro_auto.py
```

### 3) Tratamento de base de adesão
```bash
python src/etl/adesao_tratada.py
```

### 4) Comparação de matrícula entre bases
```bash
python src/etl/comparacao_matricula.py
```

### 5) Correção de irregularidades por similaridade de chave
```bash
python src/etl/resolvendo_irregularidades.py
```

### 6) Migração de tabelas SQLite para PostgreSQL
```bash
python src/migration/migracao.py
```

### 7) Consulta em linguagem natural convertida para SQL (somente SELECT)
```bash
python src/etl/analista_automatico.py
```

## Fluxo de Dados (resumo)
1. Leitura de planilhas operacionais (Excel).
2. Padronização de campos críticos (logradouro, número, complemento, matrícula e bairro).
3. Geração de chave composta para integração entre bases.
4. Carga/atualização de tabelas em SQLite.
5. Auditoria e correção de inconsistências em chaves.
6. Migração de tabelas consolidadas para PostgreSQL quando necessário.

## Banco de Dados
### SQLite (estado atual)
- Base operacional principal para integração e consultas locais.
- Escrita de tabelas via `pandas.to_sql` com estratégia de substituição (`if_exists='replace'`) nos fluxos atuais.

### Migração para PostgreSQL
- Script dedicado em `src/migration/migracao.py`.
- Leitura das tabelas do SQLite e carga no PostgreSQL em nomes normalizados (minúsculo).
- Necessário configurar corretamente string de conexão, permissões e ambiente do servidor.

## Boas Práticas / Observações Operacionais
- Não versionar arquivos de banco, planilhas ou logs operacionais.
- Validar colunas esperadas antes de execução em produção.
- Executar scripts em ambiente virtual dedicado.
- Revisar logs após cada execução para tratamento de exceções.
- Homologar em base de teste antes de rodar cargas em ambiente oficial.

## Licença
Projeto licenciado sob **GPL-3.0**. Consulte o arquivo [LICENSE](LICENSE).
