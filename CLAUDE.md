# Instruções para IA — Analisador de Testes A/B de Cashback (Méliuz)

> Este arquivo é o **ponto de acionamento por linguagem natural**. Ferramentas de IA
> (Claude Code, Cursor, GPT personalizado, Gemini) leem estas instruções e sabem
> exatamente o que fazer quando alguém do time pedir uma análise em português.

## O que esta solução faz

Recebe o CSV de **um teste A/B de cashback** e responde à pergunta central:
**"qual variante devemos escalar para 100% do tráfego?"** — com relatório para
gestor e registro na planilha de acompanhamento.

## Como agir quando o usuário pedir uma análise

Quando o usuário disser algo como:
- "analise o teste do parceiro X, o arquivo é `caminho/arquivo.csv`"
- "roda a análise A/B desse dataset novo"
- "qual variante de cashback devo escalar nesse teste?"

Faça:

1. Identifique o **caminho do arquivo** que o usuário indicou.
2. Rode no terminal:
   ```bash
   python analyze.py "CAMINHO_DO_ARQUIVO"
   ```
   - Adicione `--nome "..."` e `--descricao "..."` se o usuário fornecer.
   - Adicione `--sem-sheets` se o usuário só quiser o CSV.
3. Leia o relatório gerado em `reports/relatorio_<Parceiro>.md`.
4. **Resuma para o usuário em português**: a decisão (qual variante escalar),
   a margem líquida da vencedora, se a diferença é estatisticamente significativa,
   e o trade-off (volume vs. margem), se houver.
5. Confirme que o teste foi registrado na planilha de acompanhamento
   (Google Sheets, se configurado, e sempre no CSV `output/tracking_sheet.csv`).

## Regras de negócio (não invente, siga)

- **Métrica de decisão (OEC):** margem líquida do Méliuz = `comissão − cashback`.
  Escalar é decisão de P&L: vence a variante que deixa mais dinheiro no caixa.
- **Guardrails (contexto, não decidem sozinhos):** compradores, GMV, ticket médio,
  % de cashback sobre GMV.
- **Significância:** só recomende "escalar" com folga se a diferença de margem
  diária for estatisticamente significativa (p < 0,05). Caso contrário, recomende
  **manter/estender o teste**.
- **Robustez:** a solução detecta N variantes automaticamente (2, 3, …), sinaliza
  problemas de dados (cashback = comissão, valores negativos, datas inválidas etc.)
  e detecta **outliers** (dias atípicos), testando se a decisão se mantém quando os
  extremos são aparados. Sempre mencione ao usuário os alertas de qualidade, os
  outliers encontrados e se a decisão é robusta a eles.
- **Ressalva:** os dados têm compradores (conversões) mas não sessões/visitantes;
  não há taxa de conversão pura. Assume-se split de tráfego equilibrado.

## Estrutura do código (para quem for evoluir)

- `ab_analyzer/loader.py` — leitura + parsing de moeda BR + validações.
- `ab_analyzer/metrics.py` — agregações por variante (margem líquida + guardrails).
- `ab_analyzer/stats.py` — significância (permutação + bootstrap, só numpy).
- `ab_analyzer/outliers.py` — detecção de outliers + teste de robustez da decisão.
- `ab_analyzer/decision.py` — regra de decisão da variante a escalar.
- `ab_analyzer/report.py` — relatório Markdown + linha da planilha.
- `ab_analyzer/sheets.py` — Google Sheets + fallback CSV.
- `ab_analyzer/pipeline.py` — orquestra tudo (`analyze_file`).
- `analyze.py` — CLI.

## Como adicionar um novo teste (checklist)

1. Coloque o CSV (mesmo schema) em qualquer pasta.
2. `python analyze.py "caminho/novo.csv" --nome "..." --descricao "..."`
3. Relatório em `reports/`, linha nova na planilha. Pronto — **sem mudar código**.
