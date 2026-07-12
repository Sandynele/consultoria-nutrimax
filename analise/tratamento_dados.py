"""
Estudo de caso: Carteirizacao comercial de distribuidora ficticia
de nutricao e suplementacao.

ETAPA 1 - Exploracao inicial dos dados (data understanding).
ETAPA 2 - Tratamento (data preparation) da base de carteirizacao.

Na ETAPA 1 NAO alteramos nenhum dado: apenas "conhecemos" os arquivos
(estrutura, tamanho, tipos e qualidade). Na ETAPA 2 aplicamos o
tratamento sobre uma COPIA, preservando a base original intacta.
"""

# pandas: biblioteca padrao para manipulacao de dados tabulares.
import pandas as pd

# numpy: usada no calculo vetorizado da distancia (formula de Haversine).
import numpy as np

# unicodedata: usada para remover acentos ao padronizar textos.
import unicodedata

# pathlib: monta caminhos de forma independente do sistema operacional.
from pathlib import Path

# Caminho da pasta "dados" relativo a raiz do projeto.
# __file__ = este script (dentro de "analise"); .parent.parent sobe ate a raiz.
PASTA_DADOS = Path(__file__).parent.parent / "dados"

# Pasta "output": arquivos FINAIS que o dashboard consome diretamente
# (output/clientes_tratados.csv e output/custos_visitacao.csv). Enquanto
# "dados" guarda a base bruta e os intermediarios do tratamento, "output"
# guarda o resultado pronto para publicacao. Assim rodar este script deixa
# o dashboard atualizado automaticamente, sem copia manual de arquivos.
PASTA_OUTPUT = Path(__file__).parent.parent / "output"

# Ponto de referencia da analise de cobertura: Vila Mariana (Sao Paulo/SP).
# A partir dele medimos a distancia de cada cliente.
VILA_MARIANA_LAT = -23.5875
VILA_MARIANA_LON = -46.6396

# Raio de cobertura adotado para a carteirizacao (em quilometros).
RAIO_COBERTURA_KM = 25


def explorar(nome_arquivo: str) -> pd.DataFrame:
    """
    Le um CSV e imprime um diagnostico inicial dele.
    Retorna o DataFrame lido para uso posterior, se necessario.
    """

    caminho = PASTA_DADOS / nome_arquivo

    # ETAPA 1 - Leitura do CSV.
    # sep=";" -> os arquivos usam ponto e virgula como separador de colunas.
    # encoding="utf-8-sig" -> le UTF-8 e ignora o BOM, preservando acentos
    # (Essencia, Apice, etc.) sem quebrar em FarmÃ¡cia.
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")

    # Cabecalho visual para separar a saida de cada arquivo no terminal.
    print("=" * 70)
    print(f"ARQUIVO: {nome_arquivo}")
    print("=" * 70)

    # ETAPA 2 - Primeiras linhas.
    # head() mostra as 5 primeiras linhas para inspecao visual do conteudo.
    print("\n[2] PRIMEIRAS LINHAS (head):")
    print(df.head())

    # ETAPA 3 - Dimensoes do dataset.
    # df.shape retorna a tupla (linhas, colunas).
    print("\n[3] QUANTIDADE DE LINHAS E COLUNAS:")
    print(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}")

    # ETAPA 4 - Tipos de dados de cada coluna.
    # dtypes indica como o pandas interpretou cada coluna (int, float, object...).
    # Ajuda a identificar colunas numericas lidas como texto, datas como string, etc.
    print("\n[4] TIPOS DE DADOS (dtypes):")
    print(df.dtypes)

    # ETAPA 5 - Valores nulos por coluna.
    # isnull().sum() conta quantas celulas vazias existem em cada coluna.
    # Colunas como "data_ultima_compra" ou "obs_visita" tendem a ter nulos.
    print("\n[5] VALORES NULOS POR COLUNA:")
    print(df.isnull().sum())

    print("\n")  # Espacamento entre um arquivo e outro.

    # ETAPA 6 - Nenhum dado foi alterado ate aqui: apenas leitura e diagnostico.
    return df


def _padronizar_texto(valor):
    """
    Padroniza um valor de texto:
    - remove espacos nas pontas e colapsa espacos internos repetidos;
    - remove acentos (Fisica/Física -> Fisica);
    - aplica Title Case (primeira letra de cada palavra em maiuscula).

    Assim "loja fisica", " Loja  Fisica " e "Loja Física" viram
    todos "Loja Fisica". Valores nulos (NaN) sao preservados.
    """

    # Mantem nulos como nulos (nao tentamos padronizar celula vazia).
    if pd.isna(valor):
        return valor

    # Garante que estamos lidando com string.
    texto = str(valor)

    # split() sem argumento quebra por qualquer espaco e descarta os vazios;
    # o join com um unico espaco colapsa espacos duplicados e tira as pontas.
    texto = " ".join(texto.split())

    # Remove acentos: decompoe os caracteres (NFKD) e descarta os sinais.
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    # Padroniza a capitalizacao.
    return texto.title()


def tratar(nome_arquivo: str) -> pd.DataFrame:
    """
    ETAPA 2 - Tratamento da base de carteirizacao.

    Regras aplicadas (sobre uma COPIA, preservando o original):
      1. Preservar a base original;
      2. Padronizar canal_venda (espacos e maiusculas/minusculas);
      3. Converter faturamento_12m e qtd_pedidos_12m para numerico;
      4. Converter data_cadastro e data_ultima_compra para data;
      5. Criar coluna cep_preenchido (Sim/Nao);
      6. Gerar tabela de auditoria de id_cliente duplicado;
      7. NAO remover duplicidades automaticamente;
      8. Mostrar um resumo das alteracoes realizadas.
    """

    caminho = PASTA_DADOS / nome_arquivo

    # (1) BASE ORIGINAL - lida e mantida intacta como referencia.
    df_original = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")

    # Trabalhamos sempre sobre uma copia para nao alterar o original.
    df = df_original.copy()

    print("=" * 70)
    print(f"TRATAMENTO: {nome_arquivo}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # (2) PADRONIZAR canal_venda
    # ------------------------------------------------------------------
    # Guardamos os valores distintos ANTES para mostrar no resumo.
    canais_antes = sorted(df_original["canal_venda"].dropna().unique().tolist())
    df["canal_venda"] = df["canal_venda"].map(_padronizar_texto)
    canais_depois = sorted(df["canal_venda"].dropna().unique().tolist())

    # ------------------------------------------------------------------
    # (3) CONVERTER colunas numericas
    # ------------------------------------------------------------------
    # Colunas que devem ser numericas.
    colunas_numericas = ["faturamento_12m", "qtd_pedidos_12m"]
    for coluna in colunas_numericas:
        # Normaliza possivel formato brasileiro antes de converter:
        # remove ponto de milhar e troca virgula decimal por ponto.
        serie_texto = (
            df[coluna]
            .astype(str)
            .str.strip()
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        # to_numeric com errors="coerce": o que nao for numero vira NaN,
        # em vez de quebrar a execucao.
        df[coluna] = pd.to_numeric(serie_texto, errors="coerce")

    # ------------------------------------------------------------------
    # (4) CONVERTER colunas de data
    # ------------------------------------------------------------------
    colunas_data = ["data_cadastro", "data_ultima_compra"]
    for coluna in colunas_data:
        # format="%Y-%m-%d" -> as datas vem no padrao ISO (2025-06-23).
        # errors="coerce": datas invalidas viram NaT (nulo de data).
        df[coluna] = pd.to_datetime(
            df[coluna], format="%Y-%m-%d", errors="coerce"
        )

    # ------------------------------------------------------------------
    # (5) CRIAR coluna cep_preenchido (Sim/Nao)
    # ------------------------------------------------------------------
    # Consideramos "nao preenchido" quando o CEP e nulo ou string vazia.
    cep_texto = df["cep"].astype(str).str.strip()
    cep_ausente = df["cep"].isna() | (cep_texto == "") | (cep_texto.str.lower() == "nan")
    df["cep_preenchido"] = cep_ausente.map({True: "Nao", False: "Sim"})

    # ------------------------------------------------------------------
    # (6) TABELA DE AUDITORIA de id_cliente duplicado
    # ------------------------------------------------------------------
    # keep=False marca TODAS as ocorrencias de um id que aparece mais de uma vez.
    marcados = df["id_cliente"].duplicated(keep=False)
    auditoria_duplicados = (
        df.loc[marcados]
        .sort_values("id_cliente")
        .copy()
    )
    # Quantas vezes cada id_cliente aparece (util para o relatorio).
    contagem_ids = (
        df["id_cliente"]
        .value_counts()
        .loc[lambda s: s > 1]
        .rename_axis("id_cliente")
        .reset_index(name="qtd_ocorrencias")
    )

    # (7) IMPORTANTE: nao removemos as duplicidades. Apenas as auditamos;
    #     a decisao de remover fica a cargo da area de negocio.

    # ------------------------------------------------------------------
    # (8) RESUMO DAS ALTERACOES
    # ------------------------------------------------------------------
    print("\n[RESUMO DO TRATAMENTO]")
    print(f"- Base original preservada: {df_original.shape[0]} linhas x "
          f"{df_original.shape[1]} colunas (intacta).")

    print(f"\n- canal_venda padronizado:")
    print(f"    antes  ({len(canais_antes)} valores): {canais_antes}")
    print(f"    depois ({len(canais_depois)} valores): {canais_depois}")

    print("\n- Conversao numerica:")
    for coluna in colunas_numericas:
        invalidos = int(df[coluna].isna().sum())
        print(f"    {coluna}: tipo -> {df[coluna].dtype} | "
              f"valores nao convertidos (NaN): {invalidos}")

    print("\n- Conversao de datas:")
    for coluna in colunas_data:
        nulos_orig = int(df_original[coluna].isna().sum())
        nulos_depois = int(df[coluna].isna().sum())
        # Datas que ficaram nulas alem das que ja eram vazias = falhas de parse.
        falhas = nulos_depois - nulos_orig
        print(f"    {coluna}: tipo -> {df[coluna].dtype} | "
              f"vazias na origem: {nulos_orig} | "
              f"invalidas na conversao: {max(falhas, 0)}")

    preenchidos = int((df["cep_preenchido"] == "Sim").sum())
    ausentes = int((df["cep_preenchido"] == "Nao").sum())
    print(f"\n- cep_preenchido criada: Sim={preenchidos} | Nao={ausentes}")

    print("\n- Auditoria de id_cliente duplicado:")
    if contagem_ids.empty:
        print("    Nenhum id_cliente duplicado encontrado.")
    else:
        print(f"    ids distintos duplicados: {contagem_ids.shape[0]}")
        print(f"    linhas envolvidas: {auditoria_duplicados.shape[0]}")
        print(contagem_ids.to_string(index=False))
    print("    (duplicidades NAO foram removidas — apenas auditadas.)")

    # ------------------------------------------------------------------
    # Persistencia dos resultados do tratamento.
    # ------------------------------------------------------------------
    # Salva a base tratada e a auditoria em arquivos separados,
    # sem sobrescrever a base original.
    saida_tratada = PASTA_DADOS / "carteirizacao_tratada.csv"
    saida_auditoria = PASTA_DADOS / "auditoria_id_duplicado.csv"
    df.to_csv(saida_tratada, sep=";", index=False, encoding="utf-8-sig")
    auditoria_duplicados.to_csv(
        saida_auditoria, sep=";", index=False, encoding="utf-8-sig"
    )
    print(f"\n- Arquivos gerados:")
    print(f"    base tratada -> {saida_tratada.name}")
    print(f"    auditoria    -> {saida_auditoria.name}")
    print("\n")

    return df


def _haversine_km(lat, lon, lat_ref, lon_ref):
    """
    Calcula a distancia EM LINHA RETA (great-circle) entre dois pontos
    sobre a superficie da Terra, em quilometros, pela formula de Haversine.

    IMPORTANTE: esta e uma distancia "em linha reta" (voo de passaro).
    Ela NAO representa o trajeto real de carro. O percurso rodoviario
    tende a ser MAIOR, pois depende do traçado das ruas, sentido das
    vias, rios, viadutos, transito e obstaculos. Serve como aproximacao
    rapida de proximidade, nao como estimativa de deslocamento real.

    Aceita valores escalares ou vetores (Series/array) do numpy, permitindo
    calcular a distancia de varios clientes de uma so vez.
    """

    # Raio medio da Terra em quilometros (usado para converter o angulo
    # entre os dois pontos em distancia sobre a superficie).
    raio_terra_km = 6371.0

    # As funcoes trigonometricas trabalham em radianos, entao convertemos
    # as coordenadas de graus para radianos.
    lat = np.radians(lat)
    lon = np.radians(lon)
    lat_ref = np.radians(lat_ref)
    lon_ref = np.radians(lon_ref)

    # Diferencas de latitude e de longitude entre os dois pontos.
    d_lat = lat_ref - lat
    d_lon = lon_ref - lon

    # Formula de Haversine:
    # a  -> "quadrado da metade da corda" entre os pontos;
    # c  -> distancia angular (em radianos) entre eles.
    a = np.sin(d_lat / 2) ** 2 + np.cos(lat) * np.cos(lat_ref) * np.sin(d_lon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    # Distancia = raio da Terra x angulo (em radianos).
    return raio_terra_km * c


def analisar_cobertura(df: pd.DataFrame) -> pd.DataFrame:
    """
    ETAPA 3 - Analise de cobertura geografica.

    A partir da base ja tratada, calcula para cada cliente:
      - distancia_km        : distancia em LINHA RETA ate a Vila Mariana;
      - dentro_raio_25km    : "Sim" se a distancia <= 25 km, senao "Nao".

    Em seguida imprime:
      - resumo de clientes dentro e fora do raio;
      - faturamento total dentro do raio;
      - percentual do faturamento coberto pelo raio.

    OBS.: a distancia usada aqui e "em linha reta" (Haversine) e NAO
    corresponde ao trajeto real de carro (ver _haversine_km).
    """

    # Trabalhamos sobre uma copia para nao alterar o DataFrame recebido.
    df = df.copy()

    print("=" * 70)
    print("ANALISE DE COBERTURA - Raio a partir da Vila Mariana")
    print("=" * 70)

    # Garante que latitude/longitude sejam numericas; coordenadas invalidas
    # viram NaN (e, consequentemente, distancia NaN) em vez de quebrar.
    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")

    # (1) distancia_km - distancia em linha reta ate a Vila Mariana.
    # round(2) apenas para leitura; o calculo em si usa a precisao total.
    df["distancia_km"] = _haversine_km(
        lat, lon, VILA_MARIANA_LAT, VILA_MARIANA_LON
    ).round(2)

    # (2) dentro_raio_25km - marca "Sim"/"Nao" conforme o raio de cobertura.
    dentro = df["distancia_km"] <= RAIO_COBERTURA_KM
    df["dentro_raio_25km"] = dentro.map({True: "Sim", False: "Nao"})

    # ------------------------------------------------------------------
    # (3) RESUMO de clientes dentro e fora do raio
    # ------------------------------------------------------------------
    # Clientes sem coordenada valida ficam com distancia NaN e nao entram
    # nem em "dentro" nem em "fora"; contamos esses casos a parte.
    qtd_dentro = int((df["dentro_raio_25km"] == "Sim").sum())
    qtd_fora = int((df["dentro_raio_25km"] == "Nao").sum())
    qtd_sem_coord = int(df["distancia_km"].isna().sum())
    total = df.shape[0]

    print(f"\n[RESUMO DE COBERTURA] (raio de {RAIO_COBERTURA_KM} km)")
    print(f"- Total de clientes: {total}")
    print(f"- Dentro do raio: {qtd_dentro} "
          f"({qtd_dentro / total:.1%} dos clientes)")
    print(f"- Fora do raio:   {qtd_fora} "
          f"({qtd_fora / total:.1%} dos clientes)")
    if qtd_sem_coord:
        print(f"- Sem coordenada valida (nao classificados): {qtd_sem_coord}")

    # ------------------------------------------------------------------
    # (4) FATURAMENTO dentro do raio e (5) percentual coberto
    # ------------------------------------------------------------------
    # faturamento_12m ja foi convertido para numerico na etapa de tratamento.
    faturamento_total = df["faturamento_12m"].sum()
    faturamento_dentro = df.loc[dentro, "faturamento_12m"].sum()

    # Evita divisao por zero caso o faturamento total seja 0.
    if faturamento_total > 0:
        percentual_coberto = faturamento_dentro / faturamento_total
    else:
        percentual_coberto = 0.0

    print("\n[FATURAMENTO x COBERTURA]")
    print(f"- Faturamento total (12m):        R$ {faturamento_total:,.2f}")
    print(f"- Faturamento dentro do raio:     R$ {faturamento_dentro:,.2f}")
    print(f"- Percentual coberto pelo raio:   {percentual_coberto:.1%}")
    print("  (distancia em linha reta; o trajeto real de carro pode ser maior.)")

    # ------------------------------------------------------------------
    # Persistencia do resultado da analise de cobertura.
    # ------------------------------------------------------------------
    saida_cobertura = PASTA_DADOS / "carteirizacao_cobertura.csv"
    df.to_csv(saida_cobertura, sep=";", index=False, encoding="utf-8-sig")
    print(f"\n- Arquivo gerado: {saida_cobertura.name}")
    print("\n")

    return df


def classificar_prioridade(df: pd.DataFrame) -> pd.DataFrame:
    """
    ETAPA 4 - Classificacao de prioridade comercial.

    Cria a coluna prioridade_comercial combinando 5 sinais da base tratada:
      - faturamento_12m       -> VALOR do cliente;
      - qtd_pedidos_12m       -> FREQUENCIA de compra (potencial/engajamento);
      - ja_visitado           -> RELACIONAMENTO ja existente;
      - dentro_raio_25km      -> LOGISTICA (facil de atender);
      - data_ultima_compra    -> RECENCIA (ativo x candidato a reativacao).

    Os limites NAO sao fixos: usamos PERCENTIS calculados da propria base,
    para que a regra se ajuste sozinha se a base mudar.

    Definicao de "alto valor": estar no topo 25% (percentil 75) em
    faturamento OU em numero de pedidos. Assim priorizamos tanto quem
    fatura muito quanto quem compra com frequencia.

    Classificacoes (avaliadas nesta ordem de precedencia):
      - Prioridade A       : alto valor, dentro do raio e NUNCA visitado
                             (maior oportunidade: perto e ainda sem contato);
      - Prioridade B       : alto valor, dentro do raio e JA visitado
                             (relacao ativa -> foco em expandir a conta);
      - Excecao estrategica: alto valor mas FORA do raio
                             (vale o esforco apesar da logistica);
      - Prioridade C       : demais clientes (menor valor ou reativacao).
    """

    df = df.copy()

    print("=" * 70)
    print("PRIORIZACAO COMERCIAL - Percentis calculados da base")
    print("=" * 70)

    # ------------------------------------------------------------------
    # (1) LIMIARES POR PERCENTIL (sem numeros fixos "chutados")
    # ------------------------------------------------------------------
    # Topo 25% em faturamento e em pedidos definem "alto valor".
    lim_fat = df["faturamento_12m"].quantile(0.75)
    lim_ped = df["qtd_pedidos_12m"].quantile(0.75)

    # Recencia: dias desde a ultima compra. Como nao temos a data de
    # extracao, usamos a compra mais recente da base como "hoje".
    data_ultima = pd.to_datetime(df["data_ultima_compra"], errors="coerce")
    data_ref = data_ultima.max()
    dias_sem_compra = (data_ref - data_ultima).dt.days
    df["dias_sem_compra"] = dias_sem_compra

    # "Inativo" = nunca comprou (data vazia) ou faz muito tempo que nao
    # compra (acima do percentil 75 de dias sem compra da base).
    lim_inativo = dias_sem_compra.quantile(0.75)
    inativo = dias_sem_compra.isna() | (dias_sem_compra > lim_inativo)

    # ------------------------------------------------------------------
    # (2) SINAIS BOOLEANOS por cliente
    # ------------------------------------------------------------------
    alto_valor = (df["faturamento_12m"] >= lim_fat) | (df["qtd_pedidos_12m"] >= lim_ped)
    dentro = df["dentro_raio_25km"].eq("Sim")
    visitado = df["ja_visitado"].eq("Sim")

    # ------------------------------------------------------------------
    # (3) REGRA DE CLASSIFICACAO (np.select escolhe a 1a condicao verdadeira)
    # ------------------------------------------------------------------
    condicoes = [
        alto_valor & ~dentro,               # alto valor, porem fora do raio
        alto_valor & dentro & ~visitado,    # alto valor, perto e sem contato
        alto_valor & dentro & visitado,     # alto valor, perto e ja atendido
    ]
    rotulos = ["Excecao estrategica", "Prioridade A", "Prioridade B"]
    df["prioridade_comercial"] = np.select(condicoes, rotulos, default="Prioridade C")

    # ------------------------------------------------------------------
    # (4) RESUMO: limiares usados, contagem e faturamento por grupo
    # ------------------------------------------------------------------
    print("\n[LIMIARES POR PERCENTIL]")
    print(f"- Alto valor: faturamento_12m >= R$ {lim_fat:,.2f} (P75) "
          f"OU qtd_pedidos_12m >= {lim_ped:.0f} (P75)")
    print(f"- Inativo (reativacao): sem compra ou > {lim_inativo:.0f} dias "
          f"sem comprar (P75); referencia = {data_ref.date()}")

    # Ordem fixa e faturamento total para calcular a participacao (%).
    ordem = ["Prioridade A", "Prioridade B", "Excecao estrategica", "Prioridade C"]
    faturamento_total = df["faturamento_12m"].sum()

    print("\n[CLIENTES E FATURAMENTO POR GRUPO]")
    for grupo in ordem:
        linhas = df["prioridade_comercial"] == grupo
        qtd = int(linhas.sum())
        fat = df.loc[linhas, "faturamento_12m"].sum()
        pct_fat = fat / faturamento_total if faturamento_total else 0
        print(f"- {grupo:<20} clientes: {qtd:>3} | "
              f"faturamento: R$ {fat:>14,.2f} ({pct_fat:.1%} do total)")

    # Leituras de apoio que usam qtd_pedidos e recencia explicitamente:
    b_expansao = int(
        ((df["prioridade_comercial"] == "Prioridade B")
         & (df["qtd_pedidos_12m"] < df["qtd_pedidos_12m"].median())).sum()
    )
    c_reativacao = int(
        ((df["prioridade_comercial"] == "Prioridade C") & inativo).sum()
    )
    print(f"\n- Em Prioridade B, com potencial de expansao "
          f"(pedidos abaixo da mediana): {b_expansao}")
    print(f"- Em Prioridade C, candidatos a reativacao "
          f"(inativos): {c_reativacao}")

    # ------------------------------------------------------------------
    # Persistencia do resultado priorizado.
    # ------------------------------------------------------------------
    # (a) intermediario, em "dados": base priorizada completa do estudo.
    saida = PASTA_DADOS / "carteirizacao_priorizada.csv"
    df.to_csv(saida, sep=";", index=False, encoding="utf-8-sig")

    # (b) FINAL, em "output": mesma base com o nome que o dashboard le
    # (output/clientes_tratados.csv). Sem BOM porque o parser do dashboard
    # ja o remove e os demais arquivos de output seguem esse padrao.
    PASTA_OUTPUT.mkdir(exist_ok=True)
    saida_dashboard = PASTA_OUTPUT / "clientes_tratados.csv"
    df.to_csv(saida_dashboard, sep=";", index=False, encoding="utf-8")

    print(f"\n- Arquivos gerados:")
    print(f"    base priorizada -> dados/{saida.name}")
    print(f"    base do dashboard -> output/{saida_dashboard.name}")
    print("\n")

    return df


def tratar_custos(nome_arquivo: str) -> pd.DataFrame:
    """
    ETAPA 5 - Tratamento da tabela de custos de visitacao.

    A base bruta (dados/custosvisitacao.csv) traz a coluna "valor" como texto.
    Aqui convertemos "valor" para numerico e gravamos o resultado final em
    output/custos_visitacao.csv, que e o arquivo que o dashboard consome.
    Assim os parametros financeiros do dashboard saem sempre desta base,
    sem edicao manual.
    """

    caminho = PASTA_DADOS / nome_arquivo
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")

    print("=" * 70)
    print(f"TRATAMENTO DE CUSTOS: {nome_arquivo}")
    print("=" * 70)

    # Converte "valor" para numerico. Diferente da base de clientes, esta
    # tabela ja usa PONTO como separador decimal (ex.: 1.10), o padrao que o
    # pandas entende — entao NAO removemos pontos (isso corromperia 1.10 -> 110).
    # errors="coerce": valor invalido vira NaN em vez de quebrar a execucao.
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    invalidos = int(df["valor"].isna().sum())
    print(f"\n[RESUMO] {df.shape[0]} itens de custo | "
          f"valores nao convertidos (NaN): {invalidos}")

    PASTA_OUTPUT.mkdir(exist_ok=True)
    saida = PASTA_OUTPUT / "custos_visitacao.csv"
    df.to_csv(saida, sep=";", index=False, encoding="utf-8")
    print(f"- Arquivo gerado: output/{saida.name}")
    print("\n")

    return df


def main():
    # ETAPA 1 - Explora os dois arquivos do estudo de caso.
    explorar("carteirizacaospsimulado.csv")
    explorar("custosvisitacao.csv")

    # ETAPA 2 - Trata a base principal de carteirizacao.
    df_tratado = tratar("carteirizacaospsimulado.csv")

    # ETAPA 3 - Analisa a cobertura geografica (raio a partir da Vila Mariana).
    df_cobertura = analisar_cobertura(df_tratado)

    # ETAPA 4 - Classifica a prioridade comercial de cada cliente
    #           e grava a base final do dashboard (output/clientes_tratados.csv).
    classificar_prioridade(df_cobertura)

    # ETAPA 5 - Trata os custos e grava output/custos_visitacao.csv,
    #           fechando o pipeline ate a entrada do dashboard.
    tratar_custos("custosvisitacao.csv")


if __name__ == "__main__":
    main()
