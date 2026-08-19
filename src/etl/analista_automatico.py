import os
import pandas as pd
from openai import OpenAI
import datetime
import streamlit as st
import sqlalchemy
import dotenv


dotenv.load_dotenv()
# """Trazendo as variaveis de ambiente"""

engine_pg = sqlalchemy.create_engine(
    f'postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}?client_encoding=utf8'
)
# """Criando a engine da conexão com o Postgre com adaptação de encoding (Tava dando dor de cabeça esse encoding)"""

st.title("Analista de Dados por IA")
# """Título no Streamlit"""

caminho_log  = os.getenv("caminho_log")
# """Definindo o documento do log"""

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
# """Defininido a chave ollama com variavel de ambiente """

client = OpenAI(api_key=OLLAMA_API_KEY, base_url="http://localhost:11434/v1")
# """Usando a chave API do modelo de I.A local como váriavel de ambiente; Porta padrão do Ollama"""

st_pergunta = st.text_input("Digite uma query que você deseja fazer em SQL: ")
# """Input no Streamlit da query desejada"""

MSG_SEGURANCA = "Violação identificada. Log registrado"
MSG_FORA_ESCOPO = "Desculpe, não posso ajudar com isso."
# """Constantes de mensagens de segurança e de violação do escopo"""

if st_pergunta.strip():
    # """Só executa caso haja algo enviado pelo user"""

    response = client.chat.completions.create(
        #Sintaxe do Streamlit para respostas do usuário
        model="llama?.?:?b", temperature=0.1, max_tokens=500, stream=False,#Definição de parâmetros, comportamentos e limites do modelo. Você define o modelo.
        messages=[
            {"role": "system", "content":
            "Você é um especialista em PostgreSQL que traduz linguagem natural apenas para comandos SELECT. "
            "É estritamente proibido retornar qualquer comando de modificação (INSERT, UPDATE, DELETE, DROP, etc). "
            f"Se o usuário solicitar modificações, responda exatamente: '{MSG_SEGURANCA}'. "
            f"Se a pergunta não for sobre SQL, responda apenas: '{MSG_FORA_ESCOPO}'. "
            "Os nomes de tabela escritos entre aspas devem ser interpretados exatamente como escritos, incluindo acentos e caracteres especiais. "
            "Se o usuário solicitar uma consulta que envolva múltiplas tabelas, use JOINs para relacioná-las. "
            "Não use markdown, não use crases, não use ```sql. "
            "O elemento de comparação principal deve ser os elementos das colunas-chave, quando existentes. "
            "Mapeie nomes amigáveis informados pelo usuário para os nomes reais das tabelas do banco, conforme configuração do projeto. "
            "A resposta deve começar diretamente com SELECT."},
            {"role": "user", "content": f"{st_pergunta}"},
            # """Acima os comandos para a I.A. É a gente definindo como a I.A vai se comportar"""
        ]
    )

    resposta = response.choices[0].message.content.strip()
    # """Definindo a variável resposta como a entrada do usuário"""

    with open(caminho_log, "a") as log:
        log.write(f"{datetime.datetime.now()}: Pergunta: {st_pergunta}\nResposta: {resposta}\n")
        # """Joga no log a pergunta enviada e a resposta que a I.A deu (No caso, a query que ela fez)"""

    st.write(resposta)
    # """Exibição do comando SQL gerado pela I.A, é mais pra controle"""

    if resposta not in (MSG_SEGURANCA, MSG_FORA_ESCOPO):
        # """Só executa a resposta caso seja um comando em SQL"""
        try:
            df_qry = pd.read_sql_query(resposta, engine_pg)
            # """Coração do programa. A engine que criamos vai pegar uma resposta (que é um script SQL) e executar no banco de dados"""
            engine_pg.dispose()
            # """Sempre fechando a conexão"""
            st.dataframe(df_qry, use_container_width=True)
            # """Print no Streamlit da query"""
        except Exception as e:
            st.error(f"Erro ao executar a consulta: {e}")
            # """Mensagem de erro"""

engine_pg.dispose()
