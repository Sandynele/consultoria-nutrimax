"""
Gera uma versao PUBLICAVEL e autossuficiente do dashboard.

Le dashboard/index.html e injeta o conteudo dos CSVs de output/ dentro das
tags <script type="text/csv">. O resultado (publicar/index.html) e um arquivo
UNICO que funciona em qualquer host estatico (ou aberto direto no navegador),
sem precisar de servidor local nem dos arquivos CSV ao lado.
"""

from pathlib import Path

RAIZ = Path(__file__).parent.parent
origem = RAIZ / "dashboard" / "index.html"
clientes = (RAIZ / "output" / "clientes_tratados.csv").read_text(encoding="utf-8")
custos = (RAIZ / "output" / "custos_visitacao.csv").read_text(encoding="utf-8")

html = origem.read_text(encoding="utf-8")

# CSV nao contem "</script>", entao a injecao direta e segura.
html = html.replace(
    '<script id="data-clientes" type="text/csv"></script>',
    '<script id="data-clientes" type="text/csv">\n' + clientes + '</script>',
)
html = html.replace(
    '<script id="data-custos" type="text/csv"></script>',
    '<script id="data-custos" type="text/csv">\n' + custos + '</script>',
)

saida = RAIZ / "publicar" / "index.html"
saida.write_text(html, encoding="utf-8")
kb = saida.stat().st_size / 1024
print(f"Gerado: {saida} ({kb:.0f} KB, arquivo unico self-contained)")
