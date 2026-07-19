# Relatório de Teste A/B — Cashback Parceiro C

> _Gerado automaticamente em 19/07/2026 14:57 pela solução de análise de testes A/B do time de Operações Integradas._

**Parceiro:** Parceiro C  |  **Período:** 2011-07-01 a 2011-08-14  |  **Variantes:** 2  |  **Observações:** 90 linhas

**Descrição:** Teste de % de cashback, 2 variantes, jul-ago/2011

## 🎯 Decisão

### ✅ ESCALAR — Grupo 1

Escalar Grupo 1 para 100% do tráfego. Maior margem líquida (R$ 34.769) e vantagem estatisticamente significativa (p < 0.0001).

## 📊 Métricas por variante

> Métrica de decisão (OEC): **margem líquida = comissão − cashback**. As demais são métricas-guardrail (contexto).

| Variante | Dias | Compradores | GMV | Comissão | Cashback | Margem líquida | Ticket | % Cashback | Margem/compr. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Grupo 1** 🏆 | 45 | 4,549 | R$ 1.738.460 | R$ 121.693 | R$ 86.924 | **R$ 34.769** | R$ 382 | 5.0% | R$ 8 |
| **Grupo 2** | 45 | 4,522 | R$ 1.685.235 | R$ 117.967 | R$ 117.967 | **R$ 0** | R$ 373 | 7.0% | R$ 0 |

## 🧠 Por que essa variante

- Métrica de decisão: margem líquida do Méliuz (comissão − cashback).
- Grupo 1: margem R$ 34.769 | cashback 5.0% do GMV | ticket R$ 382.
- 2ª colocada Grupo 2: margem R$ 0 (diferença de R$ 34.769).
- Diferença de margem líquida média diária: R$ 773/dia (IC 95%: R$ 716 a R$ 831; p < 0.0001; d de Cohen=5.47).

## 📐 Significância estatística

Comparação da **margem líquida diária** entre a vencedora (Grupo 1) e a 2ª colocada (Grupo 2), via teste de permutação (p-valor) e bootstrap (intervalo de confiança):

- Diferença de média diária: **R$ 773/dia**
- Intervalo de confiança 95%: R$ 716 a R$ 831
- p-valor (bicaudal): **< 0.0001** (significativo a 5%)
- Tamanho de efeito (d de Cohen): 5.47
- Amostra: 45 vs 45 dias

## ⚖️ Trade-off (leitura crítica)

- Grupo 1 vence simultaneamente em margem, volume de compradores e GMV — decisão sem trade-off relevante.

## 🚨 Outliers e robustez da decisão

- Nenhum outlier detectado na margem líquida diária (método IQR).
- **Teste de robustez** (winsorização 5%/95% dos extremos): após aparar os outliers, a variante vencedora é **Grupo 1** → a decisão é ✅ **robusta** a outliers.

## 🔎 Qualidade dos dados

- ℹ️ 90 linhas lidas, 90 válidas, 2 variantes detectadas.
- ⚠️ Anomalia: na variante 'Grupo 2', o cashback é EXATAMENTE igual à comissão em todas as 45 linhas — margem líquida zero. Pode ser erro de dados ou variante que repassa 100% da comissão.

## 📎 Metodologia e ressalvas

- **Decisão por margem líquida** porque escalar uma variante é uma decisão de P&L: o Méliuz ganha comissão e paga cashback, então o valor que sobra é `comissão − cashback`.
- **Ressalva importante:** os dados trazem número de *compradores* (conversões), mas não o total de *sessões/visitantes* por variante. Sem esse denominador, não calculamos taxa de conversão pura; assumimos split de tráfego equilibrado entre variantes (padrão de teste A/B). Recomenda-se validar o split.
- Significância por reamostragem (permutação + bootstrap), sem suposição de normalidade.
