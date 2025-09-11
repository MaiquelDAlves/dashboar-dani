#utils/google_sheets.py

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet(worksheet_name, sheet_id):
    """Lê uma aba do Google Sheets e retorna um DataFrame"""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()

    return pd.DataFrame(data)
