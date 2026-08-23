from fastapi import FastAPI, status, Query
import models
from typing import List, Dict, Any, Optional

app = FastAPI()


@app.get("/anos_disponiveis/{dataset}", status_code=status.HTTP_200_OK)
def get_anos_disponiveis(dataset: str):
    anos = models.list_available_tables(dataset)
    return {"dataset": dataset, "anos": anos}


@app.get("/filtros/{dataset}/{coluna}", status_code=status.HTTP_200_OK)
def get_valores_filtro(dataset: str, coluna: str):
    valores = models.get_distinct_values(dataset, coluna)
    return {"dataset": dataset, "coluna": coluna, "valores": valores}


@app.get("/filtros/{dataset}/{coluna}/por/{filtro_coluna}", status_code=status.HTTP_200_OK)
def get_valores_filtro_condicionado(dataset: str, coluna: str, filtro_coluna: str, valor: str):
    valores = models.get_distinct_values_filtered(dataset, coluna, filtro_coluna, valor)
    return {"dataset": dataset, "coluna": coluna, "valores": valores}


_FILTROS_POR_DATASET = {
    "igc": ["sigla_da_uf", "categoria_administrativa", "igc_faixa"],
    "cpc": ["nome_do_curso", "cpc_faixa", "area_de_avaliacao", "sigla_da_uf", "conceito_enade_continuo", "nome_da_ies"],
    "idd": ["sigla_da_uf", "area_de_avaliacao", "nome_da_ies"],
    "conceito_enade": ["sigla_da_uf", "area_de_avaliacao", "nome_da_ies"],
}


@app.get("/dados_filtrados/{dataset}", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_dados_filtrados(
    dataset: str,
    anos: List[str] = Query(...),
    sigla_da_uf: Optional[str] = None,
    categoria_administrativa: Optional[str] = None,
    igc_faixa: Optional[str] = None,
    cpc_faixa: Optional[str] = None,
    area_de_avaliacao: Optional[str] = None,
    conceito_enade_continuo: Optional[str] = None,
    nome_do_curso: Optional[str] = None,
    nome_da_ies: Optional[str] = None,
):
    colunas_permitidas = _FILTROS_POR_DATASET[dataset]

    candidatos = {
        "sigla_da_uf": sigla_da_uf,
        "categoria_administrativa": categoria_administrativa,
        "igc_faixa": igc_faixa,
        "cpc_faixa": cpc_faixa,
        "area_de_avaliacao": area_de_avaliacao,
        "conceito_enade_continuo": conceito_enade_continuo,
        "nome_do_curso": nome_do_curso,
        "nome_da_ies": nome_da_ies,
    }
    filtros = {
        col: val for col, val in candidatos.items()
        if col in colunas_permitidas and val not in (None, "", "Todos")
    }

    return models.get_filtered_data(dataset, anos, filtros)