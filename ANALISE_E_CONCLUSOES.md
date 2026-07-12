# Análise e Conclusões — Carteirização de Visitação NutriMax

Documento de leitura rápida com a **recomendação**, os **KPIs** e as **respostas às 7 perguntas obrigatórias** do teste. O painel interativo está em [`dashboard/`](dashboard/) (ou na versão publicável [`publicar/index.html`](publicar/index.html)); o tratamento dos dados está em [`analise/tratamento_dados.py`](analise/tratamento_dados.py).

> ⚠️ Dados 100% fictícios (estudo de caso). Distância medida em **linha reta** (Haversine) — aproximação de proximidade, não trajeto real de carro.

---

## 🎯 Recomendação executiva (TL;DR)

**A base e o raio propostos estão certos; o ponto a ajustar é o tamanho da equipe. Comece pela Prioridade A e escale com dados.**

1. **Manter** a base em **Vila Mariana** e o **raio de 25 km** — ele cobre **92,4% do faturamento**.
2. **Contratar já 1 representante, focado na Prioridade A** (96 clientes de maior valor, nunca visitados). Visitar *todo* o A+B mensalmente exigiria 4 representantes — então "1 rep para tudo" não se sustenta; 1 rep é um **começo** bem direcionado.
3. **Alto valor fora do raio: visita pontual, não 2º ponto** — R$ 41 mil/ano contra R$ 81 mil/ano. Economia de ~R$ 40 mil no primeiro ano.
4. **Cauda longa (Grupo C)**: manter em marketplace/indicação e reativação, **sem** visita presencial dedicada.

---

## 📊 KPIs principais

| Indicador | Valor |
|---|---|
| Clientes na base | **454** registros (448 IDs únicos — 6 duplicados) |
| Com CEP preenchido | **412 (91%)** — 42 sem CEP |
| Faturamento total (12m) | **R$ 8,61 milhões** |
| Concentração A + B + Exceção | **43% dos clientes = 82,2% do faturamento** |
| Cobertura do raio de 25 km | **397 clientes (87%) = 92,4% do faturamento** |
| Prioridade A (foco inicial) | **96 clientes = 34,2% da receita**, nunca visitados |
| Alto valor fora do raio | **19 clientes** (16 nunca visitados) |
| Capacidade de 1 representante | **55 visitas/mês** |
| Custo de campo / faturamento atendido | **~5–6%** (operação viável) |

**Grupos de prioridade** (regra por percentis da própria base — ver [script](analise/tratamento_dados.py)):

| Grupo | Definição | Clientes | % Faturamento |
|---|---|---|---|
| **Prioridade A** | Alto valor, dentro do raio, **nunca** visitado | 96 | maior oportunidade |
| **Prioridade B** | Alto valor, dentro do raio, já visitado | 80 | expandir conta |
| **Exceção estratégica** | Alto valor, **fora** do raio | 19 | avaliar caso a caso |
| **Prioridade C** | Demais (menor valor / reativação) | 259 | cauda longa |

---

## ❓ Respostas às 7 perguntas obrigatórias

### 1. Quantos clientes existem? Quantos têm CEP? Isso muda a análise de cobertura?
- **454 registros**, mas apenas **448 IDs únicos** — há **6 IDs duplicados** (12 linhas). Foram **auditados, não removidos**: consolidar é decisão de negócio.
- **412 têm CEP preenchido (91%)**; 42 estão sem CEP.
- **Não muda a análise de cobertura.** Todos os 454 clientes têm **latitude/longitude por bairro**, então a cobertura geográfica está garantida mesmo sem CEP. O CEP só seria necessário para **roteirização fina porta-a-porta**.

### 2. Qual bairro/zona concentra mais clientes e mais faturamento? É a mesma região?
- **Sim, é a mesma região:** a zona **Sul** lidera nas duas pontas — **24,4% dos clientes** e **27,3% do faturamento**.
- Não há descolamento relevante entre volume e receita por zona, o que **simplifica a logística** da rota.

### 3. Com o raio proposto, quantos clientes e quanto de faturamento entram na carteira?
- **397 clientes (87%)** ficam dentro dos 25 km a partir de Vila Mariana.
- Eles representam **92,4% do faturamento** — o raio captura quase toda a receita. **Proposta geográfica validada.**

### 4. Há relação entre já ter sido visitado e o faturamento? (e o que isso *não* diz)
- Visualmente **sim**: clientes já visitados têm faturamento **mediano de R$ 14.649**, contra **R$ 5.122** dos nunca visitados — quase **3×**.
- **Ressalva importante:** isto é **associação, não causa**. A empresa provavelmente **escolheu visitar quem já era grande** (viés de seleção). O gráfico **não prova** que a visita gera faturamento.
- Para medir o efeito real seria preciso um **piloto A/B** (comparar visitados vs. um grupo de controle parecido) ou análise **antes/depois** da visita.

### 5. Há clientes de alto valor, nunca visitados, fora do raio? O que fazer?
- **Sim: 19 clientes de alto valor fora do raio** (grupo "Exceção estratégica"), dos quais **16 nunca foram visitados** — dinheiro na mesa.
- **Recomendação:** atendê-los por **visita pontual/avulsa**, sem expandir o raio nem criar rota fixa por causa deles. Reavaliar se o grupo crescer (ver pergunta 6).

### 6. A proposta (1 rep, 25 km, Vila Mariana) é a melhor? Pontual × 2º ponto (com número)
- **Base e raio: manter.** **Equipe: ajustar.** 1 representante faz ~55 visitas/mês:
  - Visitar **só a Prioridade A** (96 clientes) **1×/mês → 2 representantes**; a cada 2 meses → **1**.
  - Visitar **todo o A+B** mensalmente **→ 4 representantes**.
  - Logo, "1 representante para toda a carteira prioritária" **não se sustenta**; 1 rep é um bom **começo focado no Grupo A**.
- **Fora do raio — pontual vs. 2º ponto** (base [`custos_visitacao.csv`](output/custos_visitacao.csv)):

  | Opção | Custo (ano 1) |
  |---|---|
  | **Visita pontual** (19 clientes, 1×/mês) | **R$ 41.040** |
  | **Abrir 2º ponto** (salário anual + R$ 3.200 de abertura) | **R$ 81.200** |

  → A **visita pontual custa metade**. **Não abrir 2º ponto agora.**
- No cenário de campo, o custo equivale a **~5–6% do faturamento atendido** — **operação financeiramente viável**.

### 7. Se tivesse 1 gráfico só para convencer a diretoria, qual e por quê?
- **"Faturamento por grupo de prioridade"** (marcado com ★ no dashboard).
- **Por quê:** numa única imagem mostra que **A, B e Exceção concentram 82,2% da receita** — e quase todos estão dentro dos 25 km. Ele responde de imediato *"quem visitar"* e justifica **contratar já**, começando pelo grupo certo.

---

## 🧹 Qualidade dos dados (a base tem imperfeições de propósito)

Tratamento aplicado em [`analise/tratamento_dados.py`](analise/tratamento_dados.py), **preservando a base original**:

- **`canal_venda` padronizado** (espaços, acentos e maiúsculas: `"Loja Física"`, `" loja  fisica "` → `Loja Fisica`).
- **Números e datas convertidos** com tolerância a formato inválido (vira nulo, não quebra).
- **`cep_preenchido` (Sim/Não)** criada para medir completude do cadastro.
- **IDs duplicados auditados** em [`dados/auditoria_id_duplicado.csv`](dados/auditoria_id_duplicado.csv) — **não removidos**.
- **Prioridade por percentis** (P75 de faturamento/pedidos) — a regra se ajusta sozinha se a base mudar.

---

## ⚠️ Ressalvas honestas

- **Correlação ≠ causalidade** na relação visita × faturamento (viés de seleção — ver pergunta 4).
- **Distância em linha reta** (Haversine): o trajeto real de carro tende a ser maior. Por isso o custo usa `2 × distância × R$/km`, para não subestimar.
- **6 IDs duplicados** ainda a consolidar por regra de negócio antes de operacionalizar.

---

*Todos os números deste documento são reproduzidos ao vivo no [dashboard](dashboard/), onde custo e frequência de visita são ajustáveis para simular cenários.*
