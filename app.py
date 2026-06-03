import os
import warnings

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

warnings.filterwarnings("ignore")

# =========================================================
# CONFIG
# =========================================================

path_main = os.getcwd()
name_file = "Exemplo.xlsx"
title = "Dashboard " + name_file.replace(".xlsx", "").replace("_", " ")

CARD_BG = "#F7F8FA"
SIDEBAR_BG = "#001D3D"
APP_BG = "#EDEDED"

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = title
server = app.server

# CSS injetado via index_string (compatível com todas as versões do Dash)
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        body {
            background-color: #EDEDED;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #B8B8B8; border-radius: 20px; }
        .dashboard-title {
            color: #222;
            font-weight: 700;
            font-size: 1.7rem;
            text-align: center;
            padding: 1.2rem 0 0.5rem 0;
            letter-spacing: 0.01em;
        }
        .sidebar {
            background-color: #001D3D;
            position: fixed;
            top: 0;
            left: 0;
            width: 280px;
            max-width: 280px;
            min-height: 100vh;
            height: 100vh;
            padding: 1.5rem 1rem;
            z-index: 1500;
            border-right: 1px solid rgba(255,255,255,0.08);
            box-shadow: 4px 0 16px rgba(0,0,0,0.15);
            overflow-y: auto;
            transform: translateX(0);
            transition: transform 0.25s ease;
        }
        .sidebar-title {
            color: #fff;
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 1.2rem;
            text-align: center;
            letter-spacing: 0.04em;
        }
        .filter-label {
            color: #fff;
            font-weight: 700;
            font-size: 0.82rem;
            margin-bottom: 0.2rem;
            margin-top: 0.8rem;
            display: block;
        }
        .Select-control {
            background-color: #F7F8FA !important;
            border-radius: 12px !important;
            border: 1px solid #D0D0D0 !important;
        }
        .gray-card {
            background: #F7F8FA;
            border-radius: 26px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.10);
            margin-bottom: 15px;
        }
        .section-header {
            color: #222;
            font-weight: 700;
            font-size: 1rem;
            text-align: center;
            margin-bottom: 0.5rem;
            margin-top: 0.3rem;
        }
        .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td,
        .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
            font-weight: 700 !important;
            font-family: 'Segoe UI', sans-serif;
            font-size: 0.85rem;
        }
        .pager-label {
            color: #222;
            font-weight: 700;
            font-size: 0.82rem;
            margin-bottom: 0.2rem;
        }
        .pager-info {
            color: #555;
            font-size: 0.82rem;
            margin-top: 0.6rem;
        }
        .main-content {
            padding: 0 1.5rem 2rem 1.5rem;
        }
        .Select-value {
            background-color: #001d3d !important;
            color: #fff !important;
            border-radius: 8px !important;
        }
        .sidebar-toggle {
            position: fixed;
            top: 12px;
            left: 12px;
            z-index: 2000;
            background-color: #001D3D;
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 6px 10px;
            font-size: 18px;
            line-height: 1;
            box-shadow: 0 6px 16px rgba(0,0,0,0.20);
            cursor: pointer;
        }
        .sidebar-toggle:focus {
            outline: none;
            box-shadow: 0 0 0 3px rgba(0,29,61,0.25);
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# =========================================================
# LOAD DATA
# =========================================================

list_meses = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
]


def carregar_dados():
    df = pd.read_excel(os.path.join(path_main, name_file))

    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
    df["Ano"] = df["Data"].dt.year.astype(str)
    df["Mês"] = df["Data"].dt.month.astype(str).str.zfill(2)

    df_group = (
        df.groupby(["Ano", "Mês", "Loja"], as_index=False)[
            ["Nota Atingida", "Nota Possível"]
        ].sum()
    )
    df_group["Média"] = df_group["Nota Atingida"] / df_group["Nota Possível"]
    df_group["Ano / Mês"] = df_group["Mês"] + "/" + df_group["Ano"]
    df_group["Color"] = df_group["Média"].apply(
        lambda x: "#ff4b4b" if x < 0.88 else "#22c55e"
    )
    df_group = df_group.sort_values(by=["Ano", "Mês"])

    return df, df_group


df, df_group = carregar_dados()

anos = sorted(df["Ano"].dropna().unique())
meses_unicos = df["Mês"].apply(lambda x: list_meses[int(x) - 1]).dropna().unique()
meses = sorted(meses_unicos, key=lambda x: list_meses.index(x))
lojas = sorted(df["Loja"].dropna().unique())
topicos = sorted(df["Tópico"].dropna().unique())
tags = sorted(df["Tag"].dropna().unique())

# =========================================================
# LAYOUT
# =========================================================

def make_dropdown(id_, options, placeholder, multi=True):
    return dcc.Dropdown(
        id=id_,
        options=[{"label": o, "value": o} for o in options],
        multi=multi,
        placeholder=placeholder,
        style={
            "borderRadius": "12px",
            "backgroundColor": "#F2F2F2",
            "border": "1px solid #D0D0D0",
            "fontSize": "0.85rem",
        },
    )


sidebar = html.Div(
    id="sidebar-col",
    className="sidebar",
    # start hidden off-canvas
    style={"transform": "translateX(-110%)"},
    children=[
        html.Div("🔎 Filtros", className="sidebar-title"),
        html.Span("Ano", className="filter-label"),
        make_dropdown("filter-ano", anos, "Selecione..."),
        html.Span("Mês", className="filter-label"),
        make_dropdown("filter-mes", meses, "Selecione..."),
        html.Span("Loja", className="filter-label"),
        make_dropdown("filter-loja", lojas, "Selecione..."),
        html.Span("Tópico", className="filter-label"),
        make_dropdown("filter-topico", topicos, "Selecione..."),
        html.Span("Tag", className="filter-label"),
        make_dropdown("filter-tag", tags, "Selecione..."),
    ],
)

main_content = html.Div(
    className="main-content",
    children=[
        html.H1(f"📊 {title}", className="dashboard-title"),

        # ── Row 1: Gauge + Line chart ──────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        className="gray-card",
                        children=[
                            html.Div("Média / Meta", className="section-header"),
                            dcc.Graph(id="gauge-chart", config={"displayModeBar": False}),
                        ],
                    ),
                    md=5,
                ),
                dbc.Col(
                    html.Div(
                        className="gray-card",
                        children=[
                            html.Div("Média por Ano e Mês", className="section-header"),
                            dcc.Graph(id="line-chart", config={"displayModeBar": False}),
                        ],
                    ),
                    md=7,
                ),
            ],
            className="mb-3",
        ),

        # ── Row 2: Rankings ────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        className="gray-card",
                        children=[
                            html.Div("Ranking por Loja", className="section-header"),
                            html.Div(id="table-lojas"),
                        ],
                    ),
                    md=4,
                ),
                dbc.Col(
                    html.Div(
                        className="gray-card",
                        children=[
                            html.Div("Ranking por Tópico", className="section-header"),
                            html.Div(id="table-topicos"),
                        ],
                    ),
                    md=4,
                ),
                dbc.Col(
                    html.Div(
                        className="gray-card",
                        children=[
                            html.Div("Ranking por Tag", className="section-header"),
                            html.Div(id="table-tags"),
                        ],
                    ),
                    md=4,
                ),
            ],
            className="mb-3",
        ),

        # ── Row 3: Tabela Geral ────────────────────────────────
        html.Div(
            className="gray-card",
            children=[
                html.Div("Tabela Geral", className="section-header"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div("Linhas por página", className="pager-label"),
                                dcc.Dropdown(
                                    id="rows-per-page",
                                    options=[
                                        {"label": str(n), "value": n}
                                        for n in [10, 20, 50, 100]
                                    ],
                                    value=20,
                                    clearable=False,
                                    style={
                                        "width": "100px",
                                        "borderRadius": "12px",
                                        "backgroundColor": "#F2F2F2",
                                        "border": "1px solid #D0D0D0",
                                        "fontSize": "0.85rem",
                                    },
                                ),
                            ],
                            md=2,
                        ),
                        dbc.Col(
                            [
                                html.Div("Página", className="pager-label"),
                                dbc.Input(
                                    id="page-number",
                                    type="number",
                                    value=1,
                                    min=1,
                                    step=1,
                                    style={
                                        "width": "80px",
                                        "borderRadius": "12px",
                                        "border": "1px solid #D0D0D0",
                                        "fontSize": "0.85rem",
                                        "backgroundColor": "#F2F2F2",
                                    },
                                ),
                            ],
                            md=2,
                        ),
                        dbc.Col(
                            html.Div(id="pager-info", className="pager-info"),
                            md=8,
                            style={"display": "flex", "alignItems": "flex-end"},
                        ),
                    ],
                    className="mb-2",
                ),
                html.Div(id="tabela-geral"),
            ],
        ),
    ],
)

app.layout = html.Div(
    children=[
        dcc.Store(id="sidebar-store", data=True),
        html.Button("☰", id="sidebar-toggle", className="sidebar-toggle"),
        sidebar,
        dbc.Row(
            [
                dbc.Col(
                    main_content,
                    id="main-col",
                    width={"size": 12, "md": 12},
                ),
            ],
            style={"margin": "0"},
        ),
    ]
)


# =========================================================
# HELPERS
# =========================================================

def apply_filters(ano_sel, mes_sel, loja_sel, topico_sel, tag_sel):
    dff = df.copy()
    if ano_sel:
        dff = dff[dff["Ano"].isin(ano_sel)]
    if mes_sel:
        mes_nums = [str(list_meses.index(m) + 1).zfill(2) for m in mes_sel]
        dff = dff[dff["Mês"].isin(mes_nums)]
    if loja_sel:
        dff = dff[dff["Loja"].isin(loja_sel)]
    if topico_sel:
        dff = dff[dff["Tópico"].isin(topico_sel)]
    if tag_sel:
        dff = dff[dff["Tag"].isin(tag_sel)]
    return dff


def dropdown_options(values):
    return [{"label": value, "value": value} for value in values]


def valid_selection(selected, allowed):
    if not selected:
        return selected
    allowed_set = set(allowed)
    return [value for value in selected if value in allowed_set]


def available_values(dff, column):
    values = dff[column].dropna().unique()
    if column == "Mês":
        month_labels = [list_meses[int(value) - 1] for value in values]
        return sorted(month_labels, key=lambda value: list_meses.index(value))
    return sorted(values)


def color_for(v):
    if v >= 0.85:
        return "#22C55E"
    if v >= 0.70:
        return "#FDBA3B"
    return "#FF4B4B"


def make_ranking_table(data, col_name):
    """Return a Dash DataTable for a ranking dataframe."""
    data = data.copy().reset_index(drop=True)
    data["Média_fmt"] = data["Média"].apply(lambda v: f"{v:.2%}".replace(".", ","))
    style_data_conditional = [
        {
            "if": {"row_index": i, "column_id": "Média_fmt"},
            "color": color_for(v),
            "fontWeight": "700",
        }
        for i, v in enumerate(data["Média"])
    ]

    return dash_table.DataTable(
        data=data[[col_name, "Média_fmt"]].to_dict("records"),
        columns=[
            {"name": col_name, "id": col_name},
            {"name": "Média", "id": "Média_fmt"},
        ],
        style_table={
            "overflowY": "auto",
            "height": "300px",
            "borderRadius": "14px",
        },
        style_header={
            "backgroundColor": CARD_BG,
            "fontWeight": "700",
            "color": "#222",
            "border": "none",
            "fontSize": "0.85rem",
            "fontFamily": "'Segoe UI', sans-serif",
        },
        style_cell={
            "backgroundColor": CARD_BG,
            "color": "#222",
            "border": "none",
            "fontSize": "0.85rem",
            "fontFamily": "'Segoe UI', sans-serif",
            "padding": "6px 10px",
        },
        style_data_conditional=style_data_conditional,
        page_action="none",
    )


def make_general_table(dff_page):
    return dash_table.DataTable(
        data=dff_page.to_dict("records"),
        columns=[{"name": c, "id": c} for c in dff_page.columns],
        style_table={"overflowX": "auto", "borderRadius": "14px"},
        style_header={
            "backgroundColor": CARD_BG,
            "fontWeight": "700",
            "color": "#222",
            "border": "none",
            "fontSize": "0.84rem",
            "fontFamily": "'Segoe UI', sans-serif",
        },
        style_cell={
            "backgroundColor": CARD_BG,
            "color": "#333",
            "border": "none",
            "fontSize": "0.84rem",
            "fontFamily": "'Segoe UI', sans-serif",
            "padding": "6px 10px",
            "textOverflow": "ellipsis",
            "overflow": "hidden",
            "maxWidth": "180px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#EFEFEF"}
        ],
        page_action="none",
        style_as_list_view=True,
    )


# =========================================================
# CALLBACKS
# =========================================================

@app.callback(
    Output("sidebar-col", "style"),
    Output("sidebar-store", "data"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar-store", "data"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, collapsed):
    collapsed = not collapsed
    sidebar_style = {"transform": "translateX(0%)"}

    if collapsed:
        sidebar_style = {"transform": "translateX(-110%)"}

    return sidebar_style, collapsed


@app.callback(
    Output("filter-ano", "options"),
    Output("filter-ano", "value"),
    Output("filter-mes", "options"),
    Output("filter-mes", "value"),
    Output("filter-loja", "options"),
    Output("filter-loja", "value"),
    Output("filter-topico", "options"),
    Output("filter-topico", "value"),
    Output("filter-tag", "options"),
    Output("filter-tag", "value"),
    Input("filter-ano", "value"),
    Input("filter-mes", "value"),
    Input("filter-loja", "value"),
    Input("filter-topico", "value"),
    Input("filter-tag", "value"),
)
def update_filter_options(ano_sel, mes_sel, loja_sel, topico_sel, tag_sel):
    anos_disp = available_values(
        apply_filters(None, mes_sel, loja_sel, topico_sel, tag_sel), "Ano"
    )
    meses_disp = available_values(
        apply_filters(ano_sel, None, loja_sel, topico_sel, tag_sel), "Mês"
    )
    lojas_disp = available_values(
        apply_filters(ano_sel, mes_sel, None, topico_sel, tag_sel), "Loja"
    )
    topicos_disp = available_values(
        apply_filters(ano_sel, mes_sel, loja_sel, None, tag_sel), "Tópico"
    )
    tags_disp = available_values(
        apply_filters(ano_sel, mes_sel, loja_sel, topico_sel, None), "Tag"
    )

    return (
        dropdown_options(anos_disp),
        valid_selection(ano_sel, anos_disp),
        dropdown_options(meses_disp),
        valid_selection(mes_sel, meses_disp),
        dropdown_options(lojas_disp),
        valid_selection(loja_sel, lojas_disp),
        dropdown_options(topicos_disp),
        valid_selection(topico_sel, topicos_disp),
        dropdown_options(tags_disp),
        valid_selection(tag_sel, tags_disp),
    )


@app.callback(
    Output("gauge-chart", "figure"),
    Output("line-chart", "figure"),
    Output("table-lojas", "children"),
    Output("table-topicos", "children"),
    Output("table-tags", "children"),
    Output("tabela-geral", "children"),
    Output("pager-info", "children"),
    Input("filter-ano", "value"),
    Input("filter-mes", "value"),
    Input("filter-loja", "value"),
    Input("filter-topico", "value"),
    Input("filter-tag", "value"),
    Input("rows-per-page", "value"),
    Input("page-number", "value"),
)
def update_all(ano_sel, mes_sel, loja_sel, topico_sel, tag_sel, rows_per_page, page):
    dff = apply_filters(ano_sel, mes_sel, loja_sel, topico_sel, tag_sel)

    # ── Gauge ─────────────────────────────────────────────
    media_geral = (
        dff["Nota Atingida"].sum() / dff["Nota Possível"].sum()
        if dff["Nota Possível"].sum() > 0
        else 0
    )
    gauge_color = color_for(media_geral)

    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=media_geral * 100,
            number={"suffix": "%", "font": {"size": 48, "color": "#222"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0},
                "bar": {"color": gauge_color, "thickness": 1.0},
                "bgcolor": "white",
                "steps": [{"range": [0, 100], "color": "#E5E7EB"}],
                "threshold": {
                    "line": {"color": "#222", "width": 10},
                    "thickness": 0.8,
                    "value": 85,
                },
            },
        )
    )
    fig_gauge.update_layout(
        height=300,
        margin=dict(t=40, b=20, l=30, r=30),
        paper_bgcolor=CARD_BG,
        font={"color": "#222"},
    )

    # ── Line chart ────────────────────────────────────────
    df_mes = (
        dff.groupby(["Ano", "Mês"], as_index=False)
        .agg({"Nota Atingida": "sum", "Nota Possível": "sum"})
    )
    df_mes["Média"] = df_mes["Nota Atingida"] / df_mes["Nota Possível"].replace(0, 1)
    df_mes["AnoMes"] = df_mes["Mês"] + "/" + df_mes["Ano"]
    df_mes = df_mes.sort_values(["Ano", "Mês"])

    show_labels = len(df_mes) <= 14
    text_values = (
        [f"{v:.1%}".replace(".", ",") for v in df_mes["Média"]]
        if show_labels
        else None
    )

    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=df_mes["AnoMes"],
            y=df_mes["Média"],
            mode="lines+markers+text" if show_labels else "lines+markers",
            text=text_values,
            textposition="top center",
            line=dict(color="#A8A8A8", width=4),
            marker=dict(
                size=10,
                color=[color_for(v) for v in df_mes["Média"]],
            ),
        )
    )
    fig_line.update_layout(
        height=300,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, color="#666"),
        yaxis=dict(tickformat=".0%", showgrid=False, color="#666"),
        font=dict(color="#222"),
        showlegend=False,
    )

    # ── Ranking tables ────────────────────────────────────
    def ranking(col):
        r = (
            dff.groupby(col, as_index=False)
            .agg({"Nota Atingida": "sum", "Nota Possível": "sum"})
        )
        r["Média"] = r["Nota Atingida"] / r["Nota Possível"].replace(0, 1)
        return r.sort_values("Média", ascending=False)

    tbl_lojas = make_ranking_table(ranking("Loja"), "Loja")
    tbl_topicos = make_ranking_table(ranking("Tópico"), "Tópico")
    tbl_tags = make_ranking_table(ranking("Tag"), "Tag")

    # ── Tabela Geral ──────────────────────────────────────
    rows_per_page = rows_per_page or 20
    page = page or 1

    tabela_base = dff[
        ["Data", "Loja", "Tópico", "Tag", "Questão", "Resposta", "Observação"]
    ].copy()
    tabela_base["Data"] = tabela_base["Data"].dt.strftime("%d/%m/%Y")

    total_rows = len(tabela_base)
    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)
    page = min(page, total_pages)

    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    tabela_page = tabela_base.iloc[start:end]

    tbl_geral = make_general_table(tabela_page)
    pager_info = f"Página {page} de {total_pages} | {total_rows} linhas"

    return (
        fig_gauge,
        fig_line,
        tbl_lojas,
        tbl_topicos,
        tbl_tags,
        tbl_geral,
        pager_info,
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=False)
