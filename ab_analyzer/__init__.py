"""
Solução reutilizável de análise de testes A/B de cashback — Méliuz / Operações Integradas.

Uso programático:
    from ab_analyzer import analyze_file
    result = analyze_file("datasets/dataset_01_parceiroA.csv", test_name="Parceiro A")
"""
from __future__ import annotations

from .pipeline import AnalysisResult, analyze_file

__all__ = ["analyze_file", "AnalysisResult"]
__version__ = "1.0.0"
