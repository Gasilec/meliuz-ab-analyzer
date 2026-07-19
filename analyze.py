#!/usr/bin/env python3
"""
CLI da solução de análise de testes A/B de cashback — Méliuz / Operações Integradas.

Uso:
    python analyze.py datasets/dataset_01_parceiroA.csv
    python analyze.py caminho/para/novo_teste.csv --nome "Teste X" --descricao "..."
    python analyze.py <arquivo> --sem-sheets      # só CSV, não tenta o Google Sheets

A MESMA solução processa qualquer dataset novo — basta trocar o arquivo.
"""
from __future__ import annotations

import argparse
import sys

from ab_analyzer import analyze_file


def main(argv=None) -> int:
    # Console do Windows costuma usar cp1252; garante UTF-8 na saída.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(
        description="Analisa um teste A/B de cashback e recomenda a variante a escalar.",
    )
    p.add_argument("dataset", help="Caminho do CSV do teste A/B.")
    p.add_argument("--nome", dest="test_name", default=None,
                   help="Nome do teste (default: inferido do parceiro).")
    p.add_argument("--descricao", dest="description", default="",
                   help="Descrição livre do teste.")
    p.add_argument("--saida", dest="output_dir", default="reports",
                   help="Pasta dos relatórios (default: reports).")
    p.add_argument("--csv", dest="csv_path", default="output/tracking_sheet.csv",
                   help="Caminho do CSV de acompanhamento.")
    p.add_argument("--sem-docx", dest="no_docx", action="store_true",
                   help="Não gera o relatório em Word (.docx).")
    p.add_argument("--sem-sheets", dest="no_sheets", action="store_true",
                   help="Não tenta escrever no Google Sheets (grava só o CSV).")
    p.add_argument("--sheet-url", dest="sheet_url", default=None,
                   help="URL da planilha do Google Sheets (ou use MELIUZ_SHEET_URL).")
    p.add_argument("--credenciais", dest="credentials_path", default=None,
                   help="JSON da conta de serviço (ou use GOOGLE_APPLICATION_CREDENTIALS).")
    args = p.parse_args(argv)

    try:
        result = analyze_file(
            args.dataset,
            test_name=args.test_name,
            description=args.description,
            output_dir=args.output_dir,
            csv_path=args.csv_path,
            write_docx=not args.no_docx,
            register=True,
            sheet_url=None if args.no_sheets else args.sheet_url,
            credentials_path=None if args.no_sheets else args.credentials_path,
        )
    except FileNotFoundError:
        print(f"ERRO: arquivo não encontrado: {args.dataset}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERRO de dados: {e}", file=sys.stderr)
        return 1

    d = result.decision
    print("=" * 70)
    print(f"  {result.summary['nome_do_teste']}")
    print("=" * 70)
    print(f"Parceiro: {result.dataset.partner} | "
          f"Período: {result.dataset.date_min} a {result.dataset.date_max} | "
          f"Variantes: {result.dataset.n_variants}")
    print()
    print(f"DECISÃO: {d.headline}")
    print()
    print("Racional:")
    for r in d.rationale:
        print(f"  - {r}")
    print()
    if result.report_path:
        print(f"Relatório (Markdown) salvo em: {result.report_path}")
    if result.docx_path:
        print(f"Relatório (Word) salvo em: {result.docx_path}")
    if result.register_messages:
        for m in result.register_messages:
            print(f"  · {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
