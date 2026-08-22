import pandas as pd
from db import carregar_serie_historica, buscar_valores_filtro, buscar_anos_disponiveis

TABELA = "cpc"
ANOS_CURSOS = buscar_anos_disponiveis(TABELA)

# ---------- Estados iniciais ----------

anos_disponiveis_cursos = ["Todos"] + ANOS_CURSOS
cursos_disponiveis_cursos = ["Todos"] + buscar_valores_filtro(TABELA, "nome_do_curso")
conceitos_disponiveis_cursos = ["Todos"] + buscar_valores_filtro(TABELA, "conceito_enade_continuo")
notas_cpc_disponiveis_cursos = ["Todos"] + buscar_valores_filtro(TABELA, "cpc_faixa")
ufs_disponiveis_cursos = ["Todos"] + buscar_valores_filtro(TABELA, "sigla_da_uf")
areas_disponiveis_cursos = ["Todos"] + buscar_valores_filtro(TABELA, "area_de_avaliacao")


ano_selecionado_cursos = max(ANOS_CURSOS)
curso_selecionado_cursos = "Todos"
conceito_selecionado_cursos = "Todos"
nota_cpc_selecionada_cursos = "Todos"
uf_selecionada_cursos = "Todos"
area_selecionada_cursos = "Todos"


_COLUNAS_TABELA = [
    "area_de_avaliacao", "nome_da_ies", "sigla_da_ies", "sigla_da_uf",
    "conceito_enade_continuo", "nota_padronizada_idd", "cpc_faixa", "ano",
]

_RENOMEAR_TABELA = {
    "area_de_avaliacao": "Curso",
    "nome_da_ies": "IES",
    "sigla_da_ies": "Sigla da IES",
    "sigla_da_uf": "UF",
    "conceito_enade_continuo": "Conceito Enade",
    "nota_padronizada_idd": "IDD (Padronizada)",
    "cpc_faixa": "CPC (Faixa)",
    "ano": "Ano",
}


def _preparar_tabela(df: pd.DataFrame) -> pd.DataFrame:
    colunas_existentes = [c for c in _COLUNAS_TABELA if c in df.columns]
    return df[colunas_existentes].rename(columns=_RENOMEAR_TABELA)


def _buscar_dados_filtrados(
    ano_selecionado=ano_selecionado_cursos,
    curso_selecionado=curso_selecionado_cursos,
    conceito_selecionado=conceito_selecionado_cursos,
    nota_cpc_selecionada=nota_cpc_selecionada_cursos,
    uf_selecionada=uf_selecionada_cursos,
    area_selecionada=area_selecionada_cursos,
) -> pd.DataFrame:
    filtros = {
        "nome_do_curso": curso_selecionado,
        "cpc_faixa": nota_cpc_selecionada,
        "sigla_da_uf": uf_selecionada,
        "area_de_avaliacao": area_selecionada,
        "conceito_enade_continuo": conceito_selecionado,
    }

    anos = ANOS_CURSOS if ano_selecionado == "Todos" else [ano_selecionado]
    df = carregar_serie_historica(TABELA, anos, filtros)
    return _preparar_tabela(df)


df_cursos = _buscar_dados_filtrados()


# ---------- Callbacks ----------

def on_change_filtro_cursos(state):
    aplicar_filtros_cursos(state)


def aplicar_filtros_cursos(state):
    state.df_cursos = _buscar_dados_filtrados(
        state.ano_selecionado_cursos,
        state.curso_selecionado_cursos,
        state.conceito_selecionado_cursos,
        state.nota_cpc_selecionada_cursos,
        state.uf_selecionada_cursos,
        state.area_selecionada_cursos,
    )


def limpar_filtros_cursos(state):
    state.ano_selecionado_cursos = "Todos"
    state.curso_selecionado_cursos = "Todos"
    state.conceito_selecionado_cursos = "Todos"
    state.nota_cpc_selecionada_cursos = "Todos"
    state.uf_selecionada_cursos = "Todos"
    state.area_selecionada_cursos = "Todos"
    aplicar_filtros_cursos(state)


# ---------- Layout ----------

pagina_cursos_md = """
# Pesquisa por Cursos e Áreas do Conhecimento
Consulte cursos e áreas com base no Conceito Enade e na nota da instituição

<|part|class_name=card|
### Filtros

<|layout|columns=1 1 1|gap=5px|
<|{ano_selecionado_cursos}|selector|lov={anos_disponiveis_cursos}|on_change=on_change_filtro_cursos|label=Ano|dropdown|>

<|{nota_cpc_selecionada_cursos}|selector|lov={notas_cpc_disponiveis_cursos}|on_change=on_change_filtro_cursos|label=Nota do curso (CPC)|dropdown|>

<|{uf_selecionada_cursos}|selector|lov={ufs_disponiveis_cursos}|on_change=on_change_filtro_cursos|label=Unidade Federativa (UF)|dropdown|>

|>

<|layout|columns=1 2|gap=5px|
<|{area_selecionada_cursos}|selector|lov={areas_disponiveis_cursos}|on_change=on_change_filtro_cursos|label=Curso|dropdown|>

<|
<|Limpar filtros|button|on_action=limpar_filtros_cursos|>
|>
|>

|>

### Resultados
<|{df_cursos}|table|page_size=15|filter=True|>
"""