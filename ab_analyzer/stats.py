"""
Testes estatísticos livres de distribuição (só numpy).

- Teste de permutação para o p-valor (a diferença observada é real ou sorte?).
- Bootstrap para o intervalo de confiança da diferença de médias diárias.
- Cohen's d como tamanho de efeito.

Usamos métodos de reamostragem porque não temos o denominador de tráfego
(sessões/visitantes) por variante — então evitamos suposições paramétricas
sobre taxa de conversão e trabalhamos com as observações diárias que temos.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

SEED = 42


@dataclass
class TestResult:
    variant_a: str
    variant_b: str
    mean_a: float
    mean_b: float
    diff: float           # média(a) - média(b), na métrica diária
    p_value: float        # bicaudal, via permutação
    ci_low: float         # IC 95% da diferença (bootstrap)
    ci_high: float
    cohens_d: float
    n_a: int
    n_b: int

    @property
    def significant(self) -> bool:
        return self.p_value < 0.05


def _cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
    if pooled <= 0:
        return 0.0
    return float((a.mean() - b.mean()) / np.sqrt(pooled))


def compare(series_a, series_b, name_a: str, name_b: str,
            n_perm: int = 10000, n_boot: int = 10000) -> TestResult:
    """Compara duas séries diárias (ex.: margem líquida diária de duas variantes)."""
    a = np.asarray(series_a, dtype=float)
    b = np.asarray(series_b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    rng = np.random.default_rng(SEED)

    obs_diff = a.mean() - b.mean()

    # ---- teste de permutação (p-valor bicaudal) ----
    pooled = np.concatenate([a, b])
    na = len(a)
    perm_diffs = np.empty(n_perm)
    for i in range(n_perm):
        rng.shuffle(pooled)
        perm_diffs[i] = pooled[:na].mean() - pooled[na:].mean()
    p_value = float((np.abs(perm_diffs) >= abs(obs_diff) - 1e-12).mean())

    # ---- bootstrap (IC 95% da diferença de médias) ----
    boot = np.empty(n_boot)
    for i in range(n_boot):
        ra = rng.choice(a, size=len(a), replace=True)
        rb = rng.choice(b, size=len(b), replace=True)
        boot[i] = ra.mean() - rb.mean()
    ci_low, ci_high = np.percentile(boot, [2.5, 97.5])

    return TestResult(
        variant_a=name_a, variant_b=name_b,
        mean_a=float(a.mean()), mean_b=float(b.mean()),
        diff=float(obs_diff), p_value=p_value,
        ci_low=float(ci_low), ci_high=float(ci_high),
        cohens_d=_cohens_d(a, b), n_a=len(a), n_b=len(b),
    )
