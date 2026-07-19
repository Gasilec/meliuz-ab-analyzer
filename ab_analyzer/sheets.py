"""
Registro do teste na planilha de acompanhamento.

Dois caminhos:
1. Google Sheets (ideal / diferencial) — via gspread + conta de serviço.
2. CSV local (mínimo garantido) — sempre gravado, mesmo sem credenciais.

Configuração do Google Sheets (ver README):
- Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS = caminho do JSON da conta de serviço.
- Variável de ambiente MELIUZ_SHEET_URL = URL da planilha (compartilhada com o e-mail da conta de serviço como Editor).
"""
from __future__ import annotations

import csv
import os

# Ordem fixa das colunas da planilha (1 teste = 1 linha).
COLUMNS = [
    "data_analise",
    "nome_do_teste",
    "descricao",
    "parceiro",
    "periodo",
    "n_variantes",
    "variante_vencedora",
    "resultado",
    "decisao",
    "margem_liquida_vencedora",
    "p_valor",
    "outliers_detectados",
    "decisao_robusta_a_outliers",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def append_csv(row: dict, csv_path: str) -> str:
    """Adiciona a linha ao CSV de acompanhamento (cria com cabeçalho se novo)."""
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    new_file = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in COLUMNS})
    return csv_path


def append_google_sheet(row: dict, sheet_url: str, credentials_path: str) -> str:
    """
    Adiciona a linha diretamente numa planilha do Google Sheets.
    Lança exceção se as libs/credenciais não estiverem disponíveis — quem chama
    decide o fallback.
    """
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1

    # garante cabeçalho (insere no topo se ausente ou diferente)
    # RAW: grava os valores exatamente como formatados, sem reinterpretação de
    # locale (evita, ex., "0,1424" virar 1424 numa planilha pt-BR).
    existing = ws.get_all_values()
    if not existing or existing[0] != COLUMNS:
        ws.insert_row(COLUMNS, index=1, value_input_option="RAW")
    ws.append_row([str(row.get(c, "")) for c in COLUMNS], value_input_option="RAW")
    return sheet_url


def register_test(row: dict, csv_path: str,
                  sheet_url: str | None = None,
                  credentials_path: str | None = None) -> list[str]:
    """
    Registra o teste. Sempre grava no CSV; tenta o Google Sheets se configurado.
    Devolve mensagens de status.
    """
    messages = []

    append_csv(row, csv_path)
    messages.append(f"CSV atualizado: {csv_path}")

    sheet_url = sheet_url or os.environ.get("MELIUZ_SHEET_URL")
    credentials_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if sheet_url and credentials_path:
        try:
            append_google_sheet(row, sheet_url, credentials_path)
            messages.append(f"Google Sheets atualizado: {sheet_url}")
        except Exception as e:  # noqa: BLE001 — fallback amigável
            messages.append(f"Google Sheets não atualizado ({type(e).__name__}: {e}). "
                            f"O CSV foi gravado normalmente.")
    else:
        messages.append("Google Sheets pulado (defina MELIUZ_SHEET_URL e "
                        "GOOGLE_APPLICATION_CREDENTIALS para ativar). CSV gravado.")
    return messages
