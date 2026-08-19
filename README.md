# Banco de Dados Revitaliza Pampulha

## Visão geral
Este repositório reúne scripts Python para apoio operacional ao projeto Revitaliza Pampulha (COPASA), com foco em:
- sincronização de planilhas para base Postgres, SQLite anteriormente;
- auditoria e correção de inconsistências cadastrais;
- consulta assistida por linguagem natural (somente SELECT).

## Estrutura atual do projeto
```text
.
├── src/
│   ├── __init__.py
│   └── etl/
│       ├── __init__.py
│       ├── analista_automatico.py
│       ├── resolvendo_irregularidades.py
│       └── sync/
│           ├── __init__.py
│           └── sincronia_auto.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Requisitos
- Python 3.10+
- Ambiente virtual Python (recomendado)
- Banco SQLite local
- Banco Postgres em qualquer servidor que se tenha acesso
- Arquivos Excel de entrada conforme layout esperado nos scripts

## Instalação
```bash
git clone https://github.com/ghccostagustavo-cpu/Banco_de_Dados_Revitaliza_Pampulha.git
cd Banco_de_Dados_Revitaliza_Pampulha

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Como executar
Antes da execução, ajuste caminhos, parâmetros e nomes de tabela diretamente em cada script.

### 1) Sincronização principal
```bash
python src/etl/sync/sincronia_auto.py
```

### 2) Correção de irregularidades por similaridade de chave
```bash
python src/etl/resolvendo_irregularidades.py
```

### 3) Consulta em linguagem natural convertida para SQL (somente SELECT)
```bash
python src/etl/analista_automatico.py
```

## Boas práticas
- Não versionar bancos, planilhas e logs operacionais.
- Validar colunas esperadas antes de execução em produção.
- Revisar logs após cada execução.
- Homologar em base de teste antes de rodar em ambiente oficial.

## Licença
Projeto licenciado sob **GPL-3.0**. Consulte [LICENSE](LICENSE).


(Só pra aviso, copilot formatou o README e só organizou as pastas do diretório)
