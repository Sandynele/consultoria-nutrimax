# Consultoria NutriMax — Carteirização Comercial

Estudo de caso de **carteirização comercial** de uma distribuidora fictícia de
nutrição e suplementação. O projeto cobre todo o fluxo: exploração e tratamento
dos dados, cálculo de custos de visitação e um **dashboard interativo** com mapa
e gráficos.

> ⚠️ Todos os dados são **fictícios**, criados apenas para fins de estudo.

> 📄 **Conclusões, KPIs e respostas às 7 perguntas do teste:** veja **[ANALISE_E_CONCLUSOES.md](ANALISE_E_CONCLUSOES.md)**.

## Estrutura

```
.
├── analise/
│   ├── tratamento_dados.py     # ETAPA 1 (exploração) + ETAPA 2 (tratamento)
│   └── build_dashboard.py      # gera a versão self-contained do dashboard
├── dados/                      # bases brutas de carteirização (CSV)
├── output/                     # bases FINAIS consumidas pelo dashboard
│   ├── clientes_tratados.csv
│   └── custos_visitacao.csv
├── dashboard/
│   └── index.html              # dashboard (lê os CSVs de output/ via fetch)
├── publicar/
│   └── index.html              # dashboard self-contained (dados embutidos, offline)
└── imagens/                    # identidade visual da marca NutriMax
```

## Como executar

### 1. Tratamento dos dados

Requer Python 3 com `pandas` e `numpy`:

```bash
pip install --user pandas numpy
python analise/tratamento_dados.py
```

Isso gera/atualiza os arquivos em `output/`.

### 2. Dashboard

O dashboard em `dashboard/index.html` lê os CSVs via `fetch`, então **precisa ser
servido por HTTP** (não funciona abrindo o arquivo direto por `file://`):

```bash
python -m http.server 8000
# abra: http://localhost:8000/dashboard/
```

Para enviar a alguém ou usar offline, use a versão **self-contained** em
`publicar/index.html` (dados já embutidos) — basta abrir com duplo clique.

## Tecnologias

- **Python** (pandas, numpy) — tratamento de dados
- **Plotly** — gráficos interativos
- **Leaflet** — mapa geográfico (distância em linha reta via Haversine)
