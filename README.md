# Analisador de Testes A/B de Cashback — Méliuz · Operações Integradas

Solução **reutilizável e parametrizada** que recebe o dataset de um teste A/B de
cashback e responde à pergunta central:

> **"Dado esse teste A/B, qual variante de cashback devemos escalar para 100% do tráfego?"**

A mesma solução processa **qualquer** teste novo **sem alterar código** — basta
apontar o arquivo. Para cada teste, entrega um **relatório apresentável para gestor**
e registra um **resumo consolidado** em uma planilha de acompanhamento (Google Sheets
ou CSV).

---

## 📁 O que tem neste repositório

| Parte | Onde | O que é |
|---|---|---|
| 📄 **Instruções** (acionamento por IA) | [`CLAUDE.md`](CLAUDE.md) | Instruções em linguagem natural — arquivo-padrão que Claude Code / Cursor leem automaticamente |
| 🐍 **Script principal** | [`analyze.py`](analyze.py) | Ponto de entrada (linha de comando) |
| 🧩 **Módulos da solução** | [`ab_analyzer/`](ab_analyzer/) | `loader`, `metrics`, `stats`, `outliers`, `decision`, `report`, `report_docx`, `sheets`, `pipeline` |
| 📊 **Relatório — Parceiro A** | [Markdown](reports/relatorio_Parceiro_A.md) · [Word](reports/relatorio_Parceiro_A.docx) | 🟡 Escalar com cautela |
| 📊 **Relatório — Parceiro B** | [Markdown](reports/relatorio_Parceiro_B.md) · [Word](reports/relatorio_Parceiro_B.docx) | ✅ Escalar Grupo 1 |
| 📊 **Relatório — Parceiro C** | [Markdown](reports/relatorio_Parceiro_C.md) · [Word](reports/relatorio_Parceiro_C.docx) | ✅ Escalar Grupo 1 |
| 🗒️ **Planilha (espelho local)** | [`output/tracking_sheet.csv`](output/tracking_sheet.csv) | 1 linha por teste |

> 💡 No GitHub, os relatórios em **`.md` abrem formatados direto no navegador** (clique e leia).
> Os **`.docx`** são para baixar e abrir no Word.

---

## 🧭 Como a decisão é tomada

- **Métrica de decisão (OEC):** **margem líquida do Méliuz = `comissão − cashback`.**
  Escalar uma variante é uma decisão de P&L: o Méliuz *ganha* comissão e *paga*
  cashback, então o que fica no caixa é a diferença. A variante vencedora é a de
  maior margem líquida no período.
- **Métricas-guardrail (contexto):** compradores, GMV, ticket médio, % de cashback.
  Elas expõem o trade-off (mais cashback → mais volume, porém menos margem) mas não
  decidem sozinhas.
- **Significância estatística:** só recomendamos "escalar" com folga quando a
  vantagem da vencedora sobre a 2ª colocada é estatisticamente significativa
  (p < 0,05), via **teste de permutação** (p-valor) e **bootstrap** (intervalo de
  confiança) sobre a margem líquida diária. Caso contrário, a recomendação é
  **manter/estender o teste**.

> **Ressalva analítica (olho crítico):** os dados trazem *compradores* (conversões),
> mas não *sessões/visitantes* por variante. Sem esse denominador não há taxa de
> conversão pura; assumimos split de tráfego equilibrado entre variantes (padrão de
> teste A/B) e recomendamos validar o split.

---

## 📊 Resultados dos 3 datasets fornecidos

| Teste | Variantes | Decisão | Vencedora | Margem líquida | Significância |
|---|---|---|---|---|---|
| **Parceiro A** (jan–abr) | 3 | 🟡 Escalar com cautela | Grupo 1 | R$ 404.711 | p=0,14 — **não** significativo vs. Grupo 2 |
| **Parceiro B** (mai–jun) | 3 | ✅ Escalar | Grupo 1 | R$ 286.570 | p<0,001 (d=1,52) |
| **Parceiro C** (jul–ago) | 2 | ✅ Escalar | Grupo 1 | R$ 34.769 | p<0,001 (d=5,47) |

Destaques de leitura crítica:
- **Parceiro A:** o Grupo 3 traz mais compradores (11.410) e maior GMV, mas dá menos
  margem — e a liderança do Grupo 1 sobre o Grupo 2 **não** passa no teste de
  significância. A solução recomenda **não escalar ainda**.
- **Parceiro C:** o Grupo 2 tem **margem zero** (cashback = 100% da comissão em todas
  as linhas) — anomalia sinalizada automaticamente pela validação de dados.

Relatórios completos em [`reports/`](reports/).

---

## 🚀 Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Analisar um teste
```bash
python analyze.py "datasets/dataset_01_parceiroA.csv" --nome "Cashback Parceiro A" --descricao "..."
```
Opções:
- `--nome` / `--descricao` — metadados do teste.
- `--sem-sheets` — grava só o CSV (não tenta o Google Sheets).
- `--sheet-url` / `--credenciais` — sobrescrevem as variáveis de ambiente.

### 3. Acionar por linguagem natural (Claude Code / Cursor / GPT / Gemini)
O arquivo [`CLAUDE.md`](CLAUDE.md) instrui a ferramenta de IA. Basta abrir a pasta e
pedir, por exemplo: *"analise o teste A/B desse arquivo `datasets/dataset_02_parceiroB.csv`"* —
a IA roda o comando, lê o relatório e resume a decisão em português.

---

## 🔗 Configurar a escrita direta no Google Sheets (diferencial)

O CSV (`output/tracking_sheet.csv`) é sempre gravado. Para escrever **direto no
Google Sheets**:

1. No [Google Cloud Console](https://console.cloud.google.com/), crie um projeto e
   ative **Google Sheets API** e **Google Drive API**.
2. Crie uma **conta de serviço** e gere uma **chave JSON**. Salve como
   `credentials.json` (já está no `.gitignore` — **nunca** versione).
3. Crie uma planilha no Google Sheets e **compartilhe com o e-mail da conta de
   serviço** (algo como `...@...iam.gserviceaccount.com`) como **Editor**.
4. Deixe a planilha com **acesso de leitura público** (link) para a entrega.
5. Defina as variáveis de ambiente e rode:
   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\caminho\credentials.json"
   $env:MELIUZ_SHEET_URL = "https://docs.google.com/spreadsheets/d/SEU_ID/edit"
   python analyze.py "datasets/dataset_01_parceiroA.csv"
   ```
A cada análise, uma nova linha é adicionada (1 teste = 1 linha).

---

## 🗂️ Arquitetura

```
meliuz-ab-analyzer/
├── analyze.py                 # CLI (entrada parametrizada)
├── CLAUDE.md                  # acionamento por linguagem natural (IA)
├── README.md
├── requirements.txt
├── ab_analyzer/
│   ├── loader.py              # leitura + parsing de moeda BR + validações
│   ├── metrics.py             # agregações por variante (margem líquida + guardrails)
│   ├── stats.py               # significância (permutação + bootstrap, só numpy)
│   ├── outliers.py            # detecção de outliers + teste de robustez da decisão
│   ├── decision.py            # regra de decisão da variante a escalar
│   ├── report.py              # relatório Markdown + linha da planilha
│   ├── sheets.py              # Google Sheets + fallback CSV
│   └── pipeline.py            # orquestra tudo (analyze_file)
├── datasets/                  # os 3 CSVs fornecidos
├── reports/                   # relatórios gerados (1 por teste)
└── output/                    # tracking_sheet.csv (planilha de acompanhamento)
```

Princípios de construção (robustez a dados ruins):
- **N variantes automáticas** (2, 3, …) — nada hardcoded.
- **Parser de moeda tolerante** (`R$ 10.273`, `R$ 1.234,56`, `998`, vazios, negativos).
- **Validações** que não quebram a execução e viram alertas no relatório
  (datas inválidas, duplicatas, cashback = comissão, cashback > comissão, dias
  desbalanceados entre variantes, múltiplos parceiros no arquivo).
- **Detecção de outliers + teste de robustez** (`outliers.py`): identifica dias
  atípicos (IQR sobre a margem líquida diária), sinaliza quando são **concorrentes
  entre variantes** (sinal de promoção/evento real, não erro isolado) e recalcula a
  decisão com os extremos aparados (winsorização) para confirmar se a variante
  vencedora se mantém. Os outliers são **incorporados à análise**, não ignorados.

---

## 📎 Schema esperado do CSV

| Coluna | Tipo | Descrição |
|---|---|---|
| Data | YYYY-MM-DD | Data da observação |
| Grupos de usuários | string | Variante do teste (Grupo 1, 2, 3…) |
| Parceiro | string | Parceiro do teste |
| compradores | int | Usuários únicos que compraram no dia |
| comissão | R$ | Comissão paga pelo parceiro ao Méliuz |
| cashback | R$ | Cashback distribuído aos usuários |
| vendas totais | R$ | GMV (valor total de vendas) no dia |
