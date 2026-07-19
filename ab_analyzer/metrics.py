"""
Cálculo das métricas por variante do teste A/B.

Métrica de decisão (OEC): margem líquida do Méliuz = comissão - cashback.
Métricas-guardrail (contexto): compradores, GMV, ticket médio, % cashback.
"""
from __future__ import annotations

import pandas as pd


def variant_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega o dataset por variante e devolve um DataFrame (uma linha por variante)
    com totais e indicadores derivados. Não assume número fixo de variantes.
    """
    g = df.groupby("variant", observed=True)
    m = g.agg(
        dias=("date", "nunique"),
        compradores=("buyers", "sum"),
        comissao=("commission", "sum"),
        cashback=("cashback", "sum"),
        gmv=("gmv", "sum"),
    )

    # OEC e guardrails
    m["margem_liquida"] = m["comissao"] - m["cashback"]
    m["ticket_medio"] = m["gmv"] / m["compradores"].replace(0, pd.NA)
    m["cashback_pct_gmv"] = m["cashback"] / m["gmv"].replace(0, pd.NA) * 100
    m["comissao_pct_gmv"] = m["comissao"] / m["gmv"].replace(0, pd.NA) * 100
    m["margem_por_comprador"] = m["margem_liquida"] / m["compradores"].replace(0, pd.NA)
    m["margem_pct_gmv"] = m["margem_liquida"] / m["gmv"].replace(0, pd.NA) * 100

    return m.sort_values("margem_liquida", ascending=False)


def daily_series(df: pd.DataFrame, metric: str = "net_margin") -> dict[str, pd.Series]:
    """
    Devolve, por variante, a série diária de uma métrica — insumo para os
    testes estatísticos. 'net_margin' = comissão - cashback do dia.
    """
    work = df.copy()
    if metric == "net_margin":
        work["_val"] = work["commission"] - work["cashback"]
    elif metric == "buyers":
        work["_val"] = work["buyers"]
    elif metric == "gmv":
        work["_val"] = work["gmv"]
    else:
        raise ValueError(f"Métrica desconhecida: {metric}")

    out = {}
    for variant, chunk in work.groupby("variant", observed=True):
        out[variant] = chunk.groupby("date")["_val"].sum().sort_index()
    return out
