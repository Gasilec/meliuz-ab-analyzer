"""
Pipeline de ponta a ponta: carrega -> valida -> calcula -> decide -> relata -> registra.

É o coração reutilizável da solução. A mesma função processa qualquer um dos
datasets sem alteração de código — basta apontar o arquivo.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd

from . import report as report_mod
from . import report_docx as docx_mod
from . import sheets as sheets_mod
from .decision import Decision, decide
from .loader import Dataset, load_dataset
from .metrics import variant_metrics
from .outliers import OutlierReport, analyze_outliers


@dataclass
class AnalysisResult:
    dataset: Dataset
    metrics: pd.DataFrame
    decision: Decision
    report_markdown: str
    summary: dict
    report_path: str | None = None
    docx_path: str | None = None
    register_messages: list[str] | None = None


def _infer_test_name(path: str, ds: Dataset) -> str:
    return f"Teste A/B Cashback — {ds.partner}"


def analyze_file(
    path: str,
    test_name: str | None = None,
    description: str = "",
    output_dir: str = "reports",
    csv_path: str = "output/tracking_sheet.csv",
    write_report: bool = True,
    write_docx: bool = True,
    register: bool = True,
    sheet_url: str | None = None,
    credentials_path: str | None = None,
) -> AnalysisResult:
    """Executa a análise completa de um dataset de teste A/B."""
    ds = load_dataset(path)
    test_name = test_name or _infer_test_name(path, ds)

    metrics = variant_metrics(ds.df)
    decision = decide(ds.df, metrics)
    outlier_report = analyze_outliers(ds.df, decision.winner)
    md = report_mod.build_report(ds, metrics, decision, outlier_report, test_name, description)
    summary = report_mod.summary_row(ds, metrics, decision, outlier_report, test_name, description)

    safe = "".join(c if c.isalnum() else "_" for c in ds.partner).strip("_")

    report_path = None
    if write_report:
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, f"relatorio_{safe}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md)

    docx_path = None
    if write_docx:
        os.makedirs(output_dir, exist_ok=True)
        docx_path = os.path.join(output_dir, f"relatorio_{safe}.docx")
        docx_mod.build_docx(ds, metrics, decision, outlier_report,
                            test_name, description, docx_path)

    register_messages = None
    if register:
        register_messages = sheets_mod.register_test(
            summary, csv_path=csv_path,
            sheet_url=sheet_url, credentials_path=credentials_path,
        )

    return AnalysisResult(
        dataset=ds, metrics=metrics, decision=decision,
        report_markdown=md, summary=summary,
        report_path=report_path, docx_path=docx_path,
        register_messages=register_messages,
    )
