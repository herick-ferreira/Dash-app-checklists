# Dashboard de Checklists

---
license: apache-2.0
title: Dash-app-checklists
sdk: docker
emoji: 📊
colorFrom: blue
colorTo: gray
---


Bem-vindo! Este repositório contém um dashboard interativo construído com Dash que ajuda a visualizar os resultados de checklists por loja, tópico e tag. É simples de usar e fácil de personalizar — ideal para relatórios rápidos e painéis operacionais.

**Recursos principais**
- Visualização em Gauge da média geral (nota atingida / nota possível).
- Série temporal com média por ano/mês.
- Rankings por Loja, Tópico e Tag.
- Tabela paginada com filtros dinâmicos (Ano, Mês, Loja, Tópico, Tag).

**Pré-requisitos**
- Python 3.8+ instalado.
- Pacotes: `dash`, `dash-bootstrap-components`, `pandas`, `plotly`.

Instale dependências com:

```bash
pip install dash dash-bootstrap-components pandas plotly
```

**Como executar**
1. Coloque o arquivo de dados `Exemplo.xlsx` na mesma pasta do projeto (ou atualize a variável `name_file` em `app.py`).
2. Execute:

```bash
python app.py
```

Abra o navegador em `http://127.0.0.1:8050` (o Dash normalmente abre a URL automaticamente).

**Formato esperado do arquivo Excel**
O dashboard espera uma planilha com colunas (nomes exatos usados no código):

- `Data` (formato `dd/mm/YYYY`)
- `Loja`
- `Tópico`
- `Tag`
- `Nota Atingida` (numérico)
- `Nota Possível` (numérico)
- `Questão`
- `Resposta`
- `Observação`

Se alguma coluna estiver com nome diferente, atualize o `app.py` ou renomeie as colunas na planilha.

**Uso rápido**
- Abra o painel lateral para aplicar filtros por Ano, Mês, Loja, Tópico e Tag.
- O Gauge mostra a média ponderada (nota atingida / nota possível).
- A linha mostra a evolução por mês; marque até 14 pontos para visualizar rótulos.
- As tabelas de ranking usam cores para destacar desempenho (verde/amarelo/vermelho).

**Personalização**
- Para usar outro arquivo, altere a variável `name_file` em [app.py](app.py).
- Cores, textos e estilos estão embutidos no `app.index_string` e nas funções de helper.

**Dicas**
- Garanta que `Nota Possível` não contenha zeros distribuídos que quebrem médias — o código já faz uma substituição segura.
- Para produção, execute com um servidor WSGI (por exemplo, Gunicorn) e coloque atrás de um proxy reverso.

Contribuições e feedbacks são bem-vindos — abra uma issue ou envie um PR!
# Dash-app-checklists

