import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

def get_sheet(worksheet_name):
    """Lê uma aba do Google Sheets e retorna um DataFrame"""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # Pega o ID da planilha do .env
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    if not sheet_id:
        raise ValueError("GOOGLE_SHEETS_ID não encontrado no .env")

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()

    return pd.DataFrame(data)