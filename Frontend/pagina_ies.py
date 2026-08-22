import pandas as pd
from db import carregar_serie_historica, buscar_valores_filtro, buscar_anos_disponiveis

TABELA = "igc"
ANOS_IES = buscar_anos_disponiveis(TABELA)

# ---------- Estados iniciais ----------

anos_disponiveis_ies = ["Todos"] + ANOS_IES
ufs_disponiveis_ies = ["Todos"] + buscar_valores_filtro(TABELA, "sigla_da_uf")
categorias_disponiveis_ies = ["Todos"] + buscar_valores_filtro(TABELA, "categoria_administrativa")
notas_disponiveis_ies = ["Todos"] + buscar_valores_filtro(TABELA, "igc_faixa")

ano_selecionado_ies = max(ANOS_IES)
uf_selecionada_ies = "Todos"
categoria_selecionada_ies = "Todos"
nota_selecionada_ies = "Todos"


_COLUNAS_TABELA = [
    "nome_da_ies", "sigla_da_ies", "sigla_da_uf", "categoria_administrativa",
    "igc_continuo", "igc_faixa", "ano",
]

_RENOMEAR_TABELA = {
    "nome_da_ies": "IES",
    "sigla_da_ies": "Sigla IES",
    "sigla_da_uf": "UF",
    "categoria_administrativa": "Categoria Administrativa",
    "igc_continuo": "IGC (Contínuo)",
    "igc_faixa": "IGC (Faixa)",
    "ano": "Ano",
}


def _preparar_tabela(df: pd.DataFrame) -> pd.DataFrame:
    colunas_existentes = [c for c in _COLUNAS_TABELA if c in df.columns]
    return df[colunas_existentes].rename(columns=_RENOMEAR_TABELA)


def _buscar_dados_filtrados(
    ano_selecionado=ano_selecionado_ies,
    uf_selecionada=uf_selecionada_ies,
    categoria_selecionada=categoria_selecionada_ies,
    nota_selecionada=nota_selecionada_ies,
) -> pd.DataFrame:
    filtros = {
        "sigla_da_uf": uf_selecionada,
        "categoria_administrativa": categoria_selecionada,
        "igc_faixa": nota_selecionada,
    }

    anos = ANOS_IES if ano_selecionado == "Todos" else [ano_selecionado]
    df = carregar_serie_historica(TABELA, anos, filtros)
    return _preparar_tabela(df)


df_ies = _buscar_dados_filtrados()


# ---------- Callbacks ----------

def on_change_filtro_ies(state):
    aplicar_filtros_ies(state)


def aplicar_filtros_ies(state):
    state.df_ies = _buscar_dados_filtrados(
        state.ano_selecionado_ies,
        state.uf_selecionada_ies,
        state.categoria_selecionada_ies,
        state.nota_selecionada_ies,
    )


def limpar_filtros_ies(state):
    state.uf_selecionada_ies = "Todos"
    state.categoria_selecionada_ies = "Todos"
    state.ano_selecionado_ies = "Todos"
    state.nota_selecionada_ies = "Todos"
    aplicar_filtros_ies(state)


# ---------- Layout ----------

pagina_ies_md = """
# Pesquisa por Instituição de Ensino Superior (IES)
Encontre e analise instituições com base em indicadores de qualidade.

<|part|class_name=card|
### Filtros

<|layout|columns=1 1 1 1|gap=5px|
<|{uf_selecionada_ies}|selector|lov={ufs_disponiveis_ies}|on_change=on_change_filtro_ies|label=Unidade Federativa|dropdown|>

<|{categoria_selecionada_ies}|selector|lov={categorias_disponiveis_ies}|on_change=on_change_filtro_ies|label=Categoria Administrativa|dropdown|>

<|{ano_selecionado_ies}|selector|lov={anos_disponiveis_ies}|on_change=on_change_filtro_ies|label=Ano|dropdown|>

<|{nota_selecionada_ies}|selector|lov={notas_disponiveis_ies}|on_change=on_change_filtro_ies|label=Nota da Instituição (IGC)|dropdown|>

<|Limpar filtros|button|on_action=limpar_filtros_ies|>
|>

|>

### Resultados
<|{df_ies}|table|page_size=15|filter=True|>
"""