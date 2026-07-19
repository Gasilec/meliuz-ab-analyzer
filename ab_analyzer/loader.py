"""
Carregamento e validação robusta de datasets de teste A/B de cashback.

Este módulo é a primeira linha de defesa contra "dados ruins": ele normaliza
nomes de colunas, faz parsing tolerante de valores monetários em formato
brasileiro (R$ 10.273 -> 10273.0) e coleta uma lista de achados de qualidade
de dados que alimenta o relatório final.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd

# Nomes canônicos usados internamente pela solução.
CANONICAL = {
    "data": "date",
    "grupos de usuarios": "variant",
    "parceiro": "partner",
    "compradores": "buyers",
    "comissao": "commission",
    "cashback": "cashback",
    "vendas totais": "gmv",
}
MONEY_COLS = ["commission", "cashback", "gmv"]


def _normalize(text: str) -> str:
    """Minúsculas, sem acentos e sem espaços duplicados — para casar colunas."""
    text = str(text).strip().lower()
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", text)


def parse_money(value) -> float:
    """
    Converte um valor monetário em formato brasileiro para float.

    Aceita: 'R$ 10.273', 'R$ 1.234,56', '998', 'R$ -50', 12345, None, ''.
    Regra: quando há vírgula, ela é o separador decimal e os pontos são milhar;
    sem vírgula, os pontos são separador de milhar (padrão dos datasets).
    Retorna NaN para valores vazios/inválidos em vez de quebrar.
    """
    if value is None:
        return float("nan")
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "" or s.lower() in {"nan", "none", "-", "n/a", "na"}:
        return float("nan")
    s = re.sub(r"(?i)r\$", "", s).strip()
    neg = s.startswith("-")
    s = re.sub(r"[^0-9.,]", "", s)
    if s == "":
        return float("nan")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    try:
        v = float(s)
    except ValueError:
        return float("nan")
    return -v if neg else v


def parse_int(value) -> float:
    """Converte contagem de compradores para inteiro de forma tolerante."""
    if value is None:
        return float("nan")
    if isinstance(value, (int, float)):
        return float(value)
    s = re.sub(r"[^0-9-]", "", str(value).strip())
    if s in {"", "-"}:
        return float("nan")
    try:
        return float(int(s))
    except ValueError:
        return float("nan")


@dataclass
class Issue:
    """Um achado de qualidade de dados."""
    severity: str  # "info" | "aviso" | "erro"
    message: str


@dataclass
class Dataset:
    """Resultado do carregamento: dados limpos + metadados + achados."""
    df: pd.DataFrame
    partner: str
    variants: list[str]
    date_min: str
    date_max: str
    n_rows: int
    issues: list[Issue] = field(default_factory=list)

    @property
    def n_variants(self) -> int:
        return len(self.variants)


def load_dataset(path: str) -> Dataset:
    """Lê um CSV de teste A/B, limpa, valida e devolve um objeto Dataset."""
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    issues: list[Issue] = []

    # ---- mapeia colunas para nomes canônicos (tolerante a acento/caixa) ----
    rename = {}
    norm_to_orig = {_normalize(c): c for c in raw.columns}
    for norm, canonical in CANONICAL.items():
        if norm in norm_to_orig:
            rename[norm_to_orig[norm]] = canonical
    df = raw.rename(columns=rename)

    missing = [c for c in CANONICAL.values() if c not in df.columns]
    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes no arquivo: {missing}. "
            f"Colunas encontradas: {list(raw.columns)}"
        )

    # ---- parsing dos tipos ----
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    df["variant"] = df["variant"].astype(str).str.strip()
    df["partner"] = df["partner"].astype(str).str.strip()
    df["buyers"] = df["buyers"].map(parse_int)
    for col in MONEY_COLS:
        df[col] = df[col].map(parse_money)

    # ---- validações (não interrompem, apenas registram) ----
    n_before = len(df)

    bad_dates = int(df["date"].isna().sum())
    if bad_dates:
        issues.append(Issue("aviso", f"{bad_dates} linha(s) com data inválida foram descartadas."))
        df = df[df["date"].notna()]

    for col in ["buyers"] + MONEY_COLS:
        n_nan = int(df[col].isna().sum())
        if n_nan:
            issues.append(Issue("aviso", f"{n_nan} valor(es) não numéricos na coluna '{col}'."))

    dup = df.duplicated(subset=["date", "variant"]).sum()
    if dup:
        issues.append(Issue("aviso", f"{int(dup)} linha(s) duplicadas por (data, variante)."))

    for col in ["buyers"] + MONEY_COLS:
        n_neg = int((df[col] < 0).sum())
        if n_neg:
            issues.append(Issue("aviso", f"{n_neg} valor(es) negativos em '{col}'."))

    n_zero_buyers = int((df["buyers"] == 0).sum())
    if n_zero_buyers:
        issues.append(Issue("info", f"{n_zero_buyers} dia(s) com zero compradores."))

    # anomalia observada no Parceiro C / Grupo 2: cashback == comissão
    eq_mask = (df["cashback"] == df["commission"]) & (df["commission"] > 0)
    per_variant_eq = df[eq_mask].groupby("variant").size()
    per_variant_total = df.groupby("variant").size()
    for variant, n_eq in per_variant_eq.items():
        if n_eq == per_variant_total[variant]:
            issues.append(Issue(
                "aviso",
                f"Anomalia: na variante '{variant}', o cashback é EXATAMENTE igual "
                f"à comissão em todas as {n_eq} linhas — margem líquida zero. "
                f"Pode ser erro de dados ou variante que repassa 100% da comissão.",
            ))

    # cashback maior que comissão (Méliuz pagaria mais do que recebe)
    over = int((df["cashback"] > df["commission"]).sum())
    if over:
        issues.append(Issue("aviso", f"{over} dia(s) com cashback > comissão (margem negativa no dia)."))

    # consistência de nº de dias por variante
    days_per_variant = df.groupby("variant")["date"].nunique()
    if days_per_variant.nunique() > 1:
        issues.append(Issue(
            "aviso",
            f"Variantes têm nº de dias diferentes: {days_per_variant.to_dict()} — "
            f"a comparação de totais pode ficar enviesada.",
        ))

    partner = df["partner"].mode().iloc[0] if not df.empty else "?"
    if df["partner"].nunique() > 1:
        issues.append(Issue("aviso", f"Mais de um parceiro no mesmo arquivo: {sorted(df['partner'].unique())}."))

    variants = sorted(df["variant"].unique())
    issues.insert(0, Issue(
        "info",
        f"{n_before} linhas lidas, {len(df)} válidas, {len(variants)} variantes detectadas.",
    ))

    return Dataset(
        df=df.reset_index(drop=True),
        partner=partner,
        variants=variants,
        date_min=str(df["date"].min().date()) if not df.empty else "?",
        date_max=str(df["date"].max().date()) if not df.empty else "?",
        n_rows=len(df),
        issues=issues,
    )
