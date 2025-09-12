import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dotenv import load_dotenv
import os

#Utilizando .env para pegar o ID da planilha
load_dotenv()
planilha_id = os.getenv("GOOGLE_SHEETS_ID")


file_name = "credentials.json"
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    filename=file_name,
    scopes=scopes
)
client = gspread.authorize(creds)

# Abrir planilha completa pelo ID
planilha_completa = client.open_by_key(planilha_id)

# Seleciona as abas d planilh
planilha_vendas = planilha_completa.get_worksheet(0)
planilha_sellout = planilha_completa.get_worksheet(1)
planilha_metas = planilha_completa.get_worksheet(2)

# Transformar em DataFrame os dados das abas
dados_vendas = planilha_vendas.get_all_records()
dados_sellout = planilha_sellout.get_all_records()
dados_metas = planilha_metas.get_all_records()

# Função para criar o data frame
def mostrar_planilha(planilha):
  dados = planilha.get_all_records()
  df = pd.DataFrame(dados)
  print(df)

mostrar_planilha(planilha_metas)