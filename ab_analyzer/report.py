"""
Geração do relatório apresentável para um gestor (Markdown) e do resumo
consolidado (uma linha) que vai para a planilha de acompanhamento.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd

from .decision import Decision, _fmt_brl, _fmt_pct, fmt_p
from .loader import Dataset

SEV_EMOJI = {"info": "ℹ️", "aviso": "⚠️", "erro": "⛔"}


def _metrics_table(metrics: pd.DataFrame, winner: str) -> str:
    header = (
        "| Variante | Dias | Compradores | GMV | Comissão | Cashback | "
        "Margem líquida | Ticket | % Cashback | Margem/compr. |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    rows = []
    for v, row in metrics.iterrows():
        star = " 🏆" if v == winner else ""
        rows.append(
            f"| **{v}**{star} | {int(row['dias'])} | {int(row['compradores']):,} | "
            f"{_fmt_brl(row['gmv'])} | {_fmt_brl(row['comissao'])} | {_fmt_brl(row['cashback'])} | "
            f"**{_fmt_brl(row['margem_liquida'])}** | {_fmt_brl(row['ticket_medio'])} | "
            f"{_fmt_pct(row['cashback_pct_gmv'])} | {_fmt_brl(row['margem_por_comprador'])} |"
        )
    return header + "\n".join(rows)


def build_report(ds: Dataset, metrics: pd.DataFrame, decision: Decision,
                 outliers, test_name: str, description: str) -> str:
    d = decision
    rec_badge = {
        "escalar": "✅ ESCALAR",
        "escalar_com_cautela": "🟡 ESCALAR COM CAUTELA",
        "inconclusivo": "⚪ INCONCLUSIVO",
    }[d.recommendation]

    lines = []
    lines.append(f"# Relatório de Teste A/B — {test_name}")
    lines.append("")
    lines.append(f"> _Gerado automaticamente em {datetime.now():%d/%m/%Y %H:%M} "
                 f"pela solução de análise de testes A/B do time de Operações Integradas._")
    lines.append("")
    lines.append(f"**Parceiro:** {ds.partner}  |  **Período:** {ds.date_min} a {ds.date_max}  "
                 f"|  **Variantes:** {ds.n_variants}  |  **Observações:** {ds.n_rows} linhas")
    if description:
        lines.append(f"\n**Descrição:** {description}")
    lines.append("")

    # ---- Decisão (topo, para o gestor) ----
    lines.append("## 🎯 Decisão")
    lines.append("")
    lines.append(f"### {rec_badge} — {d.winner}")
    lines.append("")
    lines.append(d.headline)
    lines.append("")

    # ---- Métricas ----
    lines.append("## 📊 Métricas por variante")
    lines.append("")
    lines.append("> Métrica de decisão (OEC): **margem líquida = comissão − cashback**. "
                 "As demais são métricas-guardrail (contexto).")
    lines.append("")
    lines.append(_metrics_table(metrics, d.winner))
    lines.append("")

    # ---- Racional ----
    lines.append("## 🧠 Por que essa variante")
    lines.append("")
    for r in d.rationale:
        lines.append(f"- {r}")
    lines.append("")

    # ---- Significância ----
    t = d.test_result
    lines.append("## 📐 Significância estatística")
    lines.append("")
    lines.append(f"Comparação da **margem líquida diária** entre a vencedora ({t.variant_a}) "
                 f"e a 2ª colocada ({t.variant_b}), via teste de permutação (p-valor) e "
                 f"bootstrap (intervalo de confiança):")
    lines.append("")
    lines.append(f"- Diferença de média diária: **{_fmt_brl(t.diff)}/dia**")
    lines.append(f"- Intervalo de confiança 95%: {_fmt_brl(t.ci_low)} a {_fmt_brl(t.ci_high)}")
    lines.append(f"- p-valor (bicaudal): **{fmt_p(t.p_value)}** "
                 f"({'significativo' if t.significant else 'não significativo'} a 5%)")
    lines.append(f"- Tamanho de efeito (d de Cohen): {t.cohens_d:.2f}")
    lines.append(f"- Amostra: {t.n_a} vs {t.n_b} dias")
    lines.append("")

    # ---- Trade-off ----
    lines.append("## ⚖️ Trade-off (leitura crítica)")
    lines.append("")
    for tr in d.tradeoff:
        lines.append(f"- {tr}")
    lines.append("")

    # ---- Outliers e robustez ----
    lines.append("## 🚨 Outliers e robustez da decisão")
    lines.append("")
    if outliers.total_outliers == 0:
        lines.append("- Nenhum outlier detectado na margem líquida diária (método IQR).")
    else:
        lines.append(f"- **{outliers.total_outliers} dia(s) atípico(s)** detectado(s) na margem "
                     f"líquida diária (método IQR, 1,5×):")
        for v, info in outliers.per_variant.items():
            n = len(info["outliers"])
            if n:
                dates = ", ".join(o["date"] for o in info["outliers"])
                lines.append(f"  - {v}: {n} dia(s) — {dates}")
        if outliers.concurrent_dates:
            lines.append(f"- 🔁 **Datas atípicas concorrentes** (outliers em ≥2 variantes no mesmo "
                         f"dia): {', '.join(outliers.concurrent_dates)}.")
            lines.append("  - Interpretação: padrão típico de **evento/promoção real**, não de erro "
                         "isolado. Como o pico atinge todas as variantes ao mesmo tempo, o impacto "
                         "no comparativo A/B é baixo (mas infla totais e variância).")
    # teste de robustez
    verdict = "✅ **robusta**" if outliers.is_robust else "⚠️ **sensível**"
    lines.append(f"- **Teste de robustez** (winsorização 5%/95% dos extremos): após aparar os "
                 f"outliers, a variante vencedora é **{outliers.robust_winner}** → a decisão é "
                 f"{verdict} a outliers.")
    lines.append("")

    # ---- Qualidade de dados ----
    lines.append("## 🔎 Qualidade dos dados")
    lines.append("")
    if ds.issues:
        for iss in ds.issues:
            lines.append(f"- {SEV_EMOJI.get(iss.severity, '•')} {iss.message}")
    else:
        lines.append("- Nenhum problema detectado.")
    lines.append("")

    # ---- Metodologia ----
    lines.append("## 📎 Metodologia e ressalvas")
    lines.append("")
    lines.append("- **Decisão por margem líquida** porque escalar uma variante é uma decisão "
                 "de P&L: o Méliuz ganha comissão e paga cashback, então o valor que sobra é "
                 "`comissão − cashback`.")
    lines.append("- **Ressalva importante:** os dados trazem número de *compradores* "
                 "(conversões), mas não o total de *sessões/visitantes* por variante. Sem esse "
                 "denominador, não calculamos taxa de conversão pura; assumimos split de tráfego "
                 "equilibrado entre variantes (padrão de teste A/B). Recomenda-se validar o split.")
    lines.append("- Significância por reamostragem (permutação + bootstrap), sem suposição de "
                 "normalidade.")
    lines.append("")
    return "\n".join(lines)


def summary_row(ds: Dataset, metrics: pd.DataFrame, decision: Decision,
                outliers, test_name: str, description: str) -> dict:
    """Uma linha para a planilha de acompanhamento (1 teste = 1 linha)."""
    w = metrics.loc[decision.winner]
    t = decision.test_result
    p = float(t.p_value)
    # p-valor em pt-BR (vírgula decimal); valores minúsculos viram "< 0,0001"
    p_disp = "< 0,0001" if 0 <= p < 0.0001 else f"{p:.4f}".replace(".", ",")
    p_txt = f"p {p_disp}" if p_disp.startswith("<") else f"p = {p_disp}"
    resultado = (
        f"{decision.winner} lidera em margem líquida ({_fmt_brl(w['margem_liquida'])}); "
        f"{p_txt} ({'significativo' if t.significant else 'não significativo'})"
    )
    return {
        "data_analise": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nome_do_teste": test_name,
        "descricao": description or f"Teste A/B de cashback — {ds.partner}",
        "parceiro": ds.partner,
        "periodo": f"{ds.date_min} a {ds.date_max}",
        "n_variantes": ds.n_variants,
        "variante_vencedora": decision.winner,
        "resultado": resultado,
        "decisao": {
            "escalar": f"Escalar {decision.winner} para 100%",
            "escalar_com_cautela": f"Manter teste ({decision.winner} lidera, sem significância)",
            "inconclusivo": "Inconclusivo (variante única)",
        }[decision.recommendation],
        "margem_liquida_vencedora": _fmt_brl(w["margem_liquida"]),
        "p_valor": p_disp,
        "outliers_detectados": outliers.total_outliers,
        "decisao_robusta_a_outliers": "Sim" if outliers.is_robust else "Não",
    }
