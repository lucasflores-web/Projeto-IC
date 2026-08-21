import logging
import pandas as pd
from taipy.gui import notify
from db import (
    carregar_serie_historica,
    buscar_valores_filtro,
    buscar_valores_filtro_condicionado,
    buscar_anos_disponiveis,
)

logger = logging.getLogger(__name__)

# ---------- Configuração do indicador ----------

TIPO_CURSOS = "cpc"
ANOS_CURSOS = buscar_anos_disponiveis(TIPO_CURSOS)

QTD_SLOTS = 4  # quantidade de duplas (IES + Área) disponíveis para comparação

# Métricas do CPC que queremos exibir — nome de exibição -> nome da coluna no banco
METRICAS_CPC = {
    "Contínuo": "cpc_continuo",
    "Faixa": "cpc_faixa",
}

MAX_SERIES = QTD_SLOTS * len(METRICAS_CPC)


# ---------- Estados iniciais ----------

ies_disponiveis_comparar = buscar_valores_filtro(TIPO_CURSOS, "nome_da_ies")

ies_selecionada_1 = None
ies_selecionada_2 = None
ies_selecionada_3 = None
ies_selecionada_4 = None

areas_disponiveis_1 = []
areas_disponiveis_2 = []
areas_disponiveis_3 = []
areas_disponiveis_4 = []

area_selecionada_1 = None
area_selecionada_2 = None
area_selecionada_3 = None
area_selecionada_4 = None

tabela_comparar = pd.DataFrame({"Ano": ANOS_CURSOS})
grafico_comparar = pd.DataFrame({"Ano": ANOS_CURSOS})


# ---------- Funções auxiliares (puras — não tocam em `state`) ----------

def _areas_da_ies(ies: str) -> list[str]:
    """Busca, via endpoint condicionado, as áreas de avaliação (cursos)
    oferecidas por uma IES — filtro feito no banco, não em memória."""
    if not ies:
        return []
    return buscar_valores_filtro_condicionado(
        TIPO_CURSOS, "area_de_avaliacao", "nome_da_ies", ies
    )


def _rotulo_dupla(ies: str, area: str) -> str:
    """Rótulo curto usado como nome de coluna/série no gráfico e na tabela."""
    return f"{ies} - {area}"


def _series_por_ano(ies: str, area: str) -> dict[str, dict[str, float]]:
    """Para uma dupla (IES, área), retorna a média por ano de cada métrica do CPC
    (cpc_continuo e cpc_faixa). Formato: {"Contínuo": {ano: valor}, "Faixa": {ano: valor}}."""
    filtros = {"nome_da_ies": ies, "area_de_avaliacao": area}
    df = carregar_serie_historica(TIPO_CURSOS, ANOS_CURSOS, filtros)

    logger.info("_series_por_ano ies=%r area=%r -> %d linhas, colunas=%s",
                ies, area, len(df), list(df.columns))

    if df.empty:
        return {}

    resultado = {}
    for nome_metrica, coluna in METRICAS_CPC.items():
        if coluna not in df.columns:
            logger.warning("coluna %r não encontrada em %s", coluna, list(df.columns))
            continue
        numerico = pd.to_numeric(df[coluna], errors="coerce")
        agrupado = numerico.groupby(df["ano"]).mean()
        resultado[nome_metrica] = agrupado.to_dict()

    return resultado


def _montar_serie_historica(duplas: list[tuple[str, str]]) -> tuple[pd.DataFrame, list[str]]:
    """Monta um DataFrame wide: uma linha por Ano, duas colunas por dupla selecionada
    (uma para cpc_continuo, outra para cpc_faixa). Retorna também a lista de rótulos
    que não tiveram nenhum dado encontrado."""
    dados = {"Ano": ANOS_CURSOS}
    sem_dados = []

    for ies, area in duplas:
        rotulo = _rotulo_dupla(ies, area)
        series = _series_por_ano(ies, area)
        if not series:
            sem_dados.append(rotulo)

        for nome_metrica in METRICAS_CPC:
            serie = series.get(nome_metrica, {})
            dados[f"{rotulo} ({nome_metrica})"] = [
                round(serie[ano], 2) if ano in serie and pd.notna(serie[ano]) else None
                for ano in ANOS_CURSOS
            ]

    return pd.DataFrame(dados), sem_dados


def _properties_grafico(colunas: list[str]) -> dict:
    props = {
        "x": "Ano",
        "mode": "lines+markers",
        "line_shape": "spline",
    }
    for i in range(1, MAX_SERIES + 1):
        coluna = colunas[i - 1] if i <= len(colunas) else None
        props[f"y[{i}]"] = coluna
        props[f"name[{i}]"] = coluna
        props[f"options[{i}]"] = {"connectgaps": True} if coluna else None
    return props


propriedades_grafico = _properties_grafico([])


# ---------- Callbacks ----------

def _fazer_on_change_ies(indice: int):
    """Fábrica: gera o callback de mudança de IES para um slot específico
    (1 a QTD_SLOTS), evitando repetir a mesma função para cada slot."""
    def _on_change(state):
        ies = getattr(state, f"ies_selecionada_{indice}")
        setattr(state, f"areas_disponiveis_{indice}", _areas_da_ies(ies))
        setattr(state, f"area_selecionada_{indice}", None)
    return _on_change


on_change_ies_1 = _fazer_on_change_ies(1)
on_change_ies_2 = _fazer_on_change_ies(2)
on_change_ies_3 = _fazer_on_change_ies(3)
on_change_ies_4 = _fazer_on_change_ies(4)


def comparar_cursos(state):
    """Botão 'Comparar': lê os slots do state e monta tabela + gráfico de uma vez."""
    slots = [
        (getattr(state, f"ies_selecionada_{i}"), getattr(state, f"area_selecionada_{i}"))
        for i in range(1, QTD_SLOTS + 1)
    ]

    duplas = []
    for ies, area in slots:
        if ies in (None, "", "Todos") or area in (None, "", "Todos"):
            continue
        dupla = (ies, area)
        if dupla not in duplas:
            duplas.append(dupla)

    if not duplas:
        notify(state, "warning", "Selecione ao menos uma dupla de IES + Área antes de comparar.")
        state.tabela_comparar = pd.DataFrame({"Ano": ANOS_CURSOS})
        state.grafico_comparar = pd.DataFrame({"Ano": ANOS_CURSOS})
        state.propriedades_grafico = _properties_grafico([])
        return

    try:
        wide, sem_dados = _montar_serie_historica(duplas)
        colunas_series = [c for c in wide.columns if c != "Ano"]

        with state:
            state.tabela_comparar = wide
            state.grafico_comparar = wide
            state.propriedades_grafico = _properties_grafico(colunas_series)

        notify(state, "success", "Comparação atualizada.")
        if sem_dados:
            notify(state, "warning", "Sem dados de CPC para: " + "; ".join(sem_dados))
    except Exception as e:
        logger.exception("Erro ao montar comparação")
        notify(state, "error", f"Erro ao montar comparação: {e}")


def limpar_comparacao(state):
    df_vazio = pd.DataFrame({"Ano": ANOS_CURSOS})

    with state:
        for i in range(1, QTD_SLOTS + 1):
            setattr(state, f"ies_selecionada_{i}", None)
            setattr(state, f"areas_disponiveis_{i}", [])
            setattr(state, f"area_selecionada_{i}", None)

        state.tabela_comparar = df_vazio
        state.grafico_comparar = df_vazio
        state.propriedades_grafico = _properties_grafico([])


# ---------- Layout (sem mudanças) ----------

pagina_comparar_md = """
# Comparação de Cursos ao Longo dos Anos
Escolha até 4 IES + Área de Avaliação e clique em **Comparar** para ver a evolução do CPC (Contínuo e Faixa)

<|part|class_name=card|

<|layout|columns=1 1|gap=20px|
<|
### IES 1
<|layout|columns=1 1|gap=5px|
<|{ies_selecionada_1}|selector|lov={ies_disponiveis_comparar}|on_change=on_change_ies_1|label=IES 1|dropdown|filter=True|>
<|{area_selecionada_1}|selector|lov={areas_disponiveis_1}|label=Área/Curso 1|dropdown|filter=True|>
|>
|>

<|
### IES 2
<|layout|columns=1 1|gap=5px|
<|{ies_selecionada_2}|selector|lov={ies_disponiveis_comparar}|on_change=on_change_ies_2|label=IES 2|dropdown|filter=True|>
<|{area_selecionada_2}|selector|lov={areas_disponiveis_2}|label=Área/Curso 2|dropdown|filter=True|>
|>
|>
|>

<|layout|columns=1 1|gap=20px|
<|
### IES 3
<|layout|columns=1 1|gap=5px|
<|{ies_selecionada_3}|selector|lov={ies_disponiveis_comparar}|on_change=on_change_ies_3|label=IES 3|dropdown|filter=True|>
<|{area_selecionada_3}|selector|lov={areas_disponiveis_3}|label=Área/Curso 3|dropdown|filter=True|>
|>
|>

<|
### IES 4
<|layout|columns=1 1|gap=5px|
<|{ies_selecionada_4}|selector|lov={ies_disponiveis_comparar}|on_change=on_change_ies_4|label=IES 4|dropdown|filter=True|>
<|{area_selecionada_4}|selector|lov={areas_disponiveis_4}|label=Área/Curso 4|dropdown|filter=True|>
|>
|>
|>

---

<|layout|columns=1 1|gap=5px|
<|Comparar|button|on_action=comparar_cursos|>
<|Limpar seleção|button|on_action=limpar_comparacao|>
|>

|>

<|part|class_name=card|
### Evolução do CPC (Contínuo e Faixa) por Ano
<|{grafico_comparar}|chart|properties={propriedades_grafico}|rebuild=True|>
|>

### Resultados (tabela)
<|{tabela_comparar}|table|show_all=True|rebuild=True|>
"""