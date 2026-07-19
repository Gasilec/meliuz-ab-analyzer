"""
Lógica de decisão: dada a análise, qual variante escalar para 100% do tráfego.

Regra: a variante vencedora é a de maior MARGEM LÍQUIDA total (comissão - cashback)
no período do teste. Em seguida testamos se a vantagem sobre a 2ª colocada é
estatisticamente significativa. Guardrails (compradores/GMV) entram como contexto
para expor o trade-off de crescimento vs. margem.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import stats
from .metrics import daily_series


@dataclass
class Decision:
    winner: str
    runner_up: str
    recommendation: str          # "escalar" | "escalar_com_cautela" | "inconclusivo"
    headline: str
    test_result: stats.TestResult
    rationale: list[str]
    tradeoff: list[str]


def _fmt_brl(v: float) -> str:
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def fmt_p(p: float) -> str:
    """p-valor legível: 'p < 0.0001' quando arredondaria para zero."""
    p = float(p)
    return "< 0.0001" if 0 <= p < 0.0001 else f"{p:.4f}"


def _fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


def decide(df: pd.DataFrame, metrics: pd.DataFrame) -> Decision:
    ordered = metrics.index.tolist()  # já ordenado por margem_liquida desc
    winner = ordered[0]
    runner_up = ordered[1] if len(ordered) > 1 else winner

    daily = daily_series(df, "net_margin")
    res = stats.compare(daily[winner], daily[runner_up], winner, runner_up)
    pstr = fmt_p(res.p_value)
    p_phrase = f"p {pstr}" if pstr.startswith("<") else f"p = {pstr}"

    w = metrics.loc[winner]
    r = metrics.loc[runner_up]

    # ---- classificação da recomendação ----
    if winner == runner_up:
        recommendation = "inconclusivo"
        headline = f"Apenas uma variante ({winner}) — sem comparação A/B possível."
    elif res.significant:
        recommendation = "escalar"
        headline = (
            f"Escalar {winner} para 100% do tráfego. "
            f"Maior margem líquida ({_fmt_brl(w['margem_liquida'])}) e vantagem "
            f"estatisticamente significativa ({p_phrase})."
        )
    else:
        recommendation = "escalar_com_cautela"
        headline = (
            f"{winner} lidera em margem ({_fmt_brl(w['margem_liquida'])}), mas a "
            f"vantagem sobre {runner_up} NÃO é estatisticamente significativa "
            f"({p_phrase}). Recomenda-se manter/estender o teste antes de escalar."
        )

    # ---- racional (por que essa variante) ----
    rationale = [
        f"Métrica de decisão: margem líquida do Méliuz (comissão − cashback).",
        f"{winner}: margem {_fmt_brl(w['margem_liquida'])} | "
        f"cashback {_fmt_pct(w['cashback_pct_gmv'])} do GMV | "
        f"ticket {_fmt_brl(w['ticket_medio'])}.",
        f"2ª colocada {runner_up}: margem {_fmt_brl(r['margem_liquida'])} "
        f"(diferença de {_fmt_brl(w['margem_liquida'] - r['margem_liquida'])}).",
        f"Diferença de margem líquida média diária: {_fmt_brl(res.diff)}/dia "
        f"(IC 95%: {_fmt_brl(res.ci_low)} a {_fmt_brl(res.ci_high)}; "
        f"{p_phrase}; d de Cohen={res.cohens_d:.2f}).",
    ]

    # ---- trade-off (olho crítico: volume vs. margem) ----
    tradeoff = []
    top_buyers = metrics["compradores"].idxmax()
    top_gmv = metrics["gmv"].idxmax()
    if top_buyers != winner or top_gmv != winner:
        tradeoff.append(
            f"Atenção ao trade-off: a variante de maior VOLUME é "
            f"{top_buyers} ({int(metrics.loc[top_buyers, 'compradores']):,} compradores) "
            f"e a de maior GMV é {top_gmv} "
            f"({_fmt_brl(metrics.loc[top_gmv, 'gmv'])}), mas ambas entregam MENOS "
            f"margem líquida que {winner}."
        )
        tradeoff.append(
            "Ou seja: dar mais cashback aumenta conversão/GMV, porém corrói a margem — "
            "o efeito líquido favorece a variante recomendada."
        )
    else:
        tradeoff.append(
            f"{winner} vence simultaneamente em margem, volume de compradores e GMV — "
            f"decisão sem trade-off relevante."
        )

    return Decision(
        winner=winner, runner_up=runner_up, recommendation=recommendation,
        headline=headline, test_result=res, rationale=rationale, tradeoff=tradeoff,
    )
