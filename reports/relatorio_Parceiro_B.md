# Relatório de Teste A/B — Cashback Parceiro B

> _Gerado automaticamente em 19/07/2026 14:56 pela solução de análise de testes A/B do time de Operações Integradas._

**Parceiro:** Parceiro B  |  **Período:** 2011-05-01 a 2011-06-30  |  **Variantes:** 3  |  **Observações:** 183 linhas

**Descrição:** Teste de % de cashback, 3 variantes, mai-jun/2011

## 🎯 Decisão

### ✅ ESCALAR — Grupo 1

Escalar Grupo 1 para 100% do tráfego. Maior margem líquida (R$ 286.570) e vantagem estatisticamente significativa (p < 0.0001).

## 📊 Métricas por variante

> Métrica de decisão (OEC): **margem líquida = comissão − cashback**. As demais são métricas-guardrail (contexto).

| Variante | Dias | Compradores | GMV | Comissão | Cashback | Margem líquida | Ticket | % Cashback | Margem/compr. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Grupo 1** 🏆 | 61 | 7,990 | R$ 4.093.818 | R$ 450.321 | R$ 163.751 | **R$ 286.570** | R$ 512 | 4.0% | R$ 36 |
| **Grupo 2** | 61 | 5,452 | R$ 2.863.019 | R$ 314.935 | R$ 171.778 | **R$ 143.157** | R$ 525 | 6.0% | R$ 26 |
| **Grupo 3** | 61 | 5,029 | R$ 2.629.963 | R$ 289.290 | R$ 236.697 | **R$ 52.593** | R$ 523 | 9.0% | R$ 10 |

## 🧠 Por que essa variante

- Métrica de decisão: margem líquida do Méliuz (comissão − cashback).
- Grupo 1: margem R$ 286.570 | cashback 4.0% do GMV | ticket R$ 512.
- 2ª colocada Grupo 2: margem R$ 143.157 (diferença de R$ 143.413).
- Diferença de margem líquida média diária: R$ 2.351/dia (IC 95%: R$ 1.826 a R$ 2.921; p < 0.0001; d de Cohen=1.52).

## 📐 Significância estatística

Comparação da **margem líquida diária** entre a vencedora (Grupo 1) e a 2ª colocada (Grupo 2), via teste de permutação (p-valor) e bootstrap (intervalo de confiança):

- Diferença de média diária: **R$ 2.351/dia**
- Intervalo de confiança 95%: R$ 1.826 a R$ 2.921
- p-valor (bicaudal): **< 0.0001** (significativo a 5%)
- Tamanho de efeito (d de Cohen): 1.52
- Amostra: 61 vs 61 dias

## ⚖️ Trade-off (leitura crítica)

- Grupo 1 vence simultaneamente em margem, volume de compradores e GMV — decisão sem trade-off relevante.

## 🚨 Outliers e robustez da decisão

- **6 dia(s) atípico(s)** detectado(s) na margem líquida diária (método IQR, 1,5×):
  - Grupo 1: 2 dia(s) — 2011-05-15, 2011-05-22
  - Grupo 2: 2 dia(s) — 2011-05-15, 2011-05-22
  - Grupo 3: 2 dia(s) — 2011-05-15, 2011-05-22
- 🔁 **Datas atípicas concorrentes** (outliers em ≥2 variantes no mesmo dia): 2011-05-15, 2011-05-22.
  - Interpretação: padrão típico de **evento/promoção real**, não de erro isolado. Como o pico atinge todas as variantes ao mesmo tempo, o impacto no comparativo A/B é baixo (mas infla totais e variância).
- **Teste de robustez** (winsorização 5%/95% dos extremos): após aparar os outliers, a variante vencedora é **Grupo 1** → a decisão é ✅ **robusta** a outliers.

## 🔎 Qualidade dos dados

- ℹ️ 183 linhas lidas, 183 válidas, 3 variantes detectadas.

## 📎 Metodologia e ressalvas

- **Decisão por margem líquida** porque escalar uma variante é uma decisão de P&L: o Méliuz ganha comissão e paga cashback, então o valor que sobra é `comissão − cashback`.
- **Ressalva importante:** os dados trazem número de *compradores* (conversões), mas não o total de *sessões/visitantes* por variante. Sem esse denominador, não calculamos taxa de conversão pura; assumimos split de tráfego equilibrado entre variantes (padrão de teste A/B). Recomenda-se validar o split.
- Significância por reamostragem (permutação + bootstrap), sem suposição de normalidade.
