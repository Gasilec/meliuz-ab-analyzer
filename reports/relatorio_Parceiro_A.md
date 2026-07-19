# Relatório de Teste A/B — Cashback Parceiro A

> _Gerado automaticamente em 19/07/2026 14:56 pela solução de análise de testes A/B do time de Operações Integradas._

**Parceiro:** Parceiro A  |  **Período:** 2011-01-01 a 2011-04-02  |  **Variantes:** 3  |  **Observações:** 276 linhas

**Descrição:** Teste de % de cashback, 3 variantes, jan-abr/2011

## 🎯 Decisão

### 🟡 ESCALAR COM CAUTELA — Grupo 1

Grupo 1 lidera em margem (R$ 404.711), mas a vantagem sobre Grupo 2 NÃO é estatisticamente significativa (p = 0.1424). Recomenda-se manter/estender o teste antes de escalar.

## 📊 Métricas por variante

> Métrica de decisão (OEC): **margem líquida = comissão − cashback**. As demais são métricas-guardrail (contexto).

| Variante | Dias | Compradores | GMV | Comissão | Cashback | Margem líquida | Ticket | % Cashback | Margem/compr. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Grupo 1** 🏆 | 92 | 9,633 | R$ 5.605.173 | R$ 638.135 | R$ 233.424 | **R$ 404.711** | R$ 582 | 4.2% | R$ 42 |
| **Grupo 2** | 92 | 10,814 | R$ 6.423.096 | R$ 728.178 | R$ 370.659 | **R$ 357.519** | R$ 594 | 5.8% | R$ 33 |
| **Grupo 3** | 92 | 11,410 | R$ 6.785.856 | R$ 767.887 | R$ 503.600 | **R$ 264.287** | R$ 595 | 7.4% | R$ 23 |

## 🧠 Por que essa variante

- Métrica de decisão: margem líquida do Méliuz (comissão − cashback).
- Grupo 1: margem R$ 404.711 | cashback 4.2% do GMV | ticket R$ 582.
- 2ª colocada Grupo 2: margem R$ 357.519 (diferença de R$ 47.192).
- Diferença de margem líquida média diária: R$ 513/dia (IC 95%: R$ -146 a R$ 1.187; p = 0.1424; d de Cohen=0.22).

## 📐 Significância estatística

Comparação da **margem líquida diária** entre a vencedora (Grupo 1) e a 2ª colocada (Grupo 2), via teste de permutação (p-valor) e bootstrap (intervalo de confiança):

- Diferença de média diária: **R$ 513/dia**
- Intervalo de confiança 95%: R$ -146 a R$ 1.187
- p-valor (bicaudal): **0.1424** (não significativo a 5%)
- Tamanho de efeito (d de Cohen): 0.22
- Amostra: 92 vs 92 dias

## ⚖️ Trade-off (leitura crítica)

- Atenção ao trade-off: a variante de maior VOLUME é Grupo 3 (11,410 compradores) e a de maior GMV é Grupo 3 (R$ 6.785.856), mas ambas entregam MENOS margem líquida que Grupo 1.
- Ou seja: dar mais cashback aumenta conversão/GMV, porém corrói a margem — o efeito líquido favorece a variante recomendada.

## 🚨 Outliers e robustez da decisão

- **17 dia(s) atípico(s)** detectado(s) na margem líquida diária (método IQR, 1,5×):
  - Grupo 1: 4 dia(s) — 2011-01-08, 2011-01-11, 2011-01-13, 2011-01-14
  - Grupo 2: 6 dia(s) — 2011-01-08, 2011-01-13, 2011-01-14, 2011-01-18, 2011-02-16, 2011-03-12
  - Grupo 3: 7 dia(s) — 2011-01-08, 2011-01-13, 2011-01-14, 2011-03-11, 2011-03-12, 2011-03-13, 2011-03-14
- 🔁 **Datas atípicas concorrentes** (outliers em ≥2 variantes no mesmo dia): 2011-01-08, 2011-01-13, 2011-01-14, 2011-03-12.
  - Interpretação: padrão típico de **evento/promoção real**, não de erro isolado. Como o pico atinge todas as variantes ao mesmo tempo, o impacto no comparativo A/B é baixo (mas infla totais e variância).
- **Teste de robustez** (winsorização 5%/95% dos extremos): após aparar os outliers, a variante vencedora é **Grupo 1** → a decisão é ✅ **robusta** a outliers.

## 🔎 Qualidade dos dados

- ℹ️ 276 linhas lidas, 276 válidas, 3 variantes detectadas.

## 📎 Metodologia e ressalvas

- **Decisão por margem líquida** porque escalar uma variante é uma decisão de P&L: o Méliuz ganha comissão e paga cashback, então o valor que sobra é `comissão − cashback`.
- **Ressalva importante:** os dados trazem número de *compradores* (conversões), mas não o total de *sessões/visitantes* por variante. Sem esse denominador, não calculamos taxa de conversão pura; assumimos split de tráfego equilibrado entre variantes (padrão de teste A/B). Recomenda-se validar o split.
- Significância por reamostragem (permutação + bootstrap), sem suposição de normalidade.
