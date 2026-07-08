import datetime
import sqlite3

import pandas as pd
from openai import OpenAI

caminho_log = r"caminho_log"
caminho_banco = r"caminho_banco"

client = OpenAI(api_key="ollama", base_url="localhost")

pergunta = input("Digite uma query que você deseja fazer em SQL: ")

response = client.chat.completions.create(
    model="llama3.2:3b",
    temperature=0.7,
    max_tokens=500,
    stream=False,
    messages=[
        {
            "role": "system",
            "content": "Você é um especialista em SQLite que traduz linguagem natural apenas para comandos SELECT. É estritamente proibido retornar qualquer comando de modificação (INSERT, UPDATE, DELETE, DROP, etc). Se o usuário solicitar modificações, responda exatamente: 'Procure o setor de T.I. Log registrado'. Se a pergunta não for sobre SQL, responda apenas: 'Desculpe, não posso ajudar com isso.'. Retorne APENAS o comando SQL, sem explicações.",
        },
        {"role": "user", "content": pergunta},
    ],
)

resposta = response.choices[0].message.content.strip()
print(response.choices[0].message.content)

with open(caminho_log, "a") as log:
    log.write(f"{datetime.datetime.now()}: Pergunta: {pergunta}\nResposta: {resposta}\n")

conexao = sqlite3.connect(caminho_banco)
df_qry = pd.read_sql_query(f"{resposta}", conexao)

print(df_qry.to_markdown(index=False, tablefmt="grid"))
