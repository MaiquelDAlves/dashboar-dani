# Dashboard Dani

Um dashboard em **Streamlit** para análise de dados de vendas, sell-out e metas, integrado ao **Google Sheets**.  
O objetivo é centralizar os indicadores em uma interface web interativa e visual.

---

## Funcionalidades

- Visualização de **vendas, sell-out e metas** em abas separadas.
- Layout responsivo usando **containers, colunas e gráficos**.
- Integração com **Google Sheets** para leitura e atualização dos dados.
- Possibilidade de adicionar filtros e métricas customizadas.
- Modularidade: cada página é gerenciada por um módulo separado (`vendas`, `sellout`, `metas`).

---

## Tecnologias Utilizadas

- Python 3.10+
- Streamlit
- Pandas
- gspread
- oauth2client
- python-dotenv

---

## Pré-requisitos

1. Ter Python 3 instalado
2. Ter uma conta no Google com acesso à planilha
3. Ter o arquivo de credenciais do Google (Service Account JSON)
4. Ter um arquivo `.env` com a variável `GOOGLE_SHEETS_ID` apontando para o ID da planilha

---

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/dashboard-dani.git
cd dashboard-dani
```
