import os
import json
import re
import unicodedata
from datetime import datetime

import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

INPUT_FILE_1 = os.getenv("INPUT_FILE_1")
INPUT_FILE_2 = os.getenv("INPUT_FILE_2")
INPUT_FILE_3 = os.getenv("INPUT_FILE_3")
INPUT_FILE_4 = os.getenv("INPUT_FILE_4")
LOG_FILE = os.getenv("LOG_FILE")

INPUT_SHEET_1 = os.getenv("INPUT_SHEET_1")
INPUT_SHEET_2 = os.getenv("INPUT_SHEET_2")
INPUT_SHEET_3 = os.getenv("INPUT_SHEET_3")

OUTPUT_TABLE_1 = os.getenv("OUTPUT_TABLE_1")
OUTPUT_TABLE_2 = os.getenv("OUTPUT_TABLE_2")
OUTPUT_TABLE_3 = os.getenv("OUTPUT_TABLE_3")
OUTPUT_TABLE_4 = os.getenv("OUTPUT_TABLE_4")

BAIRROS_CORRIGIDOS = json.loads(
    os.getenv("BAIRROS_CORRIGIDOS_JSON", '{"BAIRRO_ERRADO": "BAIRRO CERTO"}')
)
LOGRADOUROS_CORRIGIDOS = json.loads(
    os.getenv("LOGRADOUROS_CORRIGIDOS_JSON", '{"LOGRADOURO_ERRADO": "LOGRADOURO_CERTO"}')
)

engine_db = create_engine(
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
    f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
)

def registrar_log(mensagem: str) -> None:
    """Grava uma mensagem no arquivo de log e no console, com timestamp."""
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    linha = f"[{timestamp}] {mensagem}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as arquivo_log:
        arquivo_log.write(linha)
    print(linha.strip())


def apagar_vazias(df: pd.DataFrame) -> pd.DataFrame:
    """Remove colunas sem nome criadas durante a leitura."""
    colunas_fantasma = [col for col in df.columns if "Unnamed:" in str(col)]
    return df.drop(columns=colunas_fantasma)


def somente_alfanumerico(texto: str) -> str:
    """Mantém apenas letras e números de um texto."""
    return "".join(filter(str.isalnum, texto))


def remover_acentos(texto: str) -> str:
    """Remove acentuação de um texto, mantendo os caracteres ASCII."""
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")


ABREVIACOES_LOGRADOURO = {
    "RUA": "R",
    "BECO": "BC",
    "AVENIDA": "AV",
    "VIA": "VI",
}


def limpar(texto) -> str:
    """Normaliza um campo de endereço: maiúsculas, sem acento e sem espaços."""
    if pd.isna(texto) or str(texto).strip() == "" or str(texto).upper() == "NAN":
        return ""

    resultado = str(texto).upper()
    for termo, sigla in ABREVIACOES_LOGRADOURO.items():
        resultado = resultado.replace(termo, sigla)

    resultado = remover_acentos(resultado)

    for termo, sigla in LOGRADOUROS_CORRIGIDOS.items():
        resultado = resultado.replace(termo, sigla)
    return somente_alfanumerico(resultado)


def compl(texto) -> str:
    """Padroniza o campo de complemento de endereço (AP, CASA, LOJA etc)."""
    if pd.isna(texto):
        return ""

    valor = str(texto).strip().upper()
    if valor in ("", "NAN", " ", "CA"):
        return ""
    return valor.replace(" ", "").replace("CASA", "CA").replace("LOJA", "LJ").replace(".", "").replace("KITNET", "CA").replace(",","")


def matricula_vazia_nova(texto) -> str:
    """Padroniza o campo de matrícula, substituindo 'NOVA' por 'NOVO'."""
    if not texto:
        return ""

    valor = str(texto).upper().replace("NOVA", "NOVO").strip()
    if valor == "":
        return "NOVO"
    return somente_alfanumerico(valor)


def erros_ocasionais(texto):
    """Corrige nomes de bairro com erros de digitação conhecidos."""
    if pd.isna(texto):
        return texto

    valor = str(texto).strip().upper()
    return BAIRROS_CORRIGIDOS.get(valor, texto)


def erros_ocasionais_RUA(texto):
    """Corrige nomes de rua com erros de digitação conhecidos."""
    if pd.isna(texto):
        return texto

    valor = str(texto).strip().upper()
    return LOGRADOUROS_CORRIGIDOS.get(valor, texto)


def chave_baixas_tratado(texto) -> str:
    """Monta a chave de comparação (logradouro + número + complemento + bairro)"""
    endereco = str(texto).strip().upper()
    endereco = re.sub(r"\d{5}-?\d{3}", "", endereco)  # remove CEP

    match = re.search(r"\(([^)]+)\)", endereco)
    complemento = match.group(1).strip() if match else "CASA"
    endereco = re.sub(r"\([^)]*\)", "", endereco)
    endereco = endereco.replace("CONTAGEM", "").replace("- MG", "").replace(",MG", "")

    logradouro_numero, _, bairro = endereco.partition(" - ")
    logradouro, _, numero = logradouro_numero.partition(",")

    for abrev, cheio in (("R.", "RUA"), ("BC.", "BC"), ("AV.", "AV")):
        logradouro = logradouro.replace(abrev, cheio)
    logradouro = somente_alfanumerico(logradouro)
    for cheio, sigla in (("RUA", "R"), ("AVENIDA", "AV"), ("BECO", "BC")):
        logradouro = logradouro.replace(cheio, sigla)

    numero = somente_alfanumerico(numero.strip())
    complemento = somente_alfanumerico(complemento.replace("CA ", "CASA")).replace("CASA", "CA")
    bairro = somente_alfanumerico(bairro.strip())

    return f"{logradouro}{numero}{complemento}{bairro}"


def sincronizar_dados_baixas_tratado():
    """Lê dados tratados, georreferencia e grava no destino configurado."""
    try:
        registrar_log("Lendo dados tratados")
        df = pd.read_excel(INPUT_FILE_1, sheet_name=INPUT_SHEET_1, engine="openpyxl")
        df["chave"] = df["Endereço"].apply(chave_baixas_tratado)

        registrar_log("Georreferenciando dados")
        df_geo = df.copy()
        geometria = gpd.points_from_xy(x=df_geo["Longitude"], y=df_geo["Latitude"])
        gdf = gpd.GeoDataFrame(df_geo, geometry=geometria)
        gdf.set_crs(epsg=4326, inplace=True)

        registrar_log("Enviando dados para o destino configurado")
        gdf.to_postgis(name=OUTPUT_TABLE_1, con=engine_db, if_exists="replace", index=False)

        registrar_log(f"Sucesso: {len(gdf)} linhas sincronizadas para '{OUTPUT_TABLE_1}'.")
    except Exception as e:
        registrar_log(f"Erro: {str(e)}")


def sincronizar_dados_ControleDeObra():
    """Lê a planilha de adesão x serviços, monta a chave de comparação e grava no banco."""
    try:
        registrar_log("Lendo dados de controle")
        df = pd.read_excel(
            INPUT_FILE_2, sheet_name=INPUT_SHEET_2, engine="openpyxl"
        )

        df = apagar_vazias(df)
        df["MATRÍCULA"] = df["MATRÍCULA"].apply(matricula_vazia_nova)
        df["COMPLEMENTO:"] = df["COMPLEMENTO:"].apply(compl)

        df["chave"] = (
            df["LOGRADOURO"].apply(limpar).replace("RUA", "R").replace("AVENIDA", "AV").replace("BECO", "BC").replace(",", "")
            + df["Nº"].apply(limpar)
            + df["COMPLEMENTO:"].apply(compl).replace("CASA", "CA")
            + df["BAIRRO"].apply(limpar).apply(erros_ocasionais)
        ).replace("|", "").replace("(", "").replace(")", "")
        
        registrar_log("Enviando dados de controle para o destino configurado")
        df.to_sql(OUTPUT_TABLE_2, engine_db, if_exists="replace", index=False)

        registrar_log(f"Sucesso: {len(df)} linhas sincronizadas para '{OUTPUT_TABLE_2}'.")
    except Exception as e:
        registrar_log(f"Erro: {str(e)}")


def sincronizar_dados_baixas_sem_tratamento():
    """Lê dados sem tratamento e grava no destino configurado."""
    try:
        registrar_log("Lendo dados sem tratamento")
        df = pd.read_excel(
            INPUT_FILE_3, sheet_name=INPUT_SHEET_3, engine="openpyxl"
        )

        registrar_log("Enviando dados sem tratamento para o destino configurado")
        df.to_sql(OUTPUT_TABLE_3, engine_db, if_exists="replace", index=False)

        registrar_log(f"Sucesso: {len(df)} linhas sincronizadas para '{OUTPUT_TABLE_3}'.")
    except Exception as e:
        registrar_log(f"Erro: {str(e)}")


def sincronizar_app_vistoria():
    df_app = pd.read_csv(INPUT_FILE_4, sep=";", encoding="ISO-8859-1")
    df_app.to_sql(OUTPUT_TABLE_4, engine_db, if_exists="replace", index=False)


if __name__ == "__main__":
    sincronizar_dados_baixas_tratado()
    sincronizar_dados_ControleDeObra()
    sincronizar_dados_baixas_sem_tratamento()
    sincronizar_app_vistoria()
engine_db.dispose()
