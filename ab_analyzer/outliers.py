"""
Detecção de outliers e teste de robustez da decisão.

O enunciado pede identificar problemas nos dados que "podem atrapalhar as
métricas". Aqui tratamos os outliers de forma crítica:

1. Detectamos dias atípicos por variante (método IQR sobre a margem líquida diária).
2. Verificamos se os outliers são CONCORRENTES entre variantes (mesma data em
   várias variantes) — sinal de evento/promoção real, e não de erro isolado. Como
   atingem todas as variantes ao mesmo tempo, tendem a NÃO enviesar o A/B.
3. Testamos a ROBUSTEZ da decisão: recalculamos o ranking com os extremos
   "aparados" (winsorização a 5%/95%) e conferimos se a variante vencedora muda.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .metrics import daily_series


@dataclass
class OutlierReport:
    per_variant: dict          # variant -> {"n_days", "bounds", "outliers":[{date,value,side}]}
    concurrent_dates: list      # datas que são outliers em >= 2 variantes
    total_outliers: int
    robust_winner: str          # vencedora após winsorização
    winsor_totals: dict         # variant -> margem líquida winsorizada
    is_robust: bool = field(default=False)  # a vencedora se mantém?


def _iqr_bounds(x: np.ndarray, k: float = 1.5) -> tuple[float, float]:
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def analyze_outliers(df, original_winner: str, k: float = 1.5) -> OutlierReport:
    daily = daily_series(df, "net_margin")

    per_variant: dict = {}
    date_hits: dict = {}
    total = 0
    for variant, s in daily.items():
        x = s.values.astype(float)
        lo, hi = _iqr_bounds(x, k)
        outs = []
        for date, val in s.items():
            if val > hi or val < lo:
                d = str(getattr(date, "date", lambda: date)())
                outs.append({"date": d, "value": float(val),
                             "side": "alto" if val > hi else "baixo"})
                date_hits[d] = date_hits.get(d, 0) + 1
                total += 1
        per_variant[variant] = {"n_days": int(len(x)), "bounds": (float(lo), float(hi)),
                                "outliers": outs}

    concurrent = sorted([d for d, n in date_hits.items() if n >= 2])

    # ---- robustez: ranking com extremos aparados (winsorização 5%/95%) ----
    winsor_totals = {}
    for variant, s in daily.items():
        x = s.values.astype(float)
        p5, p95 = np.percentile(x, [5, 95])
        winsor_totals[variant] = float(np.clip(x, p5, p95).sum())
    robust_winner = max(winsor_totals, key=winsor_totals.get)

    return OutlierReport(
        per_variant=per_variant,
        concurrent_dates=concurrent,
        total_outliers=total,
        robust_winner=robust_winner,
        winsor_totals=winsor_totals,
        is_robust=(robust_winner == original_winner),
    )
